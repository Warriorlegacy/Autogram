"""Tests for the follower-gated BLUEPRINT delivery flow, studio positioning
strings, viral fonts, and the committed blueprint assets."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.instagram import dm_automator as dma_mod
from src.instagram.dm_automator import InstagramDMAutomator, TRIGGERS


@pytest.fixture
def automator(tmp_path, monkeypatch):
    """Live-mode automator with gate store + persistence isolated to tmp."""
    monkeypatch.setattr(dma_mod, "FOLLOW_GATE_FILE", tmp_path / "gate.json")
    auto = InstagramDMAutomator()
    auto.dry_run = False
    auto._forced_dry_run = False
    monkeypatch.setattr(auto, "record_processed_comment", lambda **kw: None)
    return auto


def test_blueprint_keyword_matching():
    auto = InstagramDMAutomator()
    assert auto.match_keyword("send me the blueprint please") == "BLUEPRINT"
    assert auto.match_keyword("show me your portfolio studio") == "BLUEPRINT"
    assert auto.match_keyword("docker setup help") == "FOSS"
    assert auto.match_keyword("send the prompt code") == "PROMPT"
    assert auto.match_keyword("nice post, love it") is None


def test_gate_first_touch_withholds_link(automator):
    """First BLUEPRINT comment -> gate ask, PENDING, and NO DM is attempted."""
    with patch.object(automator, "send_public_reply", return_value="r_gate") as pub, \
         patch.object(automator, "send_private_dm",
                      side_effect=AssertionError("DM must not send before follow claim")):
        res = automator.process_comment(
            {"id": "c_gate_1", "text": "Send me the blueprint!", "username": "GateUser1"},
            media_id="m1",
        )
    assert res["dm_status"] == "GATE_PENDING"
    assert res["public_reply_id"] == "r_gate"
    sent_reply = pub.call_args[0][1]
    assert "Follow" in sent_reply and "FOLLOWED" in sent_reply
    assert "raw.githubusercontent" not in sent_reply  # link withheld
    assert automator.is_gate_pending("GateUser1") is True


def test_gate_claim_delivers_blueprint(automator):
    """Follow-up claim comment -> blueprint DM delivered, pending cleared."""
    automator.mark_gate_pending("GateUser2")
    captured = {}

    def fake_dm(comment_id, text):
        captured["text"] = text
        return True

    with patch.object(automator, "send_public_reply", return_value="r2"), \
         patch.object(automator, "send_private_dm", side_effect=fake_dm):
        res = automator.process_comment(
            {"id": "c_gate_2", "text": "FOLLOWED ✅", "username": "GateUser2"},
            media_id="m1",
        )
    assert res["dm_status"] == "DM_SENT"
    assert "BLUEPRINT.md" in captured["text"] or "BLUEPRINT.pdf" in captured["text"]
    assert "AI ENGINEERING STUDIO" in captured["text"]
    assert automator.is_gate_pending("GateUser2") is False


def test_foss_flow_ungated_regression(automator):
    """Existing FOSS flow still DMs immediately (no gate)."""
    with patch.object(automator, "send_public_reply", return_value="r3"), \
         patch.object(automator, "send_private_dm", return_value=True):
        res = automator.process_comment(
            {"id": "c_foss_9", "text": "FOSS please!", "username": "BuilderZ"},
            media_id="m1",
        )
    assert res["dm_status"] == "DM_SENT"
    assert res["keyword"] == "FOSS"


def test_studio_positioning_strings():
    """Reel footer + story CTA position the FULL AI ENGINEERING STUDIO."""
    from src.content.generator import generator

    with patch.object(generator, "_free_narration", return_value={}):
        script = generator.generate_reel_script("X", "Marketing Psychology")
    assert "FULL AI ENGINEERING STUDIO" in script["caption"]
    assert "signhify.studio" in script["caption"]

    story = generator.generate_story_content("Y", "AI Tool Breakdown")
    assert "FULL AI ENGINEERING STUDIO" in story["cta_text"]
    assert "@signhify.studio" in story["cta_text"]


def test_mpt_payload_uses_anton_font():
    """MPT render jobs request the viral Anton subtitle face."""
    from src.content.mpt_client import MoneyPrinterTurboClient

    captured = {}

    class _Resp:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"data": {"task_id": "t_font_1"}}

    def fake_post(url, json=None, **kw):
        captured.update(json or {})
        return _Resp()

    client = MoneyPrinterTurboClient()
    with patch("src.content.mpt_client.requests.post", side_effect=fake_post):
        assert client.create_video("say this", "Subject") == "t_font_1"
    assert captured.get("font_name") == "Anton-Regular.ttf"
    assert captured.get("video_aspect") == "9:16"


def test_blueprint_assets_committed():
    """BLUEPRINT.md + BLUEPRINT.pdf exist and market the studio."""
    root = Path(__file__).parent.parent
    md = (root / "BLUEPRINT.md").read_text(encoding="utf-8")
    assert "FULL AI ENGINEERING STUDIO" in md
    assert "signhify.studio" in md
    for section in ("PORTFOLIO", "WEBSITES", "PROMPT PACK", "HIRE THE STUDIO"):
        assert section in md
    pdf = root / "BLUEPRINT.pdf"
    assert pdf.exists() and pdf.stat().st_size > 2048
