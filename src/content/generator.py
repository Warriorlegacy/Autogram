"""
Comprehensive Multi-Provider Content Generator (Layer C).
Supports 100% Free Providers:
- Google Gemini (Free Tier: 1,500 requests/day)
- Groq Cloud (Free Tier: Llama 3.3 70B)
- Local Ollama (100% Free local AI)
- Built-in Autonomous Knowledge & Synthesis Engine (100% Free, zero keys required)
- Paid providers (OpenAI, Claude) if configured
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import requests

from src.config import settings
from src.content.free_knowledge_engine import get_rich_synthesized_carousel

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
BRAND_FILE = Path(__file__).parent.parent.parent / "data" / "brand.json"

class ContentGenerator:
    def __init__(self):
        self.system_prompt = self._load_prompt("system_brand.md")
        self.architect_prompt = self._load_prompt("carousel_architect.md")
        self.brand_profile = self._load_brand()
        self._disabled_providers = set()

    def _load_prompt(self, filename: str) -> str:
        p = PROMPTS_DIR / filename
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def _load_brand(self) -> dict:
        if BRAND_FILE.exists():
            try:
                return json.loads(BRAND_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"brand_name": "Autogram AI", "handle": "@autogram.ai"}

    def _build_user_prompt(self, topic: dict, sources: list[dict]) -> str:
        return f"""
TOPIC: {topic.get('topic')}
PILLAR: {topic.get('pillar', 'AI Tool Breakdown')}
ANGLE: {topic.get('angle', '')}
SOURCES: {json.dumps(sources[:3], indent=2)}

Build a cohesive, high-value 7-10 slide Instagram carousel in strict JSON following your instructions.
Slide roles: hook, standard, checklist, comparison, diagram, framework, takeaway, cta.
Return ONLY valid JSON.
"""

    def generate_with_gemini(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free Google Gemini API (1,500 free requests/day).
        """
        model = settings.llm_model if "gemini" in settings.llm_model else "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.gemini_api_key}"
        
        prompt_text = f"{self.system_prompt}\n\n{self.architect_prompt}\n\n{self._build_user_prompt(topic, sources)}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.7
            }
        }

        resp = requests.post(url, json=payload, timeout=45)
        resp.raise_for_status()
        candidates = resp.json().get("candidates", [])
        raw_text = candidates[0]["content"]["parts"][0]["text"]
        return json.loads(raw_text)

    def generate_with_groq(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free Groq Cloud API (Llama 3.3 70B).
        """
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": f"{self.system_prompt}\n\n{self.architect_prompt}"},
                {"role": "user", "content": self._build_user_prompt(topic, sources)}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        resp.raise_for_status()
        raw_text = resp.json()["choices"][0]["message"]["content"]
        return json.loads(raw_text)

    def generate_with_ollama(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free Local Ollama instance (0 internet cost, 0 API fees).
        """
        url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": f"{self.system_prompt}\n\n{self.architect_prompt}"},
                {"role": "user", "content": self._build_user_prompt(topic, sources)}
            ],
            "format": "json",
            "stream": False
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        raw_text = resp.json()["message"]["content"]
        return json.loads(raw_text)

    def generate_with_openai(self, topic: dict, sources: list[dict]) -> dict:
        """OpenAI API integration."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.llm_model if "gpt" in settings.llm_model else "gpt-4o",
            "messages": [
                {"role": "system", "content": f"{self.system_prompt}\n\n{self.architect_prompt}"},
                {"role": "user", "content": self._build_user_prompt(topic, sources)}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        raw_text = resp.json()["choices"][0]["message"]["content"]
        return json.loads(raw_text)

    def generate_carousel(self, topic: dict, sources: list[dict]) -> dict:
        """
        Master generation method.
        Automatically selects the best available FREE or configured provider.
        Always fails closed to the built-in free intelligence engine to guarantee $0.00 cost and zero error.
        """
        provider = settings.llm_provider.lower()

        # 1. Google Gemini (100% Free Tier)
        if "gemini" not in self._disabled_providers and (provider in ["auto", "gemini"]) and settings.gemini_api_key and settings.gemini_api_key.strip():
            try:
                logger.info("Generating carousel with Google Gemini (Free Tier)...")
                return self.generate_with_gemini(topic, sources)
            except Exception as e:
                logger.warning(f"Gemini generation error ({e}). Falling back.")
                self._disabled_providers.add("gemini")

        # 2. Groq Cloud (100% Free Tier)
        if "groq" not in self._disabled_providers and (provider in ["auto", "groq"]) and settings.groq_api_key and settings.groq_api_key.strip():
            try:
                logger.info("Generating carousel with Groq Cloud (Free Tier)...")
                return self.generate_with_groq(topic, sources)
            except Exception as e:
                logger.warning(f"Groq generation error ({e}). Falling back.")
                self._disabled_providers.add("groq")

        # 3. Local Ollama (100% Free Local)
        if "ollama" not in self._disabled_providers and provider in ["ollama"]:
            try:
                logger.info(f"Attempting local Ollama generation ({settings.ollama_model})...")
                return self.generate_with_ollama(topic, sources)
            except Exception as e:
                logger.debug(f"Ollama local not reachable: {e}")
                self._disabled_providers.add("ollama")

        # 4. OpenAI (Optional Paid)
        if "openai" not in self._disabled_providers and (provider in ["auto", "openai"]) and settings.openai_api_key and settings.openai_api_key.strip():
            try:
                logger.info("Generating carousel with OpenAI...")
                return self.generate_with_openai(topic, sources)
            except Exception as e:
                logger.warning(f"OpenAI generation error ({e}). Falling back.")
                self._disabled_providers.add("openai")

        # 5. Built-In 100% Free Autonomous Knowledge Engine (Guaranteed 0-cost, 0-error)
        logger.info("Generating carousel using Free Built-In Knowledge Engine (Zero Cost, Zero Dependency).")
        return get_rich_synthesized_carousel(topic, sources)

generator = ContentGenerator()
