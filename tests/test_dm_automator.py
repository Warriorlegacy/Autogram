import pytest
from unittest.mock import patch, MagicMock
from src.instagram.dm_automator import InstagramDMAutomator, TRIGGERS
from src.db.database import db

@pytest.fixture
def automator(tmp_path):
    dm = InstagramDMAutomator()
    dm.dry_run = True
    dm.state_file = tmp_path / "test_dm_state.json"
    dm._init_state()
    return dm

def test_keyword_matching(automator):
    # FOSS triggers
    assert automator.match_keyword("FOSS please!") == "FOSS"
    assert automator.match_keyword("Can you send the docker setup?") == "FOSS"
    assert automator.match_keyword("Send blueprint") == "FOSS"
    assert automator.match_keyword("I want to self-host this") == "FOSS"

    # PROMPT triggers
    assert automator.match_keyword("Send the PROMPT code") == "PROMPT"
    assert automator.match_keyword("What is the secret prompt?") == "PROMPT"
    assert automator.match_keyword("megaprompt please") == "PROMPT"
    assert automator.match_keyword("chatgpt code link") == "PROMPT"

    # Non-triggers
    assert automator.match_keyword("Looks great!") is None
    assert automator.match_keyword("Nice post brother") is None
    assert automator.match_keyword("First comment") is None

def test_process_comment_foss(automator):
    comment = {
        "id": "comment_foss_101",
        "text": "FOSS blueprint please!",
        "username": "coder_dev"
    }
    result = automator.process_comment(comment, media_id="media_123")
    assert result is not None
    assert result["comment_id"] == "comment_foss_101"
    assert result["keyword"] == "FOSS"
    assert result["dm_status"] == "DM_SENT"

    # Check deduplication
    processed = automator.load_processed_comments()
    assert "comment_foss_101" in processed

def test_process_comment_prompt(automator):
    comment = {
        "id": "comment_prompt_202",
        "text": "Send me the PROMPT code",
        "username": "ai_researcher"
    }
    result = automator.process_comment(comment, media_id="media_123")
    assert result is not None
    assert result["comment_id"] == "comment_prompt_202"
    assert result["keyword"] == "PROMPT"
    assert result["dm_status"] == "DM_SENT"

def test_deduplication_skips_processed(automator):
    comment = {
        "id": "comment_repeat_303",
        "text": "FOSS",
        "username": "repeat_user"
    }
    # First time: processes
    res1 = automator.process_comment(comment, media_id="media_123")
    assert res1 is not None

    # Scan should skip already handled comment ID
    processed = automator.load_processed_comments()
    assert "comment_repeat_303" in processed

def test_get_stats(automator):
    # Record two actions
    automator.record_processed_comment(
        comment_id="c_stat_1",
        media_id="m_1",
        username="dev_1",
        comment_text="foss link",
        keyword="FOSS",
        public_reply_id="r_1",
        dm_status="DM_SENT"
    )
    automator.record_processed_comment(
        comment_id="c_stat_2",
        media_id="m_1",
        username="dev_2",
        comment_text="prompt code",
        keyword="PROMPT",
        public_reply_id="r_2",
        dm_status="DM_SENT"
    )

    stats = automator.get_stats()
    assert stats["total_dms_sent"] >= 2
    assert stats["total_comments_handled"] >= 2
    assert stats["by_keyword"]["FOSS"] >= 1
    assert stats["by_keyword"]["PROMPT"] >= 1
    assert len(stats["recent_actions"]) >= 2

def test_scan_and_automate_dry_run(automator):
    summary = automator.scan_and_automate(limit_posts=1)
    assert summary["media_scanned"] == 1
    assert summary["comments_checked"] >= 1
    assert summary["actions_executed"] >= 1
    assert len(summary["details"]) >= 1
