import os
from pathlib import Path
import pytest

from src.config import Settings
from src.content.providers_manager import DEFAULT_PROVIDERS
from src.content.generator import ContentGenerator, settings as gen_settings


def test_workflow_files_exist():
    """Verify daily-story.yml and daily-video.yml exist in .github/workflows."""
    base_dir = Path(__file__).parent.parent
    story_wf = base_dir / ".github" / "workflows" / "daily-story.yml"
    video_wf = base_dir / ".github" / "workflows" / "daily-video.yml"
    post_wf = base_dir / ".github" / "workflows" / "daily-post.yml"

    assert story_wf.exists(), "daily-story.yml must exist"
    assert video_wf.exists(), "daily-video.yml must exist"
    assert post_wf.exists(), "daily-post.yml must exist"


def test_workflow_contents():
    """Verify workflows contain required triggers, steps, and failover logic."""
    base_dir = Path(__file__).parent.parent
    story_content = (base_dir / ".github" / "workflows" / "daily-story.yml").read_text(encoding="utf-8")
    video_content = (base_dir / ".github" / "workflows" / "daily-video.yml").read_text(encoding="utf-8")

    # Story workflow checks
    assert "cron:" in story_content
    assert "--story" in story_content
    assert "publish-story" in story_content
    assert "daily-story-artifacts" in story_content
    assert "GITHUB_COPILOT_TOKEN" in story_content

    # Video workflow checks (manual-dispatch only by design: MPT is localhost-only,
    # the 10 daily video slots run via local Windows Scheduled Tasks)
    assert "workflow_dispatch" in video_content
    assert "--video" in video_content or "--reel" in video_content
    assert "publish-video" in video_content
    assert "daily-video-artifacts" in video_content
    assert "GITHUB_COPILOT_TOKEN" in video_content


def test_github_copilot_token_in_settings():
    """Verify Settings supports GITHUB_COPILOT_TOKEN alias."""
    s = Settings()
    assert hasattr(s, "github_copilot_token")


def test_github_models_preset_in_providers():
    """Verify providers manager contains github_models preset."""
    presets = DEFAULT_PROVIDERS.get("presets", {})
    assert "github_models" in presets
    gm = presets["github_models"]
    assert "models.inference.ai.azure.com" in gm["base_url"]
    assert gm["default_model"] == "gpt-4o"
    assert "gpt-4o" in gm["models"]


def test_github_models_missing_token_raises(monkeypatch):
    """Verify generate_with_github_models raises ValueError when no token is present."""
    monkeypatch.delenv("GITHUB_COPILOT_TOKEN", raising=False)
    monkeypatch.delenv("GH_COPILOT_TOKEN", raising=False)
    monkeypatch.delenv("COPILOT_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(gen_settings, "github_copilot_token", None)
    gen = ContentGenerator()
    with pytest.raises(ValueError, match="No GITHUB_COPILOT_TOKEN or GITHUB_TOKEN configured"):
        gen.generate_with_github_models(
            {"topic": "Test Topic", "pillar": "AI Tool Breakdown"},
            []
        )

