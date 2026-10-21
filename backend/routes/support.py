from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from database.mongodb import mongo_db, users_collection


support_bp = Blueprint("support", __name__)


# MongoDB collections
support_issues_collection = mongo_db["support_issues"]
support_messages_collection = mongo_db["support_messages"]


def get_current_time():
    return datetime.now(timezone.utc)


# ============================================================
# REPORT AN ISSUE
# ============================================================

@support_bp.route("/issues", methods=["POST"])
def report_issue():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    severity = str(data.get("severity", "Medium")).strip()
    page = str(data.get("page", "Settings")).strip()

    # Required fields
    if not email:
        return jsonify({
            "success": False,
            "error": "User email is required."
        }), 400

    if not title:
        return jsonify({
            "success": False,
            "error": "Issue title is required."
        }), 400

    if not description:
        return jsonify({
            "success": False,
            "error": "Issue description is required."
        }), 400

    # Check whether the user exists
    user = users_collection.find_one({
        "email": email
    })

    if not user:
        return jsonify({
            "success": False,
            "error": "User account not found."
        }), 404

    now = get_current_time()

    issue_document = {
        "user_id": user["_id"],
        "username": user.get("username", ""),
        "email": email,
        "title": title,
        "description": description,
        "severity": severity,
        "page": page,
        "status": "open",
        "created_at": now,
        "updated_at": now,
    }

    result = support_issues_collection.insert_one(
        issue_document
    )

    return jsonify({
        "success": True,
        "message": "Issue reported successfully.",
        "issue_id": str(result.inserted_id),
    }), 201


# ============================================================
# CONTACT SUPPORT
# ============================================================

@support_bp.route("/contact", methods=["POST"])
def contact_support():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    # Required fields
    if not email:
        return jsonify({
            "success": False,
            "error": "User email is required."
        }), 400

    if not subject:
        return jsonify({
            "success": False,
            "error": "Subject is required."
        }), 400

    if not message:
        return jsonify({
            "success": False,
            "error": "Message is required."
        }), 400

    # Check whether the user exists
    user = users_collection.find_one({
        "email": email
    })

    if not user:
        return jsonify({
            "success": False,
            "error": "User account not found."
        }), 404

    now = get_current_time()

    support_message_document = {
        "user_id": user["_id"],
        "username": user.get("username", ""),
        "email": email,
        "subject": subject,
        "message": message,
        "status": "open",
        "created_at": now,
        "updated_at": now,
    }

    result = support_messages_collection.insert_one(
        support_message_document
    )

    return jsonify({
        "success": True,
        "message": "Your message has been sent to support.",
        "message_id": str(result.inserted_id),
    }), 201


# ============================================================
# CREATE MONGODB INDEXES
# ============================================================

support_issues_collection.create_index([
    ("email", 1),
    ("created_at", -1)
])

support_issues_collection.create_index([
    ("status", 1),
    ("created_at", -1)
])

support_messages_collection.create_index([
    ("email", 1),
    ("created_at", -1)
])

support_messages_collection.create_index([
    ("status", 1),
    ("created_at", -1)
])