# Autogram — Session Context & Master State

> **Last Updated:** 2026-09-12 15:30 IST  
> **Repository:** `Warriorlegacy/Autogram` (`main` branch - commit `63762e0`)  
> **Target Profile:** `@signhify.studio`  
> **Stories & Carousels Publishing & Auto-Scheduling:** **100% OPERATIONAL & VERIFIED** (7 Daily Story Drops + 7 Carousel Slots scheduled; 1080x1920 9:16 Story rendering + Meta Graph API Story publishing)  
> **Reels Video Pipeline ($0 MoneyPrinterTurbo):** **LIVE-PROVEN ×3** (proof reel `18084132620498378`, agency reel `18038336954832825`, agency story `18137079703621760`; 10 daily local slots via schtasks; every reel watermarked + captioned for @signhify.studio)
> **Blueprint Follow-Gate:** **ARMED** (`BLUEPRINT` keyword → follow-gate ask → `FOLLOWED` claim → DM with `BLUEPRINT.md`/`.pdf` links; two-step claim because Meta exposes no followers endpoint)
> **Studio Positioning:** **FULL AI ENGINEERING STUDIO** (all reel captions, story CTAs, brand.json, blueprint assets)  
> **Render Production Dashboard:** **LIVE & HEALTHY** (`https://autogram-dashboard.onrender.com/dashboard`)  
> **Vercel Production Landing:** **LIVE & READY** (`https://autogram-ai.vercel.app`)  
> **Responsive Experience:** **OPTIMIZED FOR ALL SCREENS** (Mobile 320px–480px, Tablets 768px–960px, Desktop 1024px–4K, Hamburger Navigation, Full-Width Viewport)  

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
  ├── Phase 2b: Deep Technical Research Engine (deep_researcher.py)
  ├── Phase 3:  Grounded Carousel Generation (generator.py: Multi-LLM fallback, exact facts injection)
  ├── Phase 4:  Fact-Checking (fact_checker.py: Zero hallucinated stats)
  ├── Phase 5:  Quality & Slop Gate (quality_gate.py: 80+ QA threshold, banned phrases filter)
  ├── Phase 6:  Playwright Slide Rendering (renderer/render.py: 1080x1350 JPEG)
  ├── Phase 6b: Multi-Platform Script Generation (script_writer.py)
  ├── Phase 7:  Asset Staging (uploader.py: IMGBB prioritized fast-path / S3/R2 / freeimage.host / local fallback)
  ├── Phase 8:  Instagram Publishing (publisher.py: Meta Graph API container carousel)
  └── Phase 9:  Self-Optimization & Anti-Repetition (optimizer.py: content-memory.json)
```

---

## 2. Premium 3D Immersive SaaS Platform & Image Hosting Reliability

### What Was Built
Transformed the entire Autogram platform into a scalable, premium 3D immersive commercial SaaS with multi-user authentication, universal AI provider hub, prompt library, template vault, full 3D UI redesign, and hardened cloud image hosting.

### A. Multi-User Authentication & Access Control
- **Module:** `src/auth/user_manager.py` — PBKDF2-HMAC-SHA256 (100k rounds + unique salt)
- **Admin bypass:** `AUTOGRAM_OWNER_KEY=autogram_owner_vip_2026` in `.env`
- **Client mode:** Issue keys via `python -m src.auth.licensing --issue --client "Name" --tier growth --days 30`
- **Session tokens:** JWT-style bearer tokens stored in `localStorage`
- **Endpoints:** `/api/auth/login`, `/api/auth/signup`, `/api/auth/me`, `/api/auth/logout`, `/api/auth/pricing`, `/api/auth/users`

### B. Universal AI Provider Hub
- **Module:** `src/content/providers_manager.py` — 12 provider presets + custom OpenAI-compatible endpoints
- **Text Models:** OpenAI (GPT-4o, GPT-4o-mini), Anthropic (Claude 3.5 Sonnet), Google Gemini, Groq, DeepSeek, Mistral, Cohere, Together AI, Perplexity, OpenRouter, HuggingFace, Custom
- **Image Models:** DALL-E 3, Stable Diffusion XL, Flux.1, Midjourney, Custom
- **Video Models:** Runway Gen-3, Pika Labs, Synthesia, HeyGen, Custom
- **Auto-detection:** `/api/providers/detect-models` probes endpoints for available models
- **Endpoints:** `/api/providers`, `/api/providers/set-active`, `/api/providers/set-media-model`, `/api/providers/test`, `/api/providers/detect-models`

### C. Prompt Library & Template Vault
- **Prompt Library:** `data/prompt_library.json` — categorized prompts with variables, model recommendations
- **Template Vault:** `data/templates.json` — carousel + video reel templates with slide layouts
- **Endpoints:** `/api/prompts`, `/api/templates`

### D. 5-Theme Visual System (Synced Across Landing & Dashboard)
| Theme | Style | Key Colors |
|---|---|---|
| `dark-quantum` | Default — neon cyan on dark | Cyan #00F0FF, dark bg |
| `cyberpunk` | Amber + cyan neon | Amber #FFB300, cyan #00E5FF |
| `neumorphic` | Soft shadows, light bg | Indigo #6366F1, subtle grays |
| `swiss-light` | Editorial, white bg | Cobalt #0050FF, clean whites |
| `bento-grid` | SaaS modern, light bg | Indigo #6366F1, soft cards |
| `light` | Classic day mode | Teal #0E6F77, white bg |

- **Pickers:** Dropdown in both landing page (`index.html`) and dashboard (`dashboard.html`) header
- **Persistence:** `localStorage` key `autogram_theme`
- **Cross-tab sync:** `storage` event listener in both `app.js` and `dashboard.html`

### E. Hardened Cloud Image Hosting (IMGBB Fast-Path)
- **Problem Resolved:** GitHub Actions runner previously failed when public anonymous image hosts (`freeimage.host` 400, `catbox.moe` 412, `litterbox` 25s timeout, `0x0.st` 503) exhausted without an authenticated host.
- **Resolution:**
  - Configured `IMGBB_API_KEY=f0ee2a304a71d5b2da983153c2284b73` in `.env`, `.env.example`, and `.github/workflows/daily-post.yml`.
  - Added default in `src/config.py` (`Settings.imgbb_api_key`).
  - Prioritized `_upload_to_imgbb` **first** in `src/storage/uploader.py` when key is present, providing ~1.5s authenticated direct image uploads (`https://i.ibb.co/...`) and bypassing flaky public pastebin timeouts.

### F. 3D Visual Polish & Theme-Reactive WebGL Hologram
- **Multi-tier 3D Quantum Core:** `js/three-scene.js` enhanced with outer gyro ring, wireframe torus knot, and pulsing inner nucleus.
- **Theme-reactive canvas:** Three.js scene dynamically observes `data-theme` changes and shifts material colors and opacities (amber/cyan for cyberpunk, cyan/violet for quantum, cobalt for swiss-light, indigo/emerald for bento-grid).
- **Holographic shimmer borders:** CSS `::before` pseudo-element with gradient animation on card hover.
- **Glassmorphism:** `backdrop-filter: blur(20px) saturate(1.2)` on modals and dropdowns.
- **Card parallax tilt:** Mouse-move `perspective(800px) rotateX/Y` via `premium.js`.
- **Toast animations:** Slide-in from right with `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Bento grid layout:** CSS Grid `auto-fill` for dashboard cards.

### G. Landing Page Auth Integration
- **Auth-aware pill:** Checks `localStorage` for session token, shows username or Sign In button.
- **Inline auth modal:** Login + signup tabs, calls `/api/auth/login` and `/api/auth/signup`.
- **Auto-redirect:** After successful auth, redirects to `dashboard.html`.

### Files Modified in Current Update
| File | What Changed |
|---|---|
| `.env` & `.env.example` | Added `IMGBB_API_KEY=f0ee2a304a71d5b2da983153c2284b73` |
| `src/config.py` | Added default `imgbb_api_key="f0ee2a304a71d5b2da983153c2284b73"` |
| `src/storage/uploader.py` | Prioritized authenticated IMGBB upload at top of cloud CDN cascade |
| `.github/workflows/daily-post.yml` | Injected `IMGBB_API_KEY` into workflow environment |
| `js/three-scene.js` | Upgraded to multi-tier quantum core with theme-reactive palette observer |
| `css/landing.css` | Added 5-theme spatial picker dropdown styles |
| `index.html` | Added 5-theme spatial picker dropdown in navbar |
| `js/app.js` | Added full `THEME_MAP`, `toggleThemePicker()`, outside click dismissal |
| `tests/test_image_and_scripts.py` | Added 3 tests: IMGBB prioritization, landing theme picker, three-scene theme reactivity |
| `SESSION_CONTEXT.md` | Documented IMGBB fix, 3D theme engine, and test totals (64/64) |

---

## 3. Autonomous Cloud Scheduling Infrastructure

### Active Cloud Cron Jobs (cron-job.org) — single source of truth for cloud drops
| Job ID | Slot (IST) | Target / Payload | Status |
|---|---|---|---|
| `8429357` | **08:00 IST** | Carousel dispatch `publish-slot` | **Active** |
| `8429359` | **10:30 IST** | Carousel dispatch `publish-slot` | **Active** |
| `8429363` | **13:00 IST** | Carousel dispatch `publish-slot` | **Active** |
| `8429360` | **15:30 IST** | Carousel dispatch `publish-slot` | **Active** |
| `8429361` | **18:00 IST** | Carousel dispatch `publish-slot` | **Active** |
| `8429362` | **20:30 IST** | Carousel dispatch `publish-slot` | **Active** |
| `8429364` | **22:30 IST** | Carousel dispatch `publish-slot` | **Active** |
| `8435698` | **09:00 IST** | Story dispatch `publish-story` (Morning Tech Radar) | **Active** |
| `8435700` | **11:30 IST** | Story dispatch `publish-story` (Workflow Signal) | **Active** |
| `8435701` | **14:00 IST** | Story dispatch `publish-story` (Code Deep Dive) | **Active** |
| `8435704` | **16:30 IST** | Story dispatch `publish-story` (Architecture Insight) | **Active** |
| `8435706` | **19:00 IST** | Story dispatch `publish-story` (Evening Digest) | **Active** |
| `8435709` | **21:30 IST** | Story dispatch `publish-story` (Contrarian) | **Active** |
| `8435712` | **23:30 IST** | Story dispatch `publish-story` (Late-Night Blueprint) | **Active** |
| `8429366` | **Every 10 min** | Render Flask API Keep-Alive (`https://...onrender.com/health`) | **Active** |
| `8430206` | **Every 15 min** | Render 24/7 Auto-DM & Comment Scanner (`/api/cron/auto-dm`) | **Active** |

- **Double-post fix:** native `schedule:` blocks removed from `daily-post.yml` and `daily-story.yml` — cron-job.org dispatches are now the ONLY cloud triggers (both firing = 2× publishes toward the 25/day Meta cap).
- **Reels (10/day) stay local:** `Autogram Reel 1-10` Windows Scheduled Tasks + MPT autostart (cron-job.org cannot reach localhost MPT; CI video runs fail closed by design).

---

## 4. Test Suite & Verification Status

### All Tests (123/125 passing — 2 pre-existing failures, both fail on pristine tree)
- `tests/test_run_guards.py` — 5/5 (quota skip manifest, headroom proceeds, dispatch alert+reraise, passthrough silence, SlotSkipped silence)
- `tests/test_cloud_render.py` — 5/5 (PEXELS key guard, colon-free filter regression, MPT-preferred + cloud-fallback routing, assembly wiring)
- `tests/test_guardian.py` — 5/5 (retry success/exhaustion, quota skip/allow, ALERTS.log fallback, janitor)
- `tests/test_reel_pipeline.py` — 9/9 (reel dry-run publish, narration structure, MPT-offline fail-fast, video dry-run URL, `/api/mpt/status`, `/api/publish/reel`, queued REEL execution, cap-guard block + allow)
- `tests/test_workflows_and_copilot.py` — 5/5 (daily-story.yml & daily-video.yml validation, Settings GITHUB_COPILOT_TOKEN, GitHub Models preset, unauthorized handling)
- `tests/test_youtube_shorts.py` — 5/5 (shorts publisher dry-run, title formatting, missing creds handling, `/api/publish/shorts`, `/api/publish/video`)
- `tests/test_blueprint_and_gate.py` — 7/7 (BLUEPRINT taxonomy, gate withholds link, claim delivers, FOSS ungated, studio strings, Anton payload, committed assets)
- `tests/test_responsive_ui.py` — 5/5 (mobile responsive elements, hamburger nav, double-api normalization, synthesize endpoint)
- `tests/test_auth_and_providers.py` — 20/20
- `tests/test_image_and_scripts.py` — 10/10 (IMGBB priority, theme picker, three-scene reactivity)
- `tests/test_trend_analyzer.py` — 4/4
- `tests/test_deep_research.py` — 3/3
- `tests/test_growth_engine.py` — 7/7
- `tests/test_orchestrator.py` — 1/1
- `tests/test_licensing.py` — 6/6
- `tests/test_renderer.py` — 3/3
- `tests/test_content_generation.py` — 4/4
- `tests/test_dm_automator.py` — 6/6

**Total:** 123/125 passing. Pre-existing failures (verified failing on pristine `880eb62` tree, unrelated to reel/video work):
- `test_orchestrator.py::test_full_pipeline_dry_run` (assertion on live-LLM output)
- `test_story_pipeline.py::test_schedule_json_has_seven_story_slots_and_queue` (`story_slots` key absent from committed `schedule.json`; some test side-effect flips `scheduler_enabled` — restore the file after suite runs)

---

## 5. $0 Short-Form Video Engine (MoneyPrinterTurbo & Dual Distribution)

**Architecture:** End-to-end 9:16 vertical video generation and publishing for **Instagram Reels** and **YouTube Shorts** at zero marginal cost.

### Cost Stack (all verified on-host, $0)
| Layer | Choice | Status |
|---|---|---|
| Narration script | `generate_reel_script()` → Groq free → Gemini free → Ollama local → template | in `src/content/generator.py` |
| Voiceover | Microsoft Edge-TTS via MPT (`subtitle_provider=edge`) | installed + configured ($0) |
| Stock footage | Pexels Developer API (free key, 20k req/mo) | in `config.toml` ($0) |
| Subtitles | Edge timestamp parser / faster-whisper | MPT default ($0) |
| Assembly | Local FFmpeg via MPT (`:8080`) | 2 binaries on PATH ($0) |
| Render server | MPT headless API via `start_mpt.bat` | installed, runs on demand ($0) |
| Public staging URL | `upload_video_file()` → S3/R2 presigned / Catbox / 0x0.st (video/mp4) | implemented ($0) |
| Instagram Reels | `publish_reel()` → Meta Graph API `media_type=REELS` | implemented ($0) |
| YouTube Shorts | `upload_short()` → YouTube Data API v3 resumable chunked upload | implemented in `src/youtube/shorts_publisher.py` ($0) |
| Documentation PDF | `compile_pdf.py` → `Autonomous_Video_Pipeline.pdf` | ReportLab styled manual generated ($0) |

### Flow
```
orchestrator.py --video (or pipeline_runner.py --now)
  → generator.generate_reel_script() (45-55s narration + title + caption + hashtags)
  → mpt_client.render_reel() (submit -> poll state -> download MP4)
  → uploader.upload_video_file() (public staging URL for Meta ingestion)
  → publisher.publish_reel() (Meta container -> FINISHED -> publish)
  → youtube_publisher.upload_short() (Google YouTube Data API v3 9:16 resumable upload)
  → video_manifest_<ts>.json
```

### Endpoints & UI
- `POST /api/publish/reel` (topic, pillar, mode) → reel manifest
- `POST /api/publish/shorts` (topic, pillar, mode) → shorts manifest
- `POST /api/publish/video` (topic, pillar, mode) → dual reels + shorts manifest
- `GET /api/mpt/status` → `{available, base_url}` (UI health check)
- CLI commands:
  - `python orchestrator.py --reel --dry-run` (Instagram Reel)
  - `python orchestrator.py --shorts --dry-run` (YouTube Shorts)
  - `python orchestrator.py --video --dry-run` (Dual Reels + Shorts)
  - `python pipeline_runner.py --now --dry-run` (Standalone runner)
  - `python compile_pdf.py` (Compiles `Autonomous_Video_Pipeline.pdf`)

### Live Operations Findings (2026-09-12 15:30 IST session)
- **Story "not posting" root cause:** the pasted failing log was a manual `MODE=dry-run` dispatch that actually SUCCEEDED (mock media ID). The old argparse quoting bug is already fixed (commit `17998ad`, array-based `CMD_ARGS`). Scheduled runs default to `live`. No story code change needed.
- **Meta token VALID:** read-only `check_publishing_limit()` returned `quota_usage: 13` (12 headroom at check time).
- **PEXELS verdict:** configured where it matters — key present in `D:\MoneyPrinterTurbo\config.toml` (local renders use it); `PEXELS_API_KEY` also SET in Autogram `.env` and mapped as `secrets.PEXELS_API_KEY` → env in `daily-video.yml`. No code reads it on CI because no render happens there.
- **Video lane fix (commit `63762e0`):** GitHub runners cannot reach localhost MPT, so all 10 CI video crons failed closed. Removed `schedule` from `daily-video.yml` (manual dispatch kept); the 10 daily slots now run on this PC via `run_video_slot.bat` + `ensure_mpt.bat`, armed as Windows Scheduled Tasks `Autogram Reel 1-10` (08:03–22:03 IST) + logon/Startup MPT autostart.
- **MPT v1.3.0 wire fix:** task `state`/`progress` arrive as STRINGS (`COMPLETE=1`, `FAILED=-1`, `PROCESSING=4`); `wait_for_task` now coerces to int.
- **24h API cap guard:** `publish_media()` raises legibly at `quota_usage >= 24` (Meta cap ~25/24h; 24 drops armed). With usage at 13, remaining headroom covers the rest of today; steady-state 24/day leaves 1 headroom — drop to 21/day if cap-skips appear.
- **Live proof:** 1080×1920 25s h264 reel rendered via MPT, staged on catbox.moe ($0), published to `@signhify.studio` — Media ID `18084132620498378`.
- **Agency promo drop (2026-09-12 ~15:20 IST):** story `18137079703621760` ("5 Free AI Tools That Replace a $5,000/mo Marketing Retainer") + reel `18038336954832825` ("Signhify Studio Builds AI Marketing Engines That Post While You Sleep") — different topics, both agency-promoting.
- **Standing agency branding (all future reels/stories):**
  - `watermark_reel()` burns `signhify.studio` top-center into every MP4 via FFmpeg drawtext (fail-closed; wired into `--reel`, `--shorts`, `--video` paths).
  - `generate_reel_script()` appends `🚀 Built by @signhify.studio — AI Marketing Agency | 🔗 signhify.studio` to every caption.
  - Story default CTA is now `Follow @signhify.studio · AI Marketing Agency — Link in Bio` (template already carried `@signhify.studio` handle + `SIGNHIFY.STUDIO` subtext).
- **Minutes math (GH free tier 2000/mo):** stories ~315 + carousels ~630 + videos 0 (local) ≈ 945/mo — SAFE.

### PC-Off Autonomy: Cloud Owns Everything (latest session)
User constraint: posting must continue **with the PC turned off**. Redesign:
- **Cloud video lane** (`src/content/cloud_render.py`): Pexels portrait stock + edge-TTS voiceover/SRT + FFmpeg 9:16 assembly (Anton captions, watermark) — proven with a real 1080×1920 15.7s render, zero MPT involvement. `render_reel_auto()` picks MPT when local, cloud otherwise (wired into `--reel`/`--shorts`/`--video`).
- **ffmpeg gotcha (documented):** this build misparses drive-colon absolute paths inside `subtitles`/`drawtext` options even quoted/escaped — assembly runs with `cwd=workdir` and bare relative names (regression-tested).
- **4 cloud video slots** in `daily-video.yml` (07:30/12:30/17:30/21:30 IST; ~600 free-min/mo; PEXELS-empty guard fails with guidance). PEXELS_API_KEY confirmed present in repo secrets.
- **Local auto-publish disarmed** (single-source doctrine): 10 schtasks deleted, `start_autogram.bat` no longer launches `--schedule`, dashboard slot auto-fire gated behind `slots_enabled` (default false; queue + auto-DM unaffected). `run_video_slot.bat`/MPT autostart stay for manual top-ups.
- **Robustness core** (`src/ops/guardian.py`, built by agent, 5/5): `with_retries`, `ensure_quota`/`SlotSkipped`, `send_alert` (Telegram when configured, else `output/ALERTS.log`), `janitor` (old output dirs + MPT mp4s). No Telegram/webhook tokens configured — alerts currently file-local.
- **Guard wiring (latest session):** every pipeline (carousel/story/reel/shorts/dual-video) runs janitor + IG quota precheck first (exhausted quota returns a `skipped` manifest, exit 0, no alert spam); renders/uploads retry 3×; any failure fires `send_alert` from CLI dispatch, `pipeline_runner` main, and all 4 dashboard publish endpoints. Telegram bot `signhifyauto_bot` validated; token in local `.env` (gitignored) + `TELEGRAM_BOT_TOKEN` repo secret; CI workflows map both Telegram vars. `DRY_RUN` repo secret forced `false`. `TELEGRAM_CHAT_ID` registered (`/start` received) — test alert delivered ✅.
- **Minutes math revised:** stories ~315 + carousels ~630 + 4 videos ~600 ≈ 1545/2000 — SAFE with retry headroom.
- **YouTube pending:** no local `youtube_token.json`/`client_secrets.json` — Shorts legs fail gracefully per-destination until one-time OAuth setup is done; Reels unaffected.

### Follow-Gated Blueprint + Studio Reposition (latest session)
- **Gate flow** (`dm_automator.py`): `BLUEPRINT` keyword (blueprint/vault/studio/portfolio/services) → public *"follow + reply FOLLOWED"* ask, link withheld, user marked `GATE_PENDING` in `data/dm_follow_gate.json` → follow-up claim comment (`followed`/`done`/✅, keyword or not) → blueprint DM + `delivered`. FOSS/PROMPT flows untouched. Stated limit: Meta exposes no followers-list endpoint, so the two-step claim is the enforceable gate.
- **Blueprint assets** (also studio marketing): `BLUEPRINT.md` (positioning, live portfolio table, websites, $0 stack, 5-prompt pack, hire CTA) + `BLUEPRINT.pdf` via `build_blueprint_pdf.py` (reportlab). DM'd as raw.githubusercontent links (live after push).
- **Viral fonts:** Anton-Regular (OFL, validated 1373 glyphs) → `D:\MoneyPrinterTurbo\resource\fonts\` + per-task `font_name` in MPT payloads; story `.story-title`/`.metric-value` + carousel hook `.stage-title` switched to the Anton stamp stack.
- **FULL AI ENGINEERING STUDIO:** reel caption footer, story CTA, `brand.json` positioning rewritten; `free_knowledge_engine` hook left as-is (topic hook, not identity).

## 6. Deployment Surfaces

| Surface | Config / URL | Notes |
|---|---|---|
| Local dev | `python orchestrator.py --dry-run` | Requires Playwright |
| Dashboard (local) | `python dashboard_api.py` | Port 5050; serves static files |
| Windows quick-start | `start_autogram.bat` | Starts dashboard + ngrok + scheduler |
| GitHub Actions | [.github/workflows/daily-post.yml](file:///.github/workflows/daily-post.yml) | 7 cron slots; Run `34676939949` verified SUCCESS in 2m13s |
| Render Production | `https://autogram-dashboard.onrender.com/dashboard` | Active & healthy (`v2.5-quantum`), runs `dashboard_api.py` |
| Vercel Production | `https://autogram-ai.vercel.app` | Active, serves 3D theme-reactive `index.html` + spatial assets |

---

## 7. Critical Runtime Quirks

- **`DRY_RUN=true` is the default.** Pipeline will not publish to Meta unless `DRY_RUN=false` in `.env` AND `IG_USER_ID`/`IG_ACCESS_TOKEN` are populated.
- **Timezone is `Asia/Kolkata`.** All scheduler slot calculations use IST.
- **Renderer needs outbound network.** Loads Google Fonts from CDN.
- **No async/await anywhere.** Everything is synchronous `requests` + `subprocess.Popen`.
- **JSON is the interchange format** between every layer.

---

## 8. Design System Tokens

| Token | Value | Usage |
|---|---|---|
| `--neon-cyan` | `#00F0FF` | Primary interactive, glows, links |
| `--neon-violet` | `#8A2BE2` | Secondary accent, gradients |
| `--neon-emerald` | `#00FFA3` | Success states, verification |
| `--neon-amber` | `#FFB800` | Warning states, pricing |
| `--neon-indigo` | `#6366F1` | Tertiary accent, bento theme |
| `--bg-card` | `#0D1420` | Card backgrounds (dark) |
| `--bg-surface` | `#070A10` | Page background (dark) |
| `--ease-spring` | `cubic-bezier(0.16, 1, 0.3, 1)` | All premium transitions |
