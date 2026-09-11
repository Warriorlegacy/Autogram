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
