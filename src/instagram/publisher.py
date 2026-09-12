"""
Meta Instagram Content Publishing API Client (Layer D).
Implements the official container-based carousel publishing flow.
Includes mock/dry-run mode for zero-error local testing.
"""

import logging
import time
import requests
import os
from src.config import settings

logger = logging.getLogger(__name__)

DEFAULT_GRAPH_HOST = os.environ.get("META_GRAPH_HOST", "https://graph.facebook.com")

class InstagramPublisher:
    def __init__(self, host: str | None = None, dry_run: bool | None = None):
        self.user_id = settings.ig_user_id
        self.token = settings.ig_access_token
        self.version = settings.meta_api_version
        self.graph_host = host or os.environ.get("META_GRAPH_HOST", DEFAULT_GRAPH_HOST)
        self.base_url = f"{self.graph_host}/{self.version}"
        self._forced_dry_run: bool | None = dry_run

    @property
    def dry_run(self) -> bool:
        """Evaluated lazily so CLI --dry-run flag propagates after module import."""
        if self._forced_dry_run is not None:
            return self._forced_dry_run
        return settings.dry_run or not (self.user_id and self.token)

    @dry_run.setter
    def dry_run(self, value: bool):
        self._forced_dry_run = value

    def check_publishing_limit(self) -> dict:
        """Inspects current 24-hour publishing usage."""
        if self.dry_run:
            return {"quota_usage": 1, "config": {"quota_total": 50}}

        url = f"{self.base_url}/{self.user_id}/content_publishing_limit"
        params = {"access_token": self.token}
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [{}])[0]

    def create_item_container(self, image_url: str, alt_text: str = "") -> str:
        """Creates a single carousel item media container."""
        if self.dry_run:
            simulated_id = f"mock_child_cntr_{int(time.time()*1000) % 1000000}"
            logger.info(f"[DRY-RUN] Created item container: {simulated_id} for URL: {image_url}")
            return simulated_id

        if not (image_url.startswith("http://") or image_url.startswith("https://")):
            raise ValueError(f"Invalid image_url '{image_url}': Meta Graph API strictly requires an absolute public HTTP/HTTPS URL, not a relative path or local file.")

        url = f"{self.base_url}/{self.user_id}/media"
        data = {
            "image_url": image_url,
            "media_type": "IMAGE",
            "is_carousel_item": True,
            "access_token": self.token
        }
        if alt_text:
            data["alt_text"] = alt_text

        resp = requests.post(url, data=data, timeout=30)
        if resp.status_code != 200:
            logger.error(f"Meta Graph API error in create_item_container: {resp.status_code} - {resp.text}")
        resp.raise_for_status()
        return resp.json()["id"]

    def wait_until_ready(self, container_id: str, timeout_s: int = 180) -> bool:
        """Polls container status until FINISHED or timeout."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Container {container_id} status: FINISHED (simulated)")
            return True

        start_time = time.time()
        while time.time() - start_time < timeout_s:
            url = f"{self.base_url}/{container_id}"
            params = {
                "fields": "status_code,status",
                "access_token": self.token
            }
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status_code")
                if status == "FINISHED":
                    return True
                elif status in ["ERROR", "EXPIRED"]:
                    raise RuntimeError(f"Container {container_id} failed with status: {status}")
            time.sleep(5)

        raise TimeoutError(f"Container {container_id} did not finish within {timeout_s}s.")

    def create_carousel_container(self, child_container_ids: list[str], caption: str) -> str:
        """Creates the parent carousel container referencing children."""
        if self.dry_run:
            simulated_carousel_id = f"mock_carousel_cntr_{int(time.time()*1000) % 1000000}"
            logger.info(f"[DRY-RUN] Created carousel container: {simulated_carousel_id} with {len(child_container_ids)} slides")
            return simulated_carousel_id

        url = f"{self.base_url}/{self.user_id}/media"
        data = {
            "media_type": "CAROUSEL",
            "children": ",".join(child_container_ids),
            "caption": caption,
            "is_ai_generated": "true",
            "access_token": self.token
        }
        resp = requests.post(url, data=data, timeout=30)
        if resp.status_code != 200 and "is_ai_generated" in data:
            logger.warning(f"Meta returned {resp.status_code} with is_ai_generated, retrying without it: {resp.text}")
            data.pop("is_ai_generated", None)
            resp = requests.post(url, data=data, timeout=30)
        resp.raise_for_status()
        return resp.json()["id"]

    def publish_media(self, creation_id: str) -> str:
        """Publishes the finished carousel container to the live Instagram feed."""
        if self.dry_run:
            simulated_media_id = f"mock_published_media_{int(time.time()*1000) % 1000000}"
            logger.info(f"[DRY-RUN] Successfully published carousel! Media ID: {simulated_media_id}")
            return simulated_media_id

        url = f"{self.base_url}/{self.user_id}/media_publish"
        data = {
            "creation_id": creation_id,
            "access_token": self.token
        }
        resp = requests.post(url, data=data, timeout=30)
        resp.raise_for_status()
        media_id = resp.json().get("id")
        logger.info(f"Published carousel to Instagram live feed: Media ID = {media_id}")
        return media_id

    def publish_carousel(self, image_urls: list[str], alt_texts: list[str], caption: str) -> str:
        """End-to-end carousel publishing flow."""
        logger.info(f"Starting Instagram publish sequence for {len(image_urls)} slides...")

        # Ensure caption and hashtags are ALWAYS present while posting
        caption = (caption or "").strip()
        if not caption:
            logger.warning("No caption provided to publish_carousel; generating default viral caption & hashtags...")
            try:
                from src.growth.viral_engine import viral_engine
                default_meta = viral_engine.generate_default_caption("AI Automation Systems Architecture", "AI Tool Breakdown")
                caption = default_meta["caption"]
            except Exception:
                tags = "#AIEngineering #AutogramAI #AIAutomation #AgenticAI #BuildInPublic #SystemDesign #SignhifyStudio"
                caption = (
                    "New AI Automation Systems Breakdown.\n\n"
                    "👉 Swipe through all slides to see the exact implementation blueprint.\n\n"
                    "📌 Save this post before your next architecture sprint.\n"
                    "🚀 Follow @signhify.studio for battle-tested AI automation & systems design.\n\n"
                    "— My name is Piyush. Stop posting. Start shipping.\n\n"
                    ".\n.\n"
                    f"{tags}"
                )
        elif "#" not in caption:
            logger.info("Caption missing hashtags; dynamically generating and appending viral hashtag cluster...")
            try:
                from src.growth.viral_engine import viral_engine
                tags = " ".join(viral_engine.build_viral_hashtags("AI Tool Breakdown"))
            except Exception:
                tags = "#AIEngineering #AutogramAI #AIAutomation #AgenticAI #BuildInPublic #SystemDesign #SignhifyStudio"
            caption = f"{caption}\n\n.\n.\n{tags}"

        hashtag_count = caption.count("#")
        logger.info(f"Verified post caption: {len(caption)} characters with {hashtag_count} hashtags attached.")

        # 1. Child containers
        child_ids = []
        for i, url in enumerate(image_urls):
            alt = alt_texts[i] if i < len(alt_texts) else ""
            cid = self.create_item_container(url, alt)
            self.wait_until_ready(cid)
            child_ids.append(cid)

        # 2. Parent carousel container
        carousel_id = self.create_carousel_container(child_ids, caption)
        self.wait_until_ready(carousel_id)

        # 3. Publish
        media_id = self.publish_media(carousel_id)
        return media_id

    def create_story_container(self, image_url: str) -> str:
        """Creates an Instagram Story media container (9:16 aspect ratio, media_type=STORIES)."""
        if self.dry_run:
            simulated_id = f"mock_story_cntr_{int(time.time()*1000) % 1000000}"
            logger.info(f"[DRY-RUN] Created story container: {simulated_id} for URL: {image_url}")
            return simulated_id

        if not (image_url.startswith("http://") or image_url.startswith("https://")):
            raise ValueError(
                f"Invalid image_url '{image_url}': Meta Graph API strictly requires an absolute public HTTP/HTTPS URL."
            )

        url = f"{self.base_url}/{self.user_id}/media"
        data = {
            "image_url": image_url,
            "media_type": "STORIES",
            "access_token": self.token
        }
        resp = requests.post(url, data=data, timeout=30)
        if resp.status_code != 200:
            logger.error(f"Meta Graph API error in create_story_container: {resp.status_code} - {resp.text}")
        resp.raise_for_status()
        return resp.json()["id"]

    def publish_story(self, image_url: str) -> str:
        """End-to-end single Instagram Story publishing flow."""
        logger.info(f"Starting Instagram Story publish sequence for {image_url}...")
        container_id = self.create_story_container(image_url)
        self.wait_until_ready(container_id)
        media_id = self.publish_media(container_id)
        logger.info(f"Published Instagram Story successfully! Media ID: {media_id}")
        return media_id

    def post_comment(self, media_id: str, message: str) -> str:
        """Posts a first discussion comment to the published media object."""
        if self.dry_run or str(media_id).startswith("mock"):
            logger.info(f"[DRY-RUN] Simulated posting comment to {media_id}")
            return f"mock_comment_{int(time.time()*1000) % 1000000}"

        url = f"{self.base_url}/{media_id}/comments"
        data = {
            "message": message,
            "access_token": self.token
        }
        resp = requests.post(url, data=data, timeout=20)
        resp.raise_for_status()
        comment_id = resp.json().get("id")
        logger.info(f"Published first comment to Instagram post {media_id}: Comment ID = {comment_id}")
        return comment_id

publisher = InstagramPublisher()
