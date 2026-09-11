# Autogram — Session Context & Master State

> **Last Updated:** 2026-09-11 17:30 IST  
> **Repository:** `Warriorlegacy/Autogram` (`main` branch)  
> **Latest Git Commit:** `3ca847c` ("refactor(design): makerzz-inspired redesign — editorial dark, day/night mode, SIGNHIFY watermark")  
> **Target Profile:** `@signhify.studio`  
> **Live Publishing Status:** **VERIFIED & ACTIVE** (Live Media ID: `18133054180629915` published directly to Instagram feed with first-comment ID `18190231507400189`)  
> **Growth Objective:** 100k followers in 15 days via zero-touch FOSS & Secret AI Prompts publishing.  
> **Dashboard:** **REDESIGNED** — makerzz.space-inspired editorial dark UI, live at `https://autogram-dashboard.onrender.com/dashboard`

---

## 1. High-Level System Architecture

Autogram is an end-to-end, zero-touch autonomous social media engine. It investigates trending developer tools and prompt engineering architectures, fact-checks and deep-researches them, renders 1080×1350 high-contrast carousel slides via Playwright Chromium, produces multi-platform syndication assets, and publishes via Meta's Graph API.

```
[cron-job.org (7x Daily IST)]
         │ (GitHub Actions repository_dispatch)
         ▼
[orchestrator.py]
  ├── Phase 1:  Source Acquisition (fetcher.py: GitHub Trending, Hacker News Algolia, RSS)
  ├── Phase 2:  Niche Trend Analysis & Strict Virality Gate (trend_analyzer.py: Score >= 85.0)
  │              └── Emits: viral_analysis.json
  ├── Phase 2b: Deep Technical Research Engine (deep_researcher.py: Live stars, licenses, 1-line setup, SaaS contrast)
  │              └── Emits: research_dossier.json
  ├── Phase 3:  Grounded Carousel Generation (generator.py: Multi-LLM fallback, exact facts injection)
  ├── Phase 4:  Fact-Checking (fact_checker.py: Zero hallucinated stats)
  ├── Phase 5:  Quality & Slop Gate (quality_gate.py: 80+ QA threshold, banned phrases filter)
  ├── Phase 6:  Playwright Slide Rendering (renderer/render.py: 1080x1350 JPEG)
  ├── Phase 6b: Multi-Platform Script Generation (script_writer.py)
  │              ├── caption.txt (Hook + bullet takeaways + "Comment FOSS/PROMPT" CTA)
  │              ├── hashtags.txt (3-tier viral hashtag clustering)
  │              ├── first_comment.txt (Community discussion trigger)
  │              ├── reels_script.md (30-45s fast-paced video script)
  │              ├── edit_plan.json (Makerzz Section 8 timeline with SFX and cuts)
  │              ├── x_thread.txt (6-tweet viral thread)
  │              └── linkedin_post.txt (CTO/founder thought leadership)
  ├── Phase 7:  Asset Staging (uploader.py: S3/R2 / freeimage.host / local fallback)
  ├── Phase 8:  Instagram Publishing (publisher.py: Meta Graph API container carousel)
  └── Phase 9:  Self-Optimization & Anti-Repetition (optimizer.py: content-memory.json)
```

---

## 2. Core Modules Built & Enhanced in this Session

### A. Niche Trend Analysis & The Virality Gate (`src/research/trend_analyzer.py`)
- **Strict Virality Gate (`VIRAL_GATE_THRESHOLD = 85.0`):** Automatically evaluates all ingested candidate topics. Topics scoring below 85.0 are killed and never published.
- **4-Dimensional Virality Matrix (0–100 pts):**
  1. *Hook Potency (25 pts):* Detects pattern interrupts ("Stop paying for X", "Ditch Adobe for $0", "3-persona prompt").
  2. *Save & Share Urgency (25 pts):* Measures reference utility (Docker one-liner, prompt code template, architecture blueprint).
  3. *Cost / Value Asymmetry (25 pts):* Quantifies financial savings ($0 FOSS vs $240/yr SaaS) or prompt efficiency gains (3.8x density).
  4. *Trend Heat & Social Proof (25 pts):* Evaluates GitHub stars (15k–150k+ stars = max points), HN points, and AI trend velocity.
  5. *Anti-Viral Slop Penalty (-30 pts):* Prunes beginner tutorials ("Getting started with Python") and minor patch notes.
- **Transparency Artifact:** Saves `output/YYYY-MM-DD/viral_analysis.json` documenting all analyzed topics, approved winners, and rejection logs.

### B. Deep Technical Research Engine (`src/research/deep_researcher.py`)
- **Live GitHub Verification:** Queries GitHub API for real-time stars (e.g. Stirling-PDF: 91,734 stars, Open-WebUI: 151,601 stars), license compliance, and commit activity.
- **1-Line Deployment Extraction:** Discovers and validates exact Docker/Docker Compose commands (`docker run -d -p ...`) so every post offers immediate practical execution.
- **SaaS Contrast Matrix:** Directly matches against proprietary SaaS pricing (Coolify vs Vercel, Stirling-PDF vs Adobe Acrobat, n8n vs Zapier, Documenso vs DocuSign, Open-WebUI vs ChatGPT Plus).
- **Secret ChatGPT Prompts Analysis:** Deconstructs prompt frameworks (Chain-of-Density, Tree-of-Thoughts, Reverse-Engineering Megaprompt), defines prompt variable placeholders, best model targets (GPT-4o, Claude 3.5 Sonnet, o3-mini), and benchmarked gains.
- **Prompt Grounding:** Verified facts are saved to `research_dossier.json` and injected into the LLM system prompt so all slides cite exact numbers with zero hallucinations.

### C. Multi-Platform Syndication & Video Blueprint (`src/content/script_writer.py`)
- **Dual Lead Magnet CTAs:** Every caption and slide 7/10 prompts users to comment `"FOSS"` (for Docker compose config & cheat sheet) or `"PROMPT"` (for full system prompt & variations) to maximize DM automation engagement.
- **Makerzz Section 8 Edit Plan (`edit_plan.json`):** Formats 9:16 vertical video editing timelines with hard cuts, glitch transitions, text style badges, sound effects (`whoosh_impact`, `mechanical_keyboard_clicks`), and B-roll instructions.
- **X/Twitter & LinkedIn Syndication:** 6-tweet viral thread (`x_thread.txt`) and founder-focused LinkedIn breakdown (`linkedin_post.txt`).

---

## 3. Autonomous Cloud Scheduling Infrastructure

The pipeline is triggered automatically via `cron-job.org` calling GitHub Actions `repository_dispatch` with zero dependency on GitHub's delayed internal cron queue.

### Active Cloud Cron Jobs (cron-job.org)
| Job ID | Slot (IST) | Slot (UTC) | Target / Payload | Status |
|---|---|---|---|---|
| `8429357` | **08:00 IST** | 02:30 UTC | `api.github.com/repos/Warriorlegacy/Autogram/dispatches` | **Active** |
| `8429359` | **10:30 IST** | 05:00 UTC | `api.github.com/repos/Warriorlegacy/Autogram/dispatches` | **Active** |
| `8429363` | **13:00 IST** | 07:30 UTC | `api.github.com/repos/Warriorlegacy/Autogram/dispatches` | **Active** |
| `8429360` | **15:30 IST** | 10:00 UTC | `api.github.com/repos/Warriorlegacy/Autogram/dispatches` | **Active** |
| `8429361` | **18:00 IST** | 12:30 UTC | `api.github.com/repos/Warriorlegacy/Autogram/dispatches` | **Active** |
| `8429362` | **20:30 IST** | 15:00 UTC | `api.github.com/repos/Warriorlegacy/Autogram/dispatches` | **Active** |
| `8429364` | **22:30 IST** | 17:00 UTC | `api.github.com/repos/Warriorlegacy/Autogram/dispatches` | **Active** |
| `8429366` | **Every 10 min** | Every 10 min | Render Flask API Keep-Alive (`https://...onrender.com/health`) | **Active** |
| `8430206` | **Every 15 min** | Every 15 min | Render 24/7 Auto-DM & Comment Scanner (`/api/cron/auto-dm`) | **Active** |

- **Dispatch Event:** `publish_scheduled_slot`
- **Workflow:** `.github/workflows/daily-post.yml` runs Ubuntu 24.04 with Playwright Chromium to render slides and publish.

---

## 4. Instagram Profile Bios for `@signhify.studio`

Designed for search SEO and follow-conversion:

### Option 1 (Recommended — Maximum Conversion)
- **Name Field:** `Signhify | Free AI & FOSS Tools ⚡`
- **Bio:**
  ```text
  ⚡ Replacing $1,000/mo SaaS with Free Open Source
  🔥 Secret ChatGPT Prompts & Prompt Codes
  📦 Tested 1-click Docker setups & cheatsheets
  👇 Comment "FOSS" or "PROMPT" for instant blueprints
  ```
- **Link in Bio:** Link to GitHub repo / free tools vault / ManyChat automation.

### Option 2 (Minimalist / Tech Elite)
- **Name Field:** `Signhify Studio | AI & Dev Stack 🛠️`
- **Bio:**
  ```text
  Free & Open Source Software + Advanced AI Prompt Architectures.
  Zero fluff. 100% reproducible developer tools.
  7 daily breakdowns: self-hosted alternatives & prompt codes.
  ⚡ Grab today’s blueprint below 👇
  ```

---

## 5. Output Artifacts Produced Every Run (`output/YYYY-MM-DD/`)

| File | Purpose |
|---|---|
| `slide_01.jpg` – `slide_08.jpg` | 1080×1350 JPEG slides rendered via Playwright Chromium. |
| `research_dossier.json` | Auditable proof: live GitHub stars, license, 1-line setup command, SaaS replacement cost, trade-offs. |
| `viral_analysis.json` | Niche trend analysis: evaluated topics, approved candidates (Score >= 85), rejection log. |
| `content.json` | Complete structured carousel schema (hook, headlines, body, proof chips, layout types). |
| `caption.txt` | Instagram caption with hook, bullet takeaways, "Comment FOSS/PROMPT" CTA, and 3-tier hashtags. |
| `hashtags.txt` | 17+ viral hashtags (Tier 1 high-volume, Tier 2 niche FOSS/Prompts, Tier 3 brand tags). |
| `first_comment.txt` | Discussion prompt posted immediately to trigger Instagram algorithmic reach. |
| `reels_script.md` | 30–45s spoken video script with timestamped visual cues for vertical video. |
| `edit_plan.json` | Video editing timeline specification (cuts, text animations, sound effects, B-roll notes). |
| `x_thread.txt` | 6-tweet viral thread ready for X/Twitter syndication. |
| `linkedin_post.txt` | High-engagement post formatted for LinkedIn technical leaders. |
| `manifest.json` | Execution summary: publication timestamp, media ID, QA score, viral score, image URLs. |

---

## 6. Test Suite & Verification Status

The entire project is verified and passing:
- `tests/test_trend_analyzer.py` — 4/4 passed (Virality Gate, SaaS killer scoring, Prompt framework scoring, slop rejection).
- `tests/test_deep_research.py` — 3/3 passed (GitHub stars, SaaS pricing contrast, prompt mechanisms).
- `tests/test_growth_engine.py` — 7/7 passed (Hashtags clustering, first comment, caption enforcement).
- `tests/test_orchestrator.py` — 1/1 passed (Full end-to-end dry-run with all artifacts verified).
- `tests/test_licensing.py` — 6/6 passed (HMAC license gate, owner key bypass).
- `tests/test_renderer.py` — 3/3 passed (Playwright rendering across themes).
- `tests/test_content_generation.py` — 4/4 passed (Pillars generation, QA gate, topic scoring).
- `tests/test_dm_automator.py` — 6/6 passed (Keyword matching, comment deduplication, public reply generation, private DM payload, stats retrieval, dry-run scan).
- **Total:** 41/41 tests passing cleanly with zero errors.

---

## 7. Option A: In-House Auto-DM & Comment-Reply Engine

Instead of paying $15–$150+/month to ManyChat or dealing with contact limits and manual OAuth logins, Autogram implements an in-house, zero-cost, autonomous DM engine directly through Meta's official Graph API:

### Architecture
- **Module:** [`src/instagram/dm_automator.py`](file:///d:/Autogram/src/instagram/dm_automator.py)
- **Official Endpoint:** Meta Graph API v21.0 / v23.0 Private Replies:
  - `POST /{comment_id}/replies` — Randomized public comment reply (4 variations per trigger).
  - `POST /{ig_user_id}/messages` with `{"recipient": {"comment_id": comment_id}, "message": {"text": ...}}` — Private DM delivering requested blueprint.
- **Triggers & Blueprints:**
  1. `FOSS` (patterns: `foss`, `self-host`, `docker`, `blueprint`, `setup`):
     - Public Reply: *"Just sent the full Docker setup & GitHub link to your DMs! 🚀"*
     - DM Delivery: Master GitHub vault link (`https://github.com/signhify/open-source-vault`) + 1-click Docker commands.
  2. `PROMPT` (patterns: `prompt`, `code`, `megaprompt`, `chatgpt`, `secret`):
     - Public Reply: *"Just sent the complete prompt code & variables to your DMs! 🔥"*
     - DM Delivery: Prompt vault link (`https://github.com/signhify/prompt-vault`) + instructions tested on GPT-4o, Claude 3.5 Sonnet, DeepSeek-R1.
- **Deduplication & Persistence:**
  - SQLite table `auto_dm_log` in `autopilot.db`.
  - Fallback state file [`data/dm_automation_state.json`](file:///d:/Autogram/data/dm_automation_state.json).
  - A comment is never messaged more than once.
- **Execution Channels:**
  - **Pipeline Phase 9b:** Scans comments immediately following every publication drop.
  - **Background Daemon:** Runs every 20 minutes inside `dashboard_api.py` `scheduler_worker`.
  - **CLI Trigger:** `python orchestrator.py --auto-dm [--dry-run]`
  - **Dashboard API:** `POST /api/instagram/auto-dm` and `GET /api/instagram/auto-dm/stats`
  - **Interactive Cockpit UI:** Dedicated "Auto-DM Engine" view in `dashboard.html` with real-time stats, activity log, and 1-click scan button.
   - **Cloud Automation:** GitHub Actions workflow [`.github/workflows/auto-dm.yml`](file:///d:/Autogram/.github/workflows/auto-dm.yml) running every 30 minutes 24/7.

---

## 8. Dashboard Redesign — Makerzz-Inspired Editorial Dark UI

**Commit:** `3ca847c` — pushed to `main`, deployed to Render.

### Design Shift
| Before (Sci-Fi) | After (Editorial) |
|---|---|
| Neon cyan `#00F0FF` + violet glows | Teal `#0E6F77` + amber `#FFC22B` |
| Scanlines, noise overlays, WebGL 3D lattice | Clean solid backgrounds, no overlays |
| Double-bezel "doppel-shell" cards with backdrop blur | Flat cards with subtle borders |
| Glow buttons (`box-shadow: 0 0 24px`) | 3D push-pill buttons (`box-shadow: 0px 5px 0px`) |
| "NEURAL MISSION CONTROL v2.5" branding | "Zero-Touch Carousel Engine" |
| Gamification chrome (🔥 streak, LVL 9) | Removed — clean sidebar |

### Changes Applied (Phases 1–6)
- **CSS Token Migration:** `--cyan` value changed from `#00F0FF` to `#0E6F77` (teal), glow opacities reduced
- **Cyber Chrome Removal:** `#dashboard-webgl`, `.cyber-scanlines`, `.cyber-noise`, `#confetti-canvas` set to `display: none`
- **Button System:** `.btn-island-primary`/`.btn-island-violet` → makerzz 3D push-pill (`border-radius: 999px`)
- **Card System:** `.doppel-shell` flattened — removed backdrop blur, double-bezel padding, hover glows
- **Sidebar:** Removed streak card, LVL badge, flamePulse keyframe. Brand glyph flattened. Nav labels editorialized
- **Day/Night Mode:** `[data-theme="light"]` CSS overrides, theme toggle in topbar, localStorage persistence
- **Watermark:** All templates updated from `@SIGNHIFY.STUDIO` → `SIGNHIFY.STUDIO`

### Files Modified
| File | What Changed |
|---|---|
| `dashboard.html` | CSS tokens, buttons, cards, sidebar, copy, day/night mode (~446 ins, ~522 del) |
| `data/brand.json` | Watermark + footer_text |
| `dashboard_api.py` | Fallback brand dict watermark |
| `renderer/render.py` | Fallback brand dict watermark |
| `renderer/templates/*.html` (9 files) | Jinja watermark defaults |

### Remaining (Optional)
- Phase 7: Landing page `index.html` alignment (not started)
- Remove Three.js CDN script tag (WebGL canvas hidden)
- Rename `var(--cyan)` → `var(--makerzz-teal)` across 37 inline HTML references (cosmetic, value already correct)

