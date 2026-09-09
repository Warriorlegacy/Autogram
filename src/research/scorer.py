"""
Topic scoring & candidate selection module (Layer B).
Scores candidate topics against audience relevance, utility, and anti-repetition memory.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CONTENT_PILLARS = [
    "AI Tool Breakdown",
    "Prompting & Workflow",
    "Marketing Psychology",
    "Tech Industry Explainer",
    "Career & Skills",
    "Myth-Bust / Contrarian"
]

class TopicScorer:
    def __init__(self, memory_file: Path | None = None):
        self.memory_file = memory_file or (Path(__file__).parent.parent.parent / "data" / "content-memory.json")

    def load_memory(self) -> dict:
        if self.memory_file.exists():
            try:
                return json.loads(self.memory_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"recent_posts": [], "banned_topics": []}

    def score_candidate(self, candidate: dict, memory: dict) -> float:
        """
        Calculates normalized score (0-100) based on criteria in Section 7.2 of the blueprint.
        """
        topic = candidate.get("topic", "").lower()
        
        # Check against anti-repetition memory
        for past in memory.get("recent_posts", []):
            if past.get("topic", "").lower() in topic or topic in past.get("topic", "").lower():
                return 0.0  # Automatic duplicate penalty

        for banned in memory.get("banned_topics", []):
            if banned.lower() in topic:
                return 0.0

        # Pillar rotation & diversity logic
        recent_pillars = [p.get("pillar") for p in memory.get("recent_posts", [])[:5] if p.get("pillar")]
        pillar = candidate.get("pillar", "")
        diversity_bonus = 0.0
        if recent_pillars:
            if pillar not in recent_pillars[:3]:
                diversity_bonus += 15.0  # Encourage rotation to fresh pillars
            if recent_pillars and pillar == recent_pillars[0]:
                diversity_bonus -= 10.0  # Avoid back-to-back same pillar

        # Scoring factors
        evidence = candidate.get("evidence_strength", 0.8) * 20
        novelty = candidate.get("novelty_score", 0.85) * 20
        utility = candidate.get("practicality_score", 0.9) * 25
        save_share = candidate.get("save_share_score", 0.85) * 25
        saturation_penalty = candidate.get("saturation_risk", 0.2) * 10

        total_score = evidence + novelty + utility + save_share + diversity_bonus - saturation_penalty
        return round(max(0.0, min(100.0, total_score)), 1)

    def select_best_topic(self, candidates: list[dict]) -> dict:
        """Selects highest scoring candidate and alternate backup."""
        memory = self.load_memory()
        scored = []
        for cand in candidates:
            score = self.score_candidate(cand, memory)
            cand["calculated_score"] = score
            scored.append(cand)

        scored.sort(key=lambda x: x.get("calculated_score", 0), reverse=True)
        if not scored:
            raise ValueError("No candidate topics available.")

        winner = scored[0]
        backup = scored[1] if len(scored) > 1 else scored[0]

        return {
            "winner": winner,
            "backup": backup,
            "reason": f"Top score ({winner.get('calculated_score')}) with high utility and zero overlap with recent memory."
        }

scorer = TopicScorer()
