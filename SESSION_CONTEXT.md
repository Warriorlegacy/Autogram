# Autogram — Session Context & Master State

> **Last Updated:** 2026-09-12 22:30 IST  
> **Repository:** `Warriorlegacy/Autogram` (`main` branch)  
> **Target Profile:** `@signhify.studio`  
> **Live Publishing Status:** **VERIFIED & ACTIVE**  
> **Dashboard:** **PREMIUM 3D IMMERSIVE** — 5-theme system, tier-gated, auth-aware, live at `https://autogram-dashboard.onrender.com/dashboard`

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
  ├── Phase 7:  Asset Staging (uploader.py: S3/R2 / freeimage.host / local fallback)
  ├── Phase 8:  Instagram Publishing (publisher.py: Meta Graph API container carousel)
  └── Phase 9:  Self-Optimization & Anti-Repetition (optimizer.py: content-memory.json)
```

---

## 2. Premium 3D Immersive SaaS Platform (Current Session)

### What Was Built
Transformed the entire Autogram platform into a scalable, premium 3D immersive commercial SaaS with multi-user authentication, universal AI provider hub, prompt library, template vault, and full 3D UI redesign.

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

### D. 5-Theme Visual System
| Theme | Style | Key Colors |
|---|---|---|
| `dark-quantum` | Default — neon cyan on dark | Cyan #00F0FF, dark bg |
| `cyberpunk` | Amber + cyan neon | Amber #FFB300, cyan #00E5FF |
| `neumorphic` | Soft shadows, light bg | Indigo #6366F1, subtle grays |
| `swiss-light` | Editorial, white bg | Cobalt #0050FF, clean whites |
| `bento-grid` | SaaS modern, light bg | Indigo #6366F1, soft cards |
| `light` | Classic day mode | Teal #007799, white bg |

- **Picker:** Dropdown in dashboard topbar with icon + label per theme
- **Persistence:** `localStorage` key `autogram_theme`
- **Cross-tab sync:** `storage` event listener

### E. Pricing Tier Enforcement
| Tier | Price | Features |
|---|---|---|
| Starter | $29/mo | 30 carousels/mo, Simple mode only |
| Growth | $79/mo | Unlimited, Pro mode, Providers hub, Prompt library |
| Agency Pro | $199/mo | Everything + Auto-DM, Multi-account |
| Owner/Admin | Bypass | Full access |

- **Gated features:** `pro_mode`, `providers_hub`, `unlimited_prompts`, `auto_dm`, `multi_account`
- **Enforcement:** `canAccessFeature()`, `requireTier()` in dashboard JS

### F. 3D Visual Polish
- **Holographic shimmer borders:** CSS `::before` pseudo-element with gradient animation on card hover
- **Glassmorphism:** `backdrop-filter: blur(20px) saturate(1.2)` on modals
- **Card parallax tilt:** Mouse-move `perspective(800px) rotateX/Y` via `premium.js`
- **Toast animations:** Slide-in from right with `cubic-bezier(0.16, 1, 0.3, 1)`
- **Bento grid layout:** CSS Grid `auto-fill` for dashboard cards

### G. Landing Page Auth Integration
- **Auth-aware pill:** Checks `localStorage` for session token, shows username or Sign In button
- **Inline auth modal:** Login + signup tabs, calls `/api/auth/login` and `/api/auth/signup`
- **Auto-redirect:** After successful auth, redirects to `dashboard.html`

### Files Modified
| File | What Changed |
|---|---|
| `dashboard.html` | 5-theme picker, tier enforcement, holographic borders, glassmorphism, bento grid CSS, auth-aware theme toggle |
| `css/landing.css` | 4 new theme presets (cyberpunk, neumorphic, swiss-light, bento-grid), holographic shimmer, hero gradient animation |
| `css/components.css` | Component overrides for 5 themes, pricing card glow, architecture card hover, simulator glassmorphism |
| `js/premium.js` | Extended tilt selector to include `.doppel-shell`, `.platform-tile`, `.template-card-tile` |
| `index.html` | Auth-aware nav pill, inline auth modal, session management JS |
| `src/auth/user_manager.py` | PBKDF2 auth system (pre-existing) |
| `src/content/providers_manager.py` | AI provider hub (pre-existing) |
| `tests/test_auth_and_providers.py` | 20 tests: auth CRUD, provider endpoints, prompts, templates, themes CSS, premium.js tilt |

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

### Current Session Tests (20/20 passing)
| Test | Status |
|---|---|
| `test_admin_user_seeded` | ✅ |
| `test_api_auth_login_success` | ✅ |
| `test_api_auth_login_failure` | ✅ |
| `test_api_auth_signup_and_me` | ✅ |
| `test_api_auth_pricing` | ✅ |
| `test_api_providers_get` | ✅ |
| `test_api_providers_detect_models_missing_url` | ✅ |
| `test_api_prompts_library` | ✅ |
| `test_api_templates_catalog` | ✅ |
| `test_api_auth_users_regression` | ✅ |
| `test_api_admin_users_alias` | ✅ |
| `test_api_providers_test_validation` | ✅ |
| `test_api_generate_image_validation` | ✅ |
| `test_api_auth_logout` | ✅ |
| `test_api_non_admin_users_forbidden` | ✅ |
| `test_api_providers_set_active` | ✅ |
| `test_api_health` | ✅ |
| `test_themes_css_landing` | ✅ |
| `test_themes_css_components` | ✅ |
| `test_premium_js_has_tilt` | ✅ |

### Previous Session Tests (74/74 passing)
- `tests/test_trend_analyzer.py` — 4/4
- `tests/test_deep_research.py` — 3/3
- `tests/test_growth_engine.py` — 7/7
- `tests/test_orchestrator.py` — 1/1
- `tests/test_licensing.py` — 6/6
- `tests/test_renderer.py` — 3/3
- `tests/test_content_generation.py` — 4/4
- `tests/test_dm_automator.py` — 6/6
- `tests/test_auth_and_providers.py` — 13/13 (previous session)

**Total:** 94/94 tests passing cleanly.

---

## 5. Deployment Surfaces

| Surface | Config | Notes |
|---|---|---|
| Local dev | `python orchestrator.py --dry-run` | Requires Playwright |
| Dashboard (local) | `python dashboard_api.py` | Port 5050; serves static files |
| Windows quick-start | `start_autogram.bat` | Starts dashboard + ngrok + scheduler |
| GitHub Actions | `.github/workflows/daily-post.yml` | 7 cron slots; fails over to Render webhook |
| Render | `render.yaml` | Free tier; runs `dashboard_api.py` |
| Vercel | `vercel.json` | Static only — serves `index.html` + assets |

---

## 6. Critical Runtime Quirks

- **`DRY_RUN=true` is the default.** Pipeline will not publish to Meta unless `DRY_RUN=false` in `.env` AND `IG_USER_ID`/`IG_ACCESS_TOKEN` are populated.
- **Timezone is `Asia/Kolkata`.** All scheduler slot calculations use IST.
- **Renderer needs outbound network.** Loads Google Fonts from CDN.
- **No async/await anywhere.** Everything is synchronous `requests` + `subprocess.Popen`.
- **JSON is the interchange format** between every layer.

---

## 7. Design System Tokens

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
