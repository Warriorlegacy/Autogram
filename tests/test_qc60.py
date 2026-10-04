"""Offline, fast tests for the post-production layer (qc60 + thumbnail60).

Synthetic ffmpeg fixtures are generated in tmp_path (all-black / bright clips,
silent / tone audio). The thumbnail test is a real Playwright screenshot but is
kept well under the 30s budget. No network, no publishing, no secrets.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.content import qc60
from src.content import thumbnail60


# ---------------------------------------------------------------------------
# ffmpeg fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def clips(tmp_path_factory):
    d = tmp_path_factory.mktemp("qc60_clips")
    black = d / "black.mp4"
    bright = d / "bright.mp4"
    silent = d / "silent.wav"
    tone = d / "tone.wav"

    def run(*args):
        subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True, timeout=60)

    run("-f", "lavfi", "-i", "color=c=black:s=320x320:d=4:r=10", "-pix_fmt", "yuv420p", str(black))
    run("-f", "lavfi", "-i", "smptebars=s=320x320:d=4:r=10", "-pix_fmt", "yuv420p", str(bright))
    run("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "4", str(silent))
    run("-f", "lavfi", "-i", "sine=frequency=440:duration=4", str(tone))
    return {"black": str(black), "bright": str(bright), "silent": str(silent), "tone": str(tone)}


# ---------------------------------------------------------------------------
# black_frame_check
# ---------------------------------------------------------------------------
def test_black_frame_check_detects_all_black(clips):
    ok, ratio = qc60.black_frame_check(clips["black"], sample_n=4)
    assert ok is False
    assert ratio == 1.0


def test_black_frame_check_passes_bright(clips):
    ok, ratio = qc60.black_frame_check(clips["bright"], sample_n=4)
    assert ok is True
    assert ratio == 0.0


# ---------------------------------------------------------------------------
# placeholder_check
# ---------------------------------------------------------------------------
def test_placeholder_check_finds_issues():
    dirty = "TODO ship this, FIXME later, lorem ipsum, {{var}}, REPLACE_ME, XXX, []"
    found = qc60.placeholder_check(dirty)
    for expected in ("TODO", "FIXME", "lorem ipsum", "{{", "}}", "REPLACE_ME", "XXX", "empty []"):
        assert expected in found


def test_placeholder_check_clean():
    assert qc60.placeholder_check("A clean hook about AI agents.") == []
    assert qc60.placeholder_check("") == []


# ---------------------------------------------------------------------------
# timing_check
# ---------------------------------------------------------------------------
def _plan(scenes):
    return {"scenes": scenes}


def test_timing_check_valid_passes():
    plan = _plan([
        {"start": 0.0, "end": 6.0, "caption": "First"},
        {"start": 6.0, "end": 12.0, "caption": "Second"},
        {"start": 12.0, "end": 18.0, "caption": "Third"},
    ])
    assert qc60.timing_check(plan, 18.0) == []


def test_timing_check_gap_fails():
    plan = _plan([
        {"start": 0.0, "end": 6.0, "caption": "First"},
        {"start": 8.0, "end": 12.0, "caption": "Second"},
    ])
    issues = qc60.timing_check(plan, 12.0)
    assert any("gap/overlap" in i for i in issues)


def test_timing_check_too_short_scene_fails():
    plan = _plan([{"start": 0.0, "end": 0.1, "caption": "Flash"}])
    issues = qc60.timing_check(plan, 0.1)
    assert any("duration" in i for i in issues)


def test_timing_check_empty_plan_fails():
    assert qc60.timing_check({}, 60.0) != []
    assert qc60.timing_check({"scenes": []}, 60.0) != []


# ---------------------------------------------------------------------------
# audio_check
# ---------------------------------------------------------------------------
def test_audio_check_silent_fails(clips):
    ok, details = qc60.audio_check(clips["silent"])
    assert ok is False
    assert details["mean_db"] < -40.0


def test_audio_check_tone_passes(clips):
    ok, details = qc60.audio_check(clips["tone"])
    assert ok is True
    assert details["clipping"] is False


# ---------------------------------------------------------------------------
# metadata + generation report
# ---------------------------------------------------------------------------
def test_build_metadata_spec_keys():
    meta = qc60.build_metadata(
        report={}, topic="AI agents", hook="Everyone is using AI wrong.",
        script="script", scene_plan={"scenes": []}, duration=60.0,
        style="theme-B", assets=[{"kind": "video", "path": "final_reel.mp4"}],
        voice="edge-tts", music="procedural", virality_score=88.5,
    )
    assert sorted(meta.keys()) == ["assetsUsed", "duration", "hook", "music",
                                   "renderedAt", "style", "title", "topic",
                                   "viralityScore", "voice"]
    assert meta["duration"] == 60.0
    assert meta["viralityScore"] == 88.5
    assert meta["style"] == "theme-B"
    assert "Everyone is using AI wrong" in meta["title"]


def test_build_generation_report_shape():
    gr = qc60.build_generation_report(
        [{"name": "qa", "status": "ok", "elapsed_s": 1.25, "detail": "ok"}],
        final={"status": "PUBLISHED"},
    )
    assert set(gr.keys()) == {"generatedAt", "stages", "final"}
    assert gr["stages"][0] == {"name": "qa", "status": "ok", "elapsed_s": 1.25, "detail": "ok"}
    assert gr["final"]["status"] == "PUBLISHED"


# ---------------------------------------------------------------------------
# thumbnail (real Playwright screenshot, kept < 30s)
# ---------------------------------------------------------------------------
def test_thumbnail_renders_png(tmp_path):
    hook = "Everyone is using AI wrong. Here's what they're missing."
    topic = "AI agents are changing software development"
    t0 = __import__("time").time()
    out = thumbnail60.generate_thumbnail(hook, topic, tmp_path, theme="B", square=False)
    assert out is not None
    p = Path(out)
    assert p.exists() and p.stat().st_size > 500
    assert (tmp_path / "thumbnail.png").name == p.name
    assert __import__("time").time() - t0 < 30


def test_thumbnail_1x1_renders(tmp_path):
    out = thumbnail60.generate_thumbnail("hook words", "topic", tmp_path, square=True)
    assert out is not None
    assert Path(out).exists()
