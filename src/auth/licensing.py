"""
Cryptographic Licensing and Access Control for Autogram.
Ensures the Owner has 100% free unlimited access while clients must hold valid paid licenses.
Keys are verifiable deterministically and offline using HMAC-SHA256.
"""

import os
import hmac
import hashlib
import time
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Secret salt for HMAC signing (fallback default or configured via env)
DEFAULT_SALT = "autogram_master_monetization_secret_2026_salt"


def get_salt() -> str:
    from src.config import settings
    return getattr(settings, "autogram_secret_salt", None) or os.getenv("AUTOGRAM_SECRET_SALT", DEFAULT_SALT)


def get_owner_key() -> str:
    from src.config import settings
    return getattr(settings, "autogram_owner_key", None) or os.getenv("AUTOGRAM_OWNER_KEY", "autogram_owner_vip_2026")


def is_owner_key(key: Optional[str]) -> bool:
    """Checks whether the provided key matches the master Owner key."""
    if not key:
        return False
    configured_owner_key = get_owner_key()
    return hmac.compare_digest(key.strip(), configured_owner_key.strip())


def generate_license(client_name: str, tier: str = "growth", days: int = 30) -> str:
    """
    Generates a cryptographically signed client license key.
    Format: AG-{TIER}-{EXP_HEX}-{CLIENT_SLUG}-{SIG}
    """
    tier_clean = tier.strip().upper()
    # Canonical tiers: starter / growth / agency_pro (== legacy "ENTERPRISE" slug), plus internal owner.
    if tier_clean not in ["STARTER", "GROWTH", "AGENCY_PRO", "ENTERPRISE", "OWNER"]:
        tier_clean = "GROWTH"
    if tier_clean == "ENTERPRISE":
        tier_clean = "AGENCY_PRO"  # mint canonical slug so dashboard gates match backend tiers

    client_slug = "".join(c for c in client_name.upper() if c.isalnum())[:10]
    if not client_slug:
        client_slug = "CLIENT"

    # Expiration timestamp in seconds
    expire_timestamp = int(time.time()) + (days * 86400)
    exp_hex = hex(expire_timestamp)[2:].upper()

    payload = f"{tier_clean}:{exp_hex}:{client_slug}"
    salt = get_salt().encode("utf-8")
    sig = hmac.new(salt, payload.encode("utf-8"), hashlib.sha256).hexdigest()[:8].upper()

    return f"AG-{tier_clean}-{exp_hex}-{client_slug}-{sig}"


def verify_license(license_key: Optional[str]) -> Dict[str, Any]:
    """
    Verifies a license key or owner key.
    Returns dictionary with validation status and entitlements.
    """
    if not license_key or not license_key.strip():
        return {
            "valid": False,
            "is_owner": False,
            "tier": "none",
            "client": "anonymous",
            "reason": "Missing license key. Paid subscription required.",
            "expires_at": None,
        }

    key = license_key.strip()

    # 1. Check Owner Key (Master Admin 100% Free Bypass)
    if is_owner_key(key):
        return {
            "valid": True,
            "is_owner": True,
            "tier": "owner",
            "client": "Owner (VIP Master Access)",
            "reason": "Owner VIP Master Passcode verified. 100% free unlimited access.",
            "expires_at": "Permanent / Lifetime",
        }

    # 2. Check Cryptographic Client Key
    parts = key.split("-")
    if len(parts) != 5 or parts[0] != "AG":
        return {
            "valid": False,
            "is_owner": False,
            "tier": "none",
            "client": "unknown",
            "reason": "Invalid key format. Standard format is AG-{TIER}-{EXP}-{CLIENT}-{SIG}.",
            "expires_at": None,
        }

    _, tier_clean, exp_hex, client_slug, sig = parts

    # Validate HMAC signature (payload must use the tier string exactly as minted,
    # so legacy ENTERPRISE keys still pass — normalization happens after this check)
    payload = f"{tier_clean}:{exp_hex}:{client_slug}"
    salt = get_salt().encode("utf-8")
    expected_sig = hmac.new(salt, payload.encode("utf-8"), hashlib.sha256).hexdigest()[:8].upper()

    if not hmac.compare_digest(sig.upper(), expected_sig):
        return {
            "valid": False,
            "is_owner": False,
            "tier": "none",
            "client": client_slug,
            "reason": "Tampered or counterfeit license signature.",
            "expires_at": None,
        }

    # Normalize legacy tier slugs AFTER signature verification.
    if tier_clean == "ENTERPRISE":
        tier_clean = "AGENCY_PRO"

    # Check expiration date
    try:
        expire_timestamp = int(exp_hex, 16)
    except ValueError:
        return {
            "valid": False,
            "is_owner": False,
            "tier": "none",
            "client": client_slug,
            "reason": "Invalid expiration timestamp in key.",
            "expires_at": None,
        }

    current_timestamp = int(time.time())
    exp_datetime = datetime.fromtimestamp(expire_timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if current_timestamp > expire_timestamp:
        return {
            "valid": False,
            "is_owner": False,
            "tier": tier_clean.lower(),
            "client": client_slug,
            "reason": f"License expired on {exp_datetime}. Please renew your subscription.",
            "expires_at": exp_datetime,
        }

    return {
        "valid": True,
        "is_owner": False,
        "tier": tier_clean.lower(),
        "client": client_slug,
        "reason": f"Active {tier_clean} license verified for {client_slug}.",
        "expires_at": exp_datetime,
    }


def get_active_license_status() -> Dict[str, Any]:
    """Retrieves current execution environment license status from settings/env."""
    from src.config import settings

    # Check if Owner Key is configured
    owner_key = getattr(settings, "autogram_owner_key", None) or os.getenv("AUTOGRAM_OWNER_KEY")
    if owner_key:
        return verify_license(owner_key)

    # Check Client License Key
    client_key = getattr(settings, "autogram_client_key", None) or os.getenv("AUTOGRAM_CLIENT_KEY")
    return verify_license(client_key)


def main():
    parser = argparse.ArgumentParser(description="Autogram Licensing & Monetization Gate")
    parser.add_argument("--issue", action="store_true", help="Generate a new client license key")
    parser.add_argument("--client", type=str, default="Client", help="Client name or company name")
    parser.add_argument("--tier", type=str, default="growth", choices=["starter", "growth", "agency_pro", "enterprise", "owner"], help="Subscription tier (enterprise is a legacy alias for agency_pro)")
    parser.add_argument("--days", type=int, default=30, help="Duration in days (default: 30)")
    parser.add_argument("--verify", type=str, help="Verify an existing license key or owner key")
    parser.add_argument("--status", action="store_true", help="Check active environment license status")

    args = parser.parse_args()

    if args.issue:
        key = generate_license(args.client, args.tier, args.days)
        print("==================================================")
        print(" [AUTOGRAM] Generated Client License Key")
        print("==================================================")
        print(f" Client:     {args.client}")
        print(f" Tier:       {args.tier.upper()}")
        print(f" Duration:   {args.days} days")
        print(f" License Key: {key}")
        print("==================================================")
    elif args.verify:
        res = verify_license(args.verify)
        print(f"\nVerification Result: {'VALID [OK]' if res['valid'] else 'INVALID [REJECTED]'}")
        for k, v in res.items():
            print(f" - {k}: {v}")
    elif args.status:
        res = get_active_license_status()
        print("\nActive Environment Status:")
        for k, v in res.items():
            print(f" - {k}: {v}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
