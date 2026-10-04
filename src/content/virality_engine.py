"""Virality scoring + gating, topic selection, psychology triggers, hook A/B,
and the 12-template content registry for the Signhify 60s reel engine.

Everything here is deterministic and offline-safe: LLM providers are used
best-effort with static fallback pools (mirrors src.content.script60, whose
`_llm_json` and `generate_hooks` are reused — never hard-fail when the LLM
is unavailable).
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_FILE = REPO_ROOT / "data" / "templates.json"

# Virality gate: only concepts >= 75/100 may proceed.
GATE = 75.0
# Topic novelty penalty applied when a topic already appears in content-memory.
NOVELTY_PENALTY = 25.0

# Exact virality weights (sums to 1.0). Scores are 0-100.
WEIGHTS = {
    "hook_strength": 0.20,
    "curiosity": 0.15,
    "information_value": 0.15,
    "visual_novelty": 0.15,
    "retention_potential": 0.15,
    "shareability": 0.10,
    "replayability": 0.05,
    "cta_quality": 0.05,
}

# Topic selection weights (sums to 1.0). Factors are 0-100.
TOPIC_WEIGHTS = {
    "trend": 0.20,
    "curiosity": 0.20,
    "utility": 0.20,
    "visual_potential": 0.15,
    "shareability": 0.15,
    "brand_fit": 0.10,
}

# Psychology triggers and their one-line narrative guidance.
PSYCH_TRIGGERS = [
    "CURIOSITY", "SURPRISE", "FEAR", "OPPORTUNITY", "STATUS", "MONEY",
    "PRODUCTIVITY", "FUTURE", "DISCOVERY", "CONTROVERSY", "AWE",
]
PSYCH_KEYWORDS = {
    "CURIOSITY": ["why", "how does", "secret", "actually", "never seen",
                  "what happens", "nobody told you", "?"],
    "SURPRISE": ["shock", "unexpected", "suddenly", "wow", "nobody expected",
                 "blew my mind", "overnight", "stunned"],
    "FEAR": ["replace", "replacing", "replaced", "lose", "losing", "job",
             "jobs", "obsolete", "outdated", "fired", "killing", "die"],
    "OPPORTUNITY": ["stop paying", "free", "save", "side hustle", "get ahead",
                    "opportunity", "unlock", "early access"],
    "STATUS": ["top", "elite", "pro", "engineers", "senior", "expert",
               "insider", "advanced"],
    "MONEY": ["$", "money", "cash", "revenue", "income", "profit", "earn",
              "make money", "pricing", "thousand"],
    "PRODUCTIVITY": ["save", "time", "hours", "faster", "efficient",
                     "efficiency", "workflow", "automate", "automation",
                     "productive", "streamline"],
    "FUTURE": ["future", "2027", "2028", "2029", "coming", "next wave",
               "tomorrow", "trend"],
    "DISCOVERY": ["found", "discover", "new tool", "new model", "launched",
                  "released", "just dropped", "brand new", "hidden"],
    "CONTROVERSY": ["wrong", "myth", "debate", "controvers", "overrated",
                    "backlash", "hate", "contradict", "everyone is"],
    "AWE": ["impressive", "amazing", "incredible", "mind-blowing", "best",
            "beautiful", "spectacular", "insane", "demo"],
}
PSYCH_GUIDANCE = {
    "CURIOSITY": "Open with a question or knowledge gap and delay the reveal until the payoff lands.",
    "SURPRISE": "Lead with the counter-intuitive result, then walk backwards to how it happened.",
    "FEAR": "Name the risk plainly in the first 5 seconds, then pivot to the concrete control that removes it.",
    "OPPORTUNITY": "Lead with the win the viewer can get, then show the exact path in under 60 seconds.",
    "STATUS": "Position the viewer as the person who knows before the crowd does; keep the tone insider, not braggy.",
    "MONEY": "Open with the number or saving, then prove it with a concrete workflow, never a fake stat.",
    "PRODUCTIVITY": "Show the hours saved immediately, then demonstrate the workflow step by step.",
    "FUTURE": "Paint the near-term shift as already underway, and ground it in what exists today.",
    "DISCOVERY": "Treat the topic as a fresh find worth sharing; show it, don't just claim it.",
    "CONTROVERSY": "State the contrarian claim up front, then earn it with evidence and acknowledge the other side.",
    "AWE": "Let the impressive moment play visually first, then explain how it works.",
}

# Static A/B fallback pools (used only when the LLM is down).
STATIC_VISUALS = [
    "Terminal screencast: real commands with glowing typing animation, picture-in-picture demo",
    "Kinetic typography: word-by-word bold captions over ambient tech b-roll, beat-synced",
    "Split-screen before/after: legacy workflow vs AI workflow with a countdown timer overlay",
]
_HOOK_PATTERNS = [
    "The AI tool nobody is talking about: {topic}",
    "I tested {topic} so you don't have to.",
    "You can do {topic} for free today.",
    "Why {topic} is the most underrated workflow right now.",
    "Stop doing {topic} by hand. Here's the fix.",
    "{topic} in 60 seconds, no fluff.",
]


# ─── Templates registry ──────────────────────────────────────────────────────
def _load_templates() -> dict[str, dict]:
    """Load the 12 reel content templates from data/templates.json."""
    try:
        data = json.loads(TEMPLATES_FILE.read_text(encoding="utf-8"))
        entries = data.get("reel_content_templates", [])
        return {t["id"]: t for t in entries if isinstance(t, dict) and t.get("id")}
    except Exception as e:
        logger.warning(f"templates registry unavailable ({e}); using empty registry")
        return {}


TEMPLATES: dict[str, dict] = _load_templates()


def get_template(template_id: str) -> dict | None:
    """Look up a content template by id; None when unknown."""
    return TEMPLATES.get(template_id)


# ─── Scoring helpers ─────────────────────────────────────────────────────────
def _cap(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def _hook_strength(hook: dict) -> float:
    score = float(hook.get("score") or 0.0)
    s = score * 10.0 if score else 60.0
    text = str(hook.get("text", ""))
    if "?" in text:
        s += 10.0
    if len(text) <= 90:
        s += 10.0  # short hooks hold attention
    return _cap(s)


def _curiosity(hook: dict) -> float:
    t = str(hook.get("text", "")).lower()
    s = 40.0 + 12.0 * sum(1 for kw in ("why", "how", "?", "secret", "nobody",
                                       "never", "actually", "what", "hidden") if kw in t)
    return _cap(s)


def _info_value(script: str) -> float:
    n = len(str(script).split())
    if 125 <= n <= 155:
        return 90.0
    if 100 <= n <= 180:
        return 70.0
    return 50.0


def _visual_novelty(visual: str | None) -> float:
    v = (visual or "standard tech b-roll").lower()
    s = 60.0
    for kw, bonus in (("terminal", 10), ("screencast", 10), ("kinetic", 10),
                      ("3d", 15), ("split", 5), ("glitch", 10), ("particle", 10),
                      ("morph", 10), ("b-roll", 5)):
        if kw in v:
            s += bonus
    return _cap(s)


def _retention(script: str) -> float:
    n = len(str(script).split())
    s = 60.0
    if 110 <= n <= 170:
        s += 20.0
    low = str(script).lower()
    if "step" in low or "first" in low:
        s += 10.0
    return _cap(s)


def _shareable(hook: dict, script: str) -> float:
    txt = f"{hook.get('text', '')} {script}".lower()
    s = 55.0 + 8.0 * sum(1 for kw in ("free", "open source", "save", "money",
                                      "hours", "replace", "secret", "workflow") if kw in txt)
    return _cap(s)


def _replay(script: str) -> float:
    n = len(str(script).split())
    if 120 <= n <= 165:
        return 80.0
    if 90 <= n <= 190:
        return 60.0
    return 40.0


def _cta(script: str) -> float:
    low = str(script).lower()
    return 100.0 if "signhify" in low and "follow" in low else 40.0


# ─── Concept scoring + gate ──────────────────────────────────────────────────
def concept_from_hook_script(topic: dict, hook: dict, script: str,
                             visual: str | None = None) -> dict:
    """Deterministic 0-100 sub-scores for a (hook, script, visual) concept."""
    return {
        "hook_strength": _hook_strength(hook),
        "curiosity": _curiosity(hook),
        "information_value": _info_value(script),
        "visual_novelty": _visual_novelty(visual),
        "retention_potential": _retention(script),
        "shareability": _shareable(hook, script),
        "replayability": _replay(script),
        "cta_quality": _cta(script),
    }


def score_concept(concept: dict) -> dict:
    """Weighted virality score (0-100) + per-metric breakdown.

    Concept values are 0-100; a dict whose every provided metric is <= 10 is
    treated as a 0-10 scale and scaled to 0-100. Missing metrics default to 50.
    """
    small_scale = bool(concept) and all(v <= 10 for v in concept.values())
    breakdown: dict[str, dict] = {}
    total = 0.0
    for metric, weight in WEIGHTS.items():
        raw = concept.get(metric, 50.0)
        s = _cap(raw * 10.0 if small_scale else raw)
        contribution = round(s * weight, 2)
        breakdown[metric] = {"score": round(s, 2), "weight": weight,
                             "contribution": contribution}
        total += contribution
    total = round(total, 2)
    passed = total >= GATE
    return {"total": total, "passed": passed,
            "reason": "passes virality gate" if passed else "below virality gate",
            "breakdown": breakdown}


def gate_concept(concept_or_score: dict | float) -> tuple[bool, str]:
    """Gate a concept (dict) or raw score (float) at >= 75. Returns (ok, reason)."""
    total = concept_or_score if isinstance(concept_or_score, (int, float)) \
        else score_concept(concept_or_score)["total"]
    total = round(float(total), 2)
    passed = total >= GATE
    reason = "passes virality gate" if passed else "below virality gate"
    return passed, f"{reason} ({total:.1f}/100)"


# ─── Topic selection ─────────────────────────────────────────────────────────
def _factor(topic: dict, key: str) -> float | None:
    """Read a factor by its canonical name, tolerating camelCase aliases."""
    norm = key.replace("_", "").lower()
    for k, v in topic.items():
        if k.replace("_", "").lower() == norm:
            return None if v is None else float(v)
    return None


def _in_memory(topic: dict, memory: dict | None) -> bool:
    """True when the topic overlaps a recent post in content-memory."""
    if not memory:
        return False
    t = str(topic.get("topic", "")).lower()
    if not t:
        return False
    recent = [str(p.get("topic", "")).lower() + " " + str(p.get("hook", "")).lower()
              for p in memory.get("recent_posts", [])]
    return any(r.strip() and (t[:25] in r or r[:25] in t) for r in recent)


def score_topic(topic: dict, memory: dict | None = None) -> dict:
    """topicScore = trend*.20 + curiosity*.20 + utility*.20 +
    visualPotential*.15 + shareability*.15 + brandFit*.10, minus a novelty
    penalty when the topic already exists in content-memory."""
    factors = {}
    for key, weight in TOPIC_WEIGHTS.items():
        raw = _factor(topic, key)
        factors[key] = _cap(raw if raw is not None else 50.0)
    penalty = NOVELTY_PENALTY if _in_memory(topic, memory) else 0.0
    breakdown = {k: {"score": factors[k], "weight": w,
                     "contribution": round(factors[k] * w, 2)}
                 for k, w in TOPIC_WEIGHTS.items()}
    base = round(sum(b["contribution"] for b in breakdown.values()), 2)
    return {"topic_score": round(base - penalty, 2), "base": base,
            "novelty_penalty": penalty, "breakdown": breakdown}


def select_best_topic(candidates: list[dict], memory: dict | None = None) -> dict:
    """Score all candidates against memory and return the winner (highest)."""
    scored = [(score_topic(c, memory), c) for c in candidates]
    scored.sort(key=lambda x: x[0]["topic_score"], reverse=True)
    best_detail, best_cand = scored[0]
    winner = dict(best_cand)
    winner["topic_score"] = best_detail["topic_score"]
    winner["topic_breakdown"] = best_detail["breakdown"]
    winner["novelty_penalty"] = best_detail["novelty_penalty"]
    return {"winner": winner,
            "scores": [{"topic": c["topic"], "topic_score": d["topic_score"]}
                       for d, c in scored]}


# ─── Psychology trigger classifier ───────────────────────────────────────────
def _heuristic_trigger(text: str) -> str:
    best, best_n = "CURIOSITY", 0
    for trig in PSYCH_TRIGGERS:
        n = sum(1 for kw in PSYCH_KEYWORDS.get(trig, []) if kw in text)
        if n > best_n:
            best, best_n = trig, n
    return best


def _llm_classify(topic: dict) -> str | None:
    from src.content import script60
    data = script60._llm_json(
        "Classify this tech video topic into exactly one trigger from: "
        + ", ".join(PSYCH_TRIGGERS) + ".",
        f"Topic: {topic.get('topic')}\nAngle: {topic.get('angle', '')}\n"
        f"Return JSON: {{\"trigger\": \"...\"}}")
    trig = str(data.get("trigger", "")).upper() if data else ""
    return trig if trig in PSYCH_TRIGGERS else None


def classify_psychology(topic: dict, use_llm: bool = True) -> dict:
    """Classify a topic into one psychology trigger + one-line guidance.

    Heuristic keyword classifier with optional LLM enrichment; never dishonest
    clickbait — claims must still match delivered info (see script60.fact_gate).
    """
    if use_llm:
        trig = _llm_classify(topic)
        if trig:
            return {"trigger": trig, "guidance": PSYCH_GUIDANCE[trig], "source": "llm"}
    text = f"{topic.get('topic', '')} {topic.get('angle', '')}".lower()
    trig = _heuristic_trigger(text)
    return {"trigger": trig, "guidance": PSYCH_GUIDANCE[trig], "source": "heuristic"}


# ─── Hook A/B ────────────────────────────────────────────────────────────────
def _hooks_for_ab(topic: dict) -> list[dict]:
    """10 hooks: LLM-generated first (via script60), padded with static frames."""
    from src.content import script60
    hooks = script60.generate_hooks(topic, n=10)
    for pat in _HOOK_PATTERNS:
        if len(hooks) >= 10:
            break
        t = pat.format(topic=topic["topic"][:60])
        if not any(h["text"] == t for h in hooks):
            hooks.append({"text": t, "score": 6.5})
    return hooks[:10]


def _static_script(topic: dict, hook: str, variant: int) -> dict:
    from src.content import script60
    t = topic["topic"]
    if variant == 0:
        body = (f"{hook} Today we're breaking down {t}. Here's the setup most tutorials skip. "
                f"First, the problem it actually solves, in plain language. Second, the workflow: "
                f"what you install, what you run, and where people usually get stuck. "
                f"Third, the part nobody shows you: the config flags that change the result. "
                f"I read the docs so you get the practical version, not the marketing one. "
                f"Try the smallest working example first, then scale it up once it runs locally. "
                f"If it fails, check versions and permissions before changing anything else. ")
    elif variant == 1:
        body = (f"{hook} Here's the 60-second version of {t}. The core idea: it removes the manual "
                f"step most people still do by hand. You set it up once, test it on a tiny input, "
                f"then let it run on the real workload. The gotcha is in the defaults: wrong config "
                f"silently gives wrong output. Start small, verify one result by hand, then trust it "
                f"with the full run. That's the whole workflow. ")
    else:
        body = (f"{hook} Most breakdowns of {t} skip the boring parts that actually matter. "
                f"What you need: the install, the first command, and the failure mode everyone hits. "
                f"Run it on a small sample first. Read the error when it fails, because it tells you "
                f"the fix. Once it works once, automate it and move on. That's how you get the value "
                f"without the hype. ")
    return {"text": body + script60.CTA, "words": len((body + script60.CTA).split())}


def _scripts_for_ab(topic: dict, hooks: list[dict]) -> tuple[list[dict], bool]:
    """3 script variants; LLM first, static fallback pool."""
    from src.content import script60
    data = script60._llm_json(
        "You write 3 alternative 60-second voiceovers for a Tech+AI reel. Each is 125-155 words, "
        "specific, no fake stats, no guarantees. End each exactly with the CTA line.",
        f"Topic: {topic['topic']}\nAngle: {topic.get('angle', '')}\nCTA: '{script60.CTA}'\n"
        f"Return JSON: {{\"scripts\": [{{\"text\": \"...\"}} x 3]}}")
    out: list[dict] = []
    if data and isinstance(data.get("scripts"), list):
        for sc in data["scripts"][:3]:
            t = str(sc.get("text", "")).strip()
            if len(t) < 40:
                continue
            if not re.search(r"follow\s+@?signhify\.?studio", t, re.IGNORECASE):
                t = t.rstrip(".!?, ") + f". {script60.CTA}"
            out.append({"text": t, "words": len(t.split())})
        if len(out) == 3:
            return out, True
    return [_static_script(topic, h["text"], i) for i, h in enumerate(hooks[:3])], False


def _visuals_for_ab(topic: dict) -> tuple[list[str], bool]:
    """3 visual concepts; LLM first, static fallback pool."""
    from src.content import script60
    data = script60._llm_json(
        "You write 3 visual concepts for a 1080x1920 Tech+AI reel (0-60s). Each is one line: "
        "style + key on-screen elements.",
        f"Topic: {topic['topic']}\nAngle: {topic.get('angle', '')}\n"
        f"Return JSON: {{\"visuals\": [{{\"concept\": \"...\"}} x 3]}}")
    if data and isinstance(data.get("visuals"), list):
        out = [str(v.get("concept", "")).strip() for v in data["visuals"][:3]
               if str(v.get("concept", "")).strip()]
        if len(out) == 3:
            return out, True
    return list(STATIC_VISUALS), False


def ab_test(topic: dict) -> dict:
    """Hook A/B: score all 10 hooks x 3 scripts x 3 visuals (90 combos) and
    return the highest-scoring concept. Reuses script60.generate_hooks; falls
    back to static pools when the LLM is unavailable."""
    hooks = _hooks_for_ab(topic)
    scripts, scripts_llm = _scripts_for_ab(topic, hooks)
    visuals, visuals_llm = _visuals_for_ab(topic)
    best: dict | None = None
    for h in hooks:
        for s in scripts:
            for v in visuals:
                score = score_concept(concept_from_hook_script(topic, h, s["text"], v))
                combo = {"hook": h["text"], "hook_score": h.get("score"),
                         "script": s["text"], "script_words": s["words"],
                         "visual": v, "total": score["total"],
                         "breakdown": score["breakdown"]}
                if best is None or combo["total"] > best["total"]:
                    best = combo
    return {"best": best,
            "combinations_scored": len(hooks) * len(scripts) * len(visuals),
            "hooks": [h["text"] for h in hooks],
            "scripts": [s["text"] for s in scripts],
            "visuals": visuals,
            "provider": "llm" if (scripts_llm and visuals_llm) else "static"}
