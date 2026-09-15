"""
Signhify Hindi/Hinglish Cinematic Promo Video Pipeline
=======================================================
Standalone pipeline — does NOT modify any existing Autogram modules.

Flow:
  1. Curated Hinglish script → 2. edge-tts Hindi voiceover →
  3. HyperFrames 3D animated composition → 4. Upload → Publish Instagram Reel

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

# ── UTF-8 stdout/stderr on Windows ──────────────────────────────────────────
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

# ── Paths ───────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
WORKSPACE = REPO_ROOT / "workspace" / "hindi_promo"
WORKSPACE.mkdir(parents=True, exist_ok=True)
DATA_DIR = REPO_ROOT / "data"
MEMORY_FILE = DATA_DIR / "content-memory.json"

# ── Curated Hinglish Promotional Scripts ────────────────────────────────────
# Each script: topic (English title), narration (Hinglish spoken), subject (for
# Pexels stock search), caption (Instagram), hashtags, on_screen_text (GSAP overlays)
HINDI_SCRIPTS = [
    {
        "id": "hindi_agency_disrupt",
        "topic": "Signhify Studio: Web Design Agency Ka Khatma",
        "narration": (
            "Ruko zara. Web design agencies waale pareshan ho gaye is tool se. "
            "Woh $8000 aur ek mahina lete hain Three.js code ke liye. "
            "Ab nahi. "
            "Signhify Studio se ek prompt mein Apple-grade 3D scroll website ban jaati hai 45 seconds mein. "
            "Zero code needed. "
            "Banao apna free at signhify dot dpdns dot org. "
            "Follow signhify dot studio for more."
        ),
        "subject": "futuristic 3d website dark glassmorphic ui neon emerald",
        "caption": (
            "Web agencies waale is tool se pareshan ho gaye.\n\n"
            "Ek prompt se Apple-grade 3D scroll website 45 seconds mein.\n"
            "Zero code. Full MIT export.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for direct link!\n\n"
            "#SignhifyStudio #3DWeb #WebDesign #NoCode #HindiTech #BuildInPublic"
        ),
        "hashtags": [
            "#SignhifyStudio", "#3DWeb", "#WebDesign", "#NoCode",
            "#HindiTech", "#BuildInPublic",
        ],
        "on_screen_text": "Ek Prompt Mein 3D Website",
    },
    {
        "id": "hindi_zero_code",
        "topic": "Signhify Studio: Zero Code 3D Website Builder",
        "narration": (
            "WebGL seekhne mein 3 saal lagte hain. Ab nahi lagenge. "
            "Tum bas apna product batao, colors batao, camera motion batao. "
            "Signhify ka spatial compiler clean production-ready code nikal deta hai. "
            "HTML, CSS, Express backend sab milega ZIP mein. "
            "Banao apna free at signhify dot dpdns dot org. "
            "Follow signhify dot studio for more."
        ),
        "subject": "developer terminal code compiling into 3d wireframe mesh",
        "caption": (
            "WebGL seekhne mein 3 saal? Ab nahi.\n\n"
            "Signhify ka spatial compiler clean code nikalta hai ek prompt se.\n"
            "Full ZIP export. MIT license.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#ZeroCode #3DWeb #WebDev #SignhifyStudio #HindiTech #WebGL"
        ),
        "hashtags": [
            "#ZeroCode", "#3DWeb", "#WebDev", "#SignhifyStudio",
            "#HindiTech", "#WebGL",
        ],
        "on_screen_text": "Zero Code. Full 3D.",
    },
    {
        "id": "hindi_ecommerce",
        "topic": "Signhify Studio: E-Commerce 320% Conversion Boost",
        "narration": (
            "Ek 3D interactive watch preview ne store checkout conversion badha diya 320%. "
            "Customer ne real-time 3D mein har titanium gear ghuma phone pe. "
            "Founder ne zero code mein banaya Signhify Studio pe. "
            " tum bhi bana sakte ho. "
            "Banao apna free at signhify dot dpdns dot org. "
            "Follow signhify dot studio for more."
        ),
        "subject": "luxury cybernetic timepiece 3d interactive product dark ui",
        "caption": (
            "+320% conversion with 3D product previews.\n\n"
            "Stop losing buyers to static photos.\n"
            "Let them rotate your product in 60 FPS 3D.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#EcommerceGrowth #3DCommerce #SignhifyStudio #HindiTech #ConversionRate #Shopify"
        ),
        "hashtags": [
            "#EcommerceGrowth", "#3DCommerce", "#SignhifyStudio",
            "#HindiTech", "#ConversionRate", "#Shopify",
        ],
        "on_screen_text": "+320% Conversion",
    },
    {
        "id": "hindi_apple_secret",
        "topic": "Signhify Studio: Apple 3D Scroll Secret",
        "narration": (
            "Pata hai Apple un insane 3D scroll websites kaise banata hai? "
            "Hardware explode aur rotate hota hai scroll pe? "
            "Ab tumhe math degree ki zaroorat nahi. "
            "Signhify ka spatial AI WebGL shaders instantly compile karta hai. "
            "Native 60 FPS speed. "
            "Banao apna free at signhify dot dpdns dot org. "
            "Follow signhify dot studio for more."
        ),
        "subject": "apple style titanium device exploded view dark 3d website luxury",
        "caption": (
            "Apple 3D scroll secret bahar aa gaya.\n\n"
            "Cinematic spatial websites banao without touching WebGL code.\n"
            "60 FPS mobile-ready. MIT export.\n\n"
            "Banao free: signhify.dpdns.org\n"
            "Comment '3D' for link!\n\n"
            "#AppleStyle #3DWebsite #WebDev #SignhifyStudio #HindiTech #UIUX"
        ),
        "hashtags": [
            "#AppleStyle", "#3DWebsite", "#WebDev", "#SignhifyStudio",
            "#HindiTech", "#UIUX",
        ],
        "on_screen_text": "Apple Ka 3D Secret",
    },
]


def _select_script(override_topic: str | None = None) -> dict:
    """Select least-recently-used script from memory, or by override."""
    if override_topic:
        return {
            "id": "hindi_custom",
            "topic": override_topic,
            "narration": (
                f"{override_topic}. "
                "Signhify Studio se ek prompt mein Apple-grade 3D scroll website ban jaati hai. "
                "Zero code needed. "
                "Banao apna free at signhify dot dpdns dot org. "
                "Follow signhify dot studio for more."
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
            "hashtags": [
                "#SignhifyStudio", "#3DWeb", "#HindiTech", "#NoCode",
                "#BuildInPublic", "#WebDesign",
            ],
            "on_screen_text": override_topic[:40],
        }

    recent_hooks: list[str] = []
    if MEMORY_FILE.exists():
        try:
            mem = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            recent_hooks = [
                (p.get("hook") or p.get("topic", "")).lower()
                for p in mem.get("recent_posts", [])
            ]
        except Exception:
            pass

    for script in HINDI_SCRIPTS:
        hook_check = script["narration"][:50].lower()
        if not any(hook_check in h or h in hook_check for h in recent_hooks[:30]):
            return script

    import random
    return random.choice(HINDI_SCRIPTS)


# ── Voice Synthesis (edge-tts) ─────────────────────────────────────────────
HINDI_VOICE = "hi-IN-SwaraNeural"


async def _synthesize(text: str, mp3_path: Path, srt_path: Path) -> float:
    """Synthesize Hindi voiceover + SRT subtitles. Returns duration in seconds."""
    import edge_tts

    communicate = edge_tts.Communicate(text, HINDI_VOICE, rate="+8%", pitch="+2Hz")
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
    if     inspect.isawaitable(subs):
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


def synthesize_speech(text: str, mp3_path: Path, srt_path: Path) -> float:
    """Sync wrapper for edge-tts Hindi voiceover."""
    return asyncio.run(_synthesize(text, mp3_path, srt_path))


# ── HyperFrames 3D Render ──────────────────────────────────────────────────
def render_with_hyperframes(
    topic: str,
    narration: str,
    audio_path: Path,
    output_path: Path,
    on_screen_text: str = "",
) -> dict:
    """Render 3D animated cinematic reel via HyperFrames HTML/CSS/GSAP engine."""
    from src.content.hyperframes_engine import HyperFramesEngine

    if not HyperFramesEngine.is_available():
        raise RuntimeError("HyperFrames not available (need Node >= 22 + FFmpeg)")

    engine = HyperFramesEngine()
    result = engine.render_reel(
        topic=topic,
        script_text=narration,
        audio_path=str(audio_path),
        output_path=str(output_path),
    )
    return result


# ── Cloud Fallback (Pexels + edge-tts + FFmpeg) ────────────────────────────
def render_cloud_fallback(
    narration: str,
    subject: str,
    audio_path: Path,
    srt_path: Path,
    output_path: Path,
) -> str:
    """Fallback: Pexels stock + edge-tts + FFmpeg assembly."""
    from src.content.cloud_render import render_cloud_reel

    return render_cloud_reel(
        narration,
        subject,
        str(output_path),
        voice=HINDI_VOICE,
    )


# ── Upload + Publish ────────────────────────────────────────────────────────
def upload_and_publish(video_path: Path, caption: str, dry_run: bool) -> str | None:
    """Upload video to CDN and publish as Instagram Reel."""
    from src.storage.uploader import uploader
    from src.instagram.publisher import publisher
    from src.ops.guardian import with_retries
    from src.config import settings

    publisher.dry_run = dry_run

    today_str = datetime.now().strftime("%Y-%m-%d")

    logger.info("Uploading video to CDN...")
    try:
        public_url = with_retries(
            lambda: uploader.upload_video_file(str(video_path), today_str, dry_run=dry_run)
        )
    except TypeError:
        public_url = uploader.upload_video_file(str(video_path), today_str)

    logger.info(f"Publishing Reel to Instagram ({'DRY-RUN' if dry_run else 'LIVE'})...")
    media_id = publisher.publish_reel(public_url, caption)

    return media_id


# ── Memory Logging ──────────────────────────────────────────────────────────
def log_to_memory(script: dict, caption: str):
    """Record published topic to content-memory.json for anti-repetition."""
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
        MEMORY_FILE.write_text(json.dumps(mem, indent=2), encoding="utf-8")
        logger.info("Recorded Hindi promo to content-memory.json.")
    except Exception as e:
        logger.warning(f"Could not record to memory: {e}")


# ── Main Pipeline ───────────────────────────────────────────────────────────
def run_hindi_promo_pipeline(dry_run: bool = False, topic_override: str | None = None) -> dict:
    """Execute the full Hindi/Hinglish cinematic promo pipeline."""
    script = _select_script(topic_override)
    logger.info(f"Selected Hindi script: {script['id']} — {script['topic']}")

    mp3_path = WORKSPACE / "audio.mp3"
    srt_path = WORKSPACE / "captions.srt"
    output_video = WORKSPACE / "hindi_promo.mp4"
    metadata_path = WORKSPACE / "metadata.json"

    # 1. Synthesize Hindi voiceover
    logger.info(f"Synthesizing Hindi voiceover ({HINDI_VOICE})...")
    duration = synthesize_speech(script["narration"], mp3_path, srt_path)
    logger.info(f"Voiceover ready: {mp3_path} ({duration:.1f}s)")

    # 2. Render 3D animated video (HyperFrames primary, cloud fallback)
    rendered = False
    try:
        logger.info("Rendering 3D animated cinematic reel via HyperFrames...")
        render_with_hyperframes(
            topic=script["topic"],
            narration=script["narration"],
            audio_path=mp3_path,
            output_path=output_video,
            on_screen_text=script.get("on_screen_text", ""),
        )
        rendered = True
        logger.info(f"HyperFrames render complete: {output_video}")
    except Exception as e:
        logger.warning(f"HyperFrames render failed ({e}); falling back to cloud render.")

    if not rendered:
        logger.info("Rendering via cloud fallback (Pexels + edge-tts + FFmpeg)...")
        render_cloud_fallback(
            narration=script["narration"],
            subject=script["subject"],
            audio_path=mp3_path,
            srt_path=srt_path,
            output_path=output_video,
        )
        logger.info(f"Cloud render complete: {output_video}")

    # 3. Upload + Publish
    media_id = None
    if not dry_run:
        try:
            media_id = upload_and_publish(output_video, script["caption"], dry_run=False)
            logger.info(f"Published to Instagram! Media ID: {media_id}")
        except Exception as e:
            logger.warning(f"Instagram publish failed (video saved locally): {e}")
    else:
        logger.info("[DRY-RUN] Skipping upload and publish.")

    # 4. Save metadata
    metadata = {
        "topic": script["topic"],
        "narration": script["narration"],
        "caption": script["caption"],
        "hashtags": script["hashtags"],
        "voice": HINDI_VOICE,
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
    logger.info(f"Hindi Promo Pipeline Complete!")
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
