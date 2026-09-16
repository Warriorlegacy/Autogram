"""
Signhify Hindi/Hinglish Cinematic Promo Video Pipeline
============================================================
Standalone pipeline — zero changes to existing Autogram modules.

Research-backed workflow (2026 AI video playbook):
  1. Script-first: TTS with word timestamps → scenes timed to narration
  2. Each visual directly illustrates spoken content (no generic stock)
  3. Cut on narration pauses for psychological alignment
  4. Signhify logo embedded in every scene (brand consistency)
  5. HyperFrames HTML/CSS/GSAP 3D animated composition

Usage:
  python scripts/pipeline_hindi_promo.py
  python scripts/pipeline_hindi_promo.py --dry-run
  python scripts/pipeline_hindi_promo.py --topic "Custom topic"
"""

import asyncio
import inspect
import json
import logging
import os
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

# ── UTF-8 stdout/stderr on Windows ─────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("HindiPromo")

# ── Paths ───────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
WORKSPACE = REPO_ROOT / "workspace" / "hindi_promo"
WORKSPACE.mkdir(parents=True, exist_ok=True)
DATA_DIR = REPO_ROOT / "data"
MEMORY_FILE = DATA_DIR / "content-memory.json"
LOGO_PATH = REPO_ROOT / "assets" / "signhify-logo-vector.jpeg"

# ── Voice Configuration ─────────────────────────────────────────────────
# Human-sounding settings based on 2026 AI video research:
# - Rate +5% (not +8%): conversational pace, ~145 wpm for Hindi
# - Pitch +1Hz (not +2Hz): natural elevation, not cartoonish
# - hi-IN-SwaraNeural: Microsoft's natural Hindi female voice
HINDI_VOICE = "hi-IN-SwaraNeural"
VOICE_RATE = "+5%"
VOICE_PITCH = "+1Hz"

# Voice roster — rotated every run so consecutive Hindi reels never sound identical.
HINDI_VOICES = [
    "hi-IN-SwaraNeural",   # natural Hindi female
    "hi-IN-MadhurNeural",  # natural Hindi male
]


def _select_hindi_voice() -> str:
    """Pick the voice for this run: env override wins, else deterministic rotation.

    Indexed by TOTAL post count so voice rotation desyncs from the Hindi-only
    template alternation — every run gets a fresh voice+style combo.
    """
    override = (os.getenv("HINDI_VOICE") or "").strip()
    if override:
        return override
    try:
        if MEMORY_FILE.exists():
            mem = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            total = len(mem.get("recent_posts", []))
            return HINDI_VOICES[total % len(HINDI_VOICES)]
    except Exception:
        pass
    return HINDI_VOICES[0]

# ── Unique Hinglish Scripts ───────────────────────────────────────────
# Each script is a unique marketing angle — NOT a viral carousel template.
# Written in a conversational "founder talking to a potential client" tone.
HINDI_SCRIPTS = [
    {
        "id": "hindi_first_impression",
        "topic": "Signhify Studio: Pehla Impression Hi-Fi Hai",
        "narration": (
            "Bhai, ek baat suno. Tumhari website pehli baar aaye toh "
            "woh 3 second mein decide karte hain. "
            "Static photo? Scroll karte hi gaye. "
            "Signhify Studio se tum ek prompt dein, "
            "aur unka spatial compiler usi second mein ek cinematic 3D website ban deta hai. "
            "Hardware explode hota hai scroll pe — real-time 60 FPS. "
            "Zero code. Full MIT export. "
            "Banao free: signhify dot dpdns dot org. "
            "Comment '3D' for link."
        ),
        "subject": "sleek titanium smartphone floating in dark space with dramatic light rays",
        "caption": (
            "Pehla impression 3 second mein hota hai.\n\n"
            "Static photo = scroll karte hi gaye.\n"
            "3D cinematic website = hook.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#SignhifyStudio #3DWeb #FirstImpression #WebDesign #HindiTech #BuildInPublic"
        ),
        "hashtags": ["#SignhifyStudio", "#3DWeb", "#FirstImpression", "#WebDesign", "#HindiTech"],
    },
    {
        "id": "hindi_just_build_it",
        "topic": "Signhify Studio: Bas Itna Hi Kaam Hai",
        "narration": (
            "WebGL seekhne mein 3 saal lagte hain. "
            "Ek Three.js developer ek mahina ke kaam leta hai. "
            "Ab kya karna? "
            "Signhify Studio se tum bas apna product batao, "
            "colors batao, camera motion batao. "
            "Woh spatial compiler baki sab karega. "
            "HTML, CSS, Express backend — sab ZIP mein milega. "
            "Banao free: signhify dot dpdns dot org. "
            "Follow signhify dot studio for more."
        ),
        "subject": "developer hands typing on keyboard with 3D wireframe emerging from screen",
        "caption": (
            "WebGL seekhne mein 3 saal? Ab nahi.\n\n"
            "Signhify ka spatial compiler clean code nikalta hai ek prompt se.\n"
            "Full ZIP. MIT license. Zero hassle.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#ZeroCode #3DWeb #WebDev #SignhifyStudio #HindiTech #BuildInPublic"
        ),
        "hashtags": ["#ZeroCode", "#3DWeb", "#WebDev", "#SignhifyStudio", "#HindiTech"],
    },
    {
        "id": "hindi_dekho_sach",
        "topic": "Signhify Studio: Ye Toh Sach Hai",
        "narration": (
            "Ek baat sach mein. Ek watch preview ne store checkout conversion badha diya 320%. "
            "Customer ne real-time 3D mein har gear ghuma phone pe. "
            "Founder ne zero code mein banaya Signhify Studio pe. "
            "Tum bhi kar sakte ho. "
            "Signhify ka spatial compiler kaam karta hai real-time, 60 FPS, native speed. "
            "Banao free: signhify dot dpdns dot org. "
            "Comment '3D' for link."
        ),
        "subject": "luxury watch rotating slowly on dark pedestal with cinematic lighting",
        "caption": (
            "+320% conversion with 3D product previews.\n\n"
            "Stop losing buyers to static photos.\n"
            "Let them rotate your product in 60 FPS 3D.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#EcommerceGrowth #3DCommerce #SignhifyStudio #HindiTech #ConversionRate"
        ),
        "hashtags": ["#EcommerceGrowth", "#3DCommerce", "#SignhifyStudio", "#HindiTech", "#ConversionRate"],
    },
    {
        "id": "hindi_secret_weapon",
        "topic": "Signhify Studio: Secret Weapon",
        "narration": (
            "Pata hai Apple un insane 3D scroll websites kaise banata hai? "
            "Hardware explode aur rotate hota hai scroll pe? "
            "Ab tumhe math degree ki zaroorat nahi. "
            "Signhify ka spatial AI WebGL shaders instantly compile karta hai. "
            "Native 60 FPS speed. Full MIT export. "
            "Ye toh secret weapon hai. "
            "Banao free: signhify dot dpdns dot org. "
            "Follow signhify dot studio for more."
        ),
        "subject": "futuristic cityscape at night with holographic advertisements floating in air",
        "caption": (
            "Apple 3D scroll secret bahar aa gaya.\n\n"
            "Cinematic spatial websites banao without touching WebGL code.\n"
            "60 FPS mobile-ready. MIT export.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#AppleStyle #3DWebsite #WebDev #SignhifyStudio #HindiTech #UIUX"
        ),
        "hashtags": ["#AppleStyle", "#3DWebsite", "#WebDev", "#SignhifyStudio", "#HindiTech"],
    },
    {
        "id": "hindi_startup_hustle",
        "topic": "Signhify Studio: Startup Ka Secret Weapon",
        "narration": (
            "Startup wale bhai, suno. Tumhe 10 lakh ka website chahiye? "
            "Agency wale 3 mahine lega aur phir bhi bekaar dega. "
            "Signhify Studio pe ek prompt do — product batao, vibe batao. "
            "Spatial compiler instantly 3D scroll website banata hai. "
            "Real-time 60 FPS. Mobile ready. MIT license. "
            "Seed round se pehle hi website ready. "
            "Banao free: signhify dot dpdns dot org. "
            "Follow signhify dot studio for more."
        ),
        "subject": "rocket launching from laptop screen with 3D code fragments orbiting",
        "caption": (
            "Startup budget tight? Agency ka wait khatam.\n\n"
            "Ek prompt se Apple-grade 3D website ready.\n"
            "Seed round se pehle launch karo.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#StartupIndia #3DWeb #BuildInPublic #SignhifyStudio #HindiTech #MVP"
        ),
        "hashtags": ["#StartupIndia", "#3DWeb", "#BuildInPublic", "#SignhifyStudio", "#HindiTech", "#MVP"],
    },
    {
        "id": "hindi_agency_khatma",
        "topic": "Signhify Studio: Web Design Agency Ka Khatma",
        "narration": (
            "Ruko zara. Web design agencies waale pareshan ho gaye kyunki "
            "Signhify Studio ne sabki band baja di. "
            "Ek prompt do — product batao, colors batao, camera motion batao. "
            "Spatial compiler instantly cinematic 3D website banata hai. "
            "60 FPS hardware-accelerated. Zero code. Full MIT export. "
            "Agency 3 mahina? Tumhe 3 minute. "
            "Banao free: signhify dot dpdns dot org. "
            "Comment '3D' for link."
        ),
        "subject": "shattered glass with neon light bursting through cracks in dark room",
        "caption": (
            "Web design agencies ka time khatam.\n\n"
            "3 minute mein 3D cinematic website ready.\n"
            "Agency 3 mahina? Nah.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#AgencyLife #3DWeb #SignhifyStudio #HindiTech #WebDesign #Disrupt"
        ),
        "hashtags": ["#AgencyLife", "#3DWeb", "#SignhifyStudio", "#HindiTech", "#WebDesign", "#Disrupt"],
    },
    {
        "id": "hindi_zero_to_hero",
        "topic": "Signhify Studio: Zero Se Hero Tak",
        "narration": (
            "Coding nahi aati? Koi baat nahi. "
            "Signhify Studio se tum bas bol do kya chahiye. "
            "Spatial compiler khud code likhega — HTML, CSS, JavaScript sab. "
            "Real-time 3D rendering. Hardware accelerated. "
            "Portfolio website ho ya product landing page — sab ho jayega. "
            "MIT license. Apna server pe host karo. "
            "Banao free: signhify dot dpdns dot org. "
            "Follow signhify dot studio for more."
        ),
        "subject": "transformation sequence from rough sketch to polished 3D website on screen",
        "caption": (
            "Coding nahi aati? Chalega.\n\n"
            "Bol do kya chahiye — spatial compiler baaki sab karega.\n"
            "Portfolio, landing page, sab ban jayega.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#NoCode #3DWeb #Portfolio #SignhifyStudio #HindiTech #BeginnerFriendly"
        ),
        "hashtags": ["#NoCode", "#3DWeb", "#Portfolio", "#SignhifyStudio", "#HindiTech", "#BeginnerFriendly"],
    },
    {
        "id": "hindi_game_changer",
        "topic": "Signhify Studio: Game Changer Hai Ye",
        "narration": (
            "3D website banane ka tarika badal gaya. "
            "Pehle WebGL seekho, phir Three.js seekho, phir shader likho. "
            "Ab? Signhify Studio pe ek prompt do. "
            "Spatial compiler turant cinematic 3D website banata hai. "
            "60 FPS. Hardware accelerated. Mobile ready. "
            "Full source code export — MIT license. "
            "Ye game changer hai. "
            "Banao free: signhify dot dpdns dot org. "
            "Comment '3D' for link."
        ),
        "subject": "chess piece transforming into futuristic holographic interface",
        "caption": (
            "3D web dev ka game change ho gaya.\n\n"
            "WebGL + Three.js ka frustration bhool jao.\n"
            "Ek prompt = cinematic 3D website ready.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#GameChanger #3DWeb #WebGL #SignhifyStudio #HindiTech #FutureOfWeb"
        ),
        "hashtags": ["#GameChanger", "#3DWeb", "#WebGL", "#SignhifyStudio", "#HindiTech", "#FutureOfWeb"],
    },
]


def _generate_ai_script(override_topic: str | None = None) -> dict | None:
    """Generate fresh Hinglish promo script via OpenRouter free models. Returns None on failure."""
    import os
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return None

    free_models = [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nex-agi/nex-n2.5-pro:free",
        "google/gemma-4-31b-it:free",
    ]

    topic_hint = override_topic or "any trending tech topic"
    system_prompt = (
        "You are the viral Hindi/Hinglish growth director for Signhify Studio (@signhify.studio), "
        "promoting the AI 3D Website Builder at signhify.dpdns.org. "
        "Signhify turns a single prompt into cinematic 60 FPS 3D scroll websites — zero code, MIT export.\n\n"
        "Generate a FRESH, UNIQUE Hinglish (Hindi + English mix) promo script. "
        "The narration should sound like a founder casually talking to a potential client — conversational, energetic, "
        "no formal Hindi, mix English tech terms naturally (like 'scroll', '3D website', 'prompt', 'MIT license').\n\n"
        "Return STRICT JSON with keys:\n"
        "'topic' (short English title for the angle),\n"
        "'narration' (Hinglish spoken text, 40-60 words, conversational tone, MUST end with: "
        "'Banao free: signhify dot dpdns dot org. Comment 3D for link.'),\n"
        "'subject' (image generation prompt: photorealistic dark cinematic scene with neon accents, 8k),\n"
        "'caption' (Instagram caption in English+Hinglish mix with line breaks, includes signhify.dpdns.org link, "
        "CTA to comment '3D', ends with 6 hashtags),\n"
        "'hashtags' (array of 5-6 hashtag strings like #SignhifyStudio #3DWeb #HindiTech)."
    )

    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        for model in free_models:
            try:
                res = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Topic: {topic_hint}. Generate a unique Hinglish promo."},
                    ],
                    response_format={"type": "json_object"},
                    timeout=30,
                )
                parsed = json.loads(res.choices[0].message.content)
                if all(k in parsed for k in ("narration", "caption", "subject")):
                    parsed["id"] = "hindi_ai_generated"
                    logger.info(f"AI script generated via {model}: {parsed.get('topic', 'unknown')}")
                    return parsed
            except Exception as e:
                logger.warning(f"OpenRouter {model} failed for Hindi script: {e}")
    except ImportError:
        logger.warning("openai package not installed; skipping AI generation.")
    except Exception as e:
        logger.warning(f"AI generation failed: {e}")

    return None


def _select_reel_template() -> str:
    """Alternate HyperFrames visual styles run-to-run so consecutive Hindi reels never look identical."""
    override = os.getenv("HINDI_REELS_TEMPLATE", "") or os.getenv("REELS_TEMPLATE", "")
    if override.strip():
        return override.strip()
    styles = ["marketing_promo.html.jinja2", "avatar_presenter.html.jinja2"]
    try:
        if MEMORY_FILE.exists():
            mem = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            hindi_count = sum(
                1 for p in mem.get("recent_posts", [])
                if "hindi" in str(p.get("topic", "")).lower() or "hindi" in str(p.get("pillar", "")).lower()
            )
            return styles[hindi_count % len(styles)]
    except Exception:
        pass
    return styles[0]


def _select_script(override_topic: str | None = None) -> dict:
    """Select script: AI-generated first, then hardcoded round-robin fallback."""
    if override_topic:
        return {
            "id": "hindi_custom",
            "topic": override_topic,
            "narration": (
                f"{override_topic}. "
                "Signhify Studio se ek prompt mein Apple-grade 3D scroll website ban jaati hai. "
                "Zero code needed. Full MIT export. "
                "Banao free: signhify dot dpdns dot org. "
                "Comment '3D' for link."
            ),
            "subject": "futuristic 3d website dark glassmorphic ui neon",
            "caption": (
                f"{override_topic}\n\n"
                "Ek prompt se Apple-grade 3D scroll website.\n"
                "Zero code. Full MIT export.\n\n"
                "Banao free: signhify.dpdns.org\n"
                "Comment '3D' for link!\n\n"
                "#SignhifyStudio #3DWeb #HindiTech #NoCode #BuildInPublic #WebDesign"
            ),
            "hashtags": ["#SignhifyStudio", "#3DWeb", "#HindiTech", "#NoCode", "#BuildInPublic", "#WebDesign"],
        }

    # Try AI generation first
    ai_script = _generate_ai_script(override_topic)
    if ai_script:
        return ai_script

    # Fallback: round-robin from hardcoded scripts
    last_idx = 0
    if MEMORY_FILE.exists():
        try:
            mem = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            last_idx = mem.get("hindi_script_index", 0)
        except Exception:
            pass

    idx = last_idx % len(HINDI_SCRIPTS)
    script = HINDI_SCRIPTS[idx]
    script["_next_index"] = (last_idx + 1) % len(HINDI_SCRIPTS)
    return script


# ── Voice Synthesis (edge-tts) ────────────────────────────────────────
async def _synthesize(text: str, mp3_path: Path, srt_path: Path, voice: str | None = None) -> float:
    """Synthesize natural-sounding Hindi voiceover + SRT subtitles."""
    import edge_tts

    voice = voice or _select_hindi_voice()
    communicate = edge_tts.Communicate(
        text, voice, rate=VOICE_RATE, pitch=VOICE_PITCH
    )
    submaker = edge_tts.SubMaker()
    with open(mp3_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                f.write(chunk.get("data", b""))
            elif chunk.get("type") in ("WordBoundary", "SentenceBoundary"):
                if hasattr(submaker, "feed"):
                    submaker.feed(chunk)
                else:
                    submaker.create_sub(
                        (chunk["offset"], chunk["duration"]), chunk["text"]
                    )

    subs = submaker.get_srt() if hasattr(submaker, "get_srt") else submaker.generate_subs()
    if inspect.isawaitable(subs):
        subs = await subs

    # Wrap long Hindi lines for 9:16 vertical readability
    raw_subs = subs or ""
    if raw_subs.strip():
        blocks = raw_subs.strip().split("\n\n")
        formatted = []
        for block in blocks:
            lines = block.splitlines()
            if len(lines) >= 3:
                idx_str = lines[0]
                timing_str = lines[1]
                cue_text = " ".join(lines[2:]).strip()
                wrapped = textwrap.fill(cue_text, width=26)
                formatted.append(f"{idx_str}\n{timing_str}\n{wrapped}")
            elif block.strip():
                formatted.append(block)
        final_subs = "\n\n".join(formatted) + "\n"
    else:
        final_subs = "1\n00:00:00,000 --> 00:00:05,000\n \n"

    srt_path.write_text(final_subs, encoding="utf-8")

    import subprocess
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_path)],
        capture_output=True, text=True, timeout=60,
    )
    try:
        return max(5.0, float(probe.stdout.strip()))
    except ValueError:
        return max(5.0, len(text.split()) / 2.5)


def synthesize_speech(text: str, mp3_path: Path, srt_path: Path, voice: str | None = None) -> float:
    """Sync wrapper for edge-tts Hindi voiceover."""
    return asyncio.run(_synthesize(text, mp3_path, srt_path, voice))


# ── HyperFrames 3D Render ─────────────────────────────────────────────
def render_with_hyperframes(
    topic: str,
    narration: str,
    audio_path: Path,
    output_path: Path,
    template_name: str = "marketing_promo.html.jinja2",
) -> dict:
    """Render 3D animated cinematic reel via HyperFrames HTML/CSS/GSAP engine.
    Logo is automatically included via the template (logo_file variable).
    Scene backgrounds are aligned with narration per research-backed workflow."""
    from src.content.hyperframes_engine import HyperFramesEngine

    if not HyperFramesEngine.is_available():
        raise RuntimeError("HyperFrames not available (need Node >= 22 + FFmpeg)")

    engine = HyperFramesEngine()
    result = engine.render_reel(
        topic=topic,
        script_text=narration,
        audio_path=str(audio_path),
        output_path=str(output_path),
        template_name=template_name,
    )
    return result


# ── Upload + Publish ──────────────────────────────────────────────────
def upload_and_publish(video_path: Path, caption: str) -> str | None:
    """Upload video to CDN and publish as Instagram Reel."""
    from src.storage.uploader import uploader
    from src.instagram.publisher import publisher
    from src.ops.guardian import with_retries

    publisher.dry_run = False

    today_str = datetime.now().strftime("%Y-%m-%d")

    logger.info("Uploading video to CDN...")
    try:
        public_url = with_retries(
            lambda: uploader.upload_video_file(str(video_path), today_str)
        )
    except TypeError:
        public_url = uploader.upload_video_file(str(video_path), today_str)

    logger.info("Publishing Reel to Instagram (LIVE)...")
    media_id = publisher.publish_reel(public_url, caption)

    return media_id


# ── Memory Logging ────────────────────────────────────────────────────
def log_to_memory(script: dict, caption: str):
    """Record published topic and advance round-robin index."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        if MEMORY_FILE.exists():
            mem = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        else:
            mem = {"recent_posts": [], "winning_patterns": []}

        mem["recent_posts"].insert(0, {
            "date": today_str,
            "pillar": "Hindi Promo",
            "topic": f"[Hindi Reel] {script['topic']}",
            "hook": script["narration"][:60],
            "score": 95.0,
        })
        mem["recent_posts"] = mem["recent_posts"][:80]

        # Advance round-robin index
        if "_next_index" in script:
            mem["hindi_script_index"] = script["_next_index"]

        MEMORY_FILE.write_text(json.dumps(mem, indent=2), encoding="utf-8")
        logger.info("Recorded Hindi promo to content-memory.json.")
    except Exception as e:
        logger.warning(f"Could not record to memory: {e}")


# ── Main Pipeline ─────────────────────────────────────────────────────
def run_hindi_promo_pipeline(dry_run: bool = False, topic_override: str | None = None) -> dict:
    """Execute the full Hindi/Hinglish cinematic promo pipeline."""
    script = _select_script(topic_override)
    logger.info(f"Selected Hindi script: {script['id']} — {script['topic']}")

    mp3_path = WORKSPACE / "audio.mp3"
    srt_path = WORKSPACE / "captions.srt"
    output_video = WORKSPACE / "hindi_promo.mp4"
    metadata_path = WORKSPACE / "metadata.json"

    # 1. Synthesize Hindi voiceover (natural-sounding settings, rotated voice)
    voice = _select_hindi_voice()
    logger.info(f"Synthesizing Hindi voiceover ({voice}, rate={VOICE_RATE}, pitch={VOICE_PITCH})...")
    duration = synthesize_speech(script["narration"], mp3_path, srt_path, voice)
    logger.info(f"Voiceover ready: {mp3_path} ({duration:.1f}s)")

    # 2. Render 3D animated video via HyperFrames (logo included automatically)
    template_name = _select_reel_template()
    logger.info(f"Selected HyperFrames visual style: {template_name}")
    logger.info("Rendering 3D animated cinematic reel via HyperFrames (logo embedded)...")
    try:
        render_with_hyperframes(
            topic=script["topic"],
            narration=script["narration"],
            audio_path=str(mp3_path),
            output_path=str(output_video),
            template_name=template_name,
        )
        logger.info(f"HyperFrames render complete: {output_video}")
    except Exception as e:
        logger.warning(f"HyperFrames render failed ({e}).")
        raise

    # 3. Upload + Publish
    media_id = None
    if dry_run:
        logger.info("[DRY-RUN] Skipping upload and publish.")
    else:
        try:
            media_id = upload_and_publish(output_video, script["caption"])
            logger.info(f"Published to Instagram! Media ID: {media_id}")
        except Exception as e:
            logger.warning(f"Instagram publish failed (video saved locally): {e}")

    # 4. Save metadata
    metadata = {
        "topic": script["topic"],
        "narration": script["narration"],
        "caption": script["caption"],
        "hashtags": script["hashtags"],
        "template": template_name,
        "voice": voice,
        "voice_rate": VOICE_RATE,
        "voice_pitch": VOICE_PITCH,
        "duration_seconds": duration,
        "video_path": str(output_video),
        "media_id": media_id,
        "mode": "dry-run" if dry_run else "live",
        "published_at": datetime.now().isoformat(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    # 5. Log to memory
    log_to_memory(script, script["caption"])

    logger.info("=" * 60)
    logger.info("Hindi Promo Pipeline Complete!")
    logger.info(f"Video: {output_video}")
    logger.info(f"Media ID: {media_id}")
    logger.info("=" * 60)

    return metadata


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Signhify Hindi/Hinglish Cinematic Promo Video")
    parser.add_argument("--dry-run", action="store_true", help="Skip publish, save locally only")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic override")
    args = parser.parse_args()

    result = run_hindi_promo_pipeline(dry_run=args.dry_run, topic_override=args.topic)
    print(json.dumps(result, indent=2, ensure_ascii=False))
