"""Offline, deterministic tests for the procedural music + SFX engine (src/content/music60.py)."""
import hashlib
import os
import re
import subprocess
import wave
from pathlib import Path

import pytest

from src.content import music60


def _rms_wav(path: str) -> float:
    """Root-mean-square of the decoded samples, in 0..1 units."""
    out = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "mean_volume" in line:
            db = float(line.split(":")[1].strip().replace(" dB", ""))
            return 10 ** (db / 20.0)
    return 0.0


def test_build_music_duration_and_energy(tmp_path):
    p = music60.build_music("test topic", style="futuristic_electronic",
                            out_path=str(tmp_path / "m.m4a"), seed=42)
    assert Path(p).exists() and Path(p).stat().st_size > 10_000
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", p],
        capture_output=True, text=True).stdout.strip()
    assert 59.0 <= float(dur) <= 61.0
    assert _rms_wav(p) > 0.01  # audible, not silence


def test_build_music_deterministic_and_seed_dependent(tmp_path):
    # short beds suffice for determinism; equality/inequality is duration-independent
    a = music60.build_music("x", duration=3.0, seed=7, out_path=str(tmp_path / "a.m4a"))
    b = music60.build_music("x", duration=3.0, seed=7, out_path=str(tmp_path / "b.m4a"))
    c = music60.build_music("x", duration=3.0, seed=8, out_path=str(tmp_path / "c.m4a"))
    assert hashlib.sha256(Path(a).read_bytes()).digest() == \
        hashlib.sha256(Path(b).read_bytes()).digest()
    assert hashlib.sha256(Path(a).read_bytes()).digest() != \
        hashlib.sha256(Path(c).read_bytes()).digest()


def test_build_music_filtergraph_defines_every_label():
    """Regression: [tN] labels must be DEFINED before the amix that consumes them.

    ffmpeg 8 auto-creates missing labels (so this passed locally by luck); ffmpeg 6 on
    the GH runner hard-fails with "Invalid stream specifier: t0". Assert every label
    referenced in the filtergraph is also produced by one.
    """
    p = music60._style_params("futuristic_electronic", music60._seed_rng(1))
    n = len(p["tone_freqs"])
    fc = music60._build_filtergraph(p, music60._t_expr(60.0))

    # Every segment's LAST label is the one it produces; earlier ones are its inputs.
    produced, referenced = set(), set()
    for seg in fc.split(";"):
        labels = [m for m in re.findall(r"\[([^\]]+)\]", seg) if not m.endswith(":a")]
        if not labels:
            continue
        produced.add(labels[-1])
        referenced.update(labels)
    missing = referenced - produced
    assert not missing, f"filtergraph references undefined labels: {sorted(missing)}"


def test_t_expr_scales_to_duration():
    """A bed shorter than the 60s payoff window must still reach full gain."""
    expr = music60._t_expr(3.0)
    assert "40" not in expr.split("min(1,1-")[0], "payoff must scale with duration"
    assert music60._t_expr(60.0) != expr


def test_build_music_all_styles(tmp_path):
    for style in music60.STYLES:
        p = music60.build_music("x", style=style, duration=3.0,
                                out_path=str(tmp_path / f"{style}.m4a"), seed=1)
        assert Path(p).exists() and Path(p).stat().st_size > 5_000
        assert _rms_wav(p) > 0.005


def test_sfx_library_keys_and_durations(tmp_path):
    sfx = music60.sfx_library(str(tmp_path), seed=42)
    assert set(sfx) == {"whoosh", "impact", "riser", "blip", "data_sweep"}
    expected = {"whoosh": (1.0, 1.3), "impact": (0.6, 1.0), "riser": (1.8, 2.3),
                "blip": (0.2, 0.5), "data_sweep": (0.4, 0.8)}
    for name, path in sfx.items():
        assert Path(path).exists() and Path(path).stat().st_size > 5_000
        w = wave.open(path)
        dur = w.getnframes() / w.getframerate()
        lo, hi = expected[name]
        assert lo <= dur <= hi, f"{name} duration {dur:.2f}s out of [{lo},{hi}]"
        assert w.getframerate() == music60.SR
        w.close()


def test_mix_full_with_sfx(tmp_path):
    # synthetic 60s voice (amplitude-modulated tone)
    voice = str(tmp_path / "voice.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i",
         "aevalsrc=exprs='0.35*sin(2*PI*180*t)*(0.5+0.5*sin(2*PI*2.5*t))':s=44100:d=60",
         "-c:a", "libmp3lame", "-b:a", "128k", voice], check=True, capture_output=True)
    music = music60.build_music("x", style="cinematic_synth", duration=60.0,
                                out_path=str(tmp_path / "music.m4a"), seed=5)
    sfx = music60.sfx_library(str(tmp_path / "sfx"), seed=5)
    scene_plan = {"scenes": [{"start": s, "end": e} for s, e in
                             zip([0, 2, 7, 15, 28, 40, 48], [2, 7, 15, 28, 40, 48, 60])]}
    out = music60.mix_full(voice, music, sfx, str(tmp_path / "mix.m4a"), scene_plan)
    assert Path(out).exists() and Path(out).stat().st_size > 10_000
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", out],
        capture_output=True, text=True).stdout.strip()
    assert 59.0 <= float(dur) <= 61.0
    assert _rms_wav(out) > 0.02  # audible mix
    # aac + loudnorm target: integrated loudness should be near I=-16
    r = subprocess.run(["ffmpeg", "-i", out, "-af", "loudnorm=print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    assert "input_i" in r  # loudnorm ran


def test_mix_full_empty_sfx_plan_falls_back(tmp_path):
    voice = str(tmp_path / "voice.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i",
         "aevalsrc=exprs='0.35*sin(2*PI*180*t)*(0.5+0.5*sin(2*PI*2.5*t))':s=44100:d=60",
         "-c:a", "libmp3lame", "-b:a", "128k", voice], check=True, capture_output=True)
    music = music60.build_music("x", style="minimal_pulse", duration=60.0,
                                out_path=str(tmp_path / "music.m4a"), seed=3)
    out = music60.mix_full(voice, music, {}, str(tmp_path / "mix_plain.m4a"))
    assert Path(out).exists() and Path(out).stat().st_size > 10_000
    assert _rms_wav(out) > 0.02
