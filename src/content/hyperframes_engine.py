"""
src/content/hyperframes_engine.py - HyperFrames HTML-native deterministic video engine.
Compiles 1080x1920 Instagram Reel compositions from HTML/CSS/GSAP and renders via headless Chrome + FFmpeg.
"""

import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = REPO_ROOT / "renderer" / "templates" / "reels"
DEFAULT_WORKSPACE = REPO_ROOT / "workspace" / "hyperframes_reel"


class HyperFramesEngine:
    """
    Zero-cost, HTML-native deterministic video engine.
    Turns HTML, CSS, media, and seekable GSAP animations into 1080x1920 Instagram Reels.
    """

    _available: Optional[bool] = None

    def __init__(self, workspace_dir: Path | str = DEFAULT_WORKSPACE):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    @classmethod
    def is_available(cls) -> bool:
        """
        Verifies that Node.js >= 22 and FFmpeg are installed and accessible on PATH.
        """
        if cls._available is not None:
            return cls._available

        # 1. Check Node.js
        node_ok = False
        try:
            node_out = subprocess.check_output(
                ["node", "-v"],
                stderr=subprocess.STDOUT,
                text=True,
                shell=sys.platform.startswith("win"),
                timeout=5,
            ).strip()
            match = re.search(r"v(\d+)\.", node_out)
            if match and int(match.group(1)) >= 22:
                node_ok = True
            else:
                logger.warning(f"HyperFrames requires Node.js >= 22, found {node_out}")
        except Exception as e:
            logger.warning(f"Node.js check failed: {e}")

        # 2. Check FFmpeg
        ffmpeg_ok = False
        try:
            subprocess.check_output(
                ["ffmpeg", "-version"],
                stderr=subprocess.STDOUT,
                text=True,
                shell=sys.platform.startswith("win"),
                timeout=5,
            )
            ffmpeg_ok = True
        except Exception as e:
            logger.warning(f"FFmpeg check failed: {e}")

        cls._available = node_ok and ffmpeg_ok
        return cls._available

    def _get_audio_duration(self, audio_path: str) -> float:
        """Extracts exact audio duration using ffprobe if available, else estimates."""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path,
            ]
            out = subprocess.check_output(cmd, text=True, timeout=5).strip()
            val = float(out)
            if val > 0:
                return round(val, 2)
        except Exception:
            pass
        return 20.0

    def compile_composition(
        self,
        topic: str,
        script_text: str = "",
        audio_path: Optional[str] = None,
        duration: Optional[float] = None,
        target_dir: Optional[Path] = None,
        template_name: str = "marketing_promo.html.jinja2",
    ) -> Path:
        """
        Renders Jinja2 template into index.html inside the composition directory.
        """
        work_dir = target_dir or self.workspace
        work_dir.mkdir(parents=True, exist_ok=True)

        # 1. Determine timing
        audio_dest_name = ""
        if audio_path and os.path.exists(audio_path):
            audio_dest = work_dir / "voice.mp3"
            shutil.copyfile(audio_path, audio_dest)
            audio_dest_name = "voice.mp3"
            if not duration:
                duration = self._get_audio_duration(str(audio_dest))

        total_dur = float(duration or 20.0)

        # Distribute proportional scene durations (5 scenes)
        # S1: Hook (18%), S2: Compare (24%), S3: Showcase (24%), S4: Proof (16%), S5: CTA (18%)
        s1 = round(total_dur * 0.18, 2)
        s2 = round(total_dur * 0.24, 2)
        s3 = round(total_dur * 0.24, 2)
        s4 = round(total_dur * 0.16, 2)
        s5 = round(total_dur - (s1 + s2 + s3 + s4), 2)

        # 2. Copy logo if present in assets
        logo_dest_name = ""
        logo_src = REPO_ROOT / "assets" / "signhify-logo-vector.jpeg"
        if logo_src.exists():
            logo_dest = work_dir / "logo.jpeg"
            shutil.copyfile(logo_src, logo_dest)
            logo_dest_name = "logo.jpeg"

        # 3. Extract hook / features from topic or script
        hook_title = topic
        if ":" in topic:
            parts = topic.split(":", 1)
            hook_title = parts[0].strip()
            hook_sub = parts[1].strip()
        else:
            hook_sub = script_text[:120] if script_text else "Turn 1 prompt into a 3D scroll website in minutes."

        template = self.env.get_template(template_name)
        rendered_html = template.render(
            topic=topic,
            total_duration=total_dur,
            audio_file=audio_dest_name,
            logo_file=logo_dest_name,
            spoken_preview=script_text[:140] if script_text else "Build yours at signhify.dpdns.org. Follow @signhify.studio",
            hook_alert="NEW 3D ENGINE",
            hook_title=hook_title[:60],
            hook_sub=hook_sub[:140],
            feature_title="Instant 3D Scroll Pages With Zero Three.js Code",
            scene1_start=0.0,
            scene1_duration=s1,
            scene2_start=round(s1, 2),
            scene2_duration=s2,
            scene3_start=round(s1 + s2, 2),
            scene3_duration=s3,
            scene4_start=round(s1 + s2 + s3, 2),
            scene4_duration=s4,
            scene5_start=round(s1 + s2 + s3 + s4, 2),
            scene5_duration=s5,
        )

        index_path = work_dir / "index.html"
        index_path.write_text(rendered_html, encoding="utf-8")
        logger.info(f"Compiled HyperFrames composition to {index_path} (duration: {total_dur}s)")
        return work_dir

    def render_reel(
        self,
        topic: str,
        script_text: str = "",
        audio_path: Optional[str] = None,
        output_path: Optional[str] = None,
        duration: Optional[float] = None,
        timeout: int = 180,
    ) -> Dict[str, Any]:
        """
        Compiles the HTML composition and invokes HyperFrames CLI to render the MP4 video.
        """
        if not self.is_available():
            raise RuntimeError("HyperFrames prerequisites not met: requires Node.js >= 22 and FFmpeg.")

        out_file = Path(output_path) if output_path else (self.workspace / "hyperframes_reel.mp4")
        out_file.parent.mkdir(parents=True, exist_ok=True)

        comp_dir = self.compile_composition(
            topic=topic,
            script_text=script_text,
            audio_path=audio_path,
            duration=duration,
        )

        logger.info(f"Rendering HyperFrames video from directory {comp_dir} -> {out_file}...")

        # HyperFrames CLI expects the composition DIRECTORY, not index.html
        local_bin = REPO_ROOT / "node_modules" / ".bin" / ("hyperframes.cmd" if sys.platform.startswith("win") else "hyperframes")
        if local_bin.exists():
            cmd = [
                str(local_bin.resolve()), "render",
                str(comp_dir.resolve()),
                "-o", str(out_file.resolve()),
            ]
        else:
            cmd = [
                "npx", "--yes", "hyperframes", "render",
                str(comp_dir.resolve()),
                "-o", str(out_file.resolve()),
            ]

        logger.info(f"Running command: {' '.join(cmd)}")
        proc = subprocess.run(
            cmd,
            cwd=str(comp_dir),
            capture_output=True,
            text=True,
            shell=sys.platform.startswith("win"),
            timeout=timeout,
        )

        if proc.returncode != 0:
            logger.error(f"HyperFrames render failed with code {proc.returncode}:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}")
            raise RuntimeError(f"HyperFrames render failed (exit code {proc.returncode}): {proc.stderr or proc.stdout}")

        # Ensure audio track is present if audio_path was provided
        if audio_path and os.path.exists(audio_path):
            try:
                probe_cmd = [
                    "ffprobe", "-v", "error",
                    "-select_streams", "a:0",
                    "-show_entries", "stream=codec_type",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(out_file.resolve()),
                ]
                has_audio = bool(subprocess.check_output(probe_cmd, text=True, timeout=5).strip())
                if not has_audio:
                    logger.info(f"Muxing voiceover audio track {audio_path} into {out_file}...")
                    muxed_temp = out_file.parent / f"muxed_{out_file.name}"
                    subprocess.run(
                        [
                            "ffmpeg", "-y",
                            "-i", str(out_file.resolve()),
                            "-i", str(audio_path),
                            "-c:v", "copy",
                            "-c:a", "aac",
                            "-b:a", "192k",
                            "-shortest",
                            str(muxed_temp.resolve()),
                        ],
                        check=True,
                        capture_output=True,
                        timeout=30,
                    )
                    shutil.move(str(muxed_temp.resolve()), str(out_file.resolve()))
                    logger.info("Successfully muxed voiceover audio into Reel video.")
            except Exception as e:
                logger.warning(f"Audio mux check/fallback warning: {e}")

        logger.info(f"Successfully rendered HyperFrames reel: {out_file} ({out_file.stat().st_size} bytes)")
        return {
            "ok": True,
            "provider": "hyperframes",
            "type": "video",
            "video_path": str(out_file.resolve()),
            "duration": duration or 20.0,
            "topic": topic,
        }


# Global singleton instance
hyperframes_engine = HyperFramesEngine()
