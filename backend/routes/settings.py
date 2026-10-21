from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

from database.mongodb import users_collection


settings_bp = Blueprint("settings", __name__)


DEFAULT_SETTINGS = {
    "defaultOperation": "Home",
    "theme": "Dark",
    "language": "English",

    "autoClearFiles": True,
    "notifications": True,

    "keyStorage": "Local Storage",
    "keyExpiry": 30,
    "keyBackup": False,
    "requireConfirmation": True,
    "sessionTimeout": 60,

    "modelVersion": "v1.0 (Default)",
    "sensitivityThreshold": 70,
    "piiDetection": True,
    "showConfidence": True,

    "storeHistory": True,
    "historyRetention": 90,
    "storageLocation": "Local",
    "autoDeleteDownloads": False,
}


@settings_bp.route("", methods=["GET"])
def get_settings():
    email = request.args.get("email", "").strip().lower()

    if not email:
        return jsonify({
            "success": False,
            "error": "Email is required."
        }), 400

    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({
            "success": False,
            "error": "User not found."
        }), 404

    saved_settings = user.get("settings", {})

    settings = {
        **DEFAULT_SETTINGS,
        **saved_settings,
        "username": user.get(
            "username",
            saved_settings.get("username", "user")
        ),
        "email": user.get(
            "email",
            saved_settings.get("email", email)
        ),
        "fullName": user.get(
            "full_name",
            saved_settings.get("fullName", "User")
        ),
        "role": user.get(
            "role",
            saved_settings.get("role", "user")
        ),
    }

    return jsonify({
        "success": True,
        "settings": settings,
        "user": {
            "username": settings["username"],
            "email": settings["email"],
            "fullName": settings["fullName"],
            "role": settings["role"],
        }
    }), 200


@settings_bp.route("", methods=["PUT"])
def update_settings():
    data = request.get_json(silent=True) or {}

    current_email = str(
        data.get("email", "")
    ).strip().lower()

    new_settings = data.get("settings")

    if not current_email:
        return jsonify({
            "success": False,
            "error": "Email is required."
        }), 400

    if not isinstance(new_settings, dict):
        return jsonify({
            "success": False,
            "error": "Settings must be an object."
        }), 400

    user = users_collection.find_one({
        "email": current_email
    })

    if not user:
        return jsonify({
            "success": False,
            "error": "User not found."
        }), 404

    new_username = str(
        new_settings.get(
            "username",
            user.get("username", "")
        )
    ).strip()

    new_email = str(
        new_settings.get(
            "email",
            user.get("email", current_email)
        )
    ).strip().lower()

    new_full_name = str(
        new_settings.get(
            "fullName",
            user.get("full_name", "")
        )
    ).strip()

    if not new_username:
        return jsonify({
            "success": False,
            "error": "Username cannot be empty."
        }), 400

    if not new_email:
        return jsonify({
            "success": False,
            "error": "Email cannot be empty."
        }), 400

    username_owner = users_collection.find_one({
        "username": new_username,
        "email": {"$ne": current_email}
    })

    if username_owner:
        return jsonify({
            "success": False,
            "error": "Username is already in use."
        }), 409

    email_owner = users_collection.find_one({
        "$and": [
            {"email": new_email},
            {"email": {"$ne": current_email}},
        ]
    })

    if email_owner:
        return jsonify({
            "success": False,
            "error": "Email is already in use."
        }), 409

    current_settings = user.get("settings", {})

    updated_settings = {
        **DEFAULT_SETTINGS,
        **current_settings,
        **new_settings,
        "username": new_username,
        "email": new_email,
        "fullName": new_full_name,
        "role": user.get("role", "user"),
    }

    now = datetime.now(timezone.utc)

    users_collection.update_one(
        {"email": current_email},
        {
            "$set": {
                "username": new_username,
                "email": new_email,
                "full_name": new_full_name,
                "settings": updated_settings,
                "updated_at": now,
            }
        }
    )

    return jsonify({
        "success": True,
        "message": "Settings saved successfully.",
        "settings": updated_settings,
        "user": {
            "username": new_username,
            "email": new_email,
            "fullName": new_full_name,
            "role": user.get("role", "user"),
        }
    }), 200


@settings_bp.route("/reset", methods=["POST"])
def reset_settings():
    data = request.get_json(silent=True) or {}

    email = str(
        data.get("email", "")
    ).strip().lower()

    if not email:
        return jsonify({
            "success": False,
            "error": "Email is required."
        }), 400

    user = users_collection.find_one({
        "email": email
    })

    if not user:
        return jsonify({
            "success": False,
            "error": "User not found."
        }), 404

    now = datetime.now(timezone.utc)

    reset_settings = {
        **DEFAULT_SETTINGS,
        "username": user.get("username", "user"),
        "email": user.get("email", email),
        "fullName": user.get("full_name", "User"),
        "role": user.get("role", "user"),
    }

    users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "settings": reset_settings,
                "updated_at": now,
            }
        }
    )

    return jsonify({
        "success": True,
        "message": "Settings reset successfully.",
        "settings": reset_settings,
    }), 200