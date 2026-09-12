"""Tests for pipeline guard wiring: quota skip, failure alerts, dispatch helper."""

from unittest.mock import patch

import pytest

import orchestrator
from orchestrator import _run_guarded, run_story_pipeline
from src.instagram.publisher import publisher
from src.ops.guardian import SlotSkipped


@pytest.fixture(autouse=True)
def no_janitor_side_effects():
    with patch("orchestrator.janitor", return_value={"output_dirs_removed": 0, "mp4_removed": 0}):
        yield


def test_story_quota_skip_returns_manifest():
    """Exhausted quota -> skipped manifest, no work attempted, no exception."""
    with patch.object(publisher, "check_publishing_limit", return_value={"quota_usage": 25}):
        res = run_story_pipeline(dry_run=True, custom_topic="skip me")
    assert res["status"] == "skipped"
    assert res["format"] == "story"
    assert "reason" in res


def test_story_proceeds_with_headroom():
    """Healthy quota -> pipeline proceeds past the precheck (then dry-runs)."""
    with patch.object(publisher, "check_publishing_limit", return_value={"quota_usage": 3}):
        res = run_story_pipeline(dry_run=True, custom_topic="Quota Headroom Topic")
    assert res.get("status") != "skipped"
    assert res.get("format") == "story"


def test_run_guarded_alerts_and_reraises():
    """Dispatch helper sends one alert on failure and re-raises."""
    with patch("orchestrator.send_alert", return_value=False) as alert:
        with pytest.raises(ValueError, match="boom"):
            _run_guarded("story", True, lambda: (_ for _ in ()).throw(ValueError("boom")))
    alert.assert_called_once()
    assert "story" in alert.call_args[0][0]


def test_run_guarded_passthrough_no_alert():
    """Dispatch helper returns values untouched and stays silent on success."""
    with patch("orchestrator.send_alert") as alert:
        assert _run_guarded("reel", False, lambda: {"ok": True}) == {"ok": True}
    alert.assert_not_called()


def test_run_guarded_slot_skipped_stays_silent():
    """SlotSkipped propagates without firing a failure alert."""
    def _skip():
        raise SlotSkipped("quota exceeded")

    with patch("orchestrator.send_alert") as alert:
        with pytest.raises(SlotSkipped):
            _run_guarded("video", False, _skip)
    alert.assert_not_called()
