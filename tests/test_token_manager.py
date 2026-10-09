"""Tests for src/instagram/token_manager.py (token validation + 60-day refresh)."""
import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.instagram import token_manager as tm


class FakeHTTPError(requests.HTTPError):
    """HTTPError carrying a Meta-style JSON error body, like requests raises."""

    def __init__(self, code, subcode=0):
        super().__init__(f"{code}")
        self.response = MagicMock()
        self.response.json.return_value = {
            "error": {"code": code, "error_subcode": subcode, "message": "boom"}}


def test_is_revoked_error_detects_190_and_463():
    assert tm.is_revoked_error(FakeHTTPError(190, 460))
    assert tm.is_revoked_error(FakeHTTPError(463))
    # Transient/server errors must NOT trigger a refresh.
    assert not tm.is_revoked_error(FakeHTTPError(500))
    assert not tm.is_revoked_error(FakeHTTPError(400, 100))
    assert not tm.is_revoked_error(ValueError("no response attribute"))


def test_token_reads_env_at_call_time(monkeypatch):
    """Regression: token was snapshotted at import, so a refreshed token was invisible."""
    manager = tm.TokenManager()
    monkeypatch.setenv("IG_ACCESS_TOKEN", "from-env")
    assert manager.token == "from-env"
    monkeypatch.delenv("IG_ACCESS_TOKEN")
    assert manager.token != "from-env"


def test_validate_token_true_on_200():
    manager = tm.TokenManager()
    resp = MagicMock(status_code=200)
    with patch.object(tm.requests, "get", return_value=resp):
        assert manager.validate_token("good") is True


def test_validate_token_false_on_error_and_never_raises():
    manager = tm.TokenManager()
    with patch.object(tm.requests, "get", return_value=MagicMock(status_code=400)):
        assert manager.validate_token("bad") is False
    with patch.object(tm.requests, "get", side_effect=requests.RequestException("net")):
        assert manager.validate_token("bad") is False
    assert manager.validate_token(None) is False


def test_refresh_requires_app_credentials(monkeypatch):
    manager = tm.TokenManager()
    monkeypatch.setenv("IG_ACCESS_TOKEN", "tok")
    monkeypatch.delenv("META_APP_ID", raising=False)
    monkeypatch.delenv("META_APP_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="META_APP_ID"):
        manager.refresh_token()


def test_refresh_exchanges_token_and_returns_new(monkeypatch):
    manager = tm.TokenManager()
    monkeypatch.setenv("IG_ACCESS_TOKEN", "old")
    monkeypatch.setenv("META_APP_ID", "appid")
    monkeypatch.setenv("META_APP_SECRET", "appsecret")
    resp = MagicMock()
    resp.json.return_value = {"access_token": "new", "expires_in": 5184000}
    with patch.object(tm.requests, "get", return_value=resp) as get:
        data = manager.refresh_token()
    assert data["access_token"] == "new"
    params = get.call_args.kwargs["params"]
    assert params["grant_type"] == "fb_exchange_token"
    assert params["fb_exchange_token"] == "old"
    assert params["client_id"] == "appid"


def test_refresh_raises_when_response_has_no_token(monkeypatch):
    manager = tm.TokenManager()
    monkeypatch.setenv("IG_ACCESS_TOKEN", "old")
    monkeypatch.setenv("META_APP_ID", "appid")
    monkeypatch.setenv("META_APP_SECRET", "appsecret")
    resp = MagicMock()
    resp.json.return_value = {"error": {"message": "nope"}}
    with patch.object(tm.requests, "get", return_value=resp):
        with pytest.raises(RuntimeError, match="no access_token"):
            manager.refresh_token()


def test_ensure_valid_returns_same_token_when_healthy(monkeypatch):
    manager = tm.TokenManager()
    monkeypatch.setenv("IG_ACCESS_TOKEN", "healthy")
    with patch.object(manager, "validate_token", return_value=True):
        assert manager.ensure_valid() == "healthy"


def test_ensure_valid_refreshes_and_updates_environment(monkeypatch):
    """A dead token must be swapped in os.environ so the publisher sees it."""
    manager = tm.TokenManager()
    monkeypatch.setenv("IG_ACCESS_TOKEN", "dead")
    monkeypatch.setattr(manager, "validate_token", lambda tok=None: False)
    monkeypatch.setattr(manager, "refresh_token",
                        lambda: {"access_token": "renewed", "expires_in": 5184000})
    try:
        assert manager.ensure_valid() == "renewed"
        assert os.environ["IG_ACCESS_TOKEN"] == "renewed"
    finally:
        os.environ.pop("IG_ACCESS_TOKEN", None)


def test_ensure_valid_survives_failed_refresh(monkeypatch):
    """Never raise out of ensure_valid - a dead token must not crash the slot early."""
    manager = tm.TokenManager()
    monkeypatch.setenv("IG_ACCESS_TOKEN", "dead")

    def boom():
        raise RuntimeError("cannot refresh")

    monkeypatch.setattr(manager, "validate_token", lambda tok=None: False)
    monkeypatch.setattr(manager, "refresh_token", boom)
    try:
        assert manager.ensure_valid() == "dead"
    finally:
        os.environ.pop("IG_ACCESS_TOKEN", None)


def test_ensure_valid_noop_without_token(monkeypatch):
    manager = tm.TokenManager()
    monkeypatch.delenv("IG_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(tm.settings, "ig_access_token", None, raising=False)
    assert manager.ensure_valid() is None
