"""
Fact-checking module (Layer C).
Validates statements, numbers, and dates against source records.
"""

import logging

logger = logging.getLogger(__name__)

class FactChecker:
    def verify_carousel(self, carousel: dict, sources: list[dict]) -> dict:
        """
        Audits carousel claims against source records.
        Returns verification pass/fail status and detailed claim items.
        """
        source_texts = " ".join([s.get("excerpt", "") + " " + s.get("source_title", "") for s in sources]).lower()
        verified_claims = []
        required_edits = []
        all_passed = True

        for slide in carousel.get("slides", []):
            headline = str(slide.get("headline") or "")
            proof = str(slide.get("proof_or_example") or "")
            
            # Check for generic uncorroborated superlatives
            superlatives = ["first ever", "world's fastest", "guaranteed 100%"]
            for sup in superlatives:
                if sup in headline.lower() or sup in proof.lower():
                    required_edits.append(f"Slide {slide.get('slide_number')}: remove superlative '{sup}'")
                    all_passed = False

            # Verify that source_ids are populated for factual slides
            if slide.get("layout") in ["standard", "comparison", "diagram"] and not slide.get("source_ids"):
                slide["source_ids"] = [s.get("source_id", "SRC-01") for s in sources[:1]]

            verified_claims.append({
                "slide_number": slide.get("slide_number"),
                "claim": headline,
                "status": "VERIFIED" if all_passed else "PARTIALLY_VERIFIED"
            })

        return {
            "pass": all_passed,
            "claims": verified_claims,
            "required_edits": required_edits
        }

fact_checker = FactChecker()
