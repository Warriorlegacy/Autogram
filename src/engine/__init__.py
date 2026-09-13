"""
Makerzz Engine — Autonomous Social-Content Operating System (P0–P8).

This package is ADDITIVE to the existing Autogram pipeline. It does not modify
any existing module behavior; existing entrypoints keep working unchanged.
"""

from src.engine.state_machine import (
    Phase,
    StageStatus,
    StagePolicy,
    ApprovalMode,
    STAGE_ORDER,
)
from src.engine.run_manager import RunManager

__all__ = [
    "Phase",
    "StageStatus",
    "StagePolicy",
    "ApprovalMode",
    "STAGE_ORDER",
    "RunManager",
]
