from unittest.mock import patch

import dashboard_api
from src.content.generator import generator
from src.content.mpt_client import MoneyPrinterTurboClient
from src.instagram.publisher import InstagramPublisher
from src.storage.uploader import uploader


def _test_client():
    dashboard_api.app.config["TESTING"] = True
    return dashboard_api.app.test_client()


def test_publisher_reel_dry_run_and_container():
    """Verify create_reel_container and publish_reel operate correctly in dry-run mode."""
    pub = InstagramPublisher(dry_run=True)
    cntr_id = pub.create_reel_container("https://example.com/reel.mp4", "Test caption #Reels")
    assert cntr_id.startswith("mock_reel_cntr_")

    media_id = pub.publish_reel("https://example.com/reel.mp4", "Test caption #Reels")
    assert media_id.startswith("mock_published_media_")

    # In live mode, invalid URL must raise ValueError
    pub_live = InstagramPublisher(dry_run=False)
    pub_live._forced_dry_run = False
    pub_live.user_id = "12345"
    pub_live.token = "fake_token"
    with __import__("pytest").raises(ValueError, match="Invalid video_url"):
        pub_live.create_reel_container("invalid-relative-path.mp4")


def test_reel_script_generation():
    """Verify generator.generate_reel_script returns narration + caption + hashtags."""
    script = generator.generate_reel_script("vLLM High-Throughput Inference", "AI Tool Breakdown")
    assert script["topic"] == "vLLM High-Throughput Inference"
    assert script["pillar"] == "AI Tool Breakdown"
    assert len(script["narration"].split()) >= 20  # spoken-length narration
    assert script["caption"]
    assert isinstance(script["hashtags"], list) and len(script["hashtags"]) >= 5
    assert script["subject"]  # short MPT search subject


def test_mpt_client_unavailable_server():
    """Verify the MPT client fails fast and cleanly when the render server is down."""
    dead = MoneyPrinterTurboClient(base_url="http://127.0.0.1:9")
    assert dead.is_available(timeout=2) is False


def test_uploader_video_dry_run_fabricates_url():
    """Verify upload_video_file fabricates a public MP4 URL in dry-run without network."""
    url = uploader.upload_video_file("output/2026-09-12/reel_123.mp4", "2026-09-12", dry_run=True)
    assert url.startswith("http")
    assert url.endswith("reel_123.mp4")


def test_api_mpt_status_endpoint():
    """Verify GET /api/mpt/status reports render-server availability."""
    with _test_client() as client:
        res = client.get("/api/mpt/status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["ok"] is True
        assert isinstance(data["available"], bool)
        assert "base_url" in data


def test_api_publish_reel_endpoint_dry_run():
    """Verify POST /api/publish/reel returns a valid reel manifest in dry-run mode."""
    with _test_client() as client:
        res = client.post("/api/publish/reel", json={
            "topic": "Unit Test Reel Publishing Topic",
            "pillar": "AI Tool Breakdown",
            "mode": "dry-run"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["ok"] is True
        assert data["format"] == "reel"
        assert data["mode"] == "dry-run"
        assert "media_id" in data
        assert data["topic"] == "Unit Test Reel Publishing Topic"


def test_execute_queued_reel_item():
    """Verify executing a queued reel item passes content_format='reel'."""
    with dashboard_api.pipeline_lock:
        dashboard_api.pipeline_status = "idle"

    sched = dashboard_api.read_schedule()
    queue = sched.setdefault("queue", [])
    test_id = "REEL-UNIT-TEST-1"
    sched["queue"] = [q for q in queue if q.get("id") != test_id]
    sched["queue"].insert(0, {
        "id": test_id,
        "topic": "Automated Unit Test Scheduled Reel",
        "pillar": "Tech Explainer",
        "format": "reel",
        "mode": "dry-run",
        "status": "QUEUED",
        "scheduled_time": "2026-09-12T15:00:00"
    })
    dashboard_api.write_schedule(sched)

    with patch("dashboard_api.run_pipeline_subprocess", return_value=True) as mock_subproc:
        with _test_client() as client:
            res = client.post(f"/api/schedule/{test_id}/execute")
            assert res.status_code == 200
            data = res.get_json()
            assert data["ok"] is True
            assert data["item"]["id"] == test_id
            mock_subproc.assert_called_once()
            _, kwargs = mock_subproc.call_args
            assert kwargs.get("content_format") == "reel"
            assert kwargs.get("topic") == "Automated Unit Test Scheduled Reel"

    # Cleanup
    sched = dashboard_api.read_schedule()
    sched["queue"] = [q for q in sched.get("queue", []) if q.get("id") != test_id]
    dashboard_api.write_schedule(sched)
