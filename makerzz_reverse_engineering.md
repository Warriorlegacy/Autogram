# makerzz.space — Reverse Engineering Report

**Date:** 2026-09-11  
**Target:** https://makerzz.space/  
**Analyst:** Kilo / Autogram workspace  
**Tools used:** Firecrawl scrape, webfetch, header inspection, robots.txt, sitemap.xml, llms.txt, multi-page HTML audit  

---

## 1. Executive Summary

makerzz.space is a **social media autopilot SaaS** built on **Next.js 13+ App Router** with **Tailwind CSS**, deployed behind **Cloudflare** and likely served via an **OpenNext/OpenNext.js** adapter. The product scans social profiles, generates 30-day content plans, renders carousels/reels, and publishes to **13 platforms** on a schedule. No public source repository was found. The backend stack is not explicitly disclosed, but strong architectural signals point to a server-heavy, credit-metered design rather than a simple static site.

---

## 2. Product & Positioning

| Attribute | Evidence |
|---|---|
| **Product name** | makerzz — Social Autopilot |
| **Core value prop** | "Paste one social link and makerzz scrapes the best of what already works in your niche, makes the posts for you, and puts them out to thirteen platforms on autopilot." |
| **Target users** | Founders, content creators, freelancers, agencies |
| **Pricing model** | Credit-based metering + monthly plans |
| **Public pricing tiers** | BASIC $30/mo, VISIONARY $60/mo, AGENTIC $100/mo; llms.txt also mentions Make $5/mo, Studio $100/mo, ULTRA $200/mo |
| **Free tier** | 0 credits on the free plan |
| **Key differentiator** | Server-side "judgement" engine (not a client-side chatbot); every run produces a PDF report; credits buy server-side reasoning + rendering, not pixels |

### 13 Supported Platforms
Instagram, YouTube, LinkedIn, TikTok, Facebook, Threads, X, Pinterest, Bluesky, Reddit, Telegram, Discord, Google Business

### Core Features
- **Studio** — run console: paste profile → scan niche → generate plan
- **Calendar** — editable monthly content board
- **Integrations** — connect each platform once via official sign-in
- **Trends** — daily trend digest
- **Guide** — operator documentation
- **Proof** — audit artifacts, credit arithmetic, failure modes
- **FAQ / Contact / Legal** — standard SaaS pages

---

## 3. Frontend Engineering

### Framework
- **Next.js 13+ App Router**
  - Evidence: `/_next/static/` asset paths, `self.__next_f` flight payloads, `x-powered-by: Next.js`, `x-nextjs-prerender: 1`, `x-nextjs-stale-time: 300`, `Vary: rsc, next-router-state-tree`, route segments like `app/(sa)/page-...js`, `app/layout-...js`
  - No `__NEXT_DATA__` present; uses **React Server Components (RSC)** with flight data
  - `data-dgst="BAILOUT_TO_CLIENT_SIDE_RENDERING"` indicates selective CSR fallback
- **React** — implicit via Next.js RSC payloads and component boundaries (`$Sreact.fragment`)

### Styling
- **Tailwind CSS** via Next.js CSS modules
  - Evidence: 9 hashed CSS bundles under `/_next/static/css/`, `__variable_dd5b2f` / `__className_dd5b2f` classes on `<html>`, `data-precedence="next"` on stylesheet links
  - 5 custom font preloads (`.woff2`) under `/_next/static/media/`
- **No inline `<style>` tags** — all styles are external hashed CSS bundles

### Fonts
- 5 preloaded font files (likely Inter + display font stack)
- Apple touch icon / favicon PNGs + ICO

### Key UI Sections (from DOM)
| Section | Purpose |
|---|---|
| `header.sa-header` | Nav: Studio, Calendar, Connect, How it works, Trends, Plans, Log in |
| `section.sky` | Hero: "Paste your social media here" + input form + demo video CTA |
| `section.hs-sec#how` | 4-step process: paste link → read niche → make posts → post forever |
| `section.hs-sec#what` | Walkthrough rail: paste profile, read report, render assets, schedule, approve |
| `section.hs-sec.hs-sec--tint#where` | 13 platform grid |
| `section.hs-sec.hs-sec--tint#autopilot` | Compounding growth chart (0 → 90,000 followers illustration) |
| `section.hs-sec#questions` | FAQ accordion |
| `section.fbc` | Footer CTA: "Start on autopilot" / $24/mo / See plans |
| `footer.hs-foot` | Copyright 2026, Plans, Terms, Privacy, Refunds, Contact |
| `div.mzc` | Floating chat/support widget |

### Client-Side Components (from RSC payload)
- `CookieConsentProvider` — cookie consent
- `AuthProvider` — authentication wrapper
- `MetaPixelHead` / `MetaPixelNoscript` — Meta Pixel integration
- `ResellerBrandingProvider` — suggests reseller/partner branding support

### PWA / Mobile
- `<link rel="manifest" href="/manifest.webmanifest">`
- `<meta name="apple-mobile-web-app-capable" content="yes">`
- `<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">`
- Mobile viewport meta present

---

## 4. Backend & Infrastructure Engineering

### Hosting / CDN
- **Cloudflare** is the front-facing server
  - Evidence: `Server: cloudflare`, `CF-RAY`, `Nel` / `Report-To` with `cf-nel`, `alt-svc: h3=:443`
- **OpenNext / OpenNext.js adapter**
  - Evidence: `x-opennext: 1` header
  - This indicates the site is **not running on Vercel's native runtime**; it is likely deployed on Cloudflare Workers, AWS Lambda, or another serverless target via the OpenNext adapter
- **No Vercel-specific headers** (`x-vercel-cache`, `x-vercel-id` are absent)

### API Layer
- **No public API endpoints found**
  - `GET /api/health` → 404
  - `GET /api/` → 404
  - `robots.txt` disallows `/api/`, `/admin`, `/sa-runs/`, `/editor`, `/onboarding`, `/library`, `/checkout/`, `/account/`, `/sign-in`
- API routes are likely **private/internal** and not exposed publicly
- All dynamic behavior appears to be handled via **Next.js Server Actions** or **Route Handlers** after client-side hydration

### Auth
- `AuthProvider` component present in RSC tree
- Login page exists at `/sign-in` (disallowed in robots.txt)
- No visible auth library strings in HTML (`next-auth`, `clerk`, `auth0`, `firebase` not found)
- Likely **custom auth** or **NextAuth.js** with a custom UI

### Payments
- **Dodo Payments** referenced in copy (`/plans`, `/guide`)
- No Stripe, Paddle, Lemon Squeezy, or PayPal strings found in HTML
- No payment form fields visible on pricing page
- Likely uses Dodo Payments' hosted checkout or embedded SDK

### Rendering / AI
- **HeyGen** API referenced for avatar video rendering
  - Evidence: `/integrations`, `/how-it-works`, `/plans`, `/guide`, `/faq`
  - 60-second avatar video at 1080p = 202 credits; 4K = 215 credits
- **AI image generation** implied by "renders carousels" and credit model
  - llms.txt legacy keywords suggest prior product photography / AI image generation positioning

### Database / Storage
- No direct database strings found in HTML
- Strong implication of server-side state: credits, runs, reports, calendar entries
- Likely a relational DB (PostgreSQL) or managed service, but not confirmed from public evidence

### Queue / Job Processing
- No explicit queue library strings found (`bull`, `celery`, `temporal`, `inngest`)
- Architecture implies background jobs: scan → strategy → script → render → publish pipeline
- Likely handled by server-side Next.js runtime or a managed job queue

### Email / Notifications
- No email service strings found (`resend`, `sendgrid`, `postmark`, `mailgun`, `amazonses`)
- Contact email: `teamglitch82@gmail.com` (found on `/contact`)
- PDF reports are generated server-side and emailed or downloaded

---

## 5. Analytics & Marketing Stack

| Tool | Evidence | Purpose |
|---|---|---|
| **Google Analytics 4** | `G-2MHKK0XK9B`, `googletagmanager.com/gtag/js?id=AW-18315341625` | Web analytics |
| **Google Ads** | `AW-18315341625` | Conversion tracking |
| **Meta Pixel** | `MetaPixelHead`, `MetaPixelNoscript` components | Facebook/Instagram ad tracking |
| **Cloudflare Web Analytics** | `static.cloudflareinsights.com/beacon.min.js/v31edd6df95cf4e85bb4c19e7a9bdbcba1788362987495` | Privacy-friendly analytics |
| **YouTube** | `youtu.be/QQlYf5H3Uog` embed on `/how-it-works` | Demo video hosting |

### SEO / AI Search
- `robots.txt` explicitly allows search and ChatGPT-User but blocks AI training (`ai-train=no`)
- `Content-Signal: search=yes, ai-train=no, use=reference`
- `/llms.txt` present and cached by Cloudflare — optimized for LLM discovery
- `/sitemap.xml` lists all major pages + daily trend URLs

---

## 6. Page Architecture

### Public Pages
| Path | Title | Purpose |
|---|---|---|
| `/` | makerzz — Grow on social media on autopilot | Landing / hero |
| `/studio` | Studio — Social Autopilot | Login-gated run console |
| `/calendar` | Content calendar | Editable monthly board |
| `/integrations` | Connect the accounts you already own | 13 platform OAuth connections |
| `/how-it-works` | How makerzz works | 9-phase pipeline explanation |
| `/proof` | Proof, not promises | Audit artifacts, credit arithmetic, refusal behavior |
| `/plans` | Plans & credits · billed monthly | Pricing tiers |
| `/trends` | Trends · daily | Daily trend digest |
| `/guide` | Operator's guide | Documentation |
| `/faq` | makerzz FAQ | Accordion FAQ |
| `/contact` | Contact — makerzz | Support email |
| `/legal` | Legal | Legal hub |
| `/legal/*` | Various | Privacy, Terms, Shipping, Refund, Cookies, DPA, Acceptable Use |

### Gated / Disallowed Paths (from robots.txt)
- `/sign-in`, `/onboarding`, `/library`, `/editor`, `/checkout/`, `/account/`, `/admin`, `/api/`, `/sa-runs/`

### llms.txt Reveals Additional Paths
- `/editor`, `/agent`, `/showcase`, `/pricing`, `/features`, `/horizon`, `/roadmap`, `/docs/api`, `/status`, `/compare`

---

## 7. UI/UX Design System

### Visual Language
- **Minimalist dark-tech aesthetic** with high contrast
- **Tint backgrounds** (`hs-sec--tint`) used to alternate section shading
- **Phase imagery** — numbered step illustrations (`06-phase-scan.png`, `07-phase-strategy.png`, etc.)
- **Object illustrations** — terminal, clock, shield icons
- **Walkthrough screenshots** — WebP format, realistic UI mockups (`/walkthrough/03_paste_profile.webp`, etc.)

### Typography
- 5 custom font preloads (likely a display + body font stack)
- Large hero headlines, compact body copy
- Strong H1/H2 hierarchy on all content pages

### Interaction Patterns
- **Hero input form** — paste social handle, select platform, submit
- **FAQ accordion** — expand/collapse without page reload
- **Calendar selectors** — month/year dropdown navigation
- **Platform connect buttons** — OAuth-style connection flow
- **Floating chat widget** — persistent support/chat CTA (`div.mzc`)
- **Cookie consent** — `CookieConsentProvider` component

### Responsive Behavior
- Mobile viewport meta present
- Apple mobile web app capable
- Likely fully responsive via Tailwind breakpoints

---

## 8. Content Strategy

### Tone
- Direct, anti-corporate, "no bullshit" positioning
- Frequent use of "by design" refusals (402, 409, 401, 429, "no number it did not receive")
- Transparent credit arithmetic and cost disclosure
- "Proof, not promises" — emphasizes auditability

### Key Messaging
- "Four steps. You are only in the first one."
- "Set it once. Then stop thinking about it."
- "It never invents a number"
- "Credits buy judgement. Never GPU time."

### Dynamic Content
- `/trends` — daily trend articles with SEO-friendly URLs (`/trends/2026-09-11-...`)
- `/llms.txt` — updated with latest pricing and product info
- `/sitemap.xml` — `lastmod` timestamps suggest daily updates to trends

---

## 9. Security & Privacy Signals

| Signal | Detail |
|---|---|
| **X-Frame-Options** | `DENY` — prevents clickjacking |
| **X-Content-Type-Options** | `nosniff` — prevents MIME sniffing |
| **Referrer-Policy** | `strict-origin-when-cross-origin` |
| **Permissions-Policy** | camera=(), microphone=(self), geolocation=() — restricts browser APIs |
| **robots.txt** | Blocks private paths; allows search; explicitly blocks AI training bots |
| **Cookie consent** | Present via `CookieConsentProvider` |
| **No passwords stored** | Claims "makerzz never sees or stores a password" — OAuth only |

---

## 10. Likely Stack Summary

| Layer | Technology | Confidence | Evidence |
|---|---|---|---|
| **Frontend framework** | Next.js 13+ App Router | **High** | `_next/static`, RSC payloads, `x-powered-by`, route segments |
| **Styling** | Tailwind CSS | **High** | Hashed CSS bundles, `__variable_*` classes |
| **Hosting/CDN** | Cloudflare + OpenNext | **High** | `Server: cloudflare`, `x-opennext: 1`, `CF-RAY` |
| **Analytics** | GA4, Google Ads, Meta Pixel, Cloudflare Analytics | **High** | Script tags, component names |
| **Auth** | Unknown / likely NextAuth.js or custom | **Medium** | `AuthProvider` component, `/sign-in` route |
| **Payments** | Dodo Payments | **Medium** | Mentioned in copy, no Stripe/Paddle strings found |
| **Video/Avatar** | HeyGen API | **High** | Explicitly named in multiple pages |
| **Database** | Unknown (likely PostgreSQL) | **Low** | No public strings; implied by server-side state |
| **Queue/Jobs** | Unknown (likely server-side runtime) | **Low** | No public strings; implied by pipeline architecture |
| **Email** | Unknown | **Low** | No public strings; PDF reports implied |

---

## 11. Architecture Diagram (Inferred)

```
[Browser]
    ↓
[Cloudflare CDN] ← DDoS protection, caching, analytics
    ↓
[OpenNext Adapter] ← Next.js App Router runtime
    ↓
[Next.js Server Components / Route Handlers]
    ↓
[Auth Layer] ← AuthProvider / NextAuth?
    ↓
[Credit Meter / Business Logic]
    ↓
[Background Pipeline]
    ├── Profile Scanner
    ├── Strategy Engine
    ├── Script Writer
    ├── Asset Renderer → HeyGen API
    └── Publisher → 13 Platform OAuth integrations
    ↓
[Database] ← Runs, credits, calendar, reports
    ↓
[PDF Report Generator] → Email / Download
```

---

## 12. Competitive Intelligence Notes

- **No open-source repo found** — fully proprietary
- **llms.txt** is well-maintained and cached by Cloudflare — optimized for AI search visibility
- **Daily trends** content suggests aggressive SEO / content marketing strategy
- **Transparent pricing and failure modes** on `/proof` is a strong trust signal
- **Credit-based metering** with per-render cost disclosure is unusual and likely reduces support friction
- **13 platform integrations** is a broad surface area; likely uses each platform's official API
- **No Stripe** — Dodo Payments is a less common choice, possibly for global/regional payment optimization

---

## 13. Open Questions

1. What is the actual backend runtime? (Cloudflare Workers? AWS Lambda? Vercel Edge?)
2. What database is used? (PostgreSQL via Neon/Supabase/Railway? MySQL?)
3. What auth library is used? (NextAuth.js? Clerk? Custom?)
4. How are background jobs orchestrated? (In-process? Temporal? Inngest?)
5. Is the "scan niche" engine AI-generated or rule-based? (LLM? Custom NLP?)
6. What image/video rendering stack is used besides HeyGen? (Flux? Replicate? Custom?)
7. Is there a public changelog or API docs beyond `/docs/api`?

---

*Report generated from public-facing web evidence only. No source code, private APIs, or backend systems were accessed.*
