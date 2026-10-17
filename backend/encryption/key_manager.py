import os
import base64

BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

KEY_FOLDER = os.path.join(BACKEND_DIR, "keys")


def generate_and_save_key(filename):
    """
    Generate a 256-bit key and save it for the encrypted file.

    The key is stored separately from the encrypted file.
    """

    from encryption.aes import generate_key

    os.makedirs(KEY_FOLDER, exist_ok=True)

    key = generate_key()

    key_filename = filename + ".key"
    key_path = os.path.join(KEY_FOLDER, key_filename)

    with open(key_path, "wb") as file:
        file.write(base64.b64encode(key))

    return key, key_path


def load_key(filename):
    """
    Load an existing AES key.
    """

    key_filename = filename + ".key"
    key_path = os.path.join(KEY_FOLDER, key_filename)

    if not os.path.exists(key_path):
        raise FileNotFoundError(
            f"Encryption key not found for {filename}"
        )

    with open(key_path, "rb") as file:
        key = base64.b64decode(file.read())

    return key