"""
MoneyPrinterTurbo Local Render Client (Layer C2).
Submits 9:16 short-form video jobs to the local MPT FastAPI server
(http://127.0.0.1:8080) and polls until the MP4 is ready.

Zero marginal cost: edge-tts voiceover, Pexels free stock footage,
local FFmpeg assembly. No new API keys, no signups, no cloud bills.
"""

import logging
import time
from pathlib import Path

import requests

from src.config import settings

logger = logging.getLogger(__name__)

DEFAULT_MPT_BASE_URL = "http://127.0.0.1:8080"


def _mpt_base_url() -> str:
    return (
        getattr(settings, "mpt_base_url", None)
        or DEFAULT_MPT_BASE_URL
    ).rstrip("/")


class MoneyPrinterTurboClient:
    """Thin synchronous wrapper over MPT's /api/v1 video endpoints."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or _mpt_base_url()).rstrip("/")

    def is_available(self, timeout: int = 5) -> bool:
        """Side-effect-free health check. False when the MPT server is down."""
        for path in ["/api/v1/tasks", "/api/v1/videos", "/"]:
            try:
                resp = requests.get(f"{self.base_url}{path}", timeout=timeout)
                if resp.status_code in (200, 404, 405):
                    # If it responds with HTTP, server is reachable
                    return True
            except Exception:
                continue
        return False

    def create_video(
        self,
        script: str,
        subject: str,
        terms: str | None = None,
        voice_name: str = "en-US-ChristopherNeural",
        aspect: str = "9:16",
    ) -> str:
        """Submits a render job. Returns the MPT task_id."""
        payload = {
            "video_subject": subject,
            "video_script": script,
            "video_terms": terms or subject,
            "video_aspect": aspect,
            "video_concat_mode": "random",
            "video_clip_duration": 5,
            "video_count": 1,
            "video_source": "pexels",
            "voice_name": voice_name,
            "voice_volume": 1.0,
            "bgm_type": "random",
            "bgm_volume": 0.15,
            "subtitle_enabled": True,
            "subtitle_position": "bottom",
        }
        # Try /api/v1/videos first, then fallback to /api/v1/tasks
        endpoints = [f"{self.base_url}/api/v1/videos", f"{self.base_url}/api/v1/tasks"]
        resp = None
        last_error = None
        for ep in endpoints:
            try:
                r = requests.post(ep, json=payload, timeout=30)
                if r.status_code == 404:
                    continue
                r.raise_for_status()
                resp = r
                break
            except Exception as e:
                last_error = e

        if resp is None:
            if last_error:
                raise last_error
            raise RuntimeError(f"MPT failed to accept render job on endpoints {endpoints}")

        body = resp.json()
        task_id = (body.get("data") or {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"MPT rejected render job: {str(body)[:300]}")
        logger.info(f"MPT render job accepted: task_id={task_id}")
        return task_id

    def get_task(self, task_id: str, timeout: int = 15) -> dict:
        """Returns the raw MPT task dict (state: 0=running, 1=done, -1=failed)."""
        resp = requests.get(f"{self.base_url}/api/v1/tasks/{task_id}", timeout=timeout)
        resp.raise_for_status()
        return (resp.json().get("data") or {}).get("task") or resp.json().get("data") or {}

    def wait_for_task(self, task_id: str, timeout_s: int = 900, poll_s: int = 10) -> dict:
        """Blocks until the task succeeds, fails, or times out. Returns final task dict."""
        start = time.time()
        while time.time() - start < timeout_s:
            task = self.get_task(task_id)
            try:
                state = int(task.get("state", 0))
            except (TypeError, ValueError):
                state = 0
            if state == 1:  # TASK_STATE_COMPLETE
                return task
            if state == -1:  # TASK_STATE_FAILED
                raise RuntimeError(
                    f"MPT render failed for {task_id}: {str(task.get('error', task.get('message', '')))[:300]}"
                )
            time.sleep(poll_s)
        raise TimeoutError(f"MPT task {task_id} did not finish within {timeout_s}s.")

    def download_video(self, video_url: str, dest: str | Path) -> str:
        """Fetches the rendered MP4 (absolute or /tasks-relative URL) to dest."""
        url = video_url if video_url.startswith("http") else f"{self.base_url}{video_url}"
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)
        logger.info(f"MPT video saved: {dest} ({dest.stat().st_size // 1024} KB)")
        return str(dest)

    def render_reel(
        self,
        script: str,
        subject: str,
        dest: str | Path,
        voice_name: str = "en-US-ChristopherNeural",
        timeout_s: int = 900,
    ) -> str:
        """One-call render: submit -> wait -> download. Returns local MP4 path."""
        task_id = self.create_video(script=script, subject=subject, voice_name=voice_name)
        task = self.wait_for_task(task_id, timeout_s=timeout_s)
        videos = task.get("videos") or (task.get("data") or {}).get("videos") or []
        if not videos:
            raise RuntimeError(f"MPT task {task_id} finished with no videos.")
        return self.download_video(videos[0], dest)

    render_video = render_reel


mpt_client = MoneyPrinterTurboClient()
