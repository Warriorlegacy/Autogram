#!/usr/bin/env python3
"""
Autonomous Short-Form Video Pipeline Runner (pipeline_runner.py).
Coordinates zero-marginal-cost script generation, MoneyPrinterTurbo video assembly,
cloud media staging, and dual publishing to YouTube Shorts & Instagram Reels.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("PipelineRunner")

# Import core subsystems
from src.config import settings
from src.content.generator import generator
from src.content.cloud_render import render_reel_auto
from src.content.mpt_client import watermark_reel
from src.storage.uploader import uploader
from src.instagram.publisher import publisher
from src.youtube.shorts_publisher import youtube_publisher


def purge_old_artifacts(target_dir: Path, max_age_hours: int = 48):
    """Purges rendered video files older than max_age_hours to prevent disk saturation."""
    if not target_dir.exists():
        return
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    purged_count = 0
    for mp4_file in target_dir.glob("**/*.mp4"):
        try:
            if mp4_file.stat().st_mtime < cutoff:
                mp4_file.unlink()
                purged_count += 1
        except Exception as e:
            logger.debug(f"Could not purge {mp4_file}: {e}")
    if purged_count > 0:
        logger.info(f"Purged {purged_count} cached MP4 files older than {max_age_hours}h.")


def execute_autonomous_run(
    topic: str | None = None,
    pillar: str = "AI Tool Breakdown",
    dry_run: bool = False,
    destinations: list[str] | None = None,
) -> dict:
    """
    Executes a complete short-form video generation & dual-publishing job.
    Destinations can include ['reels', 'shorts'] or both.
    """
    if destinations is None:
        destinations = ["reels", "shorts"]

    selected_topic = topic or "vLLM High-Throughput Engine vs Ollama"
    logger.info("==================================================")
    logger.info(f"Executing Autonomous Video Pipeline Run: '{selected_topic}'")
    logger.info(f"Target Destinations: {destinations}")
    logger.info(f"Execution Mode: {'DRY-RUN / SIMULATION' if dry_run else 'LIVE PRODUCTION'}")
    logger.info("==================================================")
    publisher.dry_run = dry_run

    # 1. Script Generation ($0 multi-LLM chain: Ollama -> Groq -> Gemini -> Template)
    logger.info("Phase 1: Synthesizing narration script & social metadata...")
    script_meta = generator.generate_reel_script(selected_topic, pillar)
    logger.info(f"Narration generated ({len(script_meta['narration'].split())} words): '{script_meta['subject']}'")

    # 2. Setup Output Directory
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = Path("output") / today_str
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    dest_video_path = out_dir / f"video_{timestamp}.mp4"

    # 3. Video Rendering (MPT when local, cloud lane otherwise)
    logger.info("Phase 2: 9:16 Video Rendering...")
    if dry_run:
        logger.info("[DRY-RUN] Skipping actual render; generating placeholder MP4.")
        dest_video_path.write_bytes(b"")
    else:
        logger.info(f"Rendering 9:16 video (MPT when local, cloud lane otherwise)...")
        render_reel_auto(
            script=script_meta["narration"],
            subject=script_meta["subject"],
            dest=dest_video_path,
        )
        logger.info("Burning signhify.studio watermark into video...")
        watermark_reel(dest_video_path)

    # 4. Multi-Platform Distribution
    results = {
        "topic": selected_topic,
        "script": script_meta,
        "video_file": str(dest_video_path),
        "mode": "dry-run" if dry_run else "live",
        "published_at": datetime.now().isoformat(),
        "destinations": {},
    }

    # 4a. YouTube Shorts Upload
    if "shorts" in destinations:
        logger.info("Phase 3a: Uploading to YouTube Shorts...")
        try:
            yt_id = youtube_publisher.upload_short(
                video_path=dest_video_path,
                title=script_meta.get("title", f"{selected_topic} #Shorts"),
                description=f"{script_meta.get('caption', '')}\n\n#Shorts #AI #Tech",
                tags=script_meta.get("hashtags", []),
                dry_run=dry_run,
            )
            results["destinations"]["youtube_shorts"] = {
                "status": "success",
                "video_id": yt_id,
                "url": f"https://youtube.com/shorts/{yt_id}",
            }
        except Exception as e:
            logger.error(f"YouTube Shorts upload failed: {e}")
            results["destinations"]["youtube_shorts"] = {"status": "error", "error": str(e)}

    # 4b. Instagram Reels Publishing
    if "reels" in destinations:
        logger.info("Phase 3b: Staging & Publishing Instagram Reel...")
        try:
            public_video_url = uploader.upload_video_file(str(dest_video_path), today_str, dry_run=dry_run)
            caption = f"{script_meta['caption']}\n\n.\n.\n{' '.join(script_meta['hashtags'])}"
            media_id = publisher.publish_reel(public_video_url, caption)
            results["destinations"]["instagram_reels"] = {
                "status": "success",
                "media_id": media_id,
                "public_url": public_video_url,
            }
        except Exception as e:
            logger.error(f"Instagram Reels publishing failed: {e}")
            results["destinations"]["instagram_reels"] = {"status": "error", "error": str(e)}

    # 5. Save Manifest
    manifest_path = out_dir / f"video_manifest_{timestamp}.json"
    manifest_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    logger.info(f"Manifest written to {manifest_path}")

    # 6. Housekeeping
    purge_old_artifacts(Path("output"), max_age_hours=48)

    logger.info("==================================================")
    logger.info("Autonomous Video Pipeline Run Completed Successfully!")
    logger.info("==================================================")
    return results


def main():
    parser = argparse.ArgumentParser(description="Autonomous Short-Form Video Pipeline Runner")
    parser.add_argument("--now", action="store_true", help="Execute single autonomous run immediately")
    parser.add_argument("--dry-run", action="store_true", help="Simulate video run without publishing")
    parser.add_argument("--topic", type=str, default=None, help="Custom video topic")
    parser.add_argument("--pillar", type=str, default="AI Tool Breakdown", help="Content pillar")
    parser.add_argument("--destination", choices=["all", "shorts", "reels"], default="all", help="Target destinations")
    args = parser.parse_args()

    destinations = ["reels", "shorts"] if args.destination == "all" else [args.destination]
    is_dry = args.dry_run or settings.dry_run

    if args.now or is_dry or args.topic:
        execute_autonomous_run(
            topic=args.topic,
            pillar=args.pillar,
            dry_run=is_dry,
            destinations=destinations,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
