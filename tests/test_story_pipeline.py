import json
from pathlib import Path
from unittest.mock import patch
import pytest
from PIL import Image

from src.instagram.publisher import InstagramPublisher, publisher
from src.content.generator import generator
from renderer.render import CarouselRenderer
from renderer.validate import STORY_TARGET_WIDTH, STORY_TARGET_HEIGHT, validate_image_file
import dashboard_api

@pytest.fixture
def client():
    dashboard_api.app.config["TESTING"] = True
    with dashboard_api.app.test_client() as client:
        yield client

def test_publisher_story_methods():
    """Verify create_story_container and publish_story operate correctly in dry-run mode."""
    pub = InstagramPublisher(dry_run=True)
    cntr_id = pub.create_story_container("https://example.com/story.jpg")
    assert cntr_id.startswith("mock_story_cntr_")

    media_id = pub.publish_story("https://example.com/story.jpg")
    assert media_id.startswith("mock_published_media_")

    # In live mode, invalid URL must raise ValueError
    pub_live = InstagramPublisher(dry_run=False)
    pub_live._forced_dry_run = False
    pub_live.user_id = "12345"
    pub_live.token = "fake_token"
    with pytest.raises(ValueError, match="Invalid image_url"):
        pub_live.create_story_container("invalid-relative-path.jpg")

def test_story_content_generation():
    """Verify generator.generate_story_content creates high-signal story structure."""
    topic = "Context Caching Architecture & 90% Cost Reduction"
    pillar = "Tech Explainer"
    story_data = generator.generate_story_content(topic, pillar)

    assert "headline" in story_data
    assert story_data["headline"] == topic
    assert story_data["badge"] == "SYSTEMS BLUEPRINT"
    assert "metric_value" in story_data
    assert len(story_data["takeaways"]) >= 2
    assert "cta_text" in story_data

def test_story_image_rendering(tmp_path):
    """Verify Playwright renders exact 1080x1920 vertical JPEG slide."""
    renderer = CarouselRenderer()
    story_data = {
        "topic": "Zero-Touch Production Agent Testing",
        "pillar": "AI Tool Breakdown",
        "headline": "Zero-Touch Production Agent Testing",
        "badge": "AI STACK BREAKDOWN",
        "metric_value": "10x",
        "metric_label": "Throughput vs Monolithic Pipelines",
        "takeaways": [
            {"bold": "Isolated Reasoning", "text": "Eliminates cascading state drift."},
            {"bold": "Deterministic Rules", "text": "Fail-closed gates protect public publishing."}
        ],
        "code_command": "pip install autogram-engine",
        "cta_text": "Tap Link in Bio for Architecture",
        "theme": "obsidian"
    }

    out_file = tmp_path / "test_rendered_story.jpg"
    rendered_path = renderer.render_story(story_data, out_file)
    assert Path(rendered_path).exists()

    val = validate_image_file(rendered_path, expected_width=STORY_TARGET_WIDTH, expected_height=STORY_TARGET_HEIGHT)
    assert val["valid"] is True
    assert val["width"] == 1080
    assert val["height"] == 1920

    with Image.open(rendered_path) as img:
        assert img.size == (1080, 1920)
        assert img.format in ["JPEG", "JPG"]

def test_schedule_json_has_seven_story_slots_and_queue():
    """Verify data/schedule.json has 7 story slots and 7 queued story postings."""
    sched_path = Path("data/schedule.json")
    assert sched_path.exists()

    data = json.loads(sched_path.read_text(encoding="utf-8"))
    assert "story_slots" in data
    assert len(data["story_slots"]) == 7

    story_queue_items = [q for q in data.get("queue", []) if q.get("format") == "story" or str(q.get("id")).startswith("STORY")]
    assert len(story_queue_items) >= 7

def test_api_publish_story_endpoint(client):
    """Verify POST /api/publish/story returns valid story manifest in dry-run mode."""
    res = client.post("/api/publish/story", json={
        "topic": "Unit Test Story Publishing Topic",
        "pillar": "AI Tool Breakdown",
        "mode": "dry-run"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["format"] == "story"
    assert data["mode"] == "dry-run"
    assert "media_id" in data
    assert data["headline"] == "Unit Test Story Publishing Topic"

def test_execute_queued_story_item(client):
    """Verify executing a queued story item passes content_format='story'."""
    with dashboard_api.pipeline_lock:
        dashboard_api.pipeline_status = "idle"

    sched = dashboard_api.read_schedule()
    queue = sched.setdefault("queue", [])
    test_id = "STORY-UNIT-TEST-1"
    sched["queue"] = [q for q in queue if q.get("id") != test_id]
    sched["queue"].insert(0, {
        "id": test_id,
        "topic": "Automated Unit Test Scheduled Story",
        "pillar": "Tech Explainer",
        "format": "story",
        "mode": "dry-run",
        "status": "QUEUED",
        "scheduled_time": "2026-09-12T15:00:00"
    })
    dashboard_api.write_schedule(sched)

    with patch("dashboard_api.run_pipeline_subprocess", return_value=True) as mock_subproc:
        res = client.post(f"/api/schedule/{test_id}/execute")
        assert res.status_code == 200
        data = res.get_json()
        assert data["ok"] is True
        assert data["item"]["id"] == test_id
        mock_subproc.assert_called_once()
        _, kwargs = mock_subproc.call_args
        assert kwargs.get("content_format") == "story"
        assert kwargs.get("topic") == "Automated Unit Test Scheduled Story"

    # Cleanup
    sched = dashboard_api.read_schedule()
    sched["queue"] = [q for q in sched.get("queue", []) if q.get("id") != test_id]
    dashboard_api.write_schedule(sched)
