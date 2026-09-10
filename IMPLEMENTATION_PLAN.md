# Autogram — Implementation Plan

## Current State Assessment

### What Works Well
- The 5-layer pipeline is functional and well-structured in `orchestrator.py`
- Multi-LLM fallback chain in `generator.py` is robust (9 providers, zero-cost guaranteed)
- Playwright-based renderer produces deterministic 1080×1350 JPEGs
- Flask dashboard with scheduler daemon is self-contained
- GitHub Actions CI runs 7 daily slots with Render webhook failover
- Cryptographic license gate is correctly implemented
- SQLite schema covers content, sources, metrics, and experiments

### Critical Technical Debt
1. **No package management** (`pyproject.toml` / `setup.py` missing). `requirements.txt` is the only source of truth.
2. **Hardcoded API key** in `src/storage/uploader.py` line 34 (`freeimage.host`).
3. **No linter, typechecker, or formatter** in CI or local dev.
4. **Scheduler logic is duplicated** between `orchestrator.py::run_scheduler` and `dashboard_api.py::scheduler_worker`.
5. **`dashboard_api.py` subprocess invocation reads `DRY_RUN` from `.env` at launch**, not at runtime; changing `.env` requires restart.
6. **No migration system** for `autopilot.db` schema changes.
7. **Renderer requires outbound network** (Google Fonts CDN). Fails in locked-down CI without cache.
8. **Tests have network dependencies** (`test_growth_engine.py::test_publish_endpoint_auto_generates_caption_and_hashtags` requires output artifacts).
9. **`package.json` uses `uv pip install`** but the actual environment uses standard `pip`.
10. **No structured error recovery** for failed Meta container creation (timeout after 180s with no retry).

---

## Phase 1 — Hardening & Developer Experience (Weeks 1-2)

### 1.1 Add Standard Python Tooling
- Add `pyproject.toml` with `[build-system]` (setuptools) and `[project]` metadata.
- Add `ruff` + `black` config.
- Add `mypy` strict config for `src/`.
- Add `pre-commit` hooks: ruff, black, mypy.
- **Why:** The repo currently has zero static analysis. `pydantic-settings` usage implies modern Python style, but there is no enforcement.

### 1.2 Remove Hardcoded Secrets
- Move `freeimage.host` API key to `.env` as `FREEIMAGE_API_KEY`.
- Update `uploader.py` to read from `settings.freeimage_api_key` with a fallback to the existing key for backward compatibility, but emit a warning.
- **Why:** Hardcoded keys in source control are a security risk, even if the service is free-tier.

### 1.3 Centralize Scheduler Logic
- Extract the 7-slot scheduling loop into `src/scheduler/daemon.py`.
- Have both `orchestrator.py --schedule` and `dashboard_api.py` import and run the same daemon.
- **Why:** Duplicated logic in two files means bug fixes must be applied twice.

### 1.4 Add Database Migrations
- Introduce `alembic` for SQLite schema versioning.
- Write initial migration for the 5 existing tables.
- **Why:** Schema changes (e.g., adding indexes, new columns) currently require manual `ALTER TABLE` statements with no rollback path.

### 1.5 Improve Test Reliability
- Add pytest fixtures for temporary output directories and mocked uploader.
- Make `test_growth_engine.py::test_publish_endpoint_auto_generates_caption_and_hashtags` skip gracefully when no output runs exist (instead of returning 404).
- Add `pytest-xdist` for parallel test execution.
- **Why:** Tests should not depend on external state or network calls.

---

## Phase 2 — Resilience & Observability (Weeks 3-4)

### 2.1 Structured Logging
- Replace `logging.basicConfig` with structlog or `logging` with JSON formatter.
- Emit `pipeline_start`, `pipeline_end`, `quality_gate_rejection`, `meta_publish_success` events.
- **Why:** Currently logs are plain text. Structured logs make debugging production failures (especially in GitHub Actions) much faster.

### 2.2 Retry & Circuit Breaker for Meta API
- Wrap Meta Graph API calls (`publisher.py`) with `tenacity` retry (exponential backoff, max 3 retries).
- Add circuit breaker for repeated 4xx/5xx failures to avoid burning quota.
- **Why:** The 180s container wait has no retry. A transient Meta outage kills the entire pipeline.

### 2.3 Renderer Font Cache
- Bundle Google Fonts locally or use `playwright install-deps` + font cache in CI.
- Add a `--no-fonts` flag to `render_sample()` for offline environments.
- **Why:** Renderer fails silently in locked-down CI. Deterministic rendering is the product's core value proposition.

### 2.4 Health Check Endpoints
- Expand `/health` in `dashboard_api.py` to include:
  - DB connectivity check
  - Playwright browser availability
  - LLM provider reachability (lightweight ping)
  - Meta token validity (lightweight Graph API call)
- **Why:** Current health check is a static string. Operators cannot tell if the engine is actually functional.

### 2.5 Content Memory Indexes
- Add SQLite indexes on `content_items(publication_date)`, `content_items(status)`, `source_records(content_hash)`.
- Add a `recent_topics` materialized view for fast anti-repetition lookups.
- **Why:** `scorer.py` loads the full `content-memory.json` into memory. As history grows, this will become a bottleneck.

---

## Phase 3 — Pipeline Extensibility (Weeks 5-6)

### 3.1 Pipeline as DAG
- Refactor `run_pipeline()` from a linear sequence into a DAG of named stages.
- Each stage returns a result dict; stages can be skipped or retried independently.
- Add a `--stage` flag to run individual stages (e.g., `--stage render-only`).
- **Why:** Currently the pipeline is a monolith. Debugging a single stage failure requires running the full pipeline.

### 3.2 Plugin Architecture for LLM Providers
- Define a `LLMProvider` protocol in `src/content/providers/base.py`.
- Move each provider method (`generate_with_gemini`, `generate_with_groq`, etc.) into its own class.
- Register providers via entry points or a simple registry dict.
- **Why:** Adding a new provider currently requires editing `generator.py` directly. A plugin system keeps the core clean.

### 3.3 Output Artifact Validation
- Add a post-render validation step that checks every slide against `renderer/validate.py` rules.
- Fail the pipeline early if a slide exceeds 80-char headlines or 240-char body.
- **Why:** Currently validation is a warning-only log message. Bad slides can still be published.

### 3.4 Carousel Template Registry
- Move `LAYOUT_TO_TEMPLATE` into `data/brand.json` or a dedicated `templates/registry.json`.
- Allow brand profiles to specify custom template mappings per pillar.
- **Why:** Template selection is currently hardcoded in `render.py`. Brand customization is a customer requirement.

---

## Phase 4 — Production Readiness (Weeks 7-8)

### 4.1 GitHub Actions Improvements
- Add `actions/cache` for `~/.cache/ms-playwright` (already present, verify it works).
- Add a lint job that runs `ruff check src/` on every PR.
- Add a test job that runs `pytest tests/ -v --tb=short`.
- Add a deployment gate: only deploy to Render if tests pass.
- **Why:** CI currently only runs the publish job. There is no quality gate before code reaches production.

### 4.2 Render.com Health Monitoring
- Add a cron job that pings `/health` every 10 minutes and sends an alert if the dashboard is down.
- Configure Render to restart the service if `/health` fails 3x in a row.
- **Why:** Render free tier spins down after 15 minutes of inactivity. The keep-alive workflow exists but does not verify actual engine health.

### 4.3 Secrets Management
- Audit all `os.environ.get()` and `settings.*` accesses in `dashboard_api.py` and `orchestrator.py`.
- Ensure no secret is ever returned by an API endpoint (verify `redact()` covers all sensitive keys).
- Rotate the hardcoded `freeimage.host` key if it has ever been committed.
- **Why:** `dashboard_api.py::api_env_get` redacts some keys, but the allowlist may be incomplete.

### 4.4 Performance Profiling
- Profile `orchestrator.py --run-all` end-to-end. Target: < 5 minutes total.
- Identify bottlenecks: LLM API latency (multiple providers tried), Playwright launch overhead, image upload cascade.
- Add timing metrics to `pipeline_manifest.json`.
- **Why:** The pipeline currently has no performance budgets. Slow runs will cause scheduler slot overlaps.

### 4.5 Multi-Account Support (Enterprise)
- Extend `data/brand.json` schema to support multiple brand profiles.
- Add brand selection to `dashboard_api.py` publish and generate endpoints.
- Update scheduler to cycle through enabled brands.
- **Why:** The pricing page advertises "Up to 3 Distinct Brand Accounts" for Enterprise, but the engine only supports one brand profile.

---

## Execution Order

```
Phase 1.1 (pyproject.toml + ruff/black)
    → Phase 1.2 (remove hardcoded key)
    → Phase 1.3 (centralize scheduler)
    → Phase 1.4 (alembic migrations)
    → Phase 1.5 (test reliability)

Phase 2.1 (structured logging)
    → Phase 2.2 (Meta retries)
    → Phase 2.3 (font cache)
    → Phase 2.4 (health endpoints)
    → Phase 2.5 (memory indexes)

Phase 3.1 (DAG pipeline)
    → Phase 3.2 (LLM plugins)
    → Phase 3.3 (artifact validation)
    → Phase 3.4 (template registry)

Phase 4.1 (CI improvements)
    → Phase 4.2 (Render monitoring)
    → Phase 4.3 (secrets audit)
    → Phase 4.4 (profiling)
    → Phase 4.5 (multi-account)
```

Phases are sequential because each builds on the previous. Within a phase, items marked with `→` are also sequential. Items not connected by arrows within the same phase can be parallelized.
