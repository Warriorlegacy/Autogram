#!/usr/bin/env python3
"""
instagram_autoposter.py — post to Instagram via the Graph API using the
token already stored as repo secrets (Autogram has IG_ACCESS_TOKEN +
IG_USER_ID + INSTAGRAM_BUSINESS_ACCOUNT_ID).

Flow (standard IG Content Publishing API):
  1. POST /{ig-user-id}/media  {image_url, caption, access_token}  -> creation_id
  2. POST /{ig-user-id}/media_publish  {creation_id, access_token} -> media id

Safety: dry-run by default (IG_DRY_RUN=1). Set IG_DRY_RUN=0 to actually post.
Never prints the token. stdlib only (urllib).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.facebook.com"


def _token() -> str:
    t = os.getenv("IG_ACCESS_TOKEN", "").strip()
    if not t:
        raise RuntimeError("IG_ACCESS_TOKEN not set")
    return t


def _ig_id() -> str:
    return os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "").strip() or os.getenv("IG_USER_ID", "").strip()


def _ver() -> str:
    return os.getenv("META_API_VERSION", "v22.0").strip() or "v22.0"


def _dry() -> bool:
    return os.getenv("IG_DRY_RUN", "1").strip() not in ("0", "false", "False")


def _req(method: str, path: str, params: dict) -> dict:
    url = f"{GRAPH}/{_ver()}/{path}"
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"IG Graph API {e.code}: {body[:400]}")


def publish_photo(image_url: str, caption: str = "") -> dict:
    if not image_url:
        raise ValueError("image_url required")
    ig = _ig_id()
    if not ig:
        raise RuntimeError("IG_USER_ID / INSTAGRAM_BUSINESS_ACCOUNT_ID not set")
    tok = _token()
    if _dry():
        print(f"[dry-run] publish_photo ig={ig} image_url={image_url[:120]} caption={caption[:80]!r}")
        return {"dry_run": True}

    creation = _req("POST", f"{ig}/media", {
        "image_url": image_url,
        "caption": caption,
        "access_token": tok,
    })
    creation_id = creation.get("id")
    if not creation_id:
        raise RuntimeError(f"media create failed: {creation}")
    # Poll until status FINISHED (can take 10-60s)
    for _ in range(12):
        st = _req("GET", f"{creation_id}", {
            "fields": "status_code,status",
            "access_token": tok,
        })
        if st.get("status_code") == "FINISHED":
            break
        time.sleep(5)
    published = _req("POST", f"{ig}/media_publish", {
        "creation_id": creation_id,
        "access_token": tok,
    })
    return {"creation_id": creation_id, "media_id": published.get("id"), "status": "published"}


def self_test() -> None:
    """No-network check: imports + env presence + dry-run default."""
    import importlib
    importlib.reload(sys.modules[__name__]) if False else None
    print("IG autoposter: imports OK")
    print(f"  IG_ACCESS_TOKEN: {'SET' if os.getenv('IG_ACCESS_TOKEN') else 'MISSING'}")
    print(f"  IG_USER_ID/BIZ_ID: {os.getenv('IG_USER_ID') or os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID') or 'MISSING'}")
    print(f"  IG_DRY_RUN: {os.getenv('IG_DRY_RUN', '1')} -> {'dry-run (safe)' if _dry() else 'LIVE'}")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        raise SystemExit(0)
    image = os.getenv("IG_IMAGE_URL", "")
    caption = os.getenv("IG_CAPTION", "")
    if not image:
        print("IG_IMAGE_URL not set — nothing to post (set IG_DRY_RUN=0 to go live)")
        raise SystemExit(0)
    try:
        res = publish_photo(image, caption)
        print(json.dumps(res))
    except RuntimeError as e:
        print(f"ERROR: {e}")
        raise SystemExit(1)
