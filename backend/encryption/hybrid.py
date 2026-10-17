import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

HYBRID_KEY_FOLDER = os.path.join(
    BACKEND_DIR,
    "keys",
    "hybrid"
)

def generate_rsa_key_pair():
    """
    Generate an RSA-2048 public/private key pair.

    Returns:
        private_key
        public_key
    """

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    return private_key, public_key


def save_rsa_keys(filename, private_key, public_key):
    """
    Save RSA public and private keys for a file.

    Keys are stored separately from encrypted files.
    """

    os.makedirs(HYBRID_KEY_FOLDER, exist_ok=True)

    base_name = os.path.basename(filename)

    private_key_path = os.path.join(
        HYBRID_KEY_FOLDER,
        base_name + ".private.pem"
    )

    public_key_path = os.path.join(
        HYBRID_KEY_FOLDER,
        base_name + ".public.pem"
    )

    # Save private key
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(private_key_path, "wb") as file:
        file.write(private_key_bytes)

    # Save public key
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(public_key_path, "wb") as file:
        file.write(public_key_bytes)

    return private_key_path, public_key_path


def load_private_key(filename):
    """
    Load an RSA private key from disk.
    """

    base_name = os.path.basename(filename)

    private_key_path = os.path.join(
        HYBRID_KEY_FOLDER,
        base_name + ".private.pem"
    )

    if not os.path.exists(private_key_path):
        raise FileNotFoundError(
            f"Hybrid private key not found for {filename}"
        )

    with open(private_key_path, "rb") as file:
        private_key = serialization.load_pem_private_key(
            file.read(),
            password=None
        )

    return private_key


def load_public_key(filename):
    """
    Load an RSA public key from disk.
    """

    base_name = os.path.basename(filename)

    public_key_path = os.path.join(
        HYBRID_KEY_FOLDER,
        base_name + ".public.pem"
    )

    if not os.path.exists(public_key_path):
        raise FileNotFoundError(
            f"Hybrid public key not found for {filename}"
        )

    with open(public_key_path, "rb") as file:
        public_key = serialization.load_pem_public_key(
            file.read()
        )

    return public_key


def encrypt_file(input_path, output_path, public_key):
    """
    Hybrid encryption using:

        AES-256-GCM for file encryption
        RSA-OAEP with SHA-256 for AES key protection

    Output format:

        12-byte AES nonce
        4-byte encrypted AES key length
        RSA-encrypted AES key
        AES-GCM ciphertext
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    # Generate random 256-bit AES session key
    aes_key = AESGCM.generate_key(
        bit_length=256
    )

    # Generate AES-GCM nonce
    nonce = os.urandom(12)

    # Read original file
    with open(input_path, "rb") as file:
        plaintext = file.read()

    # Encrypt file using AES-256-GCM
    aes = AESGCM(aes_key)

    ciphertext = aes.encrypt(
        nonce,
        plaintext,
        None
    )

    # Encrypt AES session key using RSA-OAEP
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Store encrypted data
    encrypted_key_length = len(encrypted_aes_key)

    with open(output_path, "wb") as file:

        # AES-GCM nonce
        file.write(nonce)

        # Length of RSA-encrypted AES key
        file.write(
            encrypted_key_length.to_bytes(
                4,
                byteorder="big"
            )
        )

        # RSA-encrypted AES key
        file.write(encrypted_aes_key)

        # AES-GCM ciphertext
        file.write(ciphertext)

    return {
        "algorithm": "AES-256-GCM + RSA-OAEP",
        "aes_key_size": 256,
        "rsa_key_size": 2048,
        "nonce_size": 12,
        "encrypted_key_size": encrypted_key_length
    }


def decrypt_file(input_path, output_path, private_key):
    """
    Decrypt a Hybrid encrypted file.

    Steps:

        1. Read AES-GCM nonce
        2. Read RSA-encrypted AES key
        3. Decrypt AES key using RSA private key
        4. Decrypt file using AES-256-GCM
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Encrypted file not found: {input_path}"
        )

    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    # Minimum structure:
    # 12-byte nonce + 4-byte key length
    if len(encrypted_data) < 16:
        raise ValueError(
            "Invalid hybrid encrypted file."
        )

    # Extract nonce
    nonce = encrypted_data[:12]

    # Extract encrypted AES key length
    encrypted_key_length = int.from_bytes(
        encrypted_data[12:16],
        byteorder="big"
    )

    # Validate encrypted key length
    if encrypted_key_length <= 0:
        raise ValueError(
            "Invalid encrypted AES key length."
        )

    key_start = 16
    key_end = key_start + encrypted_key_length

    if len(encrypted_data) <= key_end:
        raise ValueError(
            "Invalid hybrid encrypted file structure."
        )

    # Extract RSA-encrypted AES key
    encrypted_aes_key = encrypted_data[
        key_start:key_end
    ]

    # Remaining data is AES-GCM ciphertext
    ciphertext = encrypted_data[key_end:]

    # Recover AES session key using RSA private key
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # AES-256 requires a 32-byte key
    if len(aes_key) != 32:
        raise ValueError(
            "Recovered AES key must be exactly 32 bytes."
        )

    # Decrypt file
    aes = AESGCM(aes_key)

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    with open(output_path, "wb") as file:
        file.write(plaintext)

    return True