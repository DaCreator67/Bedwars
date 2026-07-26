"""Password encryption utilities."""
import hashlib
import os
from base64 import b64encode, b64decode

class PasswordEncryption:
    """Handle password encryption and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = os.urandom(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return b64encode(salt + pwd_hash).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            decoded = b64decode(hashed.encode('utf-8'))
            salt = decoded[:32]
            stored_hash = decoded[32:]
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return pwd_hash == stored_hash
        except Exception:
            return False
