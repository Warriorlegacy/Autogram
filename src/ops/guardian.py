"""Operational guards: retries, quota, alerts, and storage janitor."""

import datetime
import os
import shutil
import time
from pathlib import Path

import requests


class SlotSkipped(Exception):
    """Raised when a slot should skip cleanly (e.g. quota)."""


def with_retries(fn, attempts=3, delays=(30, 120), sleeper=None):
    """Call fn with retries on any exception.

    Args:
        fn: Zero-argument callable to invoke.
        attempts: Total number of tries (including the first).
        delays: Sleep durations between tries; last value repeats.
        sleeper: Sleep callable; defaults to time.sleep.

    Returns:
        Whatever fn() returns on success.

    Raises:
        Exception: The last error after exhausting all attempts.
    """
    if sleeper is None:
        sleeper = time.sleep
    last_exc = None
    for attempt in range(max(1, attempts)):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - retry on ANY exception
            last_exc = exc
            if attempt >= attempts - 1:
                break
            if delays:
                delay = delays[min(attempt, len(delays) - 1)]
            else:
                delay = 0
            sleeper(delay)
    raise last_exc


def ensure_quota(check_fn, need=1, limit=25):
    """Check quota usage and raise SlotSkipped when over limit.

    Args:
        check_fn: Zero-argument callable returning a dict with int 'quota_usage'.
        need: Units this slot needs.
        limit: Max allowed usage.

    Returns:
        Current usage as int when usage + need <= limit.

    Raises:
        SlotSkipped: If usage + need > limit.
    """
    usage = int(check_fn()["quota_usage"])
    if usage + need > limit:
        raise SlotSkipped(f"quota exceeded: usage={usage} need={need} limit={limit}")
    return usage


def send_alert(message):
    """Send an alert via Telegram or fall back to a local log file.

    Args:
        message: Alert text to send.

    Returns:
        True if Telegram accepted the message, else False. Returns False
        (and appends to output/ALERTS.log) when Telegram env is missing.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": message},
                timeout=10,
            )
            if resp.status_code != 200:
                return False
            try:
                return bool(resp.json().get("ok", True))
            except Exception:  # noqa: BLE001 - non-JSON 200 still counts as ok
                return True
        except Exception:  # noqa: BLE001 - swallow all transport errors
            return False
    log_path = Path.cwd() / "output" / "ALERTS.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp} {message}\n")
    return False


def janitor(output_base, mpt_storage=None, output_days=14, mpt_hours=48):
    """Delete stale output date-dirs and stale mp4 files.

    Args:
        output_base: Directory holding YYYY-MM-DD subdirectories.
        mpt_storage: Directory tree to scan for stale *.mp4 files.
        output_days: Max age (by mtime, in days) for output subdirs.
        mpt_hours: Max age (by mtime, in hours) for mp4 files.

    Returns:
        Dict with counts: {'output_dirs_removed': int, 'mp4_removed': int}.
        Never raises; per-item errors are ignored.
    """
    removed_dirs = 0
    removed_mp4 = 0
    now = time.time()
    try:
        base = Path(output_base)
        if base.is_dir():
            cutoff = now - output_days * 86400
            for entry in base.iterdir():
                try:
                    if entry.is_dir() and entry.stat().st_mtime < cutoff:
                        shutil.rmtree(entry, ignore_errors=False)
                        removed_dirs += 1
                except Exception:  # noqa: BLE001 - never raise from janitor
                    continue
    except Exception:  # noqa: BLE001 - never raise from janitor
        pass
    if mpt_storage is not None:
        try:
            root = Path(mpt_storage)
            if root.exists():
                cutoff = now - mpt_hours * 3600
                for path in root.rglob("*"):
                    try:
                        if path.is_file() and path.suffix.lower() == ".mp4":
                            if path.stat().st_mtime < cutoff:
                                path.unlink()
                                removed_mp4 += 1
                    except Exception:  # noqa: BLE001 - never raise from janitor
                        continue
        except Exception:  # noqa: BLE001 - never raise from janitor
            pass
    return {"output_dirs_removed": removed_dirs, "mp4_removed": removed_mp4}
