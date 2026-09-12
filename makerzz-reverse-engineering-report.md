# makerzz.space — Reverse-Engineering Report

**Target:** https://makerzz.space/ (“Social Autopilot — Grow on social media on autopilot”)
**Capture date:** 2026-09-11 (UTC)
**Methods:** Firecrawl CLI (`map`, `scrape --format markdown/html/rawHtml/links/branding`), direct `Invoke-WebRequest` header checks, DNS (`Resolve-DnsName` A/NS/TXT), TLS cert inspection, `robots.txt` / `sitemap.xml` / `llms.txt` / `manifest.webmanifest` fetch, meta/JSON-LD/chunk analysis.
**Artifacts (local, not committed):** `.firecrawl/makerzz-*.json|html|md` — homepage HTML (51 KB), rawHtml JSON (113 KB rawHtml), branding JSON, links JSON, plus per-page markdown for `/`, `/how-it-works`, `/plans`, `/guide`, `/integrations`, `/sign-in`, `/trends`, `/proof`, `/faq`, `/contact`, `/calendar`.

> Observed vs. inferred is marked throughout. Observed = bytes/headers we actually fetched. Inferred = best-fit explanation, flagged as such.

---

## 1. Executive summary

makerzz.space is a **Next.js App Router (React Server Components) app deployed via OpenNext on Cloudflare Workers, fronted by Cloudflare CDN/DNS/SSL**. It is a thin-browser, heavy-server SaaS: the marketing site + Studio/Calendar/Connect app shell ships as static/prerendered RSC payloads; all valuable work (niche scan, strategy, script, edit plan, carousel prompt compiler, credit ledger) runs server-side behind metered API calls.

The current product is **“Social Autopilot”**: paste 1 social link → 90-second niche scan (you + up to 50 competitors) → 30-day plan → hooks/scripts/captions/carousels/reels → publish to **13 platforms** → PDF report every run. Pricing is **judgement-metered, render-unbundled**: BASIC $24/mo (400 cr), VISIONARY $79/mo (1,500 cr), AGENTIC $199/mo (5,000 cr). Rendering (HeyGen avatar video, image gen, ffmpeg) is **BYOK / 0 makerzz credits** — billed by your own provider accounts.

Big finding: **the site recently pivoted and left stale metadata everywhere**. `llms.txt`, `manifest.webmanifest`, JSON-LD, and `<meta name="keywords">` still describe the _old_ product (AI product photography / studio-grade e-commerce creatives, $5–$200 tiers, `/editor`, `/agent`, `/showcase`, `/pricing`, `/horizon` routes). The live homepage/plans/guide/proof describe the _new_ product (Social Autopilot, `/studio`, `/calendar`, `/integrations`, `/how-it-works`, `/trends`, `/plans`). Anyone cloning or auditing must treat llms.txt/manifest/JSON-LD as **outdated, not source of truth**.

---

## 2. Hosting / network / DNS — observed

| Layer                           | Observed value                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Apex A records                  | `104.21.39.71`, `172.67.143.165` (Cloudflare anycast pair)                                                                                                                                                                                                                                                                                            |
| `www`                           | NXDOMAIN — **no `www` host**; apex-only canonical (`https://makerzz.space`)                                                                                                                                                                                                                                                                           |
| Nameservers                     | `candy.ns.cloudflare.com`, `augustus.ns.cloudflare.com`                                                                                                                                                                                                                                                                                               |
| TXT                             | `google-site-verification=totJtcefi1cddPJYCRBHVCZ3gxJlBOCgsVGjkSwlPh8` (Search Console verified)                                                                                                                                                                                                                                                      |
| MX                              | none (SOA only) — no inbound mail infra on apex; contact is likely a form/`hello@makerzz.com` alias (llms.txt states `hello@makerzz.com`; contact page is a form — verify before mailing)                                                                                                                                                             |
| TLS                             | `CN=makerzz.space`, issuer `CN=WE1, O=Google Trust Services` — Cloudflare Universal SSL (Google Trust Services path)                                                                                                                                                                                                                                  |
| HTTP server header              | `server: cloudflare`                                                                                                                                                                                                                                                                                                                                  |
| `Server-Timing`                 | `cfEdge;dur=743, cfOrigin;dur=0, cfWorker;dur=455` — **Cloudflare Workers origin** (not Vercel)                                                                                                                                                                                                                                                       |
| Next-on-Workers signals         | `x-opennext: 1`, `x-nextjs-cache: MISS`, `x-nextjs-prerender: 1`, `x-nextjs-stale-time: 300`, `X-Powered-By: Next.js`, `Vary: rsc, next-router-state-tree, next-router-prefetch, next-router-segment-prefetch`                                                                                                                                        |
| Cache                           | `Cache-Control: s-maxage=31536000` on prerendered pages; Firecrawl reported `cacheState: hit, cachedAt: 2026-09-11T06:20:04Z`                                                                                                                                                                                                                         |
| Security headers (observed)     | `X-Content-Type-Options: nosniff` (×2), `X-Frame-Options: DENY` (×2), `Referrer-Policy: strict-origin-when-cross-origin` (×2), `Permissions-Policy: camera=(), microphone=(self), geolocation=(), interest-cohort=()` (doubled value = header set twice — minor hygiene bug), NEL `Report-To` → `a.nel.cloudflare.com`, `Alt-Svc: h3=":443"` (HTTP/3) |
| `security.txt`                  | 404 — absent at `/.well-known/security.txt`                                                                                                                                                                                                                                                                                                           |
| RUM                             | Cloudflare Beacon `static.cloudflareinsights.com/beacon.min.js/v31edd6df…` with `data-cf-beacon {"version":"2024.11.0","token":"01f39bcacabf440baada1c3145aa2400","r":1,"spa":2}` (SPA mode)                                                                                                                                                          |
| Analytics (observed in rawHtml) | Google `gtag.js?id=AW-18315341625` (Google Ads) + `gtag('config','AW-18315341625')` + `gtag('config','G-2MHKK0XK9B',{anonymize_ip:true})` (GA4). No PostHog/Mixpanel/Amplitude/Hotjar/Intercom fingerprints in homepage HTML.                                                                                                                         |

**Inference:** OpenNext + Cloudflare Workers is the exact deployment story — `x-opennext` + `cfWorker` timing + Cloudflare DNS/A records together are conclusive. No Vercel hosting. No custom origin IP exposed (expected behind Cloudflare proxy).

---

## 3. Frontend stack — observed

- **Next.js App Router + React Server Components.** Proof: RSC flight payload in rawHtml (`self.__next_f.push([...])` chunks), `next-route-announcer`, per-route CSS splitting, `/_next/static/chunks/webpack-e2a411a64fb5ec8e.js`, `4bd1b696-100b9d70ed4e49c1.js`, `1255-b8cf77ab14370e57.js`, `main-app-9c0a4b3c1de60d3a.js`, `polyfills-42372ed130431b0a.js (nomodule)`.
- **CSS:** 9+ hashed per-route stylesheets (`64edccae0e38c8b1.css`, `b256d64c8d2a566c.css`, `0c6d1034487b2634.css`, `b298b22194f956b5.css`, `7d201b08191806f1.css`, `68b3601e14a321e8.css`, `872d91879e20d48b.css`, `85a0a358c2b93391.css`, `9bcdc57d26b2c97f.css`, plus `c841e572…`, `16053182…`, etc. preloaded as style). Firecrawl `branding.designSystem = {framework:"custom", componentLibrary:""}` — i.e. **hand-rolled `.sa-*` design system, no Tailwind/MUI/Chakra fingerprint**.
- **Fonts (self-hosted via `next/font`):** `/_next/static/media/36966cca54120369-s.p.woff2`, `1a4aa50920b5315c-s.p.woff2`, `558ca1a6aa3cb55e-s.p.woff2`, `9cc5b37ab1350db7-s.p.woff2`, `e6099e249fd938cc-s.p.woff2` preloaded as `font/woff2`. Branding reports **Archivo** (headings/body), **Space Grotesk** (body fallback stack), **JetBrains Mono** (monospace). CSS classes confirm: `__variable_dd5b2f`, `__variable_9b68a8`, `__variable_1f5468`, `__variable_f9e569` (next/font CSS-variable pattern).
- **Images:** `next/image` optimizer everywhere — `/_next/image?url=%2Fsa%2F…&w=1920&q=75` (also `w=256/3840`). Static assets under `/sa/*` (phase/object/scene PNGs), `/walkthrough/*.webp` (product screenshots), `/email/logos/*.png` (platform logos for trends cards), `/images/og-calendar.png?v=20260814` (OG), `/images/logo.png` (512).
- **Icons:** **all inline SVG, zero icon-font/package** (the integrations page states this explicitly: “Every mark is drawn inline in this app — nothing is hotlinked, and no icon package ships”). Platform tiles hardcode brand colors (X `#000`, Pinterest `#E60023`, Bluesky `#0285FF`, Reddit `#FF4500`, Telegram `#26A5E4`, Discord `#5865F2`, Google Business multi-color `#4285F4/#34A853/#FBBC04/#EA4335`).
- **PWA:** `/manifest.webmanifest` exists (`name:"makerzz"`, `display:"standalone"`, `orientation:"portrait-primary"`, icons 192/512 + maskable) — but `description` is **stale** (“Make marketing videos that sell… Upload one product photo…”) from the old product. Likewise full favicon set: `favicon.ico`, `favicon-16/32/48/96.png`, `apple-touch-icon.png (180)`, `android-chrome-192/512.png`.
- **Structured data:** `id="makerzz-jsonld"` with Organization + WebSite + SiteNavigationElement + SoftwareApplication — content is **stale** (old “upload one product photo” copy, old routes `/editor?mode=image|video`, `/agent`, `/presets`, `/marketing`, `/templates`, `/showcase`, `/pricing`, `/about`, old offer `price:"5"`, “Paid plans from $30/month — BASIC, PRO, Studio, ULTRA”, features “10 pre-prompted style tiles, 2K/4K upscale”). Do not trust for current pricing.
- **SEO meta (current):** `title` “makerzz — Grow on social media on autopilot — makerzz”, `description`/`og:description`/`twitter:description` = “A fully automated tool. Paste one social link and makerzz scrapes the best of what already works in your niche, makes the posts for you, and puts them out to thirteen platforms on autopilot.”, `canonical: https://makerzz.space/`, `robots: index, follow`, OG `1200×630` + `og:image:alt` (calendar), `twitter:card: summary_large_image`, `twitter:site: @makerzz`, `og:locale: en_US`. **Stale:** `<meta name="keywords" content="makerzz,product photography,AI image generation,product ads,ecommerce visuals,marketing images,D2C creative,catalog photography">` — leftover from old product.

---

## 4. Backend / product engineering — reconstructed from on-page contracts

The site documents its own server contracts unusually explicitly (homepage FAQ, `/how-it-works`, `/plans`, `/guide`, `/proof`). Treat this as the authoritative spec — it reads like it was written from the shipped skill/server code (“Every number on this page comes out of the shipped skill file”).

### 4.1 Nine-phase state machine (P0–P8), gate-file architecture

> “Every phase writes a real file, and the next phase refuses to start until it can read that file back.” / “The gate is the file, not a memory of having produced it.”

| Phase | Name                                                                                                                                                                 | Gate file                               | Cost                                                                                                     |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| P0    | Setup & onboarding (8–9 fields: brand, handles, niche, audience, voice, platforms, avatar, approval mode; refuses vague niches like “business”/“AI”)                 | `brief saved`                           | Free                                                                                                     |
| P1    | Profile & niche scan (you + up to 20 competitors Visionary / 50 Agentic; ranked angle table)                                                                         | `scan scored` (`scan.json`)             | **40 cr**                                                                                                |
| P2    | Strategy & calendar (8 ranked angles + slot plan; post times randomised to the minute, e.g. 7:14 not 7:00; never 7 same-format in a row)                             | `week laid out` (`plan.json`)           | **15 cr / platform**                                                                                     |
| P3    | Script (clean prose `.txt`; verifier rejects `[HOOK]`/timecodes/`**markdown**`/emoji/stage directions; failed scripts regenerate server-side, never hand-scrubbed)   | `script verified` (`script.txt`)        | **12 cr**                                                                                                |
| P4    | Avatar video (HeyGen render on your key; submit→poll→download; dropped sessions resume the poll, never double-submit)                                                | `video.mp4` (`avatar rendered`)         | **0 makerzz cr** (your HeyGen bill)                                                                      |
| P5    | Edit plan & cut (shot list, caption timings, B-roll spec, SFX map — everything the script is forbidden to contain)                                                   | `edit plan written` (`edit.json`)       | **20 cr**                                                                                                |
| P6    | Carousel (8 compiled slide prompts + caption/hashtags; you approve prompts before any render; each slide keeps its `.prompt.txt`)                                    | `slides approved` (`slides/`)           | **30 cr** (+ per-slide render: Standard 3 / High 6 / 4K 12)                                              |
| P7    | Schedule & publish (queue-writing free; per-platform aspect/caption/API pre-checks; approve-each shows final asset+caption+time and waits)                           | `queue confirmed`                       | **3 cr / platform** (one page states this; another page states publishing = 0 cr — see §4.2 discrepancy) |
| P8    | Report (what shipped/cost/platform-reported-back/what’s stuck; missing engagement data written as “not available”, never invented; ends with credits used/remaining) | `report filed` (PDF in inbox + on disk) | Free                                                                                                     |

Notes: P4/P5/P6 are a fork (carousel drop skips avatar; talking-head skips carousel). “One phase per message. It finishes, shows you the result, asks, and stops.” Studio has a collapsed daily-autopilot call P1→P3 at 25 cr. Full strategy run (scan+week+script+edit+prompts+captions) is quoted as **122 cr charged as one call**.

### 4.2 Credit ledger (“judgement-metered, render-unbundled”)

Full metered table (from `/plans` + `/how-it-works`, identical on both):

| Action                         | Call               | Credits |
| ------------------------------ | ------------------ | ------- |
| Profile/niche scan             | `scan`             | 40      |
| Trend refresh + calendar       | `trends`           | 15      |
| Script generation              | `script`           | 12      |
| Reel edit plan                 | `edit_plan`        | 20      |
| Carousel prompt set (8 slides) | `carousel_prompts` | 30      |
| Caption + hashtag pack         | `caption_pack`     | 5       |
| Carousel slide Standard        | `slide_low`        | 3       |
| Carousel slide High (2×)       | `slide_high`       | 6       |
| Carousel slide 4K (4×)         | `slide_4k`         | 12      |
| Avatar video 60s 1080p         | `video_1080p`      | 202     |
| Avatar video 60s 4K            | `video_4k`         | 215     |

Rules (enforced server-side, per copy): cost quoted before every billable call (“Script — 12 credits. You’ll have 4,168 left. Go?”); append-only ledger (balance = fold over entries); 402 at zero with halt, no retry/degrade/substitute; monthly reset, no rollover; re-reads/reports/calendar/brief/prompt-recompile = 0 cr. **Discrepancy to flag:** `/how-it-works` P7 says “Publishing is metered: 3 credits / platform”; `/plans` + homepage FAQ say “Publishing costs no credits… 0 credits… forever.” Likely the 3-cr `publish_receipt` is legacy or plan-dependent — needs a live checkout test to resolve; quote both in any rebuild.

Worked examples on-page: VISIONARY month = 4×122 + 6×24 + 2×96 + 4×202 + 60×0 = 1,632 “of 1,500 — lands exactly on the month” (their words; arithmetic actually overshoots —another copy bug); AGENTIC = 12×122 + 30×24 + 10×96 + 14×202 + 240×0 = 5,972 of 5,000. Interactive “dial” calculator on `/plans#calculator` recomputes cost/piece live.

### 4.3 Auth, accounts, checkout (partially observed)

- **Sign-in UI (observed):** modal “Welcome to makerzz — Sign in to run your content operation” with **Continue with Google** + **Continue with Email**, ToS/Privacy consent. No Clerk/Supabase/Firebase/Auth0 fingerprints in homepage HTML — **inferred custom session/JWT on Workers** (or an auth provider loaded only on `/sign-in` chunk — unverified; fetch that route’s JS to confirm before cloning auth).
- **App routes (observed via robots.txt disallows):** `/sign-in`, `/onboarding`, `/library`, `/editor`, `/checkout/`, `/account/`, `/admin`, `/api/`, `/sa-runs/` — i.e. private Studio/Library/Editor, per-run folders, checkout flow, account admin. Public IA from sitemap: `/`, `/studio`, `/calendar`, `/integrations`, `/how-it-works`, `/proof`, `/plans`, `/trends`, `/guide`, `/faq`, `/contact`, `/legal/*`, `/full`, `/compare/*`, `/blog/*`.
- **Checkout (inferred):** plan CTAs (“Get Basic/Visionary/Agentic →”) deep-link to `/checkout/` (robots-disallowed, JS-driven — no Stripe/Razorpay/Paddle strings in homepage HTML, so provider loads at checkout; likely Stripe given USD monthly + “stop renewal, keep period” language + no-refund digital-goods terms — but **unverified**, mark as unknown until checkout JS is inspected).
- **Anti-abuse (stated):** device fingerprinting at sign-in — “more than 3 distinct devices in 24h flags the account”; one plan = one operator (AGENTIC = 10 accounts under one operator); publish-on-auto needs explicit spoken confirmation, re-asked after 7 idle days.
- **Secrets handling (stated):** provider keys stored server-side, shown masked to last-4 only, “no route returns a full key to a browser”, single-button revoke. Fail-closed: unknown errors print the API’s own words, charge nothing, halt.

### 4.4 Publishing, rendering, data providers

- **Publishing (inferred aggregator):** 13 destinations — Instagram, YouTube, LinkedIn, TikTok, Facebook, Threads, X, Pinterest, Bluesky, Reddit, Telegram, Discord, Google Business — all via one OAuth “Connect” page (“approve each account on that platform’s own screen; makerzz never sees passwords”). Copy: “Our publishing provider bills us per connected profile per month rather than per post” — the classic **Ayrshare-style** pricing shape (per-profile, not per-post). No provider string in homepage HTML, so treat “Ayrshare-compatible aggregator” as inference; the optional “Instagram Graph — needs your Meta app (`instagram_content_publish` + app review)” escape hatch confirms they otherwise avoid Meta app review via the aggregator.
- **Avatar video:** **HeyGen** (explicit, repeatedly). Async submit→poll→download with resume; two house editing styles; ffmpeg composite implied (“the ffmpeg cut”).
- **Image/carousel render:** BYOK image provider on your rates (page contradicts itself on whether slide credits go to makerzz vs. your key — plans table charges slide credits; integrations page says “HeyGen minutes and image generation bill to your own provider accounts… This app spends its own credits on the writing and planning pass only”. Reconcile as: prompt-compilation = makerzz credits, pixel render = your key — but homepage FAQ says slide re-render = second charge, so at least some render cost flows through makerzz. Flag for live test.)
- **Daily trends engine (observed):** `/trends` index + date-slugged posts (`/trends/YYYY-MM-DD-*`, daily `lastmod`, `changefreq: daily`) synthesising HN points, GitHub stars, TikTok/IG/YouTube/LinkedIn formats into “scripts you can post today” with per-claim sources and platform logo chips (`/email/logos/*`). This is a **daily cron (public trend scout) + programmatic SEO surface** in one.
- **Programmatic SEO (observed):** `/compare/{higgsfield,freepik,luma,elevenlabs,…}`, `/blog/*` (100+ posts incl. `pricing-predictable-creatives`, `blog-013-*`, `blog-092-*`), stale `/use-cases`, `/tools/amazon-pack`, `/docs`, `/help`, `/showcase`, `/roadmap`, `/horizon/*` (frontier “SKU Fingerprint / Creative Genome” positioning from the old product — still in llms.txt sitemap-shaped list but largely absent from live nav; keep as legacy).
- **Skill-file distribution (observed):** `/guide`, `/how-it-works`, `/proof` repeatedly reference a **shipped skill file** (“Every number on this page comes out of the shipped skill file”, “once the skill is on your machine”, run folder with `brief/scan.json/plan.json/script.txt/edit.json/slides/*.prompt.txt/receipts`). The “app” is therefore part web-Studio, part downloadable **agent skill (Claude/Agent-Skills-shaped: `SKILL.md` + scripts)** that operates a local run folder. `/proof` lists verifiable structural facts (9 gates, 0-cr render, 90-sec single-use job tokens, append-only ledger, `.prompt.txt` beside every PNG, randomised post times, verifier-gated scripts).
- **Email:** PDF report “lands in your inbox… every run, no exceptions” → transactional mail provider (unobserved; check `/api` traffic to identify).

---

## 5. UI/UX reverse-engineering

### 5.1 Design tokens (Firecrawl branding + observed CSS)

| Token               | Value                                                                                                                                                                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mode                | Dark (`colorScheme: dark`, page bg near-black `#060606`) with light content cards (text ink `#10222A`)                                                                                                                                                      |
| Primary / Secondary | `#0E6F77` (deep teal) / `#0A545C` (darker teal)                                                                                                                                                                                                             |
| Accent / CTA        | `#FFC22B` (amber) — primary pill buttons: amber bg, ink text/border, hard offset shadow `rgb(16,34,42) 0px 6px 0px`                                                                                                                                         |
| Secondary button    | White bg, ink text/border, pill `999px`                                                                                                                                                                                                                     |
| Radius              | Cards `20px`, buttons/pills `999px`, platform tiles `10px`                                                                                                                                                                                                  |
| Type                | Archivo (headings/body, 68px H1 / 49.6px H2 / ~17px body), Space Grotesk (body fallback), JetBrains Mono (code/receipts/skill snippets)                                                                                                                     |
| Spacing             | 4px base unit; dense marketing rhythm: hero → 4-step strip → evidence gallery → compounding chart → feature grid → 13-platform wall → FAQ → CTA                                                                                                             |
| Brand mark          | Inline SVG wordmark: 32px rounded-square outline + teal arc + dot; “Social Autopilot / makerzz” lockup; favicon `favicon.ico` + PNG set; OG `og-calendar.png`                                                                                               |
| Voice               | Blunt-operator: “Buy judgement. Never GPU time.” / “When in doubt, it waits.” / “No offline mode and no degraded best-effort mode.” Numbers-as-proof, anti-hype disclaimers (“Illustrative… not a typical result”, orange “illustrative” chips on `/proof`) |

### 5.2 Layout & navigation

- **Header:** sticky “island” pill nav (Studio / Calendar / Connect / How it works / Trends / Plans) + wordmark left + Log in right; `sa-skip` a11y skip-link (`#sa-main`); `aria-label="Primary"`.
- **Homepage narrative (8 beats):** ① paste-link hero (handle input + platform tabs IG/TikTok/YT/LinkedIn/X + Send + free-text brief fallback + 2-min YouTube demo `QQlYf5H3Uog`) → ② “Four steps, you’re only in the first” (01 paste / 02 niche read / 03 make / 04 publish, ~10s + ~90s + background + forever) → ③ “Not a plan. The content.” walkthrough gallery (paste → report → render → schedule → cadence → auto/manual, `.webp` screenshots) → ④ compounding chart (Day 0→90, 0→90k illustrative) → ⑤ 4-value grid (never waits / one brief / shows working / never invents numbers) → ⑥ 13-platform wall → ⑦ FAQ accordion (app-vs-file, why server, credit math, video cost, publish cost, re-render policy) → ⑧ CTA “Start on autopilot · From $24/mo” + footer (Plans/Terms/Privacy/Refunds/Contact, © 2026).
- **`/how-it-works`:** 8-section “operator manual” (shape → P0–P8 pipeline table → script-rule gate → 7 approval stages → saved-runs/resume → credits → CTA), embedded YouTube, persona cards (agencies/freelancers/founders/creators), input grammar (handle / niche sentence / competitor / question), connect 4-steps.
- **`/plans`:** 8-section pricing machine (tiers → metered table → live “dial” calculator → worked-month arithmetic → line-by-line compare → honest-pitch → plain-English terms → FAQ → CTA). Effective rates 6.0¢/5.3¢/4.0¢.
- **`/integrations` (Connect):** 13 tiles (Not connected → Connect → Live; “Reading status — asking the publishing service which accounts are live”) + optional Instagram-Graph BYO-Meta-app section + who-pays-for-what.
- **`/trends`:** daily-brief index cards (date, hook title, platform chips, HN/GitHub metrics, tags) → per-day article.
- **`/guide`:** 10-section operator reference (~12 min read) in run order; **`/proof`:** checkable-facts ledger (files/gates/error codes/arithmetic) vs. illustrative chips.

### 5.3 UX patterns worth cloning

1. **Quote-before-spend** on every metered call; 402-halt with refill date; nothing degrades silently.
2. **Gate-file mental model** exposed to users (P0–P8 + gate filenames) — power-user trust device.
3. **Randomised-to-the-minute scheduling** + no-7-same-format rule (anti-automation-detection craft).
4. **Approve-each by default, auto as opt-in per stage** (7 toggles; publish-auto needs spoken re-confirmation).
5. **Resume-not-restart** (run folders re-read on session open; HeyGen polls + rendered slides resume).
6. **Provenance by default** (`.prompt.txt` per PNG, receipts per call, PDF per run, “not available” > invented numbers).
7. **Calculator-as-pricing-page** (dial → credits → ceiling → cost/piece) instead of static tiers.

### 5.4 Accessibility / performance notes

Skip-link, semantic landmarks, aria-hidden decorative SVGs, labelled nav — baseline present. Fonts/images preloaded aggressively (5 woff2 + 8 hero PNGs + CSS preconnects); RSC payload keeps first paint a prerendered shell with streaming `__next_f` chunks — expect good LCP on Cloudflare edge, with `x-nextjs-cache: MISS` on cold edge. No heavy client frameworks beyond Next runtime; no icon package; WebP walkthroughs. Fonts fall back to Helvetica/Arial/Space Grotesk Fallback (FOUT-tolerant).

---

## 6. Content / IA inventory (observed via map + sitemap + scrapes)

**Live nav:** Studio, Calendar, Connect (`/integrations`), How it works, Trends, Plans (+ Log in → `/sign-in`).
**Sitemap priorities:** `/` 1.0 daily; `/studio` `/how-it-works` `/plans` `/trends` 0.9 daily; `/calendar` `/integrations` `/proof` 0.8; `/guide` `/faq` 0.7; `/contact` 0.8 monthly; `/legal*` 0.5–0.6.
**App-only (robots-disallowed):** `/sign-in`, `/onboarding`, `/library`, `/editor`, `/checkout/`, `/account/`, `/admin`, `/api/`, `/sa-runs/`.
**SEO surfaces:** `/trends/YYYY-MM-DD-*` (daily), `/compare/*` (higgsfield/freepik/luma/elevenlabs + hub), `/blog/*` (100+), `/full` (long-form credit/architecture page linked from FAQ).
**AI surfaces:** `/llms.txt` (stale — describes old product; needs rewrite to Social Autopilot + current routes/pricing), GPTBot/ChatGPT-User explicitly allowed on `/`, `/how-it-works`, `/proof`, `/plans`, `/guide`, `/faq`, `/legal`, `/llms.txt` (AI-training crawlers otherwise disallowed: GPTBot, ClaudeBot, CCBot, Google-Extended, Amazonbot, Applebot-Extended, Bytespider, meta-externalagent + Cloudflare `Content-Signal: search=yes,ai-train=no,use=reference`).

---

## 7. What’s still unknown (do not guess in a rebuild)

1. Checkout/payment provider (Stripe vs. Razorpay vs. Paddle) — inspect `/checkout/` JS + network.
2. Auth implementation (custom JWT vs. managed provider) — inspect `/sign-in` chunk + cookies.
3. Publishing aggregator identity (Ayrshare-pattern fits pricing + 13-platform list, but unconfirmed) — inspect Connect network calls.
4. Image-generation provider(s) + who actually bills slide renders — live render test with masked-key account.
5. P7 publish cost (0 vs. 3 cr/platform) + VISIONARY arithmetic overshoot — live run or source read.
6. DB/session store (D1/KV/R2/Postgres?) — Workers bindings not visible externally.
7. LLM backends for scan/script/prompts (server-side, undisclosed — correctly so).

---

## 8. Rebuild recipe (if cloning the engineering, not the copy)

1. **Next.js 14+/15 App Router (TypeScript, RSC) + OpenNext on Cloudflare Workers + Cloudflare DNS/CDN/SSL.** Prerender marketing routes (`s-maxage` long, `stale-time 300`); Workers for `/api/*` + Studio/Connect/Checkout.
2. **Hand-rolled `.sa-*` CSS system** (no UI kit): Archivo + Space Grotesk + JetBrains Mono via `next/font`; teal/amber/ink tokens; 999px pills with hard offset shadows; 20px cards; island nav; inline-SVG brand tiles.
3. **State machine P0–P8 with gate files** on R2/D1 (+ local mirror for skill mode); append-only credit ledger; quote-before-spend; 402-halt; device-fingerprint abuse gate; masked-key secret store; HeyGen async poll-resume; per-slide `.prompt.txt` provenance; randomised scheduling; PDF report per run.
4. **Credit SKUs** exactly as §4.2; tiers 400/1,500/5,000 at $24/$79/$199; BYOK render keys; aggregator OAuth for 13 platforms + BYO Instagram-Graph escape hatch.
5. **Growth stack:** daily trends cron → date-slugged posts; `/compare` + `/blog` programmatic SEO; GA4 + Ads + CF Beacon; Search-Console-verified; JSON-LD/OG/PWA; AI-crawler allowlist + `llms.txt` (rewritten for the current product).
6. **Ship a skill file** (`SKILL.md` + scripts) alongside the web Studio — the product is half SaaS, half agent skill; `/proof`’s checkable-facts page is the trust anchor.

---

## 9. Sources & evidence pointers

- Homepage copy/flows: Firecrawl markdown scrape of `/` (13-platform list, 4 steps, FAQ credit math, YouTube `youtu.be/QQlYf5H3Uog`).
- Pipeline/credits: `/how-it-works` (P0–P8 table, script gate, 7 approvals, run-folder tree) + `/plans` (11-row credit table, dial calculator, 402/ledger/device rules) + `/guide` + `/proof`.
- Connect/publishing: `/integrations` (13 tiles, aggregator billing line, Instagram-Graph note).
- Auth: `/sign-in` markdown (Google + Email modal).
- Trends engine: `/trends` index + `/trends/2026-09-1*` slugs + `sitemap.xml` daily `lastmod`.
- Stack proof: response headers (`x-opennext`, `cfWorker`, `X-Powered-By: Next.js`, doubled sec-headers), rawHtml (`__next_f`, `/_next/static/chunks|media|css`, `next/font` variables, `next/image` URLs, `next-route-announcer`), DNS/TLS (Cloudflare A/NS, Google-Trust WE1), analytics IDs (`G-2MHKK0XK9B`, `AW-18315341625`, CF Beacon `01f39bcacabf440baada1c3145aa2400`), `manifest.webmanifest`, `makerzz-jsonld`, `robots.txt` (Cloudflare content-signals + route disallows), `llms.txt` (stale product snapshot — useful as pivot evidence).
- Design tokens: Firecrawl `branding` (Archivo/JetBrains Mono/Space Grotesk stacks, `#0E6F77/#0A545C/#FFC22B/#060606/#10222A`, 999px pills + `0px 6px` shadow, 20px radius, dark mode, custom framework).

_Report saved from live evidence on 2026-09-11. Re-scrape before building — pricing/credit copy has at least one internal contradiction (§4.2) and several stale-metadata fields (§3)._
