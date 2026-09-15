"""
tests/test_hyperframes_carousel.py
Tests Signhify Studio promo carousel generation, slide layout compilation,
branding assets, comment triggers, and pipeline execution.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.content.hyperframes_carousel import SignhifyCarouselEngine
from scripts.pipeline_carousel import run_carousel_pipeline


def test_carousel_engine_initialization():
    """Verifies that SignhifyCarouselEngine initializes with proper brand and slides."""
    engine = SignhifyCarouselEngine()
    assert engine.brand["brand_name"] == "Signhify Studio"
    assert "@signhify.studio" in engine.brand["handle"]
    slides = engine.get_default_slides()
    assert len(slides) == 7
    layouts = [s["layout"] for s in slides]
    assert layouts == ["hook", "comparison", "architecture", "features", "proof", "quickstart", "cta"]


def test_carousel_slide_html_compilation():
    """Verifies that all 7 slide layouts compile into valid HTML with branding and logo."""
    engine = SignhifyCarouselEngine()
    slides = engine.get_default_slides()

    for idx, slide in enumerate(slides, start=1):
        html = engine.render_slide_html(slide, slide_index=idx, total_slides=len(slides))
        assert "<!DOCTYPE html>" in html
        assert "Signhify Studio" in html
        assert f"{idx:02d} / 07" in html
        assert "@signhify.studio" in html

        # Layout specific assertions
        if slide["layout"] == "hook":
            assert "terminal-box" in html
            assert "Swipe ➔" in html
        elif slide["layout"] == "comparison":
            assert "compare-cards-container" in html
            assert "$5,000" in html
        elif slide["layout"] == "architecture":
            assert "arch-flow" in html
            assert "Spatial Intent" in html
        elif slide["layout"] == "features":
            assert "bento-grid" in html
            assert "60 FPS" in html
        elif slide["layout"] == "proof":
            assert "+320%" in html
        elif slide["layout"] == "quickstart":
            assert "signhify.dpdns.org" in html
            assert "STEP 01" in html
        elif slide["layout"] == "cta":
            assert "Save Post 🔖" in html
            assert "3D" in html


def test_carousel_caption_generation():
    """Verifies that the generated post caption has high hook rate and comment trigger."""
    engine = SignhifyCarouselEngine()
    caption = engine.generate_caption()
    assert "Apple-grade 3D scroll website" in caption
    assert 'Comment "3D"' in caption
    assert "https://signhify.dpdns.org" in caption
    assert "#signhify" in caption
    assert "#threejs" in caption


def test_pipeline_carousel_dry_run(tmp_path):
    """Verifies that the carousel pipeline runs in dry-run mode and creates manifest."""
    fake_images = [str(tmp_path / f"slide_{i:02d}.jpg") for i in range(1, 8)]
    for img in fake_images:
        Path(img).write_bytes(b"mock image data")

    with patch.object(SignhifyCarouselEngine, "render_carousel", return_value=fake_images):
        with patch("src.storage.uploader.AssetUploader.upload_carousel", return_value=[f"https://cdn.example.com/{i}.jpg" for i in range(1, 8)]):
            with patch("src.instagram.publisher.InstagramPublisher.publish_carousel", return_value="mock_carousel_123"):
                manifest = run_carousel_pipeline(
                    topic="Signhify Studio 3D Launch",
                    dry_run=True,
                    output_base_dir=tmp_path
                )

                assert manifest["dry_run"] is True
                assert manifest["slides_count"] == 7
                assert (tmp_path / "manifest.json").exists()
