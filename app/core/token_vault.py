import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings
from app.schemas.auth import EncryptedTokenRecord


class TokenVault:
    """Handles envelope encryption for OAuth tokens at rest using AES-256-GCM."""

    def __init__(self):
        derived_key = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        self.aesgcm = AESGCM(derived_key)

    def encrypt_token(self, plaintext_token: str) -> EncryptedTokenRecord:
        """Encrypts an OAuth token returning Base64 ciphertext and 96-bit nonce."""
        nonce = os.urandom(12) 
        ciphertext = self.aesgcm.encrypt(
            nonce, plaintext_token.encode("utf-8"), None
        )
        return EncryptedTokenRecord(
            ciphertext=base64.b64encode(ciphertext).decode("utf-8"),
            nonce=base64.b64encode(nonce).decode("utf-8"),
        )

    def decrypt_token(self, record: EncryptedTokenRecord) -> str:
        """Decrypts and verifies authentication tag for a stored token."""
        raw_nonce = base64.b64decode(record.nonce.encode("utf-8"))
        raw_ciphertext = base64.b64decode(record.ciphertext.encode("utf-8"))
        # Standard signature: decrypt(nonce, data, associated_data)
        decrypted_bytes = self.aesgcm.decrypt(raw_nonce, raw_ciphertext, None)
        return decrypted_bytes.decode("utf-8")


token_vault = TokenVault()