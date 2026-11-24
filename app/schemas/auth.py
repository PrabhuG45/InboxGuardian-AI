from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class TokenPayload(BaseModel):
    sub: EmailStr = Field(
        ..., description="Subject identifier (usser email address)"
    )
    iss: str = Field(..., description="Token issuer")
    exp: int = Field(..., description="Unix expiration timestamp")
    iat: int = Field(..., description="Unix issued-at timestamp")
    jti: Optional[str] = Field(
        None, description="Unique JWT ID for revoaction tracking"
    )
    scopes: List[str] = Field(
        default_factory=list, description="OAuth permission scopes granted"
    )
    name: Optional[str] = None
    picture: Optional[str] = None

class UserContext(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None 
    scopes: List[str] = Field(default_factory=list)

class EncryptedTokenRecord(BaseModel):
    ciphertext: str
    nonce: str
    key_id: str = "primary"