"""
Universal AI Providers and Dynamic Model Detection Hub.
Allows connecting any AI provider (preset or custom OpenAI-compatible endpoint),
auto-detecting models from that endpoint, and managing Image/Video generation engines.
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROVIDERS_FILE = BASE_DIR / "data" / "ai_providers.json"

DEFAULT_PROVIDERS = {
    "active_text_provider": "gemini",
    "active_text_model": "gemini-2.5-flash",
    "active_image_provider": "flux_free",
    "active_image_model": "black-forest-labs/FLUX.1-schnell",
    "active_video_provider": "luma",
    "active_video_model": "dream-machine",
    "custom_providers": [],
    "presets": {
        "openai": {
            "name": "OpenAI",
            "base_url": "https://api.openai.com/v1",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "gpt-4o-mini",
            "models": ["gpt-4o", "gpt-4o-mini", "o3-mini", "gpt-4-turbo"]
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "base_url": "https://api.anthropic.com/v1",
            "auth_header": "x-api-key",
            "auth_prefix": "",
            "default_model": "claude-3-5-sonnet-20241022",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
        },
        "gemini": {
            "name": "Google Gemini",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "gemini-2.5-flash",
            "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"]
        },
        "groq": {
            "name": "Groq Cloud (Fast)",
            "base_url": "https://api.groq.com/openai/v1",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "llama-3.3-70b-versatile",
            "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
        },
        "deepseek": {
            "name": "DeepSeek",
            "base_url": "https://api.deepseek.com/v1",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "deepseek-chat",
            "models": ["deepseek-chat", "deepseek-reasoner"]
        },
        "mistral": {
            "name": "Mistral AI",
            "base_url": "https://api.mistral.ai/v1",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "mistral-large-latest",
            "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest"]
        },
        "together": {
            "name": "Together AI",
            "base_url": "https://api.together.xyz/v1",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-R1", "Qwen/Qwen2.5-72B-Instruct-Turbo"]
        },
        "openrouter": {
            "name": "OpenRouter (Universal Router)",
            "base_url": "https://openrouter.ai/api/v1",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "meta-llama/llama-3.3-70b-instruct:free",
            "models": [
                "meta-llama/llama-3.3-70b-instruct:free",
                "deepseek/deepseek-r1:free",
                "google/gemini-2.0-flash-exp:free",
                "qwen/qwen-2.5-72b-instruct:free"
            ]
        },
        "perplexity": {
            "name": "Perplexity Sonar",
            "base_url": "https://api.perplexity.ai",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "sonar",
            "models": ["sonar", "sonar-pro", "sonar-reasoning"]
        },
        "ollama": {
            "name": "Local Ollama (Offline)",
            "base_url": "http://localhost:11434/v1",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "llama3.2",
            "models": ["llama3.2", "llama3.1:8b", "mistral", "deepseek-r1:8b", "qwen2.5:7b"]
        },
        "lmstudio": {
            "name": "LM Studio (Local)",
            "base_url": "http://localhost:1234/v1",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
            "default_model": "local-model",
            "models": ["local-model"]
        }
    },
    "image_models": [
        {"id": "flux_free", "name": "FLUX.1 Schnell ($0 Free)", "provider": "HuggingFace / Together", "model_id": "black-forest-labs/FLUX.1-schnell"},
        {"id": "dall_e_3", "name": "DALL-E 3 HD", "provider": "OpenAI", "model_id": "dall-e-3"},
        {"id": "sd3", "name": "Stable Diffusion 3.5", "provider": "Stability AI", "model_id": "sd3-medium"},
        {"id": "imagen3", "name": "Google Imagen 3", "provider": "Google Cloud", "model_id": "imagen-3.0-generate-001"},
        {"id": "midjourney_proxy", "name": "Midjourney v6.1 (API Proxy)", "provider": "Custom Proxy", "model_id": "mj-v6"}
    ],
    "video_models": [
        {"id": "luma", "name": "Luma Dream Machine", "provider": "Luma AI", "model_id": "dream-machine-v1"},
        {"id": "runway", "name": "Runway Gen-3 Alpha", "provider": "Runway ML", "model_id": "gen3a_turbo"},
        {"id": "kling", "name": "Kling AI 1.5", "provider": "Kuaishou Kling", "model_id": "kling-v1.5"},
        {"id": "pika", "name": "Pika 2.0", "provider": "Pika Labs", "model_id": "pika-v2"}
    ]
}

PROVIDER_PRESETS = DEFAULT_PROVIDERS["presets"]
IMAGE_MODELS = DEFAULT_PROVIDERS["image_models"]
VIDEO_MODELS = DEFAULT_PROVIDERS["video_models"]


class ProvidersManager:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not PROVIDERS_FILE.exists():
            PROVIDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
            PROVIDERS_FILE.write_text(json.dumps(DEFAULT_PROVIDERS, indent=2), encoding="utf-8")

    def load_config(self) -> Dict[str, Any]:
        self._ensure_file()
        try:
            return json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return DEFAULT_PROVIDERS

    def save_config(self, cfg: Dict[str, Any]):
        PROVIDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROVIDERS_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    def get_all_providers(self) -> Dict[str, Any]:
        cfg = self.load_config()
        return {
            "active_text_provider": cfg.get("active_text_provider", "gemini"),
            "active_text_model": cfg.get("active_text_model", "gemini-2.5-flash"),
            "active_image_provider": cfg.get("active_image_provider", "flux_free"),
            "active_image_model": cfg.get("active_image_model", "black-forest-labs/FLUX.1-schnell"),
            "active_video_provider": cfg.get("active_video_provider", "luma"),
            "active_video_model": cfg.get("active_video_model", "dream-machine"),
            "presets": cfg.get("presets", DEFAULT_PROVIDERS["presets"]),
            "custom_providers": cfg.get("custom_providers", []),
            "image_models": cfg.get("image_models", DEFAULT_PROVIDERS["image_models"]),
            "video_models": cfg.get("video_models", DEFAULT_PROVIDERS["video_models"])
        }

    def add_or_update_custom_provider(self, provider_id: str, name: str, base_url: str, api_key: str, default_model: Optional[str] = None, models: Optional[List[str]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Save a new or existing custom AI endpoint."""
        cfg = self.load_config()
        customs = cfg.get("custom_providers", [])
        
        # Clean URL
        base_url = base_url.strip().rstrip("/")
        if not base_url.startswith("http"):
            base_url = "https://" + base_url

        provider_entry = {
            "id": provider_id.strip().lower(),
            "name": name.strip(),
            "base_url": base_url,
            "api_key": api_key.strip(),
            "default_model": default_model.strip() if default_model else (models[0] if models else "default-model"),
            "models": models or [default_model or "default-model"],
            "headers": headers or {}
        }

        # Replace existing or append
        existing_idx = next((i for i, p in enumerate(customs) if p["id"] == provider_entry["id"]), None)
        if existing_idx is not None:
            customs[existing_idx] = provider_entry
        else:
            customs.append(provider_entry)

        cfg["custom_providers"] = customs
        self.save_config(cfg)
        return {"ok": True, "provider": provider_entry}

    def set_active_text_model(self, provider_id: str, model_id: str):
        cfg = self.load_config()
        cfg["active_text_provider"] = provider_id
        cfg["active_text_model"] = model_id
        self.save_config(cfg)

    def set_active_image_model(self, provider_id: str, model_id: str):
        cfg = self.load_config()
        cfg["active_image_provider"] = provider_id
        cfg["active_image_model"] = model_id
        self.save_config(cfg)

    def set_active_video_model(self, provider_id: str, model_id: str):
        cfg = self.load_config()
        cfg["active_video_provider"] = provider_id
        cfg["active_video_model"] = model_id
        self.save_config(cfg)

    def detect_models_from_endpoint(self, base_url: str, api_key: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Dynamically probe the given endpoint to auto-detect supported models.
        Supports standard OpenAI /v1/models, Ollama /api/tags, and custom proxies.
        """
        base_url = base_url.strip().rstrip("/")
        if not base_url.startswith("http"):
            base_url = "https://" + base_url

        req_headers = {"User-Agent": "Autogram/2.5 AI Engine"}
        if api_key and api_key.strip():
            req_headers["Authorization"] = f"Bearer {api_key.strip()}"
        if headers:
            req_headers.update(headers)

        detected_models = []
        errors = []

        # Probe 1: Standard OpenAI /models endpoint
        endpoints_to_try = [
            f"{base_url}/models",
            f"{base_url}/v1/models" if not base_url.endswith("/v1") else f"{base_url}/models",
            f"{base_url}/api/tags"  # Ollama native
        ]

        success = False
        for ep in endpoints_to_try:
            try:
                resp = requests.get(ep, headers=req_headers, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    # 1. OpenAI schema: {"data": [{"id": "..."}, ...]}
                    if "data" in data and isinstance(data["data"], list):
                        for item in data["data"]:
                            m_id = item.get("id") or item.get("name")
                            if m_id and m_id not in detected_models:
                                detected_models.append(str(m_id))
                        success = True
                        break
                    # 2. Ollama schema: {"models": [{"name": "..."}, ...]}
                    elif "models" in data and isinstance(data["models"], list):
                        for item in data["models"]:
                            m_id = item.get("name") or item.get("model")
                            if m_id and m_id not in detected_models:
                                detected_models.append(str(m_id))
                        success = True
                        break
                    # 3. Direct list schema: [{"id": "..."}, ...]
                    elif isinstance(data, list):
                        for item in data:
                            m_id = item.get("id") if isinstance(item, dict) else str(item)
                            if m_id and m_id not in detected_models:
                                detected_models.append(str(m_id))
                        success = True
                        break
            except Exception as e:
                errors.append(f"{ep}: {e}")

        if not success or not detected_models:
            return {
                "ok": False,
                "error": f"Could not auto-detect models from {base_url}. Verify endpoint URL and API key.",
                "details": errors
            }

        # Sort and filter clean names
        detected_models.sort()
        return {
            "ok": True,
            "endpoint": base_url,
            "total_models": len(detected_models),
            "models": detected_models
        }


providers_manager = ProvidersManager()
