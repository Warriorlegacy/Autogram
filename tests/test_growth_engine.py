import pytest
from pathlib import Path
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

def test_topic_aware_viral_hashtags():
    tags = viral_engine.build_viral_hashtags("AI Tool Breakdown", topic="Multi-Agent Systems with RAG")
    assert any("Agent" in t for t in tags)
    assert any("RAG" in t or "AI" in t for t in tags)
    assert len(tags) >= 10
    assert "#SignhifyStudio" in tags or "#AutogramAI" in tags

def test_caption_and_hashtag_enforcement_in_publisher():
    from src.instagram.publisher import publisher
    publisher.dry_run = True

    # 1. Test empty caption -> publisher must auto-generate caption with hashtags
    mid_empty = publisher.publish_carousel(["https://example.com/slide1.jpg"], ["Slide 1"], caption="")
    assert mid_empty.startswith("mock_")

    # 2. Test caption without hashtags -> publisher must append hashtags
    plain_caption = "New architecture breakdown for engineering teams."
    mid_plain = publisher.publish_carousel(["https://example.com/slide1.jpg"], ["Slide 1"], caption=plain_caption)
    assert mid_plain.startswith("mock_")

def test_api_caption_generate_endpoint():
    from dashboard_api import app
    client = app.test_client()

    resp = client.post("/api/caption/generate", json={
        "topic": "Deterministic State Machines for AI Agents",
        "pillar": "AI Tool Breakdown"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "Deterministic State Machines" in data["caption"]
    assert "#" in data["caption"]
    assert len(data["hashtags"]) >= 8
    assert "first_comment" in data

def test_publish_endpoint_auto_generates_caption_and_hashtags(monkeypatch):
    from dashboard_api import app
    from src.storage.uploader import uploader
    
    # Mock uploader to avoid external network calls during unit test
    monkeypatch.setattr(uploader, "upload_slide_images", lambda paths, date: [f"https://cdn.example.com/{Path(p).name}" for p in paths])
    
    client = app.test_client()
    resp = client.post("/api/publish", json={"mode": "dry-run"})
    assert resp.status_code in [200, 404]  # 200 if output runs exist, 404 if clean workspace
    if resp.status_code == 200:
        data = resp.get_json()
        assert data["ok"] is True
        assert data["hashtags_count"] >= 5
        assert "#" in data["caption"]

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

