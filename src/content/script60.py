"""60-second Tech+AI viral script + hook + scene-plan engine.

Chain: topic discovery -> 5-10 hooks -> fact/quality gate -> 60s script
-> scene JSON. Provider fallback: OpenRouter -> Gemini -> Groq -> static.
Zero paid deps, no secrets in code/logs.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MEM_FILE = REPO_ROOT / "data" / "content-memory.json"

CTA = "Follow Signhify.studio for more."
TARGET_WORDS = (125, 155)

PILLARS = ["AI Tool Breakdown", "Prompting & Workflow", "Tech Explainer",
           "Trending GitHub Spotlight", "Contrarian", "Local AI & Edge Compute"]

# Deterministic fallback pool: real open-source AI topics, no fabricated stats.
FALLBACK_TOPICS = [
    {"topic": "Pipecat: open-source voice pipeline framework for realtime AI agents",
     "pillar": "Trending GitHub Spotlight", "angle": "How Pipecat routes STT, LLM and TTS frames for low-latency voice agents"},
    {"topic": "Ollama: run Llama 3 and Mistral locally in one command",
     "pillar": "Local AI & Edge Compute", "angle": "Local inference workflow you can try free today"},
    {"topic": "RAG with reranking: why retrieval order matters more than model size",
     "pillar": "Tech Explainer", "angle": "Practical retrieval workflow for coding agents"},
    {"topic": "vLLM paged attention: high-throughput local LLM serving",
     "pillar": "Tech Explainer", "angle": "What paged attention changes for self-hosting"},
    {"topic": "LangGraph state machines for coding agents that do not loop forever",
     "pillar": "Prompting & Workflow", "angle": "Guardrails that keep agents on task"},
    {"topic": "Whisper + diarization: turn meetings into searchable transcripts locally",
     "pillar": "AI Tool Breakdown", "angle": "Free local transcription workflow"},
]

HOOK_FRAMES = [
    "Everyone is using AI wrong. Here's what they're missing.",
    "This open-source AI tool replaces a workflow that used to take hours.",
    "You don't need an expensive setup for this.",
    "This changes how developers should use AI.",
    "Most people have never seen AI used this way.",
    "Stop paying for this SaaS. This free repo does it locally.",
    "I tested this AI workflow so you don't have to.",
    "This 60-second trick fixes broken AI answers.",
]

BANNED_CLAIMS = re.compile(
    r"(guarantee[ds]? \d+%|\+\d{2,}% conversion|320%|1000x|world'?s (fastest|first ever)|"
    r"fda approv|beats gpt-?4 by \d+%|benchmark[^.]{0,40}\d+%)",
    re.IGNORECASE,
)
BANNED_INTROS = ("ai is changing everything", "in today's fast-paced world", "revolutionize the world")


def _memory() -> dict:
    try:
        return json.loads(MEM_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"recent_posts": []}


def _recent_texts(n: int = 60) -> list[str]:
    return [(p.get("topic", "") + " " + p.get("hook", "")).lower()
            for p in _memory().get("recent_posts", [])[:n]]


def _fresh(fallback_pool: list[dict]) -> dict:
    recent = _recent_texts()
    for c in fallback_pool:
        t = c["topic"].lower()
        if not any(t[:25] in r or r[:25] in t for r in recent if r.strip()):
            return c
    return random.choice(fallback_pool)


def discover_topic(pillar: str | None = None, override: str | None = None) -> dict:
    """Autonomous topic discovery: override > live signals > curated fallback."""
    if override and override.strip():
        return {"topic": override.strip(), "pillar": pillar or "Tech Explainer",
                "angle": override.strip(), "source": "manual"}
    # Try live signals from existing fetcher (RSS/HN/seeds); never hard-fail.
    try:
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from src.research.fetcher import fetcher
        sources = fetcher.acquire_sources(live_fetch=True) or fetcher.load_seed_records()
        cands = [s for s in sources if s.get("source_title")]
        recent = _recent_texts()
        for s in cands:
            t = str(s.get("source_title", ""))
            if len(t) < 20 or len(t) > 140:
                continue
            low = t.lower()
            if any(low[:25] in r for r in recent if r.strip()):
                continue
            if any(b in low for b in ("generic ai will", "10 random ai tools")):
                continue
            return {"topic": t, "pillar": pillar or s.get("pillar") or random.choice(PILLARS),
                    "angle": s.get("excerpt", t)[:180], "source": "live",
                    "url": s.get("url", ""), "stars": s.get("stars", 0)}
    except Exception as e:
        logger.warning(f"live discovery unavailable ({e}); using curated fallback")
    fb = _fresh(FALLBACK_TOPICS)
    return {**fb, "source": "curated_fallback"}


def _llm_json(system: str, user: str) -> dict | None:
    """OpenCode -> OpenRouter -> Gemini -> Groq. Returns parsed dict or None."""
    # 0. OpenCode free models (env-configured endpoint, OpenAI-compatible shape).
    #    Needs OPENCODE_API_KEY + OPENCODE_BASE_URL (+ optional OPENCODE_MODELS csv)
    #    as secrets; skipped silently when unconfigured, fails soft otherwise.
    okey, obase = os.getenv("OPENCODE_API_KEY", ""), os.getenv("OPENCODE_BASE_URL", "").rstrip("/")
    omodels = [m.strip() for m in os.getenv("OPENCODE_MODELS", "").split(",") if m.strip()]
    if okey and obase and omodels:
        try:
            import requests
            for model in omodels:
                try:
                    r = requests.post(
                        f"{obase}/chat/completions",
                        headers={"Authorization": f"Bearer {okey}", "Content-Type": "application/json"},
                        json={"model": model, "messages": [
                            {"role": "system", "content": system + " Reply ONLY with valid JSON."},
                            {"role": "user", "content": user}],
                            "response_format": {"type": "json_object"}, "temperature": 0.8},
                        timeout=30)
                    if r.status_code == 200:
                        txt = r.json()["choices"][0]["message"]["content"]
                        return json.loads(txt[txt.find("{"):txt.rfind("}") + 1])
                    logger.warning(f"opencode {model}: HTTP {r.status_code}")
                except Exception as e:
                    logger.warning(f"opencode {model}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"opencode unavailable: {e}")
    # 1. OpenRouter
    key = os.getenv("OPENROUTER_API_KEY", "")
    if key:
        try:
            import requests
            for model in ("nvidia/nemotron-3-super-120b-a12b:free",
                          "google/gemma-4-31b-it:free", "nex-agi/nex-n2.5-pro:free"):
                try:
                    r = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                 "HTTP-Referer": "https://github.com/Warriorlegacy/Autogram",
                                 "X-Title": "Autogram-60s"},
                        json={"model": model, "messages": [
                            {"role": "system", "content": system + " Reply ONLY with valid JSON."},
                            {"role": "user", "content": user}],
                            "response_format": {"type": "json_object"}, "temperature": 0.8},
                        timeout=30)
                    if r.status_code == 200:
                        txt = r.json()["choices"][0]["message"]["content"]
                        return json.loads(txt[txt.find("{"):txt.rfind("}") + 1])
                except Exception as e:
                    logger.warning(f"openrouter {model}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"openrouter unavailable: {e}")
    # 2. Gemini
    gkey = os.getenv("GEMINI_API_KEY", "")
    if gkey:
        try:
            import requests
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gkey}",
                json={"contents": [{"parts": [{"text": system + "\n\n" + user}]}],
                      "generationConfig": {"response_mime_type": "application/json", "temperature": 0.8}},
                timeout=40)
            if r.status_code == 200:
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
        except Exception as e:
            logger.warning(f"gemini unavailable: {e}")
    # 3. Groq
    qkey = os.getenv("GROQ_API_KEY", "")
    if qkey:
        try:
            import requests
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {qkey}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [
                    {"role": "system", "content": system + " Reply ONLY with valid JSON."},
                    {"role": "user", "content": user}],
                    "response_format": {"type": "json_object"}, "temperature": 0.8},
                timeout=30)
            if r.status_code == 200:
                txt = r.json()["choices"][0]["message"]["content"]
                return json.loads(txt[txt.find("{"):txt.rfind("}") + 1])
        except Exception as e:
            logger.warning(f"groq unavailable: {e}")
    return None


def generate_hooks(topic: dict, n: int = 7) -> list[dict]:
    """Generate n hooks, score internally, strongest first. Never repeats memory."""
    recent = _recent_texts()
    data = _llm_json(
        "You write scroll-stopping hooks for a Tech+AI Instagram Reel audience (developers, builders). "
        "No fake stats, no engagement guarantees, no clickbait without substance.",
        f"Topic: {topic['topic']}\nAngle: {topic.get('angle','')}\n"
        f"Return JSON: {{\"hooks\": [{{\"text\": \"...\", \"curiosity\": 1-10, \"novelty\": 1-10, "
        f"\"specificity\": 1-10, \"emotion\": 1-10, \"gap\": 1-10}} x {n}]}}") or {}
    raw = data.get("hooks") if isinstance(data.get("hooks"), list) else []
    hooks: list[dict] = []
    for h in raw[:n]:
        t = str(h.get("text", "")).strip()
        if len(t) < 12 or BANNED_CLAIMS.search(t):
            continue
        if any(t.lower()[:30] in r for r in recent):
            continue
        score = sum(float(h.get(k, 5)) for k in ("curiosity", "novelty", "specificity", "emotion", "gap")) / 5
        hooks.append({"text": t, "score": round(score, 2)})
    # Deterministic fallback frames filled with the topic
    for f in HOOK_FRAMES:
        if len(hooks) >= n:
            break
        t = f if "AI" in f or "tool" in f.lower() else f"{f} ({topic['topic'][:60]})"
        if any(t.lower()[:30] in r for r in recent):
            continue
        hooks.append({"text": t, "score": 7.0})
    hooks.sort(key=lambda h: h["score"], reverse=True)
    return hooks[:n] or [{"text": f"Most people have never seen AI used this way. ({topic['topic'][:60]})", "score": 7.0}]


def fact_gate(topic: dict, script: str) -> tuple[bool, str]:
    """Reject unsupported stats / fabricated capabilities / unsafe claims."""
    low = script.lower()
    if BANNED_CLAIMS.search(script):
        return False, "unsupported statistic or fabricated benchmark"
    if any(b in low for b in BANNED_INTROS):
        return False, "generic banned intro"
    if "ai is changing everything" in low and len(script.split()) < 60:
        return False, "low-substance generic summary"
    return True, "ok"


def _static_60s(topic: dict, hook: str) -> str:
    t, pillar = topic["topic"], topic.get("pillar", "Tech Explainer")
    return (
        f"{hook} "  # 0-5s pattern interrupt + curiosity gap
        f"Today we're breaking down {t}. "  # 5-15s context
        f"Here's the setup most tutorials skip. First, the problem it actually solves, in plain language. "
        f"Second, the workflow: what you install, what you run, and where people usually get stuck. "
        f"Third, the part nobody shows you: the config flags and defaults that change the result. "
        f"I ran through the docs and the repo so you get the practical version, not the marketing version. "  # 15-40s value
        f"Try the smallest working example first, then scale it up once it runs locally. "
        f"If it fails, check versions and permissions before changing anything else. "  # 40-52s payoff
        f"{CTA}"  # 52-60s CTA + end-card time
    )


def generate_60s_script(topic: dict, hook: str) -> dict:
    """60s narration (~125-155 words) with CTA; LLM first, static fallback."""
    data = _llm_json(
        "You write 60-second Instagram Reel voiceovers for Tech+AI builders. "
        "Structure: 0-5s pattern interrupt, 5-15s context, 15-40s high-value how-it-works, "
        "40-52s payoff/takeaway, 52-60s CTA. 125-155 words. Conversational, specific, "
        "no fake stats, no guarantees, no hashtag soup in narration.",
        f"Topic: {topic['topic']}\nPillar: {topic.get('pillar')}\nAngle: {topic.get('angle','')}\n"
        f"Hook (use/adapt as opening): {hook}\n"
        f"End EXACTLY with: '{CTA}'\nReturn JSON: {{\"script\": \"...\"}}") or {}
    script = str(data.get("script", "")).strip()
    provider = "llm" if script else "static"
    if not script:
        script = _static_60s(topic, hook)
    # Enforce CTA
    if not re.search(r"follow\s+@?signhify\.?studio", script, re.IGNORECASE):
        script = script.rstrip(".!?, ") + f". {CTA}"
    # Enforce word count by trimming/padding middle (never cut CTA)
    words = script.split()
    if len(words) > TARGET_WORDS[1]:
        body, cta = script.rsplit(".", 1)[0], CTA
        script = " ".join(body.split()[: TARGET_WORDS[1] - 6]) + f". {cta}"
    elif len(words) < TARGET_WORDS[0]:
        pad = (" Stick around for the exact steps, because the last one saves the most time.")
        if CTA in script:
            script = script.replace(CTA, pad.strip() + f" {CTA}")
    ok, reason = fact_gate(topic, script)
    return {"script": script, "words": len(script.split()), "provider": provider,
            "fact_ok": ok, "fact_reason": reason}


def build_scene_plan(script: str, hook: str, duration: float = 60.0, n: int = 9) -> dict:
    """Scene JSON with timing derived from narration weight (not arbitrary chunks)."""
    from src.content.hyperframes_engine import HyperFramesEngine
    eng = HyperFramesEngine()
    scenes = eng.build_scene_plan_60(script, hook, duration, n)
    return {"duration": duration, "hook": hook, "cta": CTA, "scenes": scenes,
            "hash": hashlib.sha256(script.encode()).hexdigest()[:12]}


def build_caption(topic: dict, hook: str) -> tuple[str, list[str]]:
    tags = ["#AItools", "#TechReels", "#BuildInPublic", "#OpenSource", "#AIAgents", "#Coding"]
    caption = (
        f"{hook}\n\n{topic['topic']}: the practical breakdown — setup, workflow, gotchas.\n"
        f"What's the first AI workflow you'd automate?\n\n{CTA}\n\n"
        f"Try free builds: signhify.dpdns.org\n\n{' '.join(tags)}")
    return caption, tags


def select_topic_script(pillar: str | None = None, override: str | None = None) -> dict:
    """Full front-half: topic -> hooks -> script -> fact gate -> scene plan + caption."""
    topic = discover_topic(pillar, override)
    hooks = generate_hooks(topic)
    hook = hooks[0]["text"]
    s = generate_60s_script(topic, hook)
    if not s["fact_ok"]:  # insufficient confidence -> different topic (spec §8)
        logger.warning(f"fact gate rejected ({s['fact_reason']}); rotating topic")
        fb = _fresh([t for t in FALLBACK_TOPICS if t["topic"] != topic["topic"]] or FALLBACK_TOPICS)
        topic = {**fb, "source": "fact_gate_rotation"}
        hooks = generate_hooks(topic)
        hook = hooks[0]["text"]
        s = generate_60s_script(topic, hook)
    plan = build_scene_plan(s["script"], hook)
    caption, tags = build_caption(topic, hook)
    return {"topic": topic["topic"], "pillar": topic.get("pillar", "Tech Explainer"),
            "angle": topic.get("angle", ""), "source": topic.get("source", ""),
            "hook": hook, "hooks": hooks, "script": s["script"],
            "words": s["words"], "llm_provider": s["provider"],
            "scene_plan": plan, "caption": caption, "hashtags": tags,
            "script_hash": hashlib.sha256(s["script"].encode()).hexdigest()[:16],
            "created_at": datetime.now().isoformat()}
