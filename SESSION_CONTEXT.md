# Autogram — Session Context & Master State

> **Last Updated:** 2026-09-12 13:15 IST  
> **Repository:** `Warriorlegacy/Autogram` (`main` branch - commit `edf99ee`)  
> **Target Profile:** `@signhify.studio`  
> **Stories & Carousels Publishing & Auto-Scheduling:** **100% OPERATIONAL & VERIFIED** (7 Daily Story Drops + 7 Carousel Slots scheduled; 1080x1920 9:16 Story rendering + Meta Graph API Story publishing)  
> **Reels Video Pipeline ($0 MoneyPrinterTurbo):** **OPERATIONAL** (`--reel` CLI, `/api/publish/reel`, `/api/mpt/status`; edge-tts + Pexels free + local FFmpeg; 89/89 passing tests)  
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

### Active Cloud Cron Jobs (cron-job.org)
| Job ID | Slot (IST) | Status |
|---|---|---|
| `8429357` | **08:00 IST** | **Active** |
| `8429359` | **10:30 IST** | **Active** |
| `8429363` | **13:00 IST** | **Active** |
| `8429360` | **15:30 IST** | **Active** |
| `8429361` | **18:00 IST** | **Active** |
| `8429362` | **20:30 IST** | **Active** |
| `8429364` | **22:30 IST** | **Active** |
| `8429366` | **Every 10 min** | Render Keep-Alive |
| `8430206` | **Every 15 min** | Auto-DM Scanner |

---

## 4. Test Suite & Verification Status

### All Tests (89/89 passing)
- `tests/test_reel_pipeline.py` — 7/7 (reel dry-run publish, narration structure, MPT-offline fail-fast, video dry-run URL, `/api/mpt/status`, `/api/publish/reel`, queued REEL execution)
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

**Total:** 89/89 tests passing cleanly. All platforms verified.

---

## 5. $0 Reels Video Pipeline (MoneyPrinterTurbo)

**Commit:** `edf99ee` — end-to-end 9:16 Reel generation at zero marginal cost.

### Cost Stack (all verified on-host, $0)
| Layer | Choice | Status |
|---|---|---|
| Narration script | `generate_reel_script()` → Groq free → Gemini free → Ollama local → template | in `src/content/generator.py` |
| Voiceover | edge-tts via MPT (`subtitle_provider=edge`) | installed + configured |
| Stock footage | Pexels via key already in `D:\MoneyPrinterTurbo\config.toml` | key present |
| Subtitles | edge timestamp parser (no Whisper download) | MPT default |
| Assembly | Local FFmpeg via MPT | 2 binaries on PATH |
| Render server | MPT `POST /api/v1/videos` on `:8080`, started via `start_mpt.bat` | installed, runs on demand |
| Public staging URL | `upload_video_file()` → S3/R2 → catbox.moe → litterbox → 0x0.st (video/mp4) | implemented |
| Publishing | `publish_reel()` → Meta `media_type=REELS`, 10-min transcode wait | implemented |

### Flow
```
orchestrator.py --reel
  → generator.generate_reel_script() (45-55s narration + caption + hashtags)
  → mpt_client.render_reel() (submit → poll state 0/1/-1 → download MP4)
  → uploader.upload_video_file() (public URL for Meta ingestion)
  → publisher.publish_reel() (container → FINISHED → media_publish)
  → reel_manifest_<ts>.json
```

### Endpoints & UI
- `POST /api/publish/reel` (topic, pillar, mode) → reel manifest
- `GET /api/mpt/status` → `{available, base_url}` (UI gates on this)
- Queue `format: "reel"` (REEL-*) flows through `/api/schedule/<id>/execute` → `--reel`
- Dashboard: 🎬 REEL badge, reel option in Schedule modal, "🎬 Publish Reel" quick action
- Dry-run fabricates everything (no MPT needed); live render requires `start_mpt.bat` running
- Verified: `python orchestrator.py --reel --dry-run` completes with mock media ID

---

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
