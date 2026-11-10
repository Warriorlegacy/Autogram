"""
src/content/remotion_reel_pipeline.py
Autonomous Remotion Reel Production & Publishing Engine for Autogram.

Integrates:
1. High-retention Remotion React visual compositions (1080x1920 60fps)
2. Ultra-realistic female voice synthesis (Microsoft Neural Ava / ElevenLabs-tier)
3. Automatic word-level subtitle alignment & avatar lip-sync
4. Zero-egress Cloudflare R2 / S3 upload cascade
5. Meta Graph API Instagram Reel container publishing
6. Autonomous follow-gated DM automation trigger
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Stabilize OpenMP / MKL thread memory on CPU
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

logger = logging.getLogger("Autogram.RemotionReel")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REEL_KIT_DIR = BASE_DIR / "docs" / "reel-studio-kit"
SCHEDULE_PATH = BASE_DIR / "data" / "schedule.json"
MEMORY_PATH = BASE_DIR / "data" / "content-memory.json"

AVAILABLE_REELS = [
    "diwali-dev-mode",
    "replaced-editor",
    "local-voice",
    "doc-engine",
    "deleted-production",
    "content-factory",
    "claude-vs-premiere",
    "happy-diwali"
]

REEL_METADATA = {
    "diwali-dev-mode": {
        "title": "The Developer's Diwali: How Engineers Light Up The World 🪔✨",
        "pillar": "Local AI & Festive Tech",
        "trigger": "FESTIVE",
        "caption": (
            "The Developer's Diwali: How Engineers Light Up The World 🪔✨\n\n"
            "This Diwali, don't just light firecrackers outside. Light up your terminal.\n\n"
            "While your family is cleaning the house, you're running `docker system prune` and reclaiming 300GB of cache.\n"
            "Instead of burning cash on sky shots, we're burning GPU cycles fine-tuning local models that run at 40 tokens/sec for $0.00.\n\n"
            "Goddess Lakshmi blessings for every engineer in 2026:\n"
            "📈 10x ARR delivery to your codebase\n"
            "🛡️ Zero 500 errors in your cloud logs\n"
            "💳 Clients who pay invoices on time without chasing\n"
            "📦 Pure open-source software stack replacing four-figure SaaS bills\n\n"
            "From all of us at Signhify Studio, Happy Diwali to every builder shipping in silence! 🪔🚀\n\n"
            "👉 Drop the word \"FESTIVE\" or \"DIWALI\" below and our automated system will deliver the complete open-source master repo vault + architecture blueprints straight to your DMs!\n"
            "(Must follow @signhify.studio to unlock 🔒)\n\n"
            "Engineered with pride at Signhify Studio (signhify.dpdns.org)\n"
            "Stop posting. Start shipping. 🪔⚡\n\n"
            "#HappyDiwali #Diwali2026 #DevDiwali #SoftwareEngineering #Docker #OpenSource #LocalAI #Remotion #AIEngineering #BuildInPublic #SignhifyStudio #CodingLife"
        ),
        "first_comment": "Drop 'FESTIVE' or 'DIWALI' below to unlock our complete open-source repo starter pack & architecture blueprints in your DMs! 🪔✨"
    },
    "replaced-editor": {
        "title": "I Replaced A $5,000/Mo Video Editor With 1 Open-Source Script",
        "pillar": "Video Automation & Engineering",
        "trigger": "CUT",
        "caption": (
            "I Replaced A $5,000/Mo Video Editor With 1 Open-Source Script 🎬⚡\n\n"
            "Most creators spend 8 hours editing a 30-second Reel.\n"
            "Here is the exact Python + Remotion script we use at Signhify Studio to produce 60fps viral vertical videos directly from terminal commands.\n\n"
            "Drop 'CUT' below to get the full source code and Remotion template sent to your DMs! 🚀"
        ),
        "first_comment": "Drop 'CUT' below and I'll DM you the complete script + Remotion template! 🎬"
    },
    "local-voice": {
        "title": "Never Pay For ElevenLabs Again: $0 Local Voice Engine",
        "pillar": "Local AI & Audio",
        "trigger": "VOICE",
        "caption": (
            "Never Pay For ElevenLabs Again: $0 Local Voice Engine 🎙️⚡\n\n"
            "Stop burning $50/month on cloud voice credits.\n"
            "Here is how to run ultra-realistic neural TTS locally on your laptop with studio EQ and broadcast compression.\n\n"
            "Drop 'VOICE' below to unlock the repo!"
        ),
        "first_comment": "Drop 'VOICE' below to get the zero-cost audio mastering script! 🎙️"
    },
    "doc-engine": {
        "title": "How To Build A Netflix-Grade AI Documentary Engine In 1 Weekend",
        "pillar": "System Architecture",
        "trigger": "DOCS",
        "caption": (
            "How To Build A Netflix-Grade AI Documentary Engine In 1 Weekend 🎥🧠\n\n"
            "Multi-agent narrative trees, automated Ken Burns zooms, and orchestral mastering.\n\n"
            "Drop 'DOCS' below to get the architectural blueprint!"
        ),
        "first_comment": "Drop 'DOCS' below to get the architecture guide in your DMs! 📜"
    }
}


class RemotionReelPipeline:
    def __init__(self, dry_run: bool | None = None):
        from src.config import settings
        from src.instagram.publisher import publisher
        from src.storage.uploader import uploader
        from src.instagram.dm_automator import dm_automator

        self.settings = settings
        self.publisher = publisher
        self.uploader = uploader
        self.dm_automator = dm_automator
        self.dry_run = dry_run if dry_run is not None else settings.dry_run

    def select_reel_project(self, requested_id: str | None = None) -> str:
        """Selects the requested project or picks the best next project from history."""
        if requested_id and requested_id in AVAILABLE_REELS:
            return requested_id
        
        # Check history in schedule.json to avoid repeating recently published reels
        history_topics = []
        if SCHEDULE_PATH.exists():
            try:
                sched = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
                history_topics = [h.get("topic", "") for h in sched.get("history", [])] + [q.get("topic", "") for q in sched.get("queue", [])]
            except Exception:
                pass

        for reel_id in AVAILABLE_REELS:
            meta = REEL_METADATA.get(reel_id, {})
            if meta.get("title") not in history_topics:
                return reel_id
        
        return "diwali-dev-mode"

    def synthesize_voice(self, reel_id: str, voice: str = "ava", rate: str = "+5%", force: bool = False) -> Path:
        """Synthesizes high-fidelity voice using Edge-TTS or Kokoro."""
        project_dir = REEL_KIT_DIR / "projects" / reel_id
        voice_txt = project_dir / "voice.txt"
        if not voice_txt.exists():
            raise FileNotFoundError(f"Missing voice.txt for project {reel_id} at {voice_txt}")

        public_dir = REEL_KIT_DIR / "public" / "reels" / reel_id
        public_dir.mkdir(parents=True, exist_ok=True)
        out_wav = public_dir / "vo.wav"

        if not force and out_wav.exists() and out_wav.stat().st_size > 50000:
            logger.info(f"✓ Existing voiceover found for {reel_id}: {out_wav} (skipping re-synthesis)")
            return out_wav

        logger.info(f"Synthesizing voiceover for {reel_id} using female voice '{voice}'...")
        cmd = [
            sys.executable,
            str(BASE_DIR / "tts_studio.py"),
            "--engine", "edge",
            "--voice", voice,
            "--rate", rate,
            "--file", str(voice_txt),
            "--out", str(out_wav)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR))
        if res.returncode != 0:
            logger.error(f"Voice synthesis failed: {res.stderr}")
            raise RuntimeError(f"TTS synthesis error: {res.stderr}")
        
        logger.info(f"✓ Voice synthesis complete: {out_wav}")
        return out_wav

    def sync_captions_and_lipsync(self, reel_id: str, model: str = "tiny", force: bool = False):
        """Aligns subtitles and computes mouth shape frames for the avatar."""
        words_f = REEL_KIT_DIR / "public" / "reels" / reel_id / "captions.words.json"
        mouth_f = REEL_KIT_DIR / "public" / "reels" / reel_id / "mouth.json"
        
        if not force and words_f.exists() and mouth_f.exists() and words_f.stat().st_size > 100:
            logger.info(f"✓ Audio & lipsync already in sync for {reel_id} (using cached alignment)")
            return

        logger.info(f"Synchronizing word timestamps and avatar lipsync for {reel_id} (Whisper {model})...")
        env = os.environ.copy()
        env["OMP_NUM_THREADS"] = "1"
        env["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        cmd = ["npm", "run", "sync", "--", reel_id, "--model", model]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REEL_KIT_DIR), env=env, shell=True)
        if res.returncode != 0:
            logger.error(f"Sync failed: {res.stderr}\n{res.stdout}")
            raise RuntimeError(f"Sync error: {res.stderr}")
        logger.info(f"✓ Audio & lipsync synced successfully for {reel_id}")

    def render_reel(self, reel_id: str) -> Path:
        """Renders 1080x1920 60fps MP4 using Remotion."""
        rel_out = f"out/{reel_id}.mp4"
        out_mp4 = REEL_KIT_DIR / "out" / f"{reel_id}.mp4"
        out_mp4.parent.mkdir(parents=True, exist_ok=True)

        # If already rendered and newer than audio, reuse existing render
        vo_f = REEL_KIT_DIR / "public" / "reels" / reel_id / "vo.wav"
        if out_mp4.exists() and out_mp4.stat().st_size > 1000000:
            if not vo_f.exists() or out_mp4.stat().st_mtime >= vo_f.stat().st_mtime:
                logger.info(f"✓ Using existing render for {reel_id}: {out_mp4} ({out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")
                return out_mp4

        logger.info(f"Rendering Remotion reel '{reel_id}' to {out_mp4}...")
        env = os.environ.copy()
        env["NODE_OPTIONS"] = "--max-old-space-size=4096"
        cmd = ["npm", "run", "render", "--", reel_id, rel_out]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REEL_KIT_DIR), env=env, shell=True)
        if res.returncode != 0:
            logger.error(f"Remotion render failed: {res.stderr}\n{res.stdout}")
            raise RuntimeError(f"Render error: {res.stderr}")
        
        if not out_mp4.exists():
            raise FileNotFoundError(f"Rendered file not found at {out_mp4}")

        size_mb = out_mp4.stat().st_size / (1024 * 1024)
        logger.info(f"✓ Render complete! MP4 size: {size_mb:.2f} MB")
        return out_mp4

    def run_pipeline(self, reel_id: str | None = None, voice: str = "ava", dry_run: bool | None = None) -> dict:
        """Executes the full end-to-end autonomous Reel pipeline."""
        is_dry = dry_run if dry_run is not None else self.dry_run
        target_reel = self.select_reel_project(reel_id)
        meta = REEL_METADATA.get(target_reel, {
            "title": f"Autogram Reel: {target_reel}",
            "pillar": "AI & Software Engineering",
            "trigger": "CODE",
            "caption": f"Automated Reel: {target_reel} by @signhify.studio\n\nComment CODE below to unlock resources!",
            "first_comment": "Drop 'CODE' below to unlock the complete source pack! ⚡"
        })

        logger.info(f"Starting Remotion Reel Pipeline for: {target_reel} (dry_run={is_dry})")
        
        # 1. Synthesize female voiceover
        self.synthesize_voice(target_reel, voice=voice)

        # 2. Sync captions & avatar lipsync
        self.sync_captions_and_lipsync(target_reel, model="tiny")

        # 3. Render MP4
        video_path = self.render_reel(target_reel)

        # 4. Upload video to CDN
        today_str = datetime.now().strftime("%Y-%m-%d")
        video_url = self.uploader.upload_video_file(str(video_path), today_str, dry_run=is_dry)
        logger.info(f"Public Video URL: {video_url}")

        media_id = None
        live_url = None

        if is_dry:
            media_id = f"mock_reel_{int(time.time())}"
            live_url = f"https://www.instagram.com/p/{media_id}/"
            logger.info(f"[DRY-RUN] Simulated Reel publication: {live_url}")
        else:
            self.publisher.dry_run = False
            logger.info(f"Publishing Reel container to Instagram Graph API...")
            media_id = self.publisher.publish_reel(video_url, meta["caption"])
            live_url = f"https://www.instagram.com/p/{media_id}/"
            logger.info(f"🎉 REEL IS LIVE ON INSTAGRAM: {live_url}")

            # Pinned first comment trigger
            if meta.get("first_comment"):
                time.sleep(2)
                try:
                    c_id = self.publisher.post_comment(media_id, meta["first_comment"])
                    logger.info(f"✓ Pinned comment posted: {c_id}")
                except Exception as e:
                    logger.warning(f"Notice posting first comment: {e}")

            # Run DM automator scan
            time.sleep(3)
            try:
                summary = self.dm_automator.scan_and_automate(limit_posts=5)
                logger.info(f"DM Automator scan complete: {summary}")
            except Exception as e:
                logger.warning(f"DM Automator notice: {e}")

        # Update memory & schedule ledgers
        self._record_run(target_reel, meta, media_id, live_url, is_dry)

        return {
            "reel_id": target_reel,
            "title": meta["title"],
            "video_path": str(video_path),
            "video_url": video_url,
            "media_id": media_id,
            "live_url": live_url,
            "dry_run": is_dry
        }

    def _record_run(self, reel_id: str, meta: dict, media_id: str, live_url: str, dry_run: bool):
        now_iso = datetime.now().isoformat()
        try:
            if SCHEDULE_PATH.exists():
                sched = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
            else:
                sched = {"queue": [], "history": []}
            
            entry = {
                "id": f"SCH-{datetime.now().strftime('%Y%m%d')}-REEL-{reel_id.upper()}",
                "scheduled_time": now_iso,
                "topic": meta["title"],
                "pillar": meta.get("pillar", "AI & Software Engineering"),
                "format": "reel",
                "mode": "dry-run" if dry_run else "live",
                "status": "COMPLETED",
                "media_id": media_id,
                "live_url": live_url,
                "trigger_words": [meta.get("trigger", "FESTIVE")]
            }
            sched.setdefault("queue", []).append(entry)
            SCHEDULE_PATH.write_text(json.dumps(sched, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to update schedule ledger: {e}")


reel_pipeline = RemotionReelPipeline()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Remotion Reel Pipeline")
    parser.add_argument("--id", default="diwali-dev-mode", choices=AVAILABLE_REELS, help="Reel project ID")
    parser.add_argument("--voice", default="ava", help="Voice shortcut or model name (default: ava - female)")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting live to Instagram")
    args = parser.parse_args()

    res = reel_pipeline.run_pipeline(reel_id=args.id, voice=args.voice, dry_run=args.dry_run)
    print("\n" + "="*50)
    print("REEL EXECUTION SUMMARY:")
    print(json.dumps(res, indent=2))
    print("="*50)

