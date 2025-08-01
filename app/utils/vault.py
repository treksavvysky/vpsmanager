import os
from cryptography.fernet import Fernet
from fastapi import HTTPException

VAULT_KEY = os.getenv("VAULT_KEY")

if not VAULT_KEY:
    raise RuntimeError("VAULT_KEY environment variable must be set")

_fernet = Fernet(VAULT_KEY)


def encrypt_secret(secret: str) -> str:
    """Encrypt a secret string using the vault key."""
    return _fernet.encrypt(secret.encode()).decode()


def decrypt_secret(token: str) -> str:
    """Decrypt a previously encrypted secret."""
    return _fernet.decrypt(token.encode()).decode()
