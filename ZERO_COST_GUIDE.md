# Autogram: 100% Zero-Cost Guarantee ($0.00 / Month)

This guide proves how every single layer of the Autogram automation runs **100% free forever** with **no hidden subscriptions, no credit card requirements, and zero recurring fees**.

---

## The Complete $0.00 Stack Breakdown

| Component | Traditional Paid Way | Autogram Zero-Cost Way | Your Cost |
|---|---|---|---|
| **AI Copywriter** | OpenAI GPT-4 ($20–$50/mo) | Built-In Engine, Google Gemini Free Tier, or Groq Free Tier | **$0.00** |
| **Image / Slide Design** | Bannerbear / Placid ($49–$99/mo) | Built-in Playwright + HTML/CSS Design System | **$0.00** |
| **Asset Hosting** | AWS S3 / Cloudinary ($10–$25/mo) | Built-in `free_host.py` + Cloudflare Tunnel or Free R2 | **$0.00** |
| **Instagram Scheduler** | Buffer / Later / Hootsuite ($20–$60/mo) | Official Meta Graph API Direct Container Flow | **$0.00** |
| **Database** | Supabase Pro / AWS RDS ($25–$50/mo) | Local Embedded SQLite (`autopilot.db`) | **$0.00** |
| **Server / Compute** | DigitalOcean / AWS EC2 ($12–$40/mo) | Your own PC or GitHub Actions Free Tier (2,000 min/mo) | **$0.00** |
| **TOTAL** | **$166 – $374 / month** | **Autogram Automation** | **$0.00 / month** |

---

## 1. Content Generation: $0.00

You have **three 100% free options**:

### Option A: Built-in Free Knowledge Engine (Default - Zero Keys Required)
- **Cost**: **$0.00**
- Runs completely offline inside `src/content/free_knowledge_engine.py`.
- Generates deep, publication-grade carousels across all 6 pillars (AI Tools, Prompting, Marketing Psychology, Tech Explainers, Career, Contrarian).
- Requires **no account, no credit card, and no API key**.

### Option B: Google Gemini Free Tier (1,500 Free Requests / Day)
- **Cost**: **$0.00**
- Visit [Google AI Studio](https://aistudio.google.com/) and click **Get API key**.
- Gemini 2.0 Flash gives 1,500 requests per day for free (a daily carousel only needs 1 request).
- Add to `.env`:
  ```env
  GEMINI_API_KEY=your_free_gemini_key
  ```

### Option C: Groq Cloud (Free Llama 3.3 70B)
- **Cost**: **$0.00**
- Visit [Groq Console](https://console.groq.com/) and create a free API key.
- Add to `.env`:
  ```env
  GROQ_API_KEY=your_free_groq_key
  ```

---

## 2. Slide Rendering: $0.00

- Traditional tools charge $49/month for rendering template images.
- Autogram uses **Playwright Chromium** installed directly on your machine.
- It renders HTML/CSS templates into pixel-perfect 1080×1350 JPEGs locally at 0 cost.

---

## 3. Public Asset Hosting for Instagram: $0.00

Instagram requires a public HTTPS URL to download images during publishing. You do not need to pay for AWS S3.

### Method: Built-in Free Host + Cloudflare Tunnel
1. Start the free asset server in terminal:
   ```bash
   python free_host.py
   ```
2. In a second terminal, open a free secure tunnel:
   ```bash
   npx localtunnel --port 8000
   ```
   *(Or download free `cloudflared` from Cloudflare).*
3. Copy the free URL given (e.g. `https://quiet-frog-22.loca.lt`) and set it in `.env`:
   ```env
   PUBLIC_CDN_BASE=https://quiet-frog-22.loca.lt
   ```
4. **Cost**: **$0.00** permanently.

---

## 4. Instagram Publishing: $0.00

- Meta's official Graph API for Instagram Professional (Creator or Business) accounts is **100% free**.
- Meta does not charge developers or creators to publish photos, carousels, or reels.
- You do not need Buffer, Later, or Hootsuite.

---

## 5. Scheduling & Database: $0.00

- **Database**: Runs on local SQLite (`autopilot.db`). No cloud database fees.
- **Scheduler**:
  - Run locally via Windows Task Scheduler (100% free on your PC).
  - Or run via GitHub Actions (`.github/workflows/daily-post.yml`). GitHub provides 2,000 free runner minutes per month. A daily carousel post takes ~30 seconds, using only ~15 minutes per month.

---

## Summary

You can run this automation indefinitely without spending a single dollar. Everything has been built to be self-contained, open-source, and zero-cost.
