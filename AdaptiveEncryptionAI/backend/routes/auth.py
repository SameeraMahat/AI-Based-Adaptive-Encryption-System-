from flask import Blueprint, request, jsonify

from extensions import bcrypt
from database.models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists."}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully."
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "error": "Username and password are required."
        }), 400

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({
            "error": "Invalid username or password."
        }), 401

    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({
            "error": "Invalid username or password."
        }), 401

    return jsonify({
        "message": "Login successful.",
        "username": user.username,
        "email": user.email,
        "role": user.role
    }), 200