"""
Meta Instagram Token Management.
Handles auto-refreshing 60-day long-lived access tokens to ensure zero-touch persistence.
"""

import logging
import os

import requests

from src.config import settings

logger = logging.getLogger(__name__)

DEFAULT_GRAPH_HOST = os.environ.get("META_GRAPH_HOST", "https://graph.facebook.com")

# Error codes that mean "this token is dead, get a new one" rather than
# "retry later": 190/460 = session invalidated (password change / security
# revocation), 463 = session expired.
REVOKED_ERROR_CODES = {190, 463}


def is_revoked_error(exc: Exception) -> bool:
    """True if `exc` is a Meta OAuth failure caused by a dead token.

    Used to decide between "retry the same token" and "refresh then retry".
    """
    resp = getattr(exc, "response", None)
    if resp is None:
        return False
    try:
        code = resp.json().get("error", {}).get("code")
    except (ValueError, AttributeError):
        return False
    return code in REVOKED_ERROR_CODES


class TokenManager:
    def __init__(self, host: str | None = None):
        self.graph_host = host or os.environ.get("META_GRAPH_HOST", DEFAULT_GRAPH_HOST)

    @property
    def token(self) -> str | None:
        """Read at call time, not import time.

        pydantic-settings snapshots os.environ once at construction, so a token
        swapped in by ensure_valid() (or exported later in a workflow step) is
        invisible to an attribute captured during module import.
        """
        return os.environ.get("IG_ACCESS_TOKEN") or settings.ig_access_token

    def _app_credentials(self) -> tuple[str, str] | None:
        app_id = os.environ.get("META_APP_ID", "")
        app_secret = os.environ.get("META_APP_SECRET", "")
        if app_id and app_secret:
            return app_id, app_secret
        return None

    def validate_token(self, token: str | None = None) -> bool:
        """Read-only probe of the current token. Never raises."""
        token = token or self.token
        if not token:
            return False
        ver = settings.meta_api_version
        user_id = settings.ig_user_id or "me"
        try:
            resp = requests.get(
                f"{self.graph_host}/{ver}/{user_id}",
                params={"fields": "id", "access_token": token},
                timeout=15,
            )
            return resp.status_code == 200
        except requests.RequestException as e:
            logger.warning(f"token validation request failed: {e}")
            return False

    def refresh_token(self) -> dict:
        """
        Extends the current long-lived Meta token by another 60 days.

        Requires META_APP_ID + META_APP_SECRET; without them we cannot exchange,
        and the caller must mint a token by hand.
        """
        token = self.token
        if not token or settings.dry_run:
            logger.info("[DRY-RUN] Instagram token refresh simulated (60-day extension granted).")
            return {"access_token": "mock_refreshed_token", "token_type": "bearer",
                    "expires_in": 5184000}

        creds = self._app_credentials()
        if not creds:
            raise RuntimeError(
                "Cannot refresh: META_APP_ID and META_APP_SECRET are not set. "
                "Mint a token manually (see AUTOGRAM_CONFIGURATION_GUIDE.md section 4)."
            )
        app_id, app_secret = creds

        # Try Instagram refresh endpoint first if host is graph.instagram.com
        if "instagram.com" in self.graph_host:
            url = f"{self.graph_host}/refresh_access_token"
            params = {"grant_type": "ig_refresh_token", "access_token": token}
        else:
            # Facebook Graph API token exchange
            url = f"{self.graph_host}/{settings.meta_api_version}/oauth/access_token"
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": token,
            }

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            new_token = data.get("access_token")
            if not new_token:
                raise RuntimeError(f"refresh response contained no access_token: {data}")
            expires_in = data.get("expires_in", 5184000)
            logger.info(f"Successfully refreshed Instagram token! Valid for {expires_in // 86400} days.")
            return data
        except Exception as e:
            logger.error(f"Failed to refresh Instagram token: {e}")
            raise

    def ensure_valid(self) -> str | None:
        """Return a working token, extending it first if it is dead.

        Propagates the new token back into os.environ so every downstream
        consumer (publisher, token_manager.token) sees it. Callers must run this
        before constructing a publisher, because InstagramPublisher snapshots
        settings at __init__.
        """
        token = self.token
        if not token or settings.dry_run:
            return token

        if self.validate_token(token):
            return token

        logger.warning("Instagram token is invalid; attempting 60-day refresh.")
        try:
            data = self.refresh_token()
        except Exception as e:
            logger.error(f"Automatic refresh failed: {e}")
            return token

        new_token = data.get("access_token")
        if new_token and new_token != "mock_refreshed_token":
            os.environ["IG_ACCESS_TOKEN"] = new_token
            settings.ig_access_token = new_token
            logger.info("Applied refreshed token to the environment.")
            return new_token
        return token


token_manager = TokenManager()
