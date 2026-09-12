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
        dossier = topic.get("dossier", {})
        dossier_section = ""
        if dossier:
            dossier_section = f"""
VERIFIED DEEP RESEARCH FACTS:
- Tool / Topic: {dossier.get('topic')}
- Replaces SaaS: {dossier.get('replaces_saas')} (SaaS Cost: {dossier.get('saas_cost_estimate')}) vs FOSS: {dossier.get('foss_cost')}
- GitHub Stars: {dossier.get('stars', 0):,}
- Software License: {dossier.get('license')}
- Exact 1-Line Setup Command: `{dossier.get('deployment_command')}`
- Tech Stack / Architecture: {dossier.get('architecture_stack')}
- Honest Gotchas & Trade-offs: {json.dumps(dossier.get('honest_tradeoffs', []))}
- Research Evidence: {json.dumps(dossier.get('research_evidence', []))}
"""
        return f"""
TOPIC: {topic.get('topic')}
PILLAR: {topic.get('pillar', 'FOSS SaaS Alternatives')}
ANGLE: {topic.get('angle', '')}
{dossier_section}
SOURCES: {json.dumps(sources[:4], indent=2)}

Build an exceptionally cohesive, save-worthy 7-10 slide (default 8 slides) Instagram carousel in strict JSON.
Slide roles: hook, standard, checklist, comparison, diagram, framework, takeaway, cta.
Embed the verified deep research facts (real stars, exact docker setup command, real SaaS contrast).
Return ONLY valid JSON.
"""

    def generate_with_gemini(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free Google Gemini API (1,500 free requests/day).
        Tries active Google models: gemini-2.5-flash, gemini-flash-latest, gemini-pro-latest.
        """
        candidate_models = []
        if settings.llm_model and "gemini" in settings.llm_model:
            candidate_models.append(settings.llm_model)
        candidate_models.extend(["gemini-2.5-flash", "gemini-flash-latest", "gemini-pro-latest"])
        
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
                resp = requests.post(url, json=payload, timeout=40)
                if resp.status_code == 200:
                    candidates = resp.json().get("candidates", [])
                    raw_text = candidates[0]["content"]["parts"][0]["text"]
                    data = json.loads(raw_text)
                    if "slides" in data and len(data["slides"]) >= 5:
                        logger.info(f"Gemini generation successful with {model} ({len(data['slides'])} slides).")
                        return data
                if resp.status_code == 429:
                    logger.warning(f"Gemini quota exhausted (HTTP 429) for model '{model}'. Aborting Gemini to trigger instant failover.")
                    raise RuntimeError(f"Gemini quota exhausted (429): {resp.text[:120]}")
                resp.raise_for_status()
            except Exception as e:
                last_err = e
                logger.warning(f"Gemini model '{model}' failed: {e}. Trying fallback...")
                if "429" in str(e):
                    break
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
        models = [
            "openai/gpt-oss-120b",
            "qwen/qwen3.6-27b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
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
                if resp.status_code in (401, 403):
                    logger.warning(f"Groq authentication failed (HTTP {resp.status_code}): Invalid or expired GROQ_API_KEY. Aborting Groq for immediate failover.")
                    raise ValueError(f"Groq API key unauthorized (HTTP {resp.status_code})")
                resp.raise_for_status()
            except Exception as e:
                last_err = e
                logger.warning(f"Groq model '{model}' failed: {e}. Trying fallback...")
                if "unauthorized" in str(e).lower() or "401" in str(e):
                    break
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
            "liquid/lfm-2.5-2.6b:free",
            "nex-agi/nex-n2.5-mini:free",
            "nvidia/nemotron-3.5-lightning:free",
            "inclusionai/ling-3.0-flash-vl:free"
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
                resp = requests.post(url, headers=headers, json=payload, timeout=(3, 7))
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

    def generate_with_github_models(self, topic: dict, sources: list[dict]) -> dict:
        """
        100% Free GitHub Models / Copilot API Tier (GPT-4o, Llama 3.1 70B, Mistral Large).
        Uses GITHUB_COPILOT_TOKEN or GITHUB_TOKEN on https://models.inference.ai.azure.com.
        """
        token = (
            getattr(settings, "github_copilot_token", None)
            or os.environ.get("GITHUB_COPILOT_TOKEN")
            or os.environ.get("GH_COPILOT_TOKEN")
            or os.environ.get("COPILOT_TOKEN")
            or os.environ.get("GITHUB_TOKEN", "")
        )
        if not token:
            raise ValueError("No GITHUB_COPILOT_TOKEN or GITHUB_TOKEN configured")

        url = "https://models.inference.ai.azure.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        models = [
            "gpt-4o",
            "gpt-4o-mini",
            "Meta-Llama-3.1-70B-Instruct",
            "Mistral-large-2407"
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
                "temperature": 0.7
            }
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    raw_text = resp.json()["choices"][0]["message"]["content"]
                    data = self._parse_json_response(raw_text)
                    if "slides" in data and len(data["slides"]) >= 5:
                        logger.info(f"GitHub Models generation successful with {model}.")
                        return data
                if resp.status_code in (401, 403):
                    logger.warning(f"GitHub token unauthorized (HTTP {resp.status_code}).")
                    raise ValueError(f"GitHub Models unauthorized (HTTP {resp.status_code})")
                resp.raise_for_status()
            except Exception as e:
                last_err = e
                logger.warning(f"GitHub Models '{model}' failed: {e}. Trying next...")
                if "unauthorized" in str(e).lower() or "401" in str(e):
                    break
                continue
        raise last_err or RuntimeError("All GitHub Models failed")

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
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    res_json = resp.json()
                    res_obj = res_json.get("result", {})
                    raw_text = res_obj.get("response", "") if isinstance(res_obj, dict) else ""
                    if not raw_text and isinstance(res_obj, dict) and "choices" in res_obj and res_obj["choices"]:
                        raw_text = res_obj["choices"][0].get("message", {}).get("content", "")
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
            for cand in ["FOSS", "DOCKER", "BLUEPRINT", "STACK", "DEV", "SYSTEM", "SCALE"]:
                if cand.lower() in t_lower:
                    data["trigger_word"] = cand
                    break
            if not data.get("trigger_word"):
                data["trigger_word"] = "FOSS"
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
            "revolutionary tool": "production tool",
            "next-gen ai": "modern AI",
            "ultimate secret": "core mechanism",
            "must-have app": "key tool",
            "stands as a testament to": "demonstrates",
            "in conclusion": "summary",
            "it's important to note": "note that"
        }
        import re
        patterns = [(re.compile(r'\b' + re.escape(banned) + r'\b', re.IGNORECASE), repl) for banned, repl in banned_replacements.items()]

        def _scrub(val):
            if isinstance(val, str):
                for pat, repl in patterns:
                    val = pat.sub(repl, val)
                return val
            elif isinstance(val, list):
                return [_scrub(x) for x in val]
            elif isinstance(val, dict):
                return {k: _scrub(v) for k, v in val.items()}
            return val

        data = _scrub(data)
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
        model_str = (settings.llm_model or "").lower()

        # Check if Gemini is specifically requested or configured as primary model
        prefer_gemini = "gemini" in model_str or provider == "gemini"
        if prefer_gemini and "gemini" not in self._disabled_providers and settings.gemini_api_key and settings.gemini_api_key.strip():
            try:
                logger.info("Generating carousel with Google Gemini (configured model)...")
                return self._normalize_carousel(self.generate_with_gemini(topic, sources), topic)
            except Exception as e:
                logger.warning(f"Gemini generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("gemini")

        # 1. Groq Cloud (Ultra-Fast Free Tier: 14,400 req/day)
        if "groq" not in self._disabled_providers and (provider in ["auto", "groq"]) and settings.groq_api_key and settings.groq_api_key.strip():
            try:
                logger.info("Generating carousel with Groq Cloud (Free Tier: LLaMA 3.3 70B)...")
                return self._normalize_carousel(self.generate_with_groq(topic, sources), topic)
            except Exception as e:
                logger.warning(f"Groq generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("groq")

        # 2. Google Gemini (100% Free Tier: 1,500 req/day)
        if "gemini" not in self._disabled_providers and (provider in ["auto", "gemini"]) and settings.gemini_api_key and settings.gemini_api_key.strip():
            try:
                logger.info("Generating carousel with Google Gemini (Free Tier: Gemini 2.0 Flash)...")
                return self._normalize_carousel(self.generate_with_gemini(topic, sources), topic)
            except Exception as e:
                logger.warning(f"Gemini generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("gemini")

        # 2.5. GitHub Models / Copilot (100% Free Tier: GPT-4o, Llama 3.1 70B)
        github_token = (
            getattr(settings, "github_copilot_token", None)
            or os.environ.get("GITHUB_COPILOT_TOKEN")
            or os.environ.get("GH_COPILOT_TOKEN")
            or os.environ.get("COPILOT_TOKEN")
            or os.environ.get("GITHUB_TOKEN", "").strip()
        )
        if "github_models" not in self._disabled_providers and (provider in ["auto", "github_models", "copilot"]) and github_token:
            try:
                logger.info("Generating carousel with GitHub Models / Copilot (Free GPT-4o)...")
                return self._normalize_carousel(self.generate_with_github_models(topic, sources), topic)
            except Exception as e:
                logger.warning(f"GitHub Models generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("github_models")

        # 3. Cloudflare Workers AI (100% Free Tier: 10,000 Neurons/day)
        cf_token = getattr(settings, "cloudflare_api_token", None) or os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
        cf_account = getattr(settings, "cloudflare_account_id", None) or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
        if "cloudflare" not in self._disabled_providers and (provider in ["auto", "cloudflare", "cf"]) and cf_token and cf_account:
            try:
                logger.info("Generating carousel with Cloudflare Workers AI (Free Tier: LLaMA 3.1 8B)...")
                return self._normalize_carousel(self.generate_with_cloudflare_ai(topic, sources), topic)
            except Exception as e:
                logger.warning(f"Cloudflare Workers AI generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("cloudflare")

        # 4. OpenRouter (100% Free Tier: LLaMA 3.3 70B, DeepSeek R1, Gemini Exp)
        openrouter_key = getattr(settings, "openrouter_api_key", None) or os.environ.get("OPENROUTER_API_KEY", "").strip()
        if "openrouter" not in self._disabled_providers and (provider in ["auto", "openrouter"]) and openrouter_key:
            try:
                logger.info("Generating carousel with OpenRouter (Free Tier models)...")
                return self._normalize_carousel(self.generate_with_openrouter(topic, sources), topic)
            except Exception as e:
                logger.warning(f"OpenRouter generation error ({e}). Falling back to next free provider.")
                self._disabled_providers.add("openrouter")

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

    def _free_narration(self, prompt: str) -> dict | None:
        """Best-effort narration JSON via $0 providers (github_models -> groq -> gemini -> ollama)."""
        # 0. GitHub Models / Copilot ($0, high-quality GPT-4o / Llama 3.1)
        copilot_token = (
            getattr(settings, "github_copilot_token", None)
            or os.environ.get("GITHUB_COPILOT_TOKEN")
            or os.environ.get("GH_COPILOT_TOKEN")
            or os.environ.get("COPILOT_TOKEN")
            or os.environ.get("GITHUB_TOKEN", "")
        )
        if copilot_token and "github_models" not in self._disabled_providers:
            try:
                resp = requests.post(
                    "https://models.inference.ai.azure.com/chat/completions",
                    headers={"Authorization": f"Bearer {copilot_token}", "Content-Type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "Return ONLY valid JSON."},
                            {"role": "user", "content": prompt},
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.7,
                    },
                    timeout=30,
                )
                if resp.status_code == 200:
                    return self._parse_json_response(resp.json()["choices"][0]["message"]["content"])
            except Exception as e:
                logger.warning(f"Reel narration via GitHub Models failed ({e}). Trying fallback...")

        # 1. Groq free tier (OpenAI-compatible chat completions)
        groq_key = getattr(settings, "groq_api_key", None) or os.environ.get("GROQ_API_KEY", "")
        if groq_key and "groq" not in self._disabled_providers:
            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {"role": "system", "content": "Return ONLY valid JSON."},
                            {"role": "user", "content": prompt},
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.7,
                    },
                    timeout=30,
                )
                if resp.status_code == 200:
                    return self._parse_json_response(resp.json()["choices"][0]["message"]["content"])
            except Exception as e:
                logger.warning(f"Reel narration via Groq failed ({e}). Trying fallback...")
        # 2. Gemini free tier
        gemini_key = getattr(settings, "gemini_api_key", None) or ""
        if gemini_key and "gemini" not in self._disabled_providers:
            try:
                resp = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"response_mime_type": "application/json", "temperature": 0.7},
                    },
                    timeout=40,
                )
                if resp.status_code == 200:
                    raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_json_response(raw)
            except Exception as e:
                logger.warning(f"Reel narration via Gemini failed ({e}). Trying fallback...")
        # 3. Local Ollama ($0, offline-capable)
        if "ollama" not in self._disabled_providers:
            try:
                resp = requests.post(
                    f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                    json={
                        "model": settings.ollama_model,
                        "messages": [
                            {"role": "system", "content": "Return ONLY valid JSON."},
                            {"role": "user", "content": prompt},
                        ],
                        "format": "json",
                        "stream": False,
                    },
                    timeout=120,
                )
                if resp.status_code == 200:
                    return self._parse_json_response(resp.json()["message"]["content"])
            except Exception as e:
                logger.warning(f"Reel narration via Ollama failed ({e}). Using template fallback...")
        return None

    def generate_reel_script(self, topic: str | dict, pillar: str | None = None, dossier: dict | None = None) -> dict:
        """
        Synthesizes a 45-55s spoken Reel narration + caption + hashtags.
        $0 chain: groq -> gemini -> ollama -> deterministic template (never fails).
        """
        if isinstance(topic, dict):
            topic_str = topic.get("topic", "")
            pillar_str = pillar or topic.get("pillar", "AI Tool Breakdown")
            dossier = dossier or topic.get("dossier", {})
        else:
            topic_str = str(topic)
            pillar_str = pillar or "AI Tool Breakdown"
            dossier = dossier or {}

        stat = f"{dossier.get('stars', 42000):,} GitHub stars" if dossier.get("stars") else f"replaces {dossier.get('saas_cost_estimate', '$200/mo')} SaaS at $0"
        prompt = (
            "Write a 45-55 second Instagram Reels voiceover script (110-130 spoken words, punchy, "
            "no stage directions, no emojis) plus an IG caption and 8 hashtags. "
            f"Topic: {topic_str}. Pillar: {pillar_str}. Proof point: {stat}. "
            'Return ONLY JSON: {"narration": "...", "caption": "...", "hashtags": ["#..", ...]}'
        )
        data = self._free_narration(prompt) or {}
        narration = str(data.get("narration") or "").strip()
        if not narration:
            narration = (
                f"Stop paying for bloated SaaS. {topic_str} gives you the same power for zero dollars. "
                f"Proof: {stat}. Self-host in one command, own your data, scale without a bill. "
                f"Comment REEL and I will send the full setup blueprint to your DMs. Follow for daily free AI stacks."
            )
        caption = str(data.get("caption") or f"{topic_str}: the $0 self-hosted blueprint. Comment REEL for the setup.").strip()
        hashtags = data.get("hashtags") or ["#BuildInPublic", "#OpenSource", "#SelfHosted", "#AIEngineering", "#DevTools", "#IndieHacker", "#TechReels", "#SignhifyStudio"]
        return {
            "topic": topic_str,
            "pillar": pillar_str,
            "narration": narration,
            "caption": caption,
            "hashtags": hashtags if isinstance(hashtags, list) else [str(hashtags)],
            "subject": " ".join(topic_str.split()[:4]),
        }

    def generate_story_content(self, topic: str | dict, pillar: str | None = None, dossier: dict | None = None) -> dict:
        """
        Synthesizes high-impact Instagram Story content (headline, badge, metric, takeaways, CTA)
        optimized for vertical 9:16 mobile consumption.
        """
        if isinstance(topic, dict):
            topic_str = topic.get("topic", "")
            pillar_str = pillar or topic.get("pillar", "AI & Systems Architecture")
            dossier = dossier or topic.get("dossier", {})
        else:
            topic_str = str(topic)
            pillar_str = pillar or "AI & Systems Architecture"
            dossier = dossier or {}

        pillar_badges = {
            "AI Tool Breakdown": "AI STACK BREAKDOWN",
            "Prompting & Workflow": "WORKFLOW HACK",
            "Tech Explainer": "SYSTEMS BLUEPRINT",
            "Marketing Psychology": "GROWTH ENGINE",
            "Career & Skills": "ENGINEER PULSE",
            "Contrarian": "CONTRARIAN SIGNAL",
            "Local AI & Edge Compute": "LOCAL AI DROP",
            "Trending GitHub Spotlight": "GITHUB RADAR"
        }
        badge = pillar_badges.get(pillar_str, "HIGH SIGNAL DROP")

        metric_val = "10x"
        metric_lbl = "Operational Efficiency vs Monolithic Prompts"
        code_cmd = ""
        takeaways = []

        if dossier:
            if dossier.get("stars"):
                metric_val = f"{dossier.get('stars', 0):,}★"
                metric_lbl = f"GitHub Stars · {dossier.get('license', 'FOSS')}"
            elif dossier.get("saas_cost_estimate"):
                metric_val = "$0/mo"
                metric_lbl = f"Self-Hosted vs {dossier.get('replaces_saas', 'Cloud')} ({dossier.get('saas_cost_estimate')})"

            if dossier.get("deployment_command"):
                code_cmd = dossier.get("deployment_command")

            evidence = dossier.get("research_evidence", [])
            for ev in evidence[:3]:
                takeaways.append({"bold": "Architecture", "text": ev})

        if not takeaways:
            takeaways = [
                {"bold": "Modular Isolation", "text": "Separates deep context from reasoning boundaries to eliminate hallucinations."},
                {"bold": "Zero-Touch Scaling", "text": "Deterministic state machines replace fragile, monolithic mega-prompts."},
                {"bold": "Production Ready", "text": "Tested and verified across long-horizon autonomous workflows."}
            ]

        headline = topic_str.strip().rstrip(".")

        return {
            "topic": topic_str,
            "pillar": pillar_str,
            "headline": headline,
            "badge": badge,
            "metric_value": metric_val,
            "metric_label": metric_lbl,
            "takeaways": takeaways,
            "code_command": code_cmd,
            "cta_text": "Tap Link in Bio for Full Architecture Blueprint",
            "publication_date": datetime.now().strftime("%Y-%m-%d")
        }

generator = ContentGenerator()
