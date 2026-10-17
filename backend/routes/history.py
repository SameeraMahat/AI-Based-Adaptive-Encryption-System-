import csv
import io
import math
import re
from datetime import datetime, timedelta, timezone

from flask import Blueprint, Response, jsonify, request, session

from database.mongodb import (
    encryption_history_collection,
    decryption_history_collection
)

from utils.helpers import as_utc, iso_utc
from auth_utils import login_required


history_bp = Blueprint("history", __name__)


# ============================================================
# SETTINGS
# ============================================================

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10

RANGE_DAYS = {
    "24h": 1,
    "7d": 7,
    "30d": 30,
    "90d": 90
}


# ============================================================
# HELPERS
# ============================================================

def get_current_user_id():
    """Return the ID of the authenticated user."""
    return str(session["user_id"])


def get_file_type(filename):
    if not filename or "." not in filename:
        return "N/A"

    return filename.rsplit(".", 1)[1].upper()


def get_sensitivity_level(score):
    if score is None:
        return "N/A"

    if score >= 75:
        return "Very High"

    if score >= 50:
        return "High"

    if score >= 25:
        return "Medium"

    return "Low"


def normalise_encryption(record):
    score = record.get("sensitivity_score")

    return {
        "id": str(record["_id"]),
        "type": "encryption",
        "filename": record.get("filename", "Unknown"),
        "file_type": (
            record.get("file_type")
            or get_file_type(record.get("filename"))
        ),
        "file_size_mb": record.get("file_size_mb"),
        "algorithm": record.get("encryption_algorithm"),
        "ml_algorithm": record.get("ml_algorithm"),
        "ml_confidence": record.get("ml_confidence"),
        "security_validation": record.get("security_validation"),
        "key_info": record.get("key_size"),
        "document_category": record.get("document_category"),
        "pii_count": record.get("pii_count", 0),
        "sensitivity_score": score,
        "sensitivity_level": get_sensitivity_level(score),
        "processing_time_ms": record.get("processing_time_ms"),
        "status": record.get("status", "Success"),
        "created_at": iso_utc(record.get("created_at"))
    }


def normalise_decryption(record):
    return {
        "id": str(record["_id"]),
        "type": "decryption",
        "filename": record.get("filename", "Unknown"),
        "file_type": get_file_type(record.get("filename")),
        "file_size_mb": None,
        "algorithm": record.get("algorithm"),
        "ml_algorithm": None,
        "ml_confidence": None,
        "security_validation": None,
        "key_info": record.get("key_type"),
        "document_category": None,
        "pii_count": None,
        "sensitivity_score": None,
        "sensitivity_level": None,
        "processing_time_ms": record.get("processing_time_ms"),
        "status": record.get("status", "Success"),
        "created_at": iso_utc(record.get("created_at"))
    }


def date_filter_from_request():
    """
    Return a MongoDB created_at filter based on ?range=.
    An unsupported range means no date restriction.
    """

    selected = request.args.get("range", "all").lower()

    if selected not in RANGE_DAYS:
        return None

    since = (
        datetime.now(timezone.utc)
        - timedelta(days=RANGE_DAYS[selected])
    )

    return {"$gte": since}


def base_query(created_filter, user_id):
    """
    Every history query must be restricted to the current user.
    """

    query = {"user_id": str(user_id)}

    if created_filter:
        query["created_at"] = created_filter

    return query


def load_items(record_type, user_id):
    """
    Load and filter history records for one authenticated user.
    """

    created_filter = date_filter_from_request()
    query = base_query(created_filter, user_id)

    items = []

    if record_type in ("all", "encryption"):
        for record in encryption_history_collection.find(query):
            items.append(normalise_encryption(record))

    if record_type in ("all", "decryption"):
        for record in decryption_history_collection.find(query):
            items.append(normalise_decryption(record))

    # ---------------- Search ----------------

    search = request.args.get("search", "").strip().lower()

    if search:
        items = [
            item for item in items
            if search in (item["filename"] or "").lower()
            or search in (item["algorithm"] or "").lower()
            or search in (item["document_category"] or "").lower()
        ]

    # ---------------- Algorithm filter ----------------

    algorithm = request.args.get("algorithm", "").strip()

    if algorithm and algorithm.lower() != "all":
        items = [
            item for item in items
            if item["algorithm"] == algorithm
        ]

    # ---------------- Status filter ----------------

    status = request.args.get("status", "").strip().lower()

    if status and status != "all":
        items = [
            item for item in items
            if (item["status"] or "").lower() == status
        ]

    # ---------------- Sorting ----------------

    newest_first = request.args.get("sort", "newest") != "oldest"

    items.sort(
        key=lambda item: item["created_at"] or "",
        reverse=newest_first
    )

    return items


def get_record_type():
    record_type = request.args.get("type", "all").lower()

    if record_type not in ("all", "encryption", "decryption"):
        record_type = "all"

    return record_type


def parse_int(value, default, minimum, maximum):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default

    return max(minimum, min(maximum, number))


def load_all_for_filters(user_id):
    """Return algorithms used by this user only."""

    items = []
    query = {"user_id": str(user_id)}

    for record in encryption_history_collection.find(
        query,
        {"encryption_algorithm": 1}
    ):
        items.append({
            "algorithm": record.get("encryption_algorithm")
        })

    for record in decryption_history_collection.find(
        query,
        {"algorithm": 1}
    ):
        items.append({
            "algorithm": record.get("algorithm")
        })

    return items


# ============================================================
# COMBINED HISTORY
# ============================================================

@history_bp.route("/history", methods=["GET"])
@login_required
def get_history():
    """
    Combined encryption and decryption history.

    Query parameters:
        type       all | encryption | decryption
        search     text in file name / algorithm / category
        algorithm  exact algorithm display name
        status     Success | Failed ...
        range      24h | 7d | 30d | 90d | all
        sort       newest | oldest
        page       1..n
        page_size  1..100
    """

    try:
        user_id = get_current_user_id()
        record_type = get_record_type()

        items = load_items(record_type, user_id)

        page_size = parse_int(
            request.args.get("page_size"),
            DEFAULT_PAGE_SIZE,
            1,
            MAX_PAGE_SIZE
        )

        total = len(items)

        total_pages = max(
            1,
            math.ceil(total / page_size)
        )

        page = parse_int(
            request.args.get("page"),
            1,
            1,
            total_pages
        )

        start = (page - 1) * page_size

        # Counts for the tabs ignore the selected type filter,
        # but still belong only to the logged-in user.
        counts = {
            "encryption": encryption_history_collection.count_documents({
                "user_id": user_id
            }),
            "decryption": decryption_history_collection.count_documents({
                "user_id": user_id
            })
        }

        counts["all"] = (
            counts["encryption"] + counts["decryption"]
        )

        algorithms = sorted({
            item["algorithm"]
            for item in load_all_for_filters(user_id)
            if item["algorithm"]
        })

        return jsonify({
            "success": True,
            "items": items[start:start + page_size],
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "counts": counts,
            "algorithms": algorithms
        }), 200

    except Exception as error:
        print("History error:", repr(error))

        return jsonify({
            "success": False,
            "error": "Unable to load history."
        }), 500


# ============================================================
# CSV EXPORT
# ============================================================

def csv_safe(value):
    """Prevent spreadsheet formula injection through file names."""

    if isinstance(value, str) and re.match(r"^[=+\-@\t\r]", value):
        return "'" + value

    return value


@history_bp.route("/history/export", methods=["GET"])
@login_required
def export_history():
    try:
        user_id = get_current_user_id()
        items = load_items(get_record_type(), user_id)

        buffer = io.StringIO()
        writer = csv.writer(buffer)

        writer.writerow([
            "Date (UTC)",
            "Operation",
            "File",
            "Type",
            "Algorithm",
            "Status",
            "Category",
            "PII Count",
            "Sensitivity Score",
            "Time (ms)"
        ])

        for item in items:
            writer.writerow([
                item["created_at"] or "",
                item["type"],
                csv_safe(item["filename"]),
                item["file_type"],
                item["algorithm"] or "",
                item["status"] or "",
                item["document_category"] or "",
                "" if item["pii_count"] is None
                else item["pii_count"],
                "" if item["sensitivity_score"] is None
                else item["sensitivity_score"],
                "" if item["processing_time_ms"] is None
                else item["processing_time_ms"]
            ])

        return Response(
            buffer.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=history.csv"
            }
        )

    except Exception as error:
        print("History export error:", repr(error))

        return jsonify({
            "success": False,
            "error": "Unable to export history."
        }), 500


# ============================================================
# BACKWARD-COMPATIBLE UPLOAD HISTORY
# ============================================================

@history_bp.route("/history/uploads", methods=["GET"])
@login_required
def get_uploaded_file_history():
    try:
        user_id = get_current_user_id()

        records = (
            encryption_history_collection
            .find({"user_id": user_id})
            .sort("created_at", -1)
        )

        history = []

        for record in records:
            record["id"] = str(record.pop("_id"))
            record["created_at"] = iso_utc(
                record.get("created_at")
            )
            history.append(record)

        return jsonify({
            "success": True,
            "history": history
        }), 200

    except Exception as error:
        print("Upload history error:", repr(error))

        return jsonify({
            "success": False,
            "error": "Unable to load upload history."
        }), 500