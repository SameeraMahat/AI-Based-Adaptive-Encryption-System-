import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms


def generate_key():
    """
    Generate a 256-bit ChaCha20 encryption key.
    """
    return os.urandom(32)


def encrypt_file(input_path, output_path, key):
    """
    Encrypt a file using ChaCha20.

    The output file contains:
        16-byte nonce + encrypted data

    Returns:
        nonce: the nonce used for encryption
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    if len(key) != 32:
        raise ValueError(
            "ChaCha20 key must be exactly 32 bytes."
        )

    # ChaCha20 requires a 16-byte nonce
    nonce = os.urandom(16)

    algorithm = algorithms.ChaCha20(
        key,
        nonce
    )

    cipher = Cipher(algorithm, mode=None)
    encryptor = cipher.encryptor()

    with open(input_path, "rb") as file:
        plaintext = file.read()

    ciphertext = encryptor.update(plaintext)

    with open(output_path, "wb") as file:
        file.write(nonce)
        file.write(ciphertext)

    return nonce


def decrypt_file(input_path, output_path, key):
    """
    Decrypt a ChaCha20 encrypted file.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Encrypted file not found: {input_path}"
        )

    if len(key) != 32:
        raise ValueError(
            "ChaCha20 key must be exactly 32 bytes."
        )

    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    # First 16 bytes contain the nonce
    nonce = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    algorithm = algorithms.ChaCha20(
        key,
        nonce
    )

    cipher = Cipher(algorithm, mode=None)
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext)

    with open(output_path, "wb") as file:
        file.write(plaintext)