"""
Durable run manager for the Makerzz P0–P8 engine.

Each run lives in an isolated workspace `runs/<run_id>/` containing every
durable JSON/media artifact plus a `run_state.json` checkpoint file. Rerunning
a failed run resumes from the last validated gate artifact — already rendered
slides are skipped, already charged credits are never charged twice.
"""

import hashlib
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from src.engine.state_machine import (
    Phase,
    StageStatus,
    StagePolicy,
    StageState,
    GateViolation,
    GATE_ARTIFACTS,
    STAGE_ORDER,
)

BASE_DIR = Path(__file__).parent.parent.parent
RUNS_DIR = BASE_DIR / "runs"


def _slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len] or "run"


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class RunManager:
    """
    Owns the lifecycle of one durable run workspace.

    Usage:
        rm = RunManager.create(brief={...})
        rm.assert_gate(Phase.P1_SCAN)         # raises GateViolation if P0 not done
        rm.write_artifact("scan.json", {...})
        rm.mark_completed(Phase.P1_SCAN)
    """

    def __init__(self, run_id: str, run_dir: Path | None = None):
        self.run_id = run_id
        self.run_dir = Path(run_dir) if run_dir else (RUNS_DIR / run_id)
        self.state_path = self.run_dir / "run_state.json"

    # ── Lifecycle ────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, brief: dict, slug: str | None = None, run_dir: Path | None = None) -> "RunManager":
        """Initialize a new run with a validated brief (P0 gate artifact)."""
        stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        slug_part = _slugify(slug or brief.get("niche") or brief.get("brand") or "makerzz")
        run_id = f"{stamp}_{slug_part}_{uuid.uuid4().hex[:6]}"
        rm = cls(run_id, run_dir=run_dir)
        rm.run_dir.mkdir(parents=True, exist_ok=True)

        # P0 stage is complete the moment the brief is written.
        stages = {
            phase.value: StageState(phase=phase).to_dict() for phase in STAGE_ORDER
        }
        stages[Phase.P0_SETUP.value]["status"] = StageStatus.COMPLETED.value
        stages[Phase.P0_SETUP.value]["finished_at"] = datetime.utcnow().isoformat()

        state = {
            "run_id": run_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "ACTIVE",
            "current_stage": Phase.P1_SCAN.value,
            "brief": brief,
            "stages": stages,
            "policy": (
                StagePolicy.autonomous().to_dict()
                if (not brief.get("approval_policy") and brief.get("mode") == "auto")
                else StagePolicy.from_dict(brief.get("approval_policy")).to_dict()
            ),
            "mode": brief.get("mode", "approve"),
        }
        rm.write_state(state)
        rm.write_artifact("brief.json", brief)
        return rm

    @classmethod
    def load(cls, run_id: str) -> "RunManager":
        rm = cls(run_id)
        if not rm.state_path.exists():
            raise FileNotFoundError(f"Run '{run_id}' does not exist (no run_state.json).")
        return rm

    @classmethod
    def list_runs(cls) -> list[dict]:
        """List all durable runs with current P0–P8 status, newest first."""
        runs = []
        if not RUNS_DIR.exists():
            return runs
        for d in sorted(RUNS_DIR.iterdir(), reverse=True):
            state_file = d / "run_state.json"
            if not d.is_dir() or not state_file.exists():
                continue
            try:
                state = json.loads(state_file.read_text(encoding="utf-8"))
                runs.append(
                    {
                        "run_id": state.get("run_id", d.name),
                        "status": state.get("status"),
                        "current_stage": state.get("current_stage"),
                        "niche": (state.get("brief") or {}).get("niche"),
                        "created_at": state.get("created_at"),
                        "updated_at": state.get("updated_at"),
                    }
                )
            except Exception:
                continue
        return runs

    # ── State I/O ────────────────────────────────────────────────────────────

    def read_state(self) -> dict:
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def write_state(self, state: dict) -> None:
        state["updated_at"] = datetime.utcnow().isoformat()
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    @property
    def state(self) -> dict:
        return self.read_state()

    # ── Artifacts & gate enforcement ─────────────────────────────────────────

    def artifact_path(self, name: str) -> Path:
        return self.run_dir / name

    def has_artifact(self, name: str) -> bool:
        return self.artifact_path(name).exists()

    def write_artifact(self, name: str, payload: dict | list | str) -> Path:
        """Write a durable artifact and register it on its owning stage."""
        path = self.artifact_path(name)
        if isinstance(payload, (dict, list)):
            text = json.dumps(payload, indent=2, ensure_ascii=False)
        else:
            text = str(payload)
        path.write_text(text, encoding="utf-8")

        state = self.read_state()
        phase = self._owning_phase(name)
        if phase:
            stage = state["stages"][phase.value]
            if name not in stage["artifacts"]:
                stage["artifacts"].append(name)
        state["updated_at"] = datetime.utcnow().isoformat()
        self.write_state(state)
        return path

    def read_artifact(self, name: str) -> dict | list | str:
        path = self.artifact_path(name)
        if not path.exists():
            raise FileNotFoundError(f"Artifact '{name}' missing in run {self.run_id}")
        text = path.read_text(encoding="utf-8")
        if name.endswith(".json"):
            return json.loads(text)
        return text

    def assert_gate(self, phase: Phase) -> None:
        """
        Gate enforcement (Makerzz contract): a downstream stage may not run
        until every UPSTREAM phase is COMPLETED and every upstream gate
        artifact exists. The current phase's own artifacts are its OUTPUT,
        produced by the stage itself.
        """
        state = self.read_state()
        idx = STAGE_ORDER.index(phase)

        missing: list[str] = []
        for upstream in STAGE_ORDER[:idx]:
            stage = state["stages"].get(upstream.value, {})
            status = stage.get("status")
            if status == StageStatus.COMPLETED.value:
                pass
            elif upstream == Phase.P4_VIDEO and status == StageStatus.SKIPPED.value:
                continue  # optional lane
            else:
                missing.append(f"upstream stage {upstream.value} not completed")
                continue

            # Upstream gate artifacts must exist and be inspectable
            for name in GATE_ARTIFACTS.get(upstream, []):
                if not self.has_artifact(name):
                    missing.append(f"{upstream.value} artifact '{name}' missing")

        if missing:
            raise GateViolation(phase, missing)

    def mark_running(self, phase: Phase) -> None:
        state = self.read_state()
        stage = state["stages"][phase.value]
        stage["status"] = StageStatus.RUNNING.value
        stage["attempt"] = int(stage.get("attempt", 0)) + 1
        stage["started_at"] = datetime.utcnow().isoformat()
        state["current_stage"] = phase.value
        self.write_state(state)

    def mark_completed(self, phase: Phase) -> None:
        state = self.read_state()
        stage = state["stages"][phase.value]
        if stage["status"] == StageStatus.SKIPPED.value:
            return  # skipped lanes stay skipped
        stage["status"] = StageStatus.COMPLETED.value
        stage["finished_at"] = datetime.utcnow().isoformat()
        nxt = STAGE_ORDER.index(phase) + 1
        if nxt < len(STAGE_ORDER):
            state["current_stage"] = STAGE_ORDER[nxt].value
        else:
            state["status"] = "COMPLETED"
        self.write_state(state)

    def mark_failed(self, phase: Phase, error: str) -> None:
        state = self.read_state()
        stage = state["stages"][phase.value]
        stage["status"] = StageStatus.FAILED.value
        stage["error"] = str(error)[:500]
        stage["finished_at"] = datetime.utcnow().isoformat()
        self.write_state(state)

    def mark_skipped(self, phase: Phase) -> None:
        state = self.read_state()
        state["stages"][phase.value]["status"] = StageStatus.SKIPPED.value
        self.write_state(state)

    def mark_blocked_credits(self, phase: Phase, reason: str) -> None:
        state = self.read_state()
        stage = state["stages"][phase.value]
        stage["status"] = StageStatus.BLOCKED_CREDITS.value
        stage["error"] = str(reason)[:500]
        self.write_state(state)

    def mark_awaiting_approval(self, phase: Phase) -> None:
        state = self.read_state()
        state["stages"][phase.value]["status"] = StageStatus.AWAITING_APPROVAL.value
        self.write_state(state)

    def mark_approved(self, phase: Phase) -> None:
        state = self.read_state()
        stage = state["stages"][phase.value]
        # Approval (re)arms a stage: pending, awaiting, or previously failed
        # stages become APPROVED so the stage can execute or retry.
        if stage["status"] in (
            StageStatus.AWAITING_APPROVAL.value,
            StageStatus.PENDING.value,
            StageStatus.FAILED.value,
        ):
            stage["status"] = StageStatus.APPROVED.value
            stage["error"] = None
        self.write_state(state)

    # ── Resumability ─────────────────────────────────────────────────────────

    def next_pending_phase(self) -> Phase | None:
        """First phase not yet COMPLETED/SKIPPED — the resume point."""
        state = self.read_state()
        for phase in STAGE_ORDER:
            stage = state["stages"].get(phase.value, {})
            if stage.get("status") not in (
                StageStatus.COMPLETED.value,
                StageStatus.SKIPPED.value,
            ):
                return phase
        return None

    def find_existing_slides(self) -> list[str]:
        """Already-rendered slide files, for skip-on-resume behavior."""
        carousel_dir = self.run_dir / "slides"
        if not carousel_dir.exists():
            return []
        return sorted(p.name for p in carousel_dir.glob("slide_*.jpg"))

    def record_charged_credits(self, phase: Phase, amount: int) -> None:
        state = self.read_state()
        stage = state["stages"][phase.value]
        stage["charged_credits"] = int(stage.get("charged_credits", 0)) + amount
        self.write_state(state)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _owning_phase(self, artifact_name: str) -> Phase | None:
        for phase, names in GATE_ARTIFACTS.items():
            if artifact_name in names:
                return phase
        # extra artifacts (scan details, etc.) map to their stage caller via
        # mark_* methods; unregistered extras are fine.
        return None

    # ── Serialization for the dashboard ──────────────────────────────────────

    def summary(self) -> dict:
        state = self.read_state()
        return {
            "run_id": state.get("run_id"),
            "status": state.get("status"),
            "current_stage": state.get("current_stage"),
            "mode": state.get("mode"),
            "brief": state.get("brief"),
            "created_at": state.get("created_at"),
            "updated_at": state.get("updated_at"),
            "stages": state.get("stages"),
            "artifacts": sorted(
                p.name for p in self.run_dir.iterdir() if p.is_file()
            ) if self.run_dir.exists() else [],
            "slides_rendered": len(self.find_existing_slides()),
        }
