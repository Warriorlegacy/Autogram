"""Tests for src.ops.guardian."""

import os
import time
from pathlib import Path

import pytest

from src.ops.guardian import SlotSkipped, ensure_quota, janitor, send_alert, with_retries


def test_with_retries_succeeds_after_two_failures():
    """Failing twice then succeeding returns value with delays [30, 120]."""
    calls = []
    sleeps = []

    def fn():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("boom")
        return "ok"

    result = with_retries(fn, attempts=3, delays=(30, 120), sleeper=sleeps.append)
    assert result == "ok"
    assert sleeps == [30, 120]


def test_with_retries_reraises_after_exhaustion():
    """Three failures re-raise and sleep twice."""
    sleeps = []

    def fn():
        raise ValueError("nope")

    with pytest.raises(ValueError, match="nope"):
        with_retries(fn, attempts=3, delays=(30, 120), sleeper=sleeps.append)
    assert sleeps == [30, 120]


def test_ensure_quota_skips_and_returns():
    """Usage 25/need 1 skips; usage 10 returns 10."""
    with pytest.raises(SlotSkipped):
        ensure_quota(lambda: {"quota_usage": 25}, need=1, limit=25)
    assert ensure_quota(lambda: {"quota_usage": 10}, need=1, limit=25) == 10


def test_send_alert_falls_back_to_log(tmp_path, monkeypatch):
    """Without token env, alert appends to output/ALERTS.log under cwd."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    assert send_alert("hello-alert") is False
    log = tmp_path / "output" / "ALERTS.log"
    assert log.is_file()
    assert "hello-alert" in log.read_text(encoding="utf-8")


def test_janitor_removes_old_keeps_fresh(tmp_path):
    """Old date-dirs and mp4s are removed; fresh ones kept."""
    output_base = tmp_path / "output"
    output_base.mkdir()
    old_dir = output_base / "2020-01-01"
    fresh_dir = output_base / "2099-01-01"
    old_dir.mkdir()
    fresh_dir.mkdir()
    (old_dir / "x.txt").write_text("old", encoding="utf-8")
    (fresh_dir / "x.txt").write_text("fresh", encoding="utf-8")

    mpt = tmp_path / "mpt"
    mpt.mkdir()
    old_mp4 = mpt / "old.mp4"
    fresh_mp4 = mpt / "fresh.mp4"
    old_mp4.write_bytes(b"0")
    fresh_mp4.write_bytes(b"1")

    old_mtime = time.time() - (15 * 86400)
    old_mp4_mtime = time.time() - (49 * 3600)
    os.utime(old_dir, (old_mtime, old_mtime))
    os.utime(old_mp4, (old_mp4_mtime, old_mp4_mtime))

    result = janitor(output_base, mpt_storage=mpt, output_days=14, mpt_hours=48)
    assert result == {"output_dirs_removed": 1, "mp4_removed": 1}
    assert not Path(old_dir).exists()
    assert Path(fresh_dir).is_dir()
    assert not Path(old_mp4).exists()
    assert Path(fresh_mp4).is_file()
