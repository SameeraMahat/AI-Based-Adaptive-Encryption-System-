"""
Hybrid encryption for the AI-Based Adaptive Encryption System.

Combines:
- ECC (ECDH) to securely derive a shared AES key between sender & receiver
- AES-256-GCM to actually encrypt the (potentially large) file data

WHY HYBRID: Pure ECC/asymmetric encryption is slow for large data. AES
is fast but you need a way to safely share the key. Hybrid encryption
gets the best of both: ECC secures the KEY, AES secures the DATA.

This is the strongest-tier option in our system, used for Critical
sensitivity files (e.g. medical records).
"""

from ecc_crypto import generate_ecc_keypair, derive_shared_key
from aes_crypto import encrypt_aes, decrypt_aes


def hybrid_encrypt(file_bytes: bytes, receiver_public_key):
    """
    Encrypts file_bytes for a specific receiver using hybrid encryption.

    Steps:
    1. Generate a fresh, one-time ECC keypair for THIS encryption (ephemeral key)
    2. Derive a shared AES key using our ephemeral private key + receiver's public key
    3. Encrypt the file with AES using that derived key
    4. Return the ciphertext + our ephemeral public key (the receiver needs
       this public key, along with their own private key, to derive the
       same AES key and decrypt)

    Returns: (ciphertext, ephemeral_public_key)
    """
    ephemeral_private, ephemeral_public = generate_ecc_keypair()

    shared_key = derive_shared_key(ephemeral_private, receiver_public_key)

    ciphertext = encrypt_aes(file_bytes, shared_key)

    return ciphertext, ephemeral_public


def hybrid_decrypt(ciphertext: bytes, ephemeral_public_key, receiver_private_key) -> bytes:
    """
    Decrypts data produced by hybrid_encrypt().

    The receiver uses their own private key + the sender's ephemeral
    public key (which travels alongside the ciphertext) to derive the
    SAME shared AES key, then decrypts normally.
    """
    shared_key = derive_shared_key(receiver_private_key, ephemeral_public_key)
    plaintext = decrypt_aes(ciphertext, shared_key)
    return plaintext


if __name__ == "__main__":
    # Quick self-test: simulate a receiver who has a long-term ECC keypair
    # (e.g. hospital server), and a sender encrypting a critical file for them.

    receiver_private, receiver_public = generate_ecc_keypair()

    original = b"CRITICAL: Patient ID 4521, Diagnosis: Type 2 Diabetes, Blood Group: O+"

    # Sender encrypts using only the receiver's PUBLIC key
    ciphertext, ephemeral_public = hybrid_encrypt(original, receiver_public)

    # Receiver decrypts using their PRIVATE key + the ephemeral public key sent along
    decrypted = hybrid_decrypt(ciphertext, ephemeral_public, receiver_private)

    print(f"Original:  {original}")
    print(f"Encrypted (unreadable): {ciphertext[:40]}...")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}")
