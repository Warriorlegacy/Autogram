"""
Canonical Pricing Loader (Single Source of Truth).

All tier definitions, prices, checkout links and payment details load from
data/pricing.json. Frontends fetch /api/auth/pricing; backend modules import
get_tiers() / TIERS from here. Env vars (STRIPE_STARTER_URL etc.) still
override per-tier Stripe links for deployment-specific checkout routing.

If data/pricing.json is missing or corrupt, built-in defaults are used so
the app never crashes — but a warning is logged.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PRICING_FILE = BASE_DIR / "data" / "pricing.json"

# Built-in fallback — mirrors data/pricing.json. Keep in sync if you edit the JSON.
_DEFAULT_TIERS: Dict[str, Dict[str, Any]] = {
    "starter": {
        "name": "Starter Autopilot",
        "price_monthly": 29,
        "price_annual": 290,
        "badge": "Entry",
        "tagline": "15 Carousels/mo · 1 Core Pillar",
        "features": [
            "30 Carousels / month",
            "Auto-Detect AI Models",
            "Standard Prompt Library (15+ prompts)",
            "3 Design Templates",
            "Manual Publishing Export",
            "Email Support",
        ],
        "limits": {
            "carousels_per_month": 30,
            "reels_per_month": 10,
            "connected_accounts": 1,
        },
        "stripe_url": None,
        "checkout_style": "upi",
        "cta_label": "Pay via UPI & WhatsApp",
    },
    "growth": {
        "name": "Growth Autopilot",
        "price_monthly": 79,
        "price_annual": 790,
        "badge": "Most Popular",
        "tagline": "30 Daily Carousels · Full Rotation",
        "features": [
            "120 Carousels / month",
            "40 AI Video Reels / month",
            "All AI Providers (OpenAI, Claude, Groq, Ollama, Custom)",
            "Full Prompt Library (30+ prompts)",
            "All 5 Carousel Design Templates",
            "7x Daily Automated Scheduler",
            "Direct Meta Graph API Publishing",
            "Priority Support",
        ],
        "limits": {
            "carousels_per_month": 120,
            "reels_per_month": 40,
            "connected_accounts": 3,
        },
        "stripe_url": None,
        "checkout_style": "upi",
        "cta_label": "Pay via UPI & WhatsApp",
    },
    "agency_pro": {
        "name": "Enterprise Swarm",
        "price_monthly": 199,
        "price_annual": 1990,
        "badge": "Uncapped",
        "tagline": "Multi-Account · Dedicated SLA",
        "features": [
            "Unlimited Carousels & Reels",
            "Custom Endpoints & Private LLM Proxies",
            "Full White-Label Watermark Removal",
            "Unlimited Client Workspaces",
            "Auto-DM Engine & Comment Funnels",
            "Dedicated Account Manager & SLA",
            "Custom CSS Design System Overrides",
        ],
        "limits": {
            "carousels_per_month": 99999,
            "reels_per_month": 99999,
            "connected_accounts": 10,
        },
        "stripe_url": None,
        "checkout_style": "contact",
        "cta_label": "Talk to Enterprise",
    },
    "owner": {
        "name": "Master Owner VIP",
        "price_monthly": 0,
        "price_annual": 0,
        "badge": "Admin Master",
        "tagline": "Root Access",
        "features": [
            "100% Unrestricted Root Master Access",
            "Zero System Rate Limits",
            "Direct Subprocess & Cloud Daemon Control",
            "License Key Minting & User Tier Management",
        ],
        "limits": {
            "carousels_per_month": 999999,
            "reels_per_month": 999999,
            "connected_accounts": 999,
        },
        "stripe_url": None,
        "checkout_style": "internal",
        "cta_label": "",
    },
}

# Env var name per tier key for Stripe checkout link overrides.
_STRIPE_ENV_OVERRIDES = {
    "starter": "STRIPE_STARTER_URL",
    "growth": "STRIPE_GROWTH_URL",
    "agency_pro": "STRIPE_ENTERPRISE_URL",  # legacy alias — enterprise == agency_pro
}

# Known non-functional placeholder URLs (old code defaults, sometimes baked into
# user-level env vars). These must never reach the frontend as real checkout links.
_PLACEHOLDER_STRIPE_URLS = {
    "https://buy.stripe.com/starter_tier",
    "https://buy.stripe.com/growth_tier",
    "https://buy.stripe.com/enterprise_tier",
}


def _load_raw_config() -> dict:
    if not PRICING_FILE.exists():
        logger.warning(
            "data/pricing.json not found — using built-in default pricing. "
            "Create the file to customize tiers without code changes."
        )
        return {}
    try:
        return json.loads(PRICING_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to parse data/pricing.json ({e}) — using built-in defaults.")
        return {}


def _apply_env_overrides(tiers: Dict[str, Dict[str, Any]]) -> None:
    """STRIPE_*_URL env vars override per-tier stripe_url from pricing.json.

    Known placeholder URLs (e.g. https://buy.stripe.com/starter_tier) are ignored
    so legacy machine-level env vars can't poison the checkout flow.
    """
    for key, env_name in _STRIPE_ENV_OVERRIDES.items():
        env_val = os.getenv(env_name, "").strip()
        if not env_val or key not in tiers:
            continue
        if env_val in _PLACEHOLDER_STRIPE_URLS:
            logger.warning(
                f"Ignoring placeholder {env_name}={env_val}. Set a real Stripe "
                f"Payment Link in data/pricing.json or a real env value."
            )
            continue
        tiers[key]["stripe_url"] = env_val


def load_pricing() -> Dict[str, Any]:
    """Load full pricing config: {"tiers": {...by key...}, "upi": {...}, "currency": "USD"}."""
    raw = _load_raw_config()

    tiers: Dict[str, Dict[str, Any]] = {}
    for tier_def in raw.get("tiers", []):
        key = tier_def.get("key")
        if not key:
            continue
        # Start from defaults so missing fields never KeyError downstream.
        merged = dict(_DEFAULT_TIERS.get(key, {}))
        merged.update({k: v for k, v in tier_def.items() if k != "key"})
        merged["key"] = key
        tiers[key] = merged

    if not tiers:
        tiers = {k: dict(v) for k, v in _DEFAULT_TIERS.items()}

    # The internal owner tier lives outside the sellable tiers array; merge it separately.
    owner = dict(_DEFAULT_TIERS["owner"])
    if isinstance(raw.get("owner"), dict):
        owner.update(raw["owner"])
    tiers["owner"] = owner

    _apply_env_overrides(tiers)

    return {
        "currency": raw.get("currency", "USD"),
        "upi": raw.get("upi", {
            "id": "6202442690@jio",
            "payee_name": "Autogram AI",
            "whatsapp_number": "916202442690",
            "whatsapp_display": "+91 6202442690",
        }),
        "tiers": tiers,
    }


def get_tiers() -> Dict[str, Dict[str, Any]]:
    """Public API: tier definitions keyed by tier key (starter/growth/agency_pro/owner)."""
    return load_pricing()["tiers"]


# Backwards-compatible module-level snapshot, same shape as the old hardcoded TIERS
# in user_manager.py. Imported by dashboard_api.py. Note: env Stripe overrides are
# applied at import time; per-request freshness is available via get_tiers().
TIERS: Dict[str, Dict[str, Any]] = get_tiers()


def get_upi_config() -> Dict[str, str]:
    return load_pricing()["upi"]


if __name__ == "__main__":
    import pprint
    pprint.pprint(load_pricing())
