"""
Makerzz stage runner — executes P0–P8 stages for a run.

The runner is the ONLY place that wires stages together. It enforces:
  1. Gate artifacts exist before a stage runs (GateViolation otherwise)
  2. Approval policy (pauses with AWAITING_APPROVAL when mode=approve)
  3. Cost-before-work credit charging (fail-closed, owner VIP bypass)
  4. Idempotent provider actions via src.engine.idempotency
  5. Resumability: completed stages and rendered slides are never redone

Existing Autogram pipelines are untouched; this runner reuses the existing
generator/renderer/publisher modules additively.
"""

import logging
from datetime import datetime

from src.engine.state_machine import (
    Phase,
    StageStatus,
    StagePolicy,
    ApprovalMode,
    ApprovalRequired,
    GateViolation,
    InsufficientCredits,
    estimate_stage_cost,
    STAGE_ORDER,
)
from src.engine.run_manager import RunManager
from src.engine import idempotency
from src.billing.credit_ledger import ledger, InsufficientCreditError

logger = logging.getLogger(__name__)

MAX_SCRIPT_RETRIES = 3


class MakerzzRunner:
    """Executes one stage at a time on a durable run."""

    def __init__(self, rm: RunManager, user_id: str = "owner"):
        self.rm = rm
        self.user_id = user_id

    # ── Public API ───────────────────────────────────────────────────────────

    def step(self, target_phase: Phase | None = None) -> dict:
        """
        Execute the next pending stage (or a specific target phase).
        Returns a status dict for the dashboard/CLI.
        """
        state = self.rm.read_state()
        policy = StagePolicy.from_dict(state.get("policy"))

        phase = target_phase or self.rm.next_pending_phase()
        if phase is None:
            return {"ok": True, "status": "COMPLETED", "message": "All stages complete."}

        try:
            self.rm.assert_gate(phase)
        except GateViolation as gv:
            self.rm.mark_failed(phase, str(gv))
            return {"ok": False, "status": "GATE_BLOCKED", "error": str(gv), "phase": phase.value}

        # Approval policy check
        mode = policy.mode_for(phase)
        if mode == ApprovalMode.APPROVE:
            stage_status = state["stages"][phase.value]["status"]
            if stage_status not in (StageStatus.APPROVED.value, StageStatus.COMPLETED.value):
                self.rm.mark_awaiting_approval(phase)
                raise ApprovalRequired(phase)

        # Optional lane: auto-skip P4 when the brief does not request video
        if phase != Phase.P4_VIDEO:
            brief = state.get("brief") or {}
            p4_status = state["stages"][Phase.P4_VIDEO.value]["status"]
            if (
                not brief.get("include_video")
                and p4_status == StageStatus.PENDING.value
                and STAGE_ORDER.index(phase) > STAGE_ORDER.index(Phase.P4_VIDEO)
            ):
                self.rm.mark_skipped(Phase.P4_VIDEO)

        # Cost-before-work
        slides = len((state.get("brief") or {}).get("slides", []) or []) or 8
        cost = estimate_stage_cost(phase, slides=slides)
        try:
            self._charge(phase, cost)
        except InsufficientCreditError as e:
            self.rm.mark_blocked_credits(phase, str(e))
            return {"ok": False, "status": "BLOCKED_CREDITS", "error": str(e), "phase": phase.value}

        self.rm.mark_running(phase)
        try:
            handler = self._handler_for(phase)
            result = handler()
            self.rm.mark_completed(phase)
            return {"ok": True, "phase": phase.value, "status": "COMPLETED", "result": result}
        except ApprovalRequired:
            raise
        except Exception as e:
            self.rm.mark_failed(phase, str(e))
            # Refund on failure — original charge entry compensated
            self._refund_phase(phase)
            return {"ok": False, "phase": phase.value, "status": "FAILED", "error": str(e)[:400]}

    def approve(self, phase: Phase) -> dict:
        """Explicit human approval for a pending stage."""
        self.rm.mark_approved(phase)
        return {"ok": True, "phase": phase.value, "status": "APPROVED"}

    def resume(self) -> dict:
        """Resume a run from its last validated gate (loop until blocked)."""
        steps = []
        for _ in range(9):  # at most 9 stages
            phase = self.rm.next_pending_phase()
            if phase is None:
                break
            try:
                res = self.step(phase)
            except ApprovalRequired:
                steps.append({"phase": phase.value, "status": "AWAITING_APPROVAL"})
                break
            steps.append({"phase": phase.value, **res})
            if not res.get("ok"):
                break
        return {"ok": True, "run_id": self.rm.run_id, "steps": steps}

    # ── Stage handlers ───────────────────────────────────────────────────────

    def _handler_for(self, phase: Phase):
        return {
            Phase.P0_SETUP: self._run_p0,
            Phase.P1_SCAN: self._run_p1,
            Phase.P2_STRATEGY: self._run_p2,
            Phase.P3_SCRIPT: self._run_p3,
            Phase.P4_VIDEO: self._run_p4,
            Phase.P5_EDIT_PLAN: self._run_p5,
            Phase.P6_CAROUSEL: self._run_p6,
            Phase.P7_PUBLISH: self._run_p7,
            Phase.P8_REPORT: self._run_p8,
        }[phase]

    def _run_p0(self) -> dict:
        brief = self.rm.read_artifact("brief.json")
        # Broad-niche rejection (Makerzz P0 contract)
        niche = (brief.get("niche") or "").strip().lower()
        BROAD_NICHES = {"business", "ai", "tech", "marketing", "content"}
        if niche in BROAD_NICHES:
            raise ValueError(
                f"Niche '{niche}' is too broad. Provide a specific segment, "
                "e.g. 'self-hosted AI tools for solo founders'."
            )
        return {"brief_saved": True}

    def _run_p1(self) -> dict:
        from src.research.niche_scanner import scan_niche

        brief = self.rm.read_artifact("brief.json")
        profile_raw = brief.get("profile") or self._synthetic_profile(brief)
        scan = scan_niche(
            profile_raw,
            competitors_raw=brief.get("competitors") or [],
            niche=brief.get("niche", ""),
        )
        self.rm.write_artifact("scan.json", scan)
        return {"angles": len(scan.get("ranked_angles", []))}

    def _run_p2(self) -> dict:
        from src.research.calendar_compiler import compile_calendar

        scan = self.rm.read_artifact("scan.json")
        brief = self.rm.read_artifact("brief.json")
        calendar = compile_calendar(
            scan.get("ranked_angles", []),
            timezone_name=brief.get("timezone", "Asia/Kolkata"),
            slot=brief.get("posting_slot", "19:30"),
            cadence=brief.get("cadence") or {"carousel": 1, "reel": 1},
            seed=42,
        )
        self.rm.write_artifact("calendar.json", calendar)
        return {"total_items": calendar.get("total_items", 0)}

    def _run_p3(self) -> dict:
        """Script generation + strict verification with bounded retries."""
        from src.content.script_verifier import verify_script, build_retry_feedback

        brief = self.rm.read_artifact("brief.json")
        scan = self.rm.read_artifact("scan.json")

        script_text = None
        verification = None
        for attempt in range(1, MAX_SCRIPT_RETRIES + 1):
            script_text = self._generate_script(brief, scan, feedback=None)
            verification = verify_script(script_text)
            if verification.passed:
                break
            logger.warning(
                f"Script attempt {attempt} failed verification: {verification.violations[:3]}"
            )

        if verification is None or not verification.passed:
            raise ValueError(
                "Script failed strict verification after "
                f"{MAX_SCRIPT_RETRIES} attempts: {verification.violations[:5]}"
            )

        self.rm.write_artifact("script.txt", verification.clean_text)
        self.rm.write_artifact("script_verification.json", verification.to_dict())
        return {"word_count": verification.word_count, "seconds": verification.estimated_seconds}

    def _run_p4(self) -> dict:
        """Video render lane. Uses JSON2Video cloud engine with local Edge-TTS/FFmpeg fallback."""
        brief = self.rm.read_artifact("brief.json")
        if not brief.get("include_video"):
            self.rm.mark_skipped(Phase.P4_VIDEO)
            return {"skipped": True, "reason": "brief.include_video not set"}

        key = idempotency.make_idempotency_key(
            "signhify", self.rm.run_id, "P4_VIDEO", "video", "render"
        )
        existing = idempotency.resolve_existing("signhify", self.rm.run_id, "P4_VIDEO", "video", "render")
        if existing and existing.get("status") == "succeeded" and existing.get("result"):
            res = json.loads(existing["result"]) if isinstance(existing["result"], str) else existing["result"]
            return {"resumed": True, "provider_job": existing["id"], "video_path": res.get("video_path")}

        job = idempotency.register_job(
            "signhify", self.rm.run_id, "P4_VIDEO", "video", "render", "json2video"
        )

        try:
            from src.content.json2video_engine import JSON2VideoEngine
            engine = JSON2VideoEngine()
            script_text = self.rm.read_artifact("script.txt")
            edit_plan = None
            if (self.rm.run_dir / "edit_plan.json").exists():
                edit_plan = self.rm.read_artifact("edit_plan.json")

            video_output_path = self.rm.run_dir / "video.mp4"
            render_res = engine.render_reel(
                script_text=script_text,
                edit_plan=edit_plan,
                output_path=video_output_path,
                fallback_to_local=True
            )

            idempotency.mark_job(job["id"], "succeeded", result=render_res)
            self.rm.write_artifact("provider_job.json", render_res)
            return {"status": "completed", "video_path": str(video_output_path), "provider": render_res.get("provider")}
        except Exception as e:
            logger.error(f"Video render failed: {e}")
            idempotency.mark_job(job["id"], "failed", error=str(e))
            self.rm.mark_skipped(Phase.P4_VIDEO)
            return {"skipped": True, "error": str(e)}

    def _run_p5(self) -> dict:
        from src.content.edit_plan_compiler import compile_edit_plan
        from src.content.script_verifier import verify_script

        script_text = self.rm.read_artifact("script.txt")
        ver = verify_script(script_text)
        plan = compile_edit_plan(script_text, estimated_seconds=ver.estimated_seconds)
        self.rm.write_artifact("edit_plan.json", plan)
        return {"beats": plan.get("total_beats", 0)}

    def _run_p6(self) -> dict:
        """Carousel plan + prompts, then render with slide-skip resumability."""
        from src.research.niche_scanner import TARGET_ANGLES  # noqa: F401 (contract ref)

        brief = self.rm.read_artifact("brief.json")
        scan = self.rm.read_artifact("scan.json")
        calendar = self.rm.read_artifact("calendar.json")

        plan = {
            "version": "1.0",
            "brand": brief.get("brand", "Signhify Studio"),
            "creator": brief.get("creator", "Piyush Raj Singh"),
            "top_angle": (scan.get("ranked_angles") or [{}])[0],
            "first_slot": ((calendar.get("days") or [{}])[0].get("items") or [{}])[0]
            if calendar.get("days")
            else {},
            "slides": [],
        }
        purposes = ["hook", "problem", "mechanism", "proof", "example", "summary", "cta"]
        top = (scan.get("ranked_angles") or [{}])[0]
        angle_text = top.get("angle", "Niche insight")
        for i in range(8):
            plan["slides"].append({
                "index": i + 1,
                "purpose": purposes[min(i, len(purposes) - 1)],
                "headline": angle_text[:80] if i == 0 else f"Point {i}",
                "body": (top.get("mechanism") or "") if i == 1 else "",
                "visualDirection": "1080x1350 cream paper, bold black display text, coral accent",
                "layout": "standard",
                "prompt": f"Slide {i + 1}: {angle_text[:120]}",
                "altText": f"Slide {i + 1} of carousel about {brief.get('niche', 'the niche')}",
            })
        self.rm.write_artifact("carousel_plan.json", plan)
        self.rm.write_artifact(
            "approved_prompts.json",
            {"approved": True, "prompts": [s["prompt"] for s in plan["slides"]]},
        )

        # Render with skip-existing behavior (resumability)
        rendered = self._render_slides(plan)
        return {"slides_planned": len(plan["slides"]), "slides_rendered": rendered}

    def _render_slides(self, plan: dict) -> int:
        """
        Render slides via the existing CarouselRenderer (reused, not modified),
        skipping already-rendered slides for resumability.
        """
        slides_dir = self.rm.run_dir / "slides"
        slides_dir.mkdir(exist_ok=True)
        existing = {p.name for p in slides_dir.glob("slide_*.jpg")}

        # Only render slides that don't exist yet (resume contract: skip done work)
        pending = [
            {
                "slide_number": s["index"],
                "layout": "standard",
                "headline": s.get("headline", ""),
                "subtitle": s.get("body", ""),
            }
            for s in plan.get("slides", [])
            if f"slide_{s['index']:02d}.jpg" not in existing
        ]

        total_planned = len(plan.get("slides", []))
        if not pending:
            return total_planned

        carousel_payload = {"slides": pending, "theme": "default"}
        from renderer.render import CarouselRenderer
        renderer = CarouselRenderer()
        rendered = renderer.render_carousel(carousel_payload, slides_dir)
        return len(existing) + len(rendered)

    def _run_p7(self) -> dict:
        """Queue build; publish only via adapters with explicit approval above."""
        from src.distribution import get_adapters

        brief = self.rm.read_artifact("brief.json")
        calendar = self.rm.read_artifact("calendar.json")
        adapters = get_adapters()

        queue = []
        statuses = {name: ad.configuration_status() for name, ad in adapters.items()}
        first_items = []
        for day in (calendar.get("days") or [])[:7]:
            first_items.extend(day.get("items", [])[:1])

        for item in first_items:
            queue.append({
                "id": item.get("id"),
                "scheduled_for": item.get("scheduled_for"),
                "format": item.get("format"),
                "angle": item.get("angle"),
                "status": "QUEUED",
                "destinations": ["instagram"] + (
                    ["ayrshare"] if statuses.get("ayrshare", {}).get("configured") else []
                ),
            })

        self.rm.write_artifact("queue.json", {"queue": queue, "adapter_status": statuses})
        self.rm.write_artifact("publish_receipt.json", {
            "status": "queued-not-published",
            "note": "Publishing executes through the dashboard approval endpoint or scheduled worker.",
            "adapter_status": statuses,
            "availability": "pending",
        })
        return {"queued": len(queue)}

    def _run_p8(self) -> dict:
        from src.billing.report_generator import generate_report

        state = self.rm.read_state()
        report = generate_report(self.rm.run_dir, state)
        return {"report": "filed", "pdf": (self.rm.run_dir / "report.pdf").exists()}

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _charge(self, phase: Phase, cost: int) -> None:
        if cost <= 0:
            return
        entry = ledger.charge(
            user_id=self.user_id,
            stage=phase.value,
            operation=phase.value.lower(),
            idempotency_key=f"{self.user_id}:{self.rm.run_id}:{phase.value}:charge",
            amount=cost,
            run_id=self.rm.run_id,
            reason=f"Makerzz stage {phase.value}",
        )
        self.rm.record_charged_credits(phase, abs(int(entry["amount_signed"])))

    def _refund_phase(self, phase: Phase) -> None:
        try:
            entry = ledger.get_entry_by_idempotency_key(
                f"{self.user_id}:{self.rm.run_id}:{phase.value}:charge"
            )
            if entry:
                ledger.refund(self.user_id, entry["id"], reason=f"{phase.value} failed — refund")
        except Exception as e:
            logger.warning(f"Refund for {phase.value} skipped: {e}")

    def _generate_script(self, brief: dict, scan: dict, feedback: str | None) -> str:
        """Try the existing LLM generator chain; fall back to deterministic draft."""
        top = (scan.get("ranked_angles") or [{}])[0]
        angle_text = top.get("angle", brief.get("niche", "this niche"))
        mechanism = top.get("mechanism", "consistent posting wins")
        try:
            from src.content.generator import generator
            topic = {
                "title": angle_text,
                "pillar": brief.get("niche", "AI Automation"),
                "style": "default",
            }
            carousel = generator.generate_carousel(topic, sources=[])
            lines = []
            for slide in carousel.get("slides", []):
                text = (slide.get("headline") or "") + ". " + (slide.get("subtitle") or slide.get("body") or "")
                lines.append(text.strip())
            raw = " ".join(line for line in lines if line)
            if raw.strip():
                return raw
        except Exception as e:
            logger.warning(f"LLM script generation unavailable, using deterministic draft: {e}")
        return (
            f"Here is the truth about {angle_text}. "
            f"Most people quit before the system compounds. "
            f"The mechanism is simple: {mechanism}. "
            f"Look at the evidence in this niche and you will see the same pattern. "
            f"Ship one piece of content every day for thirty days and the data will speak. "
            f"Save this, start tonight, and comment SYSTEM for the full playbook. Follow signhify.studio for more."
        )

    def _synthetic_profile(self, brief: dict) -> dict:
        """Profile scaffold when no scrape source is configured (never fabricated metrics)."""
        return {
            "handle": brief.get("handle", "signhify.studio"),
            "platform": "instagram",
            "followers": None,  # unknown = unavailable, never guessed
            "bio": brief.get("audience", ""),
            "posts": [
                {
                    "caption": obs.get("topic", "Niche signal"),
                    "format": obs.get("format", "carousel"),
                    "likes": None, "comments": None, "shares": None, "views": None,
                    "url": "",
                }
                for obs in []
            ],
        }
