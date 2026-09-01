"""
ChaCha20 encryption/decryption for the AI-Based Adaptive Encryption System.

Uses ChaCha20-Poly1305 (an AEAD cipher, same authenticated-encryption idea
as AES-GCM). ChaCha20 is generally FASTER than AES on devices without
hardware AES acceleration (e.g. many phones, low-power devices), which is
exactly why it's a good fit for Low-sensitivity files or low-battery
situations in our decision engine.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

KEY_SIZE_BYTES = 32    # ChaCha20 always uses a 256-bit key
NONCE_SIZE_BYTES = 12  # standard nonce size for ChaCha20-Poly1305


def generate_chacha_key() -> bytes:
    """Generates a random 256-bit ChaCha20 key."""
    return ChaCha20Poly1305.generate_key()


def encrypt_chacha20(file_bytes: bytes, key: bytes) -> bytes:
    """
    Encrypts file_bytes using ChaCha20-Poly1305.
    Returns: nonce + ciphertext, concatenated together.
    """
    chacha = ChaCha20Poly1305(key)
    nonce = os.urandom(NONCE_SIZE_BYTES)
    ciphertext = chacha.encrypt(nonce, file_bytes, associated_data=None)
    return nonce + ciphertext


def decrypt_chacha20(encrypted_bytes: bytes, key: bytes) -> bytes:
    """
    Decrypts data produced by encrypt_chacha20().
    """
    chacha = ChaCha20Poly1305(key)
    nonce = encrypted_bytes[:NONCE_SIZE_BYTES]
    ciphertext = encrypted_bytes[NONCE_SIZE_BYTES:]
    plaintext = chacha.decrypt(nonce, ciphertext, associated_data=None)
    return plaintext


if __name__ == "__main__":
    # Quick self-test
    key = generate_chacha_key()
    original = b"This is a class attendance sheet: roll_no 12, present"

    encrypted = encrypt_chacha20(original, key)
    decrypted = decrypt_chacha20(encrypted, key)

    print(f"Original:  {original}")
    print(f"Encrypted (bytes, unreadable): {encrypted[:40]}...")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}")
