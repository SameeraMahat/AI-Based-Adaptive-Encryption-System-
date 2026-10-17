from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request, session
from auth_utils import login_required

from database.mongodb import (
    encryption_history_collection,
    decryption_history_collection
)

from utils.helpers import as_utc


analytics_bp = Blueprint(
    "analytics",
    __name__
)


# ============================================================
# TEMPORARY USER ID
# ============================================================


RANGE_DAYS = {
    "7d": 7,
    "30d": 30,
    "90d": 90
}

SENSITIVITY_LEVELS = [
    "Low",
    "Medium",
    "High",
    "Very High"
]


# ============================================================
# HELPERS
# ============================================================

def sensitivity_level(score):

    if score is None:
        return None

    if score >= 75:
        return "Very High"

    if score >= 50:
        return "High"

    if score >= 25:
        return "Medium"

    return "Low"


def average(values, digits=2):

    values = [
        value for value in values
        if isinstance(value, (int, float))
    ]

    if not values:
        return 0

    return round(sum(values) / len(values), digits)


def distribution(counter):
    """
    Counter -> [{name, count, percent}], largest first.
    """

    total = sum(counter.values())

    return [
        {
            "name": name,
            "count": count,
            "percent": round(count / total * 100, 1)
        }
        for name, count in counter.most_common()
    ]


def get_tz_offset():
    """
    Minutes the user's local time is AHEAD of UTC
    (India = 330). Sent by the browser so the daily
    chart groups by the user's own days.
    """

    try:
        offset = int(request.args.get("tz_offset", 0))
    except (TypeError, ValueError):
        offset = 0

    return max(-840, min(840, offset))


# ============================================================
# ANALYTICS
# ============================================================

@analytics_bp.route(
    "/analytics",
    methods=["GET"]
)
@login_required
def get_analytics():
    """
    Aggregated statistics for the Analytics page.

    Query parameters:
        range      7d | 30d | 90d | all   (default 30d)
        tz_offset  minutes ahead of UTC   (default 0)
    """

    try:

        selected_range = request.args.get(
            "range",
            "30d"
        ).lower()

        if selected_range not in RANGE_DAYS:
            selected_range = "all"

        user_id = str(session["user_id"])
        query = {"user_id": user_id}

        since = None

        if selected_range != "all":

            since = (
                datetime.now(timezone.utc)
                - timedelta(days=RANGE_DAYS[selected_range])
            )

            query["created_at"] = {"$gte": since}

        encryptions = list(
            encryption_history_collection.find(query)
        )

        decryptions = list(
            decryption_history_collection.find(query)
        )

        # ----------------------------------------------------
        # KPIs
        # ----------------------------------------------------

        encryption_success = [
            record for record in encryptions
            if record.get("status", "Success") == "Success"
        ]

        decryption_success = [
            record for record in decryptions
            if record.get("status", "Success") == "Success"
        ]

        total_operations = len(encryptions) + len(decryptions)

        successful_operations = (
            len(encryption_success) + len(decryption_success)
        )

        success_rate = (
            round(
                successful_operations / total_operations * 100,
                1
            )
            if total_operations else 0
        )

        kpis = {
            "files_encrypted": len(encryptions),
            "files_decrypted": len(decryptions),
            "total_operations": total_operations,
            "success_rate": success_rate,
            "avg_encryption_ms": average(
                [r.get("processing_time_ms") for r in encryptions]
            ),
            "avg_decryption_ms": average(
                [r.get("processing_time_ms") for r in decryptions]
            ),
            "avg_sensitivity": average(
                [r.get("sensitivity_score") for r in encryptions],
                1
            ),
            "total_pii": sum(
                record.get("pii_count") or 0
                for record in encryptions
            ),
            "avg_confidence_percent": round(
                average(
                    [r.get("ml_confidence") for r in encryptions],
                    4
                ) * 100,
                1
            ),
            "total_size_mb": round(
                sum(
                    record.get("file_size_mb") or 0
                    for record in encryptions
                ),
                2
            )
        }

        # ----------------------------------------------------
        # DISTRIBUTIONS
        # ----------------------------------------------------

        algorithm_counter = Counter(
            record.get("encryption_algorithm") or "Unknown"
            for record in encryptions
        )

        category_counter = Counter(
            record.get("document_category") or "General"
            for record in encryptions
        )

        file_type_counter = Counter(
            (record.get("file_type") or "N/A").upper()
            for record in encryptions
        )

        sensitivity_counter = Counter(
            sensitivity_level(record.get("sensitivity_score"))
            for record in encryptions
            if record.get("sensitivity_score") is not None
        )

        sensitivity = [
            {
                "name": level,
                "count": sensitivity_counter.get(level, 0)
            }
            for level in SENSITIVITY_LEVELS
        ]

        # ----------------------------------------------------
        # PER-ALGORITHM PERFORMANCE
        # ----------------------------------------------------

        times = defaultdict(list)
        confidences = defaultdict(list)

        for record in encryptions:

            name = record.get("encryption_algorithm") or "Unknown"

            times[name].append(record.get("processing_time_ms"))
            confidences[name].append(record.get("ml_confidence"))

        algorithm_performance = [
            {
                "name": name,
                "count": len(times[name]),
                "avg_time_ms": average(times[name]),
                "avg_confidence_percent": round(
                    average(confidences[name], 4) * 100,
                    1
                )
            }
            for name, _ in algorithm_counter.most_common()
        ]

        # ----------------------------------------------------
        # DAILY TIMELINE (in the user's local days)
        # ----------------------------------------------------

        offset = timedelta(minutes=get_tz_offset())

        def local_day(value):

            value = as_utc(value)

            if value is None:
                return None

            return (value + offset).date()

        daily_encryptions = Counter(
            local_day(record.get("created_at"))
            for record in encryptions
        )

        daily_decryptions = Counter(
            local_day(record.get("created_at"))
            for record in decryptions
        )

        today = (datetime.now(timezone.utc) + offset).date()

        if selected_range == "all":

            known_days = [
                day for day in
                list(daily_encryptions) + list(daily_decryptions)
                if day is not None
            ]

            first_day = min(known_days) if known_days else today

            # Keep the chart readable.
            first_day = max(first_day, today - timedelta(days=89))

            days = (today - first_day).days + 1

        else:

            days = RANGE_DAYS[selected_range]

            first_day = today - timedelta(days=days - 1)

        timeline = []

        for index in range(days):

            day = first_day + timedelta(days=index)

            timeline.append({
                "date": day.isoformat(),
                "encryptions": daily_encryptions.get(day, 0),
                "decryptions": daily_decryptions.get(day, 0)
            })

        return jsonify({
            "success": True,
            "range": selected_range,
            "kpis": kpis,
            "algorithms": distribution(algorithm_counter),
            "categories": distribution(category_counter),
            "file_types": distribution(file_type_counter),
            "sensitivity": sensitivity,
            "algorithm_performance": algorithm_performance,
            "timeline": timeline
        }), 200

    except Exception as error:

        print("Analytics error:", repr(error))

        return jsonify({
            "success": False,
            "error": "Unable to load analytics."
        }), 500
