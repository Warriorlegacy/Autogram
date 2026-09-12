"""
YouTube Shorts Publisher (Layer C3).
Publishes 9:16 vertical short-form videos to YouTube Shorts via the Google YouTube Data API v3.

Zero-cost execution: Uses Google Cloud's free standard quota (10,000 units/day;
~1,600 units per upload = up to 6 autonomous uploads daily at $0.00).
Supports dry-run simulation mode without requiring credentials.
"""

import json
import logging
import os
import time
import uuid
from pathlib import Path

from src.config import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeShortsPublisher:
    """Synchronous publisher for YouTube Shorts using YouTube Data API v3."""

    def __init__(self, dry_run: bool | None = None):
        self.dry_run = dry_run if dry_run is not None else settings.dry_run
        self.token_file = os.getenv("YOUTUBE_TOKEN_FILE", "youtube_token.json")
        self.secret_file = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "client_secrets.json")

    def _format_title(self, title: str) -> str:
        """Ensures title contains #Shorts and fits within YouTube's 100-character limit."""
        clean_title = title.strip()
        if "#Shorts" not in clean_title and "#shorts" not in clean_title:
            clean_title = f"{clean_title} #Shorts"
        if len(clean_title) > 100:
            clean_title = clean_title[:92].strip() + " #Shorts"
        return clean_title

    def get_credentials(self):
        """Loads or refreshes Google OAuth2 credentials."""
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = None
        # 1. Try loading from token file
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            except Exception as e:
                logger.warning(f"Failed to load credentials from {self.token_file}: {e}")

        # 2. Try loading from env variable if file doesn't exist
        raw_token_json = os.getenv("YOUTUBE_TOKEN_JSON")
        if not creds and raw_token_json:
            try:
                info = json.loads(raw_token_json)
                creds = Credentials.from_authorized_user_info(info, SCOPES)
            except Exception as e:
                logger.warning(f"Failed to parse YOUTUBE_TOKEN_JSON from env: {e}")

        # 3. Refresh expired credentials
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                if os.path.exists(self.token_file):
                    with open(self.token_file, "w") as f:
                        f.write(creds.to_json())
                logger.info("Successfully refreshed YouTube OAuth token.")
            except Exception as e:
                logger.error(f"Failed to refresh YouTube OAuth token: {e}")
                creds = None

        # 4. If credentials still not available and client_secrets.json exists, start local flow
        if not creds and os.path.exists(self.secret_file):
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(self.secret_file, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(self.token_file, "w") as f:
                    f.write(creds.to_json())
                logger.info(f"Generated and saved new YouTube credentials to {self.token_file}")
            except Exception as e:
                logger.error(f"InstalledAppFlow OAuth error: {e}")
                creds = None

        return creds

    def upload_short(
        self,
        video_path: str | Path,
        title: str,
        description: str,
        tags: list[str] | None = None,
        category_id: str = "27",
        privacy_status: str = "public",
        dry_run: bool | None = None,
    ) -> str:
        """
        Uploads a 9:16 vertical video to YouTube as a Short.
        Returns the YouTube video ID.
        """
        is_dry = dry_run if dry_run is not None else self.dry_run
        formatted_title = self._format_title(title)
        video_file = Path(video_path)

        if is_dry:
            mock_id = f"mock_yt_short_{int(time.time())}_{uuid.uuid4().hex[:6]}"
            logger.info(
                f"[DRY-RUN] YouTube Short upload simulated: title='{formatted_title}', "
                f"file='{video_file.name}', mock_video_id='{mock_id}'"
            )
            return mock_id

        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        creds = self.get_credentials()
        if not creds or not creds.valid:
            raise RuntimeError(
                f"No valid YouTube credentials found. Place '{self.token_file}' or '{self.secret_file}' "
                "in workspace root, or set YOUTUBE_TOKEN_JSON in .env."
            )

        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        logger.info(f"Initiating YouTube Short upload: '{formatted_title}'...")
        youtube = build("youtube", "v3", credentials=creds)

        video_tags = tags or ["Shorts", "Tech", "AI", "SoftwareEngineering"]
        if "Shorts" not in video_tags and "#Shorts" not in video_tags:
            video_tags.append("Shorts")

        body = {
            "snippet": {
                "title": formatted_title,
                "description": description,
                "tags": video_tags,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_file),
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024 * 5,  # 5MB chunks
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"YouTube upload progress: {progress}%")

        video_id = response.get("id")
        if not video_id:
            raise RuntimeError(f"YouTube upload failed: {response}")

        logger.info(f"YouTube Short published successfully: https://youtube.com/shorts/{video_id}")
        return video_id


youtube_publisher = YouTubeShortsPublisher()
