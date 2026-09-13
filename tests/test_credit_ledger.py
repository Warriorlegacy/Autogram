"""
Tests for the append-only credit ledger (Makerzz Part IV / P8).

Validates:
  - atomic balance calculation & append-only immutability
  - idempotent charging (no double-spend on retries)
  - owner VIP bypass
  - fail-closed insufficient-credit behavior
  - refunds are new compensating entries (originals never mutated)
  - concurrent workers cannot race the same balance
"""

import threading
import pytest

from src.billing.credit_ledger import CreditLedger, InsufficientCreditError


@pytest.fixture
def ledger(tmp_path) -> CreditLedger:
    ld = CreditLedger(db_path=tmp_path / "ledger_test.db")
    return ld


def test_initial_balance_is_zero(ledger):
    assert ledger.get_balance("user_a") == 0


def test_top_up_and_charge_flow(ledger):
    ledger.top_up("user_a", 100, reason="plan grant")
    assert ledger.get_balance("user_a") == 100

    entry = ledger.charge(
        user_id="user_a",
        stage="P1_SCAN",
        operation="scan",
        idempotency_key="u1:run1:P1_SCAN:charge",
    )
    assert entry["amount_signed"] == -40  # scan costs 40
    assert entry["balance_after"] == 60
    assert ledger.get_balance("user_a") == 60


def test_insufficient_credits_fail_closed(ledger):
    ledger.top_up("user_b", 10)
    with pytest.raises(InsufficientCreditError):
        ledger.charge(
            user_id="user_b",
            stage="P1_SCAN",
            operation="scan",
            idempotency_key="u2:run1:P1_SCAN:charge",
        )
    # Balance untouched — no partial charge
    assert ledger.get_balance("user_b") == 10


def test_idempotent_charge_never_double_spends(ledger):
    ledger.top_up("user_c", 100)
    key = "u3:run1:P3_SCRIPT:charge"
    e1 = ledger.charge(user_id="user_c", stage="P3_SCRIPT", operation="script", idempotency_key=key)
    e2 = ledger.charge(user_id="user_c", stage="P3_SCRIPT", operation="script", idempotency_key=key)
    assert e1["id"] == e2["id"], "same idempotency key must return the original entry"
    assert ledger.get_balance("user_c") == 100 - 12  # script costs 12, charged once


def test_ledger_is_append_only(ledger):
    ledger.top_up("user_d", 50)
    entry = ledger.charge(
        user_id="user_d", stage="P5_EDIT_PLAN", operation="edit_plan",
        idempotency_key="u4:run1:P5:charge",
    )
    original = dict(entry)

    # Even a refund does not mutate the original
    ledger.refund("user_d", original["id"], reason="stage failed")
    after = ledger.get_entry(original["id"])
    assert after["amount_signed"] == original["amount_signed"]
    assert after["balance_after"] == original["balance_after"]
    assert after["id"] == original["id"]


def test_refund_creates_compensating_entry(ledger):
    ledger.top_up("user_e", 40)
    entry = ledger.charge(
        user_id="user_e", stage="P1_SCAN", operation="scan",
        idempotency_key="u5:run1:P1:charge",
    )
    assert ledger.get_balance("user_e") == 0

    refund = ledger.refund("user_e", entry["id"], reason="scan failed")
    assert refund["amount_signed"] == 40
    assert ledger.get_balance("user_e") == 40
    # Original still intact (append-only)
    assert ledger.get_entry(entry["id"])["amount_signed"] == -40


def test_owner_vip_unlimited_credits(ledger):
    from src.config import settings
    owner_id = settings.autogram_owner_key
    # No top-up at all — owner can still charge anything
    entry = ledger.charge(
        user_id=owner_id, stage="P4_VIDEO", operation="video_1080p_60s",
        idempotency_key="owner:run1:P4:charge", amount=202,
    )
    assert entry["balance_after"] >= 202
    assert ledger.is_owner(owner_id) is True
    assert ledger.is_owner("random_client") is False


def test_zero_cost_publishing_unmetered(ledger):
    from src.billing.credit_ledger import CREDIT_COSTS
    assert CREDIT_COSTS["publish"] == 0


def test_concurrent_charges_cannot_race(ledger):
    """Two concurrent workers must not both spend the same balance below zero."""
    ledger.top_up("user_f", 50)
    results = []
    errors = []

    def worker(key_suffix):
        try:
            entry = ledger.charge(
                user_id="user_f", stage="P1_SCAN", operation="scan",
                idempotency_key=f"u6:run1:P1:charge:{key_suffix}",
            )
            results.append(entry)
        except InsufficientCreditError:
            errors.append("insufficient")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # 50 credits / 40 cost = exactly one charge can succeed
    assert len(results) == 1
    assert len(errors) == 3
    assert ledger.get_balance("user_f") == 10


def test_standard_cost_table_matches_spec(ledger):
    from src.billing.credit_ledger import CREDIT_COSTS
    assert CREDIT_COSTS["scan"] == 40
    assert CREDIT_COSTS["script"] == 12
    assert CREDIT_COSTS["edit_plan"] == 20
    assert CREDIT_COSTS["carousel_prompts"] == 30
    assert CREDIT_COSTS["slide_low"] == 3
    assert CREDIT_COSTS["video_1080p_60s"] == 202
    assert CREDIT_COSTS["publish"] == 0
