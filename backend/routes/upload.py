from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename

from feature_extraction.text_extractor import extract_text
from feature_extraction.pii_detector import detect_pii
from feature_extraction.file_features import extract_file_features
from feature_extraction.system_features import extract_system_features
from feature_extraction.classifier import classify_document
from feature_extraction.sensitivity import calculate_sensitivity

from models.predict_model import predict_encryption_algorithm


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

    # ========================================================
    # FILE VALIDATION
    # ========================================================

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


    # ========================================================
    # SAVE FILE
    # ========================================================

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)


    # ========================================================
    # TEXT / OCR EXTRACTION
    # ========================================================

    text = extract_text(filepath)


    # ========================================================
    # PII DETECTION
    # ========================================================

    pii = detect_pii(text)


    # ========================================================
    # FILE FEATURE EXTRACTION
    # ========================================================

    features = extract_file_features(
        text,
        pii
    )


    # ========================================================
    # SYSTEM FEATURES
    # ========================================================

    system_features = extract_system_features(
        filepath
    )


    # ========================================================
    # DOCUMENT CLASSIFICATION
    # ========================================================

    classification = classify_document(
        text
    )


    # ========================================================
    # SENSITIVITY CALCULATION
    # ========================================================

    sensitivity = calculate_sensitivity(
        features,
        classification,
        system_features
    )


    # ========================================================
    # PREPARE FEATURES FOR RANDOM FOREST
    # ========================================================

    # These MUST match the features used during training.

    prediction_features = {
        "file_type": os.path.splitext(filename)[1]
        .replace(".", "")
        .upper(),

        "file_size_mb": os.path.getsize(filepath)
        / (1024 * 1024),

        "document_category": classification.get(
            "document_category",
            "General"
        ),

        "pii_count": features.get(
            "pii_count",
            0
        ),

        "category_confidence": classification.get(
            "category_confidence",
            0.5
        ),

        "confidential_marker": (
            "Yes"
            if features.get(
                "confidential_keyword_count",
                0
            ) > 0
            else "No"
        ),

        "sensitivity_score": sensitivity.get(
            "sensitivity_score",
            0
        )
    }


    # ========================================================
    # RANDOM FOREST PREDICTION
    # ========================================================

    try:

        ml_prediction = predict_encryption_algorithm(
            prediction_features
        )

    except Exception as e:

        return jsonify({
            "error": "ML prediction failed.",
            "details": str(e)
        }), 500


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return jsonify({

        "message": "File uploaded successfully.",

        "filename": filename,

        "extracted_text": text,

        "pii": pii,

        "features": features,

        "system_features": system_features,

        "classification": classification,

        "sensitivity": sensitivity,

        "prediction_features": prediction_features,

        "prediction": {
            "algorithm": ml_prediction["algorithm"],
            "confidence": ml_prediction["confidence"]
        }

    }), 200