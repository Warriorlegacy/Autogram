"""
src/content/video_engine.py - Production 1080x1920 Vertical Video & Reels Pipeline
Combines Edge-TTS audio, Faster-Whisper word timestamps, kinetic ASS subtitles, and FFmpeg.
"""

import os
import re
import json
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional
import requests

logger = logging.getLogger(__name__)

VOICE_DEFAULT = "en-US-ChristopherNeural"

def format_ass_timestamp(seconds: float) -> str:
    """Converts raw seconds into standard ASS format: H:MM:SS.cc"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int(round((seconds - int(seconds)) * 100))
    return f"{hours:d}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

class VideoEngine:
    """Generates vertical 9:16 reels with neural narration and kinetic highlight captions."""

    def __init__(self, workspace_dir: str | Path = "./reel_workspace"):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)

    async def generate_narration(self, text: str, output_path: str, voice: str = VOICE_DEFAULT) -> str:
        """Synthesize studio voiceover using Microsoft Edge-TTS (100% free, unmetered)."""
        import edge_tts
        clean_text = re.sub(r'[*_#`\[\]]', '', text).strip()
        communicate = edge_tts.Communicate(clean_text, voice=voice, rate="+6%", pitch="+0Hz")
        await communicate.save(output_path)
        logger.info(f"Generated neural voiceover at: {output_path}")
        return output_path

    def compile_kinetic_subtitles(self, audio_path: str, ass_output_path: str) -> str:
        """Extracts word-level timestamps and compiles ASS karaoke highlighting."""
        from faster_whisper import WhisperModel
        logger.info("Loading Whisper model for word timestamp alignment...")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path, word_timestamps=True)

        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticWord,Arial Black,82,&H0000FFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,7,3,5,60,60,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for segment in segments:
            words = segment.words
            if not words:
                continue

            # 3-word chunks for clean vertical mobile presentation
            chunk_size = 3
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i + chunk_size]
                for active_idx, target_word in enumerate(chunk):
                    w_start = format_ass_timestamp(target_word.start)
                    w_end = format_ass_timestamp(target_word.end)

                    line_parts = []
                    for idx, w in enumerate(chunk):
                        clean_w = w.word.strip().upper()
                        if idx == active_idx:
                            # Highlight in Bright Electric Yellow (&H0000FFFF) with 118% pulse
                            line_parts.append(f"{{\\c&H0000FFFF\\fscx118\\fscy118}}{clean_w}{{\\fscx100\\fscy100\\c&H00FFFFFF}}")
                        else:
                            line_parts.append(f"{{\\c&H00FFFFFF}}{clean_w}")

                    event_line = f"Dialogue: 0,{w_start},{w_end},KineticWord,,0,0,0,,{' '.join(line_parts)}"
                    events.append(event_line)

        with open(ass_output_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events))
        logger.info(f"Compiled kinetic ASS subtitles at: {ass_output_path}")
        return ass_output_path

    def composite_video(self, image_path: str, audio_path: str, ass_path: str, output_path: str) -> str:
        """Composites vertical 1080x1920 MP4 with Ken Burns zoompan and burned subtitles."""
        clean_ass = str(ass_path).replace("\\", "/").replace(":", "\\:")

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(image_path),
            "-i", str(audio_path),
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0018,1.20)':d=900:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
            f"subtitles='{clean_ass}'[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(output_path)
        ]
        logger.info("Rendering final 1080x1920 MP4 reel via FFmpeg...")
        subprocess.run(ffmpeg_cmd, check=True)
        logger.info(f"Master reel successfully rendered at: {output_path}")
        return str(output_path)

    def produce_reel(self, script_text: str, visual_prompt: str, output_name: str = "final_reel.mp4") -> str:
        """Full pipeline: audio -> background -> subtitles -> video compositing."""
        audio_file = self.workspace / "narration.mp3"
        bg_file = self.workspace / "background.jpg"
        ass_file = self.workspace / "subtitles.ass"
        out_file = self.workspace / output_name

        # 1. Voice
        asyncio.run(self.generate_narration(script_text, str(audio_file)))

        # 2. 9:16 Visual
        encoded = requests.utils.quote(f"{visual_prompt}, vertical 9:16, masterpiece, cinematic lighting, 8k")
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&nologo=true"
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        with open(bg_file, "wb") as f:
            f.write(resp.content)

        # 3. Kinetic Subtitles
        self.compile_kinetic_subtitles(str(audio_file), str(ass_file))

        # 4. Composite
        return self.composite_video(str(bg_file), str(audio_file), str(ass_file), str(out_file))

    def render_vertical_reel(self, script_text: str, output_path: str | Path, topic: str = "") -> dict:
        """Helper to render a vertical reel to a target output path."""
        import shutil
        out_path = Path(output_path)
        visual_prompt = f"Futuristic technical minimal abstract representation of {topic or 'social media systems'}"
        rendered_file = self.produce_reel(script_text, visual_prompt, output_name=out_path.name)
        if Path(rendered_file).resolve() != out_path.resolve():
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rendered_file, out_path)
        return {
            "status": "completed",
            "video_path": str(out_path),
            "duration_seconds": 30
        }

