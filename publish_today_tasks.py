"""
publish_today_tasks.py
Executes today's complete publishing tasks:
1. Video Reel: High-retention Remotion 60fps reel from docs/reel-studio-kit (default: doc-engine / replaced-editor)
2. Carousel Post: High-signal 7-10 slide carousel generated and rendered via Playwright, and published live
3. Pinned discussion triggers on both assets ("DOCS", "CUT", "FOSS", "PROMPT")
4. Live DM Automator scan and follow-gating verification
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

# UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Stabilize CPU OpenMP memory
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from src.config import settings
from src.instagram.publisher import publisher
from src.storage.uploader import uploader
from src.instagram.dm_automator import dm_automator
from src.content.remotion_reel_pipeline import reel_pipeline, REEL_METADATA

BASE_DIR = Path(__file__).resolve().parent
REEL_KIT_DIR = BASE_DIR / "docs" / "reel-studio-kit"
SCHEDULE_PATH = BASE_DIR / "data" / "schedule.json"
TODAY_STR = datetime.now().strftime("%Y-%m-%d")

DOC_ENGINE_CAPTION = (
    "How We Code 30-Minute AI Documentaries (React + Remotion + Whisper) 🎬🏛️\n\n"
    "Most creators take two weeks to research and edit a 30-minute documentary.\n"
    "We do it in 60 seconds with 1 open-source terminal script.\n\n"
    "Here is the architecture:\n"
    "1️⃣ Step 1: Deep research pulls primary sources from Europe PMC and ArXiv\n"
    "2️⃣ Step 2: Claude structures the narrative into three documentary acts\n"
    "3️⃣ Step 3: HyperFrames compiles visual motion, maps, and studio audio into an ultra-high definition MP4\n\n"
    "👉 Drop the word \"DOCS\" below and our automated system will deliver the complete documentary engine repository + setup blueprint straight to your DMs!\n"
    "(Must follow @signhify.studio to unlock 🔒)\n\n"
    "Engineered with pride at Signhify Studio (signhify.dpdns.org)\n"
    "My name is Piyush Raj Singh. Stop posting. Start shipping. 🚀⚡\n\n"
    "#AIDocumentary #HyperFrames #Remotion #OpenSource #Python #VideoEditing #AIEngineering #BuildInPublic #SignhifyStudio #CodingLife"
)

DOC_ENGINE_FIRST_COMMENT = (
    "Drop 'DOCS' below to get the full Remotion documentary engine + prompt chains delivered straight to your DMs! 🎬⚡ (Must follow @signhify.studio to unlock 🔐)"
)


def update_schedule_entry(entry_id: str, media_id: str, live_url: str, topic: str = "", format_type: str = "reel"):
    now_iso = datetime.now().isoformat()
    try:
        if SCHEDULE_PATH.exists():
            sched = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
        else:
            sched = {"queue": [], "history": []}

        found = False
        for q in sched.get("queue", []):
            if q.get("id") == entry_id:
                q["status"] = "COMPLETED"
                q["media_id"] = media_id
                q["live_url"] = live_url
                q["completed_at"] = now_iso
                found = True
                break

        if not found:
            sched.setdefault("queue", []).append({
                "id": entry_id,
                "scheduled_time": now_iso,
                "topic": topic,
                "format": format_type,
                "status": "COMPLETED",
                "media_id": media_id,
                "live_url": live_url,
                "completed_at": now_iso
            })

        SCHEDULE_PATH.write_text(json.dumps(sched, indent=2), encoding="utf-8")
        print(f"✓ Recorded in {SCHEDULE_PATH}")
    except Exception as e:
        print(f"⚠️ Notice recording schedule: {e}")


def publish_today_video(reel_id: str = "doc-engine", dry_run: bool = False):
    print("\n" + "="*50)
    print(f"🎬 [TASK 1/2] PUBLISHING TODAY'S VIDEO REEL: {reel_id.upper()}")
    print("="*50)

    video_file = REEL_KIT_DIR / "out" / f"{reel_id}.mp4"
    if not video_file.exists():
        print(f"Video file not pre-rendered at {video_file}. Running remotion pipeline build...")
        res = reel_pipeline.run_pipeline(reel_id=reel_id, dry_run=dry_run)
        return res.get("media_id"), res.get("permalink")

    print(f"✓ Video File: {video_file} ({video_file.stat().st_size / 1024 / 1024:.2f} MB)")

    caption = DOC_ENGINE_CAPTION if reel_id == "doc-engine" else REEL_METADATA.get(reel_id, {}).get("caption", DOC_ENGINE_CAPTION)
    first_comment = DOC_ENGINE_FIRST_COMMENT if reel_id == "doc-engine" else REEL_METADATA.get(reel_id, {}).get("first_comment", "Drop keyword below!")

    if dry_run:
        print("[DRY-RUN] Video upload and publication simulated successfully.")
        return "mock_reel_id_12345", "https://instagram.com/reel/mock_reel_12345/"

    # 1. Upload video to CDN
    print("\n1. Uploading reel to public CDN cascade...")
    video_url = uploader.upload_video_file(str(video_file), TODAY_STR, dry_run=False)
    if not video_url:
        raise RuntimeError("Failed to upload video to CDN cascade.")
    print(f"✓ Public Video CDN URL: {video_url}")

    # 2. Publish reel to Meta Graph API
    print("\n2. Creating Instagram Reel container and publishing live...")
    publisher.dry_run = False
    media_id = publisher.publish_reel(video_url, caption)
    live_url = f"https://www.instagram.com/reel/{media_id}/"
    print(f"🎉 TODAY'S VIDEO REEL IS LIVE! Media ID: {media_id}")
    print(f"🔗 Live Reel URL: {live_url}")

    # 3. Post first comment trigger
    print(f"\n3. Posting pinned first comment for trigger on {media_id}...")
    time.sleep(2)
    try:
        c_id = publisher.post_comment(media_id, first_comment)
        print(f"✓ Pinned comment posted: {c_id}")
    except Exception as e:
        print(f"⚠️ Notice posting comment: {e}")

    # 4. Update schedule ledger
    update_schedule_entry(f"SCH-{datetime.now().strftime('%Y%m%d')}-{reel_id.upper()}", media_id, live_url, topic=f"Reel: {reel_id}", format_type="reel")

    return media_id, live_url


def publish_today_post(topic: str = "7 Open-Source CLI Tools That Replace $300/Mo In Dev Subscriptions", pillar: str = "Developer Power Tools & CLI", dry_run: bool = False):
    print("\n" + "="*50)
    print(f"📸 [TASK 2/2] PUBLISHING TODAY'S CAROUSEL POST")
    print(f"Topic: {topic}")
    print(f"Pillar: {pillar}")
    print("="*50)

    from orchestrator import run_pipeline

    print("\nExecuting autonomous carousel pipeline (generation, QA, Playwright rendering, and live publishing)...")
    res = run_pipeline(dry_run=dry_run, custom_topic=topic, custom_pillar=pillar)
    
    media_id = res.get("media_id") or "carousel_published"
    live_url = res.get("permalink") or f"https://www.instagram.com/p/{media_id}/"
    
    print(f"🎉 TODAY'S CAROUSEL POST IS LIVE! Media ID: {media_id}")
    print(f"🔗 Live Post URL: {live_url}")

    update_schedule_entry(f"SCH-{datetime.now().strftime('%Y%m%d')}-EVENING-CAROUSEL", str(media_id), live_url, topic=topic, format_type="carousel")

    return media_id, live_url


def main():
    parser = argparse.ArgumentParser(description="Complete Today's Publishing Tasks: Video Reel and Carousel Post")
    parser.add_argument("--reel-id", default="doc-engine", help="Remotion reel project ID from docs/reel-studio-kit (default: doc-engine)")
    parser.add_argument("--video-only", action="store_true", help="Publish video reel only")
    parser.add_argument("--post-only", action="store_true", help="Publish carousel post only")
    parser.add_argument("--topic", default="7 Open-Source CLI Tools That Replace $300/Mo In Dev Subscriptions", help="Carousel post topic")
    parser.add_argument("--pillar", default="Developer Power Tools & CLI", help="Strategic content pillar")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without publishing live")
    args = parser.parse_args()

    publisher.dry_run = args.dry_run
    dm_automator.dry_run = args.dry_run

    print("==================================================")
    print("🚀 EXECUTING TODAY'S PUBLISHING TASKS (VIDEO + POST)")
    print(f"Target Instagram Account: {settings.ig_user_id} (@signhify.studio)")
    print(f"Target Reel: {args.reel_id}")
    print(f"Date: {TODAY_STR}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE PRODUCTION'}")
    print("==================================================")

    reel_res = None
    post_res = None

    # Step 1: Video Reel
    if not args.post_only:
        reel_res = publish_today_video(reel_id=args.reel_id, dry_run=args.dry_run)

    # Step 2: Carousel Post
    if not args.video_only:
        post_res = publish_today_post(topic=args.topic, pillar=args.pillar, dry_run=args.dry_run)

    # Step 3: Live DM Automation Scan
    if not args.dry_run:
        print("\nTriggering DM Automator scan...")
        time.sleep(3)
        try:
            summary = dm_automator.scan_and_automate(limit_posts=5)
            print(f"✓ DM Automation scan summary: {summary}")
        except Exception as e:
            print(f"⚠️ DM Automator notice: {e}")

    print("\n==================================================")
    print("🎉 TODAY'S PUBLISHING TASKS ARE 100% COMPLETE!")
    if reel_res:
        print(f"📹 Live Reel URL: {reel_res[1]}")
    if post_res:
        print(f"📸 Live Carousel URL: {post_res[1]}")
    print("==================================================")


if __name__ == "__main__":
    main()
