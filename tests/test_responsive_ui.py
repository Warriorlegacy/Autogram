import re
from pathlib import Path
import pytest
from dashboard_api import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_dashboard_html_has_mobile_responsive_elements():
    html = Path("dashboard.html").read_text(encoding="utf-8")
    assert 'id="mobile-menu-btn"' in html
    assert 'id="sidebar-backdrop"' in html
    assert 'toggleMobileSidebar' in html
    assert '@media (max-width: 960px)' in html
    assert 'margin-left: 0 !important' in html
    assert 'width: 100% !important' in html

def test_dashboard_html_no_double_api_calls():
    html = Path("dashboard.html").read_text(encoding="utf-8")
    assert "API_BASE + '/api/" not in html
    assert "API_BASE + `/api/" not in html
    assert "apiEndpoint" in html

def test_wsgi_middleware_normalizes_double_api(client):
    res = client.get("/api/api/templates")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True

    res_prompts = client.get("/api/api/prompts")
    assert res_prompts.status_code == 200
    assert res_prompts.get_json()["ok"] is True

    res_prov = client.get("/api/api/providers")
    assert res_prov.status_code == 200
    assert res_prov.get_json()["ok"] is True

    res_sched = client.get("/api/api/schedule")
    assert res_sched.status_code == 200
    assert res_sched.get_json()["ok"] is True

def test_synthesize_endpoint_exists(client):
    res = client.post("/api/content/synthesize", json={})
    assert res.status_code == 400
    assert "Topic is required" in res.get_json().get("error", "")

def test_schedule_toggle_endpoint(client):
    res = client.post("/api/scheduler/toggle", json={"enable": True})
    assert res.status_code == 200
    assert res.get_json()["ok"] is True
    assert res.get_json()["scheduler_running"] is True

    res2 = client.post("/api/scheduler/toggle", json={"enable": False})
    assert res2.status_code == 200
    assert res2.get_json()["ok"] is True
    assert res2.get_json()["scheduler_running"] is False
