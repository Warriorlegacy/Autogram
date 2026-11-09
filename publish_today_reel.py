"""
publish_today_reel.py
Direct execution script to upload and publish Day 01 Reel ('Claude. I Deleted Production')
to live Instagram via Meta Graph API, record media_id, and update schedule.json.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from src.config import settings
from src.instagram.publisher import publisher
from src.storage.uploader import uploader

REEL_PATH = Path("d:/Autogram/docs/reel-studio-kit/out/deleted-production.mp4")
SCHEDULE_FILE = Path("d:/Autogram/data/schedule.json")

CAPTION = (
    "Claude... I think I just dropped the production database. 💀\n\n"
    "The client's CEO is calling my phone.\n"
    "My hands are shaking on the keyboard.\n"
    "And there are literally two branches on GitHub:\n"
    "- production\n"
    "- production-DO-NOT-TOUCH\n\n"
    "Instead of writing an apology email, I ran one open-source Claude Code skill.\n"
    "It diffed our last 40 merged PRs, recovered the lost schema state from migration cache, and restored every single table in 3 minutes.\n\n"
    "Stop stressing over fatal terminal errors.\n\n"
    "👉 Comment \"RESTORE\" below and I will DM you the exact terminal script and GitHub skill that saved my job. (Must be following to unlock the download link 🔒)\n\n"
    "Engineered at Signhify Studio (signhify.dpdns.org)\n"
    "My name is Piyush Raj Singh. Stop posting. Start shipping.\n\n"
    "#ClaudeCode #DevOps #EngineeringHumor #WebDev #OpenSource #SoftwareEngineer #ProductionDown #SignhifyStudio #CodingMemes #DatabaseRecovery"
)

def run():
    print("=" * 60)
    print("EXECUTING LIVE INSTAGRAM REEL PUBLICATION")
    print(f"Video File: {REEL_PATH}")
    print(f"File Size: {REEL_PATH.stat().st_size:,} bytes")
    print(f"Target Account ID: {settings.ig_user_id}")
    print("=" * 60)

    # 1. Upload video to get public URL for Meta Graph API container
    today_str = datetime.now().strftime("%Y-%m-%d")
    print("\n1. Staging video to public CDN / host...")
    public_url = uploader.upload_video_file(str(REEL_PATH), today_str, dry_run=False)
    print(f"✓ Public Video URL: {public_url}")

    # 2. Publish via Meta Graph API
    print("\n2. Initializing Meta Container & Publishing Reel...")
    publisher.dry_run = False
    media_id = publisher.publish_reel(public_url, CAPTION)
    print(f"✓ Reel Published Successfully! Media ID: {media_id}")

    # 3. Post first comment
    print("\n3. Posting discussion comment...")
    try:
        comment_id = publisher.post_comment(media_id, "Drop 'RESTORE' below to get the terminal rollback script & migration guide sent directly to your DMs! 🛠️")
        print(f"✓ First comment posted: {comment_id}")
    except Exception as e:
        print(f"Note on first comment: {e}")

    # 4. Update data/schedule.json
    print("\n4. Updating schedule ledger...")
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        sched = json.load(f)

    for item in sched.get("queue", []):
        if item.get("id") == "SCH-20261108-REEL":
            item["status"] = "COMPLETED"
            item["published_at"] = datetime.now().isoformat()
            item["media_id"] = str(media_id)
            item["public_url"] = public_url

    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(sched, f, indent=2)
    print("✓ schedule.json updated: SCH-20261108-REEL marked COMPLETED.")

    print("\n" + "=" * 60)
    print(f"LIVE PUBLISHING COMPLETE: https://www.instagram.com/p/{media_id}/ (Media ID: {media_id})")
    print("=" * 60)

if __name__ == "__main__":
    run()

