from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ThreatCategory(str, Enum):
    BENIGN = "BENIGN"
    SPAM = "SPAM"
    PHISHING = "PHISHING"
    SUSPICIOUS_URGENCY = "SUSPICIOUS_URGENCY"


class ThreatAnalysisResult(BaseModel):
    message_id: str
    overall_threat_level: str = Field(..., description="SAFE, SUSPICIOUS, or CRITICAL")
    primary_category: ThreatCategory
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    phishing_probability: float = Field(..., ge=0.0, le=1.0)
    spam_probability: float = Field(..., ge=0.0, le=1.0)
    flagged_indicators: List[str] = Field(default_factory=list)
    extracted_urls: List[str] = Field(default_factory=list)
    recommended_action: str