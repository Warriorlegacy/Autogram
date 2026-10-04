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
    # Premium 3D/animated scene templates (F-J): reachable through the same
    # theme -> template lookup; A-E defaults are untouched (backward compat).
    "F": "neural_network.html.jinja2",
    "G": "data_flow.html.jinja2",
    "H": "terminal_code.html.jinja2",
    "I": "comparison.html.jinja2",
    "J": "growth_chart.html.jinja2",
}

# visual_type -> template file. build_scene_plan_60 assigns content-aware
# visual types; this dict resolves one to a concrete HyperFrames template
# (consumed by template_for_visual and the template tests).
VISUAL_TEMPLATE_MAP = {
    "3d_hook": "marketing_promo.html.jinja2",
    "3d_compare": "comparison.html.jinja2",
    "3d_showcase": "marketing_promo.html.jinja2",
    "3d_terminal": "terminal_code.html.jinja2",
    "3d_neural": "neural_network.html.jinja2",
    "3d_dataflow": "data_flow.html.jinja2",
    "3d_chart": "growth_chart.html.jinja2",
    "3d_cta": "marketing_promo.html.jinja2",
    # Legacy kinds kept for backward compatibility.
    "3d_dashboard": "marketing_promo.html.jinja2",
    "3d_metrics": "growth_chart.html.jinja2",
    "3d_reveal": "marketing_promo.html.jinja2",
}

# Content-aware visual kind scoring: keyword regex -> scene kind. Highest
# match count wins; ties break by list order (deterministic rotation).
_VISUAL_KEYWORDS = [
    ("3d_terminal", re.compile(
        r"terminal|code|deploy|command|cli|repo|console|shell|developer|github|commit|push|build", re.I)),
    ("3d_neural", re.compile(
        r"neural|network|model|agent|llm|brain|node|nodes|synapse|neuron|neurons|weights|layers|intelligence", re.I)),
    ("3d_dataflow", re.compile(
        r"data|pipeline|workflow|automate|automation|flow|process|processing|input|output|trigger|decision|execution|result|stage|packet", re.I)),
    ("3d_compare", re.compile(
        r"before|after|\bold\b|\bnew\b|\bvs\b|replace|instead|compare|comparison|versus|outdated|legacy|traditional|manual", re.I)),
    ("3d_chart", re.compile(
        r"grow|growth|scale|scaling|million|thousand|percent|%|\d+k|10x|100x|revenue|users|customers|metric|metrics|numbers|counter|views|followers", re.I)),
]


def _score_visual(narration: str, seed: int = 0) -> str:
    """Content-aware visual kind for a narration: highest keyword score wins;
    near-ties (within 1 point) rotate deterministically by `seed` so different
    scripts render different animated visuals while each scene still matches
    its narration; '3d_showcase' is the no-match fallback."""
    text = narration or ""
    best, near = -1, []
    for kind, rx in _VISUAL_KEYWORDS:
        score = len(rx.findall(text))
        if score > best:
            best, near = score, [kind]
        elif score >= best - 1:
            near.append(kind)
    if best <= 0:
        return "3d_showcase"
    return near[seed % len(near)]


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

    @staticmethod
    def template_for_visual(visual_type: str) -> str:
        """Resolve a scene visual_type to a concrete HyperFrames template."""
        return VISUAL_TEMPLATE_MAP.get(visual_type, "marketing_promo.html.jinja2")

    def _render_context(self, *, topic, total_duration, audio_file, logo_file,
                        hook_alert, hook_title, proof_metric, theme,
                        scene_narrations, scene_starts, scene_durations) -> dict:
        """Build the standard render context shared by both compile methods.
        Adds the kinetic-type shared assets (read from renderer/reels_shared/)
        so templates can use data-kinetic markup via _kinetic_head partial."""
        shared_dir = REPO_ROOT / "renderer" / "reels_shared"
        read_kinetic_css = (shared_dir / "kinetic_type.css").read_text(encoding="utf-8") if (shared_dir / "kinetic_type.css").exists() else ""
        read_kinetic_js = (shared_dir / "kinetic_type.js").read_text(encoding="utf-8") if (shared_dir / "kinetic_type.js").exists() else ""
        ctx = {
            "topic": topic,
            "total_duration": total_duration,
            "audio_file": audio_file,
            "logo_file": logo_file,
            "hook_alert": hook_alert,
            "hook_title": hook_title,
            "theme_css": self.theme_css(theme),
            "proof_metric": proof_metric,
            "read_kinetic_css": read_kinetic_css,
            "read_kinetic_js": read_kinetic_js,
        }
        for i in range(1, 6):
            ctx[f"scene{i}_narration"] = scene_narrations[f"s{i}_narration"]
            # Short headline for the scene body; narration lives in the sub-bar.
            ctx[f"scene{i}_headline"] = self._scene_headline(
                scene_narrations[f"s{i}_narration"], i - 1, 5)
            ctx[f"scene{i}_start"] = scene_starts[i - 1]
            ctx[f"scene{i}_duration"] = scene_durations[i - 1]
        return ctx

    # Content-aware visual selection: see module-level _score_visual/_scene_headline.

    def _scene_visual(self, narration: str, index: int, n: int, visual_seed: int = 0) -> str:
        """Content-aware visual kind: hook first, cta last, middle scenes
        scored by keyword regex against the narration (rotation tie-break by
        scene index + a per-script visual_seed so different scripts produce
        different visual mixes while each scene still matches its narration)."""
        if index == 0:
            return "3d_hook"
        if index == n - 1:
            return "3d_cta"
        return _score_visual(narration, seed=index + visual_seed)

    def _scene_headline(self, narration: str, index: int, n: int) -> str:
        """Short ≤6-word keyword-style headline for the scene body (the sub-bar
        shows the full narration — never duplicate it in the body).

        Deterministic frequency heuristic: pick the most frequent content words
        (non-stopwords), ties broken by first occurrence; falls back to the
        leading words when too few significant tokens remain.
        """
        low = narration.strip()
        if not low:
            return ""
        _stopwords = frozenset(
            """a an the and or but for with from your you it is are of to in on at by as
            that this these those not no so we our their they can will just get gets be
            been being do does did have has had more most than then there here what which
            who how all any about into over up down out off if while when where why because
            between both each few some such only own same too very don't won't can't it's
            that's you're we're i'm you've we've let's""".split()
        )
        words = re.findall(r"[A-Za-z0-9%.,'’!?-]+", low)
        sig = [w for w in words if w.lower() not in _stopwords and len(w) > 1]
        if len(sig) >= 2:
            seen: dict[str, list] = {}
            for w in sig:
                seen.setdefault(w.lower(), []).append(w)
            ranked = sorted(seen.values(), key=lambda lst: (-len(lst), words.index(lst[0])))
            return " ".join(lst[0] for lst in ranked[:6])
        return " ".join(words[:6]).rstrip(",;:") + "."

    def build_scene_plan_60(
        self, script_text: str, topic: str, duration: float = TARGET_DURATION, n: int = 9,
        visual_seed: int = 0
    ) -> list[dict]:
        """Split narration into n timed scenes proportional to word count.

        Timing is derived from actual narration weight, not arbitrary chunks.
        Each scene carries a content-aware visual_type (rotated by a per-script
        visual_seed so consecutive scripts differ) and a short headline so the
        on-screen graphic and text match the narration; the full narration is
        only shown in the single synced caption (sub-bar) layer.
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
            visual = self._scene_visual(narration, i, n, visual_seed)
            scenes.append({
                "index": i, "start": start, "end": end,
                "duration": round(end - start, 2),
                "narration": narration,
                "headline": self._scene_headline(narration, i, n),
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
        starts = [0.0, round(s1, 2), round(s1 + s2, 2), round(s1 + s2 + s3, 2), round(s1 + s2 + s3 + s4, 2)]
        ctx = self._render_context(
            topic=topic, total_duration=total_dur, audio_file=audio_dest_name,
            logo_file=logo_dest_name, hook_alert="NEW 3D ENGINE",
            hook_title=hook_title[:60], proof_metric="3D", theme=theme,
            scene_narrations=segments, scene_starts=starts,
            scene_durations=[s1, s2, s3, s4, s5],
        )
        rendered_html = template.render(**ctx)

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
        visual_seed: int = 0,
    ) -> tuple[Path, list[dict]]:
        """60s production entrypoint: generalized N-scene timeline mapped onto the
        5-act HTML template (acts stretch to cover the 60s scene_plan).

        `visual_seed` rotates the per-scene visual palette so consecutive
        scripts render different animated visuals while each scene still
        matches its narration.

        Returns (work_dir, scene_plan) with exact 60s coverage.
        """
        work_dir = target_dir or self.workspace
        work_dir.mkdir(parents=True, exist_ok=True)
        if scene_plan is None:
            scene_plan = self.build_scene_plan_60(script_text, topic, duration, visual_seed=visual_seed)
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
        # Content-aware template selection: pick the template matching the
        # dominant scene visual so the whole reel's aesthetic matches its
        # strongest scene; fall back to the theme mapping when none applies.
        if not template_name:
            dominant = max(
                (s.get("visual_type", "3d_showcase") for s in scene_plan),
                key=lambda v: sum(1 for s in scene_plan if s.get("visual_type") == v),
            )
            template_name = (
                VISUAL_TEMPLATE_MAP.get(dominant)
                or TEMPLATE_FILES.get(theme, "marketing_promo.html.jinja2")
            )
        tmpl = template_name or TEMPLATE_FILES.get(theme, "marketing_promo.html.jinja2")
        template = self.env.get_template(tmpl)
        s_durs = [round(hi - lo, 2) for lo, hi in bounds]
        starts = [bounds[0][0]]
        for d in s_durs[:-1]:
            starts.append(round(starts[-1] + d, 2))
        ctx = self._render_context(
            topic=topic, total_duration=duration, audio_file=audio_dest_name,
            logo_file=logo_dest_name, hook_alert="TECH + AI • 60S",
            hook_title=hook_title, proof_metric="3D", theme=theme,
            scene_narrations=seg, scene_starts=starts, scene_durations=s_durs,
        )
        rendered_html = template.render(**ctx)
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

        comp_dir = self.compile_composition_60(
            topic=topic,
            script_text=script_text,
            scene_plan=[dict(s) for s in self.build_scene_plan_60(script_text, topic, duration or TARGET_DURATION)],
            audio_path=audio_path,
            duration=duration or TARGET_DURATION,
            template_name=template_name,
            visual_seed=0,
        )[0]

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
