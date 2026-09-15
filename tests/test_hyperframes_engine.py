"""
tests/test_hyperframes_engine.py
Tests HyperFrames composition compilation, safe zones, CLI rendering, and cascading fallback.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.content.hyperframes_engine import HyperFramesEngine


def test_hyperframes_is_available():
    """Verifies that is_available returns a boolean without throwing."""
    HyperFramesEngine._available = None
    res = HyperFramesEngine.is_available()
    assert isinstance(res, bool)


def test_hyperframes_compile_composition(tmp_path):
    """Verifies that compile_composition creates a valid index.html conforming to the HyperFrames spec."""
    engine = HyperFramesEngine(workspace_dir=tmp_path)
    topic = "Signhify Studio: Build Apple-Grade 3D Scroll Websites from 1 Single Prompt"
    script = "Stop paying $5000 to agencies. Build cinematic 3D scroll websites in minutes at signhify.dpdns.org."

    comp_dir = engine.compile_composition(
        topic=topic,
        script_text=script,
        duration=25.0,
        target_dir=tmp_path,
    )

    index_file = comp_dir / "index.html"
    assert index_file.exists()
    content = index_file.read_text(encoding="utf-8")

    # Spec assertions:
    assert 'data-composition-id="marketing_reel"' in content
    assert 'data-width="1080"' in content
    assert 'data-height="1920"' in content
    assert "safe-zone" in content

    # 5-Scene checks:
    assert 'id="scene-hook"' in content
    assert 'id="scene-compare"' in content
    assert 'id="scene-showcase"' in content
    assert 'id="scene-proof"' in content
    assert 'id="scene-cta"' in content

    # GSAP timeline check:
    assert "window.__timelines.marketing_reel" in content
    assert "signhify.dpdns.org" in content

    # Logo integration check:
    logo_file = comp_dir / "logo.jpeg"
    if logo_file.exists():
        assert "logo.jpeg" in content
        assert "hero-logo-img" in content


def test_hyperframes_render_reel_mock(tmp_path):
    """Verifies that render_reel generates the proper CLI command and returns success metadata."""
    engine = HyperFramesEngine(workspace_dir=tmp_path)
    fake_mp4 = tmp_path / "out.mp4"

    def mock_run(cmd, cwd=None, capture_output=True, text=True, shell=False, timeout=None):
        # Create a dummy output file simulating successful render
        fake_mp4.write_bytes(b"x" * 2048)
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Render completed successfully."
        mock_proc.stderr = ""
        return mock_proc

    with patch.object(HyperFramesEngine, "is_available", return_value=True):
        with patch("subprocess.run", side_effect=mock_run) as run_spy:
            res = engine.render_reel(
                topic="Signhify Studio Launch",
                script_text="Launch your 3D site now.",
                output_path=str(fake_mp4),
                duration=15.0,
            )

            assert res["ok"] is True
            assert res["provider"] == "hyperframes"
            assert res["video_path"] == str(fake_mp4.resolve())
            assert fake_mp4.exists()

            # Verify CLI arguments
            called_cmd = run_spy.call_args[0][0]
            assert any("hyperframes" in str(arg).lower() for arg in called_cmd)
            assert "render" in called_cmd
            assert "-o" in called_cmd


def test_pipeline_reels_hyperframes_tier0_dispatch(tmp_path):
    """Verifies that pipeline_reels.download_ai_video selects HyperFrames when Tier 0 succeeds."""
    from scripts.pipeline_reels import download_ai_video

    fake_reel = tmp_path / "hyperframes.mp4"
    fake_reel.write_bytes(b"hyperframes_video_bytes")

    with patch("scripts.pipeline_reels._try_hyperframes", return_value=str(fake_reel)):
        res = download_ai_video(
            prompt="Cinematic 3D dark glassmorphic UI",
            topic="Signhify 3D Engine",
            script_text="Build in minutes.",
        )
        assert res["type"] == "video"
        assert res["provider"] == "hyperframes"
        assert res["path"] == str(fake_reel)


def test_pipeline_reels_hyperframes_tier0_fallback(tmp_path):
    """Verifies that when HyperFrames fails, download_ai_video cascades smoothly to Tier 1."""
    from scripts.pipeline_reels import download_ai_video

    fake_gradio_vid = tmp_path / "ltx_video.mp4"
    fake_gradio_vid.write_bytes(b"ltx_video_bytes")

    with patch("scripts.pipeline_reels._try_hyperframes", return_value=None):
        with patch("scripts.pipeline_reels._try_gradio_ai_video", return_value=str(fake_gradio_vid)):
            res = download_ai_video(
                prompt="Futuristic 3D mechanical watch",
                topic="Cyberpunk Watch",
            )
            assert res["type"] == "video"
            assert res["provider"] == "ai_video_gradio"
            assert res["path"] == str(fake_gradio_vid)
