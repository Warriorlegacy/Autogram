"""
Multi-platform distribution adapters (Makerzz P7).

The content pipeline never knows platform-specific HTTP details. Each adapter:
  - reports capabilities dynamically
  - validates a canonical post against its capabilities BEFORE publishing
  - publishes only through official/documented APIs
  - reports metrics or explicit `unavailable` (never fabricated)
"""

from src.distribution.base_adapter import (
    PublishAdapter,
    PlatformCapabilities,
    CanonicalPost,
    PublishResult,
    ValidationResult,
    UnavailableMetrics,
)
from src.distribution.adapters.instagram_adapter import InstagramAdapter
from src.distribution.adapters.ayrshare_adapter import AyrshareAdapter


def get_adapters() -> dict:
    """Adapter registry: platform name -> adapter instance."""
    return {
        "instagram": InstagramAdapter(),
        "ayrshare": AyrshareAdapter(),
    }


__all__ = [
    "PublishAdapter",
    "PlatformCapabilities",
    "CanonicalPost",
    "PublishResult",
    "ValidationResult",
    "UnavailableMetrics",
    "InstagramAdapter",
    "AyrshareAdapter",
    "get_adapters",
]
