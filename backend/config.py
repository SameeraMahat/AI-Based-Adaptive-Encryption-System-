import os
from datetime import timedelta
from dotenv import load_dotenv


# Always load the .env file from the backend directory.
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BACKEND_DIR, ".env")

load_dotenv(ENV_FILE)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY must be set in backend/.env."
        )

    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://127.0.0.1:27017/"
    )

    MONGO_DATABASE = os.getenv(
        "MONGO_DATABASE",
        "adaptive_encryption"
    )

    # Session cookie settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "false").lower()
        == "true"
    )

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)