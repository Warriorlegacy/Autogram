"""
tests/test_api_v2_runs.py - Verification for Dashboard API v2 Makerzz Endpoints
Validates listing runs, initializing runs, stepping phases, approving stages, and reading the credit ledger.
"""

import pytest
import json
from dashboard_api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_v2_list_runs(client):
    res = client.get("/api/v2/runs")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "runs" in data


def test_api_v2_create_and_step_run(client):
    brief_payload = {
        "brand": "Signhify Studio",
        "niche": "Autonomous social media engines for AI founders",
        "audience": "Software founders and solopreneurs",
        "voice": {"tone": "authoritative"},
        "platforms": ["instagram", "linkedin"],
        "include_video": False,
        "mode": "auto"
    }

    create_res = client.post("/api/v2/runs/new", json={"brief": brief_payload})
    assert create_res.status_code in (200, 201)
    create_data = create_res.get_json()
    assert create_data["ok"] is True
    run_id = create_data["run_id"]
    assert run_id is not None

    # Step through P1
    step_res = client.post(f"/api/v2/runs/{run_id}/step")
    assert step_res.status_code == 200
    step_data = step_res.get_json()
    assert step_data["ok"] is True
    assert step_data["phase"] == "P1_SCAN"

    # List artifacts
    art_res = client.get(f"/api/v2/runs/{run_id}/artifacts")
    assert art_res.status_code == 200
    art_data = art_res.get_json()
    assert any((a == "brief.json" if isinstance(a, str) else a.get("name") == "brief.json") for a in art_data["artifacts"])


def test_api_v2_ledger(client):
    res = client.get("/api/v2/ledger?brand_id=signhify&user_id=test_user")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "balance" in data
    assert "history" in data
