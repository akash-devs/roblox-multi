import base64
import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Security:
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derives a 32-byte URL-safe base64 key from a password and salt using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def generate_salt() -> bytes:
        return os.urandom(16)

    @staticmethod
    def encrypt(data_dict: dict, password: str, salt: bytes = None) -> dict:
        if not salt:
            salt = Security.generate_salt()
        
        key = Security.derive_key(password, salt)
        f = Fernet(key)
        
        # Proper JSON string serialization safely preserves special characters
        json_str = json.dumps(data_dict)
        token = f.encrypt(json_str.encode('utf-8'))
        
        return {
            "is_encrypted": True,
            "salt": base64.b64encode(salt).decode('utf-8'),
            "data": token.decode('utf-8')
        }

    @staticmethod
    def decrypt(encrypted_store: dict, password: str) -> dict:
        salt = base64.b64decode(encrypted_store['salt'])
        token = encrypted_store['data'].encode('utf-8')
        
        key = Security.derive_key(password, salt)
        f = Fernet(key)
        
        decrypted_data = f.decrypt(token)
        return json.loads(decrypted_data.decode('utf-8'))