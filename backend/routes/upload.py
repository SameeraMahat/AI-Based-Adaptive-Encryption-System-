from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory
)

import os
import time

from werkzeug.utils import secure_filename


# ============================================================
# FEATURE EXTRACTION
# ============================================================

from feature_extraction.text_extractor import extract_text
from feature_extraction.pii_detector import detect_pii
from feature_extraction.file_features import extract_file_features
from feature_extraction.system_features import extract_system_features
from feature_extraction.classifier import classify_document
from feature_extraction.sensitivity import calculate_sensitivity


# ============================================================
# MACHINE LEARNING
# ============================================================

from models.predict import predict_encryption


# ============================================================
# KEY MANAGER
# ============================================================

from encryption.key_manager import generate_and_save_key


# ============================================================
# AES-256-GCM
# ============================================================

from encryption.aes import (
    encrypt_file as aes_encrypt_file
)


# ============================================================
# CHACHA20-POLY1305
# ============================================================

from encryption.chacha20 import (
    encrypt_file as chacha_encrypt_file
)


# ============================================================
# HYBRID AES-256-GCM + RSA-OAEP
# ============================================================

from encryption.hybrid import (
    generate_rsa_key_pair,
    save_rsa_keys,
    encrypt_file as hybrid_encrypt_file
)


# ============================================================
# BLUEPRINT
# ============================================================

upload_bp = Blueprint(
    "upload",
    __name__
)


# ============================================================
# DIRECTORY CONFIGURATION
# ============================================================

BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_FOLDER = os.path.join(
    BACKEND_DIR,
    "uploads"
)

ENCRYPTED_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "encrypted"
)


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt",
    "png",
    "jpg",
    "jpeg"
}


# ============================================================
# ML CONFIGURATION
# ============================================================

SUPPORTED_ALGORITHMS = {
    "AES",
    "ChaCha20",
    "Hybrid"
}

CONFIDENCE_THRESHOLD = 0.60


# ============================================================
# DISPLAY NAMES
# ============================================================

ALGORITHM_DISPLAY_NAMES = {
    "AES": "AES-256-GCM",
    "ChaCha20": "ChaCha20-Poly1305",
    "Hybrid": "Hybrid AES-256-GCM + RSA-OAEP"
}


# ============================================================
# SECURITY LEVELS
# ============================================================

ALGORITHM_SECURITY_LEVELS = {
    "AES": "High",
    "ChaCha20": "High",
    "Hybrid": "Very High"
}


# ============================================================
# FILE VALIDATION
# ============================================================

def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.
    """

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# UPLOAD ROUTE
# ============================================================

@upload_bp.route(
    "/upload",
    methods=["POST"]
)
def upload_file():

    try:

        # ====================================================
        # 1. FILE VALIDATION
        # ====================================================

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


        # ====================================================
        # 2. CREATE DIRECTORIES
        # ====================================================

        os.makedirs(
            UPLOAD_FOLDER,
            exist_ok=True
        )

        os.makedirs(
            ENCRYPTED_FOLDER,
            exist_ok=True
        )


        # ====================================================
        # 3. SECURE FILENAME
        # ====================================================

        filename = secure_filename(
            file.filename
        )


        if not filename:

            return jsonify({
                "error": "Invalid filename."
            }), 400


        # ====================================================
        # 4. SAVE ORIGINAL FILE
        # ====================================================

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )


        file.save(
            filepath
        )


        original_size = os.path.getsize(
            filepath
        )


        # ====================================================
        # 5. TEXT EXTRACTION / OCR
        # ====================================================

        text = extract_text(
            filepath
        )


        # ====================================================
        # 6. PII DETECTION
        # ====================================================

        pii = detect_pii(
            text
        )


        # ====================================================
        # 7. FILE + TEXT FEATURES
        # ====================================================

        features = extract_file_features(
            text,
            pii
        )


        # ====================================================
        # 8. SYSTEM FEATURES
        # ====================================================

        system_features = extract_system_features(
            filepath
        )


        # ====================================================
        # 9. DOCUMENT CLASSIFICATION
        # ====================================================

        classification = classify_document(
            text
        )


        # ====================================================
        # 10. SENSITIVITY CALCULATION
        # ====================================================

        sensitivity = calculate_sensitivity(
            features,
            classification,
            system_features
        )


        # ====================================================
        # TERMINAL ANALYSIS OUTPUT
        # ====================================================

        print()
        print("=" * 60)
        print("        AI-BASED ADAPTIVE ENCRYPTION SYSTEM")
        print("=" * 60)

        print(
            "Document Category:",
            classification.get(
                "document_category"
            )
        )

        print(
            "Category Confidence:",
            classification.get(
                "category_confidence"
            )
        )

        print(
            "PII Count:",
            sensitivity.get(
                "pii_count"
            )
        )

        print(
            "Confidential Keywords:",
            sensitivity.get(
                "confidential_keyword_count"
            )
        )

        print(
            "Confidential Marker:",
            sensitivity.get(
                "confidential_marker"
            )
        )

        print(
            "Sensitivity Score:",
            sensitivity.get(
                "sensitivity_score"
            )
        )

        print(
            "File Type:",
            system_features.get(
                "file_type"
            )
        )

        print(
            "File Size MB:",
            system_features.get(
                "file_size_mb"
            )
        )

        print(
            "CPU Usage:",
            system_features.get(
                "cpu_usage"
            )
        )

        print(
            "RAM Usage:",
            system_features.get(
                "ram_usage"
            )
        )


        # ====================================================
        # 11. MACHINE LEARNING PREDICTION
        # ====================================================

        ml_prediction = predict_encryption(
            features,
            classification,
            sensitivity,
            system_features
        )


        predicted_algorithm = ml_prediction.get(
            "algorithm"
        )


        ml_confidence = float(
            ml_prediction.get(
                "confidence",
                0
            )
        )


        ml_probabilities = ml_prediction.get(
            "probabilities",
            {}
        )


        print()
        print("-" * 60)
        print("MACHINE LEARNING DECISION")
        print("-" * 60)

        print(
            "ML Prediction:",
            predicted_algorithm
        )

        print(
            "ML Display Algorithm:",
            ml_prediction.get(
                "display_algorithm"
            )
        )

        print(
            "ML Confidence:",
            ml_confidence
        )

        print(
            "ML Probabilities:",
            ml_probabilities
        )

        print(
            "Decision Source:",
            ml_prediction.get(
                "decision_source",
                "Random Forest ML Model"
            )
        )


        # ====================================================
        # 12. ML SAFETY VALIDATION
        # ====================================================

        validation_status = "Approved"

        decision_source = (
            "Random Forest ML Model"
        )


        # ----------------------------------------------------
        # Validate algorithm
        # ----------------------------------------------------

        if predicted_algorithm not in SUPPORTED_ALGORITHMS:

            print(
                "ML Safety Validation: FAILED"
            )

            return jsonify({
                "error": (
                    "Unsupported ML prediction: "
                    f"{predicted_algorithm}"
                ),

                "ml_prediction": ml_prediction,

                "validation_status": "Rejected"

            }), 422


        # ----------------------------------------------------
        # Validate confidence
        # ----------------------------------------------------

        if ml_confidence < CONFIDENCE_THRESHOLD:

            print(
                "ML Safety Validation: FAILED"
            )

            print(
                "Reason: ML confidence below threshold"
            )

            return jsonify({

                "error":
                    "ML prediction confidence is too low "
                    "for safe encryption.",

                "ml_prediction":
                    ml_prediction,

                "confidence_threshold":
                    CONFIDENCE_THRESHOLD,

                "validation_status":
                    "Rejected"

            }), 422


        # ----------------------------------------------------
        # Validation successful
        # ----------------------------------------------------

        print(
            "ML Safety Validation:",
            validation_status
        )

        print(
            "Final Decision Source:",
            decision_source
        )


        # ====================================================
        # 13. ENCRYPTED FILE PATH
        # ====================================================

        encrypted_filename = (
            filename + ".enc"
        )


        encrypted_path = os.path.join(
            ENCRYPTED_FOLDER,
            encrypted_filename
        )


        # ====================================================
        # 14. KEY VARIABLES
        # ====================================================

        key_path = None

        public_key_path = None


        # ====================================================
        # 15. ENCRYPTION METADATA
        # ====================================================

        encryption_algorithm = (
            ALGORITHM_DISPLAY_NAMES[
                predicted_algorithm
            ]
        )


        security_level = (
            ALGORITHM_SECURITY_LEVELS[
                predicted_algorithm
            ]
        )


        reason = (
            "Random Forest ML model selected "
            f"{encryption_algorithm} based on the "
            "extracted file, system, PII, classification, "
            "and sensitivity features."
        )


        # ====================================================
        # 16. START ENCRYPTION TIMER
        # ====================================================

        encryption_start = (
            time.perf_counter()
        )


        # ====================================================
        # 17. AES-256-GCM
        # ====================================================

        if predicted_algorithm == "AES":

            print()
            print(
                "Final Encryption:",
                "AES-256-GCM"
            )

            print(
                "Encryption Engine:",
                "AESGCM"
            )


            # ----------------------------------------------
            # Generate AES-256 key
            # ----------------------------------------------

            key, key_path = (
                generate_and_save_key(
                    filename
                )
            )


            # ----------------------------------------------
            # Encrypt file
            # ----------------------------------------------

            aes_encrypt_file(
                filepath,
                encrypted_path,
                key
            )


        # ====================================================
        # 18. CHACHA20-POLY1305
        # ====================================================

        elif predicted_algorithm == "ChaCha20":

            print()
            print(
                "Final Encryption:",
                "ChaCha20-Poly1305"
            )

            print(
                "Encryption Engine:",
                "ChaCha20Poly1305"
            )


            # ----------------------------------------------
            # Generate ChaCha20 key
            # ----------------------------------------------

            key, key_path = (
                generate_and_save_key(
                    filename
                )
            )


            # ----------------------------------------------
            # Encrypt file
            # ----------------------------------------------

            chacha_encrypt_file(
                filepath,
                encrypted_path,
                key
            )


        # ====================================================
        # 19. HYBRID ENCRYPTION
        # ====================================================

        elif predicted_algorithm == "Hybrid":

            print()
            print(
                "Final Encryption:",
                "Hybrid AES-256-GCM + RSA-OAEP"
            )

            print(
                "Encryption Engine:",
                "AES-256-GCM + RSA-OAEP"
            )


            # ----------------------------------------------
            # Generate RSA key pair
            # ----------------------------------------------

            private_key, public_key = (
                generate_rsa_key_pair()
            )


            # ----------------------------------------------
            # Save RSA keys
            # ----------------------------------------------

            (
                key_path,
                public_key_path
            ) = save_rsa_keys(
                filename,
                private_key,
                public_key
            )


            # ----------------------------------------------
            # Encrypt file
            # ----------------------------------------------

            hybrid_encrypt_file(
                filepath,
                encrypted_path,
                public_key
            )


        # ====================================================
        # 20. STOP ENCRYPTION TIMER
        # ====================================================

        encryption_time_ms = (
            time.perf_counter()
            - encryption_start
        ) * 1000


        # ====================================================
        # 21. VERIFY ENCRYPTED FILE
        # ====================================================

        if not os.path.exists(
            encrypted_path
        ):

            return jsonify({

                "error":
                    "Encryption completed but "
                    "encrypted file was not created."

            }), 500


        encrypted_size = os.path.getsize(
            encrypted_path
        )


        # ====================================================
        # 22. SIZE OVERHEAD
        # ====================================================

        if original_size > 0:

            size_overhead_percent = (
                (
                    encrypted_size
                    - original_size
                )
                / original_size
            ) * 100

        else:

            size_overhead_percent = 0


        # ====================================================
        # 23. PERFORMANCE
        # ====================================================

        performance = {

            "original_size_bytes":
                original_size,

            "encrypted_size_bytes":
                encrypted_size,

            "encryption_time_ms":
                round(
                    encryption_time_ms,
                    2
                ),

            "size_overhead_percent":
                round(
                    size_overhead_percent,
                    2
                ),

            "algorithm":
                encryption_algorithm

        }


        # ====================================================
        # FINAL TERMINAL OUTPUT
        # ====================================================

        print()
        print("=" * 60)
        print("ENCRYPTION COMPLETED")
        print("=" * 60)

        print(
            "AI Prediction:",
            predicted_algorithm
        )

        print(
            "AI Confidence:",
            f"{ml_confidence * 100:.2f}%"
        )

        print(
            "Validation:",
            validation_status
        )

        print(
            "Final Encryption:",
            encryption_algorithm
        )

        print(
            "Encryption Time:",
            f"{performance['encryption_time_ms']} ms"
        )

        print(
            "Original Size:",
            original_size,
            "bytes"
        )

        print(
            "Encrypted Size:",
            encrypted_size,
            "bytes"
        )

        print(
            "Size Overhead:",
            f"{performance['size_overhead_percent']}%"
        )

        print("=" * 60)
        print()


        # ====================================================
        # FINAL API RESPONSE
        # ====================================================

        return jsonify({

            "message":
                "File uploaded and encrypted successfully.",


            "filename":
                filename,


            # ------------------------------------------------
            # EXTRACTED INFORMATION
            # ------------------------------------------------

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


            # ------------------------------------------------
            # ML DECISION
            # ------------------------------------------------

            "ml_prediction": {

                "algorithm":
                    ml_prediction[
                        "algorithm"
                    ],

                "display_algorithm":
                    ml_prediction.get(
                        "display_algorithm",
                        encryption_algorithm
                    ),

                "confidence":
                    ml_prediction[
                        "confidence"
                    ],

                "probabilities":
                    ml_prediction[
                        "probabilities"
                    ],

                "decision_source":
                    decision_source,

                "validation_status":
                    validation_status,

                "confidence_threshold":
                    CONFIDENCE_THRESHOLD,

                "input_features":
                    ml_prediction.get(
                        "input_features",
                        {}
                    )

            },


            # ------------------------------------------------
            # ACTUAL ENCRYPTION
            # ------------------------------------------------

            "encryption": {

                "algorithm":
                    encryption_algorithm,

                "security_level":
                    security_level,

                "reason":
                    reason,

                "decision_source":
                    decision_source,

                "encrypted_file":
                    encrypted_filename,

                "key_file":
                    key_path,

                "public_key_file":
                    public_key_path

            },


            # ------------------------------------------------
            # PERFORMANCE
            # ------------------------------------------------

            "performance":
                performance

        }), 200


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        print()
        print("=" * 60)
        print("UPLOAD / ENCRYPTION ERROR")
        print("=" * 60)

        print(
            repr(e)
        )

        print("=" * 60)


        return jsonify({

            "error":
                str(e)

        }), 500


# ============================================================
# DOWNLOAD ENCRYPTED FILE
# ============================================================

@upload_bp.route(
    "/download/<path:filename>",
    methods=["GET"]
)
def download_file(filename):

    return send_from_directory(
        ENCRYPTED_FOLDER,
        filename,
        as_attachment=True
    )