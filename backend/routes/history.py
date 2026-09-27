from datetime import datetime

from flask import Blueprint, jsonify

from database.mongodb import (
    encryption_history_collection
)


history_bp = Blueprint(
    "history",
    __name__
)


# ============================================================
# TEMPORARY USER ID
# ============================================================

DEMO_USER_ID = "demo-user"


# ============================================================
# SERIALIZE UPLOADED FILE RECORD
# ============================================================

def serialize_uploaded_file(record):

    record["id"] = str(
        record.pop("_id")
    )

    if isinstance(
        record.get("created_at"),
        datetime
    ):
        record["created_at"] = record[
            "created_at"
        ].isoformat()

    return record


# ============================================================
# UPLOADED FILE HISTORY
# ============================================================

@history_bp.route(
    "/history/uploads",
    methods=["GET"]
)
def get_uploaded_file_history():

    records = (
        encryption_history_collection
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
            serialize_uploaded_file(
                record
            )
        )

    return jsonify({
        "success": True,
        "history": history
    }), 200