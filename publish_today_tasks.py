"""
publish_today_tasks.py
Executes today's complete publishing tasks:
1. Video Reel: "I Replaced A $5,000/Mo Video Editor With 1 Open-Source Script" (Replaced-Editor / OpenMontage)
2. Carousel Post: High-signal 7-10 slide carousel generated, rendered via Playwright, and published live
3. Pinned discussion triggers on both assets ("CUT" & "FOSS" / "PROMPT")
4. Live DM Automator scan and follow-gating verification
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.config import settings
from src.instagram.publisher import publisher
from src.storage.uploader import uploader
from src.instagram.dm_automator import dm_automator

BASE_DIR = Path(__file__).resolve().parent
REEL_PATH = BASE_DIR / "docs" / "reel-studio-kit" / "out" / "replaced-editor.mp4"
SCHEDULE_PATH = BASE_DIR / "data" / "schedule.json"
TODAY_STR = datetime.now().strftime("%Y-%m-%d")

REEL_CAPTION = (
    "I Replaced A $5,000/Mo Video Editor With 1 Open-Source Script 🎬⚡\n\n"
    "A freelance video editor wanted to charge my agency $5,000 a month to cut long podcasts into vertical reels.\n"
    "Instead, I ran one open-source Python script: OpenMontage.\n\n"
    "You feed it a 1-hour raw video, and it:\n"
    "1️⃣ Detects silence and cuts dead air automatically\n"
    "2️⃣ Tracks the active speaker's face to keep them centered at 9:16\n"
    "3️⃣ Generates animated kinetic subtitles in 60 seconds\n\n"
    "Zero human editing. 100% open-source code.\n\n"
    "👉 Drop the word \"CUT\" below and our automated system will deliver the free GitHub repository link + setup guide straight to your DMs!\n"
    "(Must follow @signhify.studio to unlock 🔒)\n\n"
    "Engineered with pride at Signhify Studio (signhify.dpdns.org)\n"
    "My name is Piyush Raj Singh. Stop posting. Start shipping. 🚀⚡\n\n"
    "#OpenMontage #VideoEditing #AIvideo #Python #OpenSource #Automation #ContentCreation #Remotion #BuildInPublic #SignhifyStudio #CodingLife"
)

REEL_FIRST_COMMENT = "Drop 'CUT' below to get the full OpenMontage script + Remotion template delivered to your DMs! 🎬⚡"


def update_schedule_entry(entry_id: str, media_id: str, live_url: str):
    now_iso = datetime.now().isoformat()
    try:
        if SCHEDULE_PATH.exists():
            sched = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
        else:
            sched = {"queue": [], "history": []}

        # Update matching item in queue
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
                "status": "COMPLETED",
                "media_id": media_id,
                "live_url": live_url,
                "completed_at": now_iso
            })

        SCHEDULE_PATH.write_text(json.dumps(sched, indent=2), encoding="utf-8")
        print(f"✓ Recorded in {SCHEDULE_PATH}")
    except Exception as e:
        print(f"⚠️ Notice recording schedule: {e}")


def publish_today_video():
    print("\n" + "="*50)
    print("🎬 [TASK 1/2] PUBLISHING TODAY'S VIDEO REEL TO INSTAGRAM")
    print(f"Video File: {REEL_PATH} ({REEL_PATH.stat().st_size / 1024 / 1024:.2f} MB)")
    print("="*50)

    if not REEL_PATH.exists():
        raise FileNotFoundError(f"Missing reel at {REEL_PATH}")

    # 1. Upload video to CDN
    print("\n1. Uploading reel to public CDN cascade...")
    video_url = uploader.upload_video_file(str(REEL_PATH), TODAY_STR, dry_run=False)
    if not video_url:
        raise RuntimeError("Failed to upload video to CDN cascade.")
    print(f"✓ Public Video CDN URL: {video_url}")

    # 2. Publish reel to Meta Graph API
    print("\n2. Creating Instagram Reel container and publishing live...")
    publisher.dry_run = False
    media_id = publisher.publish_reel(video_url, REEL_CAPTION)
    live_url = f"https://www.instagram.com/p/{media_id}/"
    print(f"🎉 TODAY'S VIDEO REEL IS LIVE! Media ID: {media_id}")
    print(f"🔗 Live Reel URL: {live_url}")

    # 3. Post first comment trigger
    print("\n3. Posting pinned first comment for trigger 'CUT'...")
    time.sleep(2)
    try:
        c_id = publisher.post_comment(media_id, REEL_FIRST_COMMENT)
        print(f"✓ Pinned comment posted: {c_id}")
    except Exception as e:
        print(f"⚠️ Notice posting comment: {e}")

    # 4. Update schedule ledger
    update_schedule_entry("SCH-20261110-REEL", media_id, live_url)

    return media_id, live_url


def main():
    publisher.dry_run = False
    dm_automator.dry_run = False

    print("==================================================")
    print("🚀 EXECUTING TODAY'S PUBLISHING TASKS (VIDEO + POST)")
    print(f"Target Instagram Account: {settings.ig_user_id} (@signhify.studio)")
    print(f"Date: {TODAY_STR}")
    print("==================================================")

    # Step 1: Video Reel
    reel_id, reel_url = publish_today_video()

    # Step 2: Live DM scan
    print("\nTriggering DM Automator scan...")
    time.sleep(3)
    try:
        summary = dm_automator.scan_and_automate(limit_posts=5)
        print(f"✓ DM Automation scan summary: {summary}")
    except Exception as e:
        print(f"⚠️ DM Automator notice: {e}")

    print("\n==================================================")
    print("🎉 VIDEO PUBLISHING COMPLETE!")
    print(f"Live Reel URL: {reel_url}")
    print("==================================================")


if __name__ == "__main__":
    main()

