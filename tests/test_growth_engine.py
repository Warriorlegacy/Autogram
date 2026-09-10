import pytest
from src.growth.viral_engine import viral_engine

def test_viral_hashtags_clustering():
    tags = viral_engine.build_viral_hashtags("AI Tool Breakdown")
    assert isinstance(tags, list)
    assert len(tags) >= 8
    assert all(t.startswith("#") for t in tags)
    # Ensure no duplicates
    assert len(tags) == len(set(tags))

def test_first_comment_generation():
    carousel = {
        "topic": "Autonomous AI Agent State Management",
        "pillar": "AI Tool Breakdown",
        "trigger_word": "SYSTEM",
        "slides": [
            {"slide_number": 1, "layout": "hook", "headline": "Stop Monolithic Prompts"},
            {"slide_number": 2, "layout": "standard", "headline": "State Machines Over Context Bloat"},
            {"slide_number": 3, "layout": "comparison", "headline": "Comparing BDI Agents with Monolithic LLMs"},
            {"slide_number": 4, "layout": "cta", "headline": "Get the Blueprint", "trigger_word": "SYSTEM"}
        ]
    }
    first_comment = viral_engine.generate_first_comment(carousel)
    assert "CORE ARCHITECTURE TAKEAWAYS" in first_comment
    assert 'Comment "SYSTEM"' in first_comment
    assert len(first_comment) > 50

def test_webhook_autopilot_auth():
    from dashboard_api import app
    client = app.test_client()

    # Unauthorized without key
    resp_unauth = client.post("/api/webhook/autopilot")
    assert resp_unauth.status_code == 401

    # Authorized with key
    resp_auth = client.post("/api/webhook/autopilot?key=autogram_owner_vip_2026&mode=dry-run")
    assert resp_auth.status_code == 200
    data = resp_auth.get_json()
    assert data["ok"] is True
    assert "started" in data["status"] or "running" in data["status"]
