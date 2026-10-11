"""Signhify Studio — code-first 9:16 Reel production pipeline.

Importing this package loads the repo .env into os.environ, overriding any
inherited value. Done here, in __init__, so EVERY entrypoint gets it: the CLI,
the CI inline scripts that import video_studio.instagram directly, and tests.

override=True is deliberate. A stale exported GROQ_API_KEY in the process
environment silently shadowed the file's value and produced a 401 that looked
like a bad key; that cost real debugging time once already.
"""
from pathlib import Path

try:
    from dotenv import load_dotenv

    _ENV = Path(__file__).resolve().parent.parent / ".env"
    if _ENV.exists():
        load_dotenv(_ENV, override=True)
except Exception:  # never let config loading break an import
    pass
