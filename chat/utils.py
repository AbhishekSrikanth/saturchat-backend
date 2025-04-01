from django.conf import settings
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import hashlib


def encrypt_api_key(plaintext_key, master_key=settings.SECRET_KEY):
    """
    Encrypt sensitive API keys before storing in database.
    This is server-side encryption, separate from the client-side E2E encryption.
    """
    # Create a key from the master key
    key = hashlib.sha256(master_key.encode()).digest()

    # Generate a random IV (Initialization Vector)
    iv = get_random_bytes(AES.block_size)

    # Create cipher and encrypt
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plaintext_key.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)

    # Combine IV and encrypted data and encode as base64
    result = base64.b64encode(iv + encrypted_data).decode('utf-8')
    return result


def decrypt_api_key(encrypted_key, master_key=settings.SECRET_KEY):
    """Decrypt an API key that was encrypted with encrypt_api_key."""
    if not encrypted_key:
        return None

    # Create key from master key
    key = hashlib.sha256(master_key.encode()).digest()

    # Decode from base64
    encrypted_data = base64.b64decode(encrypted_key)

    # Extract IV and ciphertext
    iv = encrypted_data[:AES.block_size]
    ciphertext = encrypted_data[AES.block_size:]

    # Decrypt
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = cipher.decrypt(ciphertext)

    # Unpad and return
    try:
        plaintext = unpad(padded_data, AES.block_size).decode('utf-8')
        return plaintext
    except (ValueError, UnicodeDecodeError):
        return None
