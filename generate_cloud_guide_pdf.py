"""
generate_cloud_guide_pdf.py
Compiles the Zero-PC Cloud Automation Architecture Guide into a publication-grade PDF
using Playwright and modern typography.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_PDF = Path("d:/Autogram/docs/Cloud_Automation_Zero_PC_Guide.pdf")
ARTIFACT_PDF = Path(r"C:\Users\Piyush\.gemini\antigravity\brain\a8124c42-154b-496f-9b68-ff045251762a\Cloud_Automation_Zero_PC_Guide.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

@page {
  size: A4;
  margin: 20mm 15mm 20mm 15mm;
  @bottom-right {
    content: counter(page);
    font-family: 'JetBrains Mono', monospace;
    font-size: 9pt;
    color: #64748B;
  }
}

* {
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #0F172A;
  line-height: 1.6;
  font-size: 10.5pt;
  background: #FFFFFF;
}

header {
  border-bottom: 2px solid #0F172A;
  padding-bottom: 12px;
  margin-bottom: 24px;
}

.studio-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9pt;
  font-weight: 700;
  color: #FF5500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  font-size: 22pt;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.2;
  margin: 8px 0 4px 0;
}

.subtitle {
  font-size: 12pt;
  color: #475569;
  font-weight: 500;
  margin-bottom: 12px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 8.5pt;
  margin-top: 10px;
}

.meta-item strong {
  color: #0F172A;
  display: block;
}

h2 {
  font-size: 14pt;
  font-weight: 700;
  color: #0F172A;
  margin-top: 24px;
  margin-bottom: 10px;
  border-bottom: 1px solid #E2E8F0;
  padding-bottom: 6px;
}

h3 {
  font-size: 11.5pt;
  font-weight: 700;
  color: #1E293B;
  margin-top: 16px;
  margin-bottom: 6px;
}

p {
  margin-bottom: 10px;
  color: #334155;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  font-size: 9pt;
}

th, td {
  border: 1px solid #CBD5E1;
  padding: 8px 10px;
  text-align: left;
}

th {
  background: #F1F5F9;
  font-weight: 700;
  color: #0F172A;
}

pre {
  background: #0F172A;
  color: #F8FAFC;
  padding: 12px 14px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 8pt;
  line-height: 1.45;
  overflow-x: auto;
  margin: 12px 0;
}

code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 8.5pt;
  background: #F1F5F9;
  padding: 2px 5px;
  border-radius: 4px;
  color: #0F172A;
}

pre code {
  background: transparent;
  color: inherit;
  padding: 0;
}

ul, ol {
  margin: 8px 0 14px 20px;
  color: #334155;
}

li {
  margin-bottom: 5px;
}

.callout {
  background: #FFF7ED;
  border-left: 4px solid #FF5500;
  padding: 12px 16px;
  border-radius: 0 6px 6px 0;
  margin: 14px 0;
  font-size: 9.5pt;
}

.callout-title {
  font-weight: 700;
  color: #9A3412;
  margin-bottom: 4px;
}

.page-break {
  page-break-before: always;
}
</style>
</head>
<body>

<header>
  <div class="studio-tag">Signhify Studio // Production Engineering Blueprint</div>
  <h1>Zero-PC Cloud Automation Architecture</h1>
  <div class="subtitle">How to Run Autogram 24/7 in the Cloud for $0 Using Free Developer Infrastructure</div>
  <div class="meta-grid">
    <div class="meta-item"><strong>ENGINE:</strong> Autogram v5.2</div>
    <div class="meta-item"><strong>STUDIO:</strong> signhify.dpdns.org</div>
    <div class="meta-item"><strong>HARDWARE:</strong> $0 Required</div>
    <div class="meta-item"><strong>CADENCE:</strong> 4 Drops Daily</div>
  </div>
</header>

<h2>1. Executive Summary & Strategy</h2>
<p>
This blueprint details how to transition Autogram from running locally on your workstation to an enterprise-grade, 100% autonomous cloud pipeline that operates 24/7 with zero PC uptime. By chaining five free cloud developer tiers, your content publishing machine generates high-retention carousels, video reels, and interactive stories while you sleep.
</p>

<h2>2. The Zero-Dollar Cloud Tech Stack</h2>
<table>
  <tr>
    <th>Service</th>
    <th>Free Allowance</th>
    <th>Role in Autogram</th>
    <th>Cost</th>
  </tr>
  <tr>
    <td><strong>GitHub Actions</strong></td>
    <td>2,000 Linux min/mo (Private) / Unlimited (Public)</td>
    <td>Executes pipeline, runs Playwright & Remotion, commits memory</td>
    <td><strong>$0.00</strong></td>
  </tr>
  <tr>
    <td><strong>Cloudflare Workers</strong></td>
    <td>100,000 req/day, 10ms CPU</td>
    <td>Exact-second cron triggers to eliminate GitHub Actions delay</td>
    <td><strong>$0.00</strong></td>
  </tr>
  <tr>
    <td><strong>Cloudflare R2</strong></td>
    <td>10 GB storage/mo, $0 egress fees</td>
    <td>Zero-cost media hosting for Meta Graph API container ingestion</td>
    <td><strong>$0.00</strong></td>
  </tr>
  <tr>
    <td><strong>Render.com</strong></td>
    <td>750 free instance hours/mo</td>
    <td>Hosts dashboard API and emergency failover webhook endpoint</td>
    <td><strong>$0.00</strong></td>
  </tr>
  <tr>
    <td><strong>ManyChat Cloud</strong></td>
    <td>Free tier (up to 1,000 contacts)</td>
    <td>Cloud-native comment listener & follow-gated DM automations</td>
    <td><strong>$0.00</strong></td>
  </tr>
</table>

<div class="callout">
  <div class="callout-title">💡 Why Cloudflare R2 Beats AWS S3</div>
  Meta's Graph API must download every 1080x1350 image slide and 60fps MP4 reel directly from a public URL. AWS S3 charges $0.09/GB for data egress. Cloudflare R2 has <strong>zero egress bandwidth fees</strong>, saving hundreds of dollars per year at high publishing volumes.
</div>

<div class="page-break"></div>

<h2>3. GitHub Actions Master Workflow: <code>daily-autopilot.yml</code></h2>
<p>Save this configuration file in your repository at <code>.github/workflows/daily-autopilot.yml</code>:</p>

<pre><code>name: Autogram 24/7 Cloud Autopilot

on:
  schedule:
    # 4 Daily Publishing Drops (Asia/Kolkata: UTC + 5:30)
    - cron: '0 4 * * *'   # 09:30 AM IST (04:00 UTC) — Morning High-Signal Story
    - cron: '0 6 * * *'   # 11:30 AM IST (06:00 UTC) — Midday Prime Carousel
    - cron: '0 12 * * *'  # 05:30 PM IST (12:00 UTC) — Evening Tech Radar Story
    - cron: '0 14 * * *'  # 07:30 PM IST (14:00 UTC) — Evening Prime Reel / Carousel
  repository_dispatch:
    types: [publish-slot, trigger-autopilot]
  workflow_dispatch:

jobs:
  autopilot:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    permissions:
      contents: write

    steps:
      - name: 1. Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: 2. Set Up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: 3. Install Core Python Dependencies
        run: pip install -r requirements.txt

      - name: 4. Install Playwright Headless Chromium & System Fonts
        run: |
          playwright install --with-deps chromium
          sudo apt-get update && sudo apt-get install -y fonts-inter ffmpeg

      - name: 5. Execute Autonomous Publishing Engine
        env:
          AUTOGRAM_OWNER_KEY: ${{ secrets.AUTOGRAM_OWNER_KEY || 'autogram_owner_vip_2026' }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          IG_USER_ID: ${{ secrets.IG_USER_ID }}
          IG_ACCESS_TOKEN: ${{ secrets.IG_ACCESS_TOKEN }}
          PUBLIC_CDN_BASE: ${{ secrets.PUBLIC_CDN_BASE }}
          DRY_RUN: 'false'
        run: python orchestrator.py --run-all

      - name: 6. Persist Content Memory & Anti-Repetition Ledger
        if: always()
        run: |
          git config --global user.name "autogram-cloud-bot"
          git config --global user.email "bot@signhify.dpdns.org"
          git pull --rebase origin main || true
          git add data/content-memory.json data/schedule.json autopilot.db || true
          git diff --cached --quiet || git commit -m "chore(cloud): sync memory [skip ci]"
          git push origin main || true
</code></pre>

<div class="page-break"></div>

<h2>4. Cloudflare Worker: Zero-Jitter Cron Dispatcher</h2>
<p>
GitHub's native scheduled crons can occasionally queue for 5 to 20 minutes during peak hours. Deploy this lightweight Cloudflare Worker with a Cron Trigger to fire an instant <code>repository_dispatch</code> event to GitHub at the exact second:
</p>

<pre><code>// Cloudflare Worker: autogram-cron-dispatcher.js
export default {
  async scheduled(event, env, ctx) {
    const GITHUB_REPO = "YourUsername/Autogram";
    const GITHUB_TOKEN = env.GH_PAT_TOKEN; // GitHub Personal Access Token

    const response = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/dispatches`, {
      method: "POST",
      headers: {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": `Bearer ${GITHUB_TOKEN}`,
        "User-Agent": "Autogram-Cloudflare-Cron"
      },
      body: JSON.stringify({
        event_type: "publish-slot",
        client_payload: { slot: event.cron, timestamp: new Date().toISOString() }
      })
    });
    console.log(`Dispatched GitHub Actions Autopilot: HTTP ${response.status}`);
  }
};
</code></pre>

<h2>5. Required GitHub Secrets Checklist</h2>
<table>
  <tr>
    <th>Secret Key</th>
    <th>Description</th>
    <th>Value / Source</th>
  </tr>
  <tr>
    <td><code>AUTOGRAM_OWNER_KEY</code></td>
    <td>HMAC-SHA256 license bypass</td>
    <td><code>autogram_owner_vip_2026</code></td>
  </tr>
  <tr>
    <td><code>GEMINI_API_KEY</code></td>
    <td>Google Gemini AI key</td>
    <td>Google AI Studio</td>
  </tr>
  <tr>
    <td><code>OPENROUTER_API_KEY</code></td>
    <td>Multi-LLM fallback chain</td>
    <td>OpenRouter.ai</td>
  </tr>
  <tr>
    <td><code>IG_USER_ID</code></td>
    <td>Instagram Business Account ID</td>
    <td>Meta Developer Console</td>
  </tr>
  <tr>
    <td><code>IG_ACCESS_TOKEN</code></td>
    <td>60-Day Long-Lived Token</td>
    <td>Meta Graph API Explorer</td>
  </tr>
  <tr>
    <td><code>CLOUDFLARE_API_TOKEN</code></td>
    <td>Cloudflare R2 Bucket Token</td>
    <td>Cloudflare Dashboard → R2</td>
  </tr>
  <tr>
    <td><code>PUBLIC_CDN_BASE</code></td>
    <td>Public Media Base URL</td>
    <td><code>https://cdn.signhify.dpdns.org</code></td>
  </tr>
</table>

<h2>6. Final Deployment Checklist</h2>
<ol>
  <li><strong>Push Local Code to GitHub:</strong> Ensure all files in <code>d:\Autogram</code> are pushed to your remote <code>main</code> branch.</li>
  <li><strong>Populate GitHub Secrets:</strong> Add the 7 keys from the table above into GitHub Repository Settings.</li>
  <li><strong>Enable Workflow Write Permissions:</strong> Under <em>Settings → Actions → General → Workflow permissions</em>, select <strong>"Read and write permissions"</strong> so the cloud runner can commit the updated anti-repetition memory back to Git.</li>
  <li><strong>Trigger Initial Test Run:</strong> Go to <em>Actions → Autogram 24/7 Cloud Autopilot → Run workflow</em>.</li>
  <li><strong>Power Down Your Workstation:</strong> Your machine can now be turned off. The cloud infrastructure will handle 100% of generation, rendering, uploading, and publishing autonomously.</li>
</ol>

</body>
</html>
"""

def generate_pdf():
    print("Launching Chromium to generate PDF...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(HTML_CONTENT, wait_until="networkidle")
        
        OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(OUTPUT_PDF),
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"}
        )
        print(f"Generated PDF: {OUTPUT_PDF}")
        
        # Copy to artifact directory
        ARTIFACT_PDF.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PDF, "rb") as f_in, open(ARTIFACT_PDF, "wb") as f_out:
            f_out.write(f_in.read())
        print(f"Saved artifact PDF: {ARTIFACT_PDF}")
        
        browser.close()

if __name__ == "__main__":
    generate_pdf()

