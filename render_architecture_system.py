"""
render_architecture_system.py
Renders the high-converting 'How We Fully Automate It' AI Content Engine Architecture
in both 1080x1920 (Instagram Story) and 1080x1350 (Feed Post/Slide) formats using Playwright.
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("d:/Autogram/output/architecture-pipeline")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\Piyush\.gemini\antigravity\brain\a8124c42-154b-496f-9b68-ff045251762a\architecture_pipeline")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

HTML_STORY = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
}

body {
  width: 1080px;
  height: 1920px;
  background-color: #06090F;
  background-image: 
    radial-gradient(circle at 50% 20%, rgba(255, 85, 0, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 50% 70%, rgba(0, 229, 153, 0.05) 0%, transparent 45%),
    radial-gradient(rgba(255, 255, 255, 0.09) 1.5px, transparent 1.5px);
  background-size: 100% 100%, 100% 100%, 28px 28px;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #FFFFFF;
  position: relative;
  overflow: hidden;
}

/* Studio Watermark & Header */
.top-bar {
  position: absolute;
  top: 70px;
  left: 70px;
  right: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 24px;
}

.studio-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #F8FAFC;
}

.studio-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #00E599;
  box-shadow: 0 0 12px #00E599;
}

.pipeline-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 15px;
  color: #94A3B8;
  background: rgba(255, 255, 255, 0.06);
  padding: 8px 16px;
  border-radius: 100px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* SVG Connecting Lines */
svg.connector-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 1080px;
  height: 1920px;
  pointer-events: none;
  z-index: 1;
}

/* Pipeline Nodes */
.node {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  z-index: 2;
}

.node-icon {
  width: 90px;
  height: 90px;
  border-radius: 24px;
  background: #121824;
  border: 1.5px solid rgba(255, 255, 255, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.15);
  margin-bottom: 12px;
}

.node-title {
  font-size: 20px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 4px;
  letter-spacing: -0.01em;
}

.node-sub {
  font-size: 14px;
  font-weight: 500;
  color: #94A3B8;
}

/* Specific Node Positions */
#node-yt-api {
  top: 180px;
  left: 140px;
}

#node-fable {
  top: 180px;
  left: 495px;
  transform: translateX(-50%);
}

#node-perplexity {
  top: 180px;
  right: 140px;
}

#node-opus {
  top: 360px;
  left: 495px;
  transform: translateX(-50%);
}

/* Decision Diamond */
.diamond-container {
  position: absolute;
  top: 550px;
  left: 495px;
  transform: translateX(-50%);
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.diamond-shape {
  width: 440px;
  height: 76px;
  border: 1.5px solid rgba(255, 255, 255, 0.35);
  background: #0E1420;
  clip-path: polygon(18px 0%, calc(100% - 18px) 0%, 100% 50%, calc(100% - 18px) 100%, 18px 100%, 0% 50%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.diamond-text {
  font-size: 22px;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: -0.01em;
}

.branch-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 700;
  color: #94A3B8;
  background: #06090F;
  padding: 3px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  position: absolute;
  z-index: 3;
}

/* Stock Footage Fallback Box */
.stock-box {
  position: absolute;
  top: 755px;
  right: 80px;
  width: 630px;
  padding: 24px 28px;
  border-radius: 20px;
  border: 1.5px dashed rgba(255, 255, 255, 0.25);
  background: rgba(18, 24, 36, 0.65);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 2;
}

.stock-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stock-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 26px;
  margin-bottom: 10px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}

/* Big Central Pill Banner */
.center-pill-banner {
  position: absolute;
  top: 670px;
  left: 70px;
  right: 70px;
  height: 64px;
  background: #FFFFFF;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), 0 0 40px rgba(255, 255, 255, 0.15);
  z-index: 10;
}

.center-pill-text {
  color: #06090F;
  font-size: 32px;
  font-weight: 900;
  letter-spacing: -0.02em;
}

/* Core Engine: HyperFrames */
#node-hyperframes {
  top: 960px;
  left: 540px;
  transform: translateX(-50%);
}

#node-hyperframes .node-icon {
  width: 110px;
  height: 110px;
  border-radius: 28px;
  background: #0B1622;
  border: 2px solid #00E599;
  box-shadow: 0 0 35px rgba(0, 229, 153, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.2);
}

#node-hyperframes .node-title {
  font-size: 24px;
  font-weight: 800;
  color: #00E599;
}

#node-hyperframes .node-sub {
  font-size: 15px;
  color: #CBD5E1;
}

/* Audio Inputs */
#node-elevenlabs {
  top: 965px;
  left: 120px;
}

#node-suno {
  top: 965px;
  right: 120px;
}

/* Bottom Output Stream */
.output-row {
  position: absolute;
  top: 1250px;
  left: 70px;
  right: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 2;
}

.out-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 210px;
}

.out-icon {
  width: 84px;
  height: 84px;
  border-radius: 22px;
  background: #121824;
  border: 1.5px solid rgba(255, 255, 255, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px rgba(0,0,0,0.4);
  margin-bottom: 12px;
}

/* Big Conversion CTA Pill */
.bottom-cta-banner {
  position: absolute;
  bottom: 130px;
  left: 70px;
  right: 70px;
  height: 96px;
  background: #B6F0D3;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 50px rgba(0, 229, 153, 0.25), 0 0 30px rgba(182, 240, 211, 0.4);
  z-index: 10;
  border: 1px solid #D4FBE6;
}

.bottom-cta-text {
  color: #062817;
  font-size: 32px;
  font-weight: 900;
  letter-spacing: -0.02em;
  text-align: center;
}

.footer-domain {
  position: absolute;
  bottom: 65px;
  left: 0;
  right: 0;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  color: #64748B;
  letter-spacing: 0.1em;
}
</style>
</head>
<body>

<!-- Top Bar -->
<div class="top-bar">
  <div class="studio-badge">
    <div class="studio-dot"></div>
    <span>SIGNHIFY.STUDIO</span>
  </div>
  <div class="pipeline-tag">AUTONOMOUS VIDEO SYSTEM v5.2</div>
</div>

<!-- SVG Connecting Lines & Arrows -->
<svg class="connector-canvas" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#CBD5E1"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#00E599"/>
    </marker>
  </defs>

  <!-- YouTube -> Fable -->
  <line x1="250" y1="225" x2="435" y2="225" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- Fable -> Opus -->
  <line x1="495" y1="300" x2="495" y2="350" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- Perplexity -> Opus -->
  <path d="M 870 300 L 870 410 L 580 410" fill="none" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- Opus -> Diamond -->
  <line x1="495" y1="480" x2="495" y2="540" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- Diamond 'yes' branch -> HyperFrames -->
  <path d="M 275 625 L 275 990 L 460 990" fill="none" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- Diamond 'no' branch -> Stock Footage Box -->
  <path d="M 715 625 L 820 625 L 820 745" fill="none" stroke="#64748B" stroke-width="2" stroke-dasharray="6,6" marker-end="url(#arrow)"/>

  <!-- Stock Box -> HyperFrames -->
  <path d="M 680 885 L 680 940 L 590 940" fill="none" stroke="#64748B" stroke-width="2" stroke-dasharray="6,6" marker-end="url(#arrow)"/>

  <!-- ElevenLabs -> HyperFrames -->
  <line x1="220" y1="1010" x2="455" y2="1010" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- Suno -> HyperFrames -->
  <line x1="860" y1="1010" x2="625" y2="1010" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- HyperFrames -> FFmpeg (in output row) -->
  <path d="M 540 1090 L 540 1180 L 175 1180 L 175 1240" fill="none" stroke="#00E599" stroke-width="2.5" marker-end="url(#arrow-green)"/>

  <!-- FFmpeg -> GPT Image -->
  <line x1="270" y1="1295" x2="385" y2="1295" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- GPT Image -> Zernio -->
  <line x1="565" y1="1295" x2="685" y2="1295" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- Zernio -> YouTube -->
  <line x1="860" y1="1295" x2="925" y2="1295" stroke="#FF5500" stroke-width="2.5" marker-end="url(#arrow)"/>
</svg>

<!-- Node: YouTube Data API -->
<div class="node" id="node-yt-api">
  <div class="node-icon" style="background:#FFF;">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="#FF0000">
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.5 12 3.5 12 3.5s-7.505 0-9.377.55a3.016 3.016 0 0 0-2.122 2.136C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.55 9.376.55 9.376.55s7.505 0 9.377-.55a3.016 3.016 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
    </svg>
  </div>
  <div class="node-title">YouTube Data API</div>
  <div class="node-sub">Finds viral scripts</div>
</div>

<!-- Node: Fable 5.1 -->
<div class="node" id="node-fable">
  <div class="node-icon" style="background: #181313; border-color: #FF5500;">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#FF7733" stroke-width="2.2" stroke-linecap="round">
      <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
      <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
      <circle cx="12" cy="12" r="3" fill="#FF7733"/>
    </svg>
  </div>
  <div class="node-title">Fable 5.1</div>
  <div class="node-sub">Writes the script</div>
</div>

<!-- Node: Perplexity -->
<div class="node" id="node-perplexity">
  <div class="node-icon" style="background:#0F1D21; border-color: #22D3EE;">
    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#22D3EE" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M4.93 19.07l14.14-14.14"/>
      <rect x="7" y="7" width="10" height="10" rx="2" stroke="#22D3EE"/>
    </svg>
  </div>
  <div class="node-title">Perplexity</div>
  <div class="node-sub">Researches + verifies</div>
</div>

<!-- Node: Opus 5.5 -->
<div class="node" id="node-opus">
  <div class="node-icon" style="background: #1C1318; border-color: #FF5500;">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#FF5500" stroke-width="2.5" stroke-linecap="round">
      <path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M5.6 18.4L18.4 5.6"/>
      <circle cx="12" cy="12" r="4" fill="#FF5500"/>
    </svg>
  </div>
  <div class="node-title">Opus 5.5</div>
  <div class="node-sub">Animates everything</div>
</div>

<!-- Decision Diamond -->
<div class="diamond-container">
  <div class="diamond-shape">
    <span class="diamond-text">Can Opus animate it?</span>
  </div>
</div>
<div class="branch-label" style="top: 615px; left: 245px;">yes</div>
<div class="branch-label" style="top: 615px; left: 740px;">no</div>

<!-- Center Pill Banner -->
<div class="center-pill-banner">
  <span class="center-pill-text">How we fully automate it</span>
</div>

<!-- Stock Footage Fallback Box -->
<div class="stock-box">
  <div class="stock-item">
    <div class="stock-icon" style="background:#02BE6E; color:#FFF;">px</div>
    <div class="node-title" style="font-size: 18px;">Pixabay API</div>
    <div class="node-sub">Stock footage</div>
  </div>
  <div class="stock-item">
    <div class="stock-icon" style="background:#05A081; color:#FFF;">P</div>
    <div class="node-title" style="font-size: 18px;">Pexels API</div>
    <div class="node-sub">Stock footage</div>
  </div>
  <div class="stock-item">
    <div class="stock-icon" style="background:#82B541; color:#FFF;">
      <svg width="34" height="34" viewBox="0 0 24 24" fill="#FFF"><path d="M20.5 4.5c-2.3 2.3-5.3 4.2-8.5 5.2-1.6.5-3.3.8-5 1 2.4 1.5 5.3 2.3 8.3 2.1 2.6-.2 5-1.2 7-2.8-.4 3.7-2.3 7-5.3 9.1-3 2.1-6.8 2.8-10.4 1.9 3.5-3 5.4-7.6 5.1-12.2-.2-3.1-1.6-6-3.7-8.3 4.2 0 8.4 1.6 11.5 4.7z"/></svg>
    </div>
    <div class="node-title" style="font-size: 18px;">Envato Elements</div>
    <div class="node-sub">Stock footage</div>
  </div>
</div>

<!-- ElevenLabs V4 -->
<div class="node" id="node-elevenlabs">
  <div class="node-icon" style="background:#000; border-color:#FFF;">
    <svg width="38" height="38" viewBox="0 0 24 24" fill="#FFF">
      <rect x="7" y="4" width="3.5" height="16" rx="1.5"/>
      <rect x="13.5" y="4" width="3.5" height="16" rx="1.5"/>
    </svg>
  </div>
  <div class="node-title">ElevenLabs V4</div>
  <div class="node-sub">Voiceover</div>
</div>

<!-- Central Engine: HyperFrames -->
<div class="node" id="node-hyperframes">
  <div class="node-icon">
    <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#00E599" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="16 18 22 12 16 6"/>
      <polyline points="8 6 2 12 8 18"/>
      <circle cx="12" cy="12" r="2.5" fill="#00E599"/>
    </svg>
  </div>
  <div class="node-title">HyperFrames</div>
  <div class="node-sub">Builds the 30–40 min video</div>
</div>

<!-- Suno -->
<div class="node" id="node-suno">
  <div class="node-icon" style="background:#000; border-color:#E2E8F0;">
    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#FFF" stroke-width="2.2" stroke-linecap="round">
      <path d="M9 18V5l12-2v13"/>
      <circle cx="6" cy="18" r="3" fill="#FFF"/>
      <circle cx="18" cy="16" r="3" fill="#FFF"/>
    </svg>
  </div>
  <div class="node-title">Suno</div>
  <div class="node-sub">Soundtrack & Score</div>
</div>

<!-- Bottom Output Stream -->
<div class="output-row">
  <!-- FFmpeg -->
  <div class="out-node">
    <div class="out-icon" style="border-color:#00E599; background:#071A14;">
      <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#00E599" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="5 3 19 12 5 21 5 3"/>
        <line x1="19" y1="3" x2="19" y2="21"/>
      </svg>
    </div>
    <div class="node-title">FFmpeg</div>
    <div class="node-sub">Final encode</div>
  </div>

  <!-- GPT Image 2.5 -->
  <div class="out-node">
    <div class="out-icon" style="background:#0C1717; border-color:#10A37F;">
      <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#10A37F" stroke-width="2" stroke-linecap="round">
        <circle cx="12" cy="12" r="9"/>
        <path d="M12 3a9 9 0 0 0 0 18"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
    </div>
    <div class="node-title">GPT Image 2.5</div>
    <div class="node-sub">Thumbnail</div>
  </div>

  <!-- Zernio API -->
  <div class="out-node">
    <div class="out-icon" style="background:#1B0E10; border-color:#F43F5E;">
      <svg width="44" height="44" viewBox="0 0 24 24" fill="#F43F5E">
        <polygon points="12 2 2 22 22 22"/>
      </svg>
    </div>
    <div class="node-title">Zernio API</div>
    <div class="node-sub">Posts it</div>
  </div>

  <!-- YouTube Live -->
  <div class="out-node">
    <div class="out-icon" style="background:#FFF;">
      <svg width="44" height="44" viewBox="0 0 24 24" fill="#FF0000">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.5 12 3.5 12 3.5s-7.505 0-9.377.55a3.016 3.016 0 0 0-2.122 2.136C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.55 9.376.55 9.376.55s7.505 0 9.377-.55a3.016 3.016 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
      </svg>
    </div>
    <div class="node-title">YouTube</div>
    <div class="node-sub" style="color:#FF5500; font-weight:700;">● Live</div>
  </div>
</div>

<!-- Big Bottom Mint CTA Banner -->
<div class="bottom-cta-banner">
  <span class="bottom-cta-text">Want fully made system for you ? Reply to this story</span>
</div>

<!-- Footer Branding -->
<div class="footer-domain">ARCHITECTED BY SIGNHIFY.STUDIO &bull; SIGNHIFY.DPDNS.ORG</div>

</body>
</html>
"""

def render_pipeline():
    print("Launching Chromium via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 1. Render Instagram Story (1080x1920)
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page.set_content(HTML_STORY, wait_until="networkidle")
        page.wait_for_timeout(1000)
        
        story_path = OUTPUT_DIR / "story_automation_pipeline_1080x1920.jpg"
        page.screenshot(path=str(story_path), type="jpeg", quality=95)
        print(f"Rendered Story: {story_path}")
        
        # Copy to brain artifact
        artifact_story = ARTIFACT_DIR / "story_automation_pipeline_1080x1920.jpg"
        with open(story_path, "rb") as f_in, open(artifact_story, "wb") as f_out:
            f_out.write(f_in.read())
        print(f"Saved artifact: {artifact_story}")

        # Also copy directly to brain root for direct viewer linking
        brain_root_story = Path(r"C:\Users\Piyush\.gemini\antigravity\brain\a8124c42-154b-496f-9b68-ff045251762a\story_automation_pipeline_1080x1920.jpg")
        with open(story_path, "rb") as f_in, open(brain_root_story, "wb") as f_out:
            f_out.write(f_in.read())

        # 2. Render Feed Carousel / Post (1080x1350)
        page_post = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        # Apply CSS scale to fit 1920 content into 1350 height seamlessly
        scaled_html = HTML_STORY.replace(
            "body {",
            "body { transform: scale(0.703); transform-origin: top center; "
        ).replace(
            "height: 1920px;",
            "height: 1350px;"
        )
        page_post.set_content(scaled_html, wait_until="networkidle")
        page_post.wait_for_timeout(1000)
        
        post_path = OUTPUT_DIR / "post_automation_pipeline_1080x1350.jpg"
        page_post.screenshot(path=str(post_path), type="jpeg", quality=95)
        print(f"Rendered Feed Post: {post_path}")
        
        brain_root_post = Path(r"C:\Users\Piyush\.gemini\antigravity\brain\a8124c42-154b-496f-9b68-ff045251762a\post_automation_pipeline_1080x1350.jpg")
        with open(post_path, "rb") as f_in, open(brain_root_post, "wb") as f_out:
            f_out.write(f_in.read())
            
        browser.close()
        print("Done rendering architecture pipeline story and post!")

if __name__ == "__main__":
    render_pipeline()
