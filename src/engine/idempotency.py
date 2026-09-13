"""
Idempotency key formatting and provider job dedup for the Makerzz engine.

Contract: every externally billed side effect (provider submit, publish call)
gets a deterministic key:

    {brand_id}:{run_id}:{stage}:{asset_id}:{action}

Before a provider call:
    1. look up prior provider job by key
    2. if terminal  -> reuse its result
    3. if active    -> resume polling (never resubmit)
    4. if absent    -> create the job record FIRST, then call the provider
    5. persist the provider job id immediately
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from src.config import settings

_DB_PATH = Path(getattr(settings, "database_url", "sqlite:///autopilot.db").replace("sqlite:///", "")) or Path("autopilot.db")
if not _DB_PATH.is_absolute():
    _DB_PATH = Path(__file__).parent.parent.parent / _DB_PATH


def make_idempotency_key(
    brand_id: str,
    run_id: str,
    stage: str,
    asset_id: str,
    action: str,
) -> str:
    """Canonical idempotency key format."""
    return f"{brand_id}:{run_id}:{stage}:{asset_id}:{action}"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_provider_jobs_table() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS provider_jobs (
                id TEXT PRIMARY KEY,
                idempotency_key TEXT UNIQUE NOT NULL,
                brand_id TEXT,
                run_id TEXT,
                stage TEXT,
                asset_id TEXT,
                action TEXT,
                provider TEXT,
                provider_job_id TEXT,
                status TEXT NOT NULL DEFAULT 'queued',
                result TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def _ensure_init() -> None:
    if not hasattr(_ensure_init, "_done"):
        init_provider_jobs_table()
        _ensure_init._done = True


def new_job_id() -> str:
    return f"job-{uuid.uuid4().hex[:12]}"


def register_job(
    brand_id: str,
    run_id: str,
    stage: str,
    asset_id: str,
    action: str,
    provider: str,
    job_id: str | None = None,
) -> dict:
    """Create exactly one submission record BEFORE calling the provider."""
    _ensure_init()
    key = make_idempotency_key(brand_id, run_id, stage, asset_id, action)
    job_id = job_id or new_job_id()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO provider_jobs (
                id, idempotency_key, brand_id, run_id, stage, asset_id,
                action, provider, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)
            """,
            (job_id, key, brand_id, run_id, stage, asset_id, action, provider, now, now),
        )
        conn.commit()
    return get_job_by_key(key) or {"id": job_id, "idempotency_key": key, "status": "queued"}


def set_provider_job_id(job_id: str, provider_job_id: str) -> None:
    """Persist the external provider job id immediately after submission."""
    _ensure_init()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE provider_jobs
            SET provider_job_id = ?, status = 'polling', updated_at = ?
            WHERE id = ?
            """,
            (provider_job_id, datetime.utcnow().isoformat(), job_id),
        )
        conn.commit()


def mark_job(job_id: str, status: str, result: dict | None = None, error: str | None = None) -> None:
    """Transition a job to a terminal or intermediate state."""
    _ensure_init()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE provider_jobs
            SET status = ?, result = ?, error = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, json.dumps(result) if result else None, error, datetime.utcnow().isoformat(), job_id),
        )
        conn.commit()


def get_job(job_id: str) -> dict | None:
    _ensure_init()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM provider_jobs WHERE id = ?", (job_id,)).fetchone()
    return dict(row) if row else None


def get_job_by_key(key: str) -> dict | None:
    _ensure_init()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM provider_jobs WHERE idempotency_key = ?", (key,)
        ).fetchone()
    return dict(row) if row else None


def resolve_existing(
    brand_id: str,
    run_id: str,
    stage: str,
    asset_id: str,
    action: str,
) -> dict | None:
    """
    Idempotent lookup before any provider call.
    Returns the existing job record (active or terminal) or None.
    """
    key = make_idempotency_key(brand_id, run_id, stage, asset_id, action)
    return get_job_by_key(key)


TERMINAL_STATUSES = {"succeeded", "failed", "cancelled"}
ACTIVE_STATUSES = {"queued", "polling", "processing"}
