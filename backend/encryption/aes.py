import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_key():
    """
    Generate a 256-bit AES encryption key.
    """
    return AESGCM.generate_key(bit_length=256)


def encrypt_file(input_path, output_path, key):
    """
    Encrypt a file using AES-256-GCM.

    Returns:
        nonce: randomly generated nonce used for encryption
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if len(key) != 32:
        raise ValueError("AES-256 key must be exactly 32 bytes.")

    with open(input_path, "rb") as file:
        plaintext = file.read()

    # AES-GCM uses a 12-byte nonce
    nonce = os.urandom(12)

    aes = AESGCM(key)

    # GCM provides both encryption and integrity protection
    ciphertext = aes.encrypt(
        nonce,
        plaintext,
        None
    )

    with open(output_path, "wb") as file:
        file.write(nonce)
        file.write(ciphertext)

    return nonce


def decrypt_file(input_path, output_path, key):
    """
    Decrypt an AES-256-GCM encrypted file.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Encrypted file not found: {input_path}")

    if len(key) != 32:
        raise ValueError("AES-256 key must be exactly 32 bytes.")

    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    # First 12 bytes contain the nonce
    nonce = encrypted_data[:12]

    # Remaining bytes contain ciphertext + authentication tag
    ciphertext = encrypted_data[12:]

    aes = AESGCM(key)

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    with open(output_path, "wb") as file:
        file.write(plaintext)