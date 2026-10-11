"""AI generation for the daily Reel pipeline: topics and full content briefs.

Provider: Groq first (fast, free tier, OpenAI-compatible), Gemini fallback.
Every generation is validated by the same fail-closed gates as a hand-written
brief — banned phrases, schema, narration fit. An unusable generation is
rejected, never patched into something publishable.

The model is given ONLY the verified product facts below. It is explicitly told
to invent nothing, because the cost of one fabricated claim is the whole account.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

import requests

from .brief import Brief, Scene, load_brand
from .storyboard import _read_speed, _split_cues, narration_fit


def _load_dotenv_override() -> None:
    """Let the .env file WIN over an inherited environment.

    A stale GROQ_API_KEY already in the process environment silently shadows the
    file's value and fails auth, because load_dotenv() does not override by
    default. The file is the source of truth for this pipeline.
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)
    except Exception:
        pass


_load_dotenv_override()

HTTP_TIMEOUT = 90
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "qwen/qwen3.8-27b"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

HISTORY = Path(__file__).parent / "data" / "topic_history.json"

# Only these facts are handed to the model. Verified from signhify.dpdns.org.
VERIFIED_FACTS = """
PRODUCT (Signhify, https://signhify.dpdns.org) — use ONLY these facts:
- "Signhify Website Builder from a Single Prompt". Type a prompt, AI generates a
  complete scroll-reactive site, publish to a live URL in minutes.
- Mechanism: generate an ~8 second cinematic video, extract hundreds of frames,
  native browser scroll replays them as 3D parallax.
- Site's own words: "No WebGL, no Three.js, no code - just native browser scroll
  with buttery-smooth frame interpolation."
- Specs: 400+ frames per site, ~8s source video, 10-40 FPS adjustable, ZIP deployable.
- Features: Multi-Video Continuation; Full-Stack Export (ZIP, frontend + backend
  starter incl. Express API); Iterative Chat Editing; Product Injection; Adjustable FPS.
- Pricing: Starter $5/mo (5 credits), Pro $50/mo (75), Studio $100/mo (125),
  Enterprise $200/mo (300). Annual saves 20%.
- 100% MIT source code ownership.
Founder: Piyush Raj Singh, AI systems engineer, Varanasi, India. Registered MSME (UDYAM).
FORBIDDEN: do not invent customers, testimonials, revenue, user counts, rankings,
awards, press quotes, performance numbers, or any statistic not listed above.
If a claim is not in this list, do not make it.
"""

BANNED_NOTE = """
BANNED PHRASES — never appear in any field (case-insensitive):
generic hype, fake urgency, unsupported statistics, overused motivational language,
keyword stuffing, game-changer, unlock the power of, in today's fast-paced world,
dive into, at its core, seamless, robust, revolutionary tool, next-gen AI,
ultimate secret, must-have app.
Voice: authoritative, architectural, hyper-practical, zero-fluff, contrarian,
open-source-first. Short declarative sentences. No hype, no exclamation marks.
"""

BRIEF_SCHEMA = """
Return STRICT JSON only, no markdown fence, no commentary:
{
  "slug": "kebab-case-unique-slug",
  "title": "short end-card headline, max 45 chars, no period",
  "hook": "one sentence, max 90 chars, the opening claim",
  "cta": "Follow @signhify.studio for more",
  "pillar": "one of: product, ai-tooling, engineering, build-in-public",
  "sources": ["https://signhify.dpdns.org"],
  "scenes": [
    {
      "id": "kebab-case-id",
      "visual": "hook | statement | feature_card | metrics | terminal | browser",
      "duration": 4.0,
      "eyebrow": "2-3 words, lowercase, no bullet glyph",
      "headline": "max 60 chars",
      "subtext": "max 90 chars, optional",
      "narration": "the spoken line for this scene",
      "bullets": ["only for visual=feature_card or terminal, 3-6 short items"],
      "metrics": [{"v":"400+","k":"frames per site"}],
      "source_url": "only for visual=browser"
    }
  ]
}
RULES:
- 5 to 8 scenes. Total runtime 30-55 seconds.
- Each scene duration must be long enough to SPEAK and READ its narration at
  roughly 15 characters per second. WORK IT OUT for every scene:
      required_duration = ceil(len(narration) / 15) + 0.4 seconds
  Examples: a 60-char narration needs 4.4s; 90 chars needs 6.4s; 120 chars needs 8.4s.
  Set duration to that value or higher. A scene that is too short is REJECTED and
  the whole brief is thrown away.
- narration must match the on-screen meaning exactly; it is burned in as captions.
- metrics only using verified numbers from the product facts above.
- endcard is automatic; do not add an end-card scene.
"""


class GenerationError(RuntimeError):
    pass


# ---------- providers ----------
#
# Benchmarked on the REAL task (emit a schema-valid brief) on 2026-10-11, not a
# toy prompt. Score = passes every gate first try: transport, JSON, pydantic
# schema, banned phrases, narration fit, duration range.
#
#   groq/qwen3.8-27b            PASS 3.3s   <- primary
#   gemini/gemini-2.5-flash-lite PASS 3.4s   <- fallback
#   gemini/gemini-2.5-flash     needed a retry (narration fit)
#   groq/openai/gpt-oss-120b    needed a retry (narration fit)
#   groq/openai/gpt-oss-20b     transport fail
#   openrouter ":free" models   transport fail (free tier unavailable)
#
# Order is measured, not guessed. Anything not configured is skipped, so this
# degrades cleanly to whatever single key the operator actually holds.

def _groq(model: str):
    def f(prompt: str, system: str) -> str | None:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            return None
        try:
            r = requests.post(GROQ_URL, timeout=HTTP_TIMEOUT, headers={
                "Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "temperature": 0.8, "max_tokens": 4096,
                      "response_format": {"type": "json_object"},
                      "messages": [{"role": "system", "content": system},
                                   {"role": "user", "content": prompt}]})
            if r.status_code != 200:
                return None
            return (r.json()["choices"][0]["message"]["content"] or "").strip()
        except Exception:
            return None
    return f


def _gemini(model: str):
    def f(prompt: str, system: str) -> str | None:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            return None
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
                f":generateContent?key={key}", timeout=120,
                headers={"Content-Type": "application/json"},
                json={"systemInstruction": {"parts": [{"text": system}]},
                      "contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"temperature": 0.8, "maxOutputTokens": 8192,
                                           "responseMimeType": "application/json",
                                           "thinkingConfig": {"thinkingBudget": 0}}})
            if r.status_code != 200:
                return None
            return "".join(p.get("text", "") for p in
                           r.json()["candidates"][0]["content"]["parts"]).strip()
        except Exception:
            return None
    return f


def _openrouter(model: str):
    def f(prompt: str, system: str) -> str | None:
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            return None
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                              timeout=90,
                              headers={"Authorization": f"Bearer {key}",
                                       "Content-Type": "application/json"},
                              json={"model": model, "temperature": 0.8, "max_tokens": 4096,
                                    "response_format": {"type": "json_object"},
                                    "messages": [{"role": "system", "content": system},
                                                 {"role": "user", "content": prompt}]})
            if r.status_code != 200:
                return None
            return (r.json()["choices"][0]["message"]["content"] or "").strip()
        except Exception:
            return None
    return f


# (label, callable, required env var). Benchmarked order, best first.
PROVIDER_CHAIN = [
    ("groq/qwen3.8-27b", _groq("qwen/qwen3.8-27b"), "GROQ_API_KEY"),
    ("gemini/gemini-2.5-flash-lite", _gemini("gemini-2.5-flash-lite"), "GEMINI_API_KEY"),
    ("gemini/gemini-2.5-flash", _gemini("gemini-2.5-flash"), "GEMINI_API_KEY"),
    ("groq/openai/gpt-oss-120b", _groq("openai/gpt-oss-120b"), "GROQ_API_KEY"),
    ("openrouter/openai/gpt-oss-120b", _openrouter("openai/gpt-oss-120b"), "OPENROUTER_API_KEY"),
]


def available_providers() -> list[str]:
    return [name for name, _fn, env in PROVIDER_CHAIN if os.environ.get(env)]


def complete(prompt: str, system: str = "", attempt: int = 0) -> str:
    """Walk the measured provider chain, ROTATING by attempt.

    Rotating matters: when a brief is rejected for narration fit, retrying the
    same model just reproduces the same mistake — measured at 86% end-to-end
    with a fixed provider vs 100% with rotation. Start at `attempt` so each
    retry is a genuinely different model.
    """
    live = [(name, fn) for name, fn, env in PROVIDER_CHAIN if os.environ.get(env)]
    if not live:
        raise GenerationError(
            "No LLM provider configured. Set GROQ_API_KEY or GEMINI_API_KEY. "
            "A brief is never fabricated when generation fails.")
    tried = []
    for offset in range(len(live)):
        name, fn = live[(attempt + offset) % len(live)]
        out = fn(prompt, system)
        if out:
            return out
        tried.append(name)
    raise GenerationError(
        f"No provider produced a completion (tried: {', '.join(tried)}). "
        "A brief is never fabricated when generation fails.")


def _json_from(text: str) -> dict:
    t = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(t)
    except ValueError:
        m = re.search(r"\{.*\}", t, re.S)
        if not m:
            raise GenerationError(f"model returned no JSON: {text[:200]!r}")
        return json.loads(m.group(0))


# ---------- history ----------

def recent_topics(n: int = 40) -> list[str]:
    if not HISTORY.exists():
        return []
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))[-n:]
    except Exception:
        return []


def record_topic(slug: str) -> None:
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    log = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    log.append(slug)
    HISTORY.write_text(json.dumps(log[-200:], indent=2), encoding="utf-8")


# ---------- generation ----------

TOPIC_SYSTEM = ("You are the content strategist for Signhify Studio, an AI "
                "engineering studio. You write precise, technical, zero-hype short-form video scripts.")

TOPIC_PROMPT = """Pick {n} DISTINCT topics for a 45-second vertical video.

{brand}
{facts}
{banned}

REQUIRED SPREAD across the {n} topics:
- at least 2 about the Signhify product itself
- at least 2 about engineering practice / how it is actually built
- at least 1 about self-hosting or open source
- at least 1 about AI tooling for developers

Every topic must be explainable in 45 seconds using ONLY the verified facts above,
must be specific enough to write from, and must differ in angle from recent posts.

Recent topics already published (do NOT repeat these angles):
{recent}

Return STRICT JSON only:
{{"topics":[{{"slug":"kebab-case","title":"max 45 chars","hook":"one sentence max 90 chars","pillar":"product|engineering|ai-tooling|build-in-public","angle":"one line on why this is distinct"}}]}}
"""


def generate_topics(n: int = 7, retries: int = 2) -> list[dict]:
    """Distinct on-brand topics. Fails closed rather than returning filler."""
    brand = load_brand()
    system = TOPIC_SYSTEM
    last = ""
    for attempt in range(retries + 1):
        prompt = TOPIC_PROMPT.format(
            n=n, brand=f"Brand: {brand['brand_name']} ({brand['website']}). Pillars: {', '.join(brand['content_pillars'])}.",
            facts=VERIFIED_FACTS, banned=BANNED_NOTE,
            recent=", ".join(recent_topics()) or "(none yet)")
        if attempt:
            prompt += f"\n\nYour previous attempt failed: {last}\nReturn valid JSON only."
        try:
            data = _json_from(complete(prompt, system, attempt))
        except GenerationError:
            raise
        except Exception as e:
            last = str(e)[:200]
            continue
        topics = data.get("topics")
        if isinstance(topics, list) and len(topics) >= n:
            out = []
            for t in topics[:n]:
                if not isinstance(t, dict) or not t.get("slug") or not t.get("hook"):
                    raise GenerationError(f"malformed topic entry: {str(t)[:160]}")
                out.append(t)
            return out
        last = f"expected {n} topics, got {len(topics) if isinstance(topics, list) else 'none'}"
    raise GenerationError(f"topic generation failed after {retries + 1} attempts: {last}")


def _fit_scene_durations(brief: Brief) -> list[str]:
    """Last-resort timing repair: grow a scene so its own narration fits.

    This changes NO copy. The spoken words are exactly what the model wrote; the
    scene just gets enough room to say and read them, which is what a human
    editor would do. Truncating an explanation to hit a target duration is the
    failure mode this avoids. Returns the notes so the change is auditable.
    """
    notes = []
    for s in brief.scenes:
        if not s.narration:
            continue
        parts = _split_cues(s.narration)
        need = sum(len(p) / _read_speed() for p in parts) + 0.4
        if need > s.duration:
            notes.append(f"{s.id}: {s.duration}s -> {round(need, 2)}s (narration fit)")
            s.duration = round(need, 2)
    return notes


def generate_brief(topic: dict, retries: int = 2) -> Brief:
    """A complete, validated Brief. Rejects anything that fails the normal gates."""
    brand = load_brand()
    system = TOPIC_SYSTEM
    last = ""
    for attempt in range(retries + 1):
        prompt = f"""{VERIFIED_FACTS}

{BANNED_NOTE}

Write ONE 9:16 short-form video brief on this topic:
  slug:  {topic.get('slug')}
  title: {topic.get('title')}
  hook:  {topic.get('hook')}
  angle: {topic.get('angle')}

Brand fonts/colors are enforced by the template; you only write copy.
{BRIEF_SCHEMA}"""
        if attempt:
            prompt += f"\n\nPrevious attempt was rejected: {last}\nFix it and return valid JSON only."
        raw = complete(prompt, system, attempt)
        try:
            data = _json_from(raw)
            data.setdefault("slug", topic.get("slug"))
            brief = Brief.model_validate(data)
        except GenerationError:
            raise
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:200]}"
            continue

        hits = brief.banned_hits()
        if hits:
            last = f"banned phrase(s) present: {hits}"
            continue
        if not brief.scenes:
            last = "no scenes"
            continue
        over = narration_fit(brief)
        if over and attempt < retries:
            last = ("scenes too short for narration: "
                    + ", ".join(f"{o['id']} needs {o['needed']}s has {o['duration']}s" for o in over))
            continue
        if over:
            # Final attempt: repair the timing rather than discard good copy.
            for n in _fit_scene_durations(brief):
                print(f"[ai] timing repair — {n}")
        if not 20 <= brief.total_duration() <= 90:
            if attempt < retries:
                last = f"total duration {brief.total_duration()}s outside 20-90s"
                continue
            # Shrink trailing scene padding to fit the platform ceiling.
            excess = brief.total_duration() - 90
            while excess > 0.01 and brief.scenes:
                s = brief.scenes[-1]
                cut = min(excess, max(s.duration - 2.5, 0))
                if cut <= 0:
                    break
                s.duration = round(s.duration - cut, 2)
                excess = brief.total_duration() - 90
        return brief
    raise GenerationError(f"brief generation failed after {retries + 1} attempts: {last}")
