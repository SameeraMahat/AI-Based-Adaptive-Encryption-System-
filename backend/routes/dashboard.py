from datetime import datetime, timezone

from flask import Blueprint, jsonify, session

from database.mongodb import encryption_history_collection


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


# ============================================================
# SAVE ENCRYPTION DATABASE RECORD
# ============================================================

def save_encryption_record(
    user_id,
    filename,
    file_type,
    file_size_mb,
    pii_count,
    sensitivity_score,
    document_category,
    ml_algorithm,
    ml_confidence,
    security_validation,
    encryption_algorithm,
    key_size,
    processing_time_ms,
    status
):
    """
    Save encryption metadata for the specified user.
    The caller must supply the authenticated user's ID.
    """

    encryption_record = {
        "user_id": str(user_id),
        "filename": filename,
        "file_type": file_type,
        "file_size_mb": file_size_mb,
        "pii_count": pii_count,
        "sensitivity_score": sensitivity_score,
        "document_category": document_category,
        "ml_algorithm": ml_algorithm,
        "ml_confidence": ml_confidence,
        "security_validation": security_validation,
        "encryption_algorithm": encryption_algorithm,
        "key_size": key_size,
        "processing_time_ms": processing_time_ms,
        "status": status,
        "created_at": datetime.now(timezone.utc)
    }

    result = encryption_history_collection.insert_one(
        encryption_record
    )

    return result.inserted_id


# ============================================================
# GET ENCRYPTION METADATA
# ============================================================

@dashboard_bp.route(
    "/dashboard/encryption/<path:filename>",
    methods=["GET"]
)
def get_encryption_metadata(filename):
    """
    Return encryption metadata belonging to the logged-in user.
    """

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "error": "Please log in to continue."
        }), 401

    original_filename = filename

    if original_filename.lower().endswith(".enc"):
        original_filename = original_filename[:-4]

    record = encryption_history_collection.find_one(
        {
            "user_id": user_id,
            "filename": original_filename
        },
        {
            "_id": 0
        }
    )

    if record is None:
        return jsonify({
            "success": False,
            "error": "Encryption metadata not found."
        }), 404

    if isinstance(record.get("created_at"), datetime):
        record["created_at"] = record[
            "created_at"
        ].isoformat()

    return jsonify({
        "success": True,
        "metadata": record
    }), 200
