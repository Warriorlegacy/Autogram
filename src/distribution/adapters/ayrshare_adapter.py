"""
Ayrshare adapter — optional 13-platform enterprise dispatch.

Activated ONLY when AYRSHARE_API_KEY is present in .env. Without it, reports
a clean capability status {"configured": false, ...} and never publishes.

Targets: Instagram, YouTube, LinkedIn, TikTok, Facebook, Threads, X,
Pinterest, Bluesky, Reddit, Telegram, Discord, Google Business Profile.
"""

import logging

from src.distribution.base_adapter import (
    PublishAdapter,
    PlatformCapabilities,
    CanonicalPost,
    PublishResult,
    ValidationResult,
    UnavailableMetrics,
)

logger = logging.getLogger(__name__)

AYRSHARE_POST_URL = "https://api.ayrshare.com/api/post"

# 13-platform target set from the Makerzz specification
SUPPORTED_DESTINATIONS = [
    "instagram", "youtube", "linkedin", "tiktok", "facebook", "threads",
    "x", "pinterest", "bluesky", "reddit", "telegram", "discord",
    "google_business",
]


class AyrshareAdapter(PublishAdapter):
    platform = "ayrshare"

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key

    def _get_key(self) -> str | None:
        if self._api_key:
            return self._api_key
        try:
            import os
            return os.environ.get("AYRSHARE_API_KEY")
        except Exception:
            return None

    def get_capabilities(self) -> PlatformCapabilities:
        return PlatformCapabilities(
            platform=self.platform,
            supports_text=True,
            supports_images=True,
            supports_video=True,
            supports_carousel=True,
            max_images=10,
            aspect_ratios=["1:1", "4:5", "9:16", "16:9"],
            max_caption_length=5000,
            supports_alt_text=True,
            scheduling_mode="provider",
            metrics=["likes", "comments", "shares", "impressions"],
        )

    def is_configured(self) -> bool:
        return bool(self._get_key())

    def configuration_status(self) -> dict:
        status = super().configuration_status()
        if not self.is_configured():
            status["reason"] = "Missing AYRSHARE_API_KEY"
        return status

    def validate_post(self, post: CanonicalPost) -> ValidationResult:
        result = self.validate_common(post, self.get_capabilities())
        if post.metadata.get("platforms"):
            unknown = set(post.metadata["platforms"]) - set(SUPPORTED_DESTINATIONS)
            if unknown:
                result.errors.append(f"Unsupported platforms: {', '.join(sorted(unknown))}")
                result.valid = False
        return result

    def publish(self, post: CanonicalPost) -> PublishResult:
        key = self._get_key()
        if not key:
            # Fail-closed clean status: never fake a publish
            return PublishResult(
                ok=False,
                error="Missing AYRSHARE_API_KEY — Ayrshare dispatch not configured.",
                receipt={"configured": False, "reason": "Missing AYRSHARE_API_KEY"},
            )

        validation = self.validate_post(post)
        if not validation.valid:
            return PublishResult(ok=False, error="; ".join(validation.errors))

        payload = {
            "post": post.caption,
            "platforms": post.metadata.get("platforms", SUPPORTED_DESTINATIONS),
            "mediaUrls": post.media_urls,
        }
        if post.scheduled_for:
            payload["scheduleDate"] = post.scheduled_for

        try:
            import requests
            resp = requests.post(
                AYRSHARE_POST_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
            resp.raise_for_status()
            body = resp.json()
            return PublishResult(
                ok=bool(body.get("status") in ("success", "pending")),
                remote_post_id=body.get("id"),
                receipt=body,
            )
        except Exception as e:
            logger.error(f"Ayrshare publish failed: {e}")
            return PublishResult(ok=False, error=str(e)[:300])

    def get_metrics(self, remote_post_id: str):
        key = self._get_key()
        if not key:
            return UnavailableMetrics(
                platform=self.platform,
                remote_post_id=remote_post_id,
                reason="Missing AYRSHARE_API_KEY",
            )
        try:
            import requests
            resp = requests.get(
                f"https://api.ayrshare.com/api/analytics/post/{remote_post_id}",
                headers={"Authorization": f"Bearer {key}"},
                timeout=20,
            )
            resp.raise_for_status()
            body = resp.json()
            return {"platform": self.platform, "remote_post_id": remote_post_id, **body}
        except Exception as e:
            return UnavailableMetrics(
                platform=self.platform,
                remote_post_id=remote_post_id,
                reason=str(e)[:200],
            )
