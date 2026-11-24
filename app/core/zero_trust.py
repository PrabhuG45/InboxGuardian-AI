from typing import Set
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
import jwt
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.auth import TokenPayload, UserContext

security_bearer = HTTPBearer(auto_error=True)
_REVOKED_JTIS: Set[str] = set()

def revoke_token(jti: str) -> None:
    """Adds a JWT unique identifier (jti) to the in-memory revocation list."""
    if jti:
        _REVOKED_JTIS.add(jti)

async def get_current_user(
    security_scopes: SecurityScopes,
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> UserContext:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or signature failed.",
        headers={"WWW-Authenticate": f"Bearer scope='{security_scopes.scope_str}'"},
    )
    try:
        payload_dict = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            issuer=settings.PROJECT_NAME,
            options={"require": ["exp", "iss", "sub", "iat"]},
        )
        token_data = TokenPayload(**payload_dict)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValidationError):
        raise credentials_exception

    if token_data.jti and token_data.jti in _REVOKED_JTIS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked.",
            headers={"WWW-Authenticate": f"Bearer scope='{security_scopes.scope_str}'"},
        )

    user_scopes = set(token_data.scopes)
    for required_scope in security_scopes.scopes:
        if required_scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Missing required scope '{required_scope}'.",
            )

    return UserContext(
        email=token_data.sub,
        name=token_data.name,
        picture=token_data.picture,
        scopes=token_data.scopes,
    )