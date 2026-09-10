"""
Automated Copywriting & Script Engine for Autogram.
Generates:
1. Carousel Narrative Scripts (Slide-by-slide copy with layout roles)
2. High-Converting Instagram Captions (Hook + Value Bullets + Algorithm CTAs + Hashtags)
3. 30–45 Second Talking-Head Reels / Shorts / TikTok Video Scripts
"""

import json
import logging
from typing import Dict, Any, List
from src.config import settings
from src.content.generator import generator

logger = logging.getLogger(__name__)

class ScriptWriter:
    def __init__(self):
        self.generator = generator

    def generate_caption(self, carousel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds an algorithm-optimized Instagram caption from carousel content.
        Uses the proven structure:
        1. Scroll-Stopping Hook (0.5s attention grab)
        2. Context / Tension (Why this matters now)
        3. 3 Practical Bullets (High save signal)
        4. CTA (Save + Share + Discussion question)
        5. 15 Categorized Hashtags
        """
        slides = carousel.get("slides", [])
        hook_slide = slides[0] if slides else {}
        topic = carousel.get("topic", "")
        pillar = carousel.get("pillar", "AI & Technology")

        hook_text = hook_slide.get("headline", topic)
        body_summary = hook_slide.get("body", "")

        # Extract proof points and takeaways
        takeaways = []
        for s in slides[1:5]:
            headline = s.get("headline", "")
            if headline and headline not in takeaways:
                takeaways.append(headline)

        bullets_str = "\n".join([f"• {t}" for t in takeaways[:3]])

        cta_question = f"Are you already applying this in your workflow, or still running the manual approach?"

        from pathlib import Path
        brand = {}
        brand_path = Path(__file__).parent.parent.parent / "data" / "brand.json"
        if brand_path.exists():
            try:
                brand = json.loads(brand_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        handle = brand.get("handle", "@signhify.studio")
        sign_off = brand.get("sign_off", "My name is Piyush. Stop posting. Start shipping.")
        secondary_links = brand.get("secondary_links", "")

        trigger_word = carousel.get("trigger_word") or (slides[-1].get("trigger_word") if slides else "DOCUMENT") or "DOCUMENT"

        caption_lines = [
            hook_text,
            "",
            body_summary,
            "",
            "Key architecture inside this breakdown:",
            bullets_str,
            "",
            "👉 Swipe through all slides to see the exact implementation diagrams.",
            "",
            f'⚡ Want the full blueprint & runnable repo? Comment "{trigger_word}" below and I\'ll send it straight to your DMs.',
            "",
            "📌 Save this post before your next architecture sprint.",
            f"🚀 Follow {handle} for battle-tested AI automation & systems design.",
            "",
            f"— {sign_off}"
        ]
        if secondary_links:
            caption_lines.append(secondary_links)
        caption_lines.extend(["", f"💬 {cta_question}"])
        caption_text = "\n".join(caption_lines)

        # Build dynamic 3-tier viral hashtags (Macro Explore + Intent + Community + Topic)
        try:
            from src.growth.viral_engine import viral_engine
            selected_tags = viral_engine.build_viral_hashtags(pillar, topic=topic)
            # Ensure mandatory core tags for consistency & test suite
            for req in ["#AIEngineering", "#AutogramAI", "#AIAutomation", "#AgenticAI"]:
                if req not in selected_tags:
                    selected_tags.append(req)
            first_comment = viral_engine.generate_first_comment(carousel)
        except Exception:
            selected_tags = ["#AIAutomation", "#AgenticAI", "#AIEngineering", "#AutogramAI", "#BuildInPublic", "#SoloBuilder", "#SignhifyStudio"]
            first_comment = f"📌 Follow {handle} for daily AI systems architecture breakdowns.\n\n⚡ Comment \"{trigger_word}\" for the free runnable blueprint!"

        hashtags_str = " ".join(selected_tags)
        full_caption = f"{caption_text}\n\n.\n.\n{hashtags_str}"

        return {
            "caption": full_caption,
            "body": caption_text,
            "hook": hook_text,
            "hashtags": selected_tags,
            "char_count": len(full_caption),
            "first_comment": first_comment
        }

    def generate_caption_for_topic(self, topic: str, pillar: str = "AI Tool Breakdown", custom_body: str = "") -> Dict[str, Any]:
        """
        On-demand caption and viral hashtag synthesis for any topic or pillar.
        """
        try:
            from src.growth.viral_engine import viral_engine
            default_meta = viral_engine.generate_default_caption(topic=topic, pillar=pillar)
            if custom_body:
                tags = default_meta["hashtags"]
                full_caption = viral_engine.format_caption_with_hashtags(custom_body, tags)
                return {
                    "caption": full_caption,
                    "body": custom_body,
                    "hashtags": tags,
                    "hook": topic,
                    "first_comment": f"📌 Follow @signhify.studio for daily AI systems architecture breakdowns.\n\n⚡ Comment 'BLUEPRINT' for the free runnable setup!"
                }
            return {
                "caption": default_meta["caption"],
                "body": default_meta["body"],
                "hashtags": default_meta["hashtags"],
                "hook": topic,
                "first_comment": f"📌 Follow @signhify.studio for daily AI systems architecture breakdowns.\n\n⚡ Comment 'BLUEPRINT' for the free runnable setup!"
            }
        except Exception as e:
            logger.error(f"Error in generate_caption_for_topic: {e}")
            tags = ["#AIAutomation", "#AgenticAI", "#AIEngineering", "#AutogramAI", "#SignhifyStudio"]
            fallback_cap = f"⚡ {topic}\n\nArchitecture breakdown and implementation details.\n\n👉 Swipe through all slides.\n\n.\n.\n{' '.join(tags)}"
            return {
                "caption": fallback_cap,
                "body": topic,
                "hashtags": tags,
                "hook": topic,
                "first_comment": "📌 Drop a comment below for the full architecture breakdown!"
            }

    def generate_first_comment(self, carousel: Dict[str, Any]) -> str:
        """Helper to generate conversational first comment for the carousel."""
        try:
            from src.growth.viral_engine import viral_engine
            return viral_engine.generate_first_comment(carousel)
        except Exception:
            trigger = carousel.get("trigger_word", "SYSTEM")
            return f"📌 Drop '{trigger}' below to get the full architecture sent straight to your DMs!"

    def generate_reels_script(self, carousel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts the carousel's core insight into a high-retention 30–45s video script
        for Instagram Reels, YouTube Shorts, or TikTok.
        """
        slides = carousel.get("slides", [])
        hook_slide = slides[0] if slides else {}
        second_slide = slides[1] if len(slides) > 1 else {}
        core_slide = slides[3] if len(slides) > 3 else {}
        takeaway_slide = slides[-2] if len(slides) > 2 else {}

        topic = carousel.get("topic", "")

        script = {
            "title": f"Reel: {topic}",
            "target_duration": "35-45 seconds",
            "segments": [
                {
                    "time": "0:00 - 0:03",
                    "label": "Hook (Pattern Interrupt)",
                    "visual": "Direct-to-camera, punch in. Text overlay on top third: '" + hook_slide.get("headline", topic) + "'",
                    "spoken": f"Stop doing this with your AI prompts. {hook_slide.get('headline', topic)}."
                },
                {
                    "time": "0:03 - 0:12",
                    "label": "The Problem / Root Cause",
                    "visual": "Screen recording showing code editor or architecture diagram. Fast cuts.",
                    "spoken": f"{second_slide.get('body', 'Most teams make the mistake of running everything inside a single context window.')}"
                },
                {
                    "time": "0:12 - 0:28",
                    "label": "The Shift / Architecture",
                    "visual": "Point to 3-step diagram animation on screen.",
                    "spoken": f"Here's the mechanism that actually scales: {core_slide.get('body', 'Separate your state ingestion from your validation gate.')}"
                },
                {
                    "time": "0:28 - 0:38",
                    "label": "Actionable Rule",
                    "visual": "Hold up fingers 1, 2, 3. Text card with green checkmark.",
                    "spoken": f"Remember: {takeaway_slide.get('headline', 'Architecture beats raw model parameter size every single time.')}"
                },
                {
                    "time": "0:38 - 0:42",
                    "label": "Call To Action",
                    "visual": "Point down to profile handle / carousel feed post.",
                    "spoken": "I broke down the exact blueprints in today's carousel on my feed. Check it out and save it for later."
                }
            ],
            "b_roll_suggestions": [
                "B-roll of VS Code terminal running `python orchestrator.py`",
                "Close-up of Playwright Chromium rendering 1080x1350 slides",
                "Clean technical graph or system diagram"
            ]
        }

        # Formatted readable script text
        formatted_lines = [
            f"# VIDEO SCRIPT: {topic.upper()}",
            f"Target Length: {script['target_duration']}\n",
            "---"
        ]
        for seg in script["segments"]:
            formatted_lines.append(f"\n[{seg['time']}] {seg['label'].upper()}")
            formatted_lines.append(f"VISUAL: {seg['visual']}")
            formatted_lines.append(f"AUDIO: \"{seg['spoken']}\"")

        formatted_lines.append("\n---\nB-ROLL NOTES:")
        for b in script["b_roll_suggestions"]:
            formatted_lines.append(f"- {b}")

        script["formatted_text"] = "\n".join(formatted_lines)
        return script

script_writer = ScriptWriter()
