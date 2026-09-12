import pytest
import json
from dashboard_api import app
from src.auth.user_manager import user_manager, hash_password, verify_password

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_admin_user_seeded():
    """Verify master admin user signhify.studio exists with correct credentials."""
    user = user_manager.authenticate_user("signhify.studio", "Piyushrajput#1")
    assert user.get("ok") is True
    assert user["user"]["username"] == "signhify.studio"
    assert user["user"]["role"] == "admin"
    assert user["user"]["tier"] == "owner"
    assert "token" in user

def test_api_auth_login_success(client):
    res = client.post("/api/auth/login", json={
        "username": "signhify.studio",
        "password": "Piyushrajput#1"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["user"]["role"] == "admin"
    assert "token" in data

def test_api_auth_login_failure(client):
    res = client.post("/api/auth/login", json={
        "username": "signhify.studio",
        "password": "wrong_password"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["ok"] is False

def test_api_auth_signup_and_me(client):
    unique_user = f"tester_{hash(client) % 100000}"
    res = client.post("/api/auth/signup", json={
        "username": unique_user,
        "password": "password123!",
        "email": f"{unique_user}@example.com",
        "tier": "growth"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["user"]["username"] == unique_user
    assert data["user"]["tier"] == "growth"
    token = data["token"]

    # Verify /api/auth/me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["ok"] is True
    assert me_data["user"]["username"] == unique_user

def test_api_auth_pricing(client):
    res = client.get("/api/auth/pricing")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "starter" in data["tiers"]
    assert "growth" in data["tiers"]
    assert "agency_pro" in data["tiers"]

def test_api_providers_get(client):
    res = client.get("/api/providers")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "presets" in data
    assert "openai" in data["presets"]
    assert "gemini" in data["presets"]
    assert "groq" in data["presets"]
    assert "image_models" in data
    assert "video_models" in data

def test_api_providers_detect_models_missing_url(client):
    res = client.post("/api/providers/detect-models", json={})
    assert res.status_code == 400

def test_api_prompts_library(client):
    res = client.get("/api/prompts")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "categories" in data
    assert len(data["categories"]) > 0

def test_api_templates_catalog(client):
    res = client.get("/api/templates")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "carousel_templates" in data
    assert "video_reel_templates" in data
    assert len(data["carousel_templates"]) >= 5

    # Verify double /api/api/ normalization works transparently
    res_double = client.get("/api/api/templates")
    assert res_double.status_code == 200
    assert res_double.get_json()["ok"] is True

def _admin_token(client):
    res = client.post("/api/auth/login", json={
        "username": "signhify.studio",
        "password": "Piyushrajput#1"
    })
    assert res.status_code == 200
    return res.get_json()["token"]

def test_api_auth_users_regression(client):
    """Regression: /api/auth/users must not crash (list_all_users bug)."""
    token = _admin_token(client)
    res = client.get("/api/auth/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert any(u["username"] == "signhify.studio" for u in data["users"])

def test_api_admin_users_alias(client):
    """/api/admin/users alias: 403 anon, 200 for admin."""
    anon = client.get("/api/admin/users")
    assert anon.status_code == 403
    token = _admin_token(client)
    res = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["ok"] is True

def test_api_providers_test_validation(client):
    res = client.post("/api/providers/test", json={})
    assert res.status_code == 400
    res2 = client.post("/api/providers/test", json={"base_url": "https://api.openai.com/v1"})
    assert res2.status_code == 400  # model still required

def test_api_generate_image_validation(client):
    res = client.post("/api/generate/image", json={})
    assert res.status_code == 400
    assert res.get_json()["ok"] is False

def test_api_auth_logout(client):
    """Logout clears session token."""
    token = _admin_token(client)
    res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True

def test_api_non_admin_users_forbidden(client):
    """Non-admin users cannot list all users."""
    # Create a non-admin user
    unique_user = f"nonadmin_{hash(client) % 100000}"
    signup = client.post("/api/auth/signup", json={
        "username": unique_user,
        "password": "testpass123!",
        "tier": "starter"
    })
    token = signup.get_json()["token"]
    res = client.get("/api/auth/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403

def test_api_providers_set_active(client):
    """Setting active provider works (requires auth)."""
    token = _admin_token(client)
    res = client.post("/api/providers/set-active", json={
        "provider_id": "openai",
        "model_id": "gpt-4o"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True

def test_api_health(client):
    """Health endpoint returns status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] in ("ok", "healthy")

def test_themes_css_landing():
    """Verify all 5 theme presets are defined in landing.css."""
    import pathlib
    css = pathlib.Path("css/landing.css").read_text(encoding="utf-8")
    for theme in ["cyberpunk", "neumorphic", "swiss-light", "bento-grid"]:
        assert f'data-theme="{theme}"' in css, f"Missing theme: {theme}"

def test_themes_css_components():
    """Verify component overrides exist for all themes."""
    import pathlib
    css = pathlib.Path("css/components.css").read_text(encoding="utf-8")
    for theme in ["cyberpunk", "neumorphic", "swiss-light", "bento-grid"]:
        assert f'[data-theme="{theme}"]' in css, f"Missing component overrides for: {theme}"

def test_premium_js_has_tilt():
    """Verify premium.js includes dashboard cards in tilt selector."""
    import pathlib
    js = pathlib.Path("js/premium.js").read_text(encoding="utf-8")
    assert "doppel-shell" in js
    assert "platform-tile" in js
