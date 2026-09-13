# Implementation Plan — Makerzz God-Mode Autonomous Social Operating System (P0–P8)

Integrate the complete **Makerzz Autonomous Social-Content Operating System** as specified in [`MAKERZZ_REVERSE_ENGINEER_GOD_MODE.md`](file:///d:/Autogram/MAKERZZ_REVERSE_ENGINEER_GOD_MODE.md) and [`Autonomous Posting System Architecture.pdf`](file:///d:/Autogram/Autonomous%20Posting%20System%20Architecture.pdf) into Autogram, **without disturbing or altering any currently functioning system** (such as the daily Reels GitHub Action, `dashboard_api.py`, or `scripts/pipeline_reels.py`).

---

## User Review Required

> [!IMPORTANT]
> **Zero-Disturbance Guarantee:**
> All existing production paths remain 100% operational:
>
> 1. `scripts/pipeline_reels.py` and `.github/workflows/daily_reels.yml` (publishing live daily reels to Instagram at 13:00 UTC) remain completely untouched.
> 2. Existing CLI commands (`python orchestrator.py --run-all`, `--dry-run`, `--style glitch-hormozi`) retain identical behavior and arguments.
> 3. Existing Flask Dashboard (`dashboard_api.py` on port 5050) continues serving `dashboard.html` and `index.html` seamlessly; all new endpoints will be mounted additively under `/api/v2/`.
> 4. All brand assets strictly enforce **Signhify Studio** (`signhify.studio`), `@signhify.studio`, and creator **Piyush Raj Singh** ("My name is Piyush Raj Singh. Stop posting. Start shipping.").

> [!NOTE]
> **External Services & Hybrid Zero-Cost Fallback:**
> The Makerzz architecture references external enterprise services (Ayrshare for 13-platform dispatch, Apify for profile scraping, HeyGen for talking avatars). We will build this with a **Dual-Mode Adapter Architecture**:
>
> - **Enterprise Mode:** Used when API keys are supplied in `.env` (`AYRSHARE_API_KEY`, `APIFY_API_KEY`, `HEYGEN_API_KEY`).
> - **Self-Hosted Zero-Cost Engine (Default):** Uses existing zero-cost pipelines (direct Meta Graph API for Instagram, Playwright HTML/CSS canvas for carousels, Edge-TTS + Faster-Whisper + FFmpeg for vertical video, open-source RSS/HN/GitHub scraper for research).

---

## Architecture Overview: The P0–P8 Gated State Machine

```
                              INPUT: Brief / Profile / Competitor URLs
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ P0: SETUP & ONBOARDING          │ Gate: brief.json (validated niche, audience, voice)       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ P1: NICHE & COMPETITOR SCAN     │ Gate: scan.json (engagement velocity, 8 ranked angles)    │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ P2: STRATEGY & 30-DAY CALENDAR  │ Gate: calendar.json (Hormozi rule, slot allocation)       │
├─────────────────────────────────┴───────────────────────────────────────────────────────────┤
│                                 PARALLEL PRODUCTION GATES                                   │
│  ┌──────────────────────────────────────────────┐ ┌──────────────────────────────────────┐  │
│  │ P3: SCRIPT ENGINE (Spoken Text Only)         │ │ P6: CAROUSEL COMPILER                │  │
│  │ Gate: script.txt + verification.json         │ │ Gate: carousel_plan.json + prompts   │  │
│  │ (<2.5 words/s, no markdown/bracket tags)     │ │ (8-slide Makerzz/Hormozi layout)     │  │
│  ├──────────────────────────────────────────────┤ ├──────────────────────────────────────┤  │
│  │ P4: AVATAR / MOTION VIDEO                    │ │ P6-R: HEADLESS RENDER ENGINE         │  │
│  │ Gate: video.mp4 + provider_job.json          │ │ Gate: slides/*.jpg (Playwright 1080p)│  │
│  ├──────────────────────────────────────────────┤ └──────────────────────────────────────┘  │
│  │ P5: EDIT PLAN & KINETIC TIMELINE             │                                           │
│  │ Gate: edit_plan.json (beats, SFX, overlays)  │                                           │
│  └──────────────────────────────────────────────┘                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ P7: DISTRIBUTION ADAPTERS       │ Gate: queue.json -> published_receipt.json                │
│                                 │ (Native Meta Graph API + Optional Ayrshare 13-platform)   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ P8: AUDIT REPORT & CREDIT LEDGER│ Gate: report.pdf + ledger_entries                         │
│                                 │ (Append-only SQLite ledger, no fabricated metrics)        │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

Every run executes inside an isolated workspace directory `runs/<run_id>/` with durable, inspectable JSON and media artifacts.

---

## Proposed Additions & Modifications

### 1. Core State Machine & Run Engine (`src/engine/`)

New decoupled package implementing the P0–P8 lifecycle, artifact gating, approval policies, and idempotency.

#### [NEW] [src/engine/state_machine.py](file:///d:/Autogram/src/engine/state_machine.py)

- Defines typed `Phase` enum (`P0_SETUP`, `P1_SCAN`, `P2_STRATEGY`, `P3_SCRIPT`, `P4_VIDEO`, `P5_EDIT_PLAN`, `P6_CAROUSEL`, `P7_PUBLISH`, `P8_REPORT`).
- Defines `StageStatus` (`PENDING`, `APPROVED`, `RUNNING`, `COMPLETED`, `FAILED`, `BLOCKED_CREDITS`).
- Implements `StagePolicy` (`approve` vs `auto`). When stage policy is `approve`, execution pauses and waits for user authorization before billable work or publishing.

#### [NEW] [src/engine/run_manager.py](file:///d:/Autogram/src/engine/run_manager.py)

- Manages `runs/<run_id>/` lifecycle and persists artifact hashes (`sha256`), run metadata, and execution checkpoints.
- Guarantees **resumability**: if a stage fails or browser disconnects, rerunning picks up from the last validated gate artifact without duplicating already rendered slides or charged credits.

#### [NEW] [src/engine/idempotency.py](file:///d:/Autogram/src/engine/idempotency.py)

- Formats idempotency keys: `{brand_id}:{run_id}:{stage}:{asset_id}:{action}`.
- Prevents double-submissions to external providers or publish endpoints.

---

### 2. Verification-Gated Scripting & Edit Plans (`src/content/`)

#### [NEW] [src/content/script_verifier.py](file:///d:/Autogram/src/content/script_verifier.py)

- Strict verifier mandated by Makerzz and Architecture PDF:
  - **Spoken Cadence:** Validates spoken speed $\le 2.5$ words/second.
  - **No Bracket Tags:** Rejects `[HOOK]`, `[CTA]`, `(pause)`, `(smile)`, `Beat 1:`.
  - **No Markdown/Formatting:** Rejects `**bold**`, `## Header`, bullet lists, timecodes (`00:14`).
  - **Zero Emojis:** Spoken text must be purely verbal for voice engines.
- **Fail-Closed Auto-Retry:** If a script fails verification, automatically invokes LLM with precise feedback (up to 3 retries) rather than silently mutating text.

#### [NEW] [src/content/edit_plan_compiler.py](file:///d:/Autogram/src/content/edit_plan_compiler.py)

- Separates production instructions from spoken text. Produces `edit_plan.json`:
  - Visual beats and camera framing (cut, punch-in, zoom).
  - Kinetic subtitle timings and highlighting triggers.
  - B-roll search queries / background assets.
  - Sound effect (SFX) cue points and transitions.

---

### 3. Competitor Ingestion & Strategy Matrix (`src/research/`)

#### [NEW] [src/research/niche_scanner.py](file:///d:/Autogram/src/research/niche_scanner.py)

- Normalizes competitor profile data into structured signals.
- Computes engagement velocity:
  $$\text{Engagement Rate} = \frac{\text{Likes} + (\text{Comments} \times 2) + (\text{Shares} \times 4)}{\text{Views}}$$
- Extracts 8 ranked content angles: Angle, Novelty Score, Mechanism, Evidence, and Reproducible Format.
- Saves validated `scan.json`.

#### [NEW] [src/research/calendar_compiler.py](file:///d:/Autogram/src/research/calendar_compiler.py)

- Generates a 30-day content calendar (`calendar.json`) based on the 8 ranked angles.
- Enforces:
  - Cadence constraints (e.g., 1 Reel + 1 Carousel / day).
  - Format diversity (no identical layouts 3 days in a row).
  - Timezone-aware posting slots (`Asia/Kolkata` default, 19:30 IST).
  - Deterministic random minute jitter for organic distribution.

---

### 4. Multi-Platform Distribution Adapters (`src/distribution/`)

#### [NEW] [src/distribution/base_adapter.py](file:///d:/Autogram/src/distribution/base_adapter.py)

- Defines abstract `PublishAdapter` protocol:
  - `get_capabilities()` -> text, image, video, carousel, aspect ratios, caption limits.
  - `validate_post(canonical_post)`.
  - `publish(canonical_post, media_urls)`.
  - `get_metrics(remote_post_id)`.

#### [NEW] [src/distribution/adapters/instagram_adapter.py](file:///d:/Autogram/src/distribution/adapters/instagram_adapter.py)

- Wraps the existing `src/instagram/publisher.py` into the new adapter interface without modifying `src/instagram/publisher.py`.

#### [NEW] [src/distribution/adapters/ayrshare_adapter.py](file:///d:/Autogram/src/distribution/adapters/ayrshare_adapter.py)

- Implements 13-platform dispatch via Ayrshare API (`https://api.ayrshare.com/api/post`) when `AYRSHARE_API_KEY` is present.
- Targets: Instagram, YouTube Shorts, LinkedIn, TikTok, Facebook, Threads, X, Pinterest, Bluesky, Reddit, Telegram, Discord, Google Business Profile.
- If unconfigured, reports clean capability status: `{"configured": false, "reason": "Missing AYRSHARE_API_KEY"}`.

---

### 5. Append-Only Credit Ledger & Audit Reporting (`src/billing/`)

#### [NEW] [src/billing/credit_ledger.py](file:///d:/Autogram/src/billing/credit_ledger.py)

- Transactional SQLite ledger in `autopilot.db` (`credit_ledger` table).
- Rules:
  - Entries are **append-only**; never mutate a previous transaction.
  - Standardized cost table:
    - Scan: 40 credits
    - Script: 12 credits
    - Edit Plan: 20 credits
    - Carousel Prompts & Plan: 30 credits
    - Standard Slide Render: 3 credits / slide
    - Vertical Video Compositing: 202 credits
    - Publishing: 0 credits (unmetered economics model)
  - `AUTOGRAM_OWNER_KEY` provides VIP unlimited credit balance.
  - Fail-closed: if credits are insufficient for non-owner, aborts stage cleanly before calling paid providers.

#### [NEW] [src/billing/report_generator.py](file:///d:/Autogram/src/billing/report_generator.py)

- Compiles the final run audit report into `runs/<run_id>/report.json` and styled PDF `runs/<run_id>/report.pdf`:
  - Input brief & research sources.
  - Ranked angles & decisions taken.
  - Shipped assets (slides, video paths, captions).
  - Exact publish receipts & remote post IDs.
  - Ledger debits & credit breakdown.
  - Analytics snapshots (or explicit `unavailable` marker — never fabricated).

---

### 6. Dashboard & CLI Integration (Additive Only)

#### [MODIFY] [dashboard_api.py](file:///d:/Autogram/dashboard_api.py)

- Add additive `/api/v2/` endpoints without altering any existing `/api/` routes:
  - `GET /api/v2/runs` — List all durable runs and their current P0-P8 status.
  - `POST /api/v2/runs/new` — Initialize a new P0 run from brief/profile link.
  - `POST /api/v2/runs/<run_id>/step` — Trigger next stage (with approval check).
  - `POST /api/v2/runs/<run_id>/approve` — User approval for pending stage.
  - `GET /api/v2/runs/<run_id>/artifacts` — Inspect generated JSON/media artifacts.
  - `GET /api/v2/ledger` — View credit ledger transactions and balance.

#### [MODIFY] [orchestrator.py](file:///d:/Autogram/orchestrator.py)

- Add `--makerzz-run [brief_path]` and `--resume-run [run_id]` flags to CLI parser. Existing flags (`--dry-run`, `--run-all`, `--schedule`, `--style`) retain 100% backward compatibility.

---

## Verification Plan

### Automated Tests

1. **State Machine & Gate Transition Tests:**

   ```bash
   pytest tests/test_makerzz_state_machine.py -v
   ```

   - Validates that P1 cannot execute without a valid `brief.json`.
   - Validates that P3 script verifier strictly fails scripts with markdown or bracket section titles.
   - Validates that already-rendered slides are skipped on resumption.

2. **Credit Ledger Transaction Tests:**

   ```bash
   pytest tests/test_credit_ledger.py -v
   ```

   - Validates atomic balance calculation and append-only immutability.
   - Validates owner VIP bypass and non-owner fail-closed behavior.

3. **Regression Test on Existing Systems:**

   ```bash
   pytest tests/test_glitch_hormozi_engine.py tests/test_growth_engine.py -v
   ```

   - Confirms all 14 slide templates, lead capture, and existing pipeline commands work identically.

4. **Dry-Run Pipeline Execution:**
   ```bash
   python orchestrator.py --dry-run --style glitch-hormozi
   ```

   - Verifies the standard end-to-end publishing pipeline completes without errors.

---

## Open Questions for User Approval

1. **Ayrshare Multi-Platform API Key:**  
   Do you have an active Ayrshare API key, or should the default multi-platform dispatcher operate in **Direct Meta Mode** (publishing to Instagram via Meta Graph API, and staging other platform payloads locally)?
2. **Avatar Video Mode:**  
   When vertical videos are rendered in P4:
   - Should it use our internal **Zero-Cost Edge-TTS + Kinetic Subtitles + Zoompan** engine (active now)?
   - Or should it support optional HeyGen API green-screen integration if a `HEYGEN_API_KEY` is provided in `.env`?
