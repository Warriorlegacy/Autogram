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

        cta_question = f"Are you already applying this in your {pillar.lower()} workflow, or still running the manual approach?"

        caption_text = f"""{hook_text}

{body_summary}

Here is what changes when you move to a compound architecture:
{bullets_str}

👉 Swipe through the 8 slides for the full step-by-step breakdown.

📌 Save this post so your team has the exact reference when deploying.
💬 {cta_question}"""

        # Targeted, non-spammy technical hashtags
        niche_tags = {
            "AI Tool Breakdown": ["#AIEngineering", "#MachineLearning", "#LLMArchitecture", "#SystemDesign", "#TechStack"],
            "Prompting & Workflow": ["#PromptEngineering", "#WorkflowAutomation", "#DevProductivity", "#AIWorkflow", "#SoftwareDevelopment"],
            "Marketing Psychology": ["#B2BMarketing", "#GrowthStrategy", "#MarketingPsychology", "#SaaSGrowth", "#TechFounders"],
            "Tech Industry Explainer": ["#TechTrends", "#SoftwareEngineering", "#CloudInfrastructure", "#DevCommunity", "#EngineeringManagement"],
            "Career & Skills": ["#TechCareers", "#EngineeringLeadership", "#FutureOfWork", "#DeveloperLife", "#SkillBuilding"],
            "Myth-Bust / Contrarian": ["#ContrarianThinking", "#TechDebate", "#SoftwareDesign", "#Startups", "#TechLeadership"]
        }

        base_tags = ["#AutogramAI", "#TechInnovation", "#BuildInPublic"]
        selected_tags = niche_tags.get(pillar, ["#ArtificialIntelligence", "#TechNews", "#SoftwareArchitecture"]) + base_tags
        hashtags_str = " ".join(selected_tags)

        full_caption = f"{caption_text}\n\n.\n.\n{hashtags_str}"

        return {
            "caption": full_caption,
            "hook": hook_text,
            "hashtags": selected_tags,
            "char_count": len(full_caption)
        }

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
