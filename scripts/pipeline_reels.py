"""Autonomous Instagram Reels pipeline (spec: AUTONOMOUS_INSTAGRAM_REELS_AGENT_SPEC).

Thin spec-compatible facade over the existing Autogram engine — no duplicated
provider logic:
- script  -> src.content.generator (OpenRouter :free chain + template fallback)
- visual  -> src.content.image_generator (Pollinations FLUX 9:16)
- TTS     -> edge-tts (no key, uncapped)
- subs    -> faster-whisper (optional) -> kinetic .ass karaoke
- render  -> FFmpeg + libass zoompan

Spec API preserved: generate_reel_content / synthesize_speech / download_visual /
to_ass_time / compile_word_level_ass / render_ffmpeg / execute_reels_pipeline.
"""

import asyncio
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent / "workspace"
BASE_DIR.mkdir(parents=True, exist_ok=True)

VOICE_NAME = os.getenv("REELS_VOICE", "en-US-ChristopherNeural")

AUDIO_FILE = str(BASE_DIR / "audio.mp3")
BACKGROUND_IMG = str(BASE_DIR / "background.jpg")
SUBTITLES_ASS = str(BASE_DIR / "subtitles.ass")
OUTPUT_REEL = str(BASE_DIR / "final_reel.mp4")

FREE_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nex-agi/nex-n2.5-pro:free",
    "google/gemma-4-31b-it:free",
]

CURATED_VIRAL_REEL_TOPICS = [
    {"topic": "vLLM vs Ollama: 24x High-Throughput LLM Serving for $0", "pillar": "Local AI & Edge Compute"},
    {"topic": "Documenso: Stop Paying $40/User/Month for DocuSign", "pillar": "FOSS SaaS Alternatives"},
    {"topic": "Coolify: Self-Host Next.js and Docker Apps with Zero Lock-In", "pillar": "FOSS SaaS Alternatives"},
    {"topic": "Uptime Kuma: Free Self-Hosted Status Page That Beats Datadog", "pillar": "Developer Power Tools & CLI"},
    {"topic": "Open-WebUI: Run ChatGPT Plus 100% Offline with Local Models", "pillar": "Local AI & Edge Compute"},
    {"topic": "PocketBase: An Entire Backend & Realtime Auth in a Single 15MB File", "pillar": "Self-Hosted Architecture"},
    {"topic": "Stirling-PDF: The 100% Local Adobe Acrobat Pro Alternative", "pillar": "Trending GitHub Spotlight"},
    {"topic": "LazyGit: Why 50,000+ Developers Abandoned GUI Git Clients", "pillar": "Developer Power Tools & CLI"},
    {"topic": "Ripgrep: Recursive Regex Search 10x Faster Than GNU Grep", "pillar": "Developer Power Tools & CLI"},
    {"topic": "Caddy 2: Automatic HTTPS Reverse Proxy with 3 Lines of Config", "pillar": "Self-Hosted Architecture"},
    {"topic": "SearXNG: Private Self-Hosted Metasearch Without Google Tracking", "pillar": "Self-Hosted Architecture"},
    {"topic": "Authentik: Open Source Identity & SSO Replacing $1,000/mo Auth0", "pillar": "FOSS SaaS Alternatives"},
    {"topic": "PostHog: Full-Featured Product Analytics Without Cloud Invoices", "pillar": "FOSS SaaS Alternatives"},
    {"topic": "Vaultwarden: Lightweight Bitwarden Server on a $5/mo VPS", "pillar": "Self-Hosted Architecture"},
    {"topic": "RustDesk: The Self-Hosted TeamViewer and AnyDesk Alternative", "pillar": "FOSS SaaS Alternatives"},
    {"topic": "Immich: High-Performance Google Photos Alternative You Own", "pillar": "Trending GitHub Spotlight"},
    {"topic": "AppFlowy: Open Source Notion Alternative with Local Data Privacy", "pillar": "FOSS SaaS Alternatives"},
    {"topic": "Cal.com: Self-Hosted Meeting Scheduler Without Calendly Fees", "pillar": "FOSS SaaS Alternatives"},
    {"topic": "Tree-of-Thoughts Prompt: 3 Autonomous Reviewers in One Prompt", "pillar": "Prompting & Workflow"},
    {"topic": "Skeleton-of-Thought: The UC Berkeley Method Accelerating LLMs 4x", "pillar": "Local AI & Edge Compute"},
    {"topic": "Chain-of-Density: Condense 10,000-Word Docs into 5 Dense Takeaways", "pillar": "Local AI & Edge Compute"},
    {"topic": "Why Multi-Agent Systems Beat Monolithic Prompts in Production", "pillar": "Tech Explainer"},
    {"topic": "Context Caching Architecture: How to Slash 90% of LLM API Costs", "pillar": "Tech Explainer"},
    {"topic": "The Zero-Hallucination SQL Pattern: Strict Schema AST Bounds", "pillar": "Developer Power Tools & CLI"},
    {"topic": "The Deep-Research Agent: 6 Hours of Technical Analysis in 60s", "pillar": "Local AI & Edge Compute"},
    {"topic": "The 1% Rule of Compounding Daily Habits in Software Engineering", "pillar": "Marketing Psychology"},
    {"topic": "Why Micro-SaaS Startups Relicense from MIT to BSL", "pillar": "Open Source Economics & Contrarian"},
    {"topic": "The Hidden Cost of Cloud Subscriptions: Owning Your Compute", "pillar": "Open Source Economics & Contrarian"},
    {"topic": "LiteLLM: 100+ LLMs Behind a Single OpenAI-Compatible Proxy", "pillar": "Trending GitHub Spotlight"},
    {"topic": "n8n: Self-Hosted Automation Engine Replacing Zapier for $0", "pillar": "FOSS SaaS Alternatives"},
]


def get_unique_viral_reel_topic(override_topic: str | None = None) -> str:
    """Selects a fresh, high-virality topic strictly avoiding past memory."""
    import difflib
    import json
    from datetime import datetime

    if override_topic and override_topic.strip():
        return override_topic.strip()

    mem_file = Path(__file__).resolve().parent.parent / "data" / "content-memory.json"
    recent_topics: list[str] = []
    if mem_file.exists():
        try:
            mem = json.loads(mem_file.read_text(encoding="utf-8"))
            recent_topics = [
                p.get("topic", "").lower().replace("[reel]", "").replace("[story]", "").strip()
                for p in mem.get("recent_posts", [])
                if p.get("topic")
            ]
        except Exception:
            recent_topics = []

    def is_dup(cand: str) -> bool:
        c_low = cand.lower().strip()
        for past in recent_topics[:40]:  # check against 40 most recent postings
            if not past:
                continue
            if c_low in past or past in c_low:
                return True
            if difflib.SequenceMatcher(None, c_low, past).ratio() >= 0.65:
                return True
        return False

    # 1. Filter curated candidates for unposted topics
    unposted = [c["topic"] for c in CURATED_VIRAL_REEL_TOPICS if not is_dup(c["topic"])]
    if unposted:
        return unposted[0]

    # 2. If all curated have been posted recently, find the one posted longest ago
    def recency_rank(topic_str: str) -> int:
        t_low = topic_str.lower()
        for idx, past in enumerate(recent_topics):
            if t_low in past or past in t_low or difflib.SequenceMatcher(None, t_low, past).ratio() >= 0.65:
                return idx
        return 999999

    sorted_by_oldest = sorted(CURATED_VIRAL_REEL_TOPICS, key=lambda c: recency_rank(c["topic"]), reverse=True)
    return sorted_by_oldest[0]["topic"]


def generate_reel_content(topic: str) -> dict:
    """Viral script + visual prompt + caption via OpenRouter :free (falls back to engine)."""
    import json

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    system_prompt = (
        "You are an elite Instagram viral content director for @signhify.studio. Create an engaging 20-second Reel script. "
        "Return STRICT JSON with keys: "
        "'script' (concise spoken text under 45 words, high-tension hook, no emojis, MUST end with: 'Follow signhify.studio for more.'), "
        "'visual_prompt' (photorealistic 9:16 portrait scene description, dramatic volumetric lighting), "
        "'caption' (punchy caption with 5 niche hashtags ending with follow @signhify.studio for more)."
    )
    data = None
    if api_key:
        from openai import OpenAI

        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        last_err = None
        for model in FREE_MODELS:
            try:
                res = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Topic: {topic}"},
                    ],
                    response_format={"type": "json_object"},
                )
                parsed = json.loads(res.choices[0].message.content)
                if "script" in parsed and "visual_prompt" in parsed:
                    data = parsed
                    break
            except Exception as e:
                last_err = e
                logger.warning(f"OpenRouter {model} failed: {e}")
        if not data:
            logger.warning(f"All OpenRouter :free models failed ({last_err}); using engine fallback.")

    if not data:
        # $0 fallback: existing engine chain (groq/gemini/ollama/template — never fails)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from src.content.generator import generator

        script = generator.generate_reel_script({"topic": topic, "pillar": "Tech Explainer"})
        data = {
            "script": script["narration"],
            "visual_prompt": f"Cinematic 9:16 portrait of {script['subject']}, dramatic volumetric lighting, photorealistic",
            "caption": f"{script['caption']}\n\n{' '.join(script['hashtags'])}",
        }

    # Defensive regex enforcement: spoken script MUST end with 'Follow signhify.studio for more.'
    script_text = str(data.get("script") or "").strip()
    cta = "Follow signhify.studio for more."
    cleaned_spoken = re.sub(
        r"[\s\.\,\!\?]*follow\s+@?signhify\.?studio(\s+for\s+more)?[\s\.\,\!\?]*$",
        "",
        script_text,
        flags=re.IGNORECASE,
    ).strip()
    if cleaned_spoken:
        data["script"] = f"{cleaned_spoken}. {cta}"
    else:
        data["script"] = f"Stop paying for bloated software. {topic}. {cta}"

    caption = str(data.get("caption") or f"{topic} #reels #viral #tech #opensource").strip()
    if not re.search(r"follow\s+@?signhify\.?studio", caption, re.IGNORECASE):
        caption = f"{caption}\n\n👉 Follow @signhify.studio for more daily AI architectures."
    data["caption"] = caption

    return data


async def synthesize_speech(text: str, output_path: str = AUDIO_FILE):
    import edge_tts

    comm = edge_tts.Communicate(text, voice=VOICE_NAME, rate="+5%", pitch="+0Hz")
    await comm.save(output_path)


def download_visual(prompt: str, output_path: str = BACKGROUND_IMG):
    """9:16 visual via existing Pollinations dispatcher (Cloudflare fallback built in)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.content.image_generator import image_generator

    clean = re.sub(r"[^a-zA-Z0-9\s]", "", prompt)[:180]
    image_generator.generate_image(clean, width=1080, height=1920, output_path=output_path)


def to_ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


_ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kinetic,Arial Black,76,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,2,5,60,60,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _events_for_words(words: list[tuple[str, float, float]], chunk_size: int = 3) -> list[str]:
    """Pure helper (testable without whisper): karaoke events for (word, start, end)."""
    events = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i : i + chunk_size]
        for active_idx, (_, w_start, w_end) in enumerate(chunk):
            parts = []
            for idx, (w, _, _) in enumerate(chunk):
                clean = w.strip().upper()
                if idx == active_idx:
                    parts.append(f"{{\\c&H0000FFFF\\fscx115\\fscy115}}{clean}{{\\fscx100\\fscy100\\c&H00FFFFFF}}")
                else:
                    parts.append(f"{{\\c&H00FFFFFF}}{clean}")
            events.append(
                f"Dialogue: 0,{to_ass_time(w_start)},{to_ass_time(w_end)},Kinetic,,0,0,0,,{' '.join(parts)}"
            )
    return events


def compile_word_level_ass(audio_path: str = AUDIO_FILE, ass_path: str = SUBTITLES_ASS):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        WhisperModel = None
    events: list[str] = []
    if WhisperModel is not None:
        whisper = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = whisper.transcribe(audio_path, word_timestamps=True)
        for segment in segments:
            chunk_words = [(w.word, w.start, w.end) for w in (segment.words or [])]
            events.extend(_events_for_words(chunk_words))
    else:
        # ponytail: no naive fallback — fake timestamps would desync karaoke.
        # Upgrade path: pip install faster-whisper for true word alignment.
        raise RuntimeError("faster-whisper not installed; run pip install -r requirements.txt")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(_ASS_HEADER + "\n".join(events))


def render_ffmpeg(
    image_path: str = BACKGROUND_IMG,
    audio_path: str = AUDIO_FILE,
    ass_path: str = SUBTITLES_ASS,
    output_path: str = OUTPUT_REEL,
):
    clean_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "zoompan=z='min(zoom+0.0012,1.15)':d=750:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
        f"subtitles='{clean_ass}'[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path,
    ]
    subprocess.run(cmd, check=True)


def execute_reels_pipeline(topic: str = "") -> dict:
    import json as _json
    from datetime import datetime

    topic = (topic or "").strip()
    if not topic or topic.lower() in ("auto", "none", "null"):
        topic = get_unique_viral_reel_topic()

    logger.info(f"Executing Reels pipeline with unique topic: '{topic}'")
    data = generate_reel_content(topic)
    asyncio.run(synthesize_speech(data["script"], AUDIO_FILE))
    download_visual(data["visual_prompt"], BACKGROUND_IMG)
    compile_word_level_ass(AUDIO_FILE, SUBTITLES_ASS)
    render_ffmpeg(BACKGROUND_IMG, AUDIO_FILE, SUBTITLES_ASS, OUTPUT_REEL)
    result = {
        "video_path": OUTPUT_REEL,
        "caption": data["caption"],
        "script": data["script"],
        "visual_prompt": data["visual_prompt"],
        "topic": topic,
    }
    with open(str(BASE_DIR / "metadata.json"), "w", encoding="utf-8") as f:
        _json.dump(result, f, indent=2)

    # Persist topic into content-memory.json for zero-repetition across workflows
    try:
        mem_file = Path(__file__).resolve().parent.parent / "data" / "content-memory.json"
        if mem_file.exists():
            mem = _json.loads(mem_file.read_text(encoding="utf-8"))
            recent = mem.get("recent_posts", [])
            recent.insert(0, {
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "pillar": "Reels Autopilot",
                "topic": f"[Reel] {topic}",
                "hook": data["script"][:60],
                "score": 95.0
            })
            mem["recent_posts"] = recent[:80]
            mem_file.write_text(_json.dumps(mem, indent=2), encoding="utf-8")
            logger.info(f"Recorded Reel '{topic}' to content-memory.json.")
    except Exception as e:
        logger.warning(f"Could not record Reel to memory: {e}")

    return result


if __name__ == "__main__":
    passed_topic = sys.argv[1] if len(sys.argv) > 1 else ""
    result = execute_reels_pipeline(passed_topic)
    print(f"Generated Reel at: {result['video_path']}")
