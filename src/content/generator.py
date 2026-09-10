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
import os
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
        Tries active Google models: gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro.
        """
        candidate_models = []
        if settings.llm_model and "gemini" in settings.llm_model:
            candidate_models.append(settings.llm_model)
        candidate_models.extend(["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
        
        # Deduplicate while preserving order
        seen = set()
        models = [m for m in candidate_models if not (m in seen or seen.add(m))]

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

        last_err = None
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.gemini_api_key}"
            try:
                logger.info(f"Attempting Gemini generation with model: {model}...")
                resp = requests.post(url, json=payload, timeout=15)
                if resp.status_code == 200:
                    candidates = resp.json().get("candidates", [])
                    raw_text = candidates[0]["content"]["parts"][0]["text"]
                    data = json.loads(raw_text)
                    if "slides" in data and len(data["slides"]) >= 5:
                        logger.info(f"Gemini generation successful with {model} ({len(data['slides'])} slides).")
                        return data
                resp.raise_for_status()
            except Exception as e:
                last_err = e
                logger.warning(f"Gemini model '{model}' failed: {e}. Trying fallback...")
                continue
        raise last_err or RuntimeError("All Gemini models failed")

    def _parse_json_response(self, text: str) -> dict:
        """Safely extracts and parses JSON even if wrapped in markdown codeblocks or thought tags."""
        import re
        # Remove reasoning tags if model output includes <think>...</think> (e.g. DeepSeek R1)
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Try markdown codeblock ```json ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        # Try finding outer curly braces
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start:end+1])
            except Exception:
                pass

        raise ValueError(f"Failed to parse valid JSON from model response: {cleaned[:180]}...")

    def generate_with_groq(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free Groq Cloud API (14,400 req/day, sub-second LLaMA 3.3 70B & 3.1 8B).
        """
        api_key = getattr(settings, "groq_api_key", None) or os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("No GROQ_API_KEY configured")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        last_err = None
        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": f"{self.system_prompt}\n\n{self.architect_prompt}"},
                    {"role": "user", "content": self._build_user_prompt(topic, sources)}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7
            }
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    raw_text = resp.json()["choices"][0]["message"]["content"]
                    data = self._parse_json_response(raw_text)
                    if "slides" in data and len(data["slides"]) >= 5:
                        logger.info(f"Groq generation successful with {model}.")
                        return data
                resp.raise_for_status()
            except Exception as e:
                last_err = e
                logger.warning(f"Groq model '{model}' failed: {e}. Trying fallback...")
                continue
        raise last_err or RuntimeError("All Groq models failed")

    def generate_with_openrouter(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free OpenRouter Tier (Meta LLaMA 3.3 70B, DeepSeek R1, Gemini 2.0 Flash Exp, Qwen 2.5 Coder).
        """
        api_key = getattr(settings, "openrouter_api_key", None) or os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            raise ValueError("No OPENROUTER_API_KEY configured")
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://autogram-ai.vercel.app",
            "X-Title": "Autogram AI",
            "Content-Type": "application/json"
        }
        free_models = [
            "nvidia/nemotron-3.5-lightning:free",
            "google/gemma-4-31b-it:free",
            "liquid/lfm-2.5-2.6b:free",
            "google/gemma-4-26b-a4b-it:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "deepseek/deepseek-r1:free"
        ]
        last_err = None
        for model in free_models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": f"{self.system_prompt}\n\n{self.architect_prompt}\nIMPORTANT: Reply ONLY with valid JSON."},
                    {"role": "user", "content": self._build_user_prompt(topic, sources)}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7
            }
            try:
                logger.info(f"Attempting OpenRouter free model: {model}...")
                resp = requests.post(url, headers=headers, json=payload, timeout=12)
                if resp.status_code == 200:
                    raw_text = resp.json()["choices"][0]["message"]["content"]
                    data = self._parse_json_response(raw_text)
                    if "slides" in data and len(data["slides"]) >= 5:
                        logger.info(f"OpenRouter generation successful with {model}.")
                        return data
                resp.raise_for_status()
            except Exception as e:
                last_err = e
                logger.warning(f"OpenRouter model '{model}' failed: {e}. Trying next free model...")
                continue
        raise last_err or RuntimeError("All OpenRouter free models failed")

    def generate_with_cloudflare_ai(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free Cloudflare Workers AI (10,000 free Neurons/day).
        Models: @cf/meta/llama-3.1-8b-instruct, @cf/mistral/mistral-7b-instruct-v0.2, @cf/deepseek-ai/deepseek-r1-distill-qwen-32b.
        """
        token = getattr(settings, "cloudflare_api_token", None) or os.environ.get("CLOUDFLARE_API_TOKEN", "")
        account_id = getattr(settings, "cloudflare_account_id", None) or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        if not token or not account_id:
            raise ValueError("No Cloudflare credentials configured")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        models = [
            "@cf/meta/llama-3.1-8b-instruct",
            "@cf/mistral/mistral-7b-instruct-v0.2",
            "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
            "@cf/meta/llama-3.3-70b-instruct"
        ]
        last_err = None
        for model in models:
            url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
            payload = {
                "messages": [
                    {"role": "system", "content": f"{self.system_prompt}\n\n{self.architect_prompt}\nIMPORTANT: Respond with ONLY valid JSON."},
                    {"role": "user", "content": self._build_user_prompt(topic, sources)}
                ],
                "max_tokens": 2048
            }
            try:
                logger.info(f"Attempting Cloudflare Workers AI generation with {model}...")
                resp = requests.post(url, headers=headers, json=payload, timeout=18)
                if resp.status_code == 200:
                    res_json = resp.json()
                    raw_text = res_json.get("result", {}).get("response", "")
                    data = self._parse_json_response(raw_text)
                    if "slides" in data and len(data["slides"]) >= 5:
                        logger.info(f"Cloudflare Workers AI generation successful with {model}.")
                        return data
            except Exception as e:
                last_err = e
                logger.warning(f"Cloudflare model '{model}' failed: {e}. Trying fallback...")
                continue
        raise last_err or RuntimeError("All Cloudflare Workers AI models failed")

    def generate_with_nvidia_nim(self, topic: dict, sources: list[dict]) -> dict:
        """
        NVIDIA NIM API (Free developer tier: 1,000 credits).
        Models: meta/llama-3.3-70b-instruct, mistralai/mistral-large-2-instruct, deepseek-ai/deepseek-r1.
        """
        api_key = getattr(settings, "nvidia_nim_api_key", None) or os.environ.get("NVIDIA_NIM_API_KEY", "")
        if not api_key:
            raise ValueError("No NVIDIA_NIM_API_KEY configured")

        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        models = [
            "meta/llama-3.3-70b-instruct",
            "mistralai/mistral-large-2-instruct",
            "deepseek-ai/deepseek-r1"
        ]
        last_err = None
        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": f"{self.system_prompt}\n\n{self.architect_prompt}"},
                    {"role": "user", "content": self._build_user_prompt(topic, sources)}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
                "max_tokens": 2048
            }
            try:
                logger.info(f"Attempting NVIDIA NIM generation with {model}...")
                resp = requests.post(url, headers=headers, json=payload, timeout=25)
                if resp.status_code == 200:
                    raw_text = resp.json()["choices"][0]["message"]["content"]
                    data = self._parse_json_response(raw_text)
                    if "slides" in data and len(data["slides"]) >= 5:
                        logger.info(f"NVIDIA NIM generation successful with {model}.")
                        return data
            except Exception as e:
                last_err = e
                logger.warning(f"NVIDIA NIM model '{model}' failed: {e}. Trying fallback...")
                continue
        raise last_err or RuntimeError("All NVIDIA NIM models failed")

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

    def _normalize_carousel(self, data: dict, topic: dict) -> dict:
        """Ensure consistent fields, slide layout roles, and trigger_word for CTA banners."""
        if not data.get("trigger_word"):
            for s in data.get("slides", []):
                if s.get("layout") == "cta" and s.get("trigger_word"):
                    data["trigger_word"] = s["trigger_word"]
                    break
        if not data.get("trigger_word"):
            t_lower = (topic.get("topic") or "").lower()
            for cand in ["PROMPTS", "AGENCY", "OUTBOUND", "CONTENT", "STACK", "AGENTS", "DEV", "SYSTEM", "SCALE", "BLUEPRINT"]:
                if cand.lower() in t_lower:
                    data["trigger_word"] = cand
                    break
            if not data.get("trigger_word"):
                data["trigger_word"] = "SYSTEM"
        for s in data.get("slides", []):
            if s.get("layout") == "cta":
                s["trigger_word"] = data["trigger_word"]

        if not data.get("theme"):
            from renderer.render import resolve_theme
            data["theme"] = resolve_theme({"pillar": topic.get("pillar", ""), "topic": topic.get("topic", "")})

        # Automatically scrub banned marketing clichés
        banned_replacements = {
            "robust": "reliable",
            "seamless": "frictionless",
            "game-changer": "step-function shift",
            "unlock the power of": "leverage",
            "in today's fast-paced world": "in modern production",
            "dive into": "examine",
            "at its core": "fundamentally",
            "unleash": "activate",
        }
        import re
        for s in data.get("slides", []):
            for field in ["headline", "body", "proof_or_example", "meta_chips"]:
                val = s.get(field)
                if val and isinstance(val, str):
                    for banned, repl in banned_replacements.items():
                        pattern = re.compile(re.escape(banned), re.IGNORECASE)
                        s[field] = pattern.sub(repl, s[field])

        if data.get("caption") and isinstance(data["caption"], str):
            for banned, repl in banned_replacements.items():
                pattern = re.compile(re.escape(banned), re.IGNORECASE)
                data["caption"] = pattern.sub(repl, data["caption"])

        return data

    def generate_with_huggingface(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free Hugging Face Router API (Meta LLaMA 3.3 70B Instruct / Qwen 2.5 72B).
        """
        token = getattr(settings, "huggingface_api_key", None) or os.environ.get("HUGGINGFACE_API_KEY", "")
        if not token:
            raise ValueError("No HUGGINGFACE_API_KEY configured")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        models = [
            "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "meta-llama/Llama-3.1-70B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct"
        ]

        last_err = None
        for model in models:
            url = "https://router.huggingface.co/together/v1/chat/completions"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": f"{self.system_prompt}\n\n{self.architect_prompt}"},
                    {"role": "user", "content": self._build_user_prompt(topic, sources)}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7
            }
            try:
                logger.info(f"Attempting Hugging Face generation with model: {model}...")
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                if resp.status_code == 200:
                    raw_text = resp.json()["choices"][0]["message"]["content"]
                    data = json.loads(raw_text)
                    if "slides" in data and len(data["slides"]) >= 5:
                        logger.info(f"Hugging Face generation successful with {model} ({len(data['slides'])} slides).")
                        return data
                resp.raise_for_status()
            except Exception as e:
                last_err = e
                logger.warning(f"Hugging Face model '{model}' failed: {e}")
                continue
        raise last_err or RuntimeError("All Hugging Face models failed")

    def generate_carousel(self, topic: dict, sources: list[dict]) -> dict:
        """
        Master generation method with intelligent multi-provider auto-fallback.
        Priority order for 100% Free Tiers:
        1. Groq Cloud (Free Tier: 14,400 req/day, sub-second LLaMA 3.3 70B & 3.1 8B)
        2. OpenRouter (Free Tier: LLaMA 3.3 70B, DeepSeek R1, Gemini 2.0 Flash Exp)
        3. Google Gemini (Free Tier: 1,500 req/day, Gemini 2.0 Flash & 1.5 Flash)
        4. Cloudflare Workers AI (Free Tier: 10,000 Neurons/day, LLaMA 3.3 70B & DeepSeek R1 Distill)
        5. NVIDIA NIM (Free Tier Credits: LLaMA 3.3 70B, Mistral Large, DeepSeek R1)
        6. Hugging Face Router (Free Tier: LLaMA 3.3 70B Turbo)
        7. Local Ollama (Free Local)
        8. OpenAI (Optional Paid)
        9. Free Built-In Anti-Repetition Synthesis Engine (Guaranteed zero-failure fail-safe)
        """
        provider = (settings.llm_provider or "auto").lower()

        # 1. Groq Cloud (Ultra-Fast Free Tier: 14,400 req/day)
        if "groq" not in self._disabled_providers and (provider in ["auto", "groq"]) and settings.groq_api_key and settings.groq_api_key.strip():
            try:
                logger.info("Generating carousel with Groq Cloud (Free Tier: LLaMA 3.3 70B)...")
                return self._normalize_carousel(self.generate_with_groq(topic, sources), topic)
            except Exception as e:
                logger.warning(f"Groq generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("groq")

        # 2. OpenRouter (100% Free Tier: LLaMA 3.3 70B, DeepSeek R1, Gemini Exp)
        openrouter_key = getattr(settings, "openrouter_api_key", None) or os.environ.get("OPENROUTER_API_KEY", "").strip()
        if "openrouter" not in self._disabled_providers and (provider in ["auto", "openrouter"]) and openrouter_key:
            try:
                logger.info("Generating carousel with OpenRouter (Free Tier models)...")
                return self._normalize_carousel(self.generate_with_openrouter(topic, sources), topic)
            except Exception as e:
                logger.warning(f"OpenRouter generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("openrouter")

        # 3. Google Gemini (100% Free Tier: 1,500 req/day)
        if "gemini" not in self._disabled_providers and (provider in ["auto", "gemini"]) and settings.gemini_api_key and settings.gemini_api_key.strip():
            try:
                logger.info("Generating carousel with Google Gemini (Free Tier: Gemini 2.0 Flash)...")
                return self._normalize_carousel(self.generate_with_gemini(topic, sources), topic)
            except Exception as e:
                logger.warning(f"Gemini generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("gemini")

        # 4. Cloudflare Workers AI (100% Free Tier: 10,000 Neurons/day)
        cf_token = getattr(settings, "cloudflare_api_token", None) or os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
        cf_account = getattr(settings, "cloudflare_account_id", None) or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
        if "cloudflare" not in self._disabled_providers and (provider in ["auto", "cloudflare", "cf"]) and cf_token and cf_account:
            try:
                logger.info("Generating carousel with Cloudflare Workers AI (Free Tier: LLaMA 3.3 70B)...")
                return self._normalize_carousel(self.generate_with_cloudflare_ai(topic, sources), topic)
            except Exception as e:
                logger.warning(f"Cloudflare Workers AI generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("cloudflare")

        # 5. NVIDIA NIM (Free Developer Tier: 1,000 credits)
        nvidia_key = getattr(settings, "nvidia_nim_api_key", None) or os.environ.get("NVIDIA_NIM_API_KEY", "").strip()
        if "nvidia" not in self._disabled_providers and (provider in ["auto", "nvidia", "nim"]) and nvidia_key:
            try:
                logger.info("Generating carousel with NVIDIA NIM (Free Tier credits)...")
                return self._normalize_carousel(self.generate_with_nvidia_nim(topic, sources), topic)
            except Exception as e:
                logger.warning(f"NVIDIA NIM generation error ({e}). Falling back to next provider.")
                self._disabled_providers.add("nvidia")

        # 6. Hugging Face (100% Free Tier: Llama 3.3 70B Instruct)
        hf_key = getattr(settings, "huggingface_api_key", None) or os.environ.get("HUGGINGFACE_API_KEY", "").strip()
        if "huggingface" not in self._disabled_providers and (provider in ["auto", "huggingface"]) and hf_key:
            try:
                logger.info("Generating carousel with Hugging Face (Free Tier: LLaMA 3.3 70B)...")
                return self._normalize_carousel(self.generate_with_huggingface(topic, sources), topic)
            except Exception as e:
                logger.warning(f"Hugging Face generation error ({e}). Falling back to next provider.")
                self._disabled_providers.add("huggingface")

        # 7. Local Ollama (100% Free Local)
        if "ollama" not in self._disabled_providers and provider in ["ollama", "auto"]:
            try:
                logger.info(f"Attempting local Ollama generation ({settings.ollama_model})...")
                return self._normalize_carousel(self.generate_with_ollama(topic, sources), topic)
            except Exception as e:
                logger.debug(f"Ollama local not reachable: {e}")
                self._disabled_providers.add("ollama")

        # 8. OpenAI (Optional Paid)
        if "openai" not in self._disabled_providers and (provider in ["auto", "openai"]) and settings.openai_api_key and settings.openai_api_key.strip():
            try:
                logger.info("Generating carousel with OpenAI...")
                return self._normalize_carousel(self.generate_with_openai(topic, sources), topic)
            except Exception as e:
                logger.warning(f"OpenAI generation error ({e}). Falling back.")
                self._disabled_providers.add("openai")

        # 9. Built-In 100% Free Autonomous Knowledge Engine (Guaranteed 0-cost, 0-error, anti-repetition)
        logger.info("Generating carousel using Free Built-In Anti-Repetition Synthesis Engine.")
        return self._normalize_carousel(get_rich_synthesized_carousel(topic, sources), topic)

generator = ContentGenerator()
