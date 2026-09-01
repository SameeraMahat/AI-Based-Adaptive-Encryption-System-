"""
AES-256 encryption/decryption for the AI-Based Adaptive Encryption System.

Uses AES in GCM mode (Galois/Counter Mode) — this gives both:
- Confidentiality (the data is unreadable without the key)
- Integrity/authenticity (any tampering with the encrypted data is detected)

This is the classic, well-trusted "default" algorithm — good balance of
speed and security, suitable for High-sensitivity files.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_SIZE_BYTES = 32   # 32 bytes = 256 bits -> AES-256
NONCE_SIZE_BYTES = 12  # standard nonce size for GCM mode


def generate_aes_key() -> bytes:
    """Generates a random 256-bit AES key."""
    return AESGCM.generate_key(bit_length=256)


def encrypt_aes(file_bytes: bytes, key: bytes) -> bytes:
    """
    Encrypts file_bytes using AES-256-GCM.

    Returns: nonce + ciphertext, concatenated together.
    (The nonce must travel with the ciphertext — it's needed to decrypt,
    but it does NOT need to be kept secret.)
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE_BYTES)
    ciphertext = aesgcm.encrypt(nonce, file_bytes, associated_data=None)
    return nonce + ciphertext


def decrypt_aes(encrypted_bytes: bytes, key: bytes) -> bytes:
    """
    Decrypts data produced by encrypt_aes().
    Expects the first NONCE_SIZE_BYTES to be the nonce, rest is ciphertext.
    """
    aesgcm = AESGCM(key)
    nonce = encrypted_bytes[:NONCE_SIZE_BYTES]
    ciphertext = encrypted_bytes[NONCE_SIZE_BYTES:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    return plaintext


if __name__ == "__main__":
    # Quick self-test
    key = generate_aes_key()
    original = b"This is a salary record: employee John, salary 75000"

    encrypted = encrypt_aes(original, key)
    decrypted = decrypt_aes(encrypted, key)

    print(f"Original:  {original}")
    print(f"Encrypted (bytes, unreadable): {encrypted[:40]}...")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}")
