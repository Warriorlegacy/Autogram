"""
src/content/json2video_engine.py - JSON2Video Cloud Rendering Engine
Integrates JSON2Video API (v2) for video rendering with local fallback to VideoEngine.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

import requests
from src.config import settings

logger = logging.getLogger(__name__)


class JSON2VideoEngine:
    """
    Cloud video rendering engine backed by JSON2Video API,
    with local FFmpeg + Edge-TTS fallback.
    """

    API_BASE = "https://api.json2video.com/v2"

    def __init__(self, api_key: Optional[str] = None):
        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            self.api_key = (getattr(settings, "json2video_api_key", None) or os.getenv("JSON2VIDEO_API_KEY") or "").strip()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def compile_movie_payload(self, script: str, edit_plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compiles a JSON2Video movie payload matching vertical Instagram format.
        """
        beats = []
        if edit_plan and isinstance(edit_plan, dict) and "beats" in edit_plan:
            beats = edit_plan["beats"]
        else:
            # Generate fallback beats from sentences
            sentences = [s.strip() for s in script.split(".") if s.strip()]
            for idx, s in enumerate(sentences):
                beats.append({
                    "beat_index": idx + 1,
                    "spoken_text": s + ".",
                    "target_duration_seconds": max(3.0, len(s.split()) * 0.4)
                })

        scenes = []
        for beat in beats:
            spoken_text = beat.get("spoken_text", "").strip()
            duration = float(beat.get("target_duration_seconds", 4.0))

            scene_elements = [
                {
                    "type": "text",
                    "text": spoken_text.upper(),
                    "style": "01",
                    "position": "center",
                    "font-size": 52,
                    "font-weight": "bold",
                    "color": "#FFFFFF"
                },
                {
                    "type": "text",
                    "text": "SIGNHIFY.STUDIO",
                    "position": "bottom",
                    "font-size": 24,
                    "color": "#6366F1"
                }
            ]

            scenes.append({
                "duration": duration,
                "elements": scene_elements
            })

        return {
            "resolution": "instagram-story",
            "fps": 30,
            "scenes": scenes
        }

    def submit_render(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submits movie generation request to JSON2Video API."""
        if not self.is_configured():
            raise RuntimeError("JSON2Video API key is not configured.")

        url = f"{self.API_BASE}/movies"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"JSON2Video API error ({resp.status_code}): {resp.text}")

        data = resp.json()
        project_id = data.get("project") or data.get("project_id")
        return {"project_id": project_id, "raw_response": data}

    def poll_movie_status(
        self,
        project_id: str,
        timeout_seconds: int = 180,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """Polls for video completion."""
        url = f"{self.API_BASE}/movies"
        headers = {"x-api-key": self.api_key}
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            resp = requests.get(f"{url}?project={project_id}", headers=headers, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                movie = data.get("movie", {})
                status = movie.get("status")
                if status == "done":
                    return {
                        "status": "completed",
                        "video_url": movie.get("url"),
                        "project_id": project_id
                    }
                elif status == "error":
                    raise RuntimeError(f"JSON2Video rendering failed: {movie.get('message', 'Unknown error')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"JSON2Video rendering timed out after {timeout_seconds} seconds")

    def render_reel(
        self,
        script_text: str,
        edit_plan: Optional[Dict[str, Any]] = None,
        output_path: Optional[Union[str, Path]] = None,
        fallback_to_local: bool = True
    ) -> Dict[str, Any]:
        """
        Renders vertical reel via JSON2Video cloud or falls back to local FFmpeg/Edge-TTS.
        """
        if self.is_configured():
            try:
                payload = self.compile_movie_payload(script_text, edit_plan)
                sub_res = self.submit_render(payload)
                poll_res = self.poll_movie_status(sub_res["project_id"])

                video_url = poll_res.get("video_url")
                if output_path and video_url:
                    out = Path(output_path)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    r = requests.get(video_url, timeout=60)
                    if r.status_code == 200:
                        out.write_bytes(r.content)
                        poll_res["video_path"] = str(out)

                poll_res["provider"] = "json2video"
                return poll_res
            except Exception as e:
                logger.warning(f"JSON2Video cloud render failed ({e}); checking fallback.")
                if not fallback_to_local:
                    raise

        if fallback_to_local:
            # 1. First try HyperFrames for premium deterministic HTML/GSAP motion graphics
            try:
                from src.content.hyperframes_engine import HyperFramesEngine
                if HyperFramesEngine.is_available():
                    logger.info("Attempting local render via HyperFrames deterministic engine...")
                    hf_engine = HyperFramesEngine()
                    out_p = Path(output_path) if output_path else None
                    hf_res = hf_engine.render_reel(
                        topic=script_text[:80],
                        script_text=script_text,
                        output_path=str(out_p) if out_p else None,
                    )
                    return {
                        "provider": "hyperframes",
                        "status": "completed",
                        "video_path": hf_res["video_path"],
                        "duration_seconds": hf_res.get("duration", 20.0),
                    }
            except Exception as hf_err:
                logger.warning(f"HyperFrames local render failed ({hf_err}); trying FFmpeg VideoEngine.")

            logger.info("Falling back to local FFmpeg / Edge-TTS VideoEngine.")
            from src.content.video_engine import VideoEngine
            engine = VideoEngine()
            out_p = Path(output_path) if output_path else None
            local_res = engine.render_vertical_reel(script_text, output_path=out_p)
            return {
                "provider": "local_ffmpeg",
                "status": local_res.get("status", "completed"),
                "video_path": local_res.get("video_path"),
                "duration_seconds": local_res.get("duration_seconds", 15)
            }

        raise RuntimeError("JSON2Video is not configured and local fallback is disabled.")