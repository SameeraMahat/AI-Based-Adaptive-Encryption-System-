from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from database.mongodb import users_collection


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(silent=True) or {}

        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not username or not email or not password:
            return jsonify({
                "success": False,
                "message": "Username, email and password are required."
            }), 400

        if len(password) < 6:
            return jsonify({
                "success": False,
                "message": "Password must contain at least 6 characters."
            }), 400

        existing_user = users_collection.find_one({
            "$or": [
                {"email": email},
                {"username": username}
            ]
        })

        if existing_user:
            return jsonify({
                "success": False,
                "message": "User with this email or username already exists."
            }), 409

        now = datetime.now(timezone.utc)

        user = {
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": "user",
            "created_at": now,
            "updated_at": now
        }

        result = users_collection.insert_one(user)

        return jsonify({
            "success": True,
            "message": "Registration successful.",
            "user": {
                "id": str(result.inserted_id),
                "username": username,
                "email": email,
                "role": "user"
            }
        }), 201

    except Exception as error:
        print("Register error:", error)

        return jsonify({
            "success": False,
            "message": "Registration failed."
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password are required."
            }), 400

        user = users_collection.find_one({
            "email": email
        })

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        if not check_password_hash(
            user.get("password_hash", ""),
            password
        ):
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": {
                "id": str(user["_id"]),
                "username": user.get("username", ""),
                "email": user.get("email", ""),
                "role": user.get("role", "user")
            }
        }), 200

    except Exception as error:
        print("Login error:", error)

        return jsonify({
            "success": False,
            "message": "Login failed."
        }), 500