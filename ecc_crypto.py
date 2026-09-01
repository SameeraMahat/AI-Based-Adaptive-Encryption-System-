"""
ECC (Elliptic Curve Cryptography) key exchange for the AI-Based Adaptive
Encryption System.

IMPORTANT CONCEPT: ECC here is NOT used to encrypt the file itself.
It's used to securely derive a shared secret key between two parties
(e.g. sender and receiver) using ECDH (Elliptic Curve Diffie-Hellman).
That shared secret is then used as the AES key in hybrid_crypto.py.

Why this matters: ECC key exchange means we never have to send the
actual AES key over an insecure channel — each side derives the SAME
key independently, using their own private key + the other side's
public key.

Curve used: SECP384R1 (a widely trusted, strong curve)
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

CURVE = ec.SECP384R1()


def generate_ecc_keypair():
    """
    Generates a new ECC private/public key pair.
    Returns: (private_key, public_key)
    """
    private_key = ec.generate_private_key(CURVE)
    public_key = private_key.public_key()
    return private_key, public_key


def derive_shared_key(my_private_key, their_public_key) -> bytes:
    """
    Performs ECDH key exchange: combines my private key with their public
    key to derive a shared secret. The other party does the same with
    THEIR private key + MY public key, and arrives at the identical secret.

    The raw ECDH output isn't directly safe to use as an AES key, so we
    run it through HKDF (a standard key-derivation function) to produce
    a clean 256-bit key suitable for AES.
    """
    shared_secret = my_private_key.exchange(ec.ECDH(), their_public_key)

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,  # 256-bit key, ready for AES
        salt=None,
        info=b"adaptive-encryption-ecc-aes-key",
    ).derive(shared_secret)

    return derived_key


if __name__ == "__main__":
    # Quick self-test: simulate sender + receiver deriving the SAME key
    # independently, without ever transmitting the key itself.

    sender_private, sender_public = generate_ecc_keypair()
    receiver_private, receiver_public = generate_ecc_keypair()

    # Sender derives shared key using their private key + receiver's public key
    sender_shared_key = derive_shared_key(sender_private, receiver_public)

    # Receiver derives shared key using their private key + sender's public key
    receiver_shared_key = derive_shared_key(receiver_private, sender_public)

    print(f"Sender's derived key:   {sender_shared_key.hex()}")
    print(f"Receiver's derived key: {receiver_shared_key.hex()}")
    print(f"Keys match: {sender_shared_key == receiver_shared_key}")
