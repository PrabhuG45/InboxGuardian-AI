import uuid
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, Query, Security, status
from fastapi.responses import RedirectResponse
import httpx
from app.core.config import settings
from app.core.security import create_access_token, generate_pkce_pair, generate_state_token
from app.core.token_vault import token_vault
from app.core.zero_trust import get_current_user
from app.schemas.auth import EncryptedTokenRecord, UserContext

router = APIRouter()

_OAUTH_STATE_STORE: dict[str, dict[str, str]] = {}
_USER_TOKEN_DB: dict[str, EncryptedTokenRecord] = {}

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


@router.get("/google", summary="Start Google OAuth Sign-in")
async def start_google_oauth():
    code_verifier, code_challenge = generate_pkce_pair()
    state = generate_state_token()
    _OAUTH_STATE_STORE[state] = {"code_verifier": code_verifier}
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


@router.get("/google/callback", summary="Validate OAuth Callback & Issue Zero Trust JWT")
async def callback_google(
    code: str | None = Query(None, description="Authorization code from provider"),
    state: str = Query(..., description="Anti-CSRF state token"),
    error: str | None = Query(None, description="OAuth provider error"),
):
    """Validates state and PKCE varifier, exchanges code for tokens, and returns app JWT."""
    session_data = _OAUTH_STATE_STORE.pop(state, None)
    if not session_data:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="INvalid or expired OAuth state parameter (CSRF protection failed).",
        )
    if error:
        callback_url = f"{settings.FRONTEND_URL.rstrip('/')}/#"
        callback_url += urlencode({"error": error})
        return RedirectResponse(callback_url)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return an authorization code.",
        )

    code_verifier = session_data["code_verifier"]

    token_payload = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "code_verifier": code_verifier,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
    
        token_res = await client.post(GOOGLE_TOKEN_URL, data=token_payload)
        if token_res.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"OAuth token exchange failed: {token_res.text}",
            )
        token_data = token_res.json()

        user_res = await client.get(
            GOOGLE_USERINFO_URL, 
            headers={"Authorization": f"Bearer {token_data[ 'access_token']}"}
        )
        if user_res.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to retrieve user profile from provider."
            )
        user_info = user_res.json()

    user_email = user_info["email"]

    if "refresh_token" in token_data:
        encrypted_record = token_vault.encrypt_token(token_data["refresh_token"])
        _USER_TOKEN_DB[user_email] =encrypted_record

    app_jwt = create_access_token(
        subject=user_email,
        claims={
            "jti": str(uuid.uuid4()),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "scopes": [
                "email:read",
                "email:send",
                "email:draft",
                "email:classify",
                "email:summarize",
            ],
        },
    )

    callback_url = f"{settings.FRONTEND_URL.rstrip('/')}/#"
    callback_url += urlencode({"access_token": app_jwt})
    return RedirectResponse(callback_url)

@router.get("/me", response_model=UserContext, summary="Get Current Validated USer")
async def get_me(
    current_user: UserContext = Security(get_current_user, scopes=["email:read"])
):
    """Protected test route requiring the 'email:read' scope."""
    return current_user 