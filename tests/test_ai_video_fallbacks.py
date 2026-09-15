"""
tests/test_ai_video_fallbacks.py
Verifies the 5-tier cascading AI video fallback architecture in scripts/pipeline_reels.py.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from scripts.pipeline_reels import (
    download_ai_video,
    render_ffmpeg,
    _try_hyperframes,
    _try_gradio_ai_video,
    _try_json2video,
    _try_pexels_video,
    _try_flux_image,
)


@pytest.fixture(autouse=True)
def disable_hyperframes_for_legacy_tier_tests():
    """Ensure HyperFrames Tier 0 does not intercept legacy 5-tier fallback tests."""
    with patch("scripts.pipeline_reels._try_hyperframes", return_value=None):
        yield


def test_download_ai_video_tier1_success(tmp_path):
    """When Gradio AI video generation succeeds, download_ai_video returns tier 1 video."""
    fake_vid = tmp_path / "mock_ai.mp4"
    fake_vid.write_bytes(b"fake_mp4_bytes")

    with patch("scripts.pipeline_reels._try_gradio_ai_video", return_value=str(fake_vid)):
        res = download_ai_video("Cyberpunk watch 3D exploded view", "Cyberpunk Watch")
        assert res["type"] == "video"
        assert res["provider"] == "ai_video_gradio"
        assert res["path"] == str(fake_vid)


def test_download_ai_video_tier2_json2video_fallback(tmp_path):
    """When Tier 1 fails, cascades to Tier 2 (JSON2Video)."""
    fake_vid = tmp_path / "j2v.mp4"
    fake_vid.write_bytes(b"j2v_video_bytes")

    with patch("scripts.pipeline_reels._try_gradio_ai_video", return_value=None):
        with patch("scripts.pipeline_reels._try_json2video", return_value=str(fake_vid)):
            res = download_ai_video("Titanium EV Supercar 3D", "Titanium Supercar")
            assert res["type"] == "video"
            assert res["provider"] == "json2video"
            assert res["path"] == str(fake_vid)


def test_download_ai_video_tier4_pexels_fallback(tmp_path):
    """When Tiers 1-3 fail, cascades to Tier 4 (Pexels 4K stock video)."""
    fake_vid = tmp_path / "pexels.mp4"
    fake_vid.write_bytes(b"pexels_clip_bytes")

    with patch("scripts.pipeline_reels._try_gradio_ai_video", return_value=None):
        with patch("scripts.pipeline_reels._try_json2video", return_value=None):
            with patch("scripts.pipeline_reels._try_fal_or_apiframe", return_value=None):
                with patch("scripts.pipeline_reels._try_pexels_video", return_value=str(fake_vid)):
                    res = download_ai_video("Dark glassmorphic 3D web UI", "Signhify 3D Builder")
                    assert res["type"] == "video"
                    assert res["provider"] == "pexels_cinematic"
                    assert res["path"] == str(fake_vid)


def test_download_ai_video_tier5_flux_fallback(tmp_path):
    """When all video tiers fail, safely falls back to Tier 5 FLUX.1 + 2.5D zoompan."""
    fake_img = tmp_path / "flux.jpg"
    fake_img.write_bytes(b"flux_jpg_bytes")

    with patch("scripts.pipeline_reels._try_gradio_ai_video", return_value=None):
        with patch("scripts.pipeline_reels._try_json2video", return_value=None):
            with patch("scripts.pipeline_reels._try_fal_or_apiframe", return_value=None):
                with patch("scripts.pipeline_reels._try_pexels_video", return_value=None):
                    with patch("scripts.pipeline_reels.download_visual", return_value=None):
                        res = download_ai_video("Quantum Compute 3D", "Quantum Compute", output_image_path=str(fake_img))
                        assert res["type"] == "image"
                        assert res["provider"] == "pollinations_flux_zoompan"
                        assert res["path"] == str(fake_img)


def test_render_ffmpeg_looping_video_command(tmp_path):
    """Verifies render_ffmpeg generates the stream_loop command for video backgrounds."""
    fake_vid = str(tmp_path / "bg.mp4")
    fake_audio = str(tmp_path / "audio.mp3")
    fake_ass = str(tmp_path / "sub.ass")
    out_vid = str(tmp_path / "out.mp4")

    recorded_cmd = []

    def mock_run(cmd, check=True):
        recorded_cmd.extend(cmd)

    with patch("subprocess.run", side_effect=mock_run):
        render_ffmpeg(visual_path=fake_vid, audio_path=fake_audio, ass_path=fake_ass, output_path=out_vid, is_video=True)

    assert "-stream_loop" in recorded_cmd
    assert "-shortest" in recorded_cmd
    assert fake_vid in recorded_cmd
