"""Instagram publishing engine (spec: AUTONOMOUS_INSTAGRAM_REELS_AGENT_SPEC §3.4).

Delegates to src.instagram.publisher (container -> poll FINISHED -> publish),
which already implements retries, quota guard, and dry-run. Accepts both the
spec env names (INSTAGRAM_BUSINESS_ACCOUNT_ID / META_GRAPH_ACCESS_TOKEN) and
the engine names (IG_USER_ID / IG_ACCESS_TOKEN).
"""

import os
import sys
from pathlib import Path

# Spec env aliases -> engine env names (set before src.config import).
# ponytail: only bridge non-empty spec vars so we never shadow real .env values with "".
if os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID") and not os.getenv("IG_USER_ID"):
    os.environ["IG_USER_ID"] = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
if os.getenv("META_GRAPH_ACCESS_TOKEN") and not os.getenv("IG_ACCESS_TOKEN"):
    os.environ["IG_ACCESS_TOKEN"] = os.getenv("META_GRAPH_ACCESS_TOKEN", "")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.instagram.publisher import publisher  # noqa: E402


def publish_reel_to_instagram(video_url: str, caption: str) -> str:
    """Container creation -> status polling -> feed publication. Returns post ID."""
    if not (video_url.startswith("http://") or video_url.startswith("https://")):
        raise ValueError(f"Invalid video_url '{video_url}': Meta requires a public HTTPS URL.")
    media_id = publisher.publish_reel(video_url, caption)
    print(f"REEL PUBLISHED SUCCESSFULLY! Post ID: {media_id}")
    return media_id


if __name__ == "__main__":
    import sys as _sys

    _url = _sys.argv[1] if len(_sys.argv) > 1 else "https://example.com/final_reel.mp4"
    _cap = _sys.argv[2] if len(_sys.argv) > 2 else "Test reel #reels"
    publish_reel_to_instagram(_url, _cap)
