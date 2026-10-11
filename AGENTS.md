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

## Video Studio (HyperFrames)

`video_studio/` is a **self-contained 9:16 Instagram Reels engine**. It shares exactly one file with the legacy carousel pipeline — `data/brand.json` — and nothing else. It does not use Playwright, does not read `.env`, and needs no API key or account to render.

### ⚠️ The one thing a future agent must not get wrong

There are **two** unrelated things in this repo called "HyperFrames".

| | `src/content/hyperframes_engine.py` | `video_studio/` |
|---|---|---|
| What it is | Hand-rolled Jinja2 + Playwright + FFmpeg renderer, written in-house | Thin Python wrapper around the **real HyperFrames CLI** (HeyGen, Apache-2.0) |
| Uses the HyperFrames product? | **No.** It borrows the name only | **Yes** — every subprocess is `npx --yes hyperframes …` (`video_studio/render.py:27`) |
| Relationship to the rest of Autogram | Legacy carousel/reel path under `orchestrator.py` | Independent; run `python -m video_studio.cli` directly |

`hyperframes_engine.py` is a **name collision, not an implementation** of HyperFrames. Never rewire `video_studio` to it, and never cite a `hyperframes_engine.py` render as a HyperFrames render. Evidence and full audit: `docs/video-studio/01_TECHNICAL_RESEARCH.md` §1.1.

### The four commands

Always from `D:\Autogram`, always with the venv interpreter (the system Python lacks jinja2/pydantic):

```powershell
# 1. BUILD — validate brief, compile storyboard, write the HyperFrames project
.venv\Scripts\python.exe -m video_studio.cli build   --brief video_studio/briefs/<slug>.json

# 2. RENDER — hyperframes check → render → mux → package → QA, all five steps
.venv\Scripts\python.exe -m video_studio.cli render  --brief video_studio/briefs/<slug>.json --quality draft

# 3. QA — inspect an existing MP4 on its own
.venv\Scripts\python.exe -m video_studio.cli qa      --video video_studio/output/<slug>/reel.mp4 --frames video_studio/output/<slug>/qa_frames --no-audio

# 4. PACKAGE — regenerate captions / caption.txt / manifest only, no render
.venv\Scripts\python.exe -m video_studio.cli package --brief video_studio/briefs/<slug>.json
```

`-m video_studio.cli` is the documented form; `video_studio/__main__.py` also exists, so the bare `-m video_studio` works. `render` flags: `--quality draft|standard|high` (default `draft`), `--audio` (synthesize + mux narration), `--skip-gate` (diagnostic only — it changes no exit code).

**Exit codes** (`video_studio/cli.py`):

| Code | Meaning |
|---|---|
| `0` | Pass — QA verdict `PASS`, no defects |
| `1` | Render error or uncaught exception (`RenderError`, missing file, malformed brief JSON) |
| `2` | QA fail — at least one defect recorded by `qa.py` |
| `3` | Brief invalid — a `data/brand.json` avoid phrase hit, or `scenes` is empty |
| `4` | Narration overrun — a scene is too short to speak *and* read its own narration |

Code `4` is emitted by `_validate()` via `storyboard.narration_fit()` and is **not** listed in `06_PRODUCTION_RUNBOOK.md` §1.2 — that table is incomplete, not the code wrong.

### Input / output directory contract

```
video_studio/briefs/<slug>.json          authored input   (the contract — slug is [A-Za-z0-9-_]+)
        │  compile_storyboard()          brief -> scenes + absolute start times + caption cues
        ▼
video_studio/work/<slug>/                GENERATED, disposable
        index.html · hyperframes.json · meta.json · package.json · assets/
        ▼  hyperframes check → hyperframes render → ffmpeg
video_studio/output/<slug>/              the deliverable
        reel.mp4 · cover.jpg · captions.srt · caption.txt · storyboard.json
        brief.json · asset_manifest.json · qa_report.json · qa_report.md
        render.log · qa_frames/*.jpg
```

`write_project()` does `shutil.rmtree()` on `work/<slug>/` on every `build` **and** every `render`. **Never hand-edit `work/<slug>/index.html`** — it is gone on the next run. Edit `video_studio/briefs/<slug>.json` or `video_studio/templates/composition.html.jinja2`.

### Brand avoid-list — one guard, at the boundary

`cli.py::_validate()` runs `Brief.banned_hits()` before any other work and returns `3` on a hit. The 16 phrases live in `data/brand.json → avoid` and are matched case-insensitively against `title`, `hook`, `cta`, and every scene's `narration` / `headline` / `subtext` / `eyebrow` / `bullets`.

- **Do not bypass this check.** Not with `--skip-gate`, not by rewording the guard, not by editing `data/brand.json` to shrink the list.
- `robust` and `seamless` are the traps — ordinary engineering vocabulary that survives a casual read.
- **Not scanned:** `sources[]`, `notes`, `pillar`, and `metrics[].v` / `metrics[].k`. Those are checked by eye, which means by you.

### Fail-closed rules for this pipeline

- **Never fabricate a product claim, metric, customer, follower count, or result.** Every number must trace to `signhify.dpdns.org`, `data/brand.json`, or something you actually observed. `instagram.com/signhify.studio` was auth-walled at research time — **no post-level data exists, so none may be invented.**
- **Never claim a render, test, or publish happened without verifying it.** Read `output/<slug>/render.log` and `qa_report.md`. A `--audio` render that finds no TTS provider still exits 0 and ships silent — `render.log` will say `no TTS provider available`. A zero exit code is not proof that audio exists.
- **Never commit credentials.** The video path reads *no* environment variables. Instagram tokens (`IG_USER_ID`, `IG_ACCESS_TOKEN`, `META_API_VERSION`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `META_GRAPH_ACCESS_TOKEN`) exist only as future placeholders in `.env.example` for the legacy carousel pipeline. `.env` is gitignored — keep it that way.
- **Publishing is disabled and unauthorized.** `publish.py` produces a package and never publishes; `asset_manifest.json` hardcodes `"publishing": {"enabled": false}`. There is no `--publish` flag. Do not add one, and do not contact Instagram from `video_studio`. See `docs/video-studio/08_INSTAGRAM_PUBLISHING.md` (specification only).
- **Bounded retries: max 2 repair attempts per defect, then escalate to a human.** Never loop render-and-repair. A gate that can be bypassed is not a gate — same rule as the carousel pipeline above.

### Determinism and what the automated gate actually proves

Rendering is deterministic on a fixed stack: the reference brief produced **byte-identical MP4s** (SHA-256 `52F88E97…B61522E`) on back-to-back runs. Stated precisely, from `03_SYSTEM_ARCHITECTURE.md` §9: identical brief + identical HyperFrames version + identical Chrome build + reachable font/GSAP CDNs → identical bytes. **Change any of those and you get a different file.** Do not treat "deterministic" as "byte-identical forever" — notably, `render.py` calls bare `npx --yes hyperframes`, so it resolves whatever npm has cached.

The QA gate is three things, in order: `hyperframes check` (runtime · layout · motion · WCAG AA contrast, nonzero exit → `RenderError`), `ffprobe` plus 10 assertions in `qa.py`, and extraction of 7 real JPEGs into `output/<slug>/qa_frames/`.

> **A passing automated gate is not a production verdict.** `qa.py` reads container metadata and extracts frames. It never looks at them. Both real defects found on this build — a tofu-glyph eyebrow and a scene counter stuck on a static total — were invisible to `hyperframes check` and to `qa.py`, and obvious the moment the JPEGs were opened. Open them. `cli.py` writes the same warning into every `qa_report.md`.

Full detail: `docs/video-studio/06_PRODUCTION_RUNBOOK.md` (operations), `07_VIDEO_QUALITY_CHECKLIST.md` (human gate), `09_TROUBLESHOOTING.md` (failures).
