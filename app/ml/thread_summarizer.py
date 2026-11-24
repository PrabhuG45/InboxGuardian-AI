import re
from typing import List
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from app.schemas.summary import ThreadSummaryResponse


class ThreadSummarizerEngine:
    """T5-powered inference engine for multi-turn email thread summarization."""

    def __init__(self, model_name: str = "t5-small"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name).to(
            self.device
        )
        self.model.eval()

    def summarize_thread(
        self, thread_id: str, message_bodies: List[str]
    ) -> ThreadSummaryResponse:
        # 1. Combine chronological messages into a single thread block
        formatted_thread = "\n---\n".join(
            [f"Email {idx + 1}: {body.strip()}" for idx, body in enumerate(message_bodies)]
        )

        prompt = f"summarize email thread: {formatted_thread[:1024]}"

        # 2. Tokenize and run T5 Inference
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        ).to(self.device)

        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs.input_ids,
                max_length=150,
                min_length=30,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True,
            )

        raw_digest = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        # 3. Extract heuristic action items and key bullet points
        combined_text = " ".join(message_bodies)
        action_items = self._extract_action_items(combined_text)
        bullet_points = [
            f"Thread spans {len(message_bodies)} sequential messages.",
            f"Core topic centered on: {raw_digest[:80]}...",
        ]

        return ThreadSummaryResponse(
            thread_id=thread_id,
            concise_digest=raw_digest,
            bullet_points=bullet_points,
            action_items=action_items,
            participant_count=len(message_bodies),
        )

    def _extract_action_items(self, text: str) -> List[str]:
        """Extracts candidate action items based on task and imperative patterns."""
        action_patterns = [
            r"(?:please|kindly|need to|must|should)\s+([^.!?\n]+)",
            r"(?:send over|review|update|submit|verify)\s+([^.!?\n]+)",
        ]
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                item = m.strip()
                if len(item) > 10 and item not in actions:
                    actions.append(item[:100])
        return actions if actions else ["No explicit action items identified."]


summarizer_engine = ThreadSummarizerEngine()