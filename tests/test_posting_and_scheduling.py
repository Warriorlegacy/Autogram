import json
import pytest
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import dashboard_api
from src.storage.uploader import uploader
from src.instagram.publisher import publisher

@pytest.fixture
def client():
    dashboard_api.app.config["TESTING"] = True
    with dashboard_api.app.test_client() as client:
        yield client

def test_get_output_runs_prioritizes_dated_runs():
    runs = dashboard_api.get_output_runs()
    assert isinstance(runs, list)
    assert len(runs) > 0
    # Top runs should be dated YYYY-MM-DD
    first_run = runs[0]
    import re
    assert re.match(r"^\d{4}-\d{2}-\d{2}", first_run["date"]), f"First run {first_run['date']} should be YYYY-MM-DD"
    assert first_run["slides_count"] > 0

def test_api_publish_dry_run_instant(client):
    # Ensure publisher forced dry run for test safety
    publisher._forced_dry_run = True
    res = client.post("/api/publish", json={"mode": "dry-run"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "mock_published_media_" in str(data.get("media_id"))
    assert data.get("status") == "SIMULATED_PUBLISH"
    assert data.get("hashtags_count") > 0
    assert data.get("slides_count") > 0

def test_api_publish_with_custom_caption(client):
    publisher._forced_dry_run = True
    custom_cap = "Custom Viral Post Hook\n\nSwipe to see implementation.\n\n#AIAutomation #Tech"
    res = client.post("/api/publish", json={"mode": "dry-run", "caption": custom_cap})
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "Custom Viral Post Hook" in data["caption"]
    assert data["hashtags_count"] >= 2

def test_api_schedule_execute_endpoint(client):
    # Seed a queue item
    sched = dashboard_api.read_schedule()
    queue = sched.setdefault("queue", [])
    test_id = "SCH-TEST-999"
    # Remove if existing
    sched["queue"] = [q for q in queue if q.get("id") != test_id]
    sched["queue"].insert(0, {
        "id": test_id,
        "topic": "Automated Unit Test Scheduled Post",
        "pillar": "Tech Explainer",
        "mode": "dry-run",
        "status": "QUEUED",
        "scheduled_time": "2026-09-12T12:00:00"
    })
    dashboard_api.write_schedule(sched)

    # Reset pipeline_status to idle in case previous async tests set it to running
    with dashboard_api.pipeline_lock:
        dashboard_api.pipeline_status = "idle"

    # Mock run_pipeline_subprocess so we don't spawn full external process in unit test
    with patch("dashboard_api.run_pipeline_subprocess", return_value=True) as mock_subproc:
        res = client.post(f"/api/schedule/{test_id}/execute")
        assert res.status_code == 200
        data = res.get_json()
        assert data["ok"] is True
        assert data["item"]["id"] == test_id
        assert data["item"]["status"] == "RUNNING"
        mock_subproc.assert_called_once()
        _, kwargs = mock_subproc.call_args
        assert kwargs.get("topic") == "Automated Unit Test Scheduled Post"
        assert kwargs.get("pillar") == "Tech Explainer"
        assert kwargs.get("queue_id") == test_id

    # Clean up
    sched = dashboard_api.read_schedule()
    sched["queue"] = [q for q in sched.get("queue", []) if q.get("id") != test_id]
    dashboard_api.write_schedule(sched)

def test_api_scheduler_toggle(client):
    res = client.post("/api/scheduler/toggle", json={"enable": True})
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["scheduler_enabled"] is True
    assert data["scheduler_running"] is True

    # Toggle off
    res_off = client.post("/api/scheduler/toggle", json={"enable": False})
    assert res_off.status_code == 200
    data_off = res_off.get_json()
    assert data_off["scheduler_enabled"] is False

    # Re-enable for system health
    client.post("/api/scheduler/toggle", json={"enable": True})

def test_uploader_dry_run_and_render_fallback():
    sample_images = ["output/sample/slide_01.jpg", "output/sample/slide_02.jpg"]
    # 1. Test dry_run produces instant URLs without network
    urls = uploader.upload_slide_images(sample_images, "sample", dry_run=True)
    assert len(urls) == 2
    assert all(u.startswith("http") for u in urls)
    assert all("slide_0" in u for u in urls)

    # 2. Test fallback to public CDN base when cloud hosts fail
    with patch.object(uploader, "_upload_to_freeimage", side_effect=Exception("CDN timeout")):
        with patch.object(uploader, "_upload_to_catbox", side_effect=Exception("CDN error")):
            with patch.object(uploader, "_upload_to_litterbox", side_effect=Exception("CDN error")):
                with patch.object(uploader, "_upload_to_0x0", side_effect=Exception("CDN error")):
                    with patch.object(uploader, "_upload_to_imgbb", side_effect=Exception("CDN error")):
                        uploader.public_cdn_base = "https://autogram-dashboard.onrender.com"
                        urls_fallback = uploader.upload_slide_images(sample_images, "sample", dry_run=False)
                        assert len(urls_fallback) == 2
                        assert all("https://autogram-dashboard.onrender.com/output/sample/" in u for u in urls_fallback)

def test_dashboard_html_features_and_buttons():
    html_path = Path(__file__).parent.parent / "dashboard.html"
    html = html_path.read_text(encoding="utf-8")

    # Critical buttons & interactive elements
    assert 'id="btn-spotlight-publish"' in html
    assert 'id="btn-studio-publish"' in html
    assert 'id="btn-simple-publish"' in html
    assert 'id="top-mode-chip"' in html
    assert 'id="top-mode-label"' in html
    assert 'id="top-mode-dot"' in html
    assert 'executeQueuedItem' in html
    assert 'deleteQueuedItem' in html
    assert 'toggleSchedulerDaemon' in html
    assert 'openScheduleModal' in html
    assert 'submitNewScheduledPost' in html

    # Verify no raw unnormalized publish or execute calls
    assert "fetch(`${API_BASE}/schedule/${id}`" not in html
    assert "apiEndpoint(`/schedule/${id}/execute`)" in html
    assert "apiEndpoint('/publish')" in html
