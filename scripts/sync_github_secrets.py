"""
sync_github_secrets.py
Safely syncs production secrets from local .env into GitHub Actions repository secrets
using the official GitHub CLI (`gh secret set`) over stdin without exposing values in command logs.
"""

import sys
import subprocess
from pathlib import Path
from dotenv import dotenv_values

ENV_PATH = Path(__file__).parent.parent / ".env"

SYNC_KEYS = [
    "AUTOGRAM_OWNER_KEY",
    "GEMINI_API_KEY",
    "OPENROUTER_API_KEY",
    "GROQ_API_KEY",
    "NVIDIA_NIM_API_KEY",
    "OPENAI_API_KEY",
    "CLAUDE_API_KEY",
    "IG_USER_ID",
    "IG_ACCESS_TOKEN",
    "INSTAGRAM_BUSINESS_ACCOUNT_ID",
    "META_API_VERSION",
    "META_APP_ID",
    "META_APP_SECRET",
    "META_GRAPH_ACCESS_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "S3_ENDPOINT",
    "S3_BUCKET",
    "S3_ACCESS_KEY",
    "S3_SECRET_KEY",
    "S3_REGION",
    "PUBLIC_CDN_BASE",
    "IMGBB_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
]

def sync_secrets():
    if not ENV_PATH.exists():
        print(f"❌ .env file not found at {ENV_PATH}")
        sys.exit(1)

    env_vars = dotenv_values(ENV_PATH)
    synced_count = 0
    skipped_count = 0

    print("==================================================")
    print("🔒 SYNCING LOCAL .ENV SECRETS TO GITHUB ACTIONS")
    print("==================================================")

    for key in SYNC_KEYS:
        val = env_vars.get(key)
        if val is not None and val.strip() != "":
            # Set via stdin pipe to avoid exposing secrets in process arguments or logs
            try:
                cmd = ["gh", "secret", "set", key]
                res = subprocess.run(cmd, input=val.strip(), text=True, capture_output=True)
                if res.returncode == 0:
                    print(f"✓ Secret set: {key}")
                    synced_count += 1
                else:
                    print(f"❌ Failed to set {key}: {res.stderr.strip()}")
            except Exception as e:
                print(f"❌ Error setting {key}: {e}")
        else:
            skipped_count += 1

    print("==================================================")
    print(f"🎉 Secrets Sync Complete: {synced_count} set, {skipped_count} skipped/empty.")
    print("==================================================")

if __name__ == "__main__":
    sync_secrets()
