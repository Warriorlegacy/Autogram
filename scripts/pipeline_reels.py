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
BACKGROUND_VIDEO = str(BASE_DIR / "background.mp4")
SUBTITLES_ASS = str(BASE_DIR / "subtitles.ass")
OUTPUT_REEL = str(BASE_DIR / "final_reel.mp4")

FREE_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nex-agi/nex-n2.5-pro:free",
    "google/gemma-4-31b-it:free",
]

CURATED_VIRAL_REEL_TOPICS = [
    {"topic": "Signhify: Build Apple-Grade 3D Scroll Websites from 1 Single Prompt (signhify.dpdns.org)", "pillar": "AI 3D Website Builder"},
    {"topic": "Stop Paying $5,000 to Web Design Agencies: Ship 3D Sites in 10 Minutes with Signhify", "pillar": "Agency Disruption"},
    {"topic": "The Death of WebGL & Three.js: How Signhify Ships 60 FPS 3D Scroll with Zero Code", "pillar": "AI 3D Website Builder"},
    {"topic": "Export Production HTML, CSS & Express Backend from a 3D Prompt: 100% MIT Code on Signhify", "pillar": "Developer Power Tools"},
    {"topic": "Cyberpunk Kinetic Watch: 360° Exploded 3D Gear Assembly Generated on signhify.dpdns.org", "pillar": "3D Preset Showcase"},
    {"topic": "Titanium EV Supercar: Wind-Tunnel Aerodynamics 3D Launch Page Built with Signhify", "pillar": "3D Preset Showcase"},
    {"topic": "Multi-Video Continuation: Chain Cinematic 3D Videos into an Interactive Scroll Story", "pillar": "AI 3D Website Builder"},
    {"topic": "Product Injection AI: Drop Any Product Photo into a 3D Scroll Journey on signhify.dpdns.org", "pillar": "AI 3D Website Builder"},
    {"topic": "Zenith Spatial Headset: Interactive Micro-OLED Optical 3D Layers on signhify.dpdns.org", "pillar": "3D Preset Showcase"},
    {"topic": "Nova AI Code Copilot: Dark Glassmorphic 3D Developer Platform Built from 1 Prompt", "pillar": "3D Preset Showcase"},
    {"topic": "Orbital Quantum Compute: Deep Tech Particle Physics & 3D Cryo-Chamber Visuals on Signhify", "pillar": "3D Preset Showcase"},
    {"topic": "Vortex Wireless Audio: Exploded Hardware 3D Scroll & Instant Checkout Page", "pillar": "3D Preset Showcase"},
    {"topic": "How a Founder Replaced a $4,000 Agency Quote with a 15-Minute Session on signhify.dpdns.org", "pillar": "Agency Disruption"},
    {"topic": "Zero Code, 60 FPS Smooth: The Frame Extraction Breakthrough Behind signhify.dpdns.org", "pillar": "AI 3D Website Builder"},
    {"topic": "AuditMind AI: Autonomous Ledger Rules & R&D Tax Credit Scanner Built by Signhify", "pillar": "Enterprise WASM Suite"},
    {"topic": "ContractSentinel AI: In-Browser OOXML DOCX Contract Redliner Powered by Signhify", "pillar": "Enterprise WASM Suite"},
    {"topic": "CodeVortex SRE: Kubernetes Stack Trace to AST Syntax Diff Triage by Signhify Studio", "pillar": "Enterprise WASM Suite"},
    {"topic": "DataLightning AI: In-Browser DuckDB-WASM Million-Row SQL Analytics on signhify.dpdns.org", "pillar": "Enterprise WASM Suite"},
    {"topic": "TalentPulse AI: In-Browser Pyodide WASM Technical Assessment Sandbox by Signhify", "pillar": "Enterprise WASM Suite"},
    {"topic": "Why Flat 2D Websites Will Be Obsolete: The Cinematic 3D Shift at signhify.dpdns.org", "pillar": "Contrarian Tech"},
    {"topic": "The $5/mo AI 3D Website Studio That Outperforms $10,000 Design Retainers: Signhify", "pillar": "Agency Disruption"},
    {"topic": "Adjustable FPS Engine: Buttery Smooth 10 to 40 FPS Parallax on Every Mobile Device", "pillar": "AI 3D Website Builder"},
    {"topic": "Iterative Chat Editing: Tweak Copy, Colors, and 3D Sections with Live AI on Signhify", "pillar": "AI 3D Website Builder"},
    {"topic": "How Interactive 3D Scroll Increases E-Commerce Landing Page Conversions by 320%", "pillar": "Growth & Marketing"},
    {"topic": "From 1 Prompt to Deployed 3D Website with Full ZIP Download: Try signhify.dpdns.org", "pillar": "AI 3D Website Builder"},
    {"topic": "SynthMed AI: Clinical Patient Dialogue to Structured SOAP & ICD-10 Notes by Signhify", "pillar": "Enterprise WASM Suite"},
    {"topic": "AdGenesis AI: 50+ Multi-Channel Ad Variations & Multi-Armed Bandit ROAS Engine", "pillar": "Enterprise WASM Suite"},
    {"topic": "TenderBot Global: Autonomous RFP Compliance & Government Proposal Drafter by Signhify", "pillar": "Enterprise WASM Suite"},
    {"topic": "QualiCheck AI: In-Browser 60 FPS Edge Computer Vision Defect Metrology by Signhify", "pillar": "Enterprise WASM Suite"},
    {"topic": "HyperLocalize AI: Millisecond Video Subtitle Timing & Cultural Translation Studio", "pillar": "Enterprise WASM Suite"},
    {"topic": "How to Build Tesla-Grade Interactive Launch Pages with Zero 3D Knowledge on Signhify", "pillar": "AI 3D Website Builder"},
    {"topic": "Why Top Agencies Secretly Use Signhify Studio to 10x Client Delivery Speed", "pillar": "Agency Disruption"},
    {"topic": "Launch a Funded-Looking SaaS Landing Page in an Afternoon at signhify.dpdns.org", "pillar": "Agency Disruption"},
    {"topic": "100% MIT Code Ownership: Why Signhify Crushes Closed Proprietary Website Builders", "pillar": "Developer Power Tools"},
    {"topic": "The 6-Agent Swarm Behind Signhify's Instant 3D Website Compiler (signhify.dpdns.org)", "pillar": "AI 3D Website Builder"},
    {"topic": "Build a Viral 3D Portfolio That Stops Hiring Managers in Their Tracks: signhify.dpdns.org", "pillar": "Developer Power Tools"},
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
        "You are the elite viral growth director for Signhify Studio (@signhify.studio), promoting the revolutionary "
        "AI 3D Website Builder at signhify.dpdns.org. Signhify turns a single prompt into cinematic scroll-reactive 3D websites — "
        "10x faster than web design agencies, zero WebGL or Three.js code needed, native 60 FPS browser scroll, and instant ZIP export with full HTML/CSS/Express backend. "
        "Create an engaging 20-second viral Reel script that hooks viewers, showcases Signhify's capability, and directs them to signhify.dpdns.org. "
        "Return STRICT JSON with keys:\n"
        "'script' (concise spoken text under 45 words, high-tension hook, no emojis, MUST end with: 'Build yours at signhify.dpdns.org. Follow signhify.studio for more.'),\n"
        "'visual_prompt' (photorealistic 9:16 vertical scene: cinematic 3D website interface on dark glassmorphic UI, luxury product exploded view, or titanium supercar aerodynamics, volumetric studio lighting, 8k),\n"
        "'caption' (punchy caption highlighting the 3D builder with website link signhify.dpdns.org, CTA to comment '3D' for direct link, ending with follow @signhify.studio for more, plus 6 niche hashtags)."
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

        script = generator.generate_reel_script({"topic": topic, "pillar": "AI 3D Website Builder"})
        data = {
            "script": script["narration"],
            "visual_prompt": f"Cinematic 9:16 vertical luxury 3D interactive website interface for {script['subject']}, dark mode glassmorphic UI, glowing volumetric lighting, photorealistic 8k render",
            "caption": f"{script['caption']}\n\n🌐 Build yours: signhify.dpdns.org\n💬 Comment '3D' for the direct link!\n\n{' '.join(script['hashtags'])}",
        }

    # Defensive regex enforcement: spoken script MUST end with 'Follow signhify.studio for more.'
    script_text = str(data.get("script") or "").strip()
    cta = "Build yours at signhify.dpdns.org. Follow signhify.studio for more."
    cleaned_spoken = re.sub(
        r"[\s\.\,\!\?]*((build|try|get|start)\s+(yours\s+)?(at\s+)?signhify\.dpdns\.org\.?\s*)?follow\s+@?signhify\.?studio(\s+for\s+more)?[\s\.\,\!\?]*$",
        "",
        script_text,
        flags=re.IGNORECASE,
    ).strip()
    if cleaned_spoken:
        data["script"] = f"{cleaned_spoken}. {cta}"
    else:
        data["script"] = f"Stop paying $5,000 for web design agencies. Signhify Studio turns a single prompt into a cinematic 3D scroll website in minutes with zero code and full export. {cta}"

    caption = str(data.get("caption") or "").strip()
    if not caption or len(caption) < 20:
        caption = (
            f"🚀 {topic}\n\n"
            f"Build cinematic 3D scroll websites from a single prompt — 10x faster with Signhify Studio.\n"
            f"✨ Zero WebGL, zero Three.js, buttery 60 FPS native browser scroll.\n"
            f"📦 100% MIT code ownership — download full ZIP with HTML, CSS & Express backend.\n\n"
            f"🌐 Try it free: signhify.dpdns.org\n"
            f"💬 Comment '3D' and I'll DM you the direct builder link!\n\n"
            f"👉 Follow @signhify.studio for more daily AI architectures.\n\n"
            f"#SignhifyStudio #AIWebsite #3DWebsite #WebDesign #WebDev #BuildInPublic #AItools #LandingPage"
        )
    if "signhify.dpdns.org" not in caption:
        caption = f"{caption}\n\n🌐 Build yours now: https://signhify.dpdns.org"
    if not re.search(r"follow\s+@?signhify\.?studio", caption, re.IGNORECASE):
        caption = f"{caption}\n\n👉 Follow @signhify.studio for daily AI architectures."
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


def _try_gradio_ai_video(prompt: str, output_path: str) -> str | None:
    """Tier 1: Hugging Face ZeroGPU (LTX-Video or Wan 2.1) via gradio_client."""
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
    try:
        from gradio_client import Client
        logger.info("Attempting Tier 1 AI Video: Lightricks/ltx-video-distilled...")
        client = Client("Lightricks/ltx-video-distilled", token=token)
        clean_prompt = prompt[:200]
        res = client.predict(
            prompt=clean_prompt,
            negative_prompt="worst quality, blurry, distorted, flat 2d, watermark",
            input_image_filepath=None,
            input_video_filepath=None,
            height_ui=704,
            width_ui=512,
            mode="text-to-video",
            duration_ui=4,
            ui_frames_to_use=9,
            seed_ui=42,
            randomize_seed=True,
            ui_guidance_scale=1,
            improve_texture_flag=True,
            api_name="/text_to_video",
        )
        video_file = None
        if isinstance(res, (tuple, list)) and len(res) > 0:
            item = res[0]
            if isinstance(item, dict) and "video" in item:
                video_file = item["video"]
            elif isinstance(item, str) and os.path.exists(item):
                video_file = item
        elif isinstance(res, dict) and "video" in res:
            video_file = res["video"]
        elif isinstance(res, str) and os.path.exists(res):
            video_file = res

        if video_file and os.path.exists(video_file):
            import shutil
            shutil.copyfile(video_file, output_path)
            logger.info(f"Tier 1 AI Video generated successfully via LTX-Video: {output_path}")
            return output_path
    except Exception as e:
        logger.warning(f"Tier 1 LTX-Video generation failed/queued ({e}); checking next fallback.")
    return None


def _try_json2video(script_text: str, output_path: str) -> str | None:
    """Tier 2: JSON2Video Cloud API (configured with user API key)."""
    api_key = (os.getenv("JSON2VIDEO_API_KEY") or "").strip()
    if not api_key:
        return None
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from src.content.json2video_engine import JSON2VideoEngine
        logger.info("Attempting Tier 2 AI Video: JSON2Video Cloud API...")
        engine = JSON2VideoEngine(api_key=api_key)
        res = engine.render_reel(script_text=script_text, output_path=output_path, fallback_to_local=False)
        if res and os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
            logger.info(f"Tier 2 video generated via JSON2Video: {output_path}")
            return output_path
    except Exception as e:
        logger.warning(f"Tier 2 JSON2Video generation failed ({e}); checking next fallback.")
    return None


def _try_fal_or_apiframe(prompt: str, output_path: str) -> str | None:
    """Tier 3: Fal.ai or Apiframe if developer keys are configured."""
    fal_key = (os.getenv("FAL_KEY") or "").strip()
    if fal_key:
        try:
            logger.info("Attempting Tier 3 AI Video: Fal.ai Wan 2.1 / LTX...")
            headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
            payload = {"prompt": prompt, "aspect_ratio": "9:16"}
            r = requests.post("https://queue.fal.run/fal-ai/wan-2.1/t2v", json=payload, headers=headers, timeout=30)
            if r.status_code in (200, 201):
                video_url = r.json().get("video", {}).get("url")
                if video_url:
                    vid_data = requests.get(video_url, timeout=60).content
                    Path(output_path).write_bytes(vid_data)
                    return output_path
        except Exception as e:
            logger.warning(f"Tier 3 Fal.ai video generation failed ({e}).")

    apiframe_key = (os.getenv("APIFRAME_API_KEY") or "").strip()
    if apiframe_key:
        try:
            logger.info("Attempting Tier 3 AI Video: Apiframe unified video API...")
            headers = {"Authorization": f"Bearer {apiframe_key}", "Content-Type": "application/json"}
            payload = {"prompt": prompt, "model": "kling-v1.5", "aspect_ratio": "9:16"}
            r = requests.post("https://api.apiframe.pro/v1/video/generate", json=payload, headers=headers, timeout=30)
            if r.status_code in (200, 201):
                video_url = r.json().get("output", {}).get("url") or r.json().get("video_url")
                if video_url:
                    vid_data = requests.get(video_url, timeout=60).content
                    Path(output_path).write_bytes(vid_data)
                    return output_path
        except Exception as e:
            logger.warning(f"Tier 3 Apiframe video generation failed ({e}).")
    return None


def _try_pexels_video(topic: str, output_path: str) -> str | None:
    """Tier 4: Pexels 4K/HD Portrait Cinematic Video (100% Free, 20k req/mo)."""
    pexels_key = (os.getenv("PEXELS_API_KEY") or "").strip()
    if not pexels_key:
        return None
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from src.content.cloud_render import pexels_portrait_clips
        logger.info(f"Attempting Tier 4 Cinematic Stock Video: Pexels for '{topic}'...")
        keywords = "technology 3d animation luxury supercar watch abstract neon"
        t_low = topic.lower()
        if "watch" in t_low or "timepiece" in t_low:
            keywords = "luxury watch mechanical"
        elif "car" in t_low or "supercar" in t_low or "ev" in t_low:
            keywords = "hypercar sports car night city"
        elif "headset" in t_low or "spatial" in t_low:
            keywords = "virtual reality futuristic technology"
        elif "code" in t_low or "developer" in t_low or "copilot" in t_low:
            keywords = "coding cyber matrix computer"
        elif "website" in t_low or "design" in t_low:
            keywords = "modern design neon 3d abstract"

        clips = pexels_portrait_clips(keywords, count=2)
        if clips:
            best_clip = clips[0]
            logger.info(f"Downloading Pexels cinematic clip from {best_clip['url'][:60]}...")
            resp = requests.get(best_clip["url"], timeout=60)
            if resp.status_code == 200 and len(resp.content) > 10000:
                Path(output_path).write_bytes(resp.content)
                logger.info(f"Tier 4 Pexels cinematic clip saved to {output_path}")
                return output_path
    except Exception as e:
        logger.warning(f"Tier 4 Pexels cinematic stock failed ({e}); checking next fallback.")
    return None


def _try_flux_image(prompt: str, output_path: str) -> str:
    """Tier 5: FLUX.1 + 2.5D camera zoompan (100% Free, zero fail foundation)."""
    logger.info("Using Tier 5: Pollinations FLUX.1 9:16 vertical keyframe + 2.5D zoompan...")
    download_visual(prompt, output_path)
    return output_path


def download_ai_video(
    prompt: str,
    topic: str = "",
    script_text: str = "",
    output_video_path: str = BACKGROUND_VIDEO,
    output_image_path: str = BACKGROUND_IMG,
) -> dict:
    """
    5-Tier Cascading AI Cinematic Video Dispatcher:
    Tier 1: Wan 2.1 / LTX-Video via Hugging Face ZeroGPU (gradio_client)
    Tier 2: JSON2Video Cloud API (user-configured key)
    Tier 3: Fal.ai / Apiframe REST APIs (if configured)
    Tier 4: Pexels 4K Portrait Cinematic Stock Video (free API)
    Tier 5: Pollinations FLUX.1 + 2.5D FFmpeg Zoompan (zero-fail foundation)
    """
    # Tier 1: True AI Video
    t1 = _try_gradio_ai_video(prompt, output_video_path)
    if t1:
        return {"provider": "ai_video_gradio", "type": "video", "path": t1}

    # Tier 2: JSON2Video
    t2 = _try_json2video(script_text or prompt, output_video_path)
    if t2:
        return {"provider": "json2video", "type": "video", "path": t2}

    # Tier 3: Fal.ai / Apiframe
    t3 = _try_fal_or_apiframe(prompt, output_video_path)
    if t3:
        return {"provider": "fal_ai", "type": "video", "path": t3}

    # Tier 4: Pexels 4K Portrait Stock
    t4 = _try_pexels_video(topic or prompt, output_video_path)
    if t4:
        return {"provider": "pexels_cinematic", "type": "video", "path": t4}

    # Tier 5: Zero-Fail FLUX.1 2.5D Zoompan
    t5 = _try_flux_image(prompt, output_image_path)
    return {"provider": "pollinations_flux_zoompan", "type": "image", "path": t5}


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
    visual_path: str = BACKGROUND_IMG,
    audio_path: str = AUDIO_FILE,
    ass_path: str = SUBTITLES_ASS,
    output_path: str = OUTPUT_REEL,
    is_video: bool = False,
    image_path: str | None = None,
):
    """
    Renders 1080x1920 Instagram Reel with kinetic word-level .ass subtitles.
    If is_video is True or visual_path is an MP4/video, loops the video to match audio duration.
    If visual_path is an image, applies 2.5D camera zoompan.
    """
    if image_path is not None:
        visual_path = image_path

    clean_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    is_vid = is_video or visual_path.lower().endswith((".mp4", ".mov", ".mkv", ".webm"))

    if is_vid:
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", visual_path,
            "-i", audio_path,
            "-filter_complex",
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
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
    else:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", visual_path,
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

    # Multi-tier AI video generation with cascading fallback
    visual_meta = download_ai_video(
        prompt=data["visual_prompt"],
        topic=topic,
        script_text=data["script"],
        output_video_path=BACKGROUND_VIDEO,
        output_image_path=BACKGROUND_IMG,
    )
    compile_word_level_ass(AUDIO_FILE, SUBTITLES_ASS)
    render_ffmpeg(
        visual_path=visual_meta["path"],
        audio_path=AUDIO_FILE,
        ass_path=SUBTITLES_ASS,
        output_path=OUTPUT_REEL,
        is_video=(visual_meta["type"] == "video"),
    )
    result = {
        "video_path": OUTPUT_REEL,
        "caption": data["caption"],
        "script": data["script"],
        "visual_prompt": data["visual_prompt"],
        "topic": topic,
        "video_provider": visual_meta.get("provider", "unknown"),
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
