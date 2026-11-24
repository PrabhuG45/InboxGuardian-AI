from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, Text, JSON, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EncryptedTokenVaultModel(Base):
    """Stores AES-256-GCM encrypted OAuth refresh tokens at rest."""

    __tablename__ = "token_vault"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    encrypted_token: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ThreatLogModel(Base):
    """Stores ML threat detection outputs and flagged security indicators."""

    __tablename__ = "threat_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    overall_threat_level: Mapped[str] = mapped_column(String(32), nullable=False)
    primary_category: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    phishing_probability: Mapped[float] = mapped_column(Float, nullable=False)
    spam_probability: Mapped[float] = mapped_column(Float, nullable=False)
    flagged_indicators: Mapped[list] = mapped_column(JSON, default=list)
    extracted_urls: Mapped[list] = mapped_column(JSON, default=list)
    recommended_action: Mapped[str] = mapped_column(String(64), nullable=False)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLogModel(Base):
    """Stores Zero Trust access logs and scope enforcement activity."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    scopes_used: Mapped[list] = mapped_column(JSON, default=list)
    client_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)