"""
tests/test_glitch_hormozi_engine.py - Verification for the Makerzz / Hormozi Autopilot System
Validates 8-slide generation, HTML template rendering with Signhify Studio branding,
and comment AUTO lead capture.
"""

import pytest
from pathlib import Path
from src.content.generator import ContentGenerator
from src.leads.comment_automation import CommentLeadAutomation
from renderer.render import CarouselRenderer, LAYOUT_TO_TEMPLATE

def test_glitch_hormozi_carousel_generation():
    generator = ContentGenerator()
    topic = {
        "title": "Autonomous Omnipresence Posting",
        "pillar": "AI Automation",
        "style": "glitch-hormozi"
    }
    carousel = generator.generate_carousel(topic, sources=[])
    
    assert carousel["theme"] == "glitch"
    assert len(carousel["slides"]) == 8
    
    layouts = [s["layout"] for s in carousel["slides"]]
    assert "authority_hook" in layouts
    assert "receipt" in layouts
    assert "competitor" in layouts
    assert "calendar_matrix" in layouts
    assert "pipeline" in layouts
    assert "mega_cta" in layouts

def test_template_html_rendering():
    renderer = CarouselRenderer()
    
    test_slides = [
        {"slide_number": 1, "layout": "authority_hook", "category": "ALEX HORMOZI-STYLE", "headline": "Autonomous Posting.", "subtitle": "Be everywhere.", "image_path": ""},
        {"slide_number": 2, "layout": "receipt", "headline": "The Hormozi rule: be everywhere.", "receipt_title": "MANUAL OMNIPRESENCE · PER MONTH", "items": [{"task": "RESEARCH", "hours": "8 HRS"}], "total_hours": "50 HRS", "annotation": "quit by month two"},
        {"slide_number": 4, "layout": "competitor", "step_label": "STEP 2", "headline": "Paste any profile link.", "subtext": "Yours or competitors."},
        {"slide_number": 5, "layout": "calendar_matrix", "step_label": "STEP 3", "headline": "It writes your month.", "subtext": "Scripts, hooks and captions."},
        {"slide_number": 6, "layout": "pipeline", "step_label": "STEP 4", "headline": "It renders everything.", "subtext": "Carousels and video."},
        {"slide_number": 8, "layout": "mega_cta", "cta_prefix": "comment", "trigger_word": "AUTO", "subtext": "Get the autopilot.", "button_text": "RUN IT →"}
    ]
    
    meta = {
        "total_slides": 8,
        "theme": "glitch",
        "theme_class": "theme-glitch"
    }
    
    for slide in test_slides:
        html = renderer.render_slide_html(slide, meta)
        assert html is not None
        assert "SIGNHIFY.STUDIO" in html
        assert "<html" in html
        assert "</html>" in html

def test_comment_auto_lead_capture():
    automation = CommentLeadAutomation()
    result = automation.process_incoming_comment(
        user_handle="@alex_creator",
        comment_text="AUTO please send blueprint",
        platform="instagram"
    )
    
    assert result["status"] == "dispatched"
    assert result["trigger"] == "AUTO"
    assert "Piyush Raj Singh" in result["dm_message"]
    assert "signhify.studio" in result["dm_message"]
