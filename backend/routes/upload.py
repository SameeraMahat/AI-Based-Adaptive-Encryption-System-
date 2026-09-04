from flask import Blueprint, request, jsonify, send_from_directory
import os
import time
from werkzeug.utils import secure_filename

from feature_extraction.text_extractor import extract_text
from feature_extraction.pii_detector import detect_pii
from feature_extraction.file_features import extract_file_features
from feature_extraction.system_features import extract_system_features
from feature_extraction.classifier import classify_document
from feature_extraction.sensitivity import calculate_sensitivity

# ML prediction
from models.predict import predict_encryption

# Key manager
from encryption.key_manager import generate_and_save_key

# AES
from encryption.aes import encrypt_file as aes_encrypt_file

# ChaCha20
from encryption.chacha20 import encrypt_file as chacha_encrypt_file

# Hybrid
from encryption.hybrid import (
    generate_rsa_key_pair,
    save_rsa_keys,
    encrypt_file as hybrid_encrypt_file
)


upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt",
    "png",
    "jpg",
    "jpeg"
}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@upload_bp.route("/upload", methods=["POST"])
def upload_file():

    # --------------------------------
    # FILE VALIDATION
    # --------------------------------

    if "file" not in request.files:
        return jsonify({
            "error": "No file selected."
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file type."
        }), 400

    # --------------------------------
    # SAVE UPLOADED FILE
    # --------------------------------

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    # Original file size
    original_size = os.path.getsize(filepath)

    # --------------------------------
    # FEATURE EXTRACTION PIPELINE
    # --------------------------------

    # 1. Extract text / OCR
    text = extract_text(filepath)

    # 2. Detect PII
    pii = detect_pii(text)

    # 3. Extract file/text features
    features = extract_file_features(
        text,
        pii
    )

    # 4. Extract system/file features
    system_features = extract_system_features(
        filepath
    )

    # 5. Classify document
    classification = classify_document(
        text
    )

    # 6. Calculate sensitivity features
    sensitivity = calculate_sensitivity(
        features,
        classification,
        system_features
    )

    # --------------------------------
    # AI / ML ENCRYPTION PREDICTION
    # --------------------------------

    ml_prediction = predict_encryption(
        features,
        classification,
        sensitivity,
        system_features
    )

    predicted_algorithm = ml_prediction["algorithm"]

    # --------------------------------
    # ENCRYPTION SETUP
    # --------------------------------

    encrypted_folder = os.path.join(
        UPLOAD_FOLDER,
        "encrypted"
    )

    os.makedirs(
        encrypted_folder,
        exist_ok=True
    )

    encrypted_filename = filename + ".enc"

    encrypted_path = os.path.join(
        encrypted_folder,
        encrypted_filename
    )

    key_path = None
    public_key_path = None

    # --------------------------------
    # START ENCRYPTION TIMER
    # --------------------------------

    encryption_start = time.perf_counter()

    # --------------------------------
    # AES-256-GCM
    # --------------------------------

    if predicted_algorithm == "AES":

        encryption_algorithm = "AES-256-GCM"
        security_level = "High"

        reason = (
            "Random Forest selected AES based on the "
            "extracted file, system, PII, classification, "
            "and sensitivity features."
        )

        # Generate 256-bit AES key
        key, key_path = generate_and_save_key(
            filename
        )

        # Encrypt file
        aes_encrypt_file(
            filepath,
            encrypted_path,
            key
        )

    # --------------------------------
    # CHACHA20
    # --------------------------------

    elif predicted_algorithm == "ChaCha20":

        encryption_algorithm = "ChaCha20"
        security_level = "Medium"

        reason = (
            "Random Forest selected ChaCha20 based on the "
            "extracted file, system, PII, classification, "
            "and sensitivity features."
        )

        # Generate 256-bit ChaCha20 key
        key, key_path = generate_and_save_key(
            filename
        )

        # Encrypt file
        chacha_encrypt_file(
            filepath,
            encrypted_path,
            key
        )

    # --------------------------------
    # HYBRID AES-256-GCM + RSA-OAEP
    # --------------------------------

    elif predicted_algorithm == "Hybrid":

        encryption_algorithm = (
            "Hybrid AES-256-GCM + RSA-OAEP"
        )

        security_level = "Very High"

        reason = (
            "Random Forest selected Hybrid encryption "
            "based on the predicted security requirements "
            "of the uploaded file."
        )

        # Generate RSA-2048 key pair
        private_key, public_key = generate_rsa_key_pair()

        # Save RSA keys
        key_path, public_key_path = save_rsa_keys(
            filename,
            private_key,
            public_key
        )

        # Encrypt file
        hybrid_encrypt_file(
            filepath,
            encrypted_path,
            public_key
        )

    # --------------------------------
    # UNSUPPORTED ML PREDICTION
    # --------------------------------

    else:

        return jsonify({
            "error": (
                f"Unsupported ML prediction: "
                f"{predicted_algorithm}"
            )
        }), 400

    # --------------------------------
    # STOP ENCRYPTION TIMER
    # --------------------------------

    encryption_time_ms = (
        time.perf_counter() - encryption_start
    ) * 1000

    # --------------------------------
    # ENCRYPTED FILE SIZE
    # --------------------------------

    encrypted_size = os.path.getsize(
        encrypted_path
    )

    # --------------------------------
    # SIZE OVERHEAD
    # --------------------------------

    if original_size > 0:

        size_overhead_percent = (
            (encrypted_size - original_size)
            / original_size
        ) * 100

    else:

        size_overhead_percent = 0

    # --------------------------------
    # PERFORMANCE DATA
    # --------------------------------

    performance = {

        "original_size_bytes":
            original_size,

        "encrypted_size_bytes":
            encrypted_size,

        "encryption_time_ms":
            round(encryption_time_ms, 2),

        "size_overhead_percent":
            round(size_overhead_percent, 2),

        "algorithm":
            encryption_algorithm
    }

    # --------------------------------
    # RESPONSE
    # --------------------------------

    return jsonify({

        "message":
            "File uploaded and encrypted successfully.",

        "filename":
            filename,

        # --------------------------------
        # EXTRACTED INFORMATION
        # --------------------------------

        "extracted_text":
            text,

        "pii":
            pii,

        "features":
            features,

        "system_features":
            system_features,

        "classification":
            classification,

        "sensitivity":
            sensitivity,

        # --------------------------------
        # ML DECISION
        # --------------------------------

        "ml_prediction": {

            "algorithm":
                ml_prediction["algorithm"],

            "confidence":
                ml_prediction["confidence"],

            "probabilities":
                ml_prediction["probabilities"]
        },

        # --------------------------------
        # ACTUAL ENCRYPTION
        # --------------------------------

        "encryption": {

            "algorithm":
                encryption_algorithm,

            "security_level":
                security_level,

            "reason":
                reason,

            "encrypted_file":
                encrypted_filename,

            "key_file":
                key_path
        },

        # --------------------------------
        # PERFORMANCE
        # --------------------------------

        "performance":
            performance

    }), 200


# --------------------------------
# DOWNLOAD ENCRYPTED FILE
# --------------------------------

@upload_bp.route(
    "/download/<filename>",
    methods=["GET"]
)
def download_file(filename):

    encrypted_folder = os.path.join(
        UPLOAD_FOLDER,
        "encrypted"
    )

    return send_from_directory(
        encrypted_folder,
        filename,
        as_attachment=True
    )