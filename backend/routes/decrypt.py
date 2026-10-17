import os
import base64
import time
import tempfile
import shutil

from datetime import datetime, timezone

from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
    session,
    current_app
)

from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from cryptography.hazmat.primitives import serialization

from database.mongodb import (
    users_collection,
    decryption_history_collection,
    encryption_history_collection
)

from auth_utils import login_required

from encryption.aes import (
    decrypt_file as aes_decrypt_file
)

from encryption.chacha20 import (
    decrypt_file as chacha_decrypt_file
)

from encryption.hybrid import (
    decrypt_file as hybrid_decrypt_file,
    load_private_key
)

from encryption.key_manager import load_key


decrypt_bp = Blueprint("decrypt", __name__)


# ============================================================
# ALGORITHM NAMES
# ============================================================

AES_ALGORITHM = "AES-256-GCM"
CHACHA_ALGORITHM = "ChaCha20-Poly1305"
HYBRID_ALGORITHM = "Hybrid AES-256-GCM + RSA-OAEP"


def normalize_algorithm(algorithm):
    """Convert saved algorithm names into consistent names."""

    if not algorithm:
        return None

    value = str(algorithm).strip().lower()

    if value in {"aes", "aes-256-gcm"}:
        return AES_ALGORITHM

    if value in {
        "chacha20",
        "chacha20-poly1305"
    }:
        return CHACHA_ALGORITHM

    if value in {
        "hybrid",
        "hybrid aes-256-gcm + rsa-oaep",
        "aes-256-gcm + rsa-oaep"
    }:
        return HYBRID_ALGORITHM

    return None


# ============================================================
# PASSWORD CONFIRMATION
# ============================================================

def verify_current_user_password(password):
    """
    Verify the submitted password against the password hash
    belonging to the currently authenticated user.
    """

    user_id = session.get("user_id")
    email = session.get("email")

    if not user_id or not email or not password:
        return False

    user = users_collection.find_one({
        "email": email
    })

    if not user:
        return False

    # Prevent a session from being used if it no longer
    # matches the account ID stored in the database.
    if str(user.get("_id")) != str(user_id):
        return False

    password_hash = user.get("password_hash")

    if not password_hash:
        return False

    try:
        return check_password_hash(
            password_hash,
            password
        )
    except (ValueError, TypeError):
        return False


# ============================================================
# USER-SPECIFIC KEY IDENTIFIER
# ============================================================

def get_key_identifier(user_id, original_filename):
    """
    Must match the identifier used by the updated upload.py.
    """

    return f"{user_id}_{original_filename}"


# ============================================================
# SAVE DECRYPTION HISTORY
# ============================================================

def save_decryption_record(
    user_id,
    filename,
    algorithm,
    key_type,
    processing_time_ms,
    status
):
    record = {
        "user_id": str(user_id),
        "filename": filename,
        "algorithm": algorithm,
        "key_type": key_type,
        "processing_time_ms": processing_time_ms,
        "status": status,
        "created_at": datetime.now(timezone.utc)
    }

    result = decryption_history_collection.insert_one(
        record
    )

    return result.inserted_id


# ============================================================
# SERIALIZE DECRYPTION HISTORY
# ============================================================

def serialize_decryption_record(record):
    record["id"] = str(record.pop("_id"))

    if isinstance(record.get("created_at"), datetime):
        record["created_at"] = (
            record["created_at"].isoformat()
        )

    return record


# ============================================================
# DECRYPTION HISTORY
# ============================================================

@decrypt_bp.route(
    "/decrypt/history",
    methods=["GET"]
)
@login_required
def get_decryption_history():
    user_id = str(session["user_id"])

    records = (
        decryption_history_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
    )

    history = [
        serialize_decryption_record(record)
        for record in records
    ]

    return jsonify({
        "success": True,
        "history": history
    }), 200


# ============================================================
# GET USER'S ENCRYPTION RECORD
# ============================================================

def get_encryption_record(user_id, filename):
    """
    Retrieve metadata only if it belongs to this user.
    """

    return encryption_history_collection.find_one({
        "user_id": str(user_id),
        "filename": filename
    })


# ============================================================
# LOAD STORED DECRYPTION KEY
# ============================================================

def load_stored_decryption_key(
    key_identifier,
    encryption_algorithm
):
    if encryption_algorithm in {
        AES_ALGORITHM,
        CHACHA_ALGORITHM
    }:
        return (
            load_key(key_identifier),
            "256-bit symmetric key"
        )

    if encryption_algorithm == HYBRID_ALGORITHM:
        return (
            load_private_key(key_identifier),
            "RSA-2048 private key"
        )

    raise ValueError(
        "Unsupported encryption algorithm."
    )


# ============================================================
# CREATE DECRYPTED FILE RESPONSE
# ============================================================

def create_decryption_response(
    decrypted_out_path,
    original_filename,
    algorithm
):
    response = send_file(
        decrypted_out_path,
        as_attachment=True,
        download_name=original_filename,
        mimetype="application/octet-stream"
    )

    response.headers["X-Decryption-Algorithm"] = algorithm
    response.headers["X-Decryption-Status"] = "Success"
    response.headers["X-Original-Filename"] = original_filename

    return response


# ============================================================
# CLEANUP HELPERS
# ============================================================

def cleanup_file(file_path):
    if file_path and os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except OSError:
            current_app.logger.warning(
                "Could not remove a temporary file."
            )


def cleanup_directory(directory):
    if directory and os.path.isdir(directory):
        try:
            shutil.rmtree(directory)
        except OSError:
            current_app.logger.warning(
                "Could not remove a temporary directory."
            )


# ============================================================
# DECRYPT FILE
# ============================================================

@decrypt_bp.route(
    "/decrypt",
    methods=["POST"]
)
@login_required
def decrypt_file():

    # --------------------------------------------------------
    # 1. CONFIRM PASSWORD
    # --------------------------------------------------------

    password = request.form.get("password", "")

    if not password:
        return jsonify({
            "success": False,
            "error": "Please enter your login password to confirm decryption."
        }), 400

    if not verify_current_user_password(password):
        return jsonify({
            "success": False,
            "error": "Incorrect password. Decryption was not performed."
        }), 401

    user_id = str(session["user_id"])

    # --------------------------------------------------------
    # 2. VALIDATE ENCRYPTED FILE
    # --------------------------------------------------------

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "Encrypted file is required."
        }), 400

    enc_file = request.files["file"]

    if not enc_file.filename:
        return jsonify({
            "success": False,
            "error": "Encrypted file name is missing."
        }), 400

    encrypted_filename = secure_filename(
        os.path.basename(enc_file.filename)
    )

    if not encrypted_filename.lower().endswith(".enc"):
        return jsonify({
            "success": False,
            "error": "Unsupported encrypted file. Select a .enc file."
        }), 400

    original_filename = encrypted_filename[:-4]

    if not original_filename:
        return jsonify({
            "success": False,
            "error": "Invalid encrypted filename."
        }), 400

    # --------------------------------------------------------
    # 3. VALIDATE KEY SOURCE
    # --------------------------------------------------------

    key_source = request.form.get(
        "key_source",
        "upload"
    ).strip().lower()

    if key_source not in {"upload", "stored"}:
        return jsonify({
            "success": False,
            "error": "Invalid key source."
        }), 400

    key_file = None

    if key_source == "upload":
        if "key" not in request.files:
            return jsonify({
                "success": False,
                "error": "Please upload the decryption key."
            }), 400

        key_file = request.files["key"]

        if not key_file.filename:
            return jsonify({
                "success": False,
                "error": "The key filename is missing."
            }), 400

    # --------------------------------------------------------
    # 4. CREATE A UNIQUE TEMPORARY DIRECTORY
    # --------------------------------------------------------

    temp_dir = tempfile.mkdtemp(
        prefix="decrypt_"
    )

    temp_enc_path = os.path.join(
        temp_dir,
        "encrypted_input.enc"
    )

    decrypted_out_path = os.path.join(
        temp_dir,
        original_filename
    )

    keep_temp_dir = False

    decryption_start = time.perf_counter()

    try:
        # ----------------------------------------------------
        # 5. SAVE ENCRYPTED FILE TEMPORARILY
        # ----------------------------------------------------

        enc_file.save(temp_enc_path)

        # ----------------------------------------------------
        # 6. GET THE CURRENT USER'S ENCRYPTION RECORD
        # ----------------------------------------------------

        encryption_record = get_encryption_record(
            user_id,
            original_filename
        )

        # Ownership check: both stored-key and uploaded-key modes
        # require an encryption record that belongs to this user.
        if not encryption_record:
            return jsonify({
                "success": False,
                "error": (
                    "This encrypted file is not registered to your account. "
                    "You cannot decrypt it from this account."
                )
            }), 403

        encryption_algorithm = None

        if encryption_record:
            encryption_algorithm = normalize_algorithm(
                encryption_record.get("encryption_algorithm")
            )

            saved_algorithm = encryption_record.get(
                "encryption_algorithm"
            )

            if saved_algorithm and not encryption_algorithm:
                return jsonify({
                    "success": False,
                    "error": "The saved encryption algorithm is unsupported."
                }), 400

        # ----------------------------------------------------
        # 7. STORED KEY MODE
        # ----------------------------------------------------

        symmetric_key = None
        private_key = None
        key_type = None

        key_identifier = get_key_identifier(
            user_id,
            original_filename
        )

        if key_source == "stored":

            if not encryption_record:
                return jsonify({
                    "success": False,
                    "error": (
                        "No encryption record belonging to your account "
                        "was found for this file."
                    )
                }), 404

            if not encryption_algorithm:
                return jsonify({
                    "success": False,
                    "error": (
                        "The encryption algorithm is missing "
                        "or unsupported in the saved record."
                    )
                }), 400

            try:
                stored_key, key_type = (
                    load_stored_decryption_key(
                        key_identifier,
                        encryption_algorithm
                    )
                )

            except FileNotFoundError:
                return jsonify({
                    "success": False,
                    "error": (
                        "The stored decryption key was not found. "
                        "The key may have been saved using an older "
                        "storage path."
                    )
                }), 404

            if encryption_algorithm in {
                AES_ALGORITHM,
                CHACHA_ALGORITHM
            }:
                symmetric_key = stored_key
            else:
                private_key = stored_key

        # ----------------------------------------------------
        # 8. UPLOADED KEY MODE
        # ----------------------------------------------------

        else:
            uploaded_raw_key = key_file.read().strip()

            if not uploaded_raw_key:
                return jsonify({
                    "success": False,
                    "error": "The uploaded key file is empty."
                }), 400

            if encryption_algorithm in {
                AES_ALGORITHM,
                CHACHA_ALGORITHM
            }:
                try:
                    symmetric_key = base64.b64decode(
                        uploaded_raw_key,
                        validate=True
                    )
                except Exception:
                    symmetric_key = uploaded_raw_key

                if len(symmetric_key) != 32:
                    return jsonify({
                        "success": False,
                        "error": (
                            "Invalid symmetric key. "
                            "A 256-bit key must contain 32 decoded bytes."
                        )
                    }), 400

                key_type = "256-bit symmetric key"

            elif encryption_algorithm == HYBRID_ALGORITHM:
                try:
                    private_key = serialization.load_pem_private_key(
                        uploaded_raw_key,
                        password=None
                    )
                except (ValueError, TypeError):
                    return jsonify({
                        "success": False,
                        "error": "Invalid RSA private key."
                    }), 400

                key_type = "RSA-2048 private key"

            else:
                # Legacy compatibility: if no encryption record
                # exists for this user, identify the uploaded key
                # by its format. Do not use another user's metadata.
                try:
                    possible_symmetric_key = base64.b64decode(
                        uploaded_raw_key,
                        validate=True
                    )
                except Exception:
                    possible_symmetric_key = uploaded_raw_key

                if len(possible_symmetric_key) == 32:
                    symmetric_key = possible_symmetric_key
                    key_type = "256-bit symmetric key"
                else:
                    try:
                        private_key = serialization.load_pem_private_key(
                            uploaded_raw_key,
                            password=None
                        )
                    except (ValueError, TypeError):
                        return jsonify({
                            "success": False,
                            "error": (
                                "Invalid key format, or no supported "
                                "encryption metadata was found."
                            )
                        }), 400

                    key_type = "RSA-2048 private key"

        # ----------------------------------------------------
        # 9. SELECT THE DECRYPTION ALGORITHM
        # ----------------------------------------------------

        if encryption_algorithm == AES_ALGORITHM:
            if symmetric_key is None:
                return jsonify({
                    "success": False,
                    "error": "An AES symmetric key is required."
                }), 400

            aes_decrypt_file(
                temp_enc_path,
                decrypted_out_path,
                symmetric_key
            )

            actual_algorithm = AES_ALGORITHM

        elif encryption_algorithm == CHACHA_ALGORITHM:
            if symmetric_key is None:
                return jsonify({
                    "success": False,
                    "error": "A ChaCha20 symmetric key is required."
                }), 400

            chacha_decrypt_file(
                temp_enc_path,
                decrypted_out_path,
                symmetric_key
            )

            actual_algorithm = CHACHA_ALGORITHM

        elif encryption_algorithm == HYBRID_ALGORITHM:
            if private_key is None:
                return jsonify({
                    "success": False,
                    "error": "An RSA private key is required."
                }), 400

            hybrid_decrypt_file(
                temp_enc_path,
                decrypted_out_path,
                private_key
            )

            actual_algorithm = HYBRID_ALGORITHM

        elif symmetric_key is not None:
            # Legacy files without metadata: try the two symmetric
            # algorithms, then return an error if neither works.
            try:
                aes_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    symmetric_key
                )
                actual_algorithm = AES_ALGORITHM

            except Exception:
                cleanup_file(decrypted_out_path)

                chacha_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    symmetric_key
                )
                actual_algorithm = CHACHA_ALGORITHM

        elif private_key is not None:
            hybrid_decrypt_file(
                temp_enc_path,
                decrypted_out_path,
                private_key
            )

            actual_algorithm = HYBRID_ALGORITHM

        else:
            return jsonify({
                "success": False,
                "error": (
                    "Decryption could not proceed. "
                    "Check the encryption record and key."
                )
            }), 400

        # ----------------------------------------------------
        # 10. CONFIRM A DECRYPTED FILE WAS CREATED
        # ----------------------------------------------------

        if not os.path.isfile(decrypted_out_path):
            return jsonify({
                "success": False,
                "error": "Decryption did not produce an output file."
            }), 500

        # ----------------------------------------------------
        # 11. SAVE SUCCESS HISTORY FOR THIS USER
        # ----------------------------------------------------

        decryption_time_ms = (
            time.perf_counter() - decryption_start
        ) * 1000

        save_decryption_record(
            user_id=user_id,
            filename=original_filename,
            algorithm=actual_algorithm,
            key_type=key_type or "Uploaded key",
            processing_time_ms=round(
                decryption_time_ms,
                2
            ),
            status="Success"
        )

        # ----------------------------------------------------
        # 12. RETURN THE DECRYPTED FILE
        # ----------------------------------------------------

        response = create_decryption_response(
            decrypted_out_path,
            original_filename,
            actual_algorithm
        )

        # Keep the directory until Flask finishes sending
        # the file, then remove it.
        keep_temp_dir = True

        response.call_on_close(
            lambda: cleanup_directory(temp_dir)
        )

        return response

    except Exception:
        # Do not return internal filesystem paths, key details,
        # or cryptography exceptions to the client.
        current_app.logger.exception(
            "File decryption failed for an authenticated user."
        )

        return jsonify({
            "success": False,
            "error": (
                "Decryption failed. The key may be incorrect, "
                "the file may be corrupted, or its metadata may "
                "not match the encryption algorithm."
            )
        }), 400

    finally:
        # On failure, remove all temporary files immediately.
        # On success, response.call_on_close handles cleanup.
        if not keep_temp_dir:
            cleanup_directory(temp_dir)