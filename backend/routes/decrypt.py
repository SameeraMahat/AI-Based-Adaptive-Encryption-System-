from flask import Blueprint, request, jsonify, send_file
import os
import base64
import traceback
from cryptography.hazmat.primitives import serialization

# AES
from encryption.aes import decrypt_file as aes_decrypt_file

# ChaCha20
from encryption.chacha20 import decrypt_file as chacha_decrypt_file

# Hybrid
from encryption.hybrid import decrypt_file as hybrid_decrypt_file


decrypt_bp = Blueprint("decrypt", __name__)


@decrypt_bp.route("/decrypt", methods=["POST"])
def decrypt_file():
    """
    Decrypt an encrypted file.

    Required multipart/form-data:
        file = encrypted file
        key  = corresponding key file

    Supports:
        AES-256-GCM
        ChaCha20-Poly1305
        Hybrid AES-256-GCM + RSA-OAEP
    """

    # ========================================================
    # CHECK REQUIRED FILES
    # ========================================================

    if "file" not in request.files:
        return jsonify({
            "error": "Encrypted file is required."
        }), 400

    if "key" not in request.files:
        return jsonify({
            "error": "Key file is required."
        }), 400

    enc_file = request.files["file"]
    key_file = request.files["key"]

    if not enc_file.filename:
        return jsonify({
            "error": "Encrypted file name is missing."
        }), 400

    if not key_file.filename:
        return jsonify({
            "error": "Key file name is missing."
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
    # SAFE TEMP FILE NAMES
    # ========================================================

    encrypted_filename = os.path.basename(
        enc_file.filename
    )

    temp_enc_path = os.path.join(
        temp_dir,
        encrypted_filename
    )


    # ========================================================
    # ORIGINAL FILE NAME
    # ========================================================

    original_filename = encrypted_filename

    if original_filename.lower().endswith(".enc"):
        original_filename = original_filename[:-4]
    else:
        original_filename = (
            f"decrypted_{original_filename}"
        )


    decrypted_out_path = os.path.join(
        temp_dir,
        original_filename
    )


    try:

        # ====================================================
        # SAVE ENCRYPTED FILE
        # ====================================================

        enc_file.save(
            temp_enc_path
        )


        # ====================================================
        # READ KEY
        # ====================================================

        raw_key_bytes = key_file.read().strip()


        # ====================================================
        # 1. SYMMETRIC KEY DECRYPTION
        #
        # AES-256-GCM
        # ChaCha20-Poly1305
        # ====================================================

        decoded_key = None

        try:
            decoded_key = base64.b64decode(
                raw_key_bytes,
                validate=True
            )
        except Exception:
            decoded_key = raw_key_bytes


        # A valid AES/ChaCha key must be 32 bytes.
        if decoded_key and len(decoded_key) == 32:

            # ------------------------------------------------
            # TRY AES-256-GCM
            # ------------------------------------------------

            try:

                aes_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    decoded_key
                )

                print(
                    "Decryption successful: AES-256-GCM"
                )

                return send_file(
                    decrypted_out_path,
                    as_attachment=True,
                    download_name=original_filename,
                    mimetype="application/octet-stream"
                )

            except Exception:
                pass


            # ------------------------------------------------
            # TRY CHACHA20-POLY1305
            # ------------------------------------------------

            try:

                chacha_decrypt_file(
                    temp_enc_path,
                    decrypted_out_path,
                    decoded_key
                )

                print(
                    "Decryption successful: ChaCha20-Poly1305"
                )

                return send_file(
                    decrypted_out_path,
                    as_attachment=True,
                    download_name=original_filename,
                    mimetype="application/octet-stream"
                )

            except Exception:
                pass


        # ====================================================
        # 2. HYBRID DECRYPTION
        #
        # RSA PRIVATE KEY
        # ====================================================

        try:

            private_key = (
                serialization.load_pem_private_key(
                    raw_key_bytes,
                    password=None
                )
            )


            hybrid_decrypt_file(
                temp_enc_path,
                decrypted_out_path,
                private_key
            )


            print(
                "Decryption successful: "
                "Hybrid AES-256-GCM + RSA-OAEP"
            )


            return send_file(
                decrypted_out_path,
                as_attachment=True,
                download_name=original_filename,
                mimetype="application/octet-stream"
            )


        except Exception:
            pass


        # ====================================================
        # ALL DECRYPTION METHODS FAILED
        # ====================================================

        return jsonify({
            "error": (
                "Decryption failed. "
                "The key may be incorrect or the "
                "encrypted file format is invalid."
            )
        }), 400


    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "error": f"Decryption failed: {str(e)}"
        }), 400


    finally:

        # ====================================================
        # CLEAN TEMP ENCRYPTED FILE
        # ====================================================

        if os.path.exists(
            temp_enc_path
        ):
            try:
                os.remove(
                    temp_enc_path
                )
            except Exception:
                pass