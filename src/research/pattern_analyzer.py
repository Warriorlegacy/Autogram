"""
src/research/pattern_analyzer.py - Competitor Pattern & Viral Framework Extractor
Implements "Steal the pattern, not the post" - analyzes top creators, competitor URLs,
and topics to extract viral hooks, time audits, content calendars, and conversion CTAs.
"""

import os
import json
import logging
from typing import Optional
from openai import OpenAI

from src.config import settings

logger = logging.getLogger(__name__)

DEFAULT_COMPETITOR_PATTERNS = {
    "niche": "AI Automation & Autonomous Systems",
    "top_hooks": [
        "Be everywhere. Every platform. Without touching it.",
        "The Hormozi rule: post reliably, crank the volume.",
        "Why manual content creation is killing your engineering velocity."
    ],
    "receipt_audit": {
        "title": "MANUAL OMNIPRESENCE · PER MONTH",
        "items": [
            {"task": "RESEARCH WHAT'S WORKING", "hours": "8 HRS"},
            {"task": "WRITE SCRIPTS + CAPTIONS", "hours": "10 HRS"},
            {"task": "DESIGN CAROUSELS", "hours": "12 HRS"},
            {"task": "RECORD + EDIT VIDEO", "hours": "12 HRS"},
            {"task": "RESIZE PER PLATFORM", "hours": "5 HRS"},
            {"task": "SCHEDULE + POST × 13", "hours": "3 HRS"}
        ],
        "total_hours": "50 HRS",
        "annotation": "this is why most people quit by month two."
    },
    "script_framework": {
        "step_1": "HOOK THEM FAST",
        "step_2": "OFFER ONE IDEA",
        "step_3": "BUILD THE SYSTEM",
        "step_4": "REMOVE FRICTION",
        "step_5": "DELIVER RESULTS",
        "step_6": "SCALE RELENTLESSLY"
    },
    "conversion_trigger": {
        "prefix": "comment",
        "keyword": "AUTO",
        "subtext": "Get the Hormozi-style autopilot on your account.",
        "button": "RUN IT ON YOUR ACCOUNT →"
    }
}

class PatternAnalyzer:
    """Extracts viral structural frameworks from topics and competitor signals."""

    def __init__(self):
        self.api_key = (
            getattr(settings, "openrouter_api_key", None)
            or os.environ.get("OPENROUTER_API_KEY")
            or getattr(settings, "groq_api_key", None)
            or os.environ.get("GROQ_API_KEY")
        )

    def extract_patterns(self, topic: str, competitor_urls: Optional[list[str]] = None) -> dict:
        """
        Synthesizes high-performing hooks, time/cost audits, and viral frameworks
        for the given topic and optional competitor links.
        """
        if not self.api_key:
            logger.info("No LLM API key for pattern analyzer; returning production defaults.")
            return DEFAULT_COMPETITOR_PATTERNS

        system_prompt = (
            "You are an elite viral content architect specializing in high-status authority carousels "
            "(Alex Hormozi style, Makerzz style). "
            "Your job is to reverse-engineer viral patterns, NOT copy exact posts. "
            "Output strictly valid JSON with keys: "
            "'top_hooks' (list of 3 punchy hooks), "
            "'receipt_audit' (object with 'title', 'items' [array of {task, hours}], 'total_hours', 'annotation'), "
            "'script_framework' (object with step_1 to step_6 names), and "
            "'conversion_trigger' (object with 'prefix', 'keyword', 'subtext', 'button')."
        )

        user_content = f"Topic: {topic}\nCompetitors: {', '.join(competitor_urls or ['@alexhormozi', '@signhify.studio'])}"

        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1" if "openrouter" in getattr(settings, "llm_provider", "auto") else "https://api.groq.com/openai/v1",
                api_key=self.api_key,
            )
            model = "z-ai/glm-5.3-flash:free" if "openrouter" in getattr(settings, "llm_provider", "auto") else "llama-3.3-70b-versatile"

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                timeout=30
            )
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.warning(f"Pattern analysis fallback triggered: {e}")
            return DEFAULT_COMPETITOR_PATTERNS
