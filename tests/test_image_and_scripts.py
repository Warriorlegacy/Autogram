import pytest
from pathlib import Path
from src.content.script_writer import script_writer
from src.content.image_generator import image_generator

def test_script_writer_caption():
    sample_carousel = {
        "topic": "Why Context Caching Cuts LLM Costs",
        "pillar": "AI Tool Breakdown",
        "slides": [
            {
                "slide_number": 1,
                "headline": "How 1 API Parameter Cut Our Production Bill by 78%",
                "body": "Re-evaluating 10,000 prompt tokens on every loop is wasteful. Here is the KV-cache fix."
            },
            {
                "slide_number": 2,
                "headline": "The Hidden Cost of Static Tokens",
                "body": "Parsing system instructions over and over multiplies inference latency."
            },
            {
                "slide_number": 3,
                "headline": "Naive Re-Prompting vs Prompt Caching",
                "body": "Comparing traditional execution with cached state pointers."
            }
        ]
    }

    result = script_writer.generate_caption(sample_carousel)
    assert "caption" in result
    assert "hook" in result
    assert "hashtags" in result
    assert len(result["hashtags"]) >= 5
    assert "How 1 API Parameter Cut Our Production Bill by 78%" in result["caption"]
    assert "#AIEngineering" in result["caption"] or "#AutogramAI" in result["caption"]

def test_script_writer_reels_script():
    sample_carousel = {
        "topic": "Why Multi-Agent Orchestration Outperforms Monolithic LLMs",
        "pillar": "AI Tool Breakdown",
        "slides": [
            {
                "slide_number": 1,
                "headline": "Stop Doing Everything in One Giant Prompt",
                "body": "State management beats context stuffing."
            },
            {
                "slide_number": 2,
                "headline": "The Single-Prompt Failure Mode",
                "body": "When tasks exceed 8,000 tokens, monolithic prompts hallucinate."
            }
        ]
    }

    reel = script_writer.generate_reels_script(sample_carousel)
    assert "title" in reel
    assert "segments" in reel
    assert len(reel["segments"]) >= 4
    assert "formatted_text" in reel
    assert "HOOK" in reel["formatted_text"]
    assert "CALL TO ACTION" in reel["formatted_text"]

def test_script_writer_x_thread():
    sample_carousel = {
        "topic": "Coolify: Self-Hosted Heroku & Vercel Alternative",
        "pillar": "FOSS SaaS Alternatives",
        "slides": [
            {"slide_number": 1, "headline": "Stop Paying $200/mo on Cloud Hosting", "body": "Here is the open source PaaS."},
            {"slide_number": 2, "headline": "Coolify Overview", "body": "Self-hosted PaaS with Docker.", "proof_or_example": "35,000 GitHub stars, AGPL."},
            {"slide_number": 3, "headline": "Architecture", "body": "Runs on any Linux server with Traefik."},
            {"slide_number": 4, "headline": "1-Line Setup", "body": "Run curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash", "proof_or_example": "curl install.sh | bash"},
            {"slide_number": 5, "headline": "Comparison Matrix", "body": "$0/mo vs $200/mo."},
            {"slide_number": 6, "headline": "Honest Gotchas", "body": "Requires 2GB RAM minimum."}
        ]
    }
    thread = script_writer.generate_x_thread(sample_carousel)
    assert "1/" in thread
    assert "Coolify" in thread
    assert "FOSS" in thread

def test_script_writer_linkedin_post():
    sample_carousel = {
        "topic": "Stirling-PDF: Open Source Local PDF Manipulation",
        "pillar": "FOSS SaaS Alternatives",
        "slides": [
            {"slide_number": 1, "headline": "Why Are You Still Paying for Adobe Acrobat?", "body": "PDF editing belongs on your local machine."},
            {"slide_number": 2, "headline": "Stirling-PDF", "body": "Full-featured open source web UI.", "proof_or_example": "50,000+ stars."},
            {"slide_number": 3, "headline": "Architecture", "body": "Java Spring Boot + Docker."},
            {"slide_number": 4, "headline": "Setup", "body": "docker run -p 8080:8080 frooodle/s-pdf", "proof_or_example": "docker run -p 8080:8080"}
        ]
    }
    post = script_writer.generate_linkedin_post(sample_carousel)
    assert "SaaS subscription fatigue" in post
    assert "Stirling-PDF" in post
    assert "#OpenSource" in post


def test_image_generator_prompt_enhancement():
    enhanced = image_generator._enhance_prompt("A minimalist data server rack", style_preset="cyber-minimalist")
    assert "minimalist data server rack" in enhanced
    assert "dark obsidian" in enhanced

def test_publisher_dry_run_and_boolean_container():
    from src.instagram.publisher import InstagramPublisher
    pub = InstagramPublisher(dry_run=True)
    assert pub.dry_run is True
    
    # Test container creation returns simulated ID in dry run
    container_id = pub.create_item_container("https://iili.io/test.jpg", alt_text="Test slide")
    assert container_id.startswith("mock_child_cntr_")
    
    # Test invalid non-HTTP URL raises ValueError
    import pytest
    with pytest.raises(ValueError, match="strictly requires an absolute public HTTP/HTTPS URL"):
        pub._forced_dry_run = False  # Temporarily toggle off dry-run to test URL validator
        pub.create_item_container("/output/invalid/path.jpg")
    pub._forced_dry_run = True

def test_uploader_public_cdn_fallback():
    from src.storage.uploader import uploader
    # When given dummy paths, ensures formatted URLs are absolute HTTP/HTTPS
    urls = uploader.upload_slide_images(["output/test/slide_01.jpg"], "2026-09-10", dry_run=True)
    assert len(urls) == 1
    assert urls[0].startswith("http://") or urls[0].startswith("https://")

def test_uploader_imgbb_prioritization_and_key():
    from src.config import settings
    from src.storage.uploader import uploader
    # Ensure default IMGBB API key is configured
    assert settings.imgbb_api_key is not None
    assert len(settings.imgbb_api_key) == 32

    # Verify upload_slide_images prioritizes imgbb when mock succeeds
    import unittest.mock as mock
    with mock.patch.object(uploader, "_upload_to_imgbb", return_value="https://i.ibb.co/mock_test/slide_01.jpg") as mock_imgbb:
        urls = uploader.upload_slide_images(["output/2026-09-12/slide_01.jpg"], "2026-09-12", dry_run=False)
        assert len(urls) == 1
        assert "i.ibb.co" in urls[0]
        mock_imgbb.assert_called_once()

def test_landing_theme_picker_markup():
    import pathlib
    html = pathlib.Path("index.html").read_text(encoding="utf-8")
    assert "theme-picker-dropdown" in html
    for theme in ["dark", "cyberpunk", "neumorphic", "swiss-light", "bento-grid", "light"]:
        assert f'data-theme="{theme}"' in html

def test_three_scene_theme_reactivity():
    import pathlib
    js = pathlib.Path("js/three-scene.js").read_text(encoding="utf-8")
    assert "PALETTES" in js
    assert "data-theme" in js
    assert "cyberpunk" in js
    assert "neumorphic" in js

