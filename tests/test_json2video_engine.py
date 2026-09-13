"""
tests/test_json2video_engine.py - Verification for the JSON2Video Cloud Rendering Engine
Validates payload compilation, API authentication, job registration, and local fallback.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.content.json2video_engine import JSON2VideoEngine


def test_json2video_is_configured():
    engine = JSON2VideoEngine(api_key="HQ7RnIuqBVrWnX1HwmD0SnlTGPZyImA8ip4Jg9W9")
    assert engine.is_configured() is True

    unconfigured = JSON2VideoEngine(api_key="")
    assert unconfigured.is_configured() is False


def test_compile_movie_payload():
    engine = JSON2VideoEngine(api_key="test_key_123456789")
    script = "Stop posting manually. Software belongs in production. Deploy your content engine today."
    edit_plan = {
        "beats": [
            {"beat_index": 1, "spoken_text": "Stop posting manually.", "target_duration_seconds": 4.0},
            {"beat_index": 2, "spoken_text": "Software belongs in production.", "target_duration_seconds": 4.5},
            {"beat_index": 3, "spoken_text": "Deploy your content engine today.", "target_duration_seconds": 5.0}
        ]
    }

    payload = engine.compile_movie_payload(script, edit_plan)

    assert payload["resolution"] == "instagram-story"
    assert payload["fps"] == 30
    assert len(payload["scenes"]) == 3

    first_scene = payload["scenes"][0]
    assert first_scene["duration"] == 4.0
    elements = first_scene["elements"]
    assert any(e.get("text") == "STOP POSTING MANUALLY." for e in elements)
    assert any("SIGNHIFY.STUDIO" in e.get("text", "") for e in elements)


def test_submit_render_mock():
    engine = JSON2VideoEngine(api_key="test_key_123456789")
    payload = {"resolution": "instagram-story", "scenes": []}

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"success": True, "project": "prj_987654"}

    with patch("requests.post", return_value=mock_resp) as mock_post:
        res = engine.submit_render(payload)
        assert res["project_id"] == "prj_987654"
        mock_post.assert_called_once()


def test_poll_movie_status_mock():
    engine = JSON2VideoEngine(api_key="test_key_123456789")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "success": True,
        "movie": {
            "status": "done",
            "url": "https://cdn.json2video.com/renders/prj_987654.mp4"
        }
    }

    with patch("requests.get", return_value=mock_resp):
        res = engine.poll_movie_status("prj_987654", timeout_seconds=10, poll_interval=1)
        assert res["status"] == "completed"
        assert res["video_url"] == "https://cdn.json2video.com/renders/prj_987654.mp4"


def test_render_reel_fallback(tmp_path):
    engine = JSON2VideoEngine(api_key="invalid_or_failing_key")
    out_file = tmp_path / "test_reel.mp4"

    with patch.object(engine, "submit_render", side_effect=RuntimeError("API Network Error")):
        with patch("src.content.video_engine.VideoEngine.render_vertical_reel") as mock_local:
            mock_local.return_value = {"status": "completed", "video_path": str(out_file), "duration_seconds": 15}
            res = engine.render_reel("Sample script for fallback test.", output_path=out_file, fallback_to_local=True)
            assert res["provider"] == "local_ffmpeg"
            assert res["status"] == "completed"
