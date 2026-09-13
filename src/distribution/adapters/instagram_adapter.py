"""
Instagram adapter — wraps the EXISTING src/instagram/publisher.py into the
new P7 adapter interface WITHOUT modifying that module in any way.

Zero-disturbance guarantee: this is a pure decorator around the live publisher.
When credentials are absent or DRY_RUN is true, the underlying publisher
already behaves safely; this adapter just exposes the capability contract.
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


class InstagramAdapter(PublishAdapter):
    platform = "instagram"

    def __init__(self, dry_run: bool | None = None):
        self._dry_run_override = dry_run
        self._publisher = None

    def _get_publisher(self):
        if self._publisher is None:
            # Lazy import so the adapter can be used in unit tests without Meta
            from src.instagram.publisher import publisher
            self._publisher = publisher
            if self._dry_run_override is not None:
                self._publisher.dry_run = self._dry_run_override
        return self._publisher

    def get_capabilities(self) -> PlatformCapabilities:
        return PlatformCapabilities(
            platform=self.platform,
            supports_text=True,
            supports_images=True,
            supports_video=True,
            supports_carousel=True,
            max_images=10,
            aspect_ratios=["1:1", "4:5", "9:16"],
            max_caption_length=2200,
            supports_alt_text=True,
            scheduling_mode="app",
            metrics=["reach", "impressions", "likes", "comments", "saves", "shares"],
        )

    def is_configured(self) -> bool:
        try:
            from src.config import settings
            return bool(
                getattr(settings, "ig_user_id", None)
                and getattr(settings, "ig_access_token", None)
            )
        except Exception:
            return False

    def validate_post(self, post: CanonicalPost) -> ValidationResult:
        return self.validate_common(post, self.get_capabilities())

    def publish(self, post: CanonicalPost) -> PublishResult:
        caps = self.get_capabilities()
        validation = self.validate_post(post)
        if not validation.valid:
            return PublishResult(ok=False, error="; ".join(validation.errors))

        try:
            pub = self._get_publisher()
            if post.format in ("reel", "story", "short"):
                if len(post.media_urls) != 1:
                    return PublishResult(
                        ok=False,
                        error=f"{post.format} requires exactly 1 video URL.",
                    )
                if post.format == "story":
                    media_id = pub.publish_story(post.media_urls[0])
                else:
                    media_id = pub.publish_reel(post.media_urls[0], post.caption)
            else:
                media_id = pub.publish_carousel(
                    image_urls=post.media_urls,
                    alt_texts=post.alt_texts or None,
                    caption=post.caption,
                )

            if media_id and post.first_comment and not str(media_id).startswith("mock"):
                try:
                    pub.post_comment(media_id, post.first_comment)
                except Exception as comment_err:
                    logger.warning(f"First comment failed (saved locally): {comment_err}")

            return PublishResult(
                ok=bool(media_id),
                remote_post_id=str(media_id) if media_id else None,
                receipt={"platform": self.platform, "format": post.format},
            )
        except Exception as e:
            logger.error(f"Instagram publish failed: {e}")
            return PublishResult(ok=False, error=str(e)[:300])

    def get_metrics(self, remote_post_id: str):
        """Fetch insights directly via Meta Graph API (read-only)."""
        if str(remote_post_id).startswith("mock"):
            return UnavailableMetrics(
                platform=self.platform,
                remote_post_id=remote_post_id,
                reason="Dry-run/mock post — no live metrics",
            )
        try:
            import requests
            from src.config import settings
            api_version = getattr(settings, "meta_api_version", "v23.0")
            token = getattr(settings, "ig_access_token", None)
            if not token:
                return UnavailableMetrics(
                    platform=self.platform,
                    remote_post_id=remote_post_id,
                    reason="IG_ACCESS_TOKEN not configured",
                )
            url = f"https://graph.facebook.com/{api_version}/{remote_post_id}/insights"
            resp = requests.get(
                url,
                params={"metric": "reach,likes,comments,saves,shares", "access_token": token},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
            metrics = {
                row.get("name"): (row.get("values") or [{}])[0].get("value")
                for row in data
            }
            if not metrics:
                return UnavailableMetrics(
                    platform=self.platform,
                    remote_post_id=remote_post_id,
                    reason="No insights returned by platform",
                )
            return {"platform": self.platform, "remote_post_id": remote_post_id, **metrics}
        except Exception as e:
            return UnavailableMetrics(
                platform=self.platform,
                remote_post_id=remote_post_id,
                reason=str(e)[:200],
            )
