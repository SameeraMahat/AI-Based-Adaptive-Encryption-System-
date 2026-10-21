
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

from database.mongodb import users_collection


auth_bp = Blueprint("auth", __name__)


# ============================================================
# ORGANIZATION ADMIN SIGNUP
# POST /api/auth/signup
# ============================================================

@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json(silent=True) or {}

        organization_name = str(
            data.get("organization_name", "")
        ).strip()

        organization_email = str(
            data.get("organization_email", "")
        ).strip().lower()

        full_name = str(
            data.get("full_name", "")
        ).strip()

        username = str(
            data.get("username", "")
        ).strip()

        email = str(
            data.get("email", "")
        ).strip().lower()

        password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")

        # Validate required fields
        if not all([
            organization_name,
            organization_email,
            full_name,
            username,
            email,
            password,
        ]):
            return jsonify({
                "success": False,
                "message": "Please fill in all required fields."
            }), 400

        if not isinstance(password, str) or len(password) < 8:
            return jsonify({
                "success": False,
                "message": "Password must contain at least 8 characters."
            }), 400

        if confirm_password and password != confirm_password:
            return jsonify({
                "success": False,
                "message": "Passwords do not match."
            }), 400

        # Check duplicate account email
        existing_email = users_collection.find_one(
            {"email": email},
            {"_id": 1}
        )

        if existing_email:
            return jsonify({
                "success": False,
                "message": "This email is already registered."
            }), 409

        # Check duplicate username
        existing_username = users_collection.find_one(
            {"username": username},
            {"_id": 1}
        )

        if existing_username:
            return jsonify({
                "success": False,
                "message": "This username is already registered."
            }), 409

        now = datetime.now(timezone.utc)

        user = {
            "organization_name": organization_name,
            "organization_email": organization_email,
            "full_name": full_name,
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": "organization_admin",
            "created_at": now,
            "updated_at": now,
        }

        result = users_collection.insert_one(user)

        return jsonify({
            "success": True,
            "message": "Organization Admin account created successfully.",
            "user": {
                "id": str(result.inserted_id),
                "organization_name": organization_name,
                "organization_email": organization_email,
                "full_name": full_name,
                "username": username,
                "email": email,
                "role": "organization_admin",
            }
        }), 201

    except Exception:
        current_app.logger.exception("Signup error")

        return jsonify({
            "success": False,
            "message": "Signup failed. Please check the backend logs."
        }), 500


# ============================================================
# STANDARD USER REGISTRATION
# POST /api/auth/register
# ============================================================

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(silent=True) or {}

        username = str(
            data.get("username", "")
        ).strip()

        email = str(
            data.get("email", "")
        ).strip().lower()

        password = data.get("password", "")

        if not username or not email or not password:
            return jsonify({
                "success": False,
                "message": "Username, email and password are required."
            }), 400

        if not isinstance(password, str) or len(password) < 6:
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
            "updated_at": now,
        }

        result = users_collection.insert_one(user)

        return jsonify({
            "success": True,
            "message": "Registration successful.",
            "user": {
                "id": str(result.inserted_id),
                "username": username,
                "email": email,
                "role": "user",
            }
        }), 201

    except Exception:
        current_app.logger.exception("Register error")

        return jsonify({
            "success": False,
            "message": "Registration failed."
        }), 500


# ============================================================
# LOGIN
# POST /api/auth/login
# ============================================================

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}

        email = str(
            data.get("email", "")
        ).strip().lower()

        password = data.get("password", "")

        if not email or not isinstance(password, str) or not password:
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

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": {
                "id": str(user["_id"]),
                "username": user.get("username", ""),
                "email": user.get("email", ""),
                "full_name": user.get("full_name", ""),
                "organization_name": user.get("organization_name", ""),
                "role": user.get("role", "user"),
            }
        }), 200

    except Exception:
        current_app.logger.exception("Login error")

        return jsonify({
            "success": False,
            "message": "Login failed."
        }), 500


# ============================================================
# DECRYPT PASSWORD RE-VERIFICATION
# POST /api/auth/verify-decrypt
# ============================================================

@auth_bp.route("/verify-decrypt", methods=["POST"])
def verify_decrypt():
    try:
        data = request.get_json(silent=True) or {}

        email = str(
            data.get("email", "")
        ).strip().lower()

        password = data.get("password", "")

        if not email or not isinstance(password, str) or not password:
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
                "message": "Incorrect password. Decrypt access denied."
            }), 401

        secret_key = current_app.config.get("SECRET_KEY")

        if not secret_key:
            current_app.logger.error(
                "SECRET_KEY is not configured."
            )

            return jsonify({
                "success": False,
                "message": "Server security configuration error."
            }), 500

        serializer = URLSafeTimedSerializer(secret_key)

        token = serializer.dumps(
            {
                "user_id": str(user["_id"]),
                "email": user["email"],
                "purpose": "decrypt"
            },
            salt="decrypt-authorization"
        )

        return jsonify({
            "success": True,
            "message": "Password verified successfully.",
            "decrypt_token": token
        }), 200

    except Exception:
        current_app.logger.exception(
            "Decrypt verification failed."
        )

        return jsonify({
            "success": False,
            "message": "Unable to verify password."
        }), 500
