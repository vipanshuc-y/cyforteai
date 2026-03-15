from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class EncryptionHandler:
    """Handle encryption and decryption of messages."""
    
    def __init__(self, secret_key):
        """Initialize encryption handler with a secret key."""
        # Derive a key from the secret_key
        key = Fernet.generate_key() if not secret_key else self._derive_key(secret_key)
        self.cipher = Fernet(key)
        
    @staticmethod
    def _derive_key(secret_key):
        """Derive a valid Fernet key from a secret string."""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        from cryptography.hazmat.backends import default_backend
        import base64
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'cyforteai_salt_',
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(
            kdf.derive(secret_key.encode())
        )
        return key
        
    def encrypt_message(self, message):
        """Encrypt a message."""
        try:
            if isinstance(message, str):
                message = message.encode()
            encrypted = self.cipher.encrypt(message)
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None
            
    def decrypt_message(self, encrypted_message):
        """Decrypt a message."""
        try:
            if isinstance(encrypted_message, str):
                encrypted_message = encrypted_message.encode()
            decrypted = self.cipher.decrypt(encrypted_message)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
