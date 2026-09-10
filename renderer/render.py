"""
Playwright-based HTML/CSS slide renderer for Instagram Carousels.
Renders 1080x1350 JPEG slides with deterministic typography and layout.
"""

import json
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

from renderer.validate import validate_slide_content, validate_image_file, TARGET_WIDTH, TARGET_HEIGHT

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
CSS_FILE = Path(__file__).parent / "css" / "design-system.css"

LAYOUT_TO_TEMPLATE = {
    "hook": "hook.html",
    "standard": "standard.html",
    "explanation": "standard.html",
    "checklist": "checklist.html",
    "comparison": "comparison.html",
    "diagram": "diagram.html",
    "framework": "framework.html",
    "takeaway": "takeaway.html",
    "cta": "cta.html"
}

class CarouselRenderer:
    def __init__(self, brand_profile: dict | None = None):
        self.template_dir = TEMPLATE_DIR
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False
        )
        if brand_profile is None:
            brand_file = Path(__file__).parent.parent / "data" / "brand.json"
            if brand_file.exists():
                try:
                    brand_profile = json.loads(brand_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

        self.brand = brand_profile or {
            "brand_name": "Autogram AI",
            "handle": "@piyush.glitch",
            "watermark": "@SIGNHIFY.STUDIO",
            "name": "Piyush | AI Automation & Growth Systems",
            "secondary_links": "@ZERO.CANON · MAKERZZ.SPACE",
            "colors": {}
        }
        self.css_content = CSS_FILE.read_text(encoding="utf-8") if CSS_FILE.exists() else ""

    def render_slide_html(self, slide: dict, meta: dict) -> str:
        """Render slide template to HTML string with inlined CSS."""
        layout = slide.get("layout", "standard").lower()
        template_name = LAYOUT_TO_TEMPLATE.get(layout, "standard.html")
        template = self.jinja_env.get_template(template_name)

        html = template.render(
            slide=slide,
            meta=meta,
            brand=self.brand
        )
        # Inline CSS to guarantee robust rendering across any environment/browser
        if self.css_content and '<link rel="stylesheet"' in html:
            html = html.replace(
                '<link rel="stylesheet" href="../css/design-system.css">',
                f'<style>\n{self.css_content}\n</style>'
            )
        return html

    def render_carousel(self, carousel_data: dict, output_dir: str | Path) -> list[str]:
        """
        Renders all slides in carousel_data to 1080x1350 JPEG images in output_dir.
        Returns list of generated image file paths.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        slides = carousel_data.get("slides", [])
        total_slides = len(slides)
        meta = {
            "total_slides": total_slides,
            "pillar": carousel_data.get("pillar", "AI & Technology"),
            "topic": carousel_data.get("topic", ""),
            "date": carousel_data.get("publication_date", "")
        }

        rendered_paths = []

        with sync_playwright() as p:
            # Launch headless Chromium
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": TARGET_WIDTH, "height": TARGET_HEIGHT},
                device_scale_factor=1.0
            )
            page = context.new_page()

            for idx, slide in enumerate(slides, start=1):
                slide["slide_number"] = slide.get("slide_number", idx)
                warnings = validate_slide_content(slide)
                for w in warnings:
                    logger.warning(w)

                html_content = self.render_slide_html(slide, meta)
                
                # Render in browser
                page.set_content(html_content, wait_until="domcontentloaded", timeout=15000)
                
                # Allow a short moment for fonts if loading from Google Fonts
                page.wait_for_timeout(350)

                slide_filename = f"slide_{slide['slide_number']:02d}.jpg"
                slide_filepath = out_path / slide_filename

                page.screenshot(
                    path=str(slide_filepath),
                    type="jpeg",
                    quality=95,
                    clip={"x": 0, "y": 0, "width": TARGET_WIDTH, "height": TARGET_HEIGHT}
                )

                # Validate rendered output dimensions & format
                validate_image_file(slide_filepath)
                rendered_paths.append(str(slide_filepath))
                logger.info(f"Rendered slide {slide['slide_number']} -> {slide_filepath.name}")

            browser.close()

        return rendered_paths

def render_sample(output_dir: str = "output/sample"):
    """Utility to render a sample carousel for visual verification."""
    sample_path = Path(__file__).parent.parent / "data" / "brand.json"
    brand = json.loads(sample_path.read_text(encoding="utf-8")) if sample_path.exists() else {}

    sample_carousel = {
        "content_id": "IG-SAMPLE-001",
        "publication_date": "2026-09-09",
        "pillar": "AI Tool Breakdown",
        "topic": "Why Multi-Agent Systems Beat Monolithic LLMs",
        "slides": [
            {
                "slide_number": 1,
                "layout": "hook",
                "headline": "Why Multi-Agent Systems Are Replacing Giant Prompts",
                "body": "State management and modular verification cut failure rates by 60%.",
                "proof_or_example": "Benchmarked across 500 long-horizon engineering tasks."
            },
            {
                "slide_number": 2,
                "layout": "standard",
                "headline": "The Single-Prompt Bottleneck",
                "body": "When one prompt handles research, drafting, and validation, context drift causes subtle hallucinations that compound downstream.",
                "proof_or_example": "Context dilution accelerates past 8,000 tokens."
            },
            {
                "slide_number": 3,
                "layout": "comparison",
                "headline": "Monolithic vs Compound Architecture",
                "body": "Comparing the fragility of all-in-one execution against specialized role boundaries."
            },
            {
                "slide_number": 4,
                "layout": "diagram",
                "headline": "The 3-Stage Autonomous Pipeline",
                "body": "How production workflows achieve zero-touch reliability."
            },
            {
                "slide_number": 5,
                "layout": "checklist",
                "headline": "4 Production Guardrails",
                "body": "Non-negotiable requirements before turning on autonomous publishing.",
                "proof_or_example": "Deterministic pydantic validation\nDedicated HTML layout engine\nPre-publish fact checking gate\nBounded retry loops with fail-closed"
            },
            {
                "slide_number": 6,
                "layout": "framework",
                "headline": "The Fail-Closed Rule",
                "body": "If evidence confidence drops below 90% or the quality gate rejects copy twice, halt immediately. Never publish mediocre output unattended.",
                "proof_or_example": "One bad automated post destroys weeks of credibility."
            },
            {
                "slide_number": 7,
                "layout": "takeaway",
                "headline": "Automate Mechanics Aggressively. Automate Judgment Conservatively.",
                "body": "Your code should handle scheduling, rendering, and API distribution. Your quality gates should protect your reputation."
            },
            {
                "slide_number": 8,
                "layout": "cta",
                "headline": "Build Your Own AI Autopilot",
                "body": "Save this carousel for the architecture blueprint, and swipe up to clone the repository."
            }
        ]
    }

    renderer = CarouselRenderer(brand_profile=brand)
    paths = renderer.render_carousel(sample_carousel, output_dir)
    print(f"Sample carousel successfully rendered {len(paths)} slides to: {output_dir}")
    return paths

if __name__ == "__main__":
    render_sample()
