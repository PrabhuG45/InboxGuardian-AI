import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
import httpx
from app.core.config import settings
from app.api.v1.endpoints.auth import _USER_TOKEN_DB
from app.core.token_vault import token_vault
from app.core.zero_trust import get_current_user
from app.schemas.auth import UserContext
from app.schemas.email import (
    DraftCreatePayload,
    LabelUpdatePayload,
    SendEmailPayload,
    UnifiedEmailMessage,
    UnifiedThread,
)
from app.services.email_client import GmailConnector

router = APIRouter()

FOLDER_QUERY_MAP = {
    "INBOX": "in:inbox",
    "STARRED": "is:starred",
    "DRAFT": "in:drafts",
    "SENT": "in:sent",
    "TRASH": "in:trash",
}

async def get_gmail_client(
    user: UserContext = Security(get_current_user, scopes=["email:read"])
) -> GmailConnector:
    encrypted_token = _USER_TOKEN_DB.get(user.email)
    if not encrypted_token:
        return GmailConnector(access_token="test_token")

    refresh_token = token_vault.decrypt_token(encrypted_token)
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google access token refresh failed.",
        )
    access_token = response.json().get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google did not return an access token.",
        )
    return GmailConnector(access_token=access_token)


@router.get(
    "/messages",
    response_model=List[UnifiedEmailMessage],
    summary="List & Normalize Recent Emails",
)
async def list_emails(
    q: Optional[str] = Query(None, description="Folder name or Gmail search filter e.g. is:unread"),
    limit: int = Query(30, ge=1, le=100),
    user: UserContext = Security(get_current_user, scopes=["email:read"]),
    client: GmailConnector = Depends(get_gmail_client),
):
    normalized_query = FOLDER_QUERY_MAP.get(q.strip().upper(), q.strip()) if q else "in:inbox"
    refs = await client.list_messages(query=normalized_query, max_results=limit)
    if not refs:
        return []

    semaphore = asyncio.Semaphore(10)

    async def _fetch_one(msg_id: str) -> UnifiedEmailMessage:
        async with semaphore:
            return await client.get_message(msg_id)

    messages = await asyncio.gather(*(_fetch_one(ref["id"]) for ref in refs))
    return list(messages)


@router.get(
    "/threads/{thread_id}",
    response_model=UnifiedThread,
    summary="Get Full Normalized Thread",
)
async def get_thread(
    thread_id: str,
    user: UserContext = Security(get_current_user, scopes=["email:read"]),
    client: GmailConnector = Depends(get_gmail_client),
):
    return await client.get_thread(thread_id)


@router.post("/drafts", summary="Create Cloud-Synced Draft")
async def create_draft(
    payload: DraftCreatePayload,
    user: UserContext = Security(get_current_user, scopes=["email:draft"]),
    client: GmailConnector = Depends(get_gmail_client),
):
    return await client.create_draft(payload)

@router.post("/send", summary="Dispatch Email via Gmail Outbox")
async def send_email(
    payload: SendEmailPayload,
    user: UserContext = Security(get_current_user, scopes=["email:send"]),
    client: GmailConnector = Depends(get_gmail_client),
):
    return await client.send_email(payload)


@router.post("/messages/{message_id}/labels", summary="Update Email Labels")
async def update_message_labels(
    message_id: str,
    payload: LabelUpdatePayload,
    user: UserContext = Security(get_current_user, scopes=["email:read"]),
    client: GmailConnector = Depends(get_gmail_client),
):
    return await client.modify_labels(
        message_id,
        add_labels=payload.add_label_ids,
        remove_labels=payload.remove_label_ids,
    )


@router.post("/messages/{message_id}/trash", summary="Move Email to Trash")
async def trash_message(
    message_id: str,
    user: UserContext = Security(get_current_user, scopes=["email:read"]),
    client: GmailConnector = Depends(get_gmail_client),
):
    return await client.trash_message(message_id)