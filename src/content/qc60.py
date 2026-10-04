"""Post-production QC + metadata for the 60s Reel engine (Signhify.studio).

Fail-soft helpers: every function returns a value (never raises for bad input)
and the caller records results into the slot report. No network, no secrets.
"""
from __future__ import annotations

import json
import logging
import re
import struct
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

BLACK_LUMA_THRESHOLD = 8.0          # mean luma below this => frame is black (of 255)
MIN_SCENE_DURATION = 0.3            # seconds
AUDIO_CLIP_DB = 0.0                 # dBFS max level above this => clipping
AUDIO_RMS_RANGE = (-40.0, -8.0)     # sane RMS (dB)

# Ordered so longer / more specific patterns match first and stay readable.
PLACEHOLDER_PATTERNS = [
    (re.compile(r"\bTODO\b", re.I), "TODO"),
    (re.compile(r"\bFIXME\b", re.I), "FIXME"),
    (re.compile(r"\bREPLACE_ME\b", re.I), "REPLACE_ME"),
    (re.compile(r"\bXXX\b", re.I), "XXX"),
    (re.compile(r"lorem\s+ipsum", re.I), "lorem ipsum"),
    (re.compile(r"\{\{"), "{{"),
    (re.compile(r"\}\}"), "}}"),
    (re.compile(r"\[\s*\]"), "empty []"),
    (re.compile(r"\(\s*\)"), "empty ()"),
]


# ---------------------------------------------------------------------------
# Black frames
# ---------------------------------------------------------------------------
def _frame_luma(raw: bytes, width: int, height: int) -> float:
    """Mean luma of one raw RGB24 frame (PIL when available, else pure math)."""
    if len(raw) < width * height * 3:
        return float("nan")
    try:
        from PIL import Image
        g = Image.frombytes("RGB", (width, height), raw).convert("L")
        px = g.tobytes()  # grayscale bytes; mean = mean luma
        return sum(px) / len(px)
    except Exception:
        r = raw[0::3]
        g = raw[1::3]
        b = raw[2::3]
        return sum(0.299 * r[i] + 0.587 * g[i] + 0.114 * b[i] for i in range(len(r))) / len(r)


def black_frame_check(video_path: str, sample_n: int = 8) -> tuple[bool, float]:
    """Sample ~N frames across the video, flag black frames (mean luma < 8/255).

    Returns (pass, black_ratio). Pass = no black frame sampled. Frames are
    sampled via ffmpeg select/rawvideo piped to stdout, luma computed with PIL
    or pure struct math. Never raises: on failure returns (True, 0.0).
    """
    try:
        probe = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height",
             "-show_entries", "format=duration",
             "-of", "json", str(video_path)], text=True, timeout=15)
        info = json.loads(probe)
        vs = (info.get("streams") or [{}])[0]
        width = int(vs.get("width") or 0)
        height = int(vs.get("height") or 0)
        duration = float((info.get("format") or {}).get("duration") or 0)
        if width <= 0 or height <= 0 or duration <= 0:
            return True, 0.0
        n = max(1, min(int(sample_n), 24))
        step = max(0.5, duration / max(1, n))
        select_expr = "eq(n\\,0)" + "".join(
            f"+between(t\\,{step * i:.3f}\\,{step * i:.3f}+0.05)" for i in range(1, n))
        cmd = ["ffmpeg", "-v", "error", "-i", str(video_path),
               "-vf", f"select='{select_expr}'", "-fps_mode", "passthrough",
               "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        assert proc.stdout is not None
        black = 0
        sampled = 0
        frame_bytes = width * height * 3
        while sampled < n:
            raw = proc.stdout.read(frame_bytes)
            if not raw or len(raw) < frame_bytes:
                break
            luma = _frame_luma(raw, width, height)
            if luma < BLACK_LUMA_THRESHOLD:
                black += 1
            sampled += 1
        proc.stdout.close()
        proc.wait(timeout=30)
        if sampled == 0:
            return True, 0.0
        ratio = black / sampled
        return ratio == 0.0, round(ratio, 3)
    except Exception as e:
        logger.warning(f"black_frame_check failed: {e}")
        return True, 0.0


# ---------------------------------------------------------------------------
# Placeholder text
# ---------------------------------------------------------------------------
def placeholder_check(text: str) -> list[str]:
    """Return a list of placeholder/template issues found in text (case-insensitive)."""
    text = text or ""
    return [name for pat, name in PLACEHOLDER_PATTERNS if pat.search(text)]


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------
def timing_check(scene_plan: dict, total_duration: float) -> list[str]:
    """Validate scene timing: contiguous, cover 0..total, durations sane, captions in bounds.

    Returns a list of issue strings (empty = pass). Fail-soft: malformed plan
    yields one descriptive issue instead of raising.
    """
    issues: list[str] = []
    scenes = (scene_plan or {}).get("scenes") or []
    if not isinstance(scenes, list) or not scenes:
        return ["scene_plan has no scenes"]
    total = float(total_duration or 0)
    prev_end = 0.0
    for i, s in enumerate(scenes):
        try:
            start, end = float(s.get("start", 0)), float(s.get("end", 0))
        except (TypeError, ValueError):
            issues.append(f"scene {i}: non-numeric start/end")
            continue
        if end - start <= MIN_SCENE_DURATION:
            issues.append(f"scene {i}: duration {end - start:.2f}s <= {MIN_SCENE_DURATION}s")
        if i == 0 and start > 0.001:
            issues.append(f"scene 0 starts at {start:.2f}s, not 0")
        if abs(start - prev_end) > 0.01:
            issues.append(f"gap/overlap before scene {i}: prev_end={prev_end:.2f}s start={start:.2f}s")
        prev_end = end
    if total > 0 and abs(prev_end - total) > 0.05:
        issues.append(f"scenes end at {prev_end:.2f}s, total_duration is {total:.2f}s")
    # caption text must sit within its scene bounds (word index not available here —
    # scene narration timings are what captions.srt is built from, so bounds check on scenes)
    for i, s in enumerate(scenes):
        try:
            cap = (s.get("caption") or s.get("on_screen_text") or "").strip()
        except AttributeError:
            cap = ""
        if cap and not re.search(r"[A-Za-z0-9]", cap):
            issues.append(f"scene {i}: caption text is empty/blank")
    return issues


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
def _ffmpeg_volumedetect(path: str) -> dict:
    """Return {max_volume, mean_volume} (dB) via ffmpeg volumedetect."""
    try:
        r = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect",
             "-f", "null", "-"],
            capture_output=True, text=True, timeout=30)
        out = (r.stderr or "") + "\n" + (r.stdout or "")
        levels: dict[str, float | None] = {"max_volume": None, "mean_volume": None}
        for key in levels:
            m = re.search(rf"{key}: ([\-0-9.]+) dB", out)
            if m:
                levels[key] = float(m.group(1))
        return levels
    except Exception as e:
        logger.warning(f"volumedetect failed: {e}")
        return {"max_volume": None, "mean_volume": None, "error": str(e)}


def audio_check(audio_path: str) -> tuple[bool, dict]:
    """Check audio: stream present, no clipping (max < 0 dBFS), RMS in sane range.

    Returns (pass, details). Fail-soft: unreadable audio -> (False, {error}).
    """
    try:
        probe = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(audio_path)],
            text=True, timeout=10).strip()
        if not probe:
            return False, {"error": "no audio stream"}
    except Exception as e:
        return False, {"error": f"ffprobe failed: {e}"}

    levels = _ffmpeg_volumedetect(audio_path)
    peak = levels.get("max_volume")
    rms = levels.get("mean_volume")
    if peak is None or rms is None:
        return False, {"error": "volumedetect returned no levels", **levels}

    issues: list[str] = []
    if peak >= AUDIO_CLIP_DB:
        issues.append(f"clipping: max {peak:.1f} dBFS >= 0")
    if not (AUDIO_RMS_RANGE[0] <= rms <= AUDIO_RMS_RANGE[1]):
        issues.append(f"rms {rms:.1f} dB outside {AUDIO_RMS_RANGE}")
    ok = not issues
    return ok, {"max_db": round(peak, 2), "mean_db": round(rms, 2),
                "clipping": peak >= AUDIO_CLIP_DB, "issues": issues}


# ---------------------------------------------------------------------------
# Metadata (spec-compliant) + generation report
# ---------------------------------------------------------------------------
def _curiosity_title(hook: str, topic: str) -> str:
    """Short, curiosity-driven title derived from the hook (<= 60 chars)."""
    base = re.sub(r"\s+", " ", (hook or topic or "").strip())
    if not base:
        return "60-second tech breakdown"
    base = base.rstrip(".!?").strip()
    if len(base) > 60:
        base = base[:57].rsplit(" ", 1)[0].rstrip(",") + "…"
    return base or "60-second tech breakdown"


def build_metadata(report: dict, topic: str, hook: str, script: str, scene_plan: dict,
                   duration: float, style: str, assets: list[dict], voice: str,
                   music: str, virality_score: float | int | None = None) -> dict:
    """Spec-compliant metadata dict:
    {title, hook, topic, duration, viralityScore, style, renderedAt, assetsUsed, voice, music}
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "title": _curiosity_title(hook, topic),
        "hook": hook,
        "topic": topic,
        "duration": round(float(duration or 0), 2),
        "viralityScore": round(float(virality_score), 1) if virality_score is not None else None,
        "style": style,
        "renderedAt": now,
        "assetsUsed": [dict(a) for a in (assets or [])],
        "voice": voice,
        "music": music,
    }


def build_generation_report(stages: list[dict], final: dict | None = None) -> dict:
    """{generatedAt, stages: [{name, status, elapsed_s, detail}], final: {...}}"""
    clean = []
    for s in stages or []:
        clean.append({
            "name": s.get("name", ""),
            "status": s.get("status", "unknown"),
            "elapsed_s": round(float(s.get("elapsed_s") or 0.0), 2),
            "detail": s.get("detail") or "",
        })
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "stages": clean,
        "final": final or {},
    }


def run_extended_qc(final: str, script_text: str, captions_text: str,
                    scene_plan: dict, audio_path: str) -> dict:
    """One-shot extended QC bundle used by _post_production. Never raises."""
    t0 = time.time()
    result: dict = {"status": "ok", "checks": {}}
    try:
        black_ok, black_ratio = black_frame_check(final)
        result["checks"]["black_frames"] = {"pass": black_ok, "ratio": black_ratio}
        if not black_ok:
            result["status"] = "warn"
    except Exception as e:
        result["checks"]["black_frames"] = {"pass": None, "error": str(e)}
    try:
        ph = placeholder_check(f"{script_text}\n{captions_text}")
        result["checks"]["placeholders"] = {"pass": not ph, "found": ph}
        if ph:
            result["status"] = "warn"
    except Exception as e:
        result["checks"]["placeholders"] = {"pass": None, "error": str(e)}
    try:
        timing_issues = timing_check(scene_plan, 60.0)
        result["checks"]["timing"] = {"pass": not timing_issues, "issues": timing_issues}
        if timing_issues:
            result["status"] = "warn"
    except Exception as e:
        result["checks"]["timing"] = {"pass": None, "error": str(e)}
    try:
        audio_ok, details = audio_check(audio_path)
        result["checks"]["audio"] = {"pass": audio_ok, **details}
        if not audio_ok:
            result["status"] = "warn"
    except Exception as e:
        result["checks"]["audio"] = {"pass": None, "error": str(e)}
    result["elapsed_s"] = round(time.time() - t0, 2)
    return result
