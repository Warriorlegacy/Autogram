# Autogram — AGENTS.md

## What This Repo Is

Autogram is a zero-touch Instagram carousel publishing engine. It ingests sources, scores topics, drafts 7–10 slide carousels, fact-checks them, renders 1080×1350 JPEGs via Playwright, and publishes through Meta's Graph API. It also includes a Flask dashboard, a 7× daily scheduler daemon, and a cryptographic license gate.

## Repo Layout (the non-obvious parts)

- **No `pyproject.toml` or `setup.py`.** Dependencies are in `requirements.txt`. Run modules directly with `python orchestrator.py` or `python dashboard_api.py`.
- **Two runtime entrypoints:**
  - `orchestrator.py` — CLI master pipeline (`--dry-run`, `--run-all`, `--schedule`, `--test`, `--render-only`, `--generate-image`, `--generate-script`, `--generate-reel`, `--refresh-token`).
  - `dashboard_api.py` — Flask API + background scheduler daemon (default port `5050`). Serves `dashboard.html` and `index.html`.
- **`src/` is the engine core.** Every module under `src/` is imported directly by the orchestrator. There is no package installation step.
- **`renderer/` is Playwright-bound.** Slide rendering depends on headless Chromium. The `renderer/css/design-system.css` file is 850+ lines and is inlined at render time.
- **`data/` holds runtime state:** `brand.json`, `seed_sources.json`, `content-memory.json`, `schedule.json`. The SQLite DB `autopilot.db` lives at repo root.

## Setup Commands

```bash
# 1. Create venv (Python 3.10+)
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Unix

# 2. Install deps
pip install -r requirements.txt

# 3. Install Playwright Chromium (required for rendering, not just tests)
playwright install chromium

# 4. Copy env
copy .env.example .env
# Edit .env with keys

# 5. Verify
python orchestrator.py --test
```

## License Gate (blocks everything)

All `orchestrator.py` and `dashboard_api.py` execution is gated by `src/auth/licensing.py`.
- **Owner bypass:** set `AUTOGRAM_OWNER_KEY=autogram_owner_vip_2026` in `.env` (this is the hardcoded default).
- **Client mode:** generate keys via `python -m src.auth.licensing --issue --client "Name" --tier growth --days 30`.
- Without a valid key, the process exits with status `1` before any pipeline work runs.
- Tests bypass the gate because `src/auth/licensing.py` reads from settings, and test fixtures set the owner key by default.

## Critical Runtime Quirks

- **`DRY_RUN=true` is the default.** The pipeline will not publish to Meta unless `DRY_RUN=false` in `.env` AND `IG_USER_ID`/`IG_ACCESS_TOKEN` are populated.
- **Dry-run mode fabricates public URLs** without uploading. The uploader constructs `PUBLIC_CDN_BASE/output/YYYY-MM-DD/slide_XX.jpg` paths. For real publishing, images must be reachable by Meta's servers.
- **`freeimage.host` API key is hardcoded** in `src/storage/uploader.py` (`6d207e02198a847aa98d0a2a901485a5`). Treat it as public/free-tier; do not rely on it for sensitive assets.
- **Renderer needs outbound network.** It loads Google Fonts from CDN. If running in a locked-down CI, fonts may not load and slide typography will fall back.
- **Timezone is `Asia/Kolkata`.** The scheduler daemon (`orchestrator.py --schedule` and `dashboard_api.py`'s background thread) uses this timezone for all slot calculations.
- **`orchestrator.py` propagates `--dry-run` to `publisher.dry_run` at runtime**, but `dashboard_api.py`'s subprocess invocation reads `DRY_RUN` from `.env` at launch time. Changing `.env` requires restarting the dashboard.

## Testing

```bash
pytest tests -v
```

**Test caveats:**
- `tests/test_growth_engine.py::test_publish_endpoint_auto_generates_caption_and_hashtags` requires existing output runs or returns `404`. It monkeypatches the uploader to avoid real network calls.
- `tests/test_image_and_scripts.py::test_publisher_dry_run_and_boolean_container` toggles `publisher._forced_dry_run` internally to test URL validation. It resets to `True` at the end.
- Playwright is **not** required for unit tests unless you call `--render-only` or the renderer directly.
- There is **no linter, typechecker, or formatter config** in the repo. If adding one, prefer `ruff` + `black` to match the modern Python style implied by `pydantic-settings` usage.

## Deployment Surfaces

| Surface | Config | Notes |
|---|---|---|
| Local dev | `python orchestrator.py --dry-run` | Requires Playwright |
| Dashboard (local) | `python dashboard_api.py` | Port 5050; serves static files |
| Windows quick-start | `start_autogram.bat` | Starts dashboard + ngrok + scheduler |
| GitHub Actions | `.github/workflows/daily-post.yml` | 7 cron slots; fails over to Render webhook |
| Render | `render.yaml` | Free tier; runs `dashboard_api.py` |
| Vercel | `vercel.json` | Static only — serves `index.html` + assets |

## Architecture Summary (for agents modifying code)

```
orchestrator.py
  ├── src/research/fetcher.py        # RSS + HN Algolia → source_records
  ├── src/research/scorer.py         # 6-pillar rotation + anti-repetition
  ├── src/content/generator.py       # Multi-LLM fallback chain (9 providers)
  ├── src/content/fact_checker.py    # Light superlative + source_id checks
  ├── src/content/quality_gate.py    # Score 0–100, banned phrases, slide count
  ├── src/content/script_writer.py   # Captions, hashtags, Reels scripts
  ├── src/content/image_generator.py # FLUX.1 / Imagen / DALL-E
  ├── renderer/render.py             # Playwright → 1080×1350 JPEG
  ├── src/storage/uploader.py        # S3/R2 → free CDN cascade
  ├── src/instagram/publisher.py     # Meta Graph API container flow
  ├── src/instagram/token_manager.py # 60-day token refresh
  ├── src/analytics/optimizer.py     # Content score + memory ledger
  └── src/auth/licensing.py          # HMAC-SHA256 license gate
```

## Style / Convention Notes

- **Fail-closed is mandatory.** If the quality gate fails after 2 retries, the pipeline raises `RuntimeError` and does not publish.
- **Banned phrases** are enforced both at generation time (`generator.py` scrub) and QA time (`quality_gate.py`). The canonical list lives in `data/brand.json` under `avoid`.
- **All network calls have timeouts** (15–60s). Live Meta publishing waits up to 180s per container.
- **JSON is the interchange format** between every layer. `content.json`, `manifest.json`, `content-memory.json`, and `schedule.json` are the key persisted artifacts.
- **No async/await anywhere.** Everything is synchronous `requests` + `subprocess.Popen`.
