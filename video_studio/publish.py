"""Publication packaging: SRT, cover image, caption, asset manifest, Instagram payload.

Publishing is NEVER done here. This module only produces the package; the
publish step is explicit, opt-in, and disabled by default.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .storyboard import CaptionCue, Storyboard

HASHTAGS = ["#signhifystudio", "#vibecoding", "#ai3d", "#webdev", "#buildinpublic", "#startupindia"]


def _ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues: list[CaptionCue], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, c in enumerate(cues, 1):
        lines += [str(i), f"{_ts(c.start)} --> {_ts(c.end)}", c.text, ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def extract_cover(video: Path, cover: Path, at: float = 0.9) -> Path:
    """Dedicated thumbnail: a clean hero frame, not a mid-transition mush."""
    cover.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{at:.3f}", "-i", str(video),
                    "-frames:v", "1", "-q:v", "2", "-y", str(cover)],
                   capture_output=True, timeout=120)
    return cover


def build_caption(brief, sb: Storyboard) -> str:
    tags = " ".join(HASHTAGS)
    return (f"{brief.hook}\n\n"
            f"{brief.title} — built from a single prompt.\n\n"
            f"{tags}\n\n"
            f"{brief.cta}")


def write_package(brief, sb: Storyboard, out_dir: Path, video: Path | None = None,
                  assets: list[dict] | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_srt(sb.captions, out_dir / "captions.srt")
    (out_dir / "caption.txt").write_text(build_caption(brief, sb), encoding="utf-8")
    (out_dir / "storyboard.json").write_text(
        json.dumps({"slug": sb.slug, "total": sb.total, "endcard_at": sb.endcard_at,
                    "scenes": [s.__dict__ for s in sb.scenes],
                    "captions": [c.__dict__ for c in sb.captions]}, indent=2), encoding="utf-8")
    (out_dir / "brief.json").write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    manifest = {
        "slug": brief.slug, "generated": "2026-10-11",
        "video": str(video) if video else None,
        "spec": {"width": sb.width, "height": sb.height, "fps": sb.fps,
                 "duration": sb.total, "aspect": "9:16", "codec": "h264"},
        "publishing": {"enabled": False, "reason": "opt-in via --publish; never default"},
        "assets": assets or [],
    }
    (out_dir / "asset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def demo() -> None:
    from .brief import Scene
    from .brief import Brief as B
    from .storyboard import compile_storyboard
    b = B(slug="pkg", title="T", hook="H", scenes=[Scene(id="a", visual="hook", duration=3, narration="Hi.")])
    sb = compile_storyboard(b)
    cues = sb.captions
    assert cues and _ts(cues[0].end) > _ts(cues[0].start)
    assert _ts(3661.5) == "01:01:01,500"
    assert "game-changer" not in build_caption(b, sb)


if __name__ == "__main__":
    demo()
    print("publish.py self-check OK")