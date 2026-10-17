import os
import time

from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    session
)

from werkzeug.utils import secure_filename

from auth_utils import login_required

# Feature extraction
from feature_extraction.text_extractor import extract_text
from feature_extraction.pii_detector import detect_pii
from feature_extraction.file_features import extract_file_features
from feature_extraction.system_features import extract_system_features
from feature_extraction.classifier import classify_document
from feature_extraction.sensitivity import calculate_sensitivity

# Machine learning
from models.predict import predict_encryption

# Key manager
from encryption.key_manager import generate_and_save_key

# AES-256-GCM
from encryption.aes import encrypt_file as aes_encrypt_file

# ChaCha20-Poly1305
from encryption.chacha20 import encrypt_file as chacha_encrypt_file

# Hybrid AES-256-GCM + RSA-OAEP
from encryption.hybrid import (
    generate_rsa_key_pair,
    save_rsa_keys,
    encrypt_file as hybrid_encrypt_file
)

# MongoDB encryption history
from routes.dashboard import save_encryption_record


upload_bp = Blueprint("upload", __name__)


# ============================================================
# DIRECTORY CONFIGURATION
# ============================================================

BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

UPLOAD_ROOT = os.path.join(BACKEND_DIR, "uploads")
ENCRYPTED_ROOT = os.path.join(UPLOAD_ROOT, "encrypted")


# ============================================================
# FILE / ML CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "txt", "png", "jpg", "jpeg"
}

SUPPORTED_ALGORITHMS = {
    "AES", "ChaCha20", "Hybrid"
}

CONFIDENCE_THRESHOLD = 0.60

ALGORITHM_DISPLAY_NAMES = {
    "AES": "AES-256-GCM",
    "ChaCha20": "ChaCha20-Poly1305",
    "Hybrid": "Hybrid AES-256-GCM + RSA-OAEP"
}

ALGORITHM_SECURITY_LEVELS = {
    "AES": "High",
    "ChaCha20": "High",
    "Hybrid": "Very High"
}


# ============================================================
# USER STORAGE HELPERS
# ============================================================

def get_user_id():
    """Return the ID belonging to the logged-in session."""
    return session.get("user_id")


def get_user_upload_folder(user_id):
    """Each user gets a separate original-file directory."""
    return os.path.join(UPLOAD_ROOT, str(user_id))


def get_user_encrypted_folder(user_id):
    """Each user gets a separate encrypted-file directory."""
    return os.path.join(ENCRYPTED_ROOT, str(user_id))


def get_key_identifier(user_id, filename):
    """
    Generate a unique filename for the existing key-manager
    functions, which currently identify keys by filename.

    The same identifier must also be used by decrypt.py.
    """
    return f"{user_id}_{filename}"


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ============================================================
# UPLOAD AND ENCRYPT
# ============================================================

@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    user_id = get_user_id()

    try:
        # 1. Validate uploaded file
        if "file" not in request.files:
            return jsonify({"error": "No file selected."}), 400

        uploaded_file = request.files["file"]

        if not uploaded_file.filename:
            return jsonify({"error": "No file selected."}), 400

        if not allowed_file(uploaded_file.filename):
            return jsonify({"error": "Unsupported file type."}), 400

        filename = secure_filename(uploaded_file.filename)

        if not filename:
            return jsonify({"error": "Invalid filename."}), 400

        # 2. Create user-specific directories
        user_upload_folder = get_user_upload_folder(user_id)
        user_encrypted_folder = get_user_encrypted_folder(user_id)

        os.makedirs(user_upload_folder, exist_ok=True)
        os.makedirs(user_encrypted_folder, exist_ok=True)

        # 3. Save original file in this user's folder
        filepath = os.path.join(user_upload_folder, filename)
        uploaded_file.save(filepath)

        original_size = os.path.getsize(filepath)

        # Existing key-manager functions use filenames to
        # locate keys. Prefix the filename with the user ID.
        key_identifier = get_key_identifier(user_id, filename)

        # 4. Extract text and analyze the document
        text = extract_text(filepath)
        pii = detect_pii(text)

        features = extract_file_features(text, pii)
        system_features = extract_system_features(filepath)
        classification = classify_document(text)

        sensitivity = calculate_sensitivity(
            features,
            classification,
            system_features
        )

        print("\n" + "=" * 60)
        print("AI-BASED ADAPTIVE ENCRYPTION SYSTEM")
        print("=" * 60)
        print("User ID:", user_id)
        print("Document Category:", classification.get("document_category"))
        print("PII Count:", sensitivity.get("pii_count"))
        print("Sensitivity Score:", sensitivity.get("sensitivity_score"))
        print("File Type:", system_features.get("file_type"))
        print("File Size MB:", system_features.get("file_size_mb"))
        print("CPU Usage:", system_features.get("cpu_usage"))
        print("RAM Usage:", system_features.get("ram_usage"))

        # 5. Machine-learning prediction
        ml_prediction = predict_encryption(
            features,
            classification,
            sensitivity,
            system_features
        )

        predicted_algorithm = ml_prediction.get("algorithm")
        ml_confidence = float(ml_prediction.get("confidence", 0))
        ml_probabilities = ml_prediction.get("probabilities", {})

        print("\nMACHINE LEARNING DECISION")
        print("-" * 60)
        print("Predicted Algorithm:", predicted_algorithm)
        print(f"Confidence: {ml_confidence * 100:.2f}%")
        print("Probabilities:", ml_probabilities)

        if predicted_algorithm not in SUPPORTED_ALGORITHMS:
            return jsonify({
                "error": "ML model returned an unsupported encryption algorithm."
            }), 500

        if ml_confidence < CONFIDENCE_THRESHOLD:
            return jsonify({
                "error": (
                    "ML confidence is below the required security threshold."
                ),
                "confidence": ml_confidence,
                "threshold": CONFIDENCE_THRESHOLD
            }), 400

        validation_status = "Approved"

        encryption_algorithm = ALGORITHM_DISPLAY_NAMES[
            predicted_algorithm
        ]

        security_level = ALGORITHM_SECURITY_LEVELS[
            predicted_algorithm
        ]

        decision_source = "ML Model"

        reason = (
            "Encryption algorithm selected automatically "
            "using the adaptive machine-learning model."
        )

        # 6. Set encrypted output path
        encrypted_filename = f"{filename}.enc"
        encrypted_path = os.path.join(
            user_encrypted_folder,
            encrypted_filename
        )

        # 7. Encrypt using the selected algorithm
        key_path = None
        public_key_path = None

        encryption_start = time.perf_counter()

        if predicted_algorithm == "AES":
            print("\nFinal Encryption: AES-256-GCM")

            key, key_path = generate_and_save_key(key_identifier)

            aes_encrypt_file(
                filepath,
                encrypted_path,
                key
            )

        elif predicted_algorithm == "ChaCha20":
            print("\nFinal Encryption: ChaCha20-Poly1305")

            key, key_path = generate_and_save_key(key_identifier)

            chacha_encrypt_file(
                filepath,
                encrypted_path,
                key
            )

        elif predicted_algorithm == "Hybrid":
            print("\nFinal Encryption: Hybrid AES-256-GCM + RSA-OAEP")

            private_key, public_key = generate_rsa_key_pair()

            key_path, public_key_path = save_rsa_keys(
                key_identifier,
                private_key,
                public_key
            )

            hybrid_encrypt_file(
                filepath,
                encrypted_path,
                public_key
            )

        encryption_time_ms = (
            time.perf_counter() - encryption_start
        ) * 1000

        # 8. Verify encrypted output exists
        if not os.path.isfile(encrypted_path):
            return jsonify({
                "error": "Encryption completed but encrypted file was not created."
            }), 500

        encrypted_size = os.path.getsize(encrypted_path)

        if original_size > 0:
            size_overhead_percent = (
                (encrypted_size - original_size) / original_size
            ) * 100
        else:
            size_overhead_percent = 0

        performance = {
            "original_size_bytes": original_size,
            "encrypted_size_bytes": encrypted_size,
            "encryption_time_ms": round(encryption_time_ms, 2),
            "size_overhead_percent": round(size_overhead_percent, 2),
            "algorithm": encryption_algorithm
        }

        # 9. Save history under the authenticated user's ID
        save_encryption_record(
            user_id=user_id,
            filename=filename,
            file_type=system_features.get("file_type"),
            file_size_mb=system_features.get("file_size_mb"),
            pii_count=sensitivity.get("pii_count", 0),
            sensitivity_score=sensitivity.get("sensitivity_score", 0),
            document_category=classification.get(
                "document_category",
                "General"
            ),
            ml_algorithm=predicted_algorithm,
            ml_confidence=ml_confidence,
            security_validation=validation_status,
            encryption_algorithm=encryption_algorithm,
            key_size=(
                "AES-256 + RSA-2048"
                if predicted_algorithm == "Hybrid"
                else "256-bit"
            ),
            processing_time_ms=round(encryption_time_ms, 2),
            status="Success"
        )

        print("\n" + "=" * 60)
        print("ENCRYPTION COMPLETED")
        print("=" * 60)
        print("User ID:", user_id)
        print("Filename:", filename)
        print("Algorithm:", encryption_algorithm)
        print(f"Encryption Time: {performance['encryption_time_ms']} ms")
        print("Original Size:", original_size, "bytes")
        print("Encrypted Size:", encrypted_size, "bytes")
        print(
            "Size Overhead:",
            f"{performance['size_overhead_percent']}%"
        )
        print("=" * 60)

        # 10. Return results to the frontend
        # Do not expose server-side key paths in the API response.
        return jsonify({
            "success": True,
            "message": "File uploaded and encrypted successfully.",
            "filename": filename,
            "extracted_text": text,
            "pii": pii,
            "features": features,
            "system_features": system_features,
            "classification": classification,
            "sensitivity": sensitivity,

            "ml_prediction": {
                "algorithm": predicted_algorithm,
                "display_algorithm": ml_prediction.get(
                    "display_algorithm",
                    encryption_algorithm
                ),
                "confidence": ml_confidence,
                "probabilities": ml_probabilities,
                "decision_source": decision_source,
                "validation_status": validation_status,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "input_features": ml_prediction.get(
                    "input_features",
                    {}
                )
            },

            "encryption": {
                "algorithm": encryption_algorithm,
                "security_level": security_level,
                "reason": reason,
                "decision_source": decision_source,
                "encrypted_file": encrypted_filename,
                "key_file": (
                    os.path.basename(key_path)
                    if key_path else None
                ),
                "public_key_file": (
                    os.path.basename(public_key_path)
                    if public_key_path else None
                )
            },

            "performance": performance
        }), 200

    except Exception as error:
        print("\nUPLOAD / ENCRYPTION ERROR")
        print(repr(error))

        return jsonify({
            "success": False,
            "error": "Upload or encryption failed. Check the backend terminal."
        }), 500


# ============================================================
# DOWNLOAD ENCRYPTED FILE
# ============================================================

@upload_bp.route("/download/<path:filename>", methods=["GET"])
@login_required
def download_file(filename):
    user_id = get_user_id()

    # Never accept a directory path from the URL.
    safe_filename = secure_filename(os.path.basename(filename))

    if not safe_filename or safe_filename != filename:
        return jsonify({"error": "Invalid filename."}), 400

    if not safe_filename.lower().endswith(".enc"):
        return jsonify({"error": "Invalid encrypted filename."}), 400

    user_encrypted_folder = get_user_encrypted_folder(user_id)
    encrypted_path = os.path.join(
        user_encrypted_folder,
        safe_filename
    )

    if not os.path.isfile(encrypted_path):
        return jsonify({
            "error": "Encrypted file not found for this account."
        }), 404

    return send_from_directory(
        user_encrypted_folder,
        safe_filename,
        as_attachment=True
    )
