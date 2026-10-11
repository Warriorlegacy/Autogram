"""Content brief schema + validation. The pipeline's input contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_brand() -> dict[str, Any]:
    return json.loads((REPO_ROOT / "data" / "brand.json").read_text(encoding="utf-8"))


# ponytail: enforce the brand's own avoid-list here, not in every prompt.
# One guard at the boundary beats a check per caller.
def banned_phrases() -> list[str]:
    return [p.strip().lower() for p in load_brand().get("avoid", [])]


class Caption(BaseModel):
    text: str
    start: float = Field(ge=0)
    end: float = Field(gt=0)

    @field_validator("end")
    @classmethod
    def _after_start(cls, v: float, info):
        s = info.data.get("start")
        if s is not None and v <= s:
            raise ValueError("caption end must be after start")
        return v


class Scene(BaseModel):
    id: str
    visual: str = Field(description="Component name, e.g. hook, feature_card, end_card")
    duration: float = Field(gt=0)
    narration: str = ""
    headline: str = ""
    subtext: str = ""
    eyebrow: str = ""
    bullets: list[str] = Field(default_factory=list)
    metrics: list[dict[str, str]] = Field(default_factory=list)
    source_url: str = ""

    @field_validator("narration", "headline", "subtext", "eyebrow", "source_url",
                     mode="before")
    @classmethod
    def _null_is_empty(cls, v):
        # An LLM emits `null` for an unused optional field constantly. That is
        # absent, not invalid — coercing here keeps one bad field from failing
        # an otherwise good generation.
        return "" if v is None else v

    @field_validator("bullets", mode="before")
    @classmethod
    def _null_list(cls, v):
        if v is None:
            return []
        return ["" if x is None else x for x in v] if isinstance(v, list) else v

    @field_validator("metrics", mode="before")
    @classmethod
    def _null_metrics(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            return v
        # Accept ["400+ frames"] as well as [{"v":..,"k":..}]
        out = []
        for m in v:
            if isinstance(m, str) and m.strip():
                parts = m.split(" ", 1)
                out.append({"v": parts[0], "k": parts[1] if len(parts) > 1 else ""})
            elif isinstance(m, dict):
                out.append({str(k): ("" if val is None else str(val)) for k, val in m.items()})
        return out


class Brief(BaseModel):
    slug: str
    title: str
    pillar: str = "product"
    hook: str
    cta: str = "Follow @signhify.studio for more."
    accent: str = ""
    notes: str = ""
    width: int = 1080
    height: int = 1920
    fps: int = Field(default=30, ge=24, le=60)
    target_duration: float = Field(default=40.0, gt=0)
    narration_enabled: bool = True
    sources: list[str] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)

    @field_validator("slug")
    @classmethod
    def _slug_safe(cls, v: str) -> str:
        if not v or not all(c.isalnum() or c in "-_" for c in v):
            raise ValueError(f"slug must be alphanumeric with -/_ only, got {v!r}")
        return v

    @field_validator("accent")
    @classmethod
    def _hex(cls, v: str) -> str:
        if v and not (len(v) == 7 and v.startswith("#") and all(c in "0123456789abcdefABCDEF" for c in v[1:])):
            raise ValueError(f"accent must be #RRGGBB, got {v!r}")
        return v

    def banned_hits(self) -> list[str]:
        """Brand `avoid` phrases found anywhere in audience-facing copy."""
        blob = " ".join(
            [self.title, self.hook, self.cta]
            + [v for s in self.scenes for v in (s.narration, s.headline, s.subtext, s.eyebrow, " ".join(s.bullets))]
        ).lower()
        return sorted({p for p in banned_phrases() if p in blob})

    def total_duration(self) -> float:
        return round(sum(s.duration for s in self.scenes), 3)


def load_brief(path: str | Path) -> Brief:
    p = Path(path)
    if not p.is_absolute():
        p = (REPO_ROOT / p).resolve()
    if not p.exists():
        raise FileNotFoundError(f"brief not found: {p}")
    return Brief.model_validate(json.loads(p.read_text(encoding="utf-8")))


def demo() -> Brief:
    """Minimal self-check: validates the schema and the brand guard."""
    b = Brief(
        slug="smoke",
        title="Signhify Studio",
        hook="A hook that avoids every banned phrase.",
        scenes=[Scene(id="s1", visual="hook", duration=3.0, headline="Signhify")],
    )
    assert b.total_duration() == 3.0
    assert b.banned_hits() == []
    bad = Brief(slug="x", title="t", hook="This is a game-changer", scenes=[Scene(id="s", visual="hook", duration=1)])
    assert "game-changer" in bad.banned_hits()
    try:
        Brief(slug="bad slug!", title="t", hook="h", scenes=[Scene(id="s", visual="hook", duration=1)])
        raise AssertionError("slug guard failed")
    except ValueError:
        pass
    return b


if __name__ == "__main__":
    demo()
    print("brief.py self-check OK")