import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "adaptive-encryption-secret-key"
    )

    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://127.0.0.1:27017/"
    )

    MONGO_DATABASE = os.getenv(
        "MONGO_DATABASE",
        "adaptive_encryption"
    )