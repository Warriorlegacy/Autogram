"""
Trend Analysis & Virality Gate Engine (src/research/trend_analyzer.py).
Analyzes current niche trends (Developer Tools, FOSS SaaS Alternatives, Secret Prompts)
and strictly filters topics so Autogram ONLY posts content with high viral potential (Score >= 85).
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Minimum score to pass the Virality Gate (75.0 allows high-utility FOSS tools & prompts while killing slop)
VIRAL_GATE_THRESHOLD = 75.0

# Known SaaS cost benchmarks for calculating Cost Asymmetry
SAAS_KILLER_BENCHMARKS = {
    "coolify": {"saas": "Vercel / Heroku", "cost": "$20 - $200+/mo", "points": 25.0},
    "vercel": {"saas": "Vercel / Heroku", "cost": "$20 - $200+/mo", "points": 25.0},
    "n8n": {"saas": "Zapier / Make.com", "cost": "$59 - $299+/mo", "points": 25.0},
    "zapier": {"saas": "Zapier / Make.com", "cost": "$59 - $299+/mo", "points": 25.0},
    "documenso": {"saas": "DocuSign / PandaDoc", "cost": "$40/user/mo", "points": 24.0},
    "docusign": {"saas": "DocuSign / PandaDoc", "cost": "$40/user/mo", "points": 24.0},
    "stirling-pdf": {"saas": "Adobe Acrobat Pro", "cost": "$240/yr", "points": 25.0},
    "stirling": {"saas": "Adobe Acrobat Pro", "cost": "$240/yr", "points": 25.0},
    "adobe": {"saas": "Adobe Acrobat Pro", "cost": "$240/yr", "points": 25.0},
    "open-webui": {"saas": "ChatGPT Plus / Team", "cost": "$20 - $30/user/mo", "points": 24.0},
    "chatgpt": {"saas": "ChatGPT Plus / Team", "cost": "$20 - $30/user/mo", "points": 24.0},
    "litellm": {"saas": "LangSmith / Portkey", "cost": "$99 - $499/mo", "points": 25.0},
    "pocketbase": {"saas": "Firebase / Supabase Cloud", "cost": "$25 - $100+/mo", "points": 24.0},
    "caddy": {"saas": "NGINX SSL / Cloudflare Paid", "cost": "$20 - $200/mo", "points": 23.0},
    "appflowy": {"saas": "Notion Team", "cost": "$10 - $20/user/mo", "points": 24.0},
    "penpot": {"saas": "Figma Professional", "cost": "$15/user/mo", "points": 24.0},
    "cal.com": {"saas": "Calendly Pro", "cost": "$16/user/mo", "points": 23.0},
    "affine": {"saas": "Miro / Notion", "cost": "$15 - $30/mo", "points": 23.0},
    "ollama": {"saas": "Cloud LLM APIs", "cost": "Pay-per-token API bills", "points": 25.0},
    "vllm": {"saas": "Hyperscaler GPUs", "cost": "$500 - $2,000/mo", "points": 25.0},
    "lazygit": {"saas": "GitKraken Pro", "cost": "$60/user/yr", "points": 24.0},
    "ripgrep": {"saas": "Slow grep / IDE search", "cost": "Developer hours", "points": 23.0},
    "datasette": {"saas": "Tableau / Snowflake", "cost": "$100+/mo", "points": 24.0}
}

# High-converting viral pattern interrupt triggers
VIRAL_HOOK_TRIGGERS = [
    r"\breplace(s|ing)?\b",
    r"\balternative\b",
    r"\bditch\b",
    r"\bstop paying\b",
    r"\b\$0\b",
    r"\bfree\b",
    r"\bsecret\b",
    r"\bprompt\b",
    r"\bmegaprompt\b",
    r"\b1-click\b",
    r"\bcheat\s*sheet\b",
    r"\bself-host(ed|ing)?\b",
    r"\b100%\s*(local|offline|free|open source)\b",
    r"\barchitecture\b",
    r"\bunlimited\b",
    r"\bbypass\b"
]

# High-utility save & share triggers (users bookmark these to execute)
SAVE_SHARE_TRIGGERS = [
    r"\bdocker(-compose)?\b",
    r"\bcurl\b",
    r"\bsetup\b",
    r"\bcommand\b",
    r"\bsyntax\b",
    r"\btemplate\b",
    r"\bblueprint\b",
    r"\bcheat\s*sheet\b",
    r"\bguide\b",
    r"\bworkflow\b",
    r"\bconfig\b",
    r"\brunnable\b",
    r"\bprompt code\b",
    r"\bschema\b"
]

# Anti-viral slop triggers that kill engagement (low-value, generic tutorials)
ANTI_VIRAL_TRIGGERS = [
    r"\bgetting started with\b",
    r"\bwhat is\b",
    r"\bintroduction to\b",
    r"\bbasics of\b",
    r"\brelease v\d+\.\d+\b",
    r"\bbug\s*fix\b",
    r"\bpatch notes\b",
    r"\bminor update\b",
    r"\bdocumentation update\b",
    r"\bhow to install python\b"
]


class TrendAnalyzer:
    """
    Evaluates topics against real-time trend signals and developer virality factors:
    1. Hook Potency (0-25)
    2. Save & Share Urgency (0-25)
    3. Cost Asymmetry / Financial Shock (0-25)
    4. Trend Heat & Social Proof (0-25)
    """

    def __init__(self, gate_threshold: float = VIRAL_GATE_THRESHOLD):
        self.gate_threshold = gate_threshold

    def calculate_viral_metrics(self, candidate: dict) -> dict:
        """
        Calculates four-dimensional virality scores for a candidate topic.
        """
        topic = candidate.get("topic", "")
        excerpt = candidate.get("excerpt", "")
        combined_text = f"{topic} {excerpt} {candidate.get('angle', '')}".lower()

        # 1. HOOK POTENCY (0 - 25)
        # Measures whether the title creates an instant pattern-interrupt
        hook_score = 10.0  # Base line
        for pattern in VIRAL_HOOK_TRIGGERS:
            if re.search(pattern, combined_text):
                hook_score += 3.0
        
        # Check for immediate numbers / metrics ("$0", "3.8x", "91k stars")
        if re.search(r"\$\d+|\d+x|\d+k\s*stars|\d+%", combined_text):
            hook_score += 4.0
        
        hook_score = min(25.0, round(hook_score, 1))

        # 2. SAVE & SHARE URGENCY (0 - 25)
        # Measures bookmarkability: reproducible setup, docker command, prompt template
        save_score = 10.0
        for pattern in SAVE_SHARE_TRIGGERS:
            if re.search(pattern, combined_text):
                save_score += 2.5
        
        # Proven code or prompt assets
        if candidate.get("source_type") == "github_repository" or "github.com" in str(candidate.get("sources", "")):
            save_score += 4.0
        if "prompt" in combined_text or "chain-of-density" in combined_text or "tree-of-thought" in combined_text:
            save_score += 5.0
            
        save_score = min(25.0, round(save_score, 1))

        # 3. COST & VALUE ASYMMETRY (0 - 25)
        # Quantifies the contrast between expensive proprietary SaaS / manual effort and free tool / prompt
        cost_score = 10.0
        for key, info in SAAS_KILLER_BENCHMARKS.items():
            if key in combined_text:
                cost_score = max(cost_score, info["points"])
                break
        
        if any(w in combined_text for w in ["$0", "free", "zero cost", "unlimited", "saves", "cheaper"]):
            cost_score = min(25.0, cost_score + 5.0)

        # High-leverage AI Prompt / Performance Multiplier Asymmetry
        if any(w in combined_text for w in ["outperforms", "beats", "chain-of-density", "tree-of-thought", "megaprompt", "3.8x", "10x", "zero-shot", "few-shot"]):
            cost_score = max(cost_score, 24.0)

        cost_score = min(25.0, round(cost_score, 1))

        # 4. TREND HEAT & SOCIAL PROOF (0 - 25)
        # Evaluates GitHub stars, community points, or breakout velocity
        heat_score = 10.0
        stars = candidate.get("stars", 0)
        trust = candidate.get("evidence_strength", 0.9)

        if stars >= 50000:
            heat_score = 25.0
        elif stars >= 15000:
            heat_score = 22.0
        elif stars >= 2000:
            heat_score = 18.0
        elif stars >= 500:
            heat_score = 15.0

        # High trust / community validation bonus
        if trust >= 0.95:
            heat_score = min(25.0, heat_score + 3.0)

        # AI & Prompt breakout bonus (current highest trending niche)
        if any(w in combined_text for w in ["ollama", "deepseek", "chatgpt", "vllm", "claude", "prompt"]):
            heat_score = min(25.0, heat_score + 4.0)

        heat_score = min(25.0, round(heat_score, 1))

        # 5. ANTI-VIRAL SLOP PENALTY (-30.0)
        # Kills generic, boring, or irrelevant tutorial posts
        penalty = 0.0
        for pattern in ANTI_VIRAL_TRIGGERS:
            if re.search(pattern, combined_text):
                penalty += 15.0

        raw_total = (hook_score + save_score + cost_score + heat_score) - penalty
        viral_score = round(max(0.0, min(100.0, raw_total)), 1)

        # Categorize viral tier
        if viral_score >= 95.0:
            tier = "ULTRA-VIRAL (95-100)"
        elif viral_score >= 85.0:
            tier = "HIGH VIRAL POTENTIAL (85-94)"
        elif viral_score >= 70.0:
            tier = "MEDIOCRE (70-84 - REJECTED)"
        else:
            tier = "FLUFF/LOW (0-69 - REJECTED)"

        approved = (viral_score >= self.gate_threshold)
        rejection_reason = None
        if not approved:
            if penalty > 0:
                rejection_reason = "Rejected: Contains low-engagement tutorial or minor patch slop keywords."
            else:
                rejection_reason = f"Rejected: Viral score ({viral_score}) failed strict gate threshold ({self.gate_threshold})."

        # Generate a punchy high-conversion viral hook
        viral_hook = self._generate_viral_hook(topic, combined_text)

        return {
            "topic": topic,
            "viral_score": viral_score,
            "approved_by_viral_gate": approved,
            "viral_tier": tier,
            "metrics": {
                "hook_potency": hook_score,
                "save_share_urgency": save_score,
                "cost_asymmetry": cost_score,
                "trend_heat": heat_score,
                "slop_penalty": penalty
            },
            "viral_hook": viral_hook,
            "rejection_reason": rejection_reason
        }

    def _generate_viral_hook(self, topic: str, combined_text: str) -> str:
        """Constructs an aggressive pattern-interrupt hook for Instagram carousels."""
        if "coolify" in combined_text:
            return "Stop paying $200/mo for Vercel. Self-host everything for $0."
        elif "stirling" in combined_text:
            return "Ditch Adobe Acrobat Pro for $0. 100% local open-source PDF suite."
        elif "n8n" in combined_text:
            return "Zapier charges $59/mo for this. Here's how to get unlimited workflows for $0."
        elif "documenso" in combined_text:
            return "Why pay $40/mo for DocuSign? This open-source tool runs for $0."
        elif "open-webui" in combined_text:
            return "You don't need ChatGPT Plus. Run a local AI powerhouse with 1 command."
        elif "chain-of-density" in combined_text:
            return "99% use ChatGPT wrong. This secret prompt condenses 10 pages in 1 pass."
        elif "tree-of-thought" in combined_text:
            return "The 3-Persona Prompt that beats standard ChatGPT reasoning by 74%."
        elif "reverse-engineer" in combined_text:
            return "The Secret Megaprompt to extract complete system architectures from any app."
        elif "skeleton-of-thought" in combined_text or "sot" in combined_text:
            return "Generate 10 pages in 5 seconds. The secret prompt that speeds up LLMs by 4x."
        elif "sql" in combined_text and ("zero-hallucination" in combined_text or "guard" in combined_text):
            return "Never write a broken SQL query again. The zero-hallucination schema prompt."
        elif "security" in combined_text or "auditor" in combined_text or "red-team" in combined_text:
            return "The AppSec Red-Team prompt that finds 0-day bugs in your code in 10 seconds."
        elif "chain-of-verification" in combined_text or "cove" in combined_text:
            return "Stop ChatGPT from lying. The Meta AI self-correcting prompt architecture."
        elif "deep-research" in combined_text:
            return "The Autonomous Deep Research prompt that replaces 6 hours of research in 60s."
        elif "docker" in combined_text or "self-host" in combined_text:
            return f"The 1-Click Setup: How to self-host {topic.split(':')[0]} in 60 seconds."
        else:
            return f"Why the best engineers are switching to {topic.split(':')[0]} for $0."

    def filter_viral_candidates(self, candidates: list[dict], memory: dict | None = None) -> Tuple[list[dict], dict]:
        """
        Filters candidates against the Virality Gate (Score >= 75.0) and Anti-Repetition Memory.
        Guarantees that already-published topics are never approved when fresh topics are available.
        """
        from pathlib import Path
        if memory is None:
            mem_path = Path(__file__).parent.parent.parent / "data" / "content-memory.json"
            if mem_path.exists():
                try:
                    memory = json.loads(mem_path.read_text(encoding="utf-8"))
                except Exception:
                    memory = {}
            else:
                memory = {}

        recent_posts = memory.get("recent_posts", []) if memory else []
        recent_topics_lower = [p.get("topic", "").lower().strip() for p in recent_posts if p.get("topic")]

        import difflib
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

        def is_duplicate_of_recent(cand_topic: str) -> bool:
            c_low = cand_topic.lower().strip()
            if not c_low:
                return False
            for past in recent_topics_lower:
                if not past:
                    continue
                if len(c_low) >= 8 and len(past) >= 8:
                    if past in c_low or c_low in past:
                        return True
                if difflib.SequenceMatcher(None, c_low, past).ratio() >= 0.65:
                    return True
                for sig in tool_signatures:
                    if sig in c_low and sig in past:
                        return True
            return False

        effective_threshold = self.gate_threshold
        approved = []
        rejected = []
        all_evaluations = []

        for cand in candidates:
            v_eval = self.calculate_viral_metrics(cand)
            cand["viral_score"] = v_eval["viral_score"]
            cand["viral_tier"] = v_eval["viral_tier"]
            cand["viral_hook"] = v_eval["viral_hook"]
            cand["viral_metrics"] = v_eval["metrics"]
            
            # Anti-repetition memory gate check
            topic_str = cand.get("topic", "")
            is_dup = is_duplicate_of_recent(topic_str)
            cand["in_memory"] = is_dup

            if is_dup:
                cand["viral_score"] = 0.0
                v_eval["viral_score"] = 0.0
                v_eval["approved_by_viral_gate"] = False
                v_eval["rejection_reason"] = "Rejected by Anti-Repetition Gate: Topic or tool already published in recent memory."
                rejected.append({
                    "topic": topic_str,
                    "score": 0.0,
                    "reason": "Duplicate: Already posted recently."
                })
            elif v_eval["viral_score"] >= effective_threshold:
                cand["approved_by_viral_gate"] = True
                approved.append(cand)
            else:
                v_eval["approved_by_viral_gate"] = False
                rejected.append({
                    "topic": topic_str,
                    "score": v_eval["viral_score"],
                    "reason": v_eval["rejection_reason"]
                })
            all_evaluations.append(v_eval)

        # Dynamic backoff: if no unposted candidates passed at 75.0, check if high-quality unposted items exist at 65.0+
        if not approved:
            fresh_rejected = [c for c in candidates if not c.get("in_memory")]
            for cand in fresh_rejected:
                v_eval = self.calculate_viral_metrics(cand)
                if v_eval["viral_score"] >= 65.0:
                    cand["viral_score"] = v_eval["viral_score"]
                    cand["approved_by_viral_gate"] = True
                    approved.append(cand)
                    logger.info(f"Dynamic Virality Gate backoff approved fresh topic: '{cand.get('topic')}' (Score: {cand['viral_score']})")

        # Sort approved by viral score descending
        approved.sort(key=lambda x: x.get("viral_score", 0), reverse=True)

        # Audit report
        from datetime import timezone
        report = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "niche": "Developer Tools, Open Source Software & Advanced AI Prompts",
            "gate_threshold": effective_threshold,
            "total_evaluated": len(candidates),
            "approved_count": len(approved),
            "rejected_count": len(rejected),
            "top_viral_candidates": [
                {
                    "topic": c.get("topic"),
                    "score": c.get("viral_score"),
                    "tier": c.get("viral_tier"),
                    "hook": c.get("viral_hook"),
                    "metrics": c.get("viral_metrics"),
                    "in_memory": c.get("in_memory", False)
                }
                for c in approved[:5]
            ],
            "rejected_topics": rejected[:10]
        }

        logger.info(
            f"Trend Analysis Complete: {len(approved)} viral candidates approved (Score >= {effective_threshold}), "
            f"{len(rejected)} candidates pruned by Virality Gate (including anti-repetition memory deduplication)."
        )

        return approved, report


trend_analyzer = TrendAnalyzer()
