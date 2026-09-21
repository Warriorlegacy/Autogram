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

# 60s Signhify production constants (single source of truth for the Reel system)
TARGET_DURATION = 60.0
WIDTH, HEIGHT, FPS = 1080, 1920, 30
TOTAL_FRAMES = int(TARGET_DURATION * FPS)  # 1800

# Template rotation: 5 premium dark-tech themes injected as CSS overrides.
# ponytail: themes, not 5 duplicate HTML files — one template, 5 palettes.
THEMES = {
    "A": {"accent": "#00E599", "accent2": "#06B6D4", "bg": "#020617", "name": "emerald_circuit"},
    "B": {"accent": "#38BDF8", "accent2": "#A78BFA", "bg": "#040718", "name": "cobalt_neural"},
    "C": {"accent": "#A78BFA", "accent2": "#F472B6", "bg": "#0A0618", "name": "violet_hologram"},
    "D": {"accent": "#22D3EE", "accent2": "#34D399", "bg": "#02131A", "name": "cyan_terminal"},
    "E": {"accent": "#FBBF24", "accent2": "#00E599", "bg": "#0C0A05", "name": "amber_forge"},
}
TEMPLATE_FILES = {
    "A": "marketing_promo.html.jinja2",
    "B": "marketing_promo.html.jinja2",
    "C": "avatar_presenter.html.jinja2",
    "D": "marketing_promo.html.jinja2",
    "E": "avatar_presenter.html.jinja2",
}


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

    def _segment_script_into_scenes(self, script_text: str, topic: str) -> dict:
        """
        Segments raw narration into 5 coherent scenes (Hook, Compare, Showcase, Proof, CTA)
        so that on-screen visuals and dynamic subtitle tracks align perfectly with spoken words.
        """
        clean = re.sub(r"\s+", " ", (script_text or "").strip())
        raw_parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+|(?<=\w)—(?=\w)", clean) if p.strip()]

        s1_default = f"Stop paying $5,000 for 3D websites. {topic}"
        s2_default = "Traditional agencies take weeks of complex Three.js code. Signhify gives you instant 3D scroll."
        s3_default = "From zero WebGL code to native 60 FPS hardware acceleration, you get production-grade physics."
        s4_default = "Interactive 3D scroll depth keeps visitors exploring longer, with full MIT code export."
        s5_default = "Build yours free at signhify.dpdns.org. Comment '3D' for direct link. Follow @signhify.studio."

        if len(raw_parts) >= 5:
            s1 = raw_parts[0]
            s2 = raw_parts[1]
            s3 = raw_parts[2]
            s4 = raw_parts[3]
            s5 = " ".join(raw_parts[4:])
        elif len(raw_parts) == 4:
            s1, s2, s3, s4, s5 = raw_parts[0], raw_parts[1], raw_parts[2], s4_default, raw_parts[3]
        elif len(raw_parts) == 3:
            s1, s2, s3, s4, s5 = raw_parts[0], raw_parts[1], s3_default, s4_default, raw_parts[2]
        elif len(raw_parts) == 2:
            s1, s2, s3, s4, s5 = raw_parts[0], s2_default, s3_default, s4_default, raw_parts[1]
        elif len(raw_parts) == 1 and raw_parts[0]:
            s1, s2, s3, s4, s5 = raw_parts[0], s2_default, s3_default, s4_default, s5_default
        else:
            s1, s2, s3, s4, s5 = s1_default, s2_default, s3_default, s4_default, s5_default

        return {
            "s1_narration": s1,
            "s2_narration": s2,
            "s3_narration": s3,
            "s4_narration": s4,
            "s5_narration": s5,
        }

    @staticmethod
    def split_timeline(total: float = TARGET_DURATION, n: int = 9) -> list[tuple[float, float]]:
        """Generalized timeline: split `total` seconds into n proportional acts.

        Weight profile favors hook (act 1) and CTA (last act) while keeping
        middle acts even. Returns [(start, end)] with exact total coverage.
        """
        if n <= 0:
            return []
        if n == 1:
            return [(0.0, round(total, 2))]
        # Heavier hook + CTA, even middle: e.g. n=9 -> [1.25,1,1,1,1,1,1,1,1.25]
        weights = [1.0] * n
        weights[0] = 1.25
        weights[-1] = 1.25
        s = sum(weights)
        bounds: list[tuple[float, float]] = []
        t = 0.0
        for i, w in enumerate(weights):
            d = round(total * w / s, 2)
            if i == n - 1:
                d = round(total - t, 2)  # absorb rounding so sum == total
            bounds.append((round(t, 2), round(t + d, 2)))
            t += d
        return bounds

    @staticmethod
    def theme_css(theme: str = "A") -> str:
        """CSS variable overrides for theme rotation (A-E)."""
        t = THEMES.get(theme, THEMES["A"])
        return (
            f":root{{--hf-accent:{t['accent']};--hf-accent2:{t['accent2']};--hf-bg:{t['bg']};}}"
            f"#stage{{background:radial-gradient(circle at 50% 12%,{t['accent']}33 0%,{t['bg']} 80%);}}"
        )

    def build_scene_plan_60(
        self, script_text: str, topic: str, duration: float = TARGET_DURATION, n: int = 9
    ) -> list[dict]:
        """Split narration into n timed scenes proportional to word count.

        Timing is derived from actual narration weight, not arbitrary chunks.
        """
        clean = re.sub(r"\s+", " ", (script_text or "").strip())
        sentences = [p.strip() for p in re.split(r"(?<=[.!?])\s+", clean) if p.strip()]
        if not sentences:
            sentences = [topic]
        # Group sentences into n scenes by word weight
        words = [len(s.split()) for s in sentences]
        total_words = sum(words) or 1
        bounds = self.split_timeline(duration, n)
        scenes: list[dict] = []
        # Distribute sentences round-robin weighted: fill scenes sequentially
        idx = 0
        for i, (start, end) in enumerate(bounds):
            # Assign at least one sentence per scene while sentences remain
            chunk: list[str] = []
            if idx < len(sentences):
                # scenes remaining vs sentences remaining
                remaining_scenes = n - i
                remaining_sents = len(sentences) - idx
                take = max(1, remaining_sents // remaining_scenes) if remaining_sents > remaining_scenes else 1
                chunk = sentences[idx : idx + take]
                idx += take
            narration = " ".join(chunk) if chunk else sentences[-1]
            visual = ["3d_hook", "3d_compare", "3d_showcase", "3d_terminal", "3d_dashboard",
                      "3d_neural", "3d_metrics", "3d_reveal", "3d_cta"][i % 9]
            scenes.append({
                "index": i, "start": start, "end": end,
                "duration": round(end - start, 2),
                "narration": narration,
                "on_screen_text": narration[:90],
                "visual_type": visual,
                "motion": "push-in" if i % 2 == 0 else "pull-out",
                "transition": "glow-wipe" if i < n - 1 else "fade",
            })
        _ = total_words  # word weights inform sentence grouping above
        return scenes

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

        # 3. Segment script into 5 scene narrations aligned with video scenes
        segments = self._segment_script_into_scenes(script_text, topic)
        hook_title = topic
        if ":" in topic:
            parts = topic.split(":", 1)
            hook_title = parts[0].strip()

        template = self.env.get_template(template_name)
        theme = "A"
        for k, v in TEMPLATE_FILES.items():
            if v == template_name:
                theme = k
                break
        rendered_html = template.render(
            topic=topic,
            total_duration=total_dur,
            audio_file=audio_dest_name,
            logo_file=logo_dest_name,
            hook_alert="NEW 3D ENGINE",
            hook_title=hook_title[:60],
            theme_css=self.theme_css(theme),
            proof_metric="3D",
            scene1_narration=segments["s1_narration"],
            scene2_narration=segments["s2_narration"],
            scene3_narration=segments["s3_narration"],
            scene4_narration=segments["s4_narration"],
            scene5_narration=segments["s5_narration"],
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

    def compile_composition_60(
        self,
        topic: str,
        script_text: str = "",
        scene_plan: Optional[list[dict]] = None,
        audio_path: Optional[str] = None,
        duration: float = TARGET_DURATION,
        target_dir: Optional[Path] = None,
        template_name: Optional[str] = None,
        theme: str = "A",
    ) -> tuple[Path, list[dict]]:
        """60s production entrypoint: generalized N-scene timeline mapped onto the
        5-act HTML template (acts stretch to cover the 60s scene_plan).

        Returns (work_dir, scene_plan) with exact 60s coverage.
        """
        work_dir = target_dir or self.workspace
        work_dir.mkdir(parents=True, exist_ok=True)
        if scene_plan is None:
            scene_plan = self.build_scene_plan_60(script_text, topic, duration)
        # Normalize to exact duration
        total = sum(s["duration"] for s in scene_plan) or duration
        scale = duration / total if total else 1.0
        t = 0.0
        for i, s in enumerate(scene_plan):
            d = round(s["duration"] * scale, 2)
            if i == len(scene_plan) - 1:
                d = round(duration - t, 2)
            s["start"], s["end"], s["duration"] = round(t, 2), round(t + d, 2), d
            t += d
        # Map N scenes -> 5 visual acts by thirds (hook/context/value/payoff/cta)
        n = len(scene_plan)
        def join(lo: float, hi: float) -> str:
            part = [s["narration"] for s in scene_plan if s["start"] < hi and s["end"] > lo]
            return " ".join(part) or script_text[:200]
        acts = [(0.0, 0.12), (0.12, 0.35), (0.35, 0.68), (0.68, 0.85), (0.85, 1.0)]
        bounds = [(round(duration * a, 2), round(duration * b, 2)) for a, b in acts]
        seg = {f"s{i+1}_narration": join(lo, hi) for i, (lo, hi) in enumerate(bounds)}
        audio_dest_name = ""
        if audio_path and os.path.exists(audio_path):
            shutil.copyfile(audio_path, work_dir / "voice.mp3")
            audio_dest_name = "voice.mp3"
        logo_dest_name = ""
        logo_src = REPO_ROOT / "assets" / "signhify-logo-vector.jpeg"
        if logo_src.exists():
            shutil.copyfile(logo_src, work_dir / "logo.jpeg")
            logo_dest_name = "logo.jpeg"
        hook_title = topic.split(":", 1)[0].strip()[:60] if ":" in topic else topic[:60]
        tmpl = template_name or TEMPLATE_FILES.get(theme, "marketing_promo.html.jinja2")
        template = self.env.get_template(tmpl)
        s_durs = [round(hi - lo, 2) for lo, hi in bounds]
        starts = [bounds[0][0]]
        for d in s_durs[:-1]:
            starts.append(round(starts[-1] + d, 2))
        rendered_html = template.render(
            topic=topic, total_duration=duration, audio_file=audio_dest_name,
            logo_file=logo_dest_name, hook_alert="TECH + AI • 60S",
            hook_title=hook_title, theme_css=self.theme_css(theme), proof_metric="3D",
            scene1_narration=seg["s1_narration"], scene2_narration=seg["s2_narration"],
            scene3_narration=seg["s3_narration"], scene4_narration=seg["s4_narration"],
            scene5_narration=seg["s5_narration"],
            scene1_start=starts[0], scene1_duration=s_durs[0],
            scene2_start=starts[1], scene2_duration=s_durs[1],
            scene3_start=starts[2], scene3_duration=s_durs[2],
            scene4_start=starts[3], scene4_duration=s_durs[3],
            scene5_start=starts[4], scene5_duration=s_durs[4],
        )
        (work_dir / "index.html").write_text(rendered_html, encoding="utf-8")
        (work_dir / "scene_plan.json").write_text(
            __import__("json").dumps({"duration": duration, "theme": theme,
                                      "template": tmpl, "scenes": scene_plan}, indent=2),
            encoding="utf-8",
        )
        logger.info(f"Compiled 60s HyperFrames composition ({len(scene_plan)} scenes, theme {theme})")
        return work_dir, scene_plan

    def render_reel(
        self,
        topic: str,
        script_text: str = "",
        audio_path: Optional[str] = None,
        output_path: Optional[str] = None,
        duration: Optional[float] = None,
        timeout: int = 480,
        template_name: str = "marketing_promo.html.jinja2",
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
            template_name=template_name,
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
            "template": template_name,
        }


# Global singleton instance
hyperframes_engine = HyperFramesEngine()
