# Autogram: Fully Automated Instagram Content Engine

> **Zero-touch system for daily AI · Technology · Marketing carousel content.**  
> Implements the complete architecture from `instagram-automation-guide.md` and `instagram_ai_autopilot.pdf`.

---

## Architecture Overview

```
 [Source Fetcher]  (RSS / News / Curated Research)
        │
        ▼
 [Topic Scorer]   (Calculates utility, novelty, anti-repetition memory)
        │
        ▼
 [Carousel Architect] (Builds structured 7-10 slide narrative JSON)
        │
        ▼
 [Fact Checker]   (Audits claims against source packet)
        │
        ▼
 [Quality Gate]   (Editor pass: scores 0-100, enforces banned clichés)
        │
        ▼
 [Slide Renderer] (Deterministic HTML/CSS -> 1080x1350 JPEG via Playwright)
        │
        ▼
 [Asset Stager]   (S3 / Cloudflare R2 / Public CDN staging)
        │
        ▼
 [Meta Publisher] (Official Graph API container & carousel publishing)
        │
        ▼
 [Memory & Logs]  (SQLite ledger + anti-repetition history + analytics loop)
```

---

## Quick Start (Zero-Error Local Run)

### 1. Install Dependencies

```bash
# Python 3.10+
pip install -r requirements.txt
playwright install chromium
```

### 2. Verify Diagnostic Health

```bash
python orchestrator.py --test
```

### 3. Run Pipeline in Safe Dry-Run Mode

```bash
python orchestrator.py --dry-run
```

This will:
1. Ingest seed sources and score topics.
2. Draft an 8-slide educational carousel.
3. Validate claims and verify the quality gate.
4. Render 1080×1350 JPEG slides into `output/YYYY-MM-DD/`.
5. Write `content.json`, `caption.txt`, and `manifest.json`.
6. Update local SQLite DB and content memory.

---

## Live Production Setup (Meta Instagram API)

When you're ready to publish live to your Instagram account:

1. Convert your Instagram account to a **Professional Account** (Creator or Business) inside the Instagram mobile app.
2. In the [Meta App Dashboard](https://developers.facebook.com/apps):
   - Add the **Instagram** product.
   - Choose **API setup with Instagram Login**.
   - Request scopes: `instagram_business_basic` and `instagram_business_content_publish`.
3. Generate your 60-day long-lived access token and find your Instagram User ID.
4. Copy `.env.example` to `.env` and fill in your keys:

```env
OPENAI_API_KEY=sk-...
IG_USER_ID=your_instagram_user_id
IG_ACCESS_TOKEN=your_long_lived_token
PUBLIC_CDN_BASE=https://your-domain-or-bucket.com
DRY_RUN=false
```

5. Run live publishing:

```bash
python orchestrator.py --run-all
```

---

## Slide Templates

The engine includes 8 deterministic templates in `renderer/templates/`:
- `hook.html` — Billboard hook with gradient headline and curiosity gap
- `standard.html` — Focused insight with proof box
- `checklist.html` — Actionable bullet items with custom check marks
- `comparison.html` — The Fragile Way vs. The Compound Way
- `diagram.html` — 3-step numbered pipeline flow
- `framework.html` — Structured rule or mental model
- `takeaway.html` — Distilled core lesson
- `cta.html` — Save/share prompt and brand avatar

All slides are styled by `renderer/css/design-system.css` at 1080×1350 (4:5 aspect ratio) with safe margins.

---

## Automation Options

### Option A: GitHub Actions (Recommended, No Server Required)
A preconfigured workflow is included in `.github/workflows/daily-post.yml`. Add your repository secrets (`IG_ACCESS_TOKEN`, `IG_USER_ID`, `OPENAI_API_KEY`) and it will run on schedule daily at 09:00 AM IST (or evening slot).

### Option B: n8n Workflow
Prebuilt n8n workflow JSON files are ready to import in `n8n/`:
- `n8n/workflow-daily-production.json` — 06:00 AM production trigger
- `n8n/workflow-publish.json` — 19:30 IST live publishing trigger
- `n8n/workflow-analytics.json` — Nightly learning loop

To start self-hosted n8n and Postgres:
```bash
docker compose up -d
```
Visit `http://localhost:5678` to import the workflows.
