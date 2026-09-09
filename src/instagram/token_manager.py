"""
Meta Instagram Token Management.
Handles auto-refreshing 60-day long-lived access tokens to ensure zero-touch persistence.
"""

import logging
import requests
from src.config import settings

logger = logging.getLogger(__name__)

GRAPH_HOST = "https://graph.instagram.com"

class TokenManager:
    def __init__(self):
        self.token = settings.ig_access_token

    def refresh_token(self) -> dict:
        """
        Refreshes a long-lived Instagram User Access Token for another 60 days.
        Endpoint: GET https://graph.instagram.com/refresh_access_token
        """
        if not self.token or settings.dry_run:
            logger.info("[DRY-RUN] Instagram token refresh simulated (60-day extension granted).")
            return {"access_token": "mock_refreshed_token", "token_type": "bearer", "expires_in": 5184000}

        url = f"{GRAPH_HOST}/refresh_access_token"
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": self.token
        }

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            new_token = data.get("access_token")
            expires_in = data.get("expires_in")
            logger.info(f"Successfully refreshed Instagram token! Valid for {expires_in // 86400} days.")
            return data
        except Exception as e:
            logger.error(f"Failed to refresh Instagram token: {e}")
            raise

token_manager = TokenManager()
