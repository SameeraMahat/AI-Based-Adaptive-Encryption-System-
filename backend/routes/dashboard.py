
from datetime import datetime, timezone, timedelta

from flask import Blueprint, jsonify, request

from database.mongodb import (
    encryption_history_collection,
    decryption_history_collection,
)

dashboard_bp = Blueprint("dashboard", __name__)

DEMO_USER_ID = "demo-user"


# ============================================================
# SAVE ENCRYPTION RECORD
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
    status,
):
    record = {
        "user_id": user_id,
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
        "created_at": datetime.now(timezone.utc),
    }

    result = encryption_history_collection.insert_one(record)
    return result.inserted_id


# ============================================================
# GET ENCRYPTION METADATA
# ============================================================

@dashboard_bp.route(
    "/dashboard/encryption/<path:filename>",
    methods=["GET"],
)
def get_encryption_metadata(filename):
    original_filename = filename

    if original_filename.lower().endswith(".enc"):
        original_filename = original_filename[:-4]

    print("Metadata lookup filename:", repr(original_filename))
    print("Metadata lookup user_id:", DEMO_USER_ID)

    print(
        "Matching database filenames:",
        list(
            encryption_history_collection.find(
                {"user_id": DEMO_USER_ID},
                {"_id": 0, "filename": 1}
            ).sort("created_at", -1).limit(10)
        )
    )

    record = encryption_history_collection.find_one(
        {
            "user_id": DEMO_USER_ID,
            "filename": original_filename,
        },
        {"_id": 0},
    )

    if record is None:
        return jsonify({
            "success": False,
            "error": "Encryption metadata not found.",
        }), 404

    if isinstance(record.get("created_at"), datetime):
        record["created_at"] = record["created_at"].isoformat()

    return jsonify({
        "success": True,
        "metadata": record,
    }), 200

# ============================================================
# ANALYTICS API
# GET /api/analytics?range=all
# ============================================================

@dashboard_bp.route("/analytics", methods=["GET"])
def get_analytics():
    try:
        range_value = request.args.get("range", "30d").lower()

        range_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "all": None,
        }

        if range_value not in range_days:
            return jsonify({
                "success": False,
                "error": "Unsupported range. Use 7d, 30d, 90d, or all.",
            }), 400

        days = range_days[range_value]
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days) if days else None

        def load_records(collection, operation_type):
            records = []

            for original in collection.find({
                "user_id": DEMO_USER_ID
            }):
                record = dict(original)
                created_at = record.get("created_at")

                if not isinstance(created_at, datetime):
                    continue

                if created_at.tzinfo is None:
                    created_at = created_at.replace(
                        tzinfo=timezone.utc
                    )

                created_at = created_at.astimezone(timezone.utc)

                if cutoff and created_at < cutoff:
                    continue

                record["created_at"] = created_at
                record["type"] = operation_type

                if operation_type == "encryption":
                    record["_analytics_algorithm"] = (
                        record.get("encryption_algorithm")
                        or record.get("algorithm")
                        or "Unknown"
                    )
                else:
                    record["_analytics_algorithm"] = (
                        record.get("algorithm") or "Unknown"
                    )

                records.append(record)

            return records

        encryptions = load_records(
            encryption_history_collection, "encryption"
        )
        decryptions = load_records(
            decryption_history_collection, "decryption"
        )

        total_enc = len(encryptions)
        total_dec = len(decryptions)
        total_ops = total_enc + total_dec

        def is_success(record):
            return str(record.get("status", "")).lower() in (
                "success", "successful"
            )

        successful_enc = sum(is_success(r) for r in encryptions)
        successful_dec = sum(is_success(r) for r in decryptions)

        failed_enc = total_enc - successful_enc
        failed_dec = total_dec - successful_dec

        def average(records, field):
            values = []

            for record in records:
                value = record.get(field)
                if value is not None:
                    try:
                        values.append(float(value))
                    except (TypeError, ValueError):
                        continue

            return round(sum(values) / len(values), 2) if values else 0

        avg_enc_ms = average(encryptions, "processing_time_ms")
        avg_dec_ms = average(decryptions, "processing_time_ms")
        avg_sensitivity = average(encryptions, "sensitivity_score")

        total_pii = sum(
            int(r.get("pii_count") or 0)
            for r in encryptions
        )

        # ----------------------------------------------------
        # ALGORITHM / CATEGORY / FILE TYPE COUNTS
        # ----------------------------------------------------

        algorithm_counts = {}
        category_counts = {}
        file_type_counts = {}
        algorithm_stats = {}

        sensitivity_counts = {
            "Low": 0,
            "Medium": 0,
            "High": 0,
            "Very High": 0,
        }

        for record in encryptions:
            algorithm = record["_analytics_algorithm"]
            category = record.get("document_category") or "Unknown"

            filename = record.get("filename") or ""
            file_type = (
                record.get("file_type")
                or (
                    filename.rsplit(".", 1)[-1].upper()
                    if "." in filename else "Unknown"
                )
            )

            algorithm_counts[algorithm] = (
                algorithm_counts.get(algorithm, 0) + 1
            )
            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )
            file_type_counts[file_type] = (
                file_type_counts.get(file_type, 0) + 1
            )

            try:
                score = float(record.get("sensitivity_score") or 0)
            except (TypeError, ValueError):
                score = 0

            if score >= 75:
                level = "Very High"
            elif score >= 50:
                level = "High"
            elif score >= 25:
                level = "Medium"
            else:
                level = "Low"

            sensitivity_counts[level] += 1

            stats = algorithm_stats.setdefault(
                algorithm,
                {
                    "files": 0,
                    "processing_total": 0.0,
                    "confidence_total": 0.0,
                    "confidence_count": 0,
                },
            )

            stats["files"] += 1

            try:
                stats["processing_total"] += float(
                    record.get("processing_time_ms") or 0
                )
            except (TypeError, ValueError):
                pass

            confidence = record.get("ml_confidence")

            if confidence is not None:
                try:
                    confidence = float(confidence)
                    if confidence <= 1:
                        confidence *= 100

                    stats["confidence_total"] += confidence
                    stats["confidence_count"] += 1
                except (TypeError, ValueError):
                    pass

        # Arrays are returned for frontend components using .reduce().
        sensitivity = [
            {"name": name, "count": count}
            for name, count in sensitivity_counts.items()
        ]

        file_types = [
            {"name": name, "count": count}
            for name, count in sorted(file_type_counts.items())
        ]

        categories = [
            {"name": name, "count": count}
            for name, count in sorted(category_counts.items())
        ]

        algorithms = [
            {"name": name, "count": count}
            for name, count in sorted(
                algorithm_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]

        algorithm_performance = []

        for algorithm, stats in algorithm_stats.items():
            algorithm_performance.append({
                "algorithm": algorithm,
                "files": stats["files"],
                "avg_encryption_time_ms": round(
                    stats["processing_total"] / stats["files"], 2
                ) if stats["files"] else 0,
                "avg_model_confidence": round(
                    stats["confidence_total"] / stats["confidence_count"], 2
                ) if stats["confidence_count"] else 0,
            })

        # ----------------------------------------------------
        # DAILY ACTIVITY: BOTH ENCRYPTION AND DECRYPTION
        # ----------------------------------------------------

        daily_counts = {}

        for record in encryptions + decryptions:
            day = record["created_at"].strftime("%Y-%m-%d")

            if day not in daily_counts:
                daily_counts[day] = {
                    "date": day,
                    "encryptions": 0,
                    "decryptions": 0,
                    "count": 0,
                }

            key = (
                "encryptions"
                if record["type"] == "encryption"
                else "decryptions"
            )

            daily_counts[day][key] += 1
            daily_counts[day]["count"] += 1

        daily_activity = [
            daily_counts[day]
            for day in sorted(daily_counts)
        ]

        summary = {
            "total_encryptions": total_enc,
            "total_decryptions": total_dec,
            "total_operations": total_ops,
            "successful_encryptions": successful_enc,
            "failed_encryptions": failed_enc,
            "successful_decryptions": successful_dec,
            "failed_decryptions": failed_dec,
            "success_rate": round(
                (successful_enc + successful_dec) / total_ops * 100, 2
            ) if total_ops else 0,
            "total_pii_detected": total_pii,
            "average_processing_time_ms": avg_enc_ms,
            "average_encryption_time_ms": avg_enc_ms,
            "average_decryption_time_ms": avg_dec_ms,
            "average_sensitivity_score": avg_sensitivity,
        }

        return jsonify({
            "success": True,
            "range": range_value,
            "summary": summary,
            "algorithms": algorithms,
            "categories": categories,
            "file_types": file_types,
            "sensitivity": sensitivity,
            "algorithm_performance": algorithm_performance,
            "daily_activity": daily_activity,
        }), 200

    except (TypeError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": f"Invalid analytics parameter: {exc}",
        }), 400

    except Exception as exc:
        print("Analytics error:", repr(exc))
        return jsonify({
            "success": False,
            "error": "Unable to calculate analytics.",
        }), 500
