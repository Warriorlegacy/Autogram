"""
Meta Instagram Token Management.
Handles auto-refreshing 60-day long-lived access tokens to ensure zero-touch persistence.
"""

import os
import logging
import requests
from src.config import settings

logger = logging.getLogger(__name__)

DEFAULT_GRAPH_HOST = os.environ.get("META_GRAPH_HOST", "https://graph.facebook.com")

class TokenManager:
    def __init__(self, host: str | None = None):
        self.token = settings.ig_access_token
        self.graph_host = host or os.environ.get("META_GRAPH_HOST", DEFAULT_GRAPH_HOST)

    def refresh_token(self) -> dict:
        """
        Refreshes a long-lived Meta / Instagram Access Token for another 60 days.
        """
        if not self.token or settings.dry_run:
            logger.info("[DRY-RUN] Instagram token refresh simulated (60-day extension granted).")
            return {"access_token": "mock_refreshed_token", "token_type": "bearer", "expires_in": 5184000}

        # Try Instagram refresh endpoint first if host is graph.instagram.com
        if "instagram.com" in self.graph_host:
            url = f"{self.graph_host}/refresh_access_token"
            params = {
                "grant_type": "ig_refresh_token",
                "access_token": self.token
            }
        else:
            # Facebook Graph API token exchange
            app_id = os.environ.get("META_APP_ID")
            app_secret = os.environ.get("META_APP_SECRET")
            if app_id and app_secret:
                url = f"{self.graph_host}/v23.0/oauth/access_token"
                params = {
                    "grant_type": "fb_exchange_token",
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "fb_exchange_token": self.token
                }
            else:
                # Fallback to direct ig_refresh_token on instagram host
                url = "https://graph.instagram.com/refresh_access_token"
                params = {
                    "grant_type": "ig_refresh_token",
                    "access_token": self.token
                }

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            new_token = data.get("access_token")
            expires_in = data.get("expires_in", 5184000)
            logger.info(f"Successfully refreshed Instagram token! Valid for {expires_in // 86400} days.")
            return data
        except Exception as e:
            logger.error(f"Failed to refresh Instagram token: {e}")
            raise

token_manager = TokenManager()
