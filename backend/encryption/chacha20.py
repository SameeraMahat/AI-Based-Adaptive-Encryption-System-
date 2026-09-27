import os

from cryptography.hazmat.primitives.ciphers.aead import (
    ChaCha20Poly1305
)


def generate_key():
    """
    Generate a 256-bit ChaCha20-Poly1305 encryption key.
    """
    return ChaCha20Poly1305.generate_key()


def encrypt_file(input_path, output_path, key):
    """
    Encrypt a file using ChaCha20-Poly1305.

    Output format:

        12-byte nonce
        encrypted data + authentication tag

    Returns:
        nonce: randomly generated nonce
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    if len(key) != 32:
        raise ValueError(
            "ChaCha20-Poly1305 key must be exactly 32 bytes."
        )

    # ChaCha20-Poly1305 uses a 12-byte nonce.
    nonce = os.urandom(12)

    with open(input_path, "rb") as file:
        plaintext = file.read()

    cipher = ChaCha20Poly1305(key)

    # ChaCha20-Poly1305 automatically adds
    # an authentication tag to the ciphertext.
    ciphertext = cipher.encrypt(
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
    Decrypt a ChaCha20-Poly1305 encrypted file.

    A wrong key will raise an exception because
    the authentication tag will not be valid.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Encrypted file not found: {input_path}"
        )

    if len(key) != 32:
        raise ValueError(
            "ChaCha20-Poly1305 key must be exactly 32 bytes."
        )

    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    # 12-byte nonce + authentication tag
    if len(encrypted_data) < 12 + 16:
        raise ValueError(
            "Invalid ChaCha20-Poly1305 encrypted file."
        )

    # First 12 bytes contain the nonce.
    nonce = encrypted_data[:12]

    # Remaining bytes contain ciphertext + authentication tag.
    ciphertext = encrypted_data[12:]

    cipher = ChaCha20Poly1305(key)

    # This verifies the authentication tag.
    # Wrong key -> exception.
    plaintext = cipher.decrypt(
        nonce,
        ciphertext,
        None
    )

    with open(output_path, "wb") as file:
        file.write(plaintext)