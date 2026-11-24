import re
from typing import List, Tuple
from bs4 import BeautifulSoup


class EmailPreprocessor:
    """Extracts linguistic and structural threat signals from raw email messages."""

    SUSPICIOUS_KEYWORDS = [
        "verify your account", "login immediately", "password reset",
        "wire transfer", "urgent action required", "bank statement",
        "unauthorized activity", "suspended account", "claim prize"
    ]

    @classmethod
    def clean_text(cls, raw_html: str, raw_text: str) -> str:
        """Strips HTML tags and normalizes whitespace."""
        if raw_html:
            soup = BeautifulSoup(raw_html, "html.parser")
            text = soup.get_text(separator=" ")
        else:
            text = raw_text or ""

        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def extract_urls(cls, text: str) -> List[str]:
        """Extracts embedded URLs using regex pattern matching."""
        url_pattern = r"https?://[^\s<>\"']+|www\.[^\s<>\"']+"
        return re.findall(url_pattern, text)

    @classmethod
    def extract_heuristic_signals(cls, subject: str, body: str, sender: str) -> List[str]:
        """Detects domain mismatches, high-urgency keywords, and suspicious framing."""
        indicators = []
        combined_text = f"{subject} {body}".lower()

        # Keyword matching
        for kw in cls.SUSPICIOUS_KEYWORDS:
            if kw in combined_text:
                indicators.append(f"Contains high-risk phrase: '{kw}'")

        # Sender vs domain check
        if "@" in sender:
            domain = sender.split("@")[-1].lower()
            if any(free_domain in domain for free_domain in ["tempmail", "disposable", "mailinator"]):
                indicators.append(f"Sender uses disposable email domain: {domain}")

        # Excessive caps check in subject
        if subject and sum(1 for c in subject if c.isupper()) / max(len(subject), 1) > 0.6:
            indicators.append("Subject line uses aggressive capitalization")

        return indicators

    @classmethod
    def prepare_transformer_input(cls, subject: str, body: str) -> str:
        """Formats email header and body into a structured transformer sequence."""
        cleaned_body = cls.clean_text("", body)
        return f"Subject: {subject} | Body: {cleaned_body[:512]}"
    