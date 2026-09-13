"""
Typed P0–P8 state machine for the Makerzz Autonomous Social-Content OS.

Every phase has:
  - a canonical gate artifact (validated before downstream stages may run)
  - an approval policy (approve | auto)
  - a credit cost estimate (fail-closed if insufficient)

A downstream stage may not run until its required gate artifact exists
and passes validation. Publishing is special: it always requires explicit
confirmation unless autonomy has been explicitly enabled for the brand.
"""

import enum
from dataclasses import dataclass, field


class Phase(str, enum.Enum):
    """Canonical P0–P8 run phases. Never use arbitrary strings in code."""

    P0_SETUP = "P0_SETUP"
    P1_SCAN = "P1_SCAN"
    P2_STRATEGY = "P2_STRATEGY"
    P3_SCRIPT = "P3_SCRIPT"
    P4_VIDEO = "P4_VIDEO"
    P5_EDIT_PLAN = "P5_EDIT_PLAN"
    P6_CAROUSEL = "P6_CAROUSEL"
    P7_PUBLISH = "P7_PUBLISH"
    P8_REPORT = "P8_REPORT"


class StageStatus(str, enum.Enum):
    """Lifecycle of one stage inside a run."""

    PENDING = "PENDING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED_CREDITS = "BLOCKED_CREDITS"
    SKIPPED = "SKIPPED"


class ApprovalMode(str, enum.Enum):
    """Per-stage approval semantics. Default is approve (human in the loop)."""

    APPROVE = "approve"
    AUTO = "auto"


# Ordered execution list for the linear spine (P3/P4/P5/P6 run in parallel
# lanes in practice, but gates still resolve in this canonical order).
STAGE_ORDER: list[Phase] = [
    Phase.P0_SETUP,
    Phase.P1_SCAN,
    Phase.P2_STRATEGY,
    Phase.P3_SCRIPT,
    Phase.P4_VIDEO,
    Phase.P5_EDIT_PLAN,
    Phase.P6_CAROUSEL,
    Phase.P7_PUBLISH,
    Phase.P8_REPORT,
]

# Canonical gate artifacts per phase (relative to the run workspace).
GATE_ARTIFACTS: dict[Phase, list[str]] = {
    Phase.P0_SETUP: ["brief.json"],
    Phase.P1_SCAN: ["scan.json"],
    Phase.P2_STRATEGY: ["calendar.json"],
    Phase.P3_SCRIPT: ["script.txt", "script_verification.json"],
    Phase.P4_VIDEO: [],  # optional lane; video.mp4 + provider_job.json when executed
    Phase.P5_EDIT_PLAN: ["edit_plan.json"],
    Phase.P6_CAROUSEL: ["carousel_plan.json", "approved_prompts.json"],
    Phase.P7_PUBLISH: ["queue.json"],
    Phase.P8_REPORT: ["report.json"],
}

# Estimated credit costs per stage (canonical pricing table).
CREDIT_COSTS: dict[str, int] = {
    "scan": 40,
    "trends": 15,
    "script": 12,
    "edit_plan": 20,
    "carousel_prompts": 30,
    "caption_pack": 5,
    "slide_low": 3,
    "slide_high": 6,
    "slide_4k": 12,
    "video_1080p_60s": 202,
    "publish": 0,  # publishing is unmetered
}

PHASE_COST_KEY: dict[Phase, str] = {
    Phase.P0_SETUP: "trends",
    Phase.P1_SCAN: "scan",
    Phase.P2_STRATEGY: "trends",
    Phase.P3_SCRIPT: "script",
    Phase.P4_VIDEO: "video_1080p_60s",
    Phase.P5_EDIT_PLAN: "edit_plan",
    Phase.P6_CAROUSEL: "carousel_prompts",
    Phase.P7_PUBLISH: "publish",
    Phase.P8_REPORT: "trends",
}


@dataclass
class StagePolicy:
    """Approval policy for one run. Publishing always defaults to approve."""

    scan: ApprovalMode = ApprovalMode.APPROVE
    strategy: ApprovalMode = ApprovalMode.APPROVE
    script: ApprovalMode = ApprovalMode.APPROVE
    video: ApprovalMode = ApprovalMode.APPROVE
    edit: ApprovalMode = ApprovalMode.APPROVE
    carousel: ApprovalMode = ApprovalMode.APPROVE
    publish: ApprovalMode = ApprovalMode.APPROVE
    publish_reconfirmation_days: int = 7

    def mode_for(self, phase: Phase) -> ApprovalMode:
        mapping = {
            Phase.P1_SCAN: self.scan,
            Phase.P2_STRATEGY: self.strategy,
            Phase.P3_SCRIPT: self.script,
            Phase.P4_VIDEO: self.video,
            Phase.P5_EDIT_PLAN: self.edit,
            Phase.P6_CAROUSEL: self.carousel,
            Phase.P7_PUBLISH: self.publish,
        }
        return mapping.get(phase, ApprovalMode.APPROVE)

    @classmethod
    def autonomous(cls) -> "StagePolicy":
        """Fully autonomous mode: run everything, report afterwards."""
        return cls(
            scan=ApprovalMode.AUTO,
            strategy=ApprovalMode.AUTO,
            script=ApprovalMode.AUTO,
            video=ApprovalMode.AUTO,
            edit=ApprovalMode.AUTO,
            carousel=ApprovalMode.AUTO,
            publish=ApprovalMode.APPROVE,  # publish NEVER silently auto-runs
        )

    def to_dict(self) -> dict:
        return {
            "scan": self.scan.value,
            "strategy": self.strategy.value,
            "script": self.script.value,
            "video": self.video.value,
            "edit": self.edit.value,
            "carousel": self.carousel.value,
            "publish": self.publish.value,
            "publish_reconfirmation_days": self.publish_reconfirmation_days,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "StagePolicy":
        if not data:
            return cls()
        kwargs = {}
        for key in ("scan", "strategy", "script", "video", "edit", "carousel", "publish"):
            if key in data:
                kwargs[key] = ApprovalMode(data[key])
        if "publish_reconfirmation_days" in data:
            kwargs["publish_reconfirmation_days"] = int(data["publish_reconfirmation_days"])
        return cls(**kwargs)


@dataclass
class StageState:
    """Persisted state of a single stage in a run."""

    phase: Phase
    status: StageStatus = StageStatus.PENDING
    attempt: int = 0
    approval_required: bool = True
    estimated_credits: int = 0
    charged_credits: int = 0
    error: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "phase": self.phase.value,
            "status": self.status.value,
            "attempt": self.attempt,
            "approval_required": self.approval_required,
            "estimated_credits": self.estimated_credits,
            "charged_credits": self.charged_credits,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "artifacts": self.artifacts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StageState":
        return cls(
            phase=Phase(data["phase"]),
            status=StageStatus(data.get("status", "PENDING")),
            attempt=int(data.get("attempt", 0)),
            approval_required=bool(data.get("approval_required", True)),
            estimated_credits=int(data.get("estimated_credits", 0)),
            charged_credits=int(data.get("charged_credits", 0)),
            error=data.get("error"),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            artifacts=list(data.get("artifacts", [])),
        )


class GateViolation(RuntimeError):
    """Raised when a stage attempts to run without its upstream gate artifacts."""

    def __init__(self, phase: Phase, missing: list[str]):
        self.phase = phase
        self.missing = missing
        super().__init__(
            f"Gate violation for {phase.value}: missing required artifacts: {', '.join(missing)}"
        )


class ApprovalRequired(RuntimeError):
    """Raised when a stage is paused pending explicit human approval."""

    def __init__(self, phase: Phase):
        self.phase = phase
        super().__init__(f"Stage {phase.value} is awaiting explicit approval.")


class InsufficientCredits(RuntimeError):
    """Fail-closed: raised before any billable provider call when balance is too low."""

    def __init__(self, needed: int, available: int, stage: str):
        self.needed = needed
        self.available = available
        self.stage = stage
        super().__init__(
            f"Insufficient credits for stage {stage}: need {needed}, available {available}. "
            "Stage halted; prior work preserved."
        )


def estimate_stage_cost(phase: Phase, slides: int = 0) -> int:
    """Exact pre-work cost estimate for a phase (cost-before-work contract)."""
    base = CREDIT_COSTS[PHASE_COST_KEY[phase]]
    if phase == Phase.P6_CAROUSEL:
        # prompts + slide renders at standard tier
        return base + slides * CREDIT_COSTS["slide_low"]
    return base


def required_gate_artifacts(phase: Phase) -> list[str]:
    return list(GATE_ARTIFACTS.get(phase, []))


def upstream_phases(phase: Phase) -> list[Phase]:
    """All phases that must be COMPLETED before `phase` may execute."""
    idx = STAGE_ORDER.index(phase)
    return STAGE_ORDER[:idx]
