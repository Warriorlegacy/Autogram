"""
Signhify Studio Viral Promo Carousel Generator & Playwright Renderer.
Generates 1080x1350 (4:5 vertical portrait) high-converting multi-slide carousels
featuring the Signhify vector logo, deep obsidian aesthetics, neon emerald accents,
architecture blueprints, feature comparisons, and viral comment '3D' CTA.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

from renderer.validate import validate_image_file, TARGET_WIDTH, TARGET_HEIGHT

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = REPO_ROOT / "renderer" / "templates" / "carousel"
LOGO_PATH = REPO_ROOT / "assets" / "signhify-logo-vector.jpeg"
LOGO_PATH_PNG = REPO_ROOT / "assets" / "signhify-logo-vector.png"


class SignhifyCarouselEngine:
    """
    Autonomous engine that synthesizes and renders Apple-grade promotional
    carousel slides for Signhify Studio (signhify.dpdns.org / @signhify.studio).
    """

    def __init__(self, brand_profile: Optional[dict] = None):
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=False
        )
        self.template_name = "signhify_promo_slide.html.jinja2"

        if brand_profile is None:
            brand_file = REPO_ROOT / "data" / "brand.json"
            if brand_file.exists():
                try:
                    brand_profile = json.loads(brand_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

        self.brand = brand_profile or {
            "brand_name": "Signhify Studio",
            "handle": "@signhify.studio",
            "watermark": "SIGNHIFY.STUDIO",
            "url": "https://signhify.dpdns.org"
        }

        self.logo_base64 = self._load_logo_base64()

    def _load_logo_base64(self) -> str:
        """Reads vector logo and encodes as base64 data URI for zero-latency local rendering."""
        for path, mime in [(LOGO_PATH, "image/jpeg"), (LOGO_PATH_PNG, "image/png")]:
            if path.exists():
                try:
                    data = base64.b64encode(path.read_bytes()).decode("utf-8")
                    return f"data:{mime};base64,{data}"
                except Exception as e:
                    logger.warning(f"Failed to read logo from {path}: {e}")
        return ""

    def get_default_slides(self, topic: Optional[str] = None) -> list[dict]:
        """
        Returns the canonical 7-slide viral marketing structure for Signhify Studio.
        """
        return [
            {
                "layout": "hook",
                "eyebrow": "NEW REVOLUTION",
                "headline_html": "We Built an Apple-Grade <span class=\"highlight\">3D Scroll Website</span> in 10 Minutes with AI",
                "subtext": "Stop paying $5,000 for static 2D sites in 2026. The entire web design landscape just changed forever.",
                "terminal_prompt": "Create an immersive dark-mode portfolio with interactive Three.js floating geometry, responsive mobile camera paths, and 60 FPS scroll triggers."
            },
            {
                "layout": "comparison",
                "eyebrow": "THE REALITY CHECK",
                "headline_html": "The <span class=\"highlight\">$5,000 Agency Tax</span> vs. Autonomous AI",
                "subtext": "Traditional 3D web development is broken. Compare the friction:"
            },
            {
                "layout": "architecture",
                "eyebrow": "ENGINEERING DEEP DIVE",
                "headline_html": "How Signhify Works <span class=\"highlight\">Under the Hood</span>",
                "subtext": "From human intent to production WebGL shaders in 4 autonomous stages:"
            },
            {
                "layout": "features",
                "eyebrow": "CORE CAPABILITIES",
                "headline_html": "<span class=\"highlight\">4 Superpowers</span> Live in Your Browser",
                "subtext": "Everything you need to ship world-class spatial websites without writing 3D math."
            },
            {
                "layout": "proof",
                "eyebrow": "HARD DATA & ROI",
                "headline_html": "Why 3D Websites Convert <span class=\"highlight\">3X Better</span>",
                "subtext": "Real benchmarks from modern interactive landing pages:"
            },
            {
                "layout": "quickstart",
                "eyebrow": "60-SECOND BLUEPRINT",
                "headline_html": "Launch Your 3D Site <span class=\"highlight\">Today in 4 Steps</span>",
                "subtext": "No credit card. No complex setup. Zero installation."
            },
            {
                "layout": "cta",
                "eyebrow": "FREE BETA ACCESS",
                "headline_html": "Build Your 3D Website <span class=\"highlight\">Free Today</span>",
                "subtext": "Stop building flat, boring websites in 2026. Start shipping immersive 3D experiences."
            }
        ]

    def render_slide_html(self, slide: dict, slide_index: int, total_slides: int) -> str:
        """Renders Jinja2 HTML for a specific carousel slide."""
        template = self.jinja_env.get_template(self.template_name)
        slide_num_formatted = f"{slide_index:02d} / {total_slides:02d}"
        is_last = (slide_index == total_slides)

        return template.render(
            slide=slide,
            slide_number=slide_index,
            slide_number_formatted=slide_num_formatted,
            is_last_slide=is_last,
            logo_base64=self.logo_base64,
            brand=self.brand
        )

    def render_carousel(self, slides: list[dict], output_dir: str | Path) -> list[str]:
        """
        Renders all slides to 1080x1350 JPEG images in output_dir using Playwright.
        Returns the list of absolute image file paths.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        total_slides = len(slides)

        logger.info(f"Rendering {total_slides} promo carousel slides to {out_path}...")
        rendered_paths = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": TARGET_WIDTH, "height": TARGET_HEIGHT},
                device_scale_factor=1.0
            )
            page = context.new_page()

            for idx, slide in enumerate(slides, start=1):
                html_content = self.render_slide_html(slide, idx, total_slides)
                page.set_content(html_content, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(450)  # Font rendering stabilization

                slide_filename = f"slide_{idx:02d}.jpg"
                slide_filepath = out_path / slide_filename

                page.screenshot(
                    path=str(slide_filepath),
                    type="jpeg",
                    quality=95,
                    clip={"x": 0, "y": 0, "width": TARGET_WIDTH, "height": TARGET_HEIGHT}
                )

                validate_image_file(slide_filepath, expected_width=TARGET_WIDTH, expected_height=TARGET_HEIGHT)
                rendered_paths.append(str(slide_filepath))
                logger.info(f"✓ Rendered carousel slide {idx}/{total_slides}: {slide_filepath.name}")

            browser.close()

        return rendered_paths

    def generate_caption(self, topic: Optional[str] = None) -> str:
        """Generates viral high-converting Instagram caption with the comment '3D' CTA trigger."""
        return (
            "⚡ We built an Apple-grade 3D scroll website in 10 minutes with AI.\n\n"
            "Most founders, creators, and web agencies think interactive 3D requires:\n"
            "✕ $5,000+ agency invoices\n"
            "✕ 4 to 6 weeks of back-and-forth\n"
            "✕ Hundreds of lines of Three.js & WebGL shader math\n\n"
            "We completely broke that equation.\n\n"
            "Signhify Studio turns a single plain-English prompt into an interactive 60 FPS WebGL experience "
            "with scroll-triggered camera motion and 1-click clean MIT-licensed code export.\n\n"
            "👉 Try it free right now: https://signhify.dpdns.org\n\n"
            "💬 Comment \"3D\" below and I'll DM you the direct link + our top 5 viral 3D prompt blueprints immediately!\n\n"
            "🔖 Save this post for your next website redesign.\n\n"
            ".\n.\n"
            "#signhify #3dweb #threejs #webgl #webdev #frontend #webdesign #uiux #indiehackers #saas #javascript #creativecoding #applewebdesign #nocode #buildinpublic"
        )

    def generate_and_render_promo_carousel(
        self,
        output_dir: str | Path,
        topic: Optional[str] = None
    ) -> dict:
        """
        Orchestrates complete promo carousel creation:
        1. Compiles 7 viral slides.
        2. Renders all 1080x1350 JPEG images via Playwright.
        3. Formulates the high-converting caption with comment trigger.
        Returns a dict with paths and metadata.
        """
        slides = self.get_default_slides(topic)
        image_paths = self.render_carousel(slides, output_dir)
        caption = self.generate_caption(topic)

        return {
            "image_paths": image_paths,
            "caption": caption,
            "slides_count": len(image_paths),
            "output_dir": str(output_dir),
            "topic": topic or "Signhify Autonomous 3D Web Engine"
        }
