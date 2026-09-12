"""
Cloud-native $0 reel renderer for environments without MoneyPrinterTurbo
(e.g. GitHub Actions runners) — the PC-off proof lane.

Pipeline: Pexels free stock (portrait) + edge-TTS neural voiceover with SRT
+ FFmpeg 9:16 assembly with Anton captions + signhify.studio watermark.
Zero marginal cost, zero new accounts beyond the free Pexels API key.
"""

import asyncio
import logging
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import requests

from src.config import settings

logger = logging.getLogger(__name__)

ANTON_URL = "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf"
PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    raise RuntimeError("FFmpeg binary not found on PATH; cannot cloud-render reel.")


def _ffprobe() -> str:
    exe = shutil.which("ffprobe")
    if exe:
        return exe
    raise RuntimeError("ffprobe binary not found on PATH; cannot cloud-render reel.")


def _ffpath(p: str | Path) -> str:
    """Escapes a filesystem path for use inside FFmpeg filter arguments."""
    return str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def _ffquote(p: str | Path) -> str:
    """Single-quotes a path for FFmpeg filters (drive colon stays bare inside quotes)."""
    return "'" + str(p).replace("\\", "/").replace("'", "\\'") + "'"


def ensure_anton_font(dest_dir: str | Path) -> Path | None:
    """Fetches Anton (OFL) for caption styling; None on failure (caller falls back)."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    ttf = dest_dir / "Anton-Regular.ttf"
    if ttf.exists() and ttf.stat().st_size > 50000:
        return ttf
    try:
        with requests.get(ANTON_URL, timeout=60, stream=True) as r:
            r.raise_for_status()
            with open(ttf, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
        if ttf.stat().st_size > 50000:
            return ttf
    except Exception as e:
        logger.warning(f"Anton font download failed ({e}); falling back to system font.")
    return None


def pexels_portrait_clips(query: str, count: int = 3) -> list[dict]:
    """Searches Pexels for portrait MP4s. Returns [{url, duration}] (best first)."""
    api_key = (getattr(settings, "pexels_api_key", None) or os.environ.get("PEXELS_API_KEY", "")).strip()
    if not api_key:
        raise RuntimeError(
            "PEXELS_API_KEY is not configured. Get a free key at pexels.com/api "
            "and set it as a repo secret (CI) or in .env (local)."
        )
    resp = requests.get(
        PEXELS_SEARCH_URL,
        headers={"Authorization": api_key},
        params={"query": query, "per_page": 12, "orientation": "portrait", "size": "medium"},
        timeout=25,
    )
    resp.raise_for_status()
    clips: list[dict] = []
    for video in resp.json().get("videos", []):
        best = None
        for f in video.get("video_files", []):
            if f.get("file_type") != "video/mp4":
                continue
            w, h = f.get("width") or 0, f.get("height") or 0
            if h >= 960 and h >= w and (best is None or h > best[1]):
                best = (f.get("link"), h)
        if best and best[0]:
            clips.append({"url": best[0], "duration": float(video.get("duration") or 5)})
        if len(clips) >= count:
            break
    if not clips:
        raise RuntimeError(f"Pexels returned no portrait clips for query '{query}'.")
    return clips


def edge_tts_synthesize(text: str, mp3_path: str | Path, srt_path: str | Path,
                        voice: str = "en-US-ChristopherNeural") -> float:
    """Synthesizes narration MP4 audio + SRT via edge-TTS. Returns audio seconds."""
    import edge_tts
    import inspect

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice)
        try:
            submaker = edge_tts.SubMaker()
        except TypeError:
            submaker = None
        with open(mp3_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk.get("type") == "audio":
                    f.write(chunk.get("data", b""))
                elif chunk.get("type") == "WordBoundary" and submaker is not None:
                    if hasattr(submaker, "feed"):
                        submaker.feed(chunk)
                    else:  # legacy edge-tts API
                        submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
        if submaker is None:
            Path(srt_path).write_text("1\n00:00:00,000 --> 00:00:05,000\n \n", encoding="utf-8")
            return
        subs = submaker.get_srt() if hasattr(submaker, "get_srt") else submaker.generate_subs()
        if inspect.isawaitable(subs):
            subs = await subs
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(subs or "1\n00:00:00,000 --> 00:00:05,000\n \n")

    asyncio.run(_run())
    probe = subprocess.run(
        [_ffprobe(), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_path)],
        capture_output=True, text=True, timeout=60,
    )
    try:
        return max(5.0, float(probe.stdout.strip()))
    except ValueError:
        return max(5.0, len(text.split()) / 2.5)


def assemble_reel(clips: list[dict], audio_path: str | Path, srt_path: str | Path,
                  dest: str | Path, audio_duration: float,
                  watermark_text: str = "signhify.studio") -> str:
    """Concatenates portrait clips under the narration with burned captions + watermark."""
    ffmpeg = _ffmpeg()
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="cloudreel_"))

    # 1. Download clips (+ stage audio/srt into the assembly workdir so every
    # filter path below can stay relative)
    shutil.copy2(str(audio_path), str(workdir / "narration.mp3"))
    shutil.copy2(str(srt_path), str(workdir / "captions.srt"))
    audio_name = "narration.mp3"
    srt_name = "captions.srt"
    local_clips: list[Path] = []
    for i, clip in enumerate(clips):
        target = workdir / f"clip_{i}.mp4"
        with requests.get(clip["url"], timeout=120, stream=True) as r:
            r.raise_for_status()
            with open(target, "wb") as f:
                for chunk in r.iter_content(chunk_size=262144):
                    if chunk:
                        f.write(chunk)
        if target.stat().st_size > 100000:
            local_clips.append(target)
    if not local_clips:
        raise RuntimeError("All Pexels clip downloads failed or were empty.")

    # 2. Caption font (Anton preferred, system fallback)
    font_file = ensure_anton_font(workdir / "fonts")
    # 3. Build filter with RELATIVE paths only (this ffmpeg build misparses
    # drive-colon absolute paths inside subtitles/drawtext options, quoted or
    # escaped — so run with cwd=workdir and bare relative names).
    n = len(local_clips)
    seg = math.ceil(audio_duration / n) + 1
    parts: list[str] = []
    inputs: list[str] = []
    for i, clip in enumerate(local_clips):
        loops = min(20, math.ceil(audio_duration / max(1.0, seg)) + 1)
        inputs += ["-stream_loop", str(loops), "-i", clip.name]
        parts.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,fps=30[v{i}]"
        )
    parts.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vcat]")
    if font_file:
        sub_filter = (
            f"subtitles={srt_name}:fontsdir=fonts:"
            "force_style='FontName=Anton,FontSize=24,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H80000000,BorderStyle=1,Outline=3,Shadow=0,MarginV=150,Alignment=2'"
        )
        draw_font = "fonts/Anton-Regular.ttf"
    else:
        sub_filter = (
            f"subtitles={srt_name}:"
            "force_style='FontSize=24,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H80000000,BorderStyle=1,Outline=3,Shadow=0,MarginV=150,Alignment=2'"
        )
        draw_font = None
    vf = ";".join(parts) + f",[vcat]{sub_filter}"
    if draw_font:
        vf += (
            f",drawtext=fontfile={draw_font}:text='{watermark_text}':fontsize=44:"
            "fontcolor=white:borderw=2:bordercolor=black:"
            "box=1:boxcolor=black@0.45:boxborderw=14:x=(w-text_w)/2:y=170[vout]"
        )
    else:
        vf += ",null[vout]"
    audio_idx = n  # audio input position after the N clip inputs

    cmd = [ffmpeg, "-y", *inputs, "-i", audio_name,
           "-filter_complex", vf,
           "-map", "[vout]", "-map", f"{audio_idx}:a",
           "-t", f"{audio_duration:.1f}",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-movflags", "+faststart", str(dest)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900,
                          cwd=str(workdir))
    if proc.returncode != 0 or not dest.exists() or dest.stat().st_size < 100000:
        err_log = workdir / "ffmpeg_err.log"
        try:
            err_log.write_text(proc.stderr or "", encoding="utf-8", errors="replace")
        except Exception:
            pass
        raise RuntimeError(f"FFmpeg reel assembly failed (full log: {err_log}): {proc.stderr[-600:]}")
    logger.info(f"Cloud reel assembled: {dest} ({dest.stat().st_size // 1024} KB)")
    return str(dest)


def render_cloud_reel(narration: str, subject: str, dest: str | Path,
                      voice: str = "en-US-ChristopherNeural") -> str:
    """Full cloud render: voiceover+SRT -> stock -> assembly. Returns MP4 path."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="cloudreel_"))
    mp3 = workdir / "narration.mp3"
    srt = workdir / "captions.srt"
    logger.info("Cloud render: synthesizing voiceover via edge-TTS...")
    audio_dur = edge_tts_synthesize(narration, mp3, srt, voice)
    logger.info(f"Cloud render: fetching Pexels portrait stock for '{subject}'...")
    clips = pexels_portrait_clips(subject or narration[:60])
    return assemble_reel(clips, mp3, srt, dest, audio_dur)


def render_reel_auto(script: str, subject: str, dest: str | Path,
                     voice_name: str = "en-US-ChristopherNeural",
                     timeout_s: int = 900) -> str:
    """Smart render: local MoneyPrinterTurbo when reachable, else cloud lane.

    MPT-first preserves max quality on the owner PC; the cloud fallback keeps
    GitHub Actions runners (PC-off) fully autonomous at $0.
    """
    from src.content.mpt_client import mpt_client

    if mpt_client.is_available():
        logger.info("Render engine: local MoneyPrinterTurbo.")
        return mpt_client.render_reel(script=script, subject=subject, dest=dest,
                                      voice_name=voice_name, timeout_s=timeout_s)
    logger.info("Render engine: cloud lane (MPT unreachable) — Pexels + edge-TTS + FFmpeg.")
    return render_cloud_reel(script, subject, dest, voice=voice_name)
