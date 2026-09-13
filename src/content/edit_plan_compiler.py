"""
Edit plan compiler (Makerzz P5 gate).

Separates all NON-spoken production instructions from the spoken script.
The spoken script stays pure (P3); everything visual/temporal lives here:

  - visual beats and camera framing (cut, punch-in, zoom)
  - kinetic subtitle timings and highlight triggers
  - B-roll search queries / background assets
  - SFX cue points and transitions

Output: edit_plan.json inside the run workspace.
"""

from dataclasses import dataclass, field

# Beat templates per emotional arc position
BEAT_FRAMING = {
    "hook": {"shot": "medium-close", "framing": "direct-to-camera", "motion": "punch-in"},
    "tension": {"shot": "close", "framing": "low-angle", "motion": "slow-zoom"},
    "mechanism": {"shot": "over-shoulder", "framing": "screen-share", "motion": "cut"},
    "proof": {"shot": "close-up", "framing": "receipt-on-screen", "motion": "cut"},
    "payoff": {"shot": "medium", "framing": "direct-to-camera", "motion": "pull-back"},
    "cta": {"shot": "medium-close", "framing": "direct-to-camera", "motion": "freeze"},
}

# SFX cue map
SFX_MAP = {
    "hook": "whoosh-transition",
    "tension": "low-drone",
    "mechanism": "keyboard-click",
    "proof": "cash-register",
    "payoff": "uplift-rise",
    "cta": "button-click",
}

# Subtitle highlight trigger words per beat
HIGHLIGHT_TRIGGERS = {
    "hook": ["never", "stop", "secret", "mistake"],
    "mechanism": ["because", "exactly", "step"],
    "proof": ["proven", "data", "result"],
    "cta": ["comment", "follow", "start"],
}


@dataclass
class EditBeat:
    index: int
    purpose: str
    start_sec: float
    end_sec: float
    framing: dict
    sfx: str
    subtitle_style: dict
    broll_queries: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "purpose": self.purpose,
            "timing": {"start_sec": self.start_sec, "end_sec": self.end_sec},
            "framing": self.framing,
            "sfx": self.sfx,
            "subtitle_style": self.subtitle_style,
            "broll_queries": self.broll_queries,
        }


def compile_edit_plan(
    script_text: str,
    estimated_seconds: float | None = None,
    carousel_slides: list[dict] | None = None,
) -> dict:
    """
    Compile a production edit plan from a verified spoken script.

    This is deterministic (no LLM required) — beats are derived from sentence
    boundaries and mapped through the framing/SFX tables. Keeps the spoken
    script and production instructions fully separated.
    """
    import re

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script_text.strip()) if s.strip()]
    if not sentences:
        return {"beats": [], "total_duration_sec": 0.0, "note": "empty script"}

    if estimated_seconds is None:
        estimated_seconds = max(1.0, len(script_text) / 15.0)

    sec_per_sentence = estimated_seconds / len(sentences)

    arc = ["hook", "tension", "mechanism", "proof", "payoff", "cta"]
    beats: list[EditBeat] = []
    for i, sentence in enumerate(sentences):
        purpose = arc[min(i * len(arc) // len(sentences), len(arc) - 1)]
        framing = BEAT_FRAMING[purpose]
        start = round(i * sec_per_sentence, 2)
        end = round((i + 1) * sec_per_sentence, 2)

        words = sentence.split()
        broll = []
        if purpose == "mechanism":
            # grab 2-3 salient keywords for stock/B-roll search
            keywords = [w.lower().strip(".,!?") for w in words if len(w) > 5]
            broll = keywords[:3]

        beats.append(
            EditBeat(
                index=i + 1,
                purpose=purpose,
                start_sec=start,
                end_sec=end,
                framing=dict(framing),
                sfx=SFX_MAP[purpose],
                subtitle_style={
                    "kinetic": True,
                    "highlight_words": [
                        w for w in HIGHLIGHT_TRIGGERS.get(purpose, [])
                        if w in sentence.lower()
                    ],
                    "max_chars_per_line": 32,
                },
                broll_queries=broll,
            )
        )

    plan = {
        "version": "1.0",
        "source": "spoken_script",
        "total_duration_sec": round(estimated_seconds, 2),
        "total_beats": len(beats),
        "beats": [b.to_dict() for b in beats],
        "transitions": {"default": "hard-cut", "beat_1_to_2": "whoosh"},
        "overlay": {"watermark": "signhify.studio", "position": "bottom-right"},
        "note": "Non-spoken production instructions only. Spoken text lives in script.txt (P3).",
    }
    return plan
