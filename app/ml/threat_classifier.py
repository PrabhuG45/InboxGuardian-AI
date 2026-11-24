import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.ml.preprocessor import EmailPreprocessor
from app.schemas.threat import ThreatAnalysisResult, ThreatCategory


class ThreatClassifierEngine:
    """DistilBERT-powered inference engine for real-time phishing and threat detection."""

    def __init__(self, model_name: str = "distilbert-base-uncased"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Using a sequence classification head mapped to threat labels
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=3
        ).to(self.device)
        self.model.eval()

        self.label_map = {0: ThreatCategory.BENIGN, 1: ThreatCategory.SPAM, 2: ThreatCategory.PHISHING}

    def analyze_email(
        self, message_id: str, subject: str, body_text: str, sender: str, body_html: str = ""
    ) -> ThreatAnalysisResult:
        # 1. Clean and extract features
        clean_text = EmailPreprocessor.clean_text(body_html, body_text)
        urls = EmailPreprocessor.extract_urls(clean_text)
        indicators = EmailPreprocessor.extract_heuristic_signals(subject, clean_text, sender)

        # 2. Tokenize input sequence
        sequence_input = EmailPreprocessor.prepare_transformer_input(subject, clean_text)
        inputs = self.tokenizer(
            sequence_input,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

        # 3. Model Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = F.softmax(outputs.logits, dim=-1).squeeze().cpu().numpy()

        p_benign, p_spam, p_phishing = float(probabilities[0]), float(probabilities[1]), float(probabilities[2])

        # 4. Synthesize Heuristics & ML Probabilities
        if len(indicators) >= 2 or p_phishing > 0.65:
            primary_category = ThreatCategory.PHISHING
            overall_level = "CRITICAL"
            action = "QUARANTINE_IMMEDIATELY"
        elif p_spam > 0.60 or len(indicators) == 1:
            primary_category = ThreatCategory.SPAM
            overall_level = "SUSPICIOUS"
            action = "FLAG_FOR_REVIEW"
        else:
            primary_category = ThreatCategory.BENIGN
            overall_level = "SAFE"
            action = "DELIVER_TO_INBOX"

        confidence = max(p_benign, p_spam, p_phishing)

        return ThreatAnalysisResult(
            message_id=message_id,
            overall_threat_level=overall_level,
            primary_category=primary_category,
            confidence_score=round(confidence, 4),
            phishing_probability=round(p_phishing, 4),
            spam_probability=round(p_spam, 4),
            flagged_indicators=indicators,
            extracted_urls=urls,
            recommended_action=action
        )


threat_engine = ThreatClassifierEngine()