"""
Tests for Autogram Licensing and Access Gate.
Verifies Owner Free VIP Bypass and Cryptographic Client Monetization.
"""

import pytest
import time
from src.auth.licensing import (
    is_owner_key,
    generate_license,
    verify_license,
    get_active_license_status
)
from src.config import settings


def test_owner_key_bypass():
    """Verify system owner key grants 100% free permanent access."""
    owner_key = settings.autogram_owner_key
    assert is_owner_key(owner_key) is True
    
    result = verify_license(owner_key)
    assert result["valid"] is True
    assert result["is_owner"] is True
    assert result["tier"] == "owner"
    assert result["expires_at"] == "Permanent / Lifetime"


def test_missing_or_blank_key():
    """Verify missing key is rejected with subscription required message."""
    res_none = verify_license(None)
    assert res_none["valid"] is False
    assert "subscription required" in res_none["reason"].lower()

    res_empty = verify_license("")
    assert res_empty["valid"] is False


def test_client_license_generation_and_validation():
    """Verify generating and validating client licenses for canonical tiers."""
    for tier in ["starter", "growth", "agency_pro"]:
        key = generate_license("Acme Labs", tier=tier, days=30)
        assert key.startswith(f"AG-{tier.upper()}-")

        result = verify_license(key)
        assert result["valid"] is True
        assert result["is_owner"] is False
        assert result["tier"] == tier
        assert result["client"] == "ACMELABS"


def test_legacy_enterprise_key_still_validates_as_agency_pro():
    """Legacy keys minted with the ENTERPRISE slug remain valid and map to agency_pro."""
    # New keys mint the canonical slug
    key = generate_license("Legacy Client", tier="enterprise", days=30)
    assert key.startswith("AG-AGENCY_PRO-")

    # Simulate a genuinely legacy key: signed over the ENTERPRISE payload
    import time, hmac as hmac_mod, hashlib
    from src.auth.licensing import get_salt
    slug = "LEGACYCLT"
    exp_hex = hex(int(time.time()) + (30 * 86400))[2:].upper()
    sig = hmac_mod.new(get_salt().encode(), f"ENTERPRISE:{exp_hex}:{slug}".encode(), hashlib.sha256).hexdigest()[:8].upper()
    legacy_key = f"AG-ENTERPRISE-{exp_hex}-{slug}-{sig}"

    result = verify_license(legacy_key)
    assert result["valid"] is True
    assert result["tier"] == "agency_pro"


def test_tampered_license_signature():
    """Verify modifying any character in a key triggers signature rejection."""
    key = generate_license("TestClient", tier="growth", days=30)
    # Alter the last character of the signature
    tampered_sig = "0" if key[-1] != "0" else "1"
    tampered_key = key[:-1] + tampered_sig
    
    result = verify_license(tampered_key)
    assert result["valid"] is False
    assert "counterfeit" in result["reason"].lower() or "signature" in result["reason"].lower()


def test_expired_license_key():
    """Verify expired license key is rejected."""
    # Issue a key with -1 days (already expired in the past)
    key = generate_license("OldClient", tier="starter", days=-1)
    result = verify_license(key)
    assert result["valid"] is False
    assert "expired" in result["reason"].lower()


def test_active_environment_status():
    """Verify get_active_license_status recognizes the configured owner key."""
    status = get_active_license_status()
    assert status["valid"] is True
    assert status["is_owner"] is True
