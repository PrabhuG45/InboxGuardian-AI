import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any , Dict
import jwt 
from app.core.config import settings

def generate_pkce_pair() -> tuple[str, str]:
    """Generates a high-entropy code_verifier and code_challenge (S256)."""
    code_verifier = secrets.token_urlsafe(64)
    hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(hashed).decode("ascii").rstrip("=")
    )
    return code_verifier, code_challenge 

def generate_state_token() -> str:
    """Generates a cryptographically secure state nonce to prevent CSRF."""
    return secrets.token_urlsafe(32)


def create_access_token(
    subject: str | Any, claims: Dict[str, Any] = None
)  -> str:
     """Generates an internal Zero-Trust session JWT with bounded expiration.""" 
     expire = datetime.now(timezone.utc) + timedelta(
         minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
     )
     payload = {
         "iss": settings.PROJECT_NAME,
         "sub": str(subject),
         "exp": expire,
         "iat": datetime.now(timezone.utc),
     }
     if claims: 
          payload.update(claims)
     return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    