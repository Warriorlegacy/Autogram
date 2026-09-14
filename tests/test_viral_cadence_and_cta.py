"""
Tests for 3x Reels, 2x Stories, 2x Carousels cadence, zero repetition, and mandatory CTA:
'Follow signhify.studio for more.'
"""

import re
from pathlib import Path
import pytest

from scripts.pipeline_reels import (
    generate_reel_content,
    get_unique_viral_reel_topic,
    CURATED_VIRAL_REEL_TOPICS,
)
from src.content.generator import generator
from src.content.script_writer import script_writer
from src.research.scorer import scorer


def test_reel_script_ends_with_mandatory_cta(monkeypatch):
    """Verify generate_reel_content strictly terminates with 'Follow signhify.studio for more.'"""
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setattr(generator, "_free_narration", lambda prompt: None)
    content = generate_reel_content("Uptime Kuma Monitoring")
    script = content["script"].strip()
    assert script.endswith("Follow signhify.studio for more."), f"Script did not end with mandatory CTA: {script}"
    assert "signhify.studio" in content["caption"].lower()


def test_generator_reel_script_ends_with_mandatory_cta(monkeypatch):
    """Verify generator.generate_reel_script strictly terminates with 'Follow signhify.studio for more.'"""
    monkeypatch.setattr(generator, "_free_narration", lambda prompt: None)
    script_data = generator.generate_reel_script("PocketBase Architecture", "Self-Hosted Architecture")
    narration = script_data["narration"].strip()
    assert narration.endswith("Follow signhify.studio for more."), f"Narration did not end with mandatory CTA: {narration}"


def test_story_content_includes_mandatory_cta():
    """Verify generate_story_content cta_text includes 'Follow signhify.studio for more'."""
    story = generator.generate_story_content("Documenso FOSS Signing", "FOSS SaaS Alternatives")
    cta = story["cta_text"]
    assert "Follow signhify.studio for more" in cta, f"Story CTA missing target phrase: {cta}"


def test_script_writer_reels_script_spoken_outro():
    """Verify script_writer.generate_reels_script segment 5 outro includes the mandatory CTA."""
    dummy_carousel = {
        "topic": "Coolify Cloud",
        "slides": [
            {"headline": "Ditch Vercel", "body": "Self host Coolify"},
            {"headline": "Setup", "body": "docker compose up -d"},
        ]
    }
    reels_script = script_writer.generate_reels_script(dummy_carousel)
    cta_segment = reels_script["segments"][-1]
    assert "Follow signhify.studio for more." in cta_segment["spoken"]


def test_script_writer_caption_cta():
    """Verify script_writer.generate_caption includes 'Follow signhify.studio for more.'"""
    dummy_carousel = {
        "topic": "SearXNG Private Search",
        "slides": [{"headline": "Private Search", "body": "Zero tracking"}]
    }
    meta = script_writer.generate_caption(dummy_carousel)
    assert "Follow signhify.studio for more." in meta["caption"]


def test_unique_viral_reel_topic_selection():
    """Verify get_unique_viral_reel_topic selects a valid curated topic and respects override."""
    override = "Custom Test Topic"
    assert get_unique_viral_reel_topic(override) == override

    auto_topic = get_unique_viral_reel_topic()
    assert auto_topic in [c["topic"] for c in CURATED_VIRAL_REEL_TOPICS]


def test_scorer_fallback_avoids_identical_selection():
    """Verify scorer.select_best_topic selects unposted topic or the topic with least recent footprint."""
    memory = {
        "recent_posts": [
            {"topic": "Coolify: Self-Hosted PaaS", "score": 90},
            {"topic": "Documenso: Open Source Signing", "score": 90},
        ],
        "banned_topics": []
    }
    candidates = [
        {"topic": "Coolify: Self-Hosted PaaS", "pillar": "FOSS SaaS Alternatives"},
        {"topic": "Documenso: Open Source Signing", "pillar": "FOSS SaaS Alternatives"},
        {"topic": "PocketBase: Single-File Database", "pillar": "Self-Hosted Architecture"},
    ]
    selection = scorer.select_best_topic(candidates, memory=memory)
    # PocketBase was never posted, so it MUST win over Coolify and Documenso
    assert selection["winner"]["topic"] == "PocketBase: Single-File Database"

    # Now test when ALL candidate topics match recent memory:
    candidates_all_in_memory = [
        {"topic": "Coolify: Self-Hosted PaaS", "pillar": "FOSS SaaS Alternatives"},
        {"topic": "Documenso: Open Source Signing", "pillar": "FOSS SaaS Alternatives"},
    ]
    fallback_sel = scorer.select_best_topic(candidates_all_in_memory, memory=memory)
    # Documenso was posted at index 1 (older than Coolify at index 0), so Documenso must be chosen!
    assert fallback_sel["winner"]["topic"] == "Documenso: Open Source Signing"


def test_workflow_cadence_configurations():
    """Verify daily_reels.yml (3x), daily-story.yml (2x), and daily-post.yml (2x) cron schedules."""
    root = Path(__file__).parent.parent
    reels_yml = (root / ".github" / "workflows" / "daily_reels.yml").read_text(encoding="utf-8")
    story_yml = (root / ".github" / "workflows" / "daily-story.yml").read_text(encoding="utf-8")
    post_yml = (root / ".github" / "workflows" / "daily-post.yml").read_text(encoding="utf-8")
    video_yml = (root / ".github" / "workflows" / "daily-video.yml").read_text(encoding="utf-8")

    # 3 Viral Reels daily
    reels_crons = re.findall(r"-\s*cron:\s*['\"]([^'\"]+)['\"]", reels_yml)
    assert len(reels_crons) == 3, f"Expected 3 cron triggers in daily_reels.yml, got {reels_crons}"

    # 2 Stories daily
    story_crons = re.findall(r"-\s*cron:\s*['\"]([^'\"]+)['\"]", story_yml)
    assert len(story_crons) == 2, f"Expected 2 cron triggers in daily-story.yml, got {story_crons}"

    # 2 Carousels daily
    post_crons = re.findall(r"-\s*cron:\s*['\"]([^'\"]+)['\"]", post_yml)
    assert len(post_crons) == 2, f"Expected 2 cron triggers in daily-post.yml, got {post_crons}"

    # daily-video.yml schedule parked
    assert "# schedule:" in video_yml or "Parked" in video_yml
