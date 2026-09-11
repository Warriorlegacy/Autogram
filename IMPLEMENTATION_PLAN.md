# Autogram Dashboard Redesign — Implementation Plan

**Date:** 2026-09-11
**Reference:** https://makerzz.space
**Target:** https://autogram-dashboard.onrender.com/dashboard (dashboard.html + index.html)

---

## 1. Current State Analysis

### What exists
| File | What it does | Lines |
|---|---|---|
| `dashboard.html` | Monolith SPA — 4,696 lines, inline CSS + HTML + JS | ~4,700 |
| `index.html` | Marketing landing page | 770 |
| `css/landing.css` | Landing page design tokens + layout | 397 |
| `css/components.css` | Simulator, pricing, terminal, modal, toast | 771 |
| `js/*.js` | Three.js scene, carousel simulator, ROI calc, auth | 5 files |
| `renderer/css/design-system.css` | Slide renderer tokens (850+ lines) | — |

### Current design identity
- **Dark OLED cyber-terminal** — neon cyan/violet glows, scanlines, WebGL 3D lattice, "Neural Mission Control" branding
- **Fonts:** Archivo + Space Grotesk + JetBrains Mono
- **Palette:** `#060606` void, `#00F0FF` cyan, `#8B5CF6` violet, `#10B981` emerald, `#FFC22B` amber
- **Cards:** Double-bezel "doppel-shell" with frosted glass inner core

### Makerzz reference identity
- **Clean editorial dark** — no scanlines, no 3D lattices, no terminal aesthetic
- **Fonts:** Archivo (display) + Space Grotesk (body) + JetBrains Mono (code) — same stack, different application
- **Palette:** `#060606` void, `#0E6F77` teal, `#FFC22B` amber, `#10222A` ink — **warm, not neon**
- **Buttons:** Pill-shaped (`border-radius: 999px`), 3D shadow (`box-shadow: 0px 5px 0px`), amber primary
- **Cards:** Flat with subtle borders, no glow effects, no double-bezel
- **Layout:** Generous whitespace, single-column hero, no sidebar dashboard

---

## 2. Gap Analysis: What to Change

### HIGH PRIORITY (visual identity shift)

| # | Area | Current (Autogram) | Target (Makerzz-like) | Effort |
|---|---|---|---|---|
| 1 | **Remove scanlines + noise overlays** | `body::after` scanlines, `.cyber-scanlines`, `.cyber-noise` | Clean solid backgrounds | Delete 3 CSS rules |
| 2 | **Remove WebGL 3D lattice** | `#dashboard-webgl` Three.js canvas | No 3D background | Remove `<canvas>` + script |
| 3 | **Button system** | Neon glow pill buttons with cyan glow shadows | 3D push-effect pill buttons with `box-shadow: 0px 5px 0px #10222A` | Rewrite `.btn` classes |
| 4 | **Card system** | Double-bezel doppel-shell with frosted glass | Flat cards with `1px solid rgba(255,255,255,0.08)` borders | Rewrite `.doppel-shell` |
| 5 | **Color accent** | Cyan `#00F0FF` as primary accent | Teal `#0E6F77` + Amber `#FFC22B` as primary accents | Update CSS variables |
| 6 | **Typography tone** | "NEURAL MISSION CONTROL v2.5" sci-fi labels | Clean, editorial, product-focused labels | Rewrite headings/copy |
| 7 | **Sidebar** | 280px fixed sidebar with nav items | Makerzz has no sidebar — uses top nav or no nav in app | Decision needed |

### MEDIUM PRIORITY (layout + UX)

| # | Area | Change | Effort |
|---|---|---|---|
| 8 | **Hero/dashboard header** | Replace terminal telemetry bar with clean status bar | Rewrite topbar HTML+CSS |
| 9 | **Streak/level badges** | Remove gamification chrome (🔥 streak, LVL 9) | Delete sidebar streak card |
| 10 | **Pipeline terminal** | Replace terminal console with clean step-by-step progress | New component |
| 11 | **Platform grid** | Makerzz: horizontal icon row with labels. Ours: grid of cards with status | Restyle to match |
| 12 | **Pricing section** | Makerzz: 3 clean cards with bullet lists. Ours: already close but with neon glow | Remove glow, add 3D shadow |
| 13 | **FAQ/accordion** | Makerzz has clean FAQ. Ours: none on dashboard | Add FAQ component |
| 14 | **Footer** | Makerzz: minimal 3-column footer. Ours: none on dashboard | Add minimal footer |

### LOW PRIORITY (polish)

| # | Area | Change | Effort |
|---|---|---|---|
| 15 | **Animations** | Makerzz: subtle fade-in, no confetti/particles | Remove confetti canvas |
| 16 | **Mobile responsive** | Makerzz: clean mobile layout. Ours: sidebar breaks on mobile | Add mobile hamburger/nav |
| 17 | **Font weights** | Makerzz: lighter weights for body (400-500), bold only for headings | Audit weight usage |

---

## 3. Implementation Phases

### Phase 1: Design Token Migration (30 min)
**Goal:** Make the CSS variables match makerzz's palette and typography

**Files to edit:** `dashboard.html` `:root` block (lines 26-88)

```
Changes:
- --makerzz-teal: #0E6F77 (keep, already exists)
- --makerzz-amber: #FFC22B (keep, already exists)
- Remove --cyan, --cyan-glow as PRIMARY accents
- Make teal the primary interactive color
- Make amber the CTA/primary action color
- Keep violet/emerald as secondary badges only
```

**Verify:** Every button, link, and badge still has visible contrast on `#060606` background.

### Phase 2: Remove Cyber Chrome (15 min)
**Goal:** Strip the sci-fi overlays that makerzz doesn't have

**Delete these CSS rules from dashboard.html:**
- `body::after` scanlines (lines ~118-132)
- `.cyber-noise` (lines ~134-141)
- `#confetti-canvas` (line ~143-148)
- `#dashboard-webgl` canvas element + Three.js script tag

**Delete from index.html:**
- `css/landing.css` scanlines rule (lines 52-62)
- `js/three-scene.js` script tag

### Phase 3: Button System Rewrite (45 min)
**Goal:** Replace neon glow buttons with makerzz-style 3D push buttons

**Current:** `.btn-island-primary` with `box-shadow: 0 0 24px var(--cyan-glow)`
**Target:** `.btn-makerzz-primary` with `box-shadow: 0px 5px 0px #10222A` (already partially implemented in lines 697-749)

**Action:**
1. Make `.btn-makerzz-amber` the default primary button
2. Make `.btn-makerzz-white` the secondary button
3. Remove `.btn-island-primary`, `.btn-island-violet`, `.btn-primary` glow variants
4. Update all button references in HTML

### Phase 4: Card System Rewrite (30 min)
**Goal:** Replace doppel-shell cards with flat makerzz-style cards

**Current:** `.doppel-shell` with backdrop-filter blur + double border
**Target:** Simple `.card` with `background: var(--bg-surface)`, `border: 1px solid var(--border-outer)`, `border-radius: 16px`

**Action:**
1. Create `.card` class matching makerzz flat card style
2. Replace all `.doppel-shell > .doppel-core` patterns
3. Remove backdrop-filter blur from cards (keep it only on sidebar/topbar)

### Phase 5: Layout Restructure (1-2 hrs)
**Goal:** Restructure dashboard to match makerzz's clean single-column flow

**Decision: Keep sidebar or go top-nav?**
- Makerzz: no sidebar in app, top nav with pills
- Current Autogram: 280px sidebar with 15+ nav items
- **Recommendation:** Keep sidebar but make it collapsible on mobile, clean up nav items

**Action:**
1. Reduce sidebar width from 280px to 260px
2. Remove streak/level gamification card from sidebar
3. Clean up nav labels: "Command & Control" → "Dashboard", "Content Studio & Publish LIVE" → "Studio"
4. Remove emoji prefixes from nav items
5. Add a clean topbar with user avatar + minimal telemetry (not terminal-style)

### Phase 6: Content/Copy Rewrite (1 hr)
**Goal:** Replace sci-fi terminal copy with makerzz-style editorial copy

**Examples:**
| Current | Makerzz-style |
|---|---|
| "NEURAL MISSION CONTROL v2.5" | "Dashboard" |
| "⚡ Mission Control" | "Overview" |
| "✍️ Content Studio & Publish LIVE" | "Studio" |
| "🛡️ Proof & Gate Ledger (P0-P8)" | "Pipeline" |
| "🚀 Pipeline Console" | "Runs" |
| "Live Telemetry" | "Status" |
| "Autonomous 7x Daily Publishing Daemon" | "Auto-publishing schedule" |

### Phase 7: Landing Page Alignment (1 hr)
**Goal:** Make index.html match makerzz's landing page structure

**Makerzz landing structure:**
1. Clean top nav (logo + 6 links + CTA)
2. Hero: "Paste your social media here" with input + platform pills
3. "How it runs" — 4-step numbered flow with images
4. "What you actually get" — screenshot walkthrough carousel
5. "What autopilot means" — growth chart + feature grid
6. "Where it posts" — platform icon row
7. FAQ accordion
8. CTA footer

**Autogram current structure:**
1. HUD telemetry bar + nav
2. Hero: "Turn Instagram Into An Autonomous B2B Acquisition Engine"
3. 3D Carousel Simulator
4. Architecture section
5. ROI Calculator
6. Pricing cards
7. Terminal console

**Action:**
1. Remove HUD telemetry bar from index.html
2. Simplify hero to makerzz-style clean headline + input CTA
3. Replace 3D simulator with clean screenshot walkthrough
4. Replace terminal with FAQ accordion
5. Keep pricing cards but restyle to match makerzz flat style

---

## 4. File Change Summary

| File | Action | Est. Lines Changed |
|---|---|---|
| `dashboard.html` | Major edit — CSS tokens, remove scanlines, rewrite buttons/cards, restructure layout | ~800 |
| `index.html` | Major edit — remove HUD bar, rewrite hero, add FAQ, clean up structure | ~300 |
| `css/landing.css` | Medium edit — remove scanlines, update tokens to match new palette | ~50 |
| `css/components.css` | Medium edit — restyle pricing cards, remove terminal glow | ~80 |
| `js/three-scene.js` | Delete or gut (no 3D background) | -120 |
| `js/app.js` | Minor — remove confetti, sound synthesizer references | ~30 |

**New files needed:** None. All changes are edits to existing files.

---

## 5. What NOT to Change

These Autogram features are stronger than makerzz and should stay:

- **Sidebar navigation** — makerzz doesn't have a dashboard like this; our sidebar is better for power users
- **Platform connection grid** — our 13-platform grid with status badges is more detailed
- **Pipeline state machine visualization** — makerzz describes it in prose; we show it live
- **Auto-DM engine** — unique feature, not in makerzz
- **Cron-job.org webhook integration** — unique feature
- **3D Slide Deck Inspector** — our carousel viewer is more interactive
- **Brand.json design system** — the renderer design system is separate and should not change

---

## 6. Execution Order

```
Phase 1: Tokens        → 30 min  → Visual palette shifts immediately
Phase 2: Remove chrome → 15 min  → Clean, less noisy
Phase 3: Buttons       → 45 min  → Biggest visual impact
Phase 4: Cards         → 30 min  → Consistency
Phase 5: Layout        → 2 hrs   → Structural alignment
Phase 6: Copy          → 1 hr    — Tone alignment
Phase 7: Landing       → 1 hr    — Full alignment
                       ────────
                       ~5.5 hrs total
```

**Start with Phase 1+2+3 together** — these are all CSS-only changes that immediately make the dashboard feel makerzz-like without touching HTML structure.

---

## 7. Verification

After each phase, check:
1. `dashboard.html` renders in browser without JS errors
2. `index.html` renders without broken layouts
3. All buttons are clickable and have visible hover states
4. No neon glow artifacts remain (unless intentional)
5. Mobile viewport (< 768px) doesn't break
6. Existing API calls in `dashboard_api.py` still work (no backend changes needed)
