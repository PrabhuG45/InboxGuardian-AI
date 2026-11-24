from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class EmailAttachment(BaseModel):
    attachment_id: str
    filename: str
    mime_type: str
    size_bytes: int | str = 0

class EmailHeader(BaseModel):
    name: str
    value: str

class UnifiedEmailMessage(BaseModel):
    id: str = Field(..., description="Gmail message ID")
    thread_id: str = Field(..., description="Gmail thread ID ")
    sender: str = Field(..., description="From header")
    recipients: List[str] = Field(default_factory=list, description="To recipients")
    cc: List[str] = Field(default_factory=list, description="CC recipients")
    subject: str = Field(default="", description="Email subject line")
    body_text: str = Field(default="", description="Plaintext body representation")
    body_html: Optional[str] = Field(default=None, description="HTML body representation")
    date: Optional[str] = None
    snippet: str = Field(default="", description="Short preview snippet")
    timestamp: Optional[datetime] = Field(default=None, description="Received or sent time")
    labels: List[str] = Field(default_factory=list, description="Gmail label IDs")
    attachments: List[EmailAttachment] = Field(default_factory=list)

class UnifiedThread(BaseModel):
    thread_id: str
    history_id: Optional[str] = None
    messages: List[UnifiedEmailMessage] = Field(default_factory=list)

class DraftCreatePayload(BaseModel):
    to: List[EmailStr]
    cc: List[EmailStr] = Field(default_factory=list)
    bcc: List[EmailStr] = Field(default_factory=list)
    subject: str
    body_text: str
    body_html: Optional[str] = None
    thread_id: Optional[str] = Field(
        None, description="Provide if replying within an existing thread"
    )

class SendEmailPayload(BaseModel):
    to: List[EmailStr]
    cc: List[EmailStr] = Field(default_factory=list)
    bcc: List[EmailStr] = Field(default_factory=list)
    subject: str
    body_text: str
    body_html: Optional[str] = None
    thread_id: Optional[str] = None

class LabelUpdatePayload(BaseModel):
    add_label_ids: List[str] = Field(default_factory=list)
    remove_label_ids: List[str] = Field(default_factory=list)