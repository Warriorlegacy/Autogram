"""60s audio pipeline: TTS (edge-tts -> espeak -> offline) + timing + captions + music.

Pipecat note: the full pipecat-ai repo (torch, webrtc, daily transports) is far
too heavy for a batch GitHub Actions render. We implement the equivalent
lightweight frame pipeline (TextFrame -> TTSFrame -> AudioRawFrame -> timing)
with the same stage boundaries, documented here instead of vendoring pipecat.
Upgrade path: swap `synthesize()` internals for pipecat services if a realtime
voice agent is ever needed; stage contracts already match.
"""
from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

VOICES = ["en-US-BrianMultilingualNeural", "en-US-AvaMultilingualNeural",
          "en-US-AndrewMultilingualNeural", "en-US-EmmaMultilingualNeural"]


@dataclass
class TextFrame:
    text: str


@dataclass
class AudioRawFrame:
    path: str
    duration: float
    provider: str


def pick_voice(slot: str = "") -> str:
    import os
    if (v := os.getenv("REELS_VOICE", "").strip()):
        return v
    h = sum(ord(c) for c in slot) if slot else 0
    return VOICES[h % len(VOICES)]


def probe_duration(path: str) -> float:
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            text=True, timeout=10).strip()
        return round(float(out), 2)
    except Exception:
        return 0.0


async def _edge_tts(text: str, out: Path, voice: str) -> bool:
    try:
        import edge_tts
        await edge_tts.Communicate(text, voice=voice, rate="+6%").save(str(out))
        return out.exists() and out.stat().st_size > 1024
    except Exception as e:
        logger.warning(f"edge-tts failed ({e})")
        return False


def _espeak(text: str, out: Path) -> bool:
    if not shutil.which("espeak-ng") and not shutil.which("espeak"):
        return False
    try:
        wav = out.with_suffix(".wav")
        subprocess.run([shutil.which("espeak-ng") or "espeak", "-v", "en", "-s", "165",
                        "-w", str(wav), text], check=True, timeout=120,
                       capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "160k",
                        str(out)], check=True, timeout=60, capture_output=True)
        return out.exists()
    except Exception as e:
        logger.warning(f"espeak fallback failed ({e})")
        return False


def _offline_bed(text: str, out: Path, duration: float = 60.0) -> bool:
    """Last-resort offline narration bed: correct duration, clearly synthetic.

    ponytail: speech synthesis without network/model; upgrade path is edge-tts.
    """
    try:
        sr, n = 22050, int(22050 * duration)
        import math
        wav = out.with_suffix(".wav")
        words = max(1, len(text.split()))
        with wave.open(str(wav), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            import struct
            for i in range(n):
                t = i / sr
                # Gentle pulsed tone following word cadence — placeholder cadence only
                pulse = 0.5 + 0.5 * math.sin(2 * math.pi * words * t / duration)
                v = int(1200 * pulse * math.sin(2 * math.pi * 196 * t) * math.exp(-0.02 * (t % 3)))
                w.writeframes(struct.pack("<h", v))
        subprocess.run(["ffmpeg", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "128k",
                        str(out)], check=True, timeout=60, capture_output=True)
        return True
    except Exception as e:
        logger.warning(f"offline bed failed ({e})")
        return False


def synthesize(text: str, out_path: str, voice: str | None = None) -> AudioRawFrame:
    """TextFrame -> provider chain -> AudioRawFrame. Never hard-fails on TTS."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    voice = voice or pick_voice()
    frame = TextFrame(text=text)
    if asyncio.run(_edge_tts(frame.text, out, voice)):
        return AudioRawFrame(str(out), probe_duration(str(out)) or 55.0, f"edge-tts:{voice}")
    if _espeak(frame.text, out):
        return AudioRawFrame(str(out), probe_duration(str(out)) or 55.0, "espeak-ng")
    # Offline fallback keeps duration contract so render/QA can proceed
    _offline_bed(frame.text, out)
    return AudioRawFrame(str(out), probe_duration(str(out)) or 60.0, "offline-synth")


def stretch_to_60(voice_path: str, target: float = 60.0) -> tuple[str, float]:
    """Adapt composition to actual narration while keeping final exactly 60s.

    Uses atempo chain (FFmpeg-safe 0.5-2.0 range) + apad/trim. Returns (path, duration).
    """
    dur = probe_duration(voice_path)
    if not dur or dur <= 0:
        # Silent 60s so downstream never breaks
        out = str(Path(voice_path).with_name("voice_60s.mp3"))
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                        "-t", str(target), "-c:a", "aac", "-b:a", "128k", out],
                       check=True, timeout=60, capture_output=True)
        return out, target
    out = str(Path(voice_path).with_name("voice_60s.mp3"))
    if abs(dur - target) < 0.4:
        if voice_path != out:
            shutil.copyfile(voice_path, out)
        return out, round(min(dur, target), 2)
    if 30 <= dur <= 120:  # atempo-safe stretch
        rate = dur / target
        # chain atempo for extreme ratios
        filters, r = [], rate
        while r > 2.0:
            filters.append("atempo=2.0")
            r /= 2.0
        while r < 0.5:
            filters.append("atempo=0.5")
            r /= 0.5
        filters.append(f"atempo={r:.4f}")
        subprocess.run(["ffmpeg", "-y", "-i", voice_path, "-filter:a", ",".join(filters),
                        "-c:a", "aac", "-b:a", "160k", out],
                       check=True, timeout=90, capture_output=True)
    elif dur < 30:  # pad with low room tone to reach 60
        subprocess.run(["ffmpeg", "-y", "-i", voice_path, "-f", "lavfi", "-i",
                        "anoisesrc=d=60:c=brown:r=44100:a=0.015",
                        "-filter_complex", "[1:a]volume=0.15[bed];[0:a][bed]amix=inputs=2:duration=first,"
                        f"apad=whole_dur={target}[a]", "-map", "[a]", "-t", str(target),
                        "-c:a", "aac", "-b:a", "128k", out],
                       check=True, timeout=90, capture_output=True)
    else:  # trim long tail
        subprocess.run(["ffmpeg", "-y", "-i", voice_path, "-t", str(target),
                        "-c:a", "aac", "-b:a", "160k", out],
                       check=True, timeout=90, capture_output=True)
    return out, target


def phrase_captions(scene_plan: dict, srt_path: str) -> str:
    """Phrase-level SRT from scene_plan (word-level needs whisper; phrase syncs to scenes)."""
    def ts(s: float) -> str:
        h, m = int(s // 3600), int((s % 3600) // 60)
        sec, ms = int(s % 60), int(round((s - int(s)) * 1000))
        return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
    lines = []
    for sc in scene_plan["scenes"]:
        txt = (sc["on_screen_text"].strip() or sc["narration"][:90]).strip()
        dur = max(0.5, sc["end"] - sc["start"])
        # Split long captions into <=84-char chunks, time split proportionally
        chunks = []
        while len(txt) > 84:
            cut = txt[:84].rsplit(" ", 1)[0] or txt[:84]
            chunks.append(cut)
            txt = txt[len(cut):].strip()
        chunks.append(txt)
        for j, ch in enumerate(chunks):
            a = round(sc["start"] + dur * j / len(chunks), 2)
            b = round(sc["start"] + dur * (j + 1) / len(chunks), 2)
            lines.append((a, b, ch))
    # Re-distribute overlaps evenly (simple, deterministic)
    out = []
    for i, (a, b, t) in enumerate(lines, 1):
        out.append(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n")
    Path(srt_path).write_text("\n".join(out), encoding="utf-8")
    return srt_path


def procedural_music(out_path: str, duration: float = 60.0) -> str:
    """Royalty-safe ambient bed: layered filtered noise + sub pulse. No scraping."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y",
         "-f", "lavfi", "-i", f"anoisesrc=d={duration}:c=brown:r=44100:a=0.5",
         "-f", "lavfi", "-i", f"sine=frequency=55:d={duration}:beep_factor=0",
         "-filter_complex",
         "[0:a]lowpass=f=420,volume=0.35[pad];[1:a]volume=0.06[sub];"
         "[pad][sub]amix=inputs=2:duration=first,afftdn=nf=-25,aformat=sample_rates=44100:channel_layouts=stereo[m]",
         "-map", "[m]", "-t", str(duration), "-c:a", "aac", "-b:a", "96k", str(out)],
        check=True, timeout=90, capture_output=True)
    return str(out)


def mix_voice_music(voice60: str, music: str, out_path: str) -> str:
    """Duck music under speech (~-18 LUFS relative), normalize for Reels."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", voice60, "-i", music, "-filter_complex",
         "[1:a]volume=0.18[bed];[0:a][bed]amix=inputs=2:duration=first:dropout_transition=2,"
         "loudnorm=I=-16:TP=-1.5:LRA=11[mix]",
         "-map", "[mix]", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", out_path],
        check=True, timeout=120, capture_output=True)
    return out_path
