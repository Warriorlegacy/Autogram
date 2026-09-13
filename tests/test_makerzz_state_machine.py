"""
Tests for the Makerzz P0–P8 state machine, gate transitions, script verifier,
edit plan compiler, niche scanner, calendar compiler, and resumability.

Additive to the existing suite: these tests never touch legacy pipeline modules.
"""

import json
import pytest
from pathlib import Path

from src.engine.state_machine import (
    Phase,
    StageStatus,
    StagePolicy,
    ApprovalMode,
    GateViolation,
    estimate_stage_cost,
    STAGE_ORDER,
)
from src.engine.run_manager import RunManager
from src.engine.idempotency import (
    make_idempotency_key,
    register_job,
    resolve_existing,
    mark_job,
    TERMINAL_STATUSES,
)
from src.content.script_verifier import verify_script, build_retry_feedback
from src.content.edit_plan_compiler import compile_edit_plan
from src.research.niche_scanner import scan_niche, compute_engagement_velocity
from src.research.calendar_compiler import compile_calendar


VALID_BRIEF = {
    "brand": "Signhify Studio",
    "creator": "Piyush Raj Singh",
    "niche": "self-hosted AI tools for solo founders",
    "audience": "indie hackers shipping in public",
    "voice": "direct, technical, calm",
    "handle": "@signhify.studio",
}


@pytest.fixture
def run(tmp_path) -> RunManager:
    """A fresh run created in a temp workspace (P0 already gated by brief.json)."""
    rm = RunManager.create(brief=dict(VALID_BRIEF), run_dir=tmp_path / "run_test")
    return rm


# ─── State machine basics ────────────────────────────────────────────────────


def test_phase_enum_is_canonical():
    assert [p.value for p in STAGE_ORDER] == [
        "P0_SETUP", "P1_SCAN", "P2_STRATEGY", "P3_SCRIPT", "P4_VIDEO",
        "P5_EDIT_PLAN", "P6_CAROUSEL", "P7_PUBLISH", "P8_REPORT",
    ]


def test_default_policy_is_approve_everywhere():
    policy = StagePolicy()
    for phase in Phase:
        if phase in (Phase.P0_SETUP, Phase.P8_REPORT):
            continue
        assert policy.mode_for(phase) == ApprovalMode.APPROVE


def test_autonomous_policy_never_auto_publishes():
    policy = StagePolicy.autonomous()
    assert policy.publish == ApprovalMode.APPROVE
    assert policy.scan == ApprovalMode.AUTO


def test_stage_cost_estimates_match_pricing_table():
    assert estimate_stage_cost(Phase.P1_SCAN) == 40
    assert estimate_stage_cost(Phase.P3_SCRIPT) == 12
    assert estimate_stage_cost(Phase.P5_EDIT_PLAN) == 20
    assert estimate_stage_cost(Phase.P6_CAROUSEL, slides=8) == 30 + 8 * 3
    assert estimate_stage_cost(Phase.P7_PUBLISH) == 0


# ─── P0 brief gate & P1 gate enforcement ─────────────────────────────────────


def test_p1_cannot_execute_without_completed_p0(tmp_path):
    rm = RunManager.create(brief=dict(VALID_BRIEF), run_dir=tmp_path / "run_gate")
    # Simulate P0 NOT completed
    state = rm.read_state()
    state["stages"]["P0_SETUP"]["status"] = "PENDING"
    rm.write_state(state)

    with pytest.raises(GateViolation):
        rm.assert_gate(Phase.P1_SCAN)


def test_p1_gate_passes_after_p0_completed(run):
    rm = run
    rm.mark_completed(Phase.P0_SETUP)
    rm.assert_gate(Phase.P1_SCAN)  # must not raise


def test_p2_blocked_without_scan_artifact(run):
    rm = run
    rm.mark_completed(Phase.P0_SETUP)
    rm.mark_completed(Phase.P1_SCAN)
    with pytest.raises(GateViolation):
        rm.assert_gate(Phase.P2_STRATEGY)


def test_p3_blocked_without_upstream_gate_artifacts(run):
    """P3 may not run until P1 (scan.json) and P2 (calendar.json) gates exist."""
    rm = run
    for phase in STAGE_ORDER[:3]:
        rm.mark_completed(phase)
    with pytest.raises(GateViolation):
        rm.assert_gate(Phase.P3_SCRIPT)  # upstream scan.json/calendar.json missing

    # Writing upstream gate artifacts unlocks P3
    rm.write_artifact("scan.json", {"ranked_angles": []})
    rm.write_artifact("calendar.json", {"days": []})
    rm.assert_gate(Phase.P3_SCRIPT)


def test_p8_report_requires_publish_queue(run):
    """P8 may not file a report until P7's queue.json gate artifact exists."""
    rm = run
    for phase in STAGE_ORDER[:8]:
        rm.mark_completed(phase)
    # Write all upstream gate artifacts EXCEPT queue.json
    rm.write_artifact("scan.json", {"ranked_angles": []})
    rm.write_artifact("calendar.json", {"days": []})
    rm.write_artifact("script.txt", "clean spoken text.")
    rm.write_artifact("script_verification.json", {"passed": True})
    rm.write_artifact("edit_plan.json", {"beats": []})
    rm.write_artifact("carousel_plan.json", {"slides": []})
    rm.write_artifact("approved_prompts.json", {"approved": True})
    with pytest.raises(GateViolation):
        rm.assert_gate(Phase.P8_REPORT)
    rm.write_artifact("queue.json", {"queue": []})
    rm.assert_gate(Phase.P8_REPORT)


# ─── Script verifier (strict, fail-closed) ───────────────────────────────────


def test_script_verifier_rejects_bracket_tags():
    result = verify_script("[HOOK] This is the hook. [CTA] Follow now.")
    assert result.passed is False
    assert any("[HOOK]" in v for v in result.violations)
    assert any("[CTA]" in v for v in result.violations)


def test_script_verifier_rejects_markdown_and_stage_directions():
    result = verify_script("**bold start** and (pause) then ## Header\n- bullet one")
    assert result.passed is False
    assert any("bold" in v for v in result.violations)
    assert any("(pause)" in v for v in result.violations)


def test_script_verifier_rejects_timecodes_and_labels():
    result = verify_script("00:14 the beat starts\nBeat 1:\nCTA:")
    assert result.passed is False
    assert any("00:14" in v for v in result.violations)
    assert any("Beat" in v or "CTA" in v for v in result.violations)


def test_script_verifier_rejects_emoji():
    result = verify_script("This is huge 🚀 ship it now.")
    assert result.passed is False
    assert any("Emoji" in v or "🚀" in v for v in result.violations)


def test_script_verifier_accepts_clean_spoken_text():
    clean = (
        "Here is the truth about shipping autonomous systems. "
        "Most builders quit in week two because the feedback loop feels silent. "
        "The mechanism is compounding distribution, not viral luck. "
        "Ship one artifact daily for thirty days and the data will prove it. "
        "Save this and start tonight."
    )
    result = verify_script(clean)
    assert result.passed is True, result.violations
    assert result.cadence_ok is True


def test_retry_feedback_mentions_rules():
    feedback = build_retry_feedback(["Bracket section tag found: '[HOOK]'"])
    assert "[HOOK]" in feedback
    assert "PURE spoken text" in feedback


# ─── Edit plan compiler ──────────────────────────────────────────────────────


def test_edit_plan_separates_from_script():
    script = (
        "Stop posting randomly and start shipping systems. "
        "The problem is nobody sees your work when you post once a week. "
        "The mechanism is a durable queue that publishes for you daily. "
        "The proof is the 30 day archive this engine produced. "
        "The payoff is omnipresence without burnout. "
        "Comment SYSTEM to get the full playbook."
    )
    plan = compile_edit_plan(script, estimated_seconds=24.0)
    assert plan["total_beats"] == 6
    assert plan["total_duration_sec"] == 24.0
    assert all("framing" in b for b in plan["beats"])
    assert all("sfx" in b for b in plan["beats"])
    # Non-spoken instructions live here, NOT spoken text
    assert all("purpose" in b for b in plan["beats"])


# ─── Niche scanner ───────────────────────────────────────────────────────────


def test_engagement_velocity_formula():
    # (100 likes + 10 comments*2 + 5 shares*4) / 1000 views = 0.14
    assert compute_engagement_velocity(likes=100, comments=10, shares=5, views=1000) == 0.14


def test_engagement_velocity_unavailable_when_no_views():
    assert compute_engagement_velocity(likes=100, views=0) is None


def test_scan_produces_eight_ranked_angles():
    profile = {
        "handle": "testcreator",
        "followers": 12000,
        "posts": [
            {"caption": f"Hook number {i}: ship systems daily", "format": "reel",
             "likes": 500 - i * 10, "comments": 40, "shares": 20, "views": 8000,
             "url": f"https://example.com/p/{i}"}
            for i in range(10)
        ],
    }
    scan = scan_niche(profile, competitors_raw=[], niche="autonomous posting systems")
    assert len(scan["ranked_angles"]) == 8
    ranks = [a["rank"] for a in scan["ranked_angles"]]
    assert ranks == list(range(1, 9))
    # Ranking descending by score
    scores = [a["score"] for a in scan["ranked_angles"]]
    assert scores == sorted(scores, reverse=True)
    # Every angle has evidence with provenance
    for angle in scan["ranked_angles"]:
        assert angle["evidence"], "every angle must carry evidence"


def test_scan_never_fabricates_missing_metrics():
    profile = {
        "handle": "nocounts",
        "posts": [
            {"caption": "post without metrics", "format": "image",
             "likes": None, "comments": None, "shares": None, "views": None},
        ],
    }
    scan = scan_niche(profile, niche="testing niche")
    assert scan["profile"]["availability"]["followers"] == "unavailable"
    assert scan["profile"]["posts"][0]["availability"] == "unavailable"


# ─── Calendar compiler ───────────────────────────────────────────────────────


def test_calendar_deterministic_with_seed():
    angles = [{"rank": i, "angle": f"Angle {i}", "score": 90 - i,
               "evidence": [{"claim": f"claim {i}"}]} for i in range(1, 9)]
    cal1 = compile_calendar(angles, days=7, seed=42)
    cal2 = compile_calendar(angles, days=7, seed=42)
    assert cal1["total_items"] == cal2["total_items"]
    assert [d["items"] for d in cal1["days"]] == [d["items"] for d in cal2["days"]]


def test_calendar_respects_cadence():
    angles = [{"rank": i, "angle": f"Angle {i}", "score": 90, "evidence": []} for i in range(1, 9)]
    cal = compile_calendar(angles, days=7, cadence={"carousel": 1, "reel": 1}, seed=7)
    # 7 days x 2 formats = 14 items
    assert cal["total_items"] == 14
    formats = [i["format"] for d in cal["days"] for i in d["items"]]
    assert formats.count("carousel") == 7
    assert formats.count("reel") == 7


def test_calendar_respects_blackout_dates():
    from datetime import datetime, timedelta, timezone
    angles = [{"rank": 1, "angle": "A", "score": 90, "evidence": []}]
    start = datetime(2026, 9, 13, tzinfo=timezone.utc)
    blackout = ["2026-09-14"]
    cal = compile_calendar(angles, days=3, blackout_dates=blackout, seed=1, start_date=start)
    dates = [d["date"] for d in cal["days"]]
    assert "2026-09-14" not in dates


# ─── Idempotency ─────────────────────────────────────────────────────────────


def test_idempotency_key_format():
    key = make_idempotency_key("brand", "run", "P4_VIDEO", "asset", "render")
    assert key == "brand:run:P4_VIDEO:asset:render"


def test_provider_job_double_registration_returns_same(tmp_path):
    import src.engine.idempotency as idem
    idem._DB_PATH = tmp_path / "jobs.db"
    if hasattr(idem._ensure_init, "_done"):
        del idem._ensure_init._done

    job1 = register_job("brand", "run1", "P4_VIDEO", "video", "render", "heygen")
    job2 = register_job("brand", "run1", "P4_VIDEO", "video", "render", "heygen")
    assert job1["id"] == job2["id"]

    mark_job(job1["id"], "succeeded", result={"video": "done"})
    existing = resolve_existing("brand", "run1", "P4_VIDEO", "video", "render")
    assert existing["status"] in TERMINAL_STATUSES
    assert existing["result"] == '{"video": "done"}'


# ─── Resumability ────────────────────────────────────────────────────────────


def test_resume_skips_completed_stages(run):
    rm = run
    rm.mark_completed(Phase.P0_SETUP)
    rm.mark_completed(Phase.P1_SCAN)
    rm.mark_completed(Phase.P2_STRATEGY)
    assert rm.next_pending_phase() == Phase.P3_SCRIPT


def test_rendered_slides_skip_on_resume(run):
    rm = run
    slides_dir = rm.run_dir / "slides"
    slides_dir.mkdir(exist_ok=True)
    (slides_dir / "slide_01.jpg").write_bytes(b"fake")
    (slides_dir / "slide_02.jpg").write_bytes(b"fake")
    found = rm.find_existing_slides()
    assert found == ["slide_01.jpg", "slide_02.jpg"]


def test_failed_stage_preserves_prior_work(run):
    rm = run
    rm.mark_completed(Phase.P0_SETUP)
    rm.mark_completed(Phase.P1_SCAN)
    rm.mark_failed(Phase.P2_STRATEGY, "simulated failure")
    state = rm.read_state()
    assert state["stages"]["P0_SETUP"]["status"] == "COMPLETED"
    assert state["stages"]["P1_SCAN"]["status"] == "COMPLETED"
    assert state["stages"]["P2_STRATEGY"]["status"] == "FAILED"
    assert state["stages"]["P2_STRATEGY"]["error"] == "simulated failure"
