from flask import (
    Blueprint,
    request,
    jsonify,
    send_file
)

import os
import base64
import time
import traceback

from datetime import datetime, timezone

from cryptography.hazmat.primitives import serialization
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app

from database.mongodb import (
    decryption_history_collection,
    encryption_history_collection
)

# AES
from encryption.aes import (
    decrypt_file as aes_decrypt_file
)

# ChaCha20
from encryption.chacha20 import (
    decrypt_file as chacha_decrypt_file
)

# Hybrid
from encryption.hybrid import (
    decrypt_file as hybrid_decrypt_file,
    load_private_key
)

# Stored symmetric key
from encryption.key_manager import (
    load_key
)


decrypt_bp = Blueprint(
    "decrypt",
    __name__
)
from database.mongodb import (
    encryption_history_collection,
    decryption_history_collection,
)

# ============================================================
# TEMPORARY USER ID
# ============================================================

DEMO_USER_ID = "demo-user"

def verify_decrypt_token():
    token = request.headers.get("X-Decrypt-Token", "").strip()

    if not token:
        return None, (
            jsonify({
                "success": False,
                "error": "Password verification required."
            }),
            401
        )

    secret_key = current_app.config.get("SECRET_KEY")
    if not secret_key:
        return None, (
            jsonify({
                "success": False,
                "error": "Server security configuration error."
            }),
            500
        )

    serializer = URLSafeTimedSerializer(secret_key)

    try:
        payload = serializer.loads(
            token,
            salt="decrypt-authorization",
            max_age=300
        )
    except SignatureExpired:
        return None, (
            jsonify({
                "success": False,
                "error": "Verification expired. Enter your password again."
            }),
            401
        )
    except BadSignature:
        return None, (
            jsonify({
                "success": False,
                "error": "Invalid verification token."
            }),
            401
        )

    if (
        not isinstance(payload, dict)
        or payload.get("purpose") != "decrypt"
        or not payload.get("user_id")
        or not payload.get("email")
    ):
        return None, (
            jsonify({
                "success": False,
                "error": "Invalid verification token."
            }),
            401
        )

    return payload, None



# ============================================================
# ALGORITHM NAMES
# ============================================================

AES_ALGORITHM = "AES-256-GCM"

CHACHA_ALGORITHM = "ChaCha20-Poly1305"

HYBRID_ALGORITHM = (
    "Hybrid AES-256-GCM + RSA-OAEP"
)


# ============================================================
# SAVE DECRYPTION DATABASE RECORD
# ============================================================

def save_decryption_record(
    user_id,
    filename,
    algorithm,
    key_type,
    processing_time_ms,
    status
):
    """
    Save successful decryption information
    into MongoDB.
    """

    decryption_record = {
        "user_id": user_id,
        "filename": filename,
        "algorithm": algorithm,
        "key_type": key_type,
        "processing_time_ms": processing_time_ms,
        "status": status,
        "created_at": datetime.now(timezone.utc)
    }

    result = (
        decryption_history_collection
        .insert_one(decryption_record)
    )

    return result.inserted_id


# ============================================================
# SERIALIZE DECRYPTION HISTORY
# ============================================================

def serialize_decryption_record(record):

    record["id"] = str(
        record.pop("_id")
    )

    if isinstance(
        record.get("created_at"),
        datetime
    ):
        record["created_at"] = (
            record["created_at"]
            .isoformat()
        )

    return record

    
def fetch_history():
    history = []

    # Encryption records
    for record in encryption_history_collection.find({
        "user_id": DEMO_USER_ID
    }):
        record = serialize_uploaded_file(record)
        record["type"] = "encryption"
        record["algorithm"] = record.get(
            "encryption_algorithm", "Unknown"
        )
        history.append(record)

    # Decryption records
    for record in decryption_history_collection.find({
        "user_id": DEMO_USER_ID
    }):
        record = serialize_decryption_record(record)
        record["type"] = "decryption"
        record["algorithm"] = record.get(
            "algorithm", "Unknown"
        )
        history.append(record)

    history.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True
    )

    return history



# ============================================================
# DECRYPTION HISTORY
# ============================================================

@decrypt_bp.route(
    "/decrypt/history",
    methods=["GET"]
)
def get_decryption_history():

    records = (
        decryption_history_collection
        .find({
            "user_id": DEMO_USER_ID
        })
        .sort(
            "created_at",
            -1
        )
    )

    history = []

    for record in records:

        history.append(
            serialize_decryption_record(
                record
            )
        )

    return jsonify({
        "success": True,
        "history": history
    }), 200


# ============================================================
# GET ENCRYPTION METADATA
# ============================================================

def get_encryption_record(filename):
    print("=== DECRYPT RECORD DEBUG ===")
    print("Filename received:", repr(filename))
    print("Expected user_id:", repr(DEMO_USER_ID))

    records = list(
        encryption_history_collection.find(
            {},
            {
                "_id": 0,
                "user_id": 1,
                "filename": 1,
                "encryption_algorithm": 1
            }
        ).sort("created_at", -1).limit(10)
    )

    print("Recent encryption records:", records)

    record = encryption_history_collection.find_one({
        "user_id": DEMO_USER_ID,
        "filename": filename
    })

    print("Exact matching record:", record)
    print("============================")

    return record

# ============================================================
# LOAD STORED DECRYPTION KEY
# ============================================================

def load_stored_decryption_key(
    original_filename,
    encryption_algorithm
):
    """
    Load the correct server-side key according
    to the algorithm used during encryption.

    AES / ChaCha20:
        backend/keys/<filename>.key

    Hybrid:
        backend/keys/hybrid/<filename>.private.pem

    The exact file locations are handled by the
    existing key_manager / hybrid modules.
    """

    # --------------------------------------------------------
    # AES-256-GCM
    # --------------------------------------------------------

    if encryption_algorithm == AES_ALGORITHM:

        stored_key = load_key(
            original_filename
        )

        return (
            stored_key,
            "256-bit symmetric key"
        )


    # --------------------------------------------------------
    # ChaCha20-Poly1305
    # --------------------------------------------------------

    if encryption_algorithm == CHACHA_ALGORITHM:

        stored_key = load_key(
            original_filename
        )

        return (
            stored_key,
            "256-bit symmetric key"
        )


    # --------------------------------------------------------
    # Hybrid AES-256-GCM + RSA-OAEP
    # --------------------------------------------------------

    if encryption_algorithm == HYBRID_ALGORITHM:

        private_key = load_private_key(
            original_filename
        )

        return (
            private_key,
            "RSA-2048 private key"
        )


    raise ValueError(
        "Unsupported encryption algorithm."
    )


# ============================================================
# SEND SUCCESSFUL DECRYPTED FILE
# ============================================================

def create_decryption_response(
    decrypted_out_path,
    original_filename,
    algorithm
):
    """
    Create the decrypted-file response and expose
    the actual algorithm to the frontend.
    """

    response = send_file(
        decrypted_out_path,
        as_attachment=True,
        download_name=original_filename,
        mimetype="application/octet-stream"
    )

    response.headers[
        "X-Decryption-Algorithm"
    ] = algorithm

    response.headers[
        "X-Decryption-Status"
    ] = "Success"

    response.headers[
        "X-Original-Filename"
    ] = original_filename

    return response


# ============================================================
# CLEANUP HELPER
# ============================================================

def cleanup_file(file_path):

    if not file_path:
        return

    if os.path.exists(file_path):

        try:
            os.remove(file_path)

        except Exception:
            pass


# ============================================================
# DECRYPT FILE
# ============================================================

@decrypt_bp.route(
    "/decrypt",
    methods=["POST"]
)
def decrypt_file():
    # Require password verification before decryption.
    verified_user, auth_error = verify_decrypt_token()

    if auth_error:
        return auth_error

    # Existing CHECK ENCRYPTED FILE code continues below...

    # ========================================================
    # CHECK ENCRYPTED FILE
    # ========================================================

    if "file" not in request.files:

        return jsonify({
            "error":
                "Encrypted file is required."
        }), 400


    enc_file = request.files["file"]


    if not enc_file.filename:

        return jsonify({
            "error":
                "Encrypted file name is missing."
        }), 400


    # ========================================================
    # DETERMINE KEY SOURCE
    # ========================================================

    key_source = request.form.get(
        "key_source",
        "upload"
    ).strip().lower()


    if key_source not in {
        "upload",
        "stored"
    }:

        return jsonify({
            "error":
                "Invalid key source."
        }), 400


    # ========================================================
    # VALIDATE UPLOADED KEY
    # ========================================================

    key_file = None

    if key_source == "upload":

        if "key" not in request.files:

            return jsonify({
                "error":
                    "Key file is required."
            }), 400

        key_file = request.files["key"]

        if not key_file.filename:

            return jsonify({
                "error":
                    "Key file name is missing."
            }), 400


    # ========================================================
    # TEMP DIRECTORY
    # ========================================================

    temp_dir = os.path.join(
        os.getcwd(),
        "temp_decrypted"
    )

    os.makedirs(
        temp_dir,
        exist_ok=True
    )


    # ========================================================
    # SAFE ENCRYPTED FILE NAME
    # ========================================================

    encrypted_filename = os.path.basename(
        enc_file.filename
    )


    if not encrypted_filename.lower().endswith(
        ".enc"
    ):

        return jsonify({
            "error":
                "Unsupported encrypted file."
        }), 400


    # ========================================================
    # TEMP ENCRYPTED FILE
    # ========================================================

    temp_enc_path = os.path.join(
        temp_dir,
        encrypted_filename
    )


    # ========================================================
    # ORIGINAL FILE NAME
    # ========================================================

    original_filename = (
        encrypted_filename[:-4]
    )


    decrypted_out_path = os.path.join(
        temp_dir,
        original_filename
    )


    # ========================================================
    # START TIMER
    # ========================================================

    decryption_start = time.perf_counter()


    # These variables are populated depending
    # on the selected key source.

    encryption_algorithm = None
    key_type = None

    symmetric_key = None
    private_key = None

    uploaded_raw_key = None

    response = None


    try:

        # ====================================================
        # SAVE ENCRYPTED FILE TEMPORARILY
        # ====================================================

        enc_file.save(
            temp_enc_path
        )


        # ====================================================
        # GET ENCRYPTION RECORD
        # ====================================================

        encryption_record = (
            get_encryption_record(
                original_filename
            )
        )


        if encryption_record:

            encryption_algorithm = (
                encryption_record.get(
                    "encryption_algorithm"
                )
            )


        # ====================================================
        # STORED KEY MODE
        # ====================================================

        if key_source == "stored":

            # ------------------------------------------------
            # Encryption record is required because the
            # backend must know which stored key belongs
            # to this encrypted file.
            # ------------------------------------------------

            if not encryption_record:

                return jsonify({
                    "error":
                        "No encryption record was found "
                        "for this file. The stored key "
                        "cannot be located."
                }), 404


            if not encryption_algorithm:

                return jsonify({
                    "error":
                        "Encryption algorithm information "
                        "is missing for this file."
                }), 500


            # ------------------------------------------------
            # Load exact server-side key
            # ------------------------------------------------

            try:

                stored_key, key_type = (
                    load_stored_decryption_key(
                        original_filename,
                        encryption_algorithm
                    )
                )

            except FileNotFoundError:

                return jsonify({
                    "error":
                        "The stored decryption key "
                        "could not be found on the server."
                }), 404

            except ValueError as error:

                return jsonify({
                    "error":
                        str(error)
                }), 400

            except Exception as error:

                return jsonify({
                    "error":
                        "Unable to load stored key: "
                        f"{str(error)}"
                }), 500


            # ------------------------------------------------
            # Symmetric stored key
            # ------------------------------------------------

            if encryption_algorithm in {
                AES_ALGORITHM,
                CHACHA_ALGORITHM
            }:

                symmetric_key = stored_key


            # ------------------------------------------------
            # Hybrid stored private key
            # ------------------------------------------------

            elif encryption_algorithm == HYBRID_ALGORITHM:

                private_key = stored_key


        # ====================================================
        # UPLOADED KEY MODE
        # ====================================================

        else:

            uploaded_raw_key = (
                key_file.read().strip()
            )


            if not uploaded_raw_key:

                return jsonify({
                    "error":
                        "Please provide the required "
                        "decryption key."
                }), 400


            # ------------------------------------------------
            # If encryption metadata exists, use the exact
            # algorithm recorded during encryption.
            #
            # Otherwise preserve compatibility with the
            # previous implementation by detecting the key.
            # ------------------------------------------------

            if encryption_algorithm in {
                AES_ALGORITHM,
                CHACHA_ALGORITHM
            }:

                try:

                    symmetric_key = (
                        base64.b64decode(
                            uploaded_raw_key,
                            validate=True
                        )
                    )

                except Exception:

                    symmetric_key = (
                        uploaded_raw_key
                    )


                if not symmetric_key:

                    return jsonify({
                        "error":
                            "Invalid encryption key."
                    }), 400


                key_type = (
                    "256-bit symmetric key"
                )


            elif encryption_algorithm == HYBRID_ALGORITHM:

                try:

                    private_key = (
                        serialization
                        .load_pem_private_key(
                            uploaded_raw_key,
                            password=None
                        )
                    )

                except Exception:

                    return jsonify({
                        "error":
                            "Invalid RSA private key."
                    }), 400


                key_type = (
                    "RSA-2048 private key"
                )


            else:

                # ------------------------------------------------
                # No metadata available.
                #
                # First try a Base64/raw 32-byte symmetric key.
                # If that does not work, try RSA private key.
                # ------------------------------------------------

                try:

                    symmetric_key = (
                        base64.b64decode(
                            uploaded_raw_key,
                            validate=True
                        )
                    )

                except Exception:

                    symmetric_key = (
                        uploaded_raw_key
                    )


                if (
                    not symmetric_key
                    or
                    not isinstance(
                        symmetric_key,
                        bytes
                    )
                    or
                    len(symmetric_key) != 32
                ):

                    symmetric_key = None


                if symmetric_key:

                    key_type = (
                        "256-bit symmetric key"
                    )

                else:

                    try:

                        private_key = (
                            serialization
                            .load_pem_private_key(
                                uploaded_raw_key,
                                password=None
                            )
                        )

                    except Exception:

                        return jsonify({
                            "error":
                                "Invalid encryption key."
                        }), 400

                    key_type = (
                        "RSA-2048 private key"
                    )


        # ====================================================
        # 1. AES-256-GCM
        # ====================================================

        if (
            encryption_algorithm == AES_ALGORITHM
            and
            symmetric_key is not None
        ):

            try:

                aes_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    symmetric_key
                )

            except Exception:

                return jsonify({
                    "error":
                        "Invalid encryption key or "
                        "corrupted encrypted file."
                }), 400


            decryption_time_ms = (
                time.perf_counter()
                -
                decryption_start
            ) * 1000


            save_decryption_record(
                user_id=DEMO_USER_ID,
                filename=original_filename,
                algorithm=AES_ALGORITHM,
                key_type=key_type,
                processing_time_ms=round(
                    decryption_time_ms,
                    2
                ),
                status="Success"
            )


            response = create_decryption_response(
                decrypted_out_path,
                original_filename,
                AES_ALGORITHM
            )

            # Encrypted temporary file is no longer needed.
            cleanup_file(temp_enc_path)

            # The decrypted file is cleaned after the response
            # is closed.
            response.call_on_close(
                lambda: cleanup_file(
                    decrypted_out_path
                )
            )

            return response


        # ====================================================
        # 2. CHACHA20-POLY1305
        # ====================================================

        if (
            encryption_algorithm == CHACHA_ALGORITHM
            and
            symmetric_key is not None
        ):

            try:

                chacha_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    symmetric_key
                )

            except Exception:

                return jsonify({
                    "error":
                        "Invalid encryption key or "
                        "corrupted encrypted file."
                }), 400


            decryption_time_ms = (
                time.perf_counter()
                -
                decryption_start
            ) * 1000


            save_decryption_record(
                user_id=DEMO_USER_ID,
                filename=original_filename,
                algorithm=CHACHA_ALGORITHM,
                key_type=key_type,
                processing_time_ms=round(
                    decryption_time_ms,
                    2
                ),
                status="Success"
            )


            response = create_decryption_response(
                decrypted_out_path,
                original_filename,
                CHACHA_ALGORITHM
            )

            cleanup_file(temp_enc_path)

            response.call_on_close(
                lambda: cleanup_file(
                    decrypted_out_path
                )
            )

            return response


        # ====================================================
        # 3. HYBRID AES-256-GCM + RSA-OAEP
        # ====================================================

        if (
            encryption_algorithm == HYBRID_ALGORITHM
            and
            private_key is not None
        ):

            try:

                hybrid_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    private_key
                )

            except Exception:

                return jsonify({
                    "error":
                        "Invalid RSA private key or "
                        "corrupted encrypted file."
                }), 400


            decryption_time_ms = (
                time.perf_counter()
                -
                decryption_start
            ) * 1000


            save_decryption_record(
                user_id=DEMO_USER_ID,
                filename=original_filename,
                algorithm=HYBRID_ALGORITHM,
                key_type=key_type,
                processing_time_ms=round(
                    decryption_time_ms,
                    2
                ),
                status="Success"
            )


            response = create_decryption_response(
                decrypted_out_path,
                original_filename,
                HYBRID_ALGORITHM
            )

            cleanup_file(temp_enc_path)

            response.call_on_close(
                lambda: cleanup_file(
                    decrypted_out_path
                )
            )

            return response


        # ====================================================
        # LEGACY FALLBACK
        # ====================================================
        #
        # This is used only when there is no encryption
        # metadata for the selected file.
        #
        # It keeps compatibility with encrypted files that
        # may have existed before the encryption history
        # lookup was introduced.
        # ====================================================

        if (
            not encryption_algorithm
            and
            symmetric_key is not None
        ):

            # ------------------------------------------------
            # Try AES
            # ------------------------------------------------

            try:

                aes_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    symmetric_key
                )

                actual_algorithm = AES_ALGORITHM

            except Exception:

                # ------------------------------------------------
                # Try ChaCha20
                # ------------------------------------------------

                try:

                    chacha_decrypt_file(
                        temp_enc_path,
                        decrypted_out_path,
                        symmetric_key
                    )

                    actual_algorithm = (
                        CHACHA_ALGORITHM
                    )

                except Exception:

                    actual_algorithm = None


            if actual_algorithm:

                decryption_time_ms = (
                    time.perf_counter()
                    -
                    decryption_start
                ) * 1000


                save_decryption_record(
                    user_id=DEMO_USER_ID,
                    filename=original_filename,
                    algorithm=actual_algorithm,
                    key_type=(
                        key_type
                        or
                        "256-bit symmetric key"
                    ),
                    processing_time_ms=round(
                        decryption_time_ms,
                        2
                    ),
                    status="Success"
                )


                response = create_decryption_response(
                    decrypted_out_path,
                    original_filename,
                    actual_algorithm
                )

                cleanup_file(
                    temp_enc_path
                )

                response.call_on_close(
                    lambda: cleanup_file(
                        decrypted_out_path
                    )
                )

                return response


        # ====================================================
        # LEGACY HYBRID FALLBACK
        # ====================================================

        if (
            not encryption_algorithm
            and
            private_key is not None
        ):

            try:

                hybrid_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    private_key
                )

            except Exception:

                return jsonify({
                    "error":
                        "Invalid encryption key or "
                        "corrupted encrypted file."
                }), 400


            decryption_time_ms = (
                time.perf_counter()
                -
                decryption_start
            ) * 1000


            save_decryption_record(
                user_id=DEMO_USER_ID,
                filename=original_filename,
                algorithm=HYBRID_ALGORITHM,
                key_type=(
                    key_type
                    or
                    "RSA-2048 private key"
                ),
                processing_time_ms=round(
                    decryption_time_ms,
                    2
                ),
                status="Success"
            )


            response = create_decryption_response(
                decrypted_out_path,
                original_filename,
                HYBRID_ALGORITHM
            )

            cleanup_file(
                temp_enc_path
            )

            response.call_on_close(
                lambda: cleanup_file(
                    decrypted_out_path
                )
            )

            return response


        # ====================================================
        # NO METHOD SUCCEEDED
        # ====================================================

        return jsonify({
            "error":
                "Decryption failed. The encryption "
                "metadata or key is invalid."
        }), 400


    except Exception as error:

        traceback.print_exc()

        return jsonify({
            "error":
                f"Decryption failed: {str(error)}"
        }), 400


    finally:

        # ====================================================
        # CLEANUP ENCRYPTED TEMP FILE
        # ====================================================
        #
        # On successful decryption this was already removed.
        # This handles errors and early failures.
        # ====================================================

        cleanup_file(
            temp_enc_path
        )

        # Do NOT remove decrypted_out_path here on success.
        #
        # It is attached to response.call_on_close() so the
        # browser has time to receive the file first.