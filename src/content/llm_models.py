"""Single source of truth for Groq model names.

Groq retires models without notice, and a stale name fails with HTTP 404
model_not_found - which silently burns a whole generation slot before the
fallback chain kicks in. Keep the lists here so there is one place to update,
and so tests can assert them against the live /models endpoint.

Verified 2026-10-09 against Groq for this account. `llama-3.3-70b-versatile`
and `llama-3.1-8b-instant` were both retired; requesting them 404s.
"""

# Ordered by preference: cheapest/most reliable first for JSON work.
GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]

# Small/fast tier for narration and short JSON completions.
GROQ_FAST_MODEL = "qwen/qwen3.8-27b"

# gpt-oss is a reasoning model: it burns tokens on a "reasoning" field before
# emitting content. With the default budget the content field comes back empty
# and the caller sees a blank completion rather than an error.
GROQ_MAX_TOKENS = 4096

# Default when a caller just needs "some Groq model".
GROQ_DEFAULT_MODEL = GROQ_MODELS[0]


def is_supported(model: str) -> bool:
    return model in GROQ_MODELS
