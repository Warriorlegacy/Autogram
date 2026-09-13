"""
Abstract PublishAdapter protocol (Makerzz P7 base).

Canonical post -> platform transformation layer. The pipeline calls only
this interface; platform-specific HTTP lives inside each adapter.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class PlatformCapabilities:
    """Dynamic capability report. Validate per connection, never assume."""

    platform: str
    supports_text: bool = True
    supports_images: bool = True
    supports_video: bool = True
    supports_carousel: bool = False
    max_images: int | None = None
    max_video_bytes: int | None = None
    aspect_ratios: list[str] = field(default_factory=lambda: ["1:1", "4:5"])
    max_caption_length: int | None = None
    supports_alt_text: bool = False
    scheduling_mode: str = "none"  # app | provider | none
    metrics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "supports_text": self.supports_text,
            "supports_images": self.supports_images,
            "supports_video": self.supports_video,
            "supports_carousel": self.supports_carousel,
            "max_images": self.max_images,
            "max_video_bytes": self.max_video_bytes,
            "aspect_ratios": self.aspect_ratios,
            "max_caption_length": self.max_caption_length,
            "supports_alt_text": self.supports_alt_text,
            "scheduling_mode": self.scheduling_mode,
            "metrics": self.metrics,
        }


@dataclass
class CanonicalPost:
    """Platform-agnostic post payload (no platform-specific fields)."""

    format: str  # carousel | reel | story | short | text
    caption: str
    media_urls: list[str] = field(default_factory=list)
    alt_texts: list[str] = field(default_factory=list)
    first_comment: str | None = None
    scheduled_for: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class PublishResult:
    ok: bool
    remote_post_id: str | None = None
    receipt: dict = field(default_factory=dict)
    error: str | None = None


@dataclass
class UnavailableMetrics:
    """Explicit unavailable marker — never fabricate metrics."""

    platform: str
    remote_post_id: str
    availability: str = "unavailable"
    reason: str = "Metrics not returned by platform API"

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "remote_post_id": self.remote_post_id,
            "availability": self.availability,
            "reason": self.reason,
        }


class PublishAdapter(ABC):
    """Base protocol for every distribution adapter."""

    platform: str = "abstract"

    @abstractmethod
    def get_capabilities(self) -> PlatformCapabilities: ...

    @abstractmethod
    def is_configured(self) -> bool: ...

    def configuration_status(self) -> dict:
        """Clean capability status for the dashboard (never leaks secrets)."""
        return {
            "platform": self.platform,
            "configured": self.is_configured(),
            "capabilities": self.get_capabilities().to_dict(),
        }

    @abstractmethod
    def validate_post(self, post: CanonicalPost) -> ValidationResult: ...

    @abstractmethod
    def publish(self, post: CanonicalPost) -> PublishResult: ...

    @abstractmethod
    def get_metrics(self, remote_post_id: str):
        """Return a metrics dict or UnavailableMetrics. Never fabricate."""
        ...

    def validate_common(self, post: CanonicalPost, caps: PlatformCapabilities) -> ValidationResult:
        """Shared validation against a capability object."""
        errors: list[str] = []
        warnings: list[str] = []

        if not post.caption and caps.supports_text:
            warnings.append("Post has empty caption.")
        if caps.max_caption_length and len(post.caption) > caps.max_caption_length:
            errors.append(
                f"Caption exceeds {caps.max_caption_length} chars ({len(post.caption)})."
            )
        if not post.media_urls and post.format != "text":
            errors.append(f"Format '{post.format}' requires media but none provided.")
        if post.format == "carousel":
            if not caps.supports_carousel:
                errors.append(f"{self.platform} does not support carousel posts.")
            elif caps.max_images and len(post.media_urls) > caps.max_images:
                errors.append(
                    f"Carousel has {len(post.media_urls)} images; max is {caps.max_images}."
                )
        if post.format in ("reel", "story", "short") and not caps.supports_video:
            errors.append(f"{self.platform} does not support video posts.")
        if caps.supports_alt_text and post.alt_texts and len(post.alt_texts) != len(post.media_urls):
            warnings.append("Alt-text count does not match media count.")

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
