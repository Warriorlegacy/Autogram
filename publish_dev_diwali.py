"""
publish_dev_diwali.py
Publishes the new Developer's Diwali 2026 Reel to Instagram (@signhify.studio) via Meta Graph API v26.0:
1. Uploads out/diwali-dev-mode.mp4 to public CDN cascade
2. Creates Instagram Reel container (REELS 9:16) with festive tech caption
3. Waits for Meta media processing
4. Publishes live to @signhify.studio
5. Posts pinned first comment for the "FESTIVE" & "DIWALI" trigger
6. Runs DM automator to verify trigger monitoring
7. Records run in data/schedule.json
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Windows UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.config import settings
from src.instagram.publisher import publisher
from src.storage.uploader import uploader
from src.instagram.dm_automator import dm_automator

REEL_PATH = Path(r"d:\Autogram\docs\reel-studio-kit\out\diwali-dev-mode.mp4")
SCHEDULE_PATH = Path(r"d:\Autogram\data\schedule.json")

CAPTION = (
    "The Developer's Diwali: How Engineers Light Up The World 🪔✨\n\n"
    "This Diwali, don't just light firecrackers outside. Light up your terminal.\n\n"
    "While your family is cleaning the house, you're running `docker system prune` and reclaiming 300GB of cache.\n"
    "Instead of burning cash on sky shots, we're burning GPU cycles fine-tuning local models that run at 40 tokens/sec for $0.00.\n\n"
    "Goddess Lakshmi blessings for every engineer in 2026:\n"
    "📈 10x ARR delivery to your codebase\n"
    "🛡️ Zero 500 errors in your cloud logs\n"
    "💳 Clients who pay invoices on time without chasing\n"
    "📦 Pure open-source software stack replacing four-figure SaaS bills\n\n"
    "From all of us at Signhify Studio, Happy Diwali to every builder shipping in silence! 🪔🚀\n\n"
    "👉 Drop the word \"FESTIVE\" or \"DIWALI\" below and our automated system will deliver the complete open-source master repo vault + architecture blueprints straight to your DMs!\n"
    "(Must follow @signhify.studio to unlock 🔒)\n\n"
    "Engineered with pride at Signhify Studio (signhify.dpdns.org)\n"
    "My name is Piyush Raj Singh. Stop posting. Start shipping. 🪔⚡\n\n"
    "#HappyDiwali #Diwali2026 #DevDiwali #SoftwareEngineering #Docker #OpenSource #LocalAI #Remotion #AIEngineering #BuildInPublic #SignhifyStudio #CodingLife"
)

FIRST_COMMENT = "Drop 'FESTIVE' or 'DIWALI' below to unlock our complete open-source repo starter pack & architecture blueprints in your DMs! 🪔✨"


def record_schedule(media_id: str, live_url: str):
    try:
        if SCHEDULE_PATH.exists():
            data = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
        else:
            data = {"queue": [], "history": []}

        now_iso = datetime.now().isoformat()
        entry = {
            "id": f"SCH-{datetime.now().strftime('%Y%m%d')}-DEV-DIWALI",
            "scheduled_time": now_iso,
            "topic": "The Developer's Diwali: How Engineers Light Up The World",
            "pillar": "Local AI & Edge Compute",
            "format": "reel",
            "mode": "live",
            "status": "COMPLETED",
            "created_at": now_iso,
            "started_at": now_iso,
            "completed_at": now_iso,
            "media_id": media_id,
            "live_url": live_url,
            "trigger_words": ["FESTIVE", "DIWALI"]
        }
        data.setdefault("queue", []).append(entry)
        SCHEDULE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"✓ Recorded in {SCHEDULE_PATH}")
    except Exception as e:
        print(f"⚠️ Schedule recording note: {e}")


def publish_dev_diwali():
    publisher.dry_run = False
    dm_automator.dry_run = False

    if not REEL_PATH.exists():
        print(f"❌ Video not found at {REEL_PATH}")
        sys.exit(1)

    file_size_mb = REEL_PATH.stat().st_size / (1024 * 1024)
    print("==================================================")
    print("🪔 PUBLISHING NEW DEVELOPER'S DIWALI REEL TO INSTAGRAM LIVE")
    print(f"Target Account: {settings.ig_user_id} (@signhify.studio)")
    print(f"Video File: {REEL_PATH} ({file_size_mb:.2f} MB)")
    print("==================================================")

    # 1. Upload video
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n1. Uploading video to public CDN cascade (date: {today_str})...")
    video_url = uploader.upload_video_file(str(REEL_PATH), today_str, dry_run=False)
    if not video_url:
        print("❌ Video upload failed!")
        sys.exit(1)
    print(f"✓ Video public URL: {video_url}")

    # 2. Publish reel
    print("\n2. Creating Reel container & publishing to Meta Graph API...")
    try:
        media_id = publisher.publish_reel(video_url, CAPTION)
        live_url = f"https://www.instagram.com/p/{media_id}/"
        print(f"🎉 NEW DIWALI REEL IS LIVE ON INSTAGRAM! Media ID: {media_id}")
        print(f"🔗 Live URL: {live_url}")
    except Exception as e:
        print(f"❌ Error publishing reel: {e}")
        sys.exit(1)

    # 3. First comment
    print("\n3. Posting pinned first comment trigger...")
    time.sleep(2)
    try:
        comment_id = publisher.post_comment(media_id, FIRST_COMMENT)
        print(f"✓ First comment posted! Comment ID: {comment_id}")
    except Exception as e:
        print(f"⚠️ Notice on first comment: {e}")

    # 4. DM Automator scan
    print("\n4. Triggering Instagram DM Automator scan...")
    time.sleep(3)
    try:
        summary = dm_automator.scan_and_automate(limit_posts=5)
        print(f"✓ Posts scanned: {summary.get('media_scanned', 0)}, Comments checked: {summary.get('comments_checked', 0)}")
    except Exception as e:
        print(f"⚠️ DM automator notice: {e}")

    # 5. Record schedule
    record_schedule(media_id, live_url)

    print("\n==================================================")
    print("🪔 ALL DONE! NEW DIWALI REEL LIVE & DM AUTOMATION ACTIVE!")
    print(f"Live Reel URL: {live_url}")
    print("==================================================")
    return media_id, live_url


if __name__ == "__main__":
    publish_dev_diwali()

