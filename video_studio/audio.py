"""Narration providers.

Per-scene synthesis is what makes captions exact: each scene's audio is measured,
and that measurement becomes the scene's duration, so a caption never drifts from
its line. Kokoro-82M (Apache-2.0) is the default — local, commercial-safe, $0.
edge-tts is the fallback but Microsoft's service ToS may prohibit commercial use.

The HyperFrames `tts` CLI is deliberately NOT used: it shells out to a Python it
cannot locate (kokoro-onnx lives in .venv) and fails even with HYPERFRAMES_PYTHON
set. Calling the library directly is fewer moving parts.
"""
from __future__ import annotations

import shutil
import subprocess
import wave
from pathlib import Path

from .brief import REPO_ROOT
from .storyboard import Storyboard, WORK_DIR

# Narration lives under output/<slug>/, NOT work/<slug>/ — write_project() rmtree's
# the work dir on every build, which would delete the track between synth and mux.
OUTPUT_DIR = Path(__file__).parent / "output"

KOKORO_MODEL = REPO_ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx"
KOKORO_VOICES = REPO_ROOT / "models" / "kokoro" / "voices-v1.0.bin"
DEFAULT_VOICE = "af_heart"
DEFAULT_SPEED = 1.0


def kokoro_available() -> bool:
    return KOKORO_MODEL.exists() and KOKORO_VOICES.exists()


def wav_duration(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as w:
            return round(w.getnframes() / float(w.getframerate()), 3)
    except Exception:
        return 0.0


def _kokoro_scene(text: str, dest: Path, voice: str = DEFAULT_VOICE,
                  speed: float = DEFAULT_SPEED) -> Path | None:
    """One scene -> one wav, via the local Apache-2.0 model."""
    if not kokoro_available():
        return None
    try:
        import numpy as np
        import soundfile as sf
        from kokoro_onnx import Kokoro
    except ImportError:
        return None
    try:
        k = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
        samples, sr = k.create(text, voice, speed=speed, lang="en-us")
        dest.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(dest), np.asarray(samples), sr)
        return dest if dest.exists() and dest.stat().st_size > 0 else None
    except Exception as e:
        print(f"[audio] kokoro scene failed: {e}")
        return None


def _edge_scene(text: str, dest: Path) -> Path | None:
    """edge-tts fallback. Non-production for monetized output."""
    if not shutil.which("ffmpeg"):
        return None
    try:
        mp3 = dest.with_suffix(".mp3")
        r = subprocess.run(["edge-tts", "--voice", "en-US-AriaNeural",
                            "--text", text, "--write-media", str(mp3)],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=300)
        if r.returncode != 0 or not mp3.exists():
            return None
        c = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3),
                            "-ar", "48000", "-ac", "1", str(dest)],
                           capture_output=True, timeout=300)
        return dest if c.returncode == 0 and dest.exists() else None
    except Exception:
        return None


def synthesize_scenes(brief, sb: Storyboard, log: list[str], voice: str = DEFAULT_VOICE,
                      speed: float = DEFAULT_SPEED) -> tuple[list[Path], float]:
    """Synthesize one wav per narrated scene. Returns (files, total_duration)."""
    proj = OUTPUT_DIR / brief.slug / "audio"
    files: list[Path] = []
    for scene in sb.scenes:
        text = (scene.narration or "").strip()
        if not text:
            continue
        wav = _kokoro_scene(text, proj / "audio" / f"{scene.id}.wav", voice, speed)
        if wav is None:
            wav = _edge_scene(text, proj / "audio" / f"{scene.id}.wav")
        if wav:
            files.append(wav)
    total = round(sum(wav_duration(f) for f in files), 3)
    provider = "kokoro" if kokoro_available() else "edge-tts"
    log.append(f"[audio] provider={provider} scenes={len(files)} narration={total}s")
    return files, total


def concat_wavs(files: list[Path], dest: Path) -> Path:
    """Join per-scene wavs into one track with silence padding for scene gaps."""
    import numpy as np
    import soundfile as sf
    chunks, sr = [], 24000
    for f in files:
        data, sr = sf.read(str(f), dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        chunks.append(data)
        # 0.25s breath between scenes
        chunks.append(np.zeros(int(sr * 0.25), dtype="float32"))
    if not chunks:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(dest), np.concatenate(chunks), sr)
    return dest


def demo() -> None:
    assert isinstance(DEFAULT_SPEED, float)
    assert wav_duration(Path("nonexistent.wav")) == 0.0


if __name__ == "__main__":
    demo()
    print("audio.py self-check OK")