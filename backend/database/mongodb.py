import os

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017/"
)

MONGO_DATABASE = os.getenv(
    "MONGO_DATABASE",
    "adaptive_encryption"
)


client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

mongo_db = client[MONGO_DATABASE]

users_collection = mongo_db["users"]
encryption_history_collection = mongo_db["encryption_history"]
decryption_history_collection = mongo_db["decryption_history"]


def init_mongodb():
    try:
        client.admin.command("ping")

        users_collection.create_index(
            "email",
            unique=True
        )

        users_collection.create_index(
            "username",
            unique=True,
            sparse=True
        )

        encryption_history_collection.create_index(
            [
                ("user_id", 1),
                ("created_at", -1)
            ]
        )

        decryption_history_collection.create_index(
            [
                ("user_id", 1),
                ("created_at", -1)
            ]
        )

        print("MongoDB connected successfully.")
        print(f"Database: {MONGO_DATABASE}")

        return True

    except ConnectionFailure as error:
        print("MongoDB connection failed:")
        print(error)

        return False