"""
Analytics and Self-Optimization (Layer E).
Calculates rolling performance scores and extracts winning patterns to feed future topic selection.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
MEMORY_FILE = Path(__file__).parent.parent.parent / "data" / "content-memory.json"

class AnalyticsOptimizer:
    def __init__(self, memory_file: Path = MEMORY_FILE):
        self.memory_file = memory_file

    def calculate_content_score(self, metrics: dict) -> float:
        """
        Calculates normalized Content Score (Section 15.2 of blueprint):
        0.30 * Save Rate + 0.30 * Share Rate + 0.20 * Follow Conversion + 0.10 * Comment Rate + 0.10 * Reach Efficiency
        """
        reach = max(metrics.get("reach", 1), 1)
        saves = metrics.get("saves", 0)
        shares = metrics.get("shares", 0)
        follows = metrics.get("follows", 0)
        comments = metrics.get("comments", 0)

        save_rate = min(1.0, (saves / reach) * 10)
        share_rate = min(1.0, (shares / reach) * 15)
        follow_rate = min(1.0, (follows / reach) * 20)
        comment_rate = min(1.0, (comments / reach) * 10)
        reach_efficiency = min(1.0, reach / 5000.0)

        score = (
            0.30 * save_rate +
            0.30 * share_rate +
            0.20 * follow_rate +
            0.10 * comment_rate +
            0.10 * reach_efficiency
        ) * 100.0

        return round(score, 1)

    def update_memory_with_post(self, post_info: dict, score: float = 85.0):
        """Appends published post to content-memory.json for anti-repetition."""
        if not self.memory_file.exists():
            return

        try:
            memory = json.loads(self.memory_file.read_text(encoding="utf-8"))
            recent = memory.get("recent_posts", [])
            recent.insert(0, {
                "date": post_info.get("publication_date"),
                "pillar": post_info.get("pillar"),
                "topic": post_info.get("topic"),
                "hook": post_info.get("hook"),
                "score": score
            })
            memory["recent_posts"] = recent[:60]  # Keep rolling 60 days
            self.memory_file.write_text(json.dumps(memory, indent=2), encoding="utf-8")
            logger.info("Updated content-memory.json with published post.")
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")

optimizer = AnalyticsOptimizer()
