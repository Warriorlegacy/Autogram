"""Instagram Reels publishing — Meta Graph API, opt-in, dry-run by default.

Three calls, in order:  POST /{ig-user-id}/media (media_type=REELS)  ->
poll GET /{container-id}?fields=status_code until FINISHED  ->
POST /{ig-user-id}/media_publish.

Meta fetches the video itself from `video_url`, so that URL must be public
https. This module uploads nothing and contacts Instagram only when
publish_reel(..., dry_run=False) runs with credentials present. Credentials
come from the environment only; tokens are never logged, printed, or written
to disk.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

GRAPH_HOST = "https://graph.facebook.com"
DEFAULT_API_VERSION = "v26.0"
HTTP_TIMEOUT = 30
CAPTION_MAX = 2200

# Meta's docs contradict themselves on the post cap (100 vs 50). The current
# Content Publishing guide says 100/rolling 24h and the live
# /content_publishing_limit endpoint agrees; the reference page's 50 is stale.
POSTS_PER_24H = 100
POLL_TIMEOUT = 600
POLL_INTERVAL = 10

# OAuth "your token is dead" codes -> credentials exit code, not a transport one.
AUTH_CODES = {102, 190, 463}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}

OUT_DIR = Path(__file__).parent / "output"


class PublishError(RuntimeError):
    """Publishing refused or failed. `code` is the CLI exit code."""

    code = 6


class CredentialsError(PublishError):
    """Credentials missing, or the token/account is not authorized."""

    code = 5


def _scrub(text: str, *secrets: str | None) -> str:
    for s in secrets:
        if s:
            text = text.replace(s, "<redacted>")
    return text


def credentials() -> dict:
    """Resolve Meta credentials from the environment. Names only in any error.

    Token preference is deliberate: a Page token is issued to the Page, not to a
    human login, and Meta documents long-lived Page tokens as having no
    expiration date. A User token dies with the owner's login session — a
    password change invalidates it (error 190 subcode 460) and there is no
    refresh path. So the Page token wins when both are present.

    Override with IG_PUBLISH_TOKEN_PREFERENCE=user to force the User token.
    """
    uid = os.environ.get("IG_USER_ID") or os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID") or ""
    page_token = os.environ.get("META_GRAPH_ACCESS_TOKEN") or ""
    user_token = os.environ.get("IG_ACCESS_TOKEN") or ""
    prefer = (os.environ.get("IG_PUBLISH_TOKEN_PREFERENCE") or "page").strip().lower()
    if prefer == "user":
        token, kind = (user_token or page_token), ("user" if user_token else "page")
    else:
        token, kind = (page_token or user_token), ("page" if page_token else "user")

    missing = []
    if not uid:
        missing += ["IG_USER_ID", "INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    if not token:
        missing += ["META_GRAPH_ACCESS_TOKEN", "IG_ACCESS_TOKEN"]
    if missing:
        raise CredentialsError(
            "Missing Instagram credentials — set one name from each pair: "
            + ", ".join(missing)
            + ". The account must be Professional (Business or Creator) and linked to a "
              "Facebook Page, with instagram_basic, instagram_content_publish and "
              "pages_read_engagement granted. Prefer META_GRAPH_ACCESS_TOKEN: a Page "
              "token has no expiration date and survives a Facebook password change, "
              "which permanently kills a User token."
        )
    version = (os.environ.get("META_API_VERSION") or DEFAULT_API_VERSION).strip()
    return {"ig_user_id": uid, "access_token": token, "token_kind": kind,
            "api_version": version if version.startswith("v") else f"v{version}"}


def _public_https(url: str, what: str) -> str:
    """Meta's crawler must be able to fetch this itself. Local paths cannot work."""
    u = (url or "").strip()
    parsed = urlparse(u)
    if parsed.scheme != "https" or not parsed.netloc:
        raise PublishError(
            f"{what} must be a public https:// URL. Meta fetches the file itself and "
            f"cannot read file:// paths, localhost, or private networks. Got: {u[:120]!r}. "
            "Pass --video-url, or set PUBLIC_CDN_BASE to a public HTTPS host."
        )
    if (parsed.hostname or "").lower() in LOCAL_HOSTS:
        raise PublishError(
            f"{what} must be a public https:// URL, but it points at {parsed.hostname} — "
            "Meta's crawler runs outside your machine and cannot reach it."
        )
    return u


def _error(resp, token) -> tuple[str, int, bool]:
    """(message, code, is_auth) from a Graph error body, with the token scrubbed."""
    try:
        err = (resp.json() or {}).get("error") or {}
        msg = _scrub(str(err.get("message") or err.get("type") or ""), token)[:300]
        code = int(err.get("code") or 0)
        return msg or "no message", code, code in AUTH_CODES or "OAuthException" in str(err.get("type", ""))
    except (ValueError, AttributeError, TypeError):
        return _scrub(resp.text[:300], token), 0, False


def _checked(resp, token):
    if resp.status_code != 200:
        msg, code, is_auth = _error(resp, token)
        err = (CredentialsError if is_auth else PublishError)(
            f"Meta returned HTTP {resp.status_code} (code {code}): {msg}")
        err.graph_code = code
        raise err
    return resp


def _post(url: str, data: dict, token: str | None = None):
    try:
        resp = requests.post(url, data=data, timeout=HTTP_TIMEOUT)
    except requests.RequestException as e:
        raise PublishError(f"network error calling Meta: {e}") from None
    return _checked(resp, token)


def _get(url: str, params: dict, token: str):
    try:
        resp = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
    except requests.RequestException as e:
        raise PublishError(f"network error calling Meta: {e}") from None
    return _checked(resp, token)


def token_health() -> dict:
    """Check the publishing token: valid? what kind? when does it expire?

    Read-only. Never raises for a bad token — returns ok=False so a scheduled
    job can alert instead of crashing. `expires_at == 0` means Meta reports no
    expiry (Page tokens and non-expiring System User tokens).
    """
    out = {"ok": False, "token_kind": None, "expires_at": None, "days_left": None,
           "never_expires": None, "expiry_known": False,
           "username": None, "media_count": None,
           "quota_used": None, "quota_total": POSTS_PER_24H, "error": None}
    try:
        creds = credentials()
    except CredentialsError as e:
        out["error"] = str(e)[:300]
        return out

    token, out["token_kind"] = creds["access_token"], creds.get("token_kind", "unknown")

    app_id = os.environ.get("META_APP_ID") or ""
    app_secret = os.environ.get("META_APP_SECRET") or ""
    if app_id and app_secret:
        try:
            info = _get(_endpoint(creds, "oauth/access_token_info"),
                        {"input_token": token,
                         "access_token": f"{app_id}|{app_secret}"}, token).json()
            exp = info.get("expires_at")
            # Meta: 0 means the token never expires. The field being ABSENT means
            # the endpoint did not report expiry (app-mode restriction) — that is
            # "unknown", never "never expires". Conflating them is a false all-clear.
            out["expires_at"] = exp
            out["expiry_known"] = "expires_at" in info
            out["never_expires"] = exp == 0 if out["expiry_known"] else None
            if out["expiry_known"] and isinstance(exp, (int, float)) and exp > 0:
                out["days_left"] = round((exp - time.time()) / 86400, 1)
        except PublishError as e:
            out["error"] = f"token_info failed: {str(e)[:200]}"

    try:
        acc = _get(_endpoint(creds, creds["ig_user_id"]),
                   {"fields": "username,media_count", "access_token": token}, token).json()
        out["ok"] = "error" not in acc
        out["username"] = acc.get("username")
        out["media_count"] = acc.get("media_count")
        if out["error"] is None and "error" in acc:
            out["error"] = str(acc["error"].get("message"))[:300]
    except PublishError as e:
        out["error"] = str(e)[:300]

    q = publishing_quota()
    if q:
        out["quota_used"] = q.get("quota_usage")
        if q.get("config", {}).get("quota_total"):
            out["quota_total"] = q["config"]["quota_total"]
    return out


def _endpoint(creds: dict, path: str) -> str:
    return f"{GRAPH_HOST}/{creds['api_version']}/{path}"


def container_payload(creds: dict, video_url: str, caption: str, cover_url: str = "") -> dict:
    """The exact POST /media body. Kept separate so dry-run prints what will be sent."""
    data = {"media_type": "REELS", "video_url": video_url,
            "caption": caption[:CAPTION_MAX], "share_to_feed": "true"}
    if cover_url:
        data["cover_url"] = cover_url
    return data


def preview_payload(creds: dict, video_url: str, caption: str, cover_url: str = "") -> dict:
    """Every request dry-run would make, with the token replaced. Never a real token."""
    uid = creds.get("ig_user_id") or "<unset: IG_USER_ID>"
    creds = {**creds, "api_version": creds.get("api_version") or DEFAULT_API_VERSION}
    base = _endpoint(creds, uid)
    return {
        "1. create container": {
            "POST": f"{base}/media",
            "data": {**container_payload(creds, video_url, caption, cover_url),
                     "access_token": "<redacted>"},
        },
        "2. poll container": {
            "GET": f"{base}/<container-id>",
            "params": {"fields": "status_code,status", "access_token": "<redacted>"},
            "until": "status_code == FINISHED",
        },
        "3. publish": {
            "POST": f"{base}/media_publish",
            "data": {"creation_id": "<container-id from step 1>", "access_token": "<redacted>"},
        },
    }


def create_container(video_url: str, caption: str, cover_url: str | None = None) -> str:
    """POST /{ig-user-id}/media with media_type=REELS. Returns the container id."""
    creds = credentials()
    video_url = _public_https(video_url, "video_url")
    if cover_url:
        cover_url = _public_https(cover_url, "cover_url")
    data = container_payload(creds, video_url, caption, cover_url or "")
    data["access_token"] = creds["access_token"]
    resp = _post(_endpoint(creds, f"{creds['ig_user_id']}/media"), data, creds["access_token"])
    cid = resp.json().get("id")
    if not cid:
        raise PublishError("container creation returned no id; nothing was uploaded to Instagram")
    return cid


def wait_for_container(cid: str, timeout: int = POLL_TIMEOUT, interval: int = POLL_INTERVAL,
                       creds: dict | None = None) -> str:
    """Poll status_code until FINISHED. Raises on ERROR/EXPIRED and on timeout.

    Processing happens at container creation, so a timeout here means Meta is
    still fetching: re-query this id rather than creating another container.
    """
    creds = creds or credentials()
    url = _endpoint(creds, cid)
    deadline = time.monotonic() + timeout
    while True:
        resp = _get(url, {"fields": "status_code,status",
                          "access_token": creds["access_token"]}, creds["access_token"])
        status = (resp.json() or {}).get("status_code")
        if status == "FINISHED":
            return status
        if status in ("ERROR", "EXPIRED"):
            detail = _scrub(str((resp.json() or {}).get("status") or ""), creds["access_token"])
            raise PublishError(f"container {cid} ended as {status}: {detail}")
        if time.monotonic() >= deadline:
            raise PublishError(
                f"container {cid} was still {status or 'unknown'} after {timeout}s. Meta is "
                "still processing it. Re-query this container id before creating another — "
                "a retry loop burns the 400/day container budget and containers expire in 24h."
            )
        time.sleep(interval)


def publishing_quota() -> dict | None:
    """GET /content_publishing_limit. None means 'unknown', never a hard failure."""
    try:
        creds = credentials()
        resp = _get(_endpoint(creds, f"{creds['ig_user_id']}/content_publishing_limit"),
                    {"fields": "quota_usage,config", "access_token": creds["access_token"]},
                    creds["access_token"])
        data = (resp.json() or {}).get("data") or []
        return data[0] if data else None
    except PublishError:
        return None


def _publish_container(creds: dict, cid: str) -> str:
    resp = _post(_endpoint(creds, f"{creds['ig_user_id']}/media_publish"),
                 {"creation_id": cid, "access_token": creds["access_token"]},
                 creds["access_token"])
    mid = resp.json().get("id")
    if not mid:
        raise PublishError("media_publish returned no id; the Reel is NOT published")
    return mid


def _record(out: Path, res: dict) -> dict:
    """The audit trail. Timestamp, ids, status, ok/error — never a token."""
    out.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "container_id": res.get("container_id"), "media_id": res.get("media_id"),
           "status": res.get("status"), "ok": bool(res.get("ok"))}
    if res.get("error"):
        row["error"] = str(res["error"])[:400]
    (out / "publish_result.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
    return res


def publish_reel(slug: str, video_url: str, caption: str, cover: str | None = None,
                 dry_run: bool = True, out_dir: Path | None = None) -> dict:
    """Create container -> wait -> publish. dry_run=True prints the payloads, sends nothing."""
    video_url = _public_https(video_url, "video_url")
    cover = _public_https(cover, "cover_url") if cover else ""
    caption = (caption or "").strip()
    if len(caption) > CAPTION_MAX:
        raise PublishError(f"caption is {len(caption)} chars; Meta caps Reels at {CAPTION_MAX}")
    out = Path(out_dir) if out_dir else OUT_DIR / slug

    try:
        creds: dict = credentials()
        auth: CredentialsError | None = None
    except CredentialsError as e:
        creds, auth = {}, e

    if dry_run:
        print("[publish] DRY RUN — no request sent. Payloads that would be sent:")
        print(json.dumps(preview_payload(creds, video_url, caption, cover), indent=2))
        if auth:
            print(f"[publish] credentials unresolved: {auth}")
        return _record(out, {"ok": True, "dry_run": True, "status": "DRY_RUN", "slug": slug,
                             "video_url": video_url, "container_id": None, "media_id": None,
                             "credentials": bool(creds)})

    if auth:
        raise auth

    cid = None
    try:
        quota = publishing_quota()
        used = int((quota or {}).get("quota_usage") or 0)
        print(f"[publish] rolling 24h quota: {used}/{POSTS_PER_24H} used")
        if quota and used >= POSTS_PER_24H:
            raise PublishError(f"quota exhausted ({used}/{POSTS_PER_24H}); refusing to publish")
        cid = create_container(video_url, caption, cover or None)
        print(f"[publish] container {cid} created; waiting for Meta to finish processing ...")
        wait_for_container(cid, creds=creds)
        media_id = _publish_container(creds, cid)
    except PublishError as e:
        _record(out, {"ok": False, "status": "FAILED", "slug": slug,
                      "container_id": cid, "media_id": None, "error": e})
        raise
    print(f"[publish] PUBLISHED slug={slug} media_id={media_id}")
    return _record(out, {"ok": True, "dry_run": False, "status": "PUBLISHED", "slug": slug,
                         "video_url": video_url, "container_id": cid, "media_id": media_id,
                         "credentials": True})