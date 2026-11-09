"""Guard against retired Groq model names.

Groq 404s on retired models, which silently burns a whole generation slot
before the fallback chain rescues it. This test hits the live /models endpoint
when a key is present, and always asserts the retired names are gone from source.
"""
import re

import pytest

from src.content import llm_models

# Retired 2026-10-09; requesting them returns 404 model_not_found.
RETIRED = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "qwen/qwen3.6-27b"]

SOURCE_FILES = [
    "src/content/generator.py",
    "src/content/script60.py",
    "src/content/providers_manager.py",
    "src/research/pattern_analyzer.py",
]


@pytest.mark.parametrize("bad", RETIRED)
def test_retired_models_absent_from_source(bad):
    """No source file may hardcode a retired Groq model."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent
    hits = []
    for rel in SOURCE_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        if bad in text:
            hits.append(rel)
    assert not hits, f"retired Groq model '{bad}' still referenced in {hits}"


def test_model_list_is_ordered_and_unique():
    assert llm_models.GROQ_MODELS
    assert len(llm_models.GROQ_MODELS) == len(set(llm_models.GROQ_MODELS))
    assert llm_models.GROQ_DEFAULT_MODEL == llm_models.GROQ_MODELS[0]
    assert llm_models.GROQ_FAST_MODEL in llm_models.GROQ_MODELS


def test_groq_models_exist_live():
    """Live check: every configured model must be offered by Groq. Skipped without a key."""
    import os

    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        try:
            import pathlib
            env = pathlib.Path(__file__).resolve().parent.parent / ".env"
            if env.exists():
                m = re.search(r"^GROQ_API_KEY=(.*)$", env.read_text(encoding="utf-8"), re.M)
                key = m.group(1).strip() if m else ""
        except Exception:
            key = ""
    if not key:
        pytest.skip("no GROQ_API_KEY available")

    import requests
    r = requests.get("https://api.groq.com/openai/v1/models",
                     headers={"Authorization": f"Bearer {key}"}, timeout=30)
    if r.status_code != 200:
        pytest.skip(f"groq /models unavailable (HTTP {r.status_code})")
    live = {m["id"] for m in r.json().get("data", [])}
    missing = [m for m in llm_models.GROQ_MODELS if m not in live]
    assert not missing, (f"Groq no longer offers {missing}. "
                         f"Update src/content/llm_models.py. Live: {sorted(live)}")


def test_reasoning_models_get_token_headroom():
    """gpt-oss burns tokens on reasoning; a small budget returns empty content."""
    assert llm_models.GROQ_MAX_TOKENS >= 2048
