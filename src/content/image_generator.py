"""
AI Image Generation Module for Autogram.
Generates conceptual tech artwork, 3D glass isometric icons, and visual assets.

Supported Providers:
1. Pollinations.ai (FLUX.1 [schnell]) - 100% Free, Zero API Key required, ultra-fast.
2. Google Imagen 3 (via Google AI Studio Gemini API) - Free tier.
3. OpenAI DALL-E 3 (via OpenAI API) - Paid fallback.
"""

import os
import json
import logging
import urllib.parse
from datetime import datetime
from pathlib import Path
import requests

from src.config import settings

logger = logging.getLogger(__name__)

IMAGE_DIR = Path(__file__).parent.parent.parent / "output" / "generated_images"

# Style presets for high-end B2B tech aesthetics
STYLE_PRESETS = {
    "cyber-minimalist": "ultra-clean dark obsidian aesthetic, subtle cyan and indigo ambient rim lighting, minimalist 3D glass isometric elements, high tech, Octane render 8K, no text, no watermark",
    "3d-isometric": "3D isometric modular architecture, frosted glass nodes, glowing telemetry lines, deep space navy background, photorealistic 8K, no text, no typography",
    "photorealistic-dark": "cinematic dark studio lighting, sleek brushed aluminum and frosted acrylic, subtle depth of field, 8K editorial tech photography, no text",
    "conceptual-ai": "abstract neural cluster, luminous data streams, optical glass prism refraction, dark matte finish, 8K octane render, no text"
}

class ImageGenerator:
    def __init__(self):
        self.provider = getattr(settings, "image_provider", "pollinations").lower()
        self.default_style = getattr(settings, "image_style", "cyber-minimalist")
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    def _enhance_prompt(self, prompt: str, style_preset: str | None = None) -> str:
        """Enriches the user prompt with aesthetic guardrails to prevent low-quality outputs."""
        style = STYLE_PRESETS.get(style_preset or self.default_style, STYLE_PRESETS["cyber-minimalist"])
        return f"{prompt}, {style}"

    def generate_with_pollinations(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1080,
        seed: int | None = None,
        style_preset: str | None = None,
        output_path: Path | str | None = None
    ) -> Path:
        """
        100% Free Image Generation via Pollinations (FLUX.1 [schnell]).
        No API key required, zero recurring cost, fast generation.
        """
        enhanced = self._enhance_prompt(prompt, style_preset)
        encoded_prompt = urllib.parse.quote(enhanced)
        
        # Pollinations Flux endpoint
        seed_param = f"&seed={seed}" if seed is not None else ""
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true{seed_param}"

        logger.info(f"Generating image via Pollinations (FLUX.1): '{prompt[:60]}...'")
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        if output_path:
            filepath = Path(output_path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
        else:
            filename = f"flux_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{abs(hash(prompt)) % 10000}.jpg"
            filepath = IMAGE_DIR / filename

        filepath.write_bytes(resp.content)

        logger.info(f"Successfully generated image: {filepath.name} ({len(resp.content)} bytes)")
        return filepath

    def generate_with_imagen(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1080,
        style_preset: str | None = None
    ) -> Path:
        """
        Google Imagen 3 via Gemini API (Google AI Studio Free Tier).
        """
        if not settings.gemini_api_key or not settings.gemini_api_key.strip():
            logger.warning("No GEMINI_API_KEY found. Falling back to Pollinations FLUX.1.")
            return self.generate_with_pollinations(prompt, width, height, style_preset=style_preset)

        enhanced = self._enhance_prompt(prompt, style_preset)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={settings.gemini_api_key}"
        
        payload = {
            "instances": [{"prompt": enhanced}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1" if width == height else "4:5"
            }
        }

        logger.info("Generating image via Google Imagen 3...")
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()

        import base64
        predictions = resp.json().get("predictions", [])
        if not predictions:
            raise RuntimeError("Imagen returned empty predictions list.")

        b64_data = predictions[0].get("bytesBase64Encoded")
        img_bytes = base64.b64decode(b64_data)

        filename = f"imagen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{abs(hash(prompt)) % 10000}.jpg"
        filepath = IMAGE_DIR / filename
        filepath.write_bytes(img_bytes)

        logger.info(f"Successfully generated image with Imagen 3: {filepath.name}")
        return filepath

    def generate_with_dalle(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style_preset: str | None = None
    ) -> Path:
        """OpenAI DALL-E 3 (Paid)."""
        if not settings.openai_api_key or not settings.openai_api_key.strip():
            logger.warning("No OPENAI_API_KEY found. Falling back to Pollinations FLUX.1.")
            return self.generate_with_pollinations(prompt, width, height, style_preset=style_preset)

        enhanced = self._enhance_prompt(prompt, style_preset)
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        size_str = "1024x1024" if width == height else "1024x1792"
        payload = {
            "model": "dall-e-3",
            "prompt": enhanced,
            "n": 1,
            "size": size_str,
            "quality": "standard"
        }

        logger.info("Generating image via OpenAI DALL-E 3...")
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        img_url = resp.json()["data"][0]["url"]
        img_resp = requests.get(img_url, timeout=30)
        img_resp.raise_for_status()

        filename = f"dalle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{abs(hash(prompt)) % 10000}.jpg"
        filepath = IMAGE_DIR / filename
        filepath.write_bytes(img_resp.content)

        logger.info(f"Successfully generated image with DALL-E 3: {filepath.name}")
        return filepath

    def generate_with_cloudflare(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1080,
        style_preset: str | None = None,
        output_path: Path | str | None = None
    ) -> Path:
        """
        100% Free Cloudflare Workers AI (FLUX.1-schnell).
        10,000 free Neurons/day.
        """
        token = getattr(settings, "cloudflare_api_token", None) or os.environ.get("CLOUDFLARE_API_TOKEN", "")
        account_id = getattr(settings, "cloudflare_account_id", None) or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        if not token or not account_id:
            logger.warning("No Cloudflare credentials configured. Falling back to Pollinations.")
            return self.generate_with_pollinations(prompt, width, height, style_preset=style_preset, output_path=output_path)

        enhanced = self._enhance_prompt(prompt, style_preset)
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"prompt": enhanced, "steps": 4}

        logger.info(f"Generating image via Cloudflare Workers AI (FLUX.1): '{prompt[:60]}...'")
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        import base64
        data = resp.json()
        img_b64 = data.get("result", {}).get("image")
        if not img_b64:
            raise RuntimeError("Cloudflare did not return image data")

        img_bytes = base64.b64decode(img_b64)
        if output_path:
            filepath = Path(output_path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
        else:
            filename = f"cf_flux_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{abs(hash(prompt)) % 10000}.jpg"
            filepath = IMAGE_DIR / filename

        filepath.write_bytes(img_bytes)
        logger.info(f"Successfully generated image with Cloudflare Workers AI: {filepath.name} ({len(img_bytes)} bytes)")
        return filepath

    def generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1080,
        provider: str | None = None,
        style_preset: str | None = None,
        output_path: Path | str | None = None
    ) -> Path:
        """
        Master Image Generation dispatcher.
        Order: Cloudflare Workers AI / Pollinations (FLUX.1) -> Imagen 3 -> DALL-E.
        Guarantees $0.00 cost and zero downtime.
        """
        prov = (provider or self.provider or "pollinations").lower()

        if prov in ["cloudflare", "cf"] or (prov == "auto" and settings.cloudflare_api_token and settings.cloudflare_account_id):
            try:
                return self.generate_with_cloudflare(prompt, width, height, style_preset=style_preset, output_path=output_path)
            except Exception as e:
                logger.warning(f"Cloudflare image generation failed ({e}), falling back to Pollinations FLUX.1.")

        if prov in ["imagen", "google"]:
            try:
                return self.generate_with_imagen(prompt, width, height, style_preset=style_preset)
            except Exception as e:
                logger.warning(f"Imagen generation failed ({e}), falling back to Pollinations FLUX.1.")

        if prov in ["dalle", "openai"]:
            try:
                return self.generate_with_dalle(prompt, width, height, style_preset=style_preset)
            except Exception as e:
                logger.warning(f"DALL-E generation failed ({e}), falling back to Pollinations FLUX.1.")

        # Default free & reliable provider
        try:
            return self.generate_with_pollinations(
                prompt,
                width=width,
                height=height,
                style_preset=style_preset,
                output_path=output_path
            )
        except Exception as e:
            if settings.cloudflare_api_token and settings.cloudflare_account_id:
                logger.info("Pollinations unavailable, falling back to Cloudflare Workers AI.")
                return self.generate_with_cloudflare(prompt, width, height, style_preset=style_preset, output_path=output_path)
            raise e

image_generator = ImageGenerator()
