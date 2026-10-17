from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.mongodb import users_collection


auth_bp = Blueprint("auth", __name__)


# ============================================================
# REGISTER
# ============================================================

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
            "message": "Registration successful. Please log in.",
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


# ============================================================
# LOGIN
# ============================================================

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

        if not user or not check_password_hash(
            user.get("password_hash", ""),
            password
        ):
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        # Clear any previous session before establishing a new one.
        session.clear()
        session.permanent = True

        session["user_id"] = str(user["_id"])
        session["email"] = user.get("email", "")
        session["username"] = user.get("username", "")
        session["role"] = user.get("role", "user")

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


# ============================================================
# CHECK CURRENT LOGIN SESSION
# ============================================================

@auth_bp.route("/me", methods=["GET"])
def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "authenticated": False,
            "message": "Please log in to continue."
        }), 401

    return jsonify({
        "authenticated": True,
        "user": {
            "id": user_id,
            "username": session.get("username", ""),
            "email": session.get("email", ""),
            "role": session.get("role", "user")
        }
    }), 200


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200
