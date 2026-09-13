"""
Append-only credit ledger (Makerzz P8 / Part IV).

Rules (enforced, tested):
  - Entries are NEVER mutated or deleted. Corrections are new entries.
  - Every charge carries an idempotency key — double-charging is impossible.
  - Balance is a transactionally maintained projection (balance_after).
  - Fail-closed: insufficient balance aborts BEFORE any provider call.
  - AUTOGRAM_OWNER_KEY holder gets VIP unlimited balance.
  - Publishing is unmetered (0 credits).

Standardized cost table (versioned, single source of truth):
  Scan: 40 | Script: 12 | Edit Plan: 20 | Carousel Prompts+Plan: 30
  Standard Slide Render: 3/slide | Vertical Video Compositing: 202
  Publishing: 0 credits
"""

import sqlite3
import threading
import uuid
from datetime import datetime
from pathlib import Path

from src.config import settings

_DB_PATH = Path(__file__).parent.parent.parent / "autopilot.db"

LOCK = threading.Lock()

CREDIT_COSTS = {
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
    "publish": 0,
}


class CreditLedger:
    """Transactional append-only SQLite credit ledger."""

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = str(db_path or _DB_PATH)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS credit_ledger (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    brand_id TEXT,
                    run_id TEXT,
                    stage TEXT,
                    operation TEXT,
                    amount_signed INTEGER NOT NULL,
                    balance_after INTEGER NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'credits',
                    idempotency_key TEXT UNIQUE NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    # ── Balance & identity ───────────────────────────────────────────────────

    def is_owner(self, user_id: str) -> bool:
        """Owner VIP: unlimited credits via AUTOGRAM_OWNER_KEY identity."""
        owner_key = getattr(settings, "autogram_owner_key", "")
        return bool(owner_key) and user_id in (owner_key, "owner", "OWNER")

    def get_balance(self, user_id: str) -> int:
        """Recompute balance from ledger entries (append-only safe)."""
        if self.is_owner(user_id):
            return 10**9  # effectively unlimited for VIP owner
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT balance_after FROM credit_ledger
                WHERE user_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1
                """,
                (user_id,),
            ).fetchone()
        return int(row["balance_after"]) if row else 0

    def top_up(self, user_id: str, amount: int, reason: str = "plan grant") -> dict:
        """Grant credits (positive entry). Owner may also top up."""
        if amount <= 0:
            raise ValueError("Top-up amount must be positive.")
        return self._append(
            user_id=user_id,
            amount=amount,
            stage="billing",
            operation="top_up",
            idempotency_key=f"topup:{user_id}:{uuid.uuid4().hex[:12]}",
            reason=reason,
        )

    # ── Charge / debit (fail-closed) ─────────────────────────────────────────

    def charge(
        self,
        user_id: str,
        stage: str,
        operation: str,
        idempotency_key: str,
        amount: int | None = None,
        brand_id: str | None = None,
        run_id: str | None = None,
        reason: str | None = None,
    ) -> dict:
        """
        Atomically debit credits for one operation.

        Cost-before-work contract: call this BEFORE the provider call.
        Raises InsufficientCreditError on failure — never partial charge,
        never silent downgrade.
        """
        if amount is None:
            amount = CREDIT_COSTS.get(operation, 0)

        # Owner VIP bypass: unlimited balance (VIP floor keeps balance effectively-unlimited)
        if self.is_owner(user_id):
            return self._append(
                user_id=user_id,
                amount=-abs(amount),
                stage=stage,
                operation=operation,
                idempotency_key=idempotency_key,
                brand_id=brand_id,
                run_id=run_id,
                reason=reason or "owner VIP (unmetered)",
                vip=True,
            )

        with LOCK:
            with self._connect() as conn:
                # Idempotency: same key returns the original entry untouched
                existing = conn.execute(
                    "SELECT * FROM credit_ledger WHERE idempotency_key = ?",
                    (idempotency_key,),
                ).fetchone()
                if existing:
                    return dict(existing)

                # Transaction: serialize balance check + insert (compare-and-swap)
                conn.execute("BEGIN IMMEDIATE")
                try:
                    row = conn.execute(
                        """
                        SELECT balance_after FROM credit_ledger
                        WHERE user_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1
                        """,
                        (user_id,),
                    ).fetchone()
                    balance = int(row["balance_after"]) if row else 0

                    if balance < amount:
                        conn.rollback()
                        raise InsufficientCreditError(
                            needed=amount, available=balance, stage=stage
                        )

                    entry_id = f"cl-{uuid.uuid4().hex[:16]}"
                    conn.execute(
                        """
                        INSERT INTO credit_ledger (
                            id, user_id, brand_id, run_id, stage, operation,
                            amount_signed, balance_after, currency,
                            idempotency_key, reason, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'credits', ?, ?, ?)
                        """,
                        (
                            entry_id,
                            user_id,
                            brand_id,
                            run_id,
                            stage,
                            operation,
                            -abs(amount),
                            balance - abs(amount),
                            idempotency_key,
                            reason,
                            datetime.utcnow().isoformat(),
                        ),
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise

            return self.get_entry(entry_id)

    def refund(
        self,
        user_id: str,
        original_entry_id: str,
        reason: str = "stage failed — refund",
    ) -> dict:
        """
        Refund a prior charge by appending a compensating positive entry.
        The original entry is never mutated.
        """
        original = self.get_entry(original_entry_id)
        if not original:
            raise ValueError(f"Ledger entry '{original_entry_id}' not found.")
        refund_amount = abs(int(original["amount_signed"]))
        return self._append(
            user_id=user_id,
            amount=refund_amount,
            stage=original["stage"],
            operation="refund",
            idempotency_key=f"refund:{original_entry_id}",
            brand_id=original.get("brand_id"),
            run_id=original.get("run_id"),
            reason=reason,
        )

    # ── Introspection ────────────────────────────────────────────────────────

    def get_entry(self, entry_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM credit_ledger WHERE id = ?", (entry_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_entry_by_idempotency_key(self, key: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM credit_ledger WHERE idempotency_key = ?", (key,)
            ).fetchone()
        return dict(row) if row else None

    def list_entries(self, user_id: str | None = None, limit: int = 100) -> list[dict]:
        query = "SELECT * FROM credit_ledger"
        params: tuple = ()
        if user_id:
            query += " WHERE user_id = ?"
            params = (user_id,)
        query += " ORDER BY created_at DESC, rowid DESC LIMIT ?"
        params = params + (limit,)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    # ── Internal ─────────────────────────────────────────────────────────────

    def _append(
        self,
        user_id: str,
        amount: int,
        stage: str,
        operation: str,
        idempotency_key: str,
        brand_id: str | None = None,
        run_id: str | None = None,
        reason: str | None = None,
        vip: bool = False,
    ) -> dict:
        with LOCK:
            with self._connect() as conn:
                existing = conn.execute(
                    "SELECT * FROM credit_ledger WHERE idempotency_key = ?",
                    (idempotency_key,),
                ).fetchone()
                if existing:
                    return dict(existing)

                conn.execute("BEGIN IMMEDIATE")
                try:
                    row = conn.execute(
                        """
                        SELECT balance_after FROM credit_ledger
                        WHERE user_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1
                        """,
                        (user_id,),
                    ).fetchone()
                    balance = int(row["balance_after"]) if row else 0
                    new_balance = balance + amount
                    if vip and new_balance < 10**9:
                        # Owner VIP: projected balance is floored at effectively-unlimited
                        new_balance = 10**9
                    entry_id = f"cl-{uuid.uuid4().hex[:16]}"
                    conn.execute(
                        """
                        INSERT INTO credit_ledger (
                            id, user_id, brand_id, run_id, stage, operation,
                            amount_signed, balance_after, currency,
                            idempotency_key, reason, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'credits', ?, ?, ?)
                        """,
                        (
                            entry_id,
                            user_id,
                            brand_id,
                            run_id,
                            stage,
                            operation,
                            amount,
                            new_balance,
                            idempotency_key,
                            reason,
                            datetime.utcnow().isoformat(),
                        ),
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise

            return self.get_entry(entry_id)


class InsufficientCreditError(RuntimeError):
    """Fail-closed error raised BEFORE any billable provider call."""

    def __init__(self, needed: int, available: int, stage: str):
        self.needed = needed
        self.available = available
        self.stage = stage
        super().__init__(
            f"Insufficient credits for stage '{stage}': need {needed}, available {available}. "
            "Stage halted cleanly; all prior work preserved."
        )


# Shared singleton (uses the canonical autopilot.db)
ledger = CreditLedger()
