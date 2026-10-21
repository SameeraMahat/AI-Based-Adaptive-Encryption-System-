
from datetime import datetime, timezone, timedelta
from io import StringIO
import csv

from flask import Blueprint, jsonify, request, Response

from database.mongodb import (
    encryption_history_collection,
    decryption_history_collection,
)

history_bp = Blueprint("history", __name__)

DEMO_USER_ID = "demo-user"
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


# ============================================================
# DATE HELPERS
# ============================================================

def parse_date(value):
    """Convert datetime or ISO string to timezone-aware UTC."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return None
    else:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


# ============================================================
# SERIALIZE DATABASE RECORD
# ============================================================

def serialize_record(record, operation_type):
    record = dict(record)

    record["id"] = str(
        record.pop("_id", record.get("id", ""))
    )

    created_at = parse_date(record.get("created_at"))
    if created_at:
        record["created_at"] = created_at.isoformat()

    record["type"] = operation_type

    if operation_type == "encryption":
        record["algorithm"] = (
            record.get("encryption_algorithm")
            or record.get("algorithm")
            or "Unknown"
        )
        record["key_info"] = record.get(
            "key_size", "—"
        )
    else:
        record["algorithm"] = (
            record.get("algorithm") or "Unknown"
        )
        record["key_info"] = record.get(
            "key_type", "—"
        )

    filename = record.get("filename") or ""
    record["file_type"] = (
        record.get("file_type")
        or (
            filename.rsplit(".", 1)[-1].upper()
            if "." in filename else "Unknown"
        )
    )

    record["status"] = record.get("status") or "Unknown"

    score = record.get("sensitivity_score")
    if (
        not record.get("sensitivity_level")
        and isinstance(score, (int, float))
    ):
        if score >= 75:
            record["sensitivity_level"] = "Very High"
        elif score >= 50:
            record["sensitivity_level"] = "High"
        elif score >= 25:
            record["sensitivity_level"] = "Medium"
        else:
            record["sensitivity_level"] = "Low"

    return record


# ============================================================
# FETCH BOTH ENCRYPTION AND DECRYPTION HISTORY
# ============================================================

def fetch_history():
    history = []

    encryption_records = encryption_history_collection.find({
        "user_id": DEMO_USER_ID
    })

    for record in encryption_records:
        history.append(
            serialize_record(record, "encryption")
        )

    decryption_records = decryption_history_collection.find({
        "user_id": DEMO_USER_ID
    })

    for record in decryption_records:
        history.append(
            serialize_record(record, "decryption")
        )

    history.sort(
        key=lambda item: parse_date(item.get("created_at"))
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    return history


# ============================================================
# FILTER HISTORY
# ============================================================

def apply_filters(records, args):
    operation = args.get("type", "all").lower()
    algorithm = args.get("algorithm", "all").lower()
    status = args.get("status", "all").lower()
    date_range = args.get("range", "all").lower()
    search = args.get("search", "").strip().lower()
    sort_order = args.get("sort", "newest").lower()

    range_days = {
        "24h": 1,
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }

    now = datetime.now(timezone.utc)
    cutoff = None

    if date_range in range_days:
        cutoff = now - timedelta(
            days=range_days[date_range]
        )

    filtered = []

    for item in records:
        item_type = str(
            item.get("type", "")
        ).lower()

        if operation in ("encryption", "decryption"):
            if item_type != operation:
                continue

        item_algorithm = str(
            item.get("algorithm", "")
        ).lower()

        if algorithm != "all" and item_algorithm != algorithm:
            continue

        item_status = str(
            item.get("status", "")
        ).lower()

        if status == "success":
            if item_status not in ("success", "successful"):
                continue

        elif status == "failed":
            if item_status in ("success", "successful"):
                continue

        created_at = parse_date(item.get("created_at"))

        if cutoff and (
            created_at is None or created_at < cutoff
        ):
            continue

        searchable = " ".join([
            str(item.get("filename", "")),
            str(item.get("algorithm", "")),
            str(item.get("document_category", "")),
        ]).lower()

        if search and search not in searchable:
            continue

        filtered.append(item)

    filtered.sort(
        key=lambda item: parse_date(item.get("created_at"))
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=(sort_order != "oldest")
    )

    return filtered


# ============================================================
# SUMMARY COUNTS
# ============================================================

def build_counts(records):
    return {
        "all": len(records),
        "encryption": sum(
            1 for record in records
            if record.get("type") == "encryption"
        ),
        "decryption": sum(
            1 for record in records
            if record.get("type") == "decryption"
        ),
    }


# ============================================================
# UPLOAD HISTORY ENDPOINT
# GET /api/history/uploads
# ============================================================

@history_bp.route("/history/uploads", methods=["GET"])
def get_uploaded_file_history():
    return jsonify({
        "success": True,
        "history": fetch_history()
    }), 200


# ============================================================
# MAIN HISTORY ENDPOINT
# GET /api/history
# ============================================================

@history_bp.route("/history", methods=["GET"])
def get_history():
    try:
        page = max(
            1,
            int(request.args.get("page", 1))
        )

        page_size = min(
            MAX_PAGE_SIZE,
            max(
                1,
                int(request.args.get(
                    "page_size",
                    DEFAULT_PAGE_SIZE
                ))
            )
        )

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Invalid page or page_size"
        }), 400

    all_records = fetch_history()

    # Counts represent all records, regardless of filters.
    counts = build_counts(all_records)

    filtered_records = apply_filters(
        all_records,
        request.args
    )

    total = len(filtered_records)

    total_pages = max(
        1,
        (total + page_size - 1) // page_size
    )

    start = (page - 1) * page_size
    items = filtered_records[start:start + page_size]

    algorithms = sorted({
        str(record.get("algorithm", "Unknown"))
        for record in all_records
    })

    return jsonify({
        "success": True,
        "items": items,
        "counts": counts,
        "algorithms": algorithms,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }), 200


# ============================================================
# EXPORT HISTORY AS CSV
# GET /api/history/export
# ============================================================

@history_bp.route("/history/export", methods=["GET"])
def export_history_csv():
    records = apply_filters(
        fetch_history(),
        request.args
    )

    output = StringIO()

    columns = [
        "filename",
        "type",
        "algorithm",
        "document_category",
        "file_type",
        "file_size_mb",
        "sensitivity_score",
        "pii_count",
        "processing_time_ms",
        "status",
        "created_at",
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=columns,
        extrasaction="ignore"
    )

    writer.writeheader()
    writer.writerows(records)

    response = Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8"
    )

    response.headers["Content-Disposition"] = (
        'attachment; filename="encryption_history.csv"'
    )

    return response
