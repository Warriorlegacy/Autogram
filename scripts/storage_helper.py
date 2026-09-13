"""Public video hosting helper (spec: AUTONOMOUS_INSTAGRAM_REELS_AGENT_SPEC §3.3).

Delegates to the existing engine (src.storage.uploader: S3/R2 -> catbox ->
uguu -> litterbox -> 0x0.st) and keeps the spec's Supabase/transfer.sh path as
explicit fallbacks. Single entry point: upload_to_supabase().
"""

import logging
import os
import sys
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
BUCKET_NAME = os.getenv("SUPABASE_REELS_BUCKET", "reels-cdn")


def _upload_transfer_sh(local_file_path: str) -> str:
    with open(local_file_path, "rb") as f:
        resp = requests.put(
            f"https://transfer.sh/{Path(local_file_path).name}",
            data=f,
            timeout=120,
        )
    resp.raise_for_status()
    return resp.text.strip()


def upload_to_supabase(local_file_path: str) -> str:
    """Uploads file and returns public HTTPS URL for the Meta crawler."""
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client

        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        file_name = f"reel_{Path(local_file_path).name}"
        with open(local_file_path, "rb") as f:
            client.storage.from_(BUCKET_NAME).upload(
                path=file_name,
                file=f,
                file_options={"content-type": "video/mp4", "upsert": "true"},
            )
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"

    # Reuse engine cascade first (R2/catbox/uguu/litterbox/0x0.st), then transfer.sh.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    try:
        from src.storage.uploader import uploader

        return uploader.upload_video_file(local_file_path, "reels", dry_run=False)
    except Exception as e:
        logger.warning(f"Engine uploader unavailable ({e}); falling back to transfer.sh")
    return _upload_transfer_sh(local_file_path)
