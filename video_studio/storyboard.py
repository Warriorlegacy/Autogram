"""Compile a Brief into a timed storyboard + a HyperFrames project on disk.

One module: brief -> scenes w/ absolute start times -> index.html -> project dir.
No async, no framework. Every animation time is written explicitly.
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .brief import REPO_ROOT, Brief, load_brand

TEMPLATES = Path(__file__).parent / "templates"
BRIEFS_DIR = Path(__file__).parent / "briefs"
WORK_DIR = Path(__file__).parent / "work"
ASSETS = REPO_ROOT / "assets"
# Brand fonts live with the package so the render does not depend on a CDN.
FONTS = Path(__file__).parent / "assets" / "fonts"

HEAD_CLASS = {"hook": "", "feature_card": "sm", "metrics": "sm", "terminal": "sm",
              "browser": "sm", "end_card": "sm", "statement": ""}


@dataclass
class CaptionCue:
    id: str
    text: str
    start: float
    end: float
    dur: float


@dataclass
class CompiledScene:
    id: str
    visual: str
    start: float
    duration: float
    start_plus_dur: float
    narration: str
    headline: str
    subtext: str
    eyebrow: str
    bullets: list[str]
    metrics: list[dict[str, str]]
    source_url: str
    head_class: str


@dataclass
class Storyboard:
    slug: str
    width: int
    height: int
    fps: int
    total: float
    endcard_at: float
    endcard_head: str
    endcard_sub: str
    counter: str
    scenes: list[CompiledScene]
    captions: list[CaptionCue]
    audio: str | None
    accent: str
    cta: str


def _read_speed() -> float:
    """Captions are burned in, so they must not outrun comfortable reading."""
    return 15.0  # chars/sec, mobile-first. ponytail: one knob, tune per channel.


def _split_cues(text: str) -> list[str]:
    """Split narration into caption-sized chunks on sentence boundaries.

    Naive '.' splitting breaks tokens like 'Three.js', so only split when the
    dot is followed by whitespace+capital/end — i.e. a real sentence end.
    """
    import re
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
    # A single sentence too long for one line becomes two balanced halves.
    # 62 chars is the widest line that fits the caption box at 1080px without
    # wrapping to a third line, which would clip against the IG UI zone.
    out: list[str] = []
    for p in parts:
        if len(p) > 62:
            words, half, cur = p.split(), len(p.split()) // 2, []
            for i, w in enumerate(words):
                cur.append(w)
                if i == half - 1 or (len(" ".join(cur)) > 46 and i >= half):
                    out.append(" ".join(cur))
                    cur = []
            if cur:
                out.append(" ".join(cur))
        else:
            out.append(p)
    return out


def build_captions(scenes: list[dict], fps: int) -> list[CaptionCue]:
    """One cue per narration chunk, held for reading time, never exceeding its scene."""
    cues: list[CaptionCue] = []
    for sc in scenes:
        narration = (sc.get("narration") or "").strip()
        if not narration:
            continue
        parts = _split_cues(narration)
        if not parts:
            continue
        start, dur = sc["start"], sc["duration"]
        # Each cue gets AT LEAST its own reading time; the leftover is shared out
        # proportionally. narration_fit() guarantees sum(len/rate) + 0.4 <= dur,
        # so the minimum always fits and the reading budget holds by construction.
        mins = [len(p) / _read_speed() for p in parts]
        weights = [len(p) for p in parts]
        spare = dur - sum(mins)
        if spare < 0:
            spare = 0.0
        total_chars = sum(weights) or 1
        t_acc = 0.0
        for i, part in enumerate(parts):
            share = mins[i] + spare * (weights[i] / total_chars)
            s = start + t_acc
            e = min(s + share, start + dur - 0.02)
            t_acc += share
            if e <= s:
                continue
            cues.append(CaptionCue(id=f"cap-{sc['id']}-{i}", text=part, start=round(s, 3),
                                   end=round(e, 3), dur=round(e - s, 3)))
    return cues


def compile_storyboard(brief: Brief, narration_duration: float | None = None) -> Storyboard:
    brand = load_brand()
    colors = brand["design"]["colors"]
    accent = brief.accent or colors["accent"]

    scenes: list[CompiledScene] = []
    captions: list[CaptionCue] = []
    t = 0.0
    raw: list[dict] = []
    for s in brief.scenes:
        d = s.duration
        raw.append({"id": s.id, "visual": s.visual, "start": round(t, 3), "duration": d,
                    "narration": s.narration, "headline": s.headline, "subtext": s.subtext,
                    "eyebrow": s.eyebrow, "bullets": s.bullets, "metrics": s.metrics,
                    "source_url": s.source_url})
        t += d

    body = round(t, 3)
    # Reserve a fixed end card, but never let it eat more than 35% of the runtime.
    end_dur = round(min(4.5, max(3.0, body * 0.16)), 3)
    endcard_at = round(body, 3)
    total = round(body + end_dur, 3)

    captions = build_captions(raw, brief.fps)
    # If narration audio is longer than the scene stack, stretch total (never the speech).
    if narration_duration and narration_duration > body:
        total = round(narration_duration + end_dur, 3)

    for i, r in enumerate(raw):
        end = min(r["start"] + r["duration"], endcard_at)
        scenes.append(CompiledScene(
            id=r["id"], visual=r["visual"], start=r["start"],
            duration=round(end - r["start"], 3), start_plus_dur=round(end - 0.35, 3),
            narration=r["narration"], headline=r["headline"], subtext=r["subtext"],
            eyebrow=r["eyebrow"], bullets=r["bullets"], metrics=r["metrics"],
            source_url=r["source_url"], head_class=HEAD_CLASS.get(r["visual"], "")))

    return Storyboard(
        slug=brief.slug, width=brief.width, height=brief.height, fps=brief.fps,
        total=total, endcard_at=endcard_at,
        endcard_head=brief.title, endcard_sub=brief.hook,
        counter=f"{len(raw):02d}", scenes=scenes, captions=captions, audio=None,
        accent=accent, cta=brief.cta)


def _to_dict(s: Storyboard) -> dict:
    d = asdict(s)
    d.pop("audio", None)
    return d


def write_project(brief: Brief, sb: Storyboard, audio_rel: str | None = None,
                  logo_rel: str | None = None) -> Path:
    proj = WORK_DIR / brief.slug
    if proj.exists():
        shutil.rmtree(proj)
    (proj / "assets").mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), undefined=StrictUndefined,
                      autoescape=False, trim_blocks=False, lstrip_blocks=False)
    tpl = env.get_template("composition.html.jinja2")

    logo_src = ASSETS / "signhify-logo-vector.png"
    if logo_rel is None and logo_src.exists():
        shutil.copy2(logo_src, proj / "assets" / "logo.png")
        logo_rel = "assets/logo.png"

    # Copy the local font set so an offline render keeps real typography.
    # fonts.css ships INSIDE fonts/ so its relative url('font_NN.woff2') resolves
    # against the same directory. Copying it to assets/ broke every font lookup.
    if FONTS.exists():
        shutil.rmtree(proj / "assets" / "fonts", ignore_errors=True)
        shutil.copytree(FONTS, proj / "assets" / "fonts")

    sb.audio = audio_rel
    html = tpl.render(brief=brief, logo=logo_rel, **_to_dict(sb))
    (proj / "index.html").write_text(html, encoding="utf-8")

    (proj / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True}}, indent=2), encoding="utf-8")
    (proj / "meta.json").write_text(json.dumps(
        {"id": brief.slug, "name": brief.slug, "createdAt": "2026-10-11T00:00:00.000Z"}, indent=2), encoding="utf-8")
    (proj / "package.json").write_text(json.dumps({
        "name": brief.slug, "private": True, "type": "module", "scripts": {
            "check": "npx --yes hyperframes check",
            "render": "npx --yes hyperframes render -f 30 -q draft -o reel.mp4",
            "snapshot": "npx --yes hyperframes snapshot"}}, indent=2), encoding="utf-8")
    return proj


def narration_fit(brief: Brief) -> list[dict]:
    """Scenes whose narration cannot be spoken AND read inside its slot.

    Fail-closed: a scene that overruns forces the author to lengthen the scene,
    because the alternative is captions or speech the viewer cannot follow.
    """
    bad = []
    for s in brief.scenes:
        parts = _split_cues((s.narration or "").strip()) if s.narration else []
        need = sum(max(len(p) / _read_speed(), 0.0) for p in parts)
        if parts and need > s.duration + 0.05:
            bad.append({"id": s.id, "duration": s.duration,
                        "needed": round(need, 2),
                        "short_by": round(need - s.duration, 2)})
    return bad


def demo() -> None:
    """Minimal self-check: two scenes compile to monotonic, in-bounds timing."""
    from .brief import Scene
    b = Brief(slug="compile_demo", title="Demo", hook="H",
              scenes=[Scene(id="a", visual="hook", duration=3.0, narration="One. Two."),
                      Scene(id="b", visual="metrics", duration=4.0, metrics=[{"v": "400+", "k": "frames"}])])
    sb = compile_storyboard(b)
    assert len(sb.scenes) == 2
    assert sb.scenes[0].start == 0.0 and sb.scenes[1].start == 3.0
    assert sb.endcard_at == 7.0 and sb.total > sb.endcard_at
    for s in sb.scenes:
        assert s.start + s.duration <= sb.endcard_at + 0.001, s
    assert sb.captions and all(c.end > c.start for c in sb.captions)


if __name__ == "__main__":
    demo()
    print("storyboard.py self-check OK")