"""
Tests for the canonical pricing source of truth (data/pricing.json → src/auth/pricing.py).
"""
import json

import pytest

from src.auth.pricing import load_pricing, get_tiers, TIERS
from src.auth import pricing as pricing_module
from src.auth.licensing import generate_license, verify_license
from src.auth import user_manager


CANONICAL_PRICES = {"starter": 29, "growth": 79, "agency_pro": 199}


def test_pricing_json_exists_and_parses():
    raw = json.loads(pricing_module.PRICING_FILE.read_text(encoding="utf-8"))
    assert len(raw["tiers"]) == 3
    keys = {t["key"] for t in raw["tiers"]}
    assert keys == {"starter", "growth", "agency_pro"}


def test_loader_matches_json_prices():
    raw = json.loads(pricing_module.PRICING_FILE.read_text(encoding="utf-8"))
    tiers = get_tiers()
    for t in raw["tiers"]:
        assert tiers[t["key"]]["price_monthly"] == t["price_monthly"]
        assert tiers[t["key"]]["name"] == t["name"]


def test_canonical_price_set():
    tiers = get_tiers()
    for key, price in CANONICAL_PRICES.items():
        assert tiers[key]["price_monthly"] == price


def test_legacy_hardcoded_tiers_compat():
    """The module-level TIERS snapshot keeps the old shape consumers rely on."""
    for key in ("starter", "growth", "agency_pro", "owner"):
        assert key in TIERS
        assert "features" in TIERS[key]
        assert "limits" in TIERS[key]


def test_missing_pricing_file_falls_back_to_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(pricing_module, "PRICING_FILE", tmp_path / "nope.json")
    tiers = pricing_module.get_tiers()
    assert tiers["starter"]["price_monthly"] == 29
    assert tiers["agency_pro"]["price_monthly"] == 199


def test_corrupt_pricing_file_falls_back_to_defaults(tmp_path, monkeypatch):
    bad = tmp_path / "pricing.json"
    bad.write_text("{ not json !!", encoding="utf-8")
    monkeypatch.setattr(pricing_module, "PRICING_FILE", bad)
    tiers = pricing_module.get_tiers()
    assert tiers["growth"]["price_monthly"] == 79


def test_pricing_json_edit_reflects_in_loader(tmp_path, monkeypatch):
    custom = {
        "currency": "USD",
        "upi": {"id": "x@y", "payee_name": "T", "whatsapp_number": "1", "whatsapp_display": "1"},
        "tiers": [
            {"key": "starter", "price_monthly": 11, "name": "Starter X"},
            {"key": "growth", "price_monthly": 22, "name": "Growth X"},
            {"key": "agency_pro", "price_monthly": 33, "name": "Pro X"},
        ],
    }
    f = tmp_path / "pricing.json"
    f.write_text(json.dumps(custom), encoding="utf-8")
    monkeypatch.setattr(pricing_module, "PRICING_FILE", f)
    tiers = pricing_module.get_tiers()
    # Edited numbers win…
    assert tiers["starter"]["price_monthly"] == 11
    assert tiers["starter"]["name"] == "Starter X"
    # …while fields not present in JSON fall back to defaults (no KeyErrors downstream)
    assert "features" in tiers["starter"] and tiers["starter"]["features"]
    assert tiers["starter"]["limits"]["carousels_per_month"] == 30


def test_stripe_env_override(monkeypatch):
    monkeypatch.setenv("STRIPE_GROWTH_URL", "https://buy.stripe.com/test_growth")
    tiers = pricing_module.get_tiers()
    assert tiers["growth"]["stripe_url"] == "https://buy.stripe.com/test_growth"


def test_stripe_placeholder_env_urls_are_ignored(monkeypatch):
    """Legacy fake Stripe links baked into machine env vars must never poison checkout."""
    monkeypatch.setenv("STRIPE_STARTER_URL", "https://buy.stripe.com/starter_tier")
    monkeypatch.setenv("STRIPE_GROWTH_URL", "https://buy.stripe.com/growth_tier")
    monkeypatch.setenv("STRIPE_ENTERPRISE_URL", "https://buy.stripe.com/enterprise_tier")
    tiers = pricing_module.get_tiers()
    assert tiers["starter"]["stripe_url"] is None
    assert tiers["growth"]["stripe_url"] is None
    assert tiers["agency_pro"]["stripe_url"] is None


def test_license_enterprise_alias_mints_agency_pro():
    key = generate_license("Acme Corp", tier="enterprise", days=30)
    assert "-AGENCY_PRO-" in key
    result = verify_license(key)
    assert result["valid"] is True
    assert result["tier"] == "agency_pro"


def test_license_canonical_tiers_roundtrip():
    for tier in ("starter", "growth", "agency_pro"):
        key = generate_license("Round Trip Co", tier=tier, days=7)
        result = verify_license(key)
        assert result["valid"] is True
        assert result["tier"] == tier


def test_register_user_accepts_agency_pro_not_enterprise(tmp_path, monkeypatch):
    """'agency_pro' must register as-is; unknown 'enterprise' must not silently downgrade."""
    monkeypatch.setattr(user_manager, "DB_PATH", tmp_path / "test_auth.db")
    user_manager.user_manager.init_db()

    ok = user_manager.user_manager.register_user("pro_user", "pw123456!", tier="agency_pro")
    assert ok["ok"] is True
    assert ok["user"]["tier"] == "agency_pro"

    downgraded = user_manager.user_manager.register_user("ent_user", "pw123456!", tier="enterprise")
    assert downgraded["ok"] is True
    # Legacy 'enterprise' maps to agency_pro rather than silently becoming starter
    assert downgraded["user"]["tier"] == "agency_pro"


def test_api_auth_pricing_full_payload():
    from dashboard_api import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        res = client.get("/api/auth/pricing")
        assert res.status_code == 200
        data = res.get_json()
        assert data["ok"] is True
        assert data["currency"] == "USD"
        assert data["upi"]["id"]
        for key in ("starter", "growth", "agency_pro"):
            assert key in data["tiers"]
            assert data["tiers"][key]["price_monthly"] == CANONICAL_PRICES[key]


def test_api_issue_license_with_owner_key():
    """Owner key authorizes minting a REAL HMAC-signed key that verifies server-side."""
    from dashboard_api import app
    from src.auth.licensing import get_owner_key

    app.config["TESTING"] = True
    with app.test_client() as client:
        res = client.post("/api/auth/issue-license", json={
            "client": "Test Client Co",
            "tier": "agency_pro",
            "days": 30,
            "owner_key": get_owner_key(),
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["ok"] is True
        assert data["key"].startswith("AG-AGENCY_PRO-")

        result = verify_license(data["key"])
        assert result["valid"] is True
        assert result["tier"] == "agency_pro"
        assert result["client"] == "TESTCLIENT"  # slug capped at 10 chars


def test_api_issue_license_requires_auth():
    """Without owner key or admin session the endpoint must refuse."""
    from dashboard_api import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        res = client.post("/api/auth/issue-license", json={
            "client": "Freeloader", "tier": "growth", "days": 30,
        })
        assert res.status_code == 403
        assert res.get_json()["ok"] is False


def test_api_issue_license_requires_client_name():
    from dashboard_api import app
    from src.auth.licensing import get_owner_key

    app.config["TESTING"] = True
    with app.test_client() as client:
        res = client.post("/api/auth/issue-license", json={
            "client": "", "tier": "growth", "owner_key": get_owner_key(),
        })
        assert res.status_code == 400


def test_api_issue_license_days_clamped():
    """Days are clamped to 1..3650; garbage falls back to 30."""
    from dashboard_api import app
    from src.auth.licensing import get_owner_key

    app.config["TESTING"] = True
    with app.test_client() as client:
        res = client.post("/api/auth/issue-license", json={
            "client": "ClampTest", "tier": "starter", "days": 999999,
            "owner_key": get_owner_key(),
        })
        assert res.status_code == 200
        key = res.get_json()["key"]
        result = verify_license(key)
        assert result["valid"] is True
        # 3650 days ≈ 10 years out
        assert "2036" in result["expires_at"]
