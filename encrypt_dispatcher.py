"""
Common encryption interface for the AI-Based Adaptive Encryption System.

This is the SINGLE function the AI decision engine (Phase 3) will call.
It doesn't need to know the details of AES vs ChaCha20 vs Hybrid — it just
picks an algorithm NAME based on sensitivity/context, and this dispatcher
handles the rest.

Supported algorithm names:
- "AES"      -> AES-256-GCM
- "ChaCha20" -> ChaCha20-Poly1305
- "Hybrid"   -> ECC (ECDH) + AES-256-GCM

Note: ECC alone isn't offered as a whole-file encryption option here,
because ECC is a KEY EXCHANGE mechanism, not a bulk data cipher.
It's used internally inside "Hybrid" mode.
"""

from aes_crypto import generate_aes_key, encrypt_aes, decrypt_aes
from chacha_crypto import generate_chacha_key, encrypt_chacha20, decrypt_chacha20
from hybrid_crypto import hybrid_encrypt, hybrid_decrypt
from ecc_crypto import generate_ecc_keypair

SUPPORTED_ALGORITHMS = ["AES", "ChaCha20", "Hybrid"]


def encrypt_file(file_bytes: bytes, algorithm: str, receiver_public_key=None):
    """
    Encrypts file_bytes using the specified algorithm.

    Returns a dict with everything needed later to decrypt:
    {
        "algorithm": "AES" | "ChaCha20" | "Hybrid",
        "ciphertext": bytes,
        "key": bytes,                  # present for AES / ChaCha20
        "ephemeral_public_key": ...,   # present for Hybrid only
    }
    """
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Unknown algorithm '{algorithm}'. Must be one of {SUPPORTED_ALGORITHMS}")

    if algorithm == "AES":
        key = generate_aes_key()
        ciphertext = encrypt_aes(file_bytes, key)
        return {"algorithm": "AES", "ciphertext": ciphertext, "key": key}

    elif algorithm == "ChaCha20":
        key = generate_chacha_key()
        ciphertext = encrypt_chacha20(file_bytes, key)
        return {"algorithm": "ChaCha20", "ciphertext": ciphertext, "key": key}

    elif algorithm == "Hybrid":
        if receiver_public_key is None:
            raise ValueError("Hybrid mode requires a receiver_public_key")
        ciphertext, ephemeral_public = hybrid_encrypt(file_bytes, receiver_public_key)
        return {"algorithm": "Hybrid", "ciphertext": ciphertext, "ephemeral_public_key": ephemeral_public}


def decrypt_file(package: dict, receiver_private_key=None) -> bytes:
    """
    Decrypts a package produced by encrypt_file().
    For Hybrid mode, you must pass the receiver's private key.
    """
    algorithm = package["algorithm"]

    if algorithm == "AES":
        return decrypt_aes(package["ciphertext"], package["key"])

    elif algorithm == "ChaCha20":
        return decrypt_chacha20(package["ciphertext"], package["key"])

    elif algorithm == "Hybrid":
        if receiver_private_key is None:
            raise ValueError("Hybrid mode requires receiver_private_key to decrypt")
        return hybrid_decrypt(package["ciphertext"], package["ephemeral_public_key"], receiver_private_key)

    else:
        raise ValueError(f"Unknown algorithm '{algorithm}'")


if __name__ == "__main__":
    # Quick self-test across all 3 algorithm choices

    sample_file = b"Sample file content for testing the dispatcher."

    print("=== Testing AES ===")
    package = encrypt_file(sample_file, "AES")
    result = decrypt_file(package)
    print(f"Match: {result == sample_file}\n")

    print("=== Testing ChaCha20 ===")
    package = encrypt_file(sample_file, "ChaCha20")
    result = decrypt_file(package)
    print(f"Match: {result == sample_file}\n")

    print("=== Testing Hybrid ===")
    receiver_private, receiver_public = generate_ecc_keypair()
    package = encrypt_file(sample_file, "Hybrid", receiver_public_key=receiver_public)
    result = decrypt_file(package, receiver_private_key=receiver_private)
    print(f"Match: {result == sample_file}")
