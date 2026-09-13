"""Spec smoke tests: kinetic ASS helpers + facade wiring (no network, no GPU)."""

from scripts.pipeline_reels import _events_for_words, to_ass_time


def test_to_ass_time_format():
    assert to_ass_time(0) == "0:00:00.00"
    assert to_ass_time(61.5) == "0:01:01.50"
    assert to_ass_time(3661.25) == "1:01:01.25"


def test_karaoke_events_highlight_each_word_once():
    words = [("hello", 0.0, 0.4), ("world", 0.4, 0.8), ("again", 0.8, 1.2)]
    events = _events_for_words(words, chunk_size=3)
    assert len(events) == 3  # one event per active word
    for i, ev in enumerate(events):
        assert ev.count("\\c&H0000FFFF") == 1  # exactly one yellow word
        assert ev.startswith("Dialogue: 0,")
        assert ",Kinetic," in ev
    assert "HELLO" in events[0] and "WORLD" in events[0]


def test_publish_facade_rejects_local_paths():
    import pytest

    from scripts.publish_instagram import publish_reel_to_instagram

    with pytest.raises(ValueError, match="public HTTPS"):
        publish_reel_to_instagram("workspace/final_reel.mp4", "cap")
