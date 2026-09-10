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

def run_pipeline(dry_run: bool = False) -> dict:
    """Executes the daily automated publishing pipeline."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = OUTPUT_BASE / today_str
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("==================================================")
    logger.info(f"Starting Instagram AI Autopilot Run: {today_str}")
    logger.info(f"Mode: {'DRY RUN / SAFE TEST' if dry_run or settings.dry_run else 'LIVE PRODUCTION'}")
    logger.info("==================================================")

    # Propagate dry_run flag to publisher (overrides .env DRY_RUN for this run)
    publisher.dry_run = dry_run

    # 1. Knowledge Acquisition (Layer A)
    logger.info("Phase 1: Knowledge Acquisition...")
    sources = fetcher.acquire_sources(live_fetch=not dry_run)
    if not sources:
        raise RuntimeError("No source records available.")

    # 2. Topic Scoring & Selection (Layer B with 6-Pillar Strategic Rotation)
    logger.info("Phase 2: Topic Scoring & Selection (6-Pillar Rotation)...")
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
            "sources": [s.get("url")]
        })

    selection = scorer.select_best_topic(candidates)
    winner_topic = selection["winner"]
    logger.info(f"Selected Topic: '{winner_topic.get('topic')}'")
    logger.info(f"Pillar: '{winner_topic.get('pillar')}'")
    logger.info(f"Reason: {selection.get('reason')}")

    # 3. Creative Production & Drafting (Layer C)
    logger.info("Phase 3: Generating Carousel Copy...")
    carousel = generator.generate_carousel(winner_topic, sources)
    carousel["publication_date"] = today_str

    # Phase 3b: Optional Visual Hero Asset Synthesis (FLUX.1)
    hero_asset_file = None
    if getattr(settings, "image_provider", "none").lower() != "none":
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

    # 7. Asset Staging & Upload (Layer D)
    logger.info("Phase 7: Asset Staging / Upload...")
    public_image_urls = uploader.upload_slide_images(rendered_image_paths, today_str)

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

    if args.schedule:
        dry = args.dry_run or settings.dry_run
        run_scheduler(dry_run=dry)
        return

    # Default action or --run-all / --dry-run
    dry = args.dry_run or (not args.run_all)
    run_pipeline(dry_run=dry)

if __name__ == "__main__":
    main()
