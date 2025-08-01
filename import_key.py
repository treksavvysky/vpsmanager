"""Utility to import an existing SSH private key into the vault."""
import argparse
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

from app.database import Base
from app.models.credential import Credential, CredentialType
from app.utils.vault import encrypt_secret

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./servers.db")

def main():
    parser = argparse.ArgumentParser(description="Import SSH key to vault")
    parser.add_argument("name", help="Credential name")
    parser.add_argument("path", help="Path to private key file")
    args = parser.parse_args()

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session()
    with open(args.path, "r") as f:
        key_data = f.read()

    encrypted = encrypt_secret(key_data)
    cred = Credential(name=args.name, type=CredentialType.ssh_key, secret=encrypted)
    db.add(cred)
    db.commit()
    print(f"Imported key as '{args.name}'")

if __name__ == "__main__":
    main()
