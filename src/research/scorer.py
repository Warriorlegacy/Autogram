"""
Topic scoring & candidate selection module (Layer B).
Scores candidate topics against audience relevance, utility, and anti-repetition memory.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CONTENT_PILLARS = [
    "FOSS SaaS Alternatives",
    "Trending GitHub Spotlight",
    "Local AI & Edge Compute",
    "Developer Power Tools & CLI",
    "Self-Hosted Architecture",
    "Open Source Economics & Contrarian"
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
        Calculates normalized score (0-100) based on relevance, utility, and FOSS signals.
        """
        topic = candidate.get("topic", "").lower()
        
        # Check against anti-repetition memory with precise duplicate detection
        import difflib
        c_low = topic.strip()
        tool_signatures = [
            "open-webui", "openwebui", "coolify", "stirling", "n8n", "documenso", "ollama",
            "vllm", "affine", "supabase", "pocketbase", "appwrite", "penpot", "plane",
            "posthog", "umami", "ghost", "strapi", "directus", "typesense", "meilisearch",
            "searxng", "authentik", "keycloak", "vaultwarden", "rustdesk", "immich",
            "paperless", "hoppscotch", "nocodb", "baserow", "twenty", "cal.com",
            "uptime-kuma", "grafana", "portainer", "datasette",
            "chain-of-density", "tree-of-thought", "skeleton-of-thought",
            "chain-of-verification", "megaprompt"
        ]
        for past in memory.get("recent_posts", []):
            past_topic = past.get("topic", "").lower().strip()
            if not past_topic:
                continue
            # Substring containment
            if len(c_low) >= 8 and len(past_topic) >= 8:
                if c_low in past_topic or past_topic in c_low:
                    return 0.0
            # High text similarity
            if difflib.SequenceMatcher(None, c_low, past_topic).ratio() >= 0.65:
                return 0.0
            # Specific tool or prompt signature match
            for sig in tool_signatures:
                if sig in c_low and sig in past_topic:
                    return 0.0

        for banned in memory.get("banned_topics", []):
            if banned.lower() in topic:
                return 0.0

        # Pillar rotation & diversity logic
        recent_pillars = [p.get("pillar") for p in memory.get("recent_posts", [])[:5] if p.get("pillar")]
        pillar = candidate.get("pillar", "")
        diversity_bonus = 0.0
        if recent_pillars:
            if pillar not in recent_pillars[:3]:
                diversity_bonus += 15.0  # Strongly encourage rotation to fresh pillars
            elif len(recent_pillars) >= 2 and all(p == pillar for p in recent_pillars[:2]):
                diversity_bonus -= 10.0  # Avoid excessive consecutive posts of same pillar

        # Scoring factors
        evidence = candidate.get("evidence_strength", 0.8) * 20
        novelty = candidate.get("novelty_score", 0.85) * 20
        utility = candidate.get("practicality_score", 0.9) * 25
        save_share = candidate.get("save_share_score", 0.85) * 25
        saturation_penalty = candidate.get("saturation_risk", 0.2) * 10

        # FOSS & GitHub high-leverage signals
        foss_bonus = 0.0
        sources_str = " ".join(candidate.get("sources", [])).lower()
        if "github.com" in sources_str or candidate.get("source_type") == "github_repository":
            foss_bonus += 10.0  # Proven repo with code
        if candidate.get("stars", 0) > 500 or "star" in topic:
            foss_bonus += 5.0  # Star validation & developer adoption
        if any(k in topic for k in ["alternative", "self-hosted", "docker", "local", "foss", "open source", "zero-cost", "replace"]):
            foss_bonus += 10.0  # High save/share utility keyword

        total_score = evidence + novelty + utility + save_share + diversity_bonus + foss_bonus - saturation_penalty
        return round(max(0.0, min(100.0, total_score)), 1)

    def select_best_topic(self, candidates: list[dict], memory: dict | None = None) -> dict:
        """Selects highest scoring candidate and alternate backup, strictly enforcing zero repetition."""
        if memory is None:
            memory = self.load_memory()
        scored = []
        for cand in candidates:
            score = self.score_candidate(cand, memory)
            cand["calculated_score"] = score
            scored.append(cand)

        if not scored:
            raise ValueError(
                "select_best_topic received zero candidates. Upstream acquisition "
                "and gating must guarantee at least one candidate."
            )

        # Separate fresh unposted candidates from duplicate items
        fresh = [c for c in scored if c.get("calculated_score", 0) > 0.0]

        if fresh:
            fresh.sort(key=lambda x: x.get("calculated_score", 0), reverse=True)
            winner = fresh[0]
            backup = fresh[1] if len(fresh) > 1 else fresh[0]
            reason = f"Top score ({winner.get('calculated_score')}) with high utility and zero overlap with recent memory."
        else:
            logger.warning("All candidate topics matched recent memory! Forcing selection of candidate with least recent footprint.")
            scored.sort(key=lambda x: x.get("calculated_score", 0), reverse=True)
            winner = scored[0]
            backup = scored[1] if len(scored) > 1 else scored[0]
            reason = "Forced fallback to available candidate."

        return {
            "winner": winner,
            "backup": backup,
            "reason": reason
        }

scorer = TopicScorer()
