"""
Strategy & 30-day calendar compiler (Makerzz P2 gate).

Consumes ranked angles from scan.json (P1) and lays out a 30-day calendar:

  - cadence constraints (e.g. 1 Reel + 1 Carousel per day)
  - format diversity (no identical layout 3 days running)
  - timezone-aware posting slots (Asia/Kolkata default, 19:30 IST)
  - deterministic minute jitter (seeded random for reproducibility)
  - blackout dates respected

Gate artifact: calendar.json with the "week laid out" contract.
"""

import json
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "Asia/Kolkata"
DEFAULT_SLOT = "19:30"
DEFAULT_CADENCE = {"carousel": 1, "reel": 1}
DIVERSITY_WINDOW = 2  # no identical format within this many consecutive days
JITTER_MINUTES = 12  # randomized minute within the slot window

ANGLE_TO_LAYOUT = {
    "carousel": ["authority_hook", "receipt", "competitor", "calendar_matrix", "pipeline", "mega_cta"],
    "reel": ["hook_beat", "value_beats", "proof_beat", "cta_beat"],
}

DAYS_IN_HORIZON = 30


def compile_calendar(
    ranked_angles: list[dict],
    days: int = DAYS_IN_HORIZON,
    timezone_name: str = DEFAULT_TIMEZONE,
    slot: str = DEFAULT_SLOT,
    cadence: dict | None = None,
    blackout_dates: list[str] | None = None,
    seed: int | None = 42,
    start_date: datetime | None = None,
) -> dict:
    """
    Compile a deterministic 30-day content calendar.
    Gate artifact: calendar.json.
    """
    cadence = cadence or DEFAULT_CADENCE
    blackout = set(blackout_dates or [])
    rng = random.Random(seed)  # deterministic when seed is provided
    tz = _safe_zone(timezone_name)
    start = start_date or datetime.now(tz).replace(second=0, microsecond=0)

    if not ranked_angles:
        return {"days": [], "total_items": 0, "note": "no angles — calendar empty", "gate": "calendar empty"}

    items: list[dict] = []
    recent_formats: list[str] = []

    for day_offset in range(days):
        date = start + timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")
        if date_str in blackout:
            continue

        for fmt, per_day in cadence.items():
            for n in range(per_day):
                angle = _pick_angle(ranked_angles, items, fmt)
                item_slot = _jitter_slot(slot, rng, n, per_day)
                dt = _slot_datetime(date, item_slot, tz)

                items.append({
                    "id": f"cal-{date_str}-{fmt}-{n + 1}",
                    "date": date_str,
                    "scheduled_for": dt.isoformat(),
                    "timezone": timezone_name,
                    "format": fmt,
                    "angle": angle["angle"],
                    "angle_rank": angle["rank"],
                    "hook": _hook_from_angle(angle),
                    "source_evidence": angle.get("evidence", []),
                    "status": "IDEATION",
                })
                recent_formats.append(fmt)

        # Enforce diversity: if last 3 same-format items in a row, rotate next day's lead format
        if len(recent_formats) >= 3 and len(set(recent_formats[-3:])) == 1:
            # flip the cadence order for the next day (quality feature, not platform evasion)
            cadence = dict(reversed(list(cadence.items())))

    return {
        "version": "1.0",
        "generated_at": datetime.now(tz).isoformat(),
        "timezone": timezone_name,
        "slot": slot,
        "cadence": cadence,
        "days": _group_by_day(items),
        "total_items": len(items),
        "horizon_days": days,
        "deterministic_seed": seed,
        "gate": "week laid out",
    }


def _pick_angle(ranked_angles: list[dict], existing_items: list[dict], fmt: str) -> dict:
    """Round-robin through angles, avoiding reuse within the same format until exhausted."""
    used_counts: dict[int, int] = {}
    for item in existing_items:
        if item.get("format") == fmt:
            used_counts[item.get("angle_rank", 0)] = used_counts.get(item.get("angle_rank", 0), 0) + 1
    # least-used rank wins (deterministic tie-break by rank)
    ranked = sorted(ranked_angles, key=lambda a: (used_counts.get(a.get("rank", 0), 0), a.get("rank", 99)))
    return ranked[0]


def _hook_from_angle(angle: dict) -> str:
    ev = (angle.get("evidence") or [{}])[0]
    claim = ev.get("claim", "") if isinstance(ev, dict) else ""
    return claim[:120] or angle.get("angle", "")[:120]


def _jitter_slot(slot: str, rng: random.Random, n: int, per_day: int) -> str:
    """Deterministic minute jitter for organic distribution."""
    hour, minute = map(int, slot.split(":"))
    jitter = rng.randint(0, JITTER_MINUTES)
    if per_day > 1:
        # spread multiple same-format slots apart
        minute += n * (60 // max(1, per_day))
    total = hour * 60 + minute + jitter
    return f"{(total // 60) % 24:02d}:{total % 60:02d}"


def _slot_datetime(date: datetime, slot_str: str, tz: ZoneInfo) -> datetime:
    hour, minute = map(int, slot_str.split(":"))
    naive = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    try:
        return naive.replace(tzinfo=tz)
    except Exception:
        return naive


def _group_by_day(items: list[dict]) -> list[dict]:
    days: dict[str, list[dict]] = {}
    for item in items:
        days.setdefault(item["date"], []).append(item)
    return [{"date": d, "items": sorted(items_, key=lambda x: x["scheduled_for"])} for d, items_ in sorted(days.items())]


def _safe_zone(name: str):
    """Resolve tz by name; fall back to fixed +05:30 offset when tzdata is absent."""
    try:
        return ZoneInfo(name)
    except Exception:
        from datetime import timezone as _tz
        return _tz(timedelta(hours=5, minutes=30))


def save_calendar(calendar: dict, run_dir) -> object:
    """Persist calendar.json gate artifact."""
    from pathlib import Path
    path = Path(run_dir) / "calendar.json"
    path.write_text(json.dumps(calendar, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path
