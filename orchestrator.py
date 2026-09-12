"""
Autogram Master Orchestrator (orchestrator.py).
Executes the full zero-touch content pipeline:
Research -> Topic Selection -> Drafting -> Fact-Checking -> Quality Gate -> Rendering -> Upload -> Publishing -> Logging.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 stdout and stderr encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Autogram")

from src.config import settings
from src.db.database import db
from src.research.fetcher import fetcher
from src.research.scorer import scorer, CONTENT_PILLARS
from src.content.generator import generator
from src.content.fact_checker import fact_checker
from src.content.quality_gate import quality_gate
from src.content.image_generator import image_generator
from src.content.script_writer import script_writer
from renderer.render import CarouselRenderer
from src.storage.uploader import uploader
from src.instagram.publisher import publisher
from src.instagram.token_manager import token_manager
from src.analytics.optimizer import optimizer
from src.auth.licensing import get_active_license_status, verify_license

BASE_DIR = Path(__file__).parent
OUTPUT_BASE = BASE_DIR / "output"
BRAND_FILE = BASE_DIR / "data" / "brand.json"

def run_pipeline(dry_run: bool = False, custom_topic: str | None = None, custom_pillar: str | None = None) -> dict:
    """Executes the automated publishing pipeline for daily or targeted topics."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = OUTPUT_BASE / today_str
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("==================================================")
    logger.info(f"Starting Instagram AI Autopilot Run: {today_str}")
    if custom_topic:
        logger.info(f"Target Topic: '{custom_topic}' [{custom_pillar or 'AI Tool Breakdown'}]")
    logger.info(f"Mode: {'DRY RUN / SAFE TEST' if dry_run or settings.dry_run else 'LIVE PRODUCTION'}")
    logger.info("==================================================")

    # Propagate dry_run flag to publisher (overrides .env DRY_RUN for this run)
    publisher.dry_run = dry_run

    # 1. Knowledge Acquisition (Layer A)
    logger.info("Phase 1: Knowledge Acquisition...")
    sources = fetcher.acquire_sources(live_fetch=not dry_run)
    if not sources:
        sources = fetcher.load_seed_records()

    if custom_topic:
        pillar = custom_pillar or "AI Tool Breakdown"
        winner_topic = {
            "topic": custom_topic,
            "angle": f"Comprehensive operational architecture of {custom_topic}",
            "pillar": pillar,
            "evidence_strength": 0.96,
            "novelty_score": 0.92,
            "practicality_score": 0.95,
            "save_share_score": 0.94,
            "viral_score": 93.5,
            "viral_tier": "VIRAL_ALPHA",
            "viral_hook": custom_topic,
            "hook": custom_topic
        }
        selection = {"winner": winner_topic, "reason": "Targeted scheduled topic execution"}
        logger.info(f"Using Explicit Custom/Scheduled Topic: '{winner_topic['topic']}' [{winner_topic['pillar']}]")
    else:
        # 2. Niche Trend Analysis & Strict Virality Gate (Score >= 85.0)
        logger.info("Phase 2: Niche Trend Analysis & Virality Gate (Score >= 85.0)...")
        from src.research.trend_analyzer import trend_analyzer

        candidates = []
        for idx, s in enumerate(sources):
            pillar = s.get("pillar") or CONTENT_PILLARS[idx % len(CONTENT_PILLARS)]
            candidates.append({
                "topic": s.get("source_title"),
                "angle": f"Why {s.get('source_title')} fundamentally impacts operational efficiency",
                "pillar": pillar,
                "evidence_strength": s.get("trust_score", 0.9),
                "novelty_score": 0.88,
                "practicality_score": 0.92,
                "save_share_score": 0.90,
                "saturation_risk": 0.15,
                "sources": [s.get("url")] if s.get("url") else [],
                "source_type": s.get("source_type", ""),
                "stars": s.get("stars", 0),
                "excerpt": s.get("excerpt", "")
            })

        # Filter out anything that cannot go viral and strictly deduplicate against memory
        memory = scorer.load_memory()
        viral_candidates, viral_report = trend_analyzer.filter_viral_candidates(candidates, memory=memory)
        if not viral_candidates:
            logger.warning("No live candidates passed Virality Gate. Failing over to verified viral seed topics...")
            seed_records = fetcher.load_seed_records()
            seed_candidates = [{
                "topic": s.get("source_title"),
                "angle": f"Why {s.get('source_title')} fundamentally impacts operational efficiency",
                "pillar": s.get("pillar", "FOSS SaaS Alternatives"),
                "evidence_strength": 0.98,
                "novelty_score": 0.90,
                "practicality_score": 0.95,
                "save_share_score": 0.95,
                "saturation_risk": 0.1,
                "sources": [s.get("url")] if s.get("url") else [],
                "source_type": s.get("source_type", ""),
                "stars": s.get("stars", 10000),
                "excerpt": s.get("excerpt", "")
            } for s in seed_records]
            viral_candidates, viral_report = trend_analyzer.filter_viral_candidates(seed_candidates, memory=memory)

        # Persist viral analysis report
        viral_file = out_dir / "viral_analysis.json"
        viral_file.write_text(json.dumps(viral_report, indent=2), encoding="utf-8")
        logger.info(f"Persisted viral trend analysis artifact -> {viral_file.name}")

        selection = scorer.select_best_topic(viral_candidates, memory=memory)
        winner_topic = selection["winner"]
        if winner_topic.get("viral_hook"):
            winner_topic["hook"] = winner_topic["viral_hook"]
            winner_topic["angle"] = winner_topic["viral_hook"]

        logger.info(f"Selected Winning Viral Topic: '{winner_topic.get('topic')}'")
        logger.info(f"Viral Score: {winner_topic.get('viral_score')} | Tier: {winner_topic.get('viral_tier')}")
        logger.info(f"Viral Hook: '{winner_topic.get('viral_hook')}'")
        logger.info(f"Pillar: '{winner_topic.get('pillar')}'")
        logger.info(f"Reason: {selection.get('reason')}")

    # Phase 2b: Deep Technical Research & Fact-Enrichment ("Proof, Not Promises")
    logger.info("Phase 2b: Conducting Deep Technical Research on Selected Topic...")
    from src.research.deep_researcher import deep_researcher
    dossier = deep_researcher.research_topic(winner_topic)
    
    # Persist deep research dossier as durable audit proof
    dossier_file = out_dir / "research_dossier.json"
    dossier_file.write_text(json.dumps(dossier, indent=2), encoding="utf-8")
    logger.info(f"Persisted deep research dossier artifact -> {dossier_file.name}")

    enriched_topic = {**winner_topic, "dossier": dossier}
    targeted_sources = [{
        "source_id": "SRC-DEEP-01",
        "source_title": f"Technical Research Dossier: {dossier['topic']}",
        "publisher": dossier.get("github_repo") or dossier.get("replaces_saas") or "Technical Research Lab",
        "url": dossier.get("url", ""),
        "excerpt": (
            f"Stars: {dossier.get('stars', 0):,}. License: {dossier.get('license')}. "
            f"Replaces: {dossier.get('replaces_saas')} (SaaS Cost: {dossier.get('saas_cost_estimate')}, FOSS: {dossier.get('foss_cost')}). "
            f"Quick Run: {dossier.get('deployment_command')}. Stack: {dossier.get('architecture_stack')}. "
            f"Trade-offs: {'; '.join(dossier.get('honest_tradeoffs', []))}."
        )
    }] + sources

    # 3. Creative Production & Drafting (Layer C)
    logger.info("Phase 3: Generating Carousel Copy with Deep Research Grounding...")
    carousel = generator.generate_carousel(enriched_topic, targeted_sources)
    carousel["publication_date"] = today_str

    # Phase 3b: Optional Visual Hero Asset Synthesis (FLUX.1)
    hero_asset_file = None
    if not dry_run and getattr(settings, "image_provider", "none").lower() != "none":
        try:
            logger.info("Phase 3b: Synthesizing Conceptual Visual Hero Asset via FLUX.1...")
            hero_dest = out_dir / "hero_visual.jpg"
            img_prompt = f"Conceptual technical visualization representing {winner_topic.get('topic')}, dark luxury, high dynamic range"
            image_generator.generate_image(img_prompt, output_path=hero_dest)
            hero_asset_file = hero_dest.name
            logger.info(f"Visual hero asset generated -> {hero_dest.name}")
        except Exception as e:
            logger.warning(f"Optional visual asset generation skipped: {e}")

    # 4. Fact-Checking (Layer C)
    logger.info("Phase 4: Running Fact-Check Audit...")
    fact_result = fact_checker.verify_carousel(carousel, sources)
    logger.info(f"Fact-Check: {'PASSED' if fact_result['pass'] else 'REQUIRED EDITS'}")

    # 5. Quality Gate Evaluation (Layer C - with retry logic)
    logger.info("Phase 5: Editor Quality Gate...")
    qa_result = quality_gate.evaluate(carousel)
    
    # Bounded retry if not approved
    retries = 0
    while not qa_result["approved"] and retries < 2:
        logger.warning(f"Quality Gate rejected draft. Attempting revision {retries + 1}...")
        # Apply edits or regenerate
        carousel = generator.generate_carousel(winner_topic, sources)
        qa_result = quality_gate.evaluate(carousel)
        retries += 1

    if not qa_result["approved"]:
        logger.error(f"Quality gate failed after retries: {qa_result['rejection_reasons']}")
        db.save_content_item(carousel, status="FAILED")
        raise RuntimeError("Quality Gate failed to approve content. Terminating to protect brand.")

    # Save to DB as STAGED
    db.save_content_item(carousel, status="STAGED")

    # 6. Slide Design & Rendering (Renderer)
    logger.info("Phase 6: Rendering 1080x1350 JPEG Slides...")
    brand_data = {}
    if BRAND_FILE.exists():
        brand_data = json.loads(BRAND_FILE.read_text(encoding="utf-8"))

    renderer = CarouselRenderer(brand_profile=brand_data)
    rendered_image_paths = renderer.render_carousel(carousel, out_dir)
    logger.info(f"Successfully rendered {len(rendered_image_paths)} slides to {out_dir}")

    # Save content.json, caption.txt, and reels_script.md in output folder
    content_file = out_dir / "content.json"
    content_file.write_text(json.dumps(carousel, indent=2), encoding="utf-8")

    # Generate high-converting caption with hook, value points, CTA & 3-tier viral hashtags
    caption_meta = script_writer.generate_caption(carousel)
    caption_text = caption_meta["caption"]
    caption_file = out_dir / "caption.txt"
    caption_file.write_text(caption_text, encoding="utf-8")
    
    # Save dedicated hashtags file for easy access & reference
    hashtags_file = out_dir / "hashtags.txt"
    hashtags_list = caption_meta.get("hashtags", [])
    hashtags_file.write_text(" ".join(hashtags_list), encoding="utf-8")
    logger.info(f"Generated high-converting caption ({len(caption_text)} chars) with {len(hashtags_list)} viral hashtags attached")

    # Generate viral discussion first-comment to maximize initial engagement velocity
    first_comment_text = caption_meta.get("first_comment") or script_writer.generate_first_comment(carousel)
    first_comment_file = out_dir / "first_comment.txt"
    first_comment_file.write_text(first_comment_text, encoding="utf-8")
    logger.info(f"Generated viral engagement first-comment -> {first_comment_file.name}")

    # Repurpose into 30-45s Reels / Shorts Video Script
    reels_meta = script_writer.generate_reels_script(carousel)
    reels_file = out_dir / "reels_script.md"
    reels_file.write_text(reels_meta["formatted_text"], encoding="utf-8")
    logger.info(f"Generated accompanying 35s Reels script -> {reels_file.name}")

    # Generate production edit-plan (Makerzz Section 8 separation of audio script & visual cuts)
    try:
        edit_plan_meta = script_writer.generate_edit_plan(carousel)
        edit_plan_file = out_dir / "edit_plan.json"
        edit_plan_file.write_text(json.dumps(edit_plan_meta, indent=2), encoding="utf-8")
        logger.info(f"Generated video production edit plan -> {edit_plan_file.name}")
    except Exception as e:
        logger.warning(f"Could not generate edit plan: {e}")

    # Repurpose into Viral X / Twitter Thread
    try:
        x_thread_text = script_writer.generate_x_thread(carousel)
        x_thread_file = out_dir / "x_thread.txt"
        x_thread_file.write_text(x_thread_text, encoding="utf-8")
        logger.info(f"Generated viral X/Twitter thread -> {x_thread_file.name}")
    except Exception as e:
        logger.warning(f"Could not generate X thread: {e}")

    # Repurpose into Executive LinkedIn Post
    try:
        linkedin_text = script_writer.generate_linkedin_post(carousel)
        linkedin_file = out_dir / "linkedin_post.txt"
        linkedin_file.write_text(linkedin_text, encoding="utf-8")
        logger.info(f"Generated executive LinkedIn post -> {linkedin_file.name}")
    except Exception as e:
        logger.warning(f"Could not generate LinkedIn post: {e}")

    # 7. Asset Staging & Upload (Layer D)
    logger.info("Phase 7: Asset Staging / Upload...")
    public_image_urls = uploader.upload_slide_images(rendered_image_paths, today_str, dry_run=dry_run)

    # 8. Distribution / Instagram Publishing (Layer D)
    logger.info("Phase 8: Meta Instagram Publishing Sequence...")
    alt_texts = [s.get("body", s.get("headline", "")) for s in carousel.get("slides", [])]

    media_id = publisher.publish_carousel(
        image_urls=public_image_urls,
        alt_texts=alt_texts,
        caption=caption_text
    )

    # Post viral discussion first comment
    if media_id and not dry_run and not str(media_id).startswith("mock"):
        try:
            publisher.post_comment(media_id, first_comment_text)
            logger.info("Successfully published viral discussion first-comment to Instagram live feed!")
        except Exception as e:
            logger.warning(f"Could not post first comment via Meta API (saved locally to first_comment.txt): {e}")

    # 9. Logging & Memory Learning (Layer E)
    logger.info("Phase 9: Logging & Anti-Repetition Learning...")
    db.update_publication_status(carousel["content_id"], media_id, status="PUBLISHED")
    optimizer.update_memory_with_post(carousel, score=qa_result.get("score", 90))

    # Phase 9b: Autonomous Comment-Reply & Auto-DM Scanning
    try:
        from src.instagram.dm_automator import dm_automator
        dm_automator.dry_run = dry_run or settings.dry_run
        dm_summary = dm_automator.scan_and_automate(limit_posts=3)
        logger.info(f"Phase 9b: Auto-DM Scan completed ({dm_summary.get('actions_executed', 0)} automated responses dispatched).")
    except Exception as e:
        logger.warning(f"Phase 9b Auto-DM scan skipped: {e}")

    manifest = {
        "content_id": carousel["content_id"],
        "date": today_str,
        "topic": carousel["topic"],
        "pillar": carousel["pillar"],
        "hero_visual": hero_asset_file,
        "media_id": media_id,
        "slides_count": len(rendered_image_paths),
        "caption": caption_text,
        "hashtags": hashtags_list,
        "image_files": [Path(p).name for p in rendered_image_paths],
        "image_urls": public_image_urls,
        "qa_score": qa_result.get("score"),
        "viral_score": winner_topic.get("viral_score"),
        "viral_tier": winner_topic.get("viral_tier"),
        "status": "PUBLISHED" if not (dry_run or settings.dry_run) else "SIMULATED_PUBLISH"
    }

    manifest_file = out_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    logger.info("==================================================")
    logger.info(f"Pipeline Completed Successfully!")
    logger.info(f"Artifacts: {out_dir}")
    logger.info(f"Media ID: {media_id}")
    logger.info("==================================================")
    return manifest

def run_scheduler(dry_run: bool = False):
    """Runs a local continuous scheduler daemon for the 7 daily posting slots."""
    import time
    DAILY_SLOTS = ["08:00", "10:30", "13:00", "15:30", "18:00", "20:30", "22:30"]

    logger.info("==================================================")
    logger.info(" Autogram Autonomous 7x Daily Scheduler Active")
    logger.info(f" Daily Target Slots: {', '.join(DAILY_SLOTS)} ({settings.timezone})")
    logger.info(f" Operating Mode: {'DRY RUN / SIMULATION' if dry_run or settings.dry_run else 'LIVE PRODUCTION'}")
    logger.info("==================================================")
    logger.info("Scheduler daemon running. Press Ctrl+C to terminate.")

    triggered_today_slots = set()
    last_day_str = None

    while True:
        now_dt = datetime.now()
        current_time_str = now_dt.strftime("%H:%M")
        current_date_str = now_dt.strftime("%Y-%m-%d")

        # Reset triggered slots on a new day
        if current_date_str != last_day_str:
            triggered_today_slots = set()
            last_day_str = current_date_str

        # Check if current minute matches any of our 7 slots and hasn't run yet
        if current_time_str in DAILY_SLOTS and current_time_str not in triggered_today_slots:
            logger.info(f"Triggering scheduled autonomous publishing run for slot {current_time_str}...")
            triggered_today_slots.add(current_time_str)
            try:
                run_pipeline(dry_run=dry_run)
            except Exception as e:
                logger.error(f"Scheduled pipeline run error on slot {current_time_str}: {e}")

        time.sleep(20)

def main():
    parser = argparse.ArgumentParser(description="Autogram: Autonomous Instagram Content Engine")
    parser.add_argument("--run-all", action="store_true", help="Run full pipeline end-to-end")
    parser.add_argument("--dry-run", action="store_true", help="Run pipeline safely without publishing")
    parser.add_argument("--render-only", action="store_true", help="Render sample slides only")
    parser.add_argument("--refresh-token", action="store_true", help="Refresh Meta long-lived token")
    parser.add_argument("--test", action="store_true", help="Run diagnostic health check")
    parser.add_argument("--generate-image", type=str, metavar="PROMPT", help="Generate standalone conceptual tech image")
    parser.add_argument("--generate-script", action="store_true", help="Generate carousel script and caption only")
    parser.add_argument("--generate-reel", action="store_true", help="Generate 30-45s Reels / Shorts video script")
    parser.add_argument("--schedule", action="store_true", help="Run local autonomous daily scheduler daemon")
    parser.add_argument("--auto-dm", action="store_true", help="Scan recent posts, auto-reply to comments, and dispatch private DMs")
    parser.add_argument("--topic", type=str, default=None, help="Target topic to generate and publish")
    parser.add_argument("--pillar", type=str, default=None, help="Strategic content pillar for the target topic")
    parser.add_argument("--license-key", type=str, help="Client license key or Owner master key")

    args = parser.parse_args()

    # Access Control & Monetization Verification Gate
    if args.license_key:
        auth_status = verify_license(args.license_key)
    else:
        auth_status = get_active_license_status()

    if not auth_status["valid"]:
        print("="*60)
        print(" [AUTOGRAM ACCESS GATE] Paid Client License Required")
        print("="*60)
        print(f" Access Status: REJECTED")
        print(f" Reason:        {auth_status['reason']}")
        print("\n Autogram is a high-ticket B2B content infrastructure system.")
        print(" External clients must hold an active subscription license:")
        print("  - Starter Autopilot:    $497 / month")
        print("  - Growth Autopilot:     $997 / month")
        print("  - Enterprise Swarm:     $2,497 / month")
        print("\n To subscribe, visit: https://autogram-ai.vercel.app/#pricing")
        print(" If you are the system Owner, set AUTOGRAM_OWNER_KEY in your .env")
        print("="*60)
        sys.exit(1)

    if auth_status["is_owner"]:
        print(f"[AUTH] 👑 OWNER MASTER ACCESS: VERIFIED (100% Free Unlimited Pipeline)")
    else:
        print(f"[AUTH] 💼 ACTIVE CLIENT LICENSE: {auth_status['tier'].upper()} ({auth_status['client']}) - Expires {auth_status['expires_at']}")

    if args.generate_image:
        print(f"\n[AI Image Generation] Prompt: {args.generate_image}")
        img_path = image_generator.generate_image(args.generate_image)
        print(f"Image successfully saved to: {img_path.resolve()}\n")
        return

    if args.generate_script:
        sources = fetcher.acquire_sources(live_fetch=False)
        candidates = [{"topic": s.get("source_title"), "angle": "Operational take", "pillar": "AI Tool Breakdown", "sources": [s.get("url")]} for s in sources]
        winner = scorer.select_best_topic(candidates)["winner"]
        carousel = generator.generate_carousel(winner, sources)
        caption = script_writer.generate_caption(carousel)
        print("\n" + "="*50)
        print(f"CAROUSEL TOPIC: {carousel['topic']}")
        print(f"SLIDES: {len(carousel['slides'])}")
        print("="*50)
        print(caption["caption"])
        print("="*50 + "\n")
        return

    if args.generate_reel:
        sources = fetcher.acquire_sources(live_fetch=False)
        candidates = [{"topic": s.get("source_title"), "angle": "Operational take", "pillar": "AI Tool Breakdown", "sources": [s.get("url")]} for s in sources]
        winner = scorer.select_best_topic(candidates)["winner"]
        carousel = generator.generate_carousel(winner, sources)
        reel = script_writer.generate_reels_script(carousel)
        print("\n" + "="*50)
        print(reel["formatted_text"])
        print("="*50 + "\n")
        return

    if args.refresh_token:
        res = token_manager.refresh_token()
        print(f"Token refresh result: {res}")
        return

    if args.render_only:
        from renderer.render import render_sample
        render_sample("output/sample")
        return

    if args.test:
        print("Running Autogram Diagnostic Health Check...")
        print(f"Python Version: {sys.version}")
        print(f"DB Path: {db.db_path}")
        print(f"Dry Run Setting: {settings.dry_run}")
        sources = fetcher.acquire_sources()
        print(f"Sources Loaded: {len(sources)}")
        print("Health Check Complete: OK")
        return

    if args.auto_dm:
        from src.instagram.dm_automator import dm_automator
        dry = args.dry_run or settings.dry_run
        dm_automator.dry_run = dry
        summary = dm_automator.scan_and_automate(limit_posts=5)
        print("\n" + "="*50)
        print("INSTAGRAM AUTO-DM & COMMENT-REPLY SCAN RESULTS")
        print("="*50)
        print(f"Posts Scanned: {summary['media_scanned']}")
        print(f"Comments Checked: {summary['comments_checked']}")
        print(f"Automated DMs Dispatched: {summary['actions_executed']}")
        for act in summary['details']:
            print(f" -> @{act['username']}: matched [{act['keyword']}] -> {act['dm_status']}")
        print("="*50 + "\n")
        return

    if args.schedule:
        dry = args.dry_run or settings.dry_run
        run_scheduler(dry_run=dry)
        return

    # Default action or --run-all / --dry-run
    dry = args.dry_run or (not args.run_all)
    run_pipeline(dry_run=dry, custom_topic=args.topic, custom_pillar=args.pillar)

if __name__ == "__main__":
    main()
