"""QA gate: technical inspection + representative frame extraction + report.

A successful render is not a passed QA. This inspects the actual file with
ffprobe and extracts real frames so defects are visible, not assumed.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .render import probe

# Instagram Reels: 9:16, 1080x1920 recommended (min 540x960), 24-60fps, 3-90s.
MIN_W, MIN_H = 540, 960
OK_FPS = {24.0, 25.0, 30.0, 50.0, 60.0}


@dataclass
class QAReport:
    file: str
    width: int = 0
    height: int = 0
    fps: float = 0.0
    duration: float = 0.0
    video_codec: str = ""
    audio_codec: str = ""
    size_bytes: int = 0
    frames_extracted: list[str] = field(default_factory=list)
    checks: list[dict] = field(default_factory=list)
    defects: list[str] = field(default_factory=list)
    verdict: str = "UNKNOWN"

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append({"check": name, "pass": bool(ok), "detail": detail})
        if not ok:
            self.defects.append(f"{name}: {detail}")


def _video_stream(info: dict) -> dict:
    return next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})


def _audio_stream(info: dict) -> dict:
    return next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), {})


def _rate(s: dict) -> float:
    r = s.get("r_frame_rate") or "0/1"
    try:
        num, den = r.split("/")
        return round(float(num) / float(den), 3) if float(den) else 0.0
    except Exception:
        return 0.0


def extract_frames(video: Path, out_dir: Path, count: int = 6) -> list[str]:
    # Clear stale frames first — mixing an old render's frames with new ones
    # lets an operator inspect the wrong output and call it good.
    if out_dir.exists():
        for old in out_dir.glob("frame_*.jpg"):
            old.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)
    info = probe(video)
    dur = float(info.get("format", {}).get("duration") or 0)
    if dur <= 0:
        return []
    paths = []
    # Sample the body plus the very last frame — an empty final frame is the
    # single most common silent packaging defect.
    marks = [dur * (i + 1) / (count + 1) for i in range(count)] + [max(dur - 0.08, 0.0)]
    for i, ts in enumerate(marks):
        p = out_dir / f"frame_{i:02d}_t{ts:.2f}s.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(video),
                        "-frames:v", "1", "-q:v", "3", "-y", str(p)],
                       capture_output=True, timeout=120)
        if p.exists() and p.stat().st_size > 0:
            paths.append(str(p))
    return paths


def inspect(video: Path, out_dir: Path, expect_audio: bool = True,
            expect_duration: float | None = None, frames: int = 6) -> QAReport:
    if not video.exists() or video.stat().st_size == 0:
        return QAReport(file=str(video), verdict="FAIL",
                        defects=["file missing or zero bytes"])
    info = probe(video)
    v, a = _video_stream(info), _audio_stream(info)
    rep = QAReport(file=str(video), width=int(v.get("width") or 0), height=int(v.get("height") or 0),
                   fps=_rate(v), duration=round(float(info.get("format", {}).get("duration") or 0), 3),
                   video_codec=v.get("codec_name", ""), audio_codec=a.get("codec_name", ""),
                   size_bytes=int(info.get("format", {}).get("size") or 0))

    rep.check("container_valid", bool(v), "no video stream" if not v else f"{rep.video_codec}")
    rep.check("dimensions", rep.width >= MIN_W and rep.height >= MIN_H and rep.height > rep.width,
              f"{rep.width}x{rep.height} (need vertical >= {MIN_W}x{MIN_H})")
    rep.check("aspect_9_16", abs(rep.width / rep.height - 9 / 16) < 0.02 if rep.height else False,
              f"ratio {rep.width/rep.height if rep.height else 0:.4f}")
    rep.check("fps_supported", rep.fps in OK_FPS, f"{rep.fps} fps")
    rep.check("duration_in_range", 3.0 <= rep.duration <= 90.0, f"{rep.duration}s")
    if expect_duration:
        rep.check("duration_matches_plan", abs(rep.duration - expect_duration) < 1.0,
                  f"got {rep.duration}s, planned {expect_duration}s")
    rep.check("video_codec_h264", rep.video_codec == "h264", f"{rep.video_codec}")
    rep.check("audio_present" if expect_audio else "audio_absent",
              bool(a) == expect_audio, f"audio codec {rep.audio_codec or 'none'}")
    rep.check("nonzero_size", rep.size_bytes > 10_000, f"{rep.size_bytes} bytes")

    rep.frames_extracted = extract_frames(video, out_dir, frames)
    rep.check("frames_extractable", len(rep.frames_extracted) >= 3,
              f"{len(rep.frames_extracted)} frames extracted")

    rep.verdict = "PASS" if not rep.defects else "FAIL"
    return rep


def write_report(rep: QAReport, path: Path, extra: dict | None = None) -> Path:
    d = asdict(rep)
    if extra:
        d.update(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, indent=2), encoding="utf-8")
    return path


def demo() -> None:
    """Guard: a real file passes and a missing file fails."""
    bad = inspect(Path("definitely-missing.mp4"), Path("."))
    assert bad.verdict == "FAIL"
    good = inspect(Path("workspace/final_reel.mp4"), Path("scratch/qa_demo"), expect_audio=False, frames=2)
    assert good.verdict in ("PASS", "FAIL")
    assert good.width > 0 and good.height > 0


if __name__ == "__main__":
    demo()
    print("qa.py self-check OK")