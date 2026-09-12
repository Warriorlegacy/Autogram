import pytest
from pathlib import Path

import dashboard_api
from src.youtube.shorts_publisher import YouTubeShortsPublisher, youtube_publisher


def _test_client():
    dashboard_api.app.config["TESTING"] = True
    return dashboard_api.app.test_client()


def test_youtube_shorts_publisher_dry_run():
    """Verify YouTubeShortsPublisher operates correctly and safely in dry-run mode."""
    pub = YouTubeShortsPublisher(dry_run=True)
    video_id = pub.upload_short(
        video_path="output/sample/test.mp4",
        title="10x Developer CLI Tools",
        description="Best CLI tools for AI engineers",
        tags=["AI", "CLI", "Developer"],
    )
    assert video_id.startswith("mock_yt_short_")


def test_youtube_shorts_title_formatting():
    """Verify title formatting automatically appends #Shorts and bounds title length."""
    pub = YouTubeShortsPublisher()

    # Appends #Shorts when missing
    assert pub._format_title("vLLM vs Ollama").endswith("#Shorts")

    # Doesn't duplicate #Shorts
    assert pub._format_title("vLLM vs Ollama #Shorts").count("#Shorts") == 1

    # Handles lower-case #shorts without duplicate
    assert pub._format_title("vLLM vs Ollama #shorts") == "vLLM vs Ollama #shorts"

    # Truncates overly long titles to stay within YouTube 100-char limit
    long_title = "A" * 120
    formatted = pub._format_title(long_title)
    assert len(formatted) <= 100
    assert formatted.endswith("#Shorts")


def test_youtube_shorts_live_mode_missing_credentials():
    """Verify upload_short raises FileNotFoundError or RuntimeError when files/credentials missing in live mode."""
    pub = YouTubeShortsPublisher(dry_run=False)

    # Non-existent file
    with pytest.raises(FileNotFoundError):
        pub.upload_short("non_existent_file.mp4", "Title", "Desc")

    # When file exists but no credentials
    temp_file = Path("output/temp_test_video.mp4")
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file.write_bytes(b"placeholder")
    try:
        with pytest.raises(RuntimeError, match="No valid YouTube credentials found"):
            pub.upload_short(temp_file, "Title", "Desc")
    finally:
        if temp_file.exists():
            temp_file.unlink()


def test_api_publish_shorts_endpoint_dry_run():
    """Verify POST /api/publish/shorts returns a valid shorts manifest in dry-run mode."""
    with _test_client() as client:
        res = client.post("/api/publish/shorts", json={
            "topic": "Unit Test YouTube Shorts Topic",
            "pillar": "AI Tool Breakdown",
            "mode": "dry-run"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["ok"] is True
        assert data["format"] == "shorts"
        assert data["mode"] == "dry-run"
        assert "video_id" in data
        assert data["video_id"].startswith("mock_yt_short_")
        assert "youtube.com/shorts/" in data["url"]


def test_api_publish_dual_video_endpoint_dry_run():
    """Verify POST /api/publish/video executes dual publishing in dry-run mode."""
    with _test_client() as client:
        res = client.post("/api/publish/video", json={
            "topic": "Dual Publishing Test Topic",
            "pillar": "AI Tool Breakdown",
            "mode": "dry-run"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["ok"] is True
        assert data["format"] == "video"
        assert data["mode"] == "dry-run"
        destinations = data.get("destinations", {})
        assert "youtube_shorts" in destinations
        assert "instagram_reels" in destinations
        assert destinations["youtube_shorts"]["status"] == "success"
        assert destinations["instagram_reels"]["status"] == "success"
