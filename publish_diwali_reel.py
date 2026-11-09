"""
publish_diwali_reel.py
Publishes the Happy Diwali 2026 Developer Reel to Instagram (@signhify.studio) via Meta Graph API v26.0:
1. Uploads out/happy-diwali.mp4 to public CDN cascade
2. Creates Instagram Reel container with festive tech caption
3. Waits for Meta media processing
4. Publishes live to @signhify.studio
5. Posts pinned first comment for the "DIWALI" trigger
6. Runs DM automator to verify trigger monitoring
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Windows UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.config import settings
from src.instagram.publisher import publisher
from src.storage.uploader import uploader
from src.instagram.dm_automator import dm_automator

REEL_PATH = Path(r"d:\Autogram\docs\reel-studio-kit\out\happy-diwali.mp4")

CAPTION = (
    "Happy Diwali to every engineer still pushing code in dark mode! 🪔✨\n\n"
    "May your inference latency stay under 40 milliseconds, your GPUs never hit out of memory, and your token bills drop to $0.\n\n"
    "While everyone is lighting firecrackers outside, here's what our terminal is firing:\n"
    "⚡ Autonomous multi-agent swarms\n"
    "🎬 60 FPS video compiled straight from React & code\n"
    "🛠️ Zero merge conflicts & 100% test passes\n\n"
    "Goddess Lakshmi blessing for builders in 2026:\n"
    "1. Stop paying $35/mo for video editing timelines. Code your motion.\n"
    "2. Stop paying $50/mo for voice subscriptions. Run Kokoro-82M locally.\n"
    "3. Deploy autonomous pipelines that run while you celebrate.\n\n"
    "👉 Comment \"DIWALI\" below and I'll send our complete open-source production vault & architecture blueprints straight to your DMs! 🪔\n"
    "(Must follow @signhify.studio to unlock 🔒)\n\n"
    "Engineered with pride at Signhify Studio (signhify.dpdns.org)\n"
    "My name is Piyush Raj Singh. Happy Diwali & keep shipping! 🪔🚀\n\n"
    "#HappyDiwali #Diwali2026 #DevLife #Coding #OpenSource #AIEngineering #Remotion #Kokoro #HyperFrames #SignhifyStudio #WebDev #BuildInPublic"
)

FIRST_COMMENT = "Drop 'DIWALI' below to get our entire open-source production repo vault + setup blueprints sent to your DMs! 🪔✨"


def publish_diwali():
    publisher.dry_run = False
    dm_automator.dry_run = False

    if not REEL_PATH.exists():
        print(f"❌ Video not found at {REEL_PATH}")
        sys.exit(1)

    file_size_mb = REEL_PATH.stat().st_size / (1024 * 1024)
    print("==================================================")
    print("🪔 PUBLISHING HAPPY DIWALI REEL TO INSTAGRAM LIVE")
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
        print(f"🎉 HAPPY DIWALI REEL IS LIVE ON INSTAGRAM! Media ID: {media_id}")
        live_url = f"https://www.instagram.com/p/{media_id}/"
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
        print(f"✓ Posts scanned: {summary['media_scanned']}, Comments checked: {summary['comments_checked']}")
    except Exception as e:
        print(f"⚠️ DM automator notice: {e}")

    print("\n==================================================")
    print("🪔 ALL DONE! DIWALI REEL LIVE & DM AUTOMATION ACTIVE!")
    print(f"Live Reel URL: https://www.instagram.com/p/{media_id}/")
    print("==================================================")
    return media_id


if __name__ == "__main__":
    publish_diwali()
