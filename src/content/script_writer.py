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
        sign_off = brand.get("sign_off", "My name is Piyush Raj Singh. Stop posting. Start shipping.")
        secondary_links = brand.get("secondary_links", "")

        trigger_word = carousel.get("trigger_word") or (slides[-1].get("trigger_word") if slides else "FOSS") or "FOSS"

        caption_lines = [
            hook_text,
            "",
            body_summary,
            "",
            "Key architecture inside this breakdown:",
            bullets_str,
            "",
            "👉 Swipe through all slides to inspect the complete architecture & 1-line setup.",
            "",
            f'⚡ Want the full GitHub repo + docker-compose file? Comment "{trigger_word}" below and I\'ll send it straight to your DMs.',
            "",
            "📌 Save this post before your next self-hosting sprint.",
            f"🚀 Follow signhify.studio for more.",
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
            for req in ["#OpenSource", "#SelfHosted", "#DevTools", "#AIEngineering", "#AutogramAI"]:
                if req not in selected_tags:
                    selected_tags.append(req)
            first_comment = viral_engine.generate_first_comment(carousel)
        except Exception:
            selected_tags = ["#OpenSource", "#SelfHosted", "#DevTools", "#AIEngineering", "#AutogramAI", "#SignhifyStudio"]
            first_comment = f"📌 Follow {handle} for daily open source tools & architecture breakdowns.\n\n⚡ Comment \"{trigger_word}\" for the free runnable repo!"

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

    def generate_caption_for_topic(self, topic: str, pillar: str = "FOSS SaaS Alternatives", custom_body: str = "") -> Dict[str, Any]:
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
                    "first_comment": f"📌 Follow @signhify.studio for daily open source architecture breakdowns.\n\n⚡ Comment 'FOSS' for the free runnable setup!"
                }
            return {
                "caption": default_meta["caption"],
                "body": default_meta["body"],
                "hashtags": default_meta["hashtags"],
                "hook": topic,
                "first_comment": f"📌 Follow @signhify.studio for daily open source architecture breakdowns.\n\n⚡ Comment 'FOSS' for the free runnable setup!"
            }
        except Exception as e:
            logger.error(f"Error in generate_caption_for_topic: {e}")
            tags = ["#OpenSource", "#SelfHosted", "#DevTools", "#AIEngineering", "#AutogramAI", "#SignhifyStudio"]
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
            trigger = carousel.get("trigger_word", "FOSS")
            return f"📌 Drop '{trigger}' below to get the full GitHub repo + docker-compose file sent straight to your DMs!"

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
                    "spoken": f"Stop paying monthly SaaS bills for this. {hook_slide.get('headline', topic)}."
                },
                {
                    "time": "0:03 - 0:12",
                    "label": "The Problem / SaaS Trap",
                    "visual": "Screen recording showing expensive subscription pricing page or cloud bills. Fast cuts.",
                    "spoken": f"{second_slide.get('body', 'Most teams bleed thousands every month on SaaS tools that lock up your data and hike prices every year.')}"
                },
                {
                    "time": "0:12 - 0:28",
                    "label": "The Open Source Solution",
                    "visual": "Terminal / browser showing the GitHub repository with star count, clean UI, or docker run command.",
                    "spoken": f"Here is the open source alternative: {core_slide.get('body', 'It is 100% self-hosted, MIT-licensed, and runs with a single command.')}"
                },
                {
                    "time": "0:28 - 0:38",
                    "label": "Architectural Rule",
                    "visual": "Architecture diagram or docker compose snippet. Text card with green checkmark.",
                    "spoken": f"Remember: {takeaway_slide.get('headline', 'Data ownership and local infrastructure beat proprietary cloud lock-in every single time.')}"
                },
                {
                    "time": "0:38 - 0:42",
                    "label": "Call To Action",
                    "visual": "Point down to profile handle / carousel feed post.",
                    "spoken": "I put the full docker compose file and setup guide in today's carousel. Comment 'FOSS' below and I'll DM it to you. Follow signhify.studio for more."
                }
            ],
            "b_roll_suggestions": [
                "B-roll of terminal running `docker compose up -d`",
                "Close-up of Playwright Chromium rendering 1080x1350 slides",
                "GitHub repository page highlighting stars and license"
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

    def generate_edit_plan(self, carousel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates production edit_plan.json (Makerzz Section 8 specification)
        separating visual direction, cuts, transitions, captions, and SFX from spoken script.
        """
        slides = carousel.get("slides", [])
        topic = carousel.get("topic", "")
        hook_slide = slides[0] if slides else {}
        second_slide = slides[1] if len(slides) > 1 else {}
        setup_slide = slides[3] if len(slides) > 3 else {}

        return {
            "format": "reels_edit_plan_v1",
            "topic": topic,
            "aspect_ratio": "9:16 (1080x1920)",
            "target_duration_seconds": 40,
            "style": "fast-cut-dev-aesthetic",
            "timeline": [
                {
                    "start": "00:00",
                    "end": "00:03",
                    "shot": "talking_head_tight",
                    "on_screen_text": hook_slide.get("headline", topic),
                    "text_style": "bold_yellow_caps_centered",
                    "transition": "hard_cut",
                    "sfx": "whoosh_impact",
                    "b_roll": None
                },
                {
                    "start": "00:03",
                    "end": "00:12",
                    "shot": "screen_recording",
                    "on_screen_text": "THE SAAS BILL PROBLEM",
                    "text_style": "minimal_red_badge",
                    "transition": "glitch_cut",
                    "sfx": "cash_register_drain",
                    "b_roll": "expensive_cloud_invoice_or_saas_pricing_table"
                },
                {
                    "start": "00:12",
                    "end": "00:25",
                    "shot": "screen_recording_code",
                    "on_screen_text": second_slide.get("headline", topic),
                    "text_style": "terminal_green_monospaced",
                    "transition": "smooth_slide_left",
                    "sfx": "mechanical_keyboard_clicks",
                    "b_roll": "github_repo_page_and_star_count"
                },
                {
                    "start": "00:25",
                    "end": "00:35",
                    "shot": "terminal_zoom_in",
                    "on_screen_text": setup_slide.get("proof_or_example", "docker compose up -d"),
                    "text_style": "code_block_highlighted",
                    "transition": "punch_zoom",
                    "sfx": "terminal_beep_success",
                    "b_roll": "docker_compose_command_executing"
                },
                {
                    "start": "00:35",
                    "end": "00:40",
                    "shot": "creator_outro",
                    "on_screen_text": "COMMENT 'FOSS' FOR THE BLUEPRINT",
                    "text_style": "cta_pulse_card",
                    "transition": "fade_to_black",
                    "sfx": "bell_ping",
                    "b_roll": "instagram_carousel_preview"
                }
            ],
            "audio": {
                "background_track": "cyber_synth_low_volume",
                "ducking": "reduce_track_18db_during_speech"
            },
            "color_grading": {
                "lut": "clean_high_contrast",
                "accent_color": "#FFC22B"
            }
        }

    def generate_x_thread(self, carousel: Dict[str, Any]) -> str:
        """
        Builds a high-impact, viral X (Twitter) thread breakdown (4-6 tweets) following Makerzz architecture.
        """
        slides = carousel.get("slides", [])
        topic = carousel.get("topic", "")
        hook_slide = slides[0] if slides else {}
        second_slide = slides[1] if len(slides) > 1 else {}
        setup_slide = slides[3] if len(slides) > 3 else {}
        matrix_slide = slides[4] if len(slides) > 4 else {}
        gotcha_slide = slides[5] if len(slides) > 5 else {}
        
        tweets = [
            # Tweet 1: Hook
            f"Stop paying expensive SaaS subscriptions for something you can run yourself.\n\n"
            f"{hook_slide.get('headline', topic)}.\n\n"
            f"Here is the 100% open source breakdown, architecture, and 1-line setup 🧵👇",

            # Tweet 2: The Tool & Specs
            f"1/ The Tool: {topic}\n\n"
            f"{second_slide.get('headline', 'Battle-tested open source engine')}\n\n"
            f"{second_slide.get('body', 'Zero vendor lock-in. Full data ownership. Self-hosted on your own hardware.')}\n\n"
            f"Proof: {second_slide.get('proof_or_example', 'Open source, MIT/AGPL licensed.')}",

            # Tweet 3: Setup Command
            f"2/ 1-Line Deployment 🚀\n\n"
            f"You can get this running in 60 seconds with Docker:\n\n"
            f"{setup_slide.get('proof_or_example', 'docker run -d -p 8080:8080 --name app app/app:latest')}\n\n"
            f"All your data stays in your local persistent volume. No cloud telemetry.",

            # Tweet 4: SaaS vs FOSS Comparison
            f"3/ SaaS vs Open Source Matrix ⚖️\n\n"
            f"{matrix_slide.get('headline', 'The Real Comparison')}\n"
            f"• Proprietary SaaS: $20-200/mo, strict API rate limits, vendor lock-in.\n"
            f"• Self-Hosted FOSS: $0/mo, zero artificial limits, 100% data privacy.\n\n"
            f"{matrix_slide.get('body', '')}",

            # Tweet 5: Honest Gotchas ("Proof, Not Promises")
            f"4/ Honest Trade-offs ⚠️\n\n"
            f"{gotcha_slide.get('headline', 'What you need to know before self-hosting')}\n\n"
            f"{gotcha_slide.get('body', 'You handle your own backups and reverse proxy SSL. Treat your homelab or VPS with production care.')}",

            # Tweet 6: CTA
            f"5/ Want the full docker-compose template and setup blueprint?\n\n"
            f"1. Like & Repost this thread\n"
            f"2. Reply 'FOSS' below and I'll send you the direct GitHub link and config.\n\n"
            f"Follow @signhify_studio for daily open source engineering breakdowns."
        ]
        return "\n\n---\n\n".join(tweets)

    def generate_linkedin_post(self, carousel: Dict[str, Any]) -> str:
        """
        Builds an executive, engineering-leadership LinkedIn post for founders and CTOs.
        """
        slides = carousel.get("slides", [])
        topic = carousel.get("topic", "")
        hook_slide = slides[0] if slides else {}
        second_slide = slides[1] if len(slides) > 1 else {}
        setup_slide = slides[3] if len(slides) > 3 else {}
        
        post = (
            f"SaaS subscription fatigue is real. Most engineering teams are spending $5,000+ every month on tools they could run themselves on existing compute.\n\n"
            f"Case in point: {hook_slide.get('headline', topic)}.\n\n"
            f"Here is why more engineering leads and CTOs are migrating to open source alternatives:\n\n"
            f"1. Zero Vendor Lock-in: You own the Postgres database, the config files, and the network boundaries.\n"
            f"2. Predictable Infrastructure Costs: Replace per-seat $50/user/month pricing with a single $10/month VPS or internal Docker cluster.\n"
            f"3. Compliance & Data Privacy: No customer data leaves your private subnet. Full GDPR and SOC-2 control.\n\n"
            f"The Solution: {topic}\n"
            f"{second_slide.get('body', 'A production-grade, open-source platform with thousands of community contributors.')}\n\n"
            f"Quick Setup:\n"
            f"{setup_slide.get('proof_or_example', 'docker compose up -d')}\n\n"
            f"Swipe through the slide deck attached for the full architecture breakdown and comparison matrix.\n\n"
            f"Are you paying SaaS premiums for convenience, or are you self-hosting critical tools in your stack?\n\n"
            f"#OpenSource #SoftwareEngineering #DevOps #CloudEconomics #TechLeadership #SelfHosted"
        )
        return post

script_writer = ScriptWriter()

