#!/usr/bin/env python3
"""
generate_pdf_guide.py
Compiles AUTOGRAM_CONFIGURATION_GUIDE.md into an executive publication-grade PDF using Playwright Chromium.
"""

import sys
from pathlib import Path
import markdown
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent
MD_PATH = WORKSPACE_DIR / "AUTOGRAM_CONFIGURATION_GUIDE.md"
PDF_PATH = WORKSPACE_DIR / "AUTOGRAM_CONFIGURATION_GUIDE.pdf"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Autogram Master Configuration & Operations Guide</title>
<style>
  :root {{
    --primary: #4338CA;
    --primary-dark: #312E81;
    --primary-light: #EEF2FF;
    --text-main: #0F172A;
    --text-muted: #64748B;
    --bg-page: #FFFFFF;
    --bg-code: #0F172A;
    --border-color: #CBD5E1;
    --accent-cyan: #0284C7;
    --accent-emerald: #059669;
    --accent-amber: #D97706;
  }}

  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: var(--text-main);
    background: var(--bg-page);
    line-height: 1.6;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
  }}

  /* Cover Banner */
  .cover-banner {{
    background: linear-gradient(135deg, #090D1A 0%, #1E1B4B 50%, #090D1A 100%);
    color: #FFFFFF;
    padding: 36px 32px;
    border-radius: 10px;
    margin-bottom: 26px;
    border: 1px solid rgba(255, 255, 255, 0.15);
  }}

  .cover-badge {{
    display: inline-block;
    background: rgba(99, 102, 241, 0.3);
    border: 1px solid rgba(165, 180, 252, 0.6);
    color: #E0E7FF;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 9999px;
    margin-bottom: 14px;
  }}

  .cover-title {{
    font-size: 24pt;
    font-weight: 800;
    line-height: 1.15;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
    color: #FFFFFF;
  }}

  .cover-subtitle {{
    font-size: 11.5pt;
    color: #94A3B8;
    margin: 0 0 20px 0;
    font-weight: 400;
  }}

  .cover-meta {{
    display: flex;
    gap: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 16px;
    font-size: 8.5pt;
    color: #CBD5E1;
  }}

  .meta-item strong {{
    color: #FFFFFF;
    font-weight: 700;
  }}

  /* Headings */
  h1 {{
    font-size: 17pt;
    font-weight: 800;
    color: var(--primary-dark);
    border-bottom: 2px solid var(--primary);
    padding-bottom: 6px;
    margin-top: 32px;
    margin-bottom: 14px;
    page-break-after: avoid;
    letter-spacing: -0.3px;
  }}

  h2 {{
    font-size: 13.5pt;
    font-weight: 700;
    color: #1E293B;
    margin-top: 24px;
    margin-bottom: 10px;
    page-break-after: avoid;
    border-left: 4px solid var(--accent-cyan);
    padding-left: 8px;
  }}

  h3 {{
    font-size: 11.5pt;
    font-weight: 700;
    color: #334155;
    margin-top: 18px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }}

  p, li {{
    color: #334155;
    font-size: 10pt;
    margin-top: 0;
    margin-bottom: 8px;
  }}

  ul, ol {{
    padding-left: 20px;
    margin-bottom: 12px;
  }}

  li {{
    margin-bottom: 3px;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 18px 0;
    font-size: 9pt;
    page-break-inside: avoid;
    border: 1px solid var(--border-color);
  }}

  th {{
    background: #F1F5F9;
    color: #0F172A;
    font-weight: 700;
    text-align: left;
    padding: 8px 10px;
    border-bottom: 2px solid var(--border-color);
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  td {{
    padding: 7px 10px;
    border-bottom: 1px solid #E2E8F0;
    color: #334155;
    vertical-align: top;
  }}

  tr:nth-child(even) td {{
    background: #F8FAFC;
  }}

  /* Code Blocks */
  pre {{
    background: var(--bg-code);
    color: #F8FAFC;
    padding: 12px 14px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: Consolas, "Courier New", monospace;
    font-size: 8.5pt;
    line-height: 1.45;
    margin: 12px 0 16px 0;
    page-break-inside: avoid;
    border: 1px solid #334155;
  }}

  code {{
    font-family: Consolas, "Courier New", monospace;
    font-size: 8.5pt;
    background: #F1F5F9;
    color: #0F172A;
    padding: 1px 5px;
    border-radius: 3px;
    border: 1px solid #CBD5E1;
  }}

  pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: 8.5pt;
  }}

  blockquote {{
    margin: 14px 0;
    padding: 10px 16px;
    background: var(--primary-light);
    border-left: 4px solid var(--primary);
    border-radius: 0 6px 6px 0;
    color: #1E1B4B;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }}

  blockquote p {{
    margin: 0;
    color: inherit;
  }}

  hr {{
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 20px 0;
  }}

  a {{
    color: var(--primary);
    text-decoration: none;
  }}

  @page {{
    size: A4;
    margin: 16mm 12mm 16mm 12mm;
  }}
</style>
</head>
<body>

<div class="cover-banner">
  <div class="cover-badge">Official Architecture & Configuration Manual</div>
  <h1 class="cover-title">Autogram Master Configuration Guide</h1>
  <p class="cover-subtitle">Zero-Cost Autonomous Instagram Content Generation, Scheduling, Monetization & Publishing</p>
  <div class="cover-meta">
    <div class="meta-item"><strong>Platform:</strong> Autogram AI v2.0</div>
    <div class="meta-item"><strong>Operating Cost:</strong> $0.00 / mo</div>
    <div class="meta-item"><strong>Status:</strong> Production Ready</div>
    <div class="meta-item"><strong>Last Updated:</strong> September 2026</div>
  </div>
</div>

<div class="guide-content">
{content}
</div>

</body>
</html>
"""

def generate_pdf():
    print(f"Reading markdown from: {MD_PATH}", flush=True)
    if not MD_PATH.exists():
        print(f"Error: {MD_PATH} not found.", flush=True)
        sys.exit(1)

    raw_md = MD_PATH.read_text(encoding="utf-8")

    html_body = markdown.markdown(
        raw_md,
        extensions=[
            "tables",
            "fenced_code",
            "toc",
            "nl2br",
            "sane_lists"
        ]
    )

    full_html = HTML_TEMPLATE.format(content=html_body)

    print("Launching Playwright Chromium...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Setting page content...", flush=True)
        page.set_content(full_html, wait_until="load")

        print(f"Rendering PDF to: {PDF_PATH}...", flush=True)
        page.pdf(
            path=str(PDF_PATH),
            format="A4",
            print_background=True,
            margin={
                "top": "16mm",
                "bottom": "16mm",
                "left": "12mm",
                "right": "12mm"
            },
            display_header_footer=True,
            header_template="""
            <div style="font-size: 7.5pt; color: #94A3B8; font-family: sans-serif; width: 100%; padding: 0 12mm; display: flex; justify-content: space-between;">
              <span>Autogram AI — Master Configuration & Operations Guide</span>
              <span>Zero-Cost Autonomous Engine</span>
            </div>
            """,
            footer_template="""
            <div style="font-size: 7.5pt; color: #94A3B8; font-family: sans-serif; width: 100%; padding: 0 12mm; display: flex; justify-content: space-between;">
              <span>Confidential & Proprietary</span>
              <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
            </div>
            """
        )
        browser.close()

    size = PDF_PATH.stat().st_size
    print(f"[SUCCESS] PDF generated successfully! Size: {size:,} bytes", flush=True)

if __name__ == "__main__":
    generate_pdf()
