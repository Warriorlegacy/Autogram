"""
src/scheduler/cloud_autopilot_runner.py
Master 24/7 Cloud Autopilot Runner for Autogram.

Designed for zero-touch execution inside GitHub Actions and cloud cron runners.
Determines format (reel vs carousel vs story) based on time slot or queue,
executes Remotion video or Playwright carousel pipeline, and triggers DM automation.
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

# UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Stabilize CPU OpenMP
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Autogram.CloudRunner")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SCHEDULE_PATH = BASE_DIR / "data" / "schedule.json"
MEMORY_PATH = BASE_DIR / "data" / "content-memory.json"
IST_OFFSET = timedelta(hours=5, minutes=30)


def get_current_ist_time() -> datetime:
    """Returns current datetime in Asia/Kolkata (IST = UTC + 5:30)."""
    utc_now = datetime.now(timezone.utc)
    return utc_now + IST_OFFSET


def detect_slot_format(explicit_slot: str = "auto") -> tuple[str, str | None]:
    """
    Determines publishing format ('reel', 'carousel', or 'story') and target item ID.
    If 'auto', checks schedule.json queue first, then falls back to current IST time slot.
    """
    if explicit_slot in ["reel", "carousel", "story"]:
        return explicit_slot, None

    # Check data/schedule.json for queued items
    if SCHEDULE_PATH.exists():
        try:
            sched = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
            queue = sched.get("queue", [])
            for item in queue:
                if item.get("status") == "QUEUED":
                    fmt = item.get("format", "carousel")
                    logger.info(f"✓ Found queued task in schedule.json: {item.get('id')} ({fmt} - '{item.get('topic')}')")
                    return fmt, item.get("id")
        except Exception as e:
            logger.warning(f"Error inspecting schedule.json queue: {e}")

    # Fallback to time slot logic (IST)
    ist_now = get_current_ist_time()
    hour = ist_now.hour
    minute = ist_now.minute
    time_float = hour + (minute / 60.0)

    logger.info(f"Current IST Time: {ist_now.strftime('%H:%M:%S')} (Float: {time_float:.2f})")

    # Optimal Growth Cadence:
    # 08:30 - 11:00 -> Story (Morning High-Signal Story)
    # 11:00 - 15:30 -> Carousel (Midday Prime Carousel — Save & Share Engine)
    # 15:30 - 18:30 -> Story (Evening Tech Radar Story)
    # 18:30 - 23:59 -> Reel (Evening Prime Viral Reel — Non-Follower Reach Engine)
    if 8.5 <= time_float < 11.0:
        return "story", None
    elif 11.0 <= time_float < 15.5:
        return "carousel", None
    elif 15.5 <= time_float < 18.5:
        return "story", None
    elif 18.5 <= time_float < 24.0:
        return "reel", None
    else:
        # Default night/early morning fallback: Carousel
        return "carousel", None


def execute_reel(reel_id: str | None = None, dry_run: bool = False) -> dict:
    """Executes the autonomous Remotion Reel pipeline."""
    from src.content.remotion_reel_pipeline import reel_pipeline
    logger.info("=" * 60)
    logger.info(f"🎬 EXECUTING CLOUD REMOTION REEL PIPELINE (target={reel_id or 'auto'}, dry_run={dry_run})")
    logger.info("=" * 60)
    return reel_pipeline.run_pipeline(reel_id=reel_id, voice="ava", dry_run=dry_run)


def execute_carousel(topic: str | None = None, pillar: str | None = None, dry_run: bool = False) -> dict:
    """Executes the autonomous Carousel pipeline with Playwright rendering."""
    from orchestrator import run_pipeline
    logger.info("=" * 60)
    logger.info(f"📸 EXECUTING CLOUD CAROUSEL PIPELINE (topic={topic or 'auto'}, dry_run={dry_run})")
    logger.info("=" * 60)
    return run_pipeline(dry_run=dry_run, custom_topic=topic, custom_pillar=pillar)


def execute_story(topic: str | None = None, dry_run: bool = False) -> dict:
    """Executes the autonomous Story pipeline."""
    from orchestrator import run_story_pipeline
    logger.info("=" * 60)
    logger.info(f"📱 EXECUTING CLOUD STORY PIPELINE (topic={topic or 'auto'}, dry_run={dry_run})")
    logger.info("=" * 60)
    return run_story_pipeline(dry_run=dry_run, custom_topic=topic)


def execute_dm_scan(dry_run: bool = False) -> dict:
    """Runs the 24/7 comment-scan and DM automator."""
    from src.instagram.dm_automator import dm_automator
    logger.info("\n" + "=" * 60)
    logger.info("🤖 EXECUTING INSTAGRAM AUTO-DM & FOLLOWER-GATE SCAN")
    logger.info("=" * 60)
    dm_automator.dry_run = dry_run
    try:
        summary = dm_automator.scan_and_automate(limit_posts=5)
        logger.info(f"✓ DM Automation scan finished: {summary}")
        return summary
    except Exception as e:
        logger.error(f"⚠️ DM Automator error: {e}")
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Autogram 24/7 Cloud Autopilot Master Runner")
    parser.add_argument("--slot", default="auto", choices=["auto", "carousel", "reel", "story"], help="Publishing format or auto-detection")
    parser.add_argument("--reel-id", default=None, help="Target reel ID from docs/reel-studio-kit")
    parser.add_argument("--topic", default=None, help="Custom topic override")
    parser.add_argument("--pillar", default=None, help="Custom strategic pillar")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without publishing live")
    parser.add_argument("--skip-dm", action="store_true", help="Skip DM automation scan")
    args = parser.parse_args()

    env_dry = os.getenv("DRY_RUN", "false").lower() in ["true", "1", "yes"]
    dry_run = args.dry_run or env_dry

    logger.info("=" * 60)
    logger.info("🚀 AUTOGRAM 24/7 CLOUD AUTOPILOT INITIALIZING")
    logger.info(f"Slot Mode: {args.slot}")
    logger.info(f"Operating Mode: {'DRY RUN / SIMULATION' if dry_run else 'LIVE CLOUD PRODUCTION'}")
    logger.info(f"Current UTC: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info(f"Current IST: {get_current_ist_time().strftime('%Y-%m-%d %H:%M:%S IST')}")
    logger.info("=" * 60)

    # 1. Detect slot format
    fmt, queued_item_id = detect_slot_format(args.slot)
    logger.info(f"🎯 Selected Execution Format: {fmt.upper()} (Queued Item: {queued_item_id or 'None'})")

    result = {}
    if fmt == "reel":
        target_reel = args.reel_id
        if not target_reel and queued_item_id:
            # Check if queued item has an asset path pointing to a reel
            if SCHEDULE_PATH.exists():
                try:
                    sched = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
                    for q in sched.get("queue", []):
                        if q.get("id") == queued_item_id and q.get("asset_path"):
                            path_str = q.get("asset_path", "")
                            target_reel = Path(path_str).stem
                except Exception:
                    pass
        result = execute_reel(reel_id=target_reel, dry_run=dry_run)
    elif fmt == "story":
        result = execute_story(topic=args.topic, dry_run=dry_run)
    else:
        result = execute_carousel(topic=args.topic, pillar=args.pillar, dry_run=dry_run)

    # 2. Run Auto-DM scan
    if not args.skip_dm and not dry_run:
        time.sleep(2)
        execute_dm_scan(dry_run=False)

    logger.info("=" * 60)
    logger.info("🎉 CLOUD AUTOPILOT EXECUTION COMPLETE")
    logger.info(f"Result summary: {json.dumps(result, indent=2, default=str)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
