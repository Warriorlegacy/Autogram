"""Tests for the cloud-native $0 reel renderer (PC-off lane). All offline-safe."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.content import cloud_render
from src.content.cloud_render import render_reel_auto


def test_pexels_missing_key_raises(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "pexels_api_key", None)
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="PEXELS_API_KEY"):
        cloud_render.pexels_portrait_clips("ai tools")


def test_ffquote_keeps_filter_paths_colon_free():
    quoted = cloud_render._ffquote(Path("captions.srt"))
    assert quoted == "'captions.srt'"
    assert ":" not in quoted


def test_render_auto_prefers_mpt_when_available():
    with patch("src.content.mpt_client.mpt_client") as mpt, \
         patch("src.content.cloud_render.render_cloud_reel",
               side_effect=AssertionError("cloud lane must not run when MPT is up")):
        mpt.is_available.return_value = True
        mpt.render_reel.return_value = "out/mpt.mp4"
        assert render_reel_auto("script", "subject", "out/m.mp4") == "out/mpt.mp4"
        mpt.render_reel.assert_called_once()


def test_render_auto_falls_back_to_cloud():
    with patch("src.content.mpt_client.mpt_client") as mpt, \
         patch("src.content.cloud_render.render_cloud_reel", return_value="out/cloud.mp4") as cl:
        mpt.is_available.return_value = False
        assert render_reel_auto("script", "subject", "out/m.mp4") == "out/cloud.mp4"
        cl.assert_called_once()


def test_assemble_filter_has_no_drive_colons(tmp_path):
    """Regression: absolute Windows paths broke ffmpeg filter parsing; the
    filter graph must only contain bare relative names."""
    audio = tmp_path / "n.mp3"
    srt = tmp_path / "c.srt"
    audio.write_bytes(b"0" * 1000)
    srt.write_text("1\n00:00:00,000 --> 00:00:05,000\nHi\n", encoding="utf-8")
    dest = tmp_path / "reel.mp4"
    captured = {}

    class _FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size=1):
            yield b"0" * 200000

    class _Proc:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        captured["cwd"] = kw.get("cwd")
        dest.write_bytes(b"1" * 200000)
        return _Proc()

    clips = [{"url": "http://x/a.mp4", "duration": 6},
             {"url": "http://x/b.mp4", "duration": 6}]
    with patch("src.content.cloud_render.requests.get", return_value=_FakeResp()), \
         patch("src.content.cloud_render.subprocess.run", side_effect=fake_run):
        assert cloud_render.assemble_reel(clips, audio, srt, dest, 10.0) == str(dest)

    fc = captured["cmd"][captured["cmd"].index("-filter_complex") + 1]
    assert "subtitles=captions.srt" in fc
    assert "C:" not in fc and "D:" not in fc
    assert "drawtext" in fc and "signhify.studio" in fc
