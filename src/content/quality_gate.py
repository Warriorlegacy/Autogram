"""
Quality Gate & Automated Editor (Layer C).
Scores carousels, enforces brand guardrails, checks banned clichés, and approves for rendering.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
BRAND_FILE = Path(__file__).parent.parent.parent / "data" / "brand.json"

class QualityGate:
    def __init__(self, brand_file: Path = BRAND_FILE):
        self.brand_file = brand_file
        self.banned_phrases = self._load_banned_phrases()

    def _load_banned_phrases(self) -> list[str]:
        if self.brand_file.exists():
            try:
                data = json.loads(self.brand_file.read_text(encoding="utf-8"))
                return [p.lower() for p in data.get("avoid", [])]
            except Exception:
                pass
        return [
            "game-changer", "unlock the power of", "in today's fast-paced world",
            "dive into", "let's explore", "at its core", "stands as a testament to",
            "in conclusion", "it's important to note", "seamless", "robust", "unleash",
            "not just x, it's y", "faster, smarter, better"
        ]

    def evaluate(self, carousel: dict) -> dict:
        """
        Evaluates carousel against automatic rejection rules and scores 0-100.
        """
        score = 100
        rejection_reasons = []
        edits = []

        slides = carousel.get("slides", [])
        num_slides = len(slides)

        # 1. Slide count check (Must be 7 - 10)
        if num_slides < 7 or num_slides > 10:
            rejection_reasons.append(f"Slide count ({num_slides}) outside allowed range (7-10).")
            score -= 30

        # 2. Check each slide for banned phrases and text length
        all_text = ""
        for s in slides:
            headline = str(s.get("headline") or "")
            body_val = s.get("body", "")
            if isinstance(body_val, list):
                body = " ".join(str(item) for item in body_val)
                s["body"] = body
            else:
                body = str(body_val or "")
            slide_combined = f"{headline} {body}".lower()
            all_text += " " + slide_combined

            # Word count check on dense slides
            word_count = len(body.split())
            if word_count > 42:
                edits.append({
                    "slide_number": s.get("slide_number"),
                    "issue": f"Body text word count ({word_count}) exceeds recommended 36 words."
                })
                score -= 5

            # Banned phrase check
            for banned in self.banned_phrases:
                if banned in slide_combined:
                    rejection_reasons.append(
                        f"Slide {s.get('slide_number')} contains banned phrase: '{banned}'"
                    )
                    score -= 25

        # 3. Caption check
        caption = carousel.get("caption", "").lower()
        for banned in self.banned_phrases:
            if banned in caption:
                rejection_reasons.append(f"Caption contains banned phrase: '{banned}'")
                score -= 20

        # Final decision
        score = max(0, score)
        approved = len(rejection_reasons) == 0 and score >= 80

        result = {
            "score": score,
            "approved": approved,
            "rejection_reasons": rejection_reasons,
            "edits": edits,
            "editorial_notes": "Approved for rendering" if approved else "Revisions required."
        }

        if approved:
            logger.info(f"Quality Gate PASSED (Score: {score}/100)")
        else:
            logger.warning(f"Quality Gate FAILED (Score: {score}/100). Reasons: {rejection_reasons}")

        return result

quality_gate = QualityGate()
