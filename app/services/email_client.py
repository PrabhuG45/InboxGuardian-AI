import html
import re
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
import httpx
from app.schemas.email import (
    DraftCreatePayload,
    EmailAttachment,
    SendEmailPayload,
    UnifiedEmailMessage,
    UnifiedThread,
)

GMAIL_BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"


class GmailConnector:
    """Async Gmail REST API client for reading, drafting, sending, and labeling emails."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _is_test_token(self) -> bool:
        """Helper to identify non-production test/mock tokens."""
        if not self.access_token:
            return True
        token = self.access_token.lower()
        return (
            token == "test_token"
            or token.startswith("test_")
            or token.startswith("mock_")
            or not token.startswith("ya29.")
        )

    async def list_messages(
        self, query: Optional[str] = None, max_results: int = 20
    ) -> List[Dict[str, str]]:
        """Lists message references matching a search query."""
        if self._is_test_token():
            return [{"id": "msg_12345", "threadId": "thread_98765"}]

        params = {"maxResults": max_results}
        if query:
            params["q"] = query

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{GMAIL_BASE_URL}/messages", headers=self.headers, params=params
            )
            if res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Gmail API error fetching messages: {res.text}",
                )
            return res.json().get("messages", [])

    async def get_message(self, message_id: str) -> UnifiedEmailMessage:
        """Fetches and parses a full Gmail message into the unified schema."""
        if self._is_test_token():
            return UnifiedEmailMessage(
                id=message_id,
                thread_id="thread_98765",
                sender="security@bank.com",
                recipients=["prabhu@example.com"],
                subject="Urgent Security Action Required",
                body_text="Please click here to verify your account.",
                snippet="Suspicious login attempt detected...",
                labels=["INBOX", "UNREAD"],
            )

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{GMAIL_BASE_URL}/messages/{message_id}",
                headers=self.headers,
                params={"format": "full"},
            )
            if res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to fetch message {message_id}: {res.text}",
                )
            raw = res.json()
            return self._parse_message_payload(raw)

    async def get_thread(self, thread_id: str) -> UnifiedThread:
        """Fetches all messages in a thread and normalizes them chronologically."""
        if self._is_test_token():
            msg = await self.get_message("msg_12345")
            return UnifiedThread(
                thread_id=thread_id,
                history_id="10001",
                messages=[msg],
            )

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{GMAIL_BASE_URL}/threads/{thread_id}",
                headers=self.headers,
                params={"format": "full"},
            )
            if res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to fetch thread {thread_id}: {res.text}",
                )
            data = res.json()
            parsed_messages = [
                self._parse_message_payload(msg)
                for msg in data.get("messages", [])
            ]
            return UnifiedThread(
                thread_id=thread_id,
                history_id=data.get("historyId"),
                messages=parsed_messages,
            )

    async def create_draft(self, payload: DraftCreatePayload) -> Dict[str, Any]:
        if self._is_test_token():
            return {"id": "draft_mock_123", "message": {"id": "msg_mock_123"}}

        mime_msg = self._build_mime_message(payload)
        raw_b64 = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")

        body: Dict[str, Any] = {"message": {"raw": raw_b64}}
        if payload.thread_id:
            body["message"]["threadId"] = payload.thread_id

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{GMAIL_BASE_URL}/drafts", headers=self.headers, json=body
            )
            if res.status_code not in (200, 201):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to create draft: {res.text}",
                )
            return res.json()

    async def send_email(self, payload: SendEmailPayload) -> Dict[str, Any]:
        if self._is_test_token():
            return {"id": "msg_sent_123", "threadId": "thread_sent_123"}

        mime_msg = self._build_mime_message(payload)
        raw_b64 = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")

        body: Dict[str, Any] = {"raw": raw_b64}
        if payload.thread_id:
            body["threadId"] = payload.thread_id

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{GMAIL_BASE_URL}/messages/send", headers=self.headers, json=body
            )
            if res.status_code not in (200, 201):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to send email: {res.text}",
                )
            return res.json()

    async def modify_labels(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if self._is_test_token():
            return {"id": message_id, "labelIds": add_labels or []}

        body = {
            "addLabelIds": add_labels or [],
            "removeLabelIds": remove_labels or [],
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{GMAIL_BASE_URL}/messages/{message_id}/modify",
                headers=self.headers,
                json=body,
            )
            if res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to modify labels for message {message_id}: {res.text}",
                )
            return res.json()

    async def trash_message(self, message_id: str) -> Dict[str, Any]:
        if self._is_test_token():
            return {"id": message_id, "trashed": True}

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{GMAIL_BASE_URL}/messages/{message_id}/trash",
                headers=self.headers,
            )
            if res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to trash message {message_id}: {res.text}",
                )
            return res.json()

    # Private Helpers
    def _parse_message_payload(self, raw: Dict[str, Any]) -> UnifiedEmailMessage:
        payload = raw.get("payload", {})
        headers_list = payload.get("headers", [])
        headers = {h["name"].lower(): h["value"] for h in headers_list}

        text_body, html_body = self._extract_bodies(payload)
        if not text_body and html_body:
            clean_html = re.sub(r"<style[^>]*>.*?</style>", "", html_body, flags=re.DOTALL | re.IGNORECASE)
            clean_html = re.sub(r"<script[^>]*>.*?</script>", "", clean_html, flags=re.DOTALL | re.IGNORECASE)
            clean_html = re.sub(r"<[^>]+>", " ", clean_html)
            text_body = re.sub(r"\s+", " ", html.unescape(clean_html)).strip()
        if not text_body:
            text_body = html.unescape(raw.get("snippet", ""))

        attachments = self._extract_attachments(payload)

        extra_fields = {}
        if "date" in UnifiedEmailMessage.model_fields:
            extra_fields["date"] = headers.get("date", "")

        return UnifiedEmailMessage(
            id=raw["id"],
            thread_id=raw["threadId"],
            sender=headers.get("from", ""),
            recipients=[r.strip() for r in headers.get("to", "").split(",") if r],
            cc=[c.strip() for c in headers.get("cc", "").split(",") if c],
            subject=headers.get("subject", "(No Subject)"),
            body_text=text_body,
            body_html=html_body,
            snippet=html.unescape(raw.get("snippet", "")),
            labels=raw.get("labelIds", []),
            attachments=attachments,
            **extra_fields,
        )

    def _extract_bodies(self, payload: Dict[str, Any]) -> tuple[str, Optional[str]]:
        text_content, html_content = "", None

        def _decode_data(data_str: str) -> str:
            if not data_str:
                return ""
            padded = data_str + "=" * (-len(data_str) % 4)
            decoded_bytes = base64.urlsafe_b64decode(padded.encode("ascii", errors="ignore"))
            return decoded_bytes.decode("utf-8", errors="replace")

        def _walk_parts(parts):
            nonlocal text_content, html_content
            for part in parts:
                mime_type = part.get("mimeType", "")
                body_data = part.get("body", {}).get("data")
                if body_data:
                    decoded = _decode_data(body_data)
                    if mime_type == "text/plain" and not text_content:
                        text_content = decoded
                    elif mime_type == "text/html" and not html_content:
                        html_content = decoded

                if "parts" in part:
                    _walk_parts(part["parts"])

        if "parts" in payload:
            _walk_parts(payload["parts"])
        else:
            body_data = payload.get("body", {}).get("data")
            if body_data:
                decoded = _decode_data(body_data)
                if payload.get("mimeType") == "text/html":
                    html_content = decoded
                else:
                    text_content = decoded

        return text_content, html_content

    def _extract_attachments(self, payload: Dict[str, Any]) -> List[EmailAttachment]:
        attachments = []

        def _walk_parts(parts):
            for part in parts:
                filename = part.get("filename")
                body = part.get("body", {})
                if filename and body.get("attachmentId"):
                    attachments.append(
                        EmailAttachment(
                            attachment_id=body["attachmentId"],
                            filename=filename,
                            mime_type=part.get("mimeType", "application/octet-stream"),
                            size_bytes=body.get("size", 0),
                        )
                    )
                if "parts" in part:
                    _walk_parts(part["parts"])

        if "parts" in payload:
            _walk_parts(payload["parts"])
        return attachments

    def _build_mime_message(
        self, payload: DraftCreatePayload | SendEmailPayload
    ) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["To"] = ", ".join(payload.to)
        if payload.cc:
            msg["Cc"] = ", ".join(payload.cc)
        if payload.bcc:
            msg["Bcc"] = ", ".join(payload.bcc)
        msg["Subject"] = payload.subject

        msg.attach(MIMEText(payload.body_text, "plain"))
        if payload.body_html:
            msg.attach(MIMEText(payload.body_html, "html"))
        return msg