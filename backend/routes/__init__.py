from flask import Blueprint

main = Blueprint("main", __name__)

@main.route("/api/health", methods=["GET"])
def health():
    return {
        "status": "running",
        "message": "Adaptive AI Encryption Backend"
    }