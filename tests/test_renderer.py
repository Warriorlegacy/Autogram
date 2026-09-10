import pytest
from pathlib import Path
from renderer.render import CarouselRenderer
from renderer.validate import validate_image_file, validate_slide_content

def test_validate_slide_content():
    valid_slide = {
        "slide_number": 1,
        "headline": "Under 80 chars headline",
        "body": "A short and concise body under 240 characters."
    }
    warnings = validate_slide_content(valid_slide)
    assert len(warnings) == 0

    long_slide = {
        "slide_number": 2,
        "headline": "A" * 90,
        "body": "B" * 260
    }
    warnings = validate_slide_content(long_slide)
    assert len(warnings) == 2

def test_carousel_rendering(tmp_path):
    renderer = CarouselRenderer()
    sample_carousel = {
        "pillar": "AI Tool Breakdown",
        "topic": "Test Pipeline",
        "publication_date": "2026-09-09",
        "slides": [
            {
                "slide_number": 1,
                "layout": "hook",
                "headline": "Testing Hook Template Rendering",
                "body": "Verifying 1080x1350 resolution and aspect ratio.",
                "proof_or_example": "Verified in automated test."
            },
            {
                "slide_number": 2,
                "layout": "standard",
                "headline": "Standard Template Slide",
                "body": "Ensuring text formatting and typography are intact.",
                "proof_or_example": "Playwright headless test."
            }
        ]
    }

    rendered_paths = renderer.render_carousel(sample_carousel, tmp_path)
    assert len(rendered_paths) == 2

    for p in rendered_paths:
        val = validate_image_file(p)
        assert val["valid"] is True
        assert val["width"] == 1080
        assert val["height"] == 1350
        assert val["format"] in ["JPEG", "JPG"]

def test_all_theme_variants_render(tmp_path):
    from renderer.render import AVAILABLE_THEMES
    renderer = CarouselRenderer()
    
    for theme in AVAILABLE_THEMES:
        carousel = {
            "pillar": "AI Automation",
            "topic": f"Testing {theme} Theme",
            "theme": theme,
            "publication_date": "2026-09-10",
            "slides": [
                {
                    "slide_number": 1,
                    "layout": "hook",
                    "headline": f"Theme {theme.upper()} Active",
                    "body": "Verifying multi-theme dynamic layout."
                }
            ]
        }
        theme_dir = tmp_path / theme
        paths = renderer.render_carousel(carousel, theme_dir)
        assert len(paths) == 1
        val = validate_image_file(paths[0])
        assert val["valid"] is True
        assert val["width"] == 1080
        assert val["height"] == 1350

