"""
render_factory_carousel.py
Renders the high-converting 7-slide '12 Open-Source GitHub Repos That Run Your AI Content Factory' carousel
at 1080x1350 JPEG resolution with dark-mode IDE directory aesthetic, vibrant safety orange accents,
and clean typography.
"""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("d:/Autogram/output/carousel-factory")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\Piyush\.gemini\antigravity\brain\a8124c42-154b-496f-9b68-ff045251762a\factory_carousel")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1080
HEIGHT = 1350

SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700;800&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
}

:root {
  --bg-dark: #090D16;
  --bg-card: #0F1626;
  --bg-card-inner: #141E34;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-card: rgba(255, 255, 255, 0.12);
  --orange: #FF5500;
  --orange-light: #FF7733;
  --orange-glow: rgba(255, 85, 0, 0.25);
  --orange-soft: rgba(255, 85, 0, 0.12);
  --text-main: #F8FAFC;
  --text-dim: #94A3B8;
  --text-muted: #64748B;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

body {
  width: 1080px;
  height: 1350px;
  background-color: var(--bg-dark);
  background-image: 
    radial-gradient(circle at 10% 10%, rgba(255, 85, 0, 0.08) 0%, transparent 40%),
    radial-gradient(circle at 90% 90%, rgba(30, 58, 138, 0.12) 0%, transparent 45%),
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
  color: var(--text-main);
  font-family: var(--font-sans);
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 60px 70px;
}

/* Header */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 24px;
}

.brand-badge {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-pill {
  background: var(--orange);
  color: #000;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  padding: 6px 14px;
  border-radius: 6px;
}

.brand-text {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--text-dim);
  letter-spacing: 1.5px;
}

.slide-counter {
  font-family: var(--font-mono);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.04);
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid var(--border-subtle);
}

.slide-counter span {
  color: var(--orange);
}

/* Footer */
.footer-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  border-top: 1px solid var(--border-subtle);
  padding-top: 24px;
}

.footer-left {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--text-muted);
  letter-spacing: 1px;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--orange-soft);
  border: 1px solid rgba(255, 85, 0, 0.3);
  padding: 8px 18px;
  border-radius: 20px;
  color: var(--orange-light);
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-mono);
}

.footer-right svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

/* Typography elements */
.badge-category {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--orange);
  color: #000;
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 1px;
  text-transform: uppercase;
  padding: 6px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.title-large {
  font-size: 52px;
  font-weight: 900;
  line-height: 1.15;
  letter-spacing: -1.5px;
  color: #FFFFFF;
  margin-bottom: 14px;
}

.title-large span {
  color: var(--orange);
  background: linear-gradient(135deg, #FF7733 0%, #FF4400 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtext-clean {
  font-size: 22px;
  color: var(--text-dim);
  line-height: 1.5;
  margin-bottom: 28px;
}

/* Cards & Grid elements */
.repo-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: 20px;
  padding: 24px 28px;
  margin-bottom: 18px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  overflow: hidden;
}

.repo-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 5px;
  height: 100%;
  background: var(--orange);
}

.repo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.repo-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.repo-icon {
  width: 32px;
  height: 32px;
  background: var(--orange-soft);
  border: 1px solid rgba(255, 85, 0, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--orange);
  font-family: var(--font-mono);
  font-weight: 800;
  font-size: 15px;
}

.repo-name {
  font-size: 26px;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: -0.5px;
}

.repo-badge {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-subtle);
  padding: 4px 12px;
  border-radius: 12px;
  color: var(--text-dim);
}

.repo-url {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--orange-light);
  display: flex;
  align-items: center;
  gap: 6px;
}

.repo-url svg {
  width: 14px;
  height: 14px;
  fill: currentColor;
}

.repo-desc {
  font-size: 18px;
  color: var(--text-dim);
  line-height: 1.45;
}

.repo-metric-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card-inner);
  border: 1px solid var(--border-subtle);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #E2E8F0;
  margin-top: 4px;
}

.repo-metric-pill strong {
  color: var(--orange);
  font-family: var(--font-mono);
}
"""

SLIDES_DATA = [
    # Slide 1: Cover / Master Blueprint
    {
        "filename": "slide_01.jpg",
        "html": f"""
<!DOCTYPE html>
<html>
<head><style>{SHARED_CSS}
.cover-layout {{
  display: flex;
  gap: 36px;
  height: 940px;
}}
.sidebar {{
  width: 320px;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.explorer-header {{
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.tree-node {{
  font-family: var(--font-mono);
  font-size: 15px;
  margin-bottom: 12px;
}}
.folder-name {{
  color: var(--orange-light);
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}}
.file-list {{
  margin-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.file-item {{
  color: var(--text-dim);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}}
.file-item span {{
  color: #10B981;
}}
.main-stage {{
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.prompt-card {{
  background: linear-gradient(135deg, rgba(255, 85, 0, 0.15) 0%, rgba(15, 22, 38, 0.8) 100%);
  border: 1px solid rgba(255, 85, 0, 0.35);
  border-radius: 16px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}}
.prompt-tag {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 800;
  color: var(--orange);
  letter-spacing: 1px;
}}
.prompt-instruction {{
  font-size: 16px;
  color: #FFFFFF;
  font-weight: 600;
}}
.repos-preview-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}}
.mini-repo {{
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: 12px;
  padding: 14px 16px;
}}
.mini-repo-tag {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--orange);
  font-weight: 700;
  text-transform: uppercase;
}}
.mini-repo-name {{
  font-size: 16px;
  font-weight: 800;
  color: #FFF;
  margin: 4px 0 2px 0;
}}
.mini-repo-desc {{
  font-size: 12px;
  color: var(--text-dim);
}}
.cta-banner {{
  background: #FFFFFF;
  border-radius: 16px;
  padding: 22px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
}}
.cta-banner-text {{
  color: #090D16;
  font-size: 20px;
  font-weight: 900;
  letter-spacing: -0.5px;
}}
.cta-pill {{
  background: var(--orange);
  color: #000;
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 900;
  padding: 8px 18px;
  border-radius: 8px;
  text-transform: uppercase;
}}
</style></head>
<body>
  <div class="header-bar">
    <div class="brand-badge">
      <span class="brand-pill">Cheat Sheet</span>
      <span class="brand-text">OPEN-SOURCE STACK</span>
    </div>
    <div class="slide-counter"><span>01</span> / 07</div>
  </div>

  <div class="cover-layout">
    <div class="sidebar">
      <div>
        <div class="explorer-header">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>
          EXPLORER /factory
        </div>
        
        <div class="tree-node">
          <div class="folder-name">📁 /research</div>
          <div class="file-list">
            <div class="file-item"><span>✓</span> social-research</div>
            <div class="file-item"><span>✓</span> deep-research</div>
          </div>
        </div>

        <div class="tree-node">
          <div class="folder-name">📁 /create</div>
          <div class="file-list">
            <div class="file-item"><span>✓</span> hyperframes</div>
            <div class="file-item"><span>✓</span> opencreator</div>
            <div class="file-item"><span>✓</span> flux2</div>
            <div class="file-item"><span>✓</span> voicestudio</div>
            <div class="file-item"><span>✓</span> ace-step</div>
            <div class="file-item"><span>✓</span> podcastfy</div>
          </div>
        </div>

        <div class="tree-node">
          <div class="folder-name">📁 /edit</div>
          <div class="file-list">
            <div class="file-item"><span>✓</span> openmontage</div>
            <div class="file-item"><span>✓</span> short-video-factory</div>
            <div class="file-item"><span>✓</span> yt-shorts</div>
          </div>
        </div>

        <div class="tree-node">
          <div class="folder-name">📁 /publish</div>
          <div class="file-list">
            <div class="file-item"><span>✓</span> social-media-agent</div>
          </div>
        </div>
      </div>

      <div style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 14px;">
        12 REPOS · 100% LOCAL<br>ZERO API SUBSCRIPTIONS
      </div>
    </div>

    <div class="main-stage">
      <div>
        <div class="badge-category">Open-Source AI Studio</div>
        <h1 class="title-large">12 Repos That Run Your <span>AI Content Factory</span></h1>
        <p class="subtext-clean">Stop paying $200/mo for fragmented AI tools. Build, animate, voice clone, and publish autonomously from your terminal.</p>

        <div class="prompt-card">
          <div class="prompt-tag">⚡ SKIP THE SETUP · LET AI DO IT</div>
          <div class="prompt-instruction">Screenshot this carousel &gt; Upload to Claude or ChatGPT &gt; Say "Set up this factory for me".</div>
        </div>

        <div class="repos-preview-grid">
          <div class="mini-repo">
            <div class="mini-repo-tag">Voice Clone</div>
            <div class="mini-repo-name">VoiceStudio</div>
            <div class="mini-repo-desc">Local ElevenLabs clone + dub</div>
          </div>
          <div class="mini-repo">
            <div class="mini-repo-tag">Render</div>
            <div class="mini-repo-name">HyperFrames</div>
            <div class="mini-repo-desc">HTML + GSAP to 60fps MP4</div>
          </div>
          <div class="mini-repo">
            <div class="mini-repo-tag">Research</div>
            <div class="mini-repo-name">Social Research</div>
            <div class="mini-repo-desc">Steal top viral hooks & topics</div>
          </div>
          <div class="mini-repo">
            <div class="mini-repo-tag">Publish</div>
            <div class="mini-repo-name">Social Agent</div>
            <div class="mini-repo-desc">Multi-platform autonomous agent</div>
          </div>
        </div>
      </div>

      <div class="cta-banner">
        <div class="cta-banner-text">Comment "FACTORY" for all direct GitHub links</div>
        <div class="cta-pill">Swipe Next ➔</div>
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="footer-left">@SIGNHIFY.STUDIO · MASTER SYSTEM ARCHITECTURE</div>
    <div class="footer-right">
      <svg viewBox="0 0 24 24"><path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/></svg>
      SWIPE TO STEAL
    </div>
  </div>
</body>
</html>
"""
    },

    # Slide 2: Research
    {
        "filename": "slide_02.jpg",
        "html": f"""
<!DOCTYPE html>
<html>
<head><style>{SHARED_CSS}</style></head>
<body>
  <div class="header-bar">
    <div class="brand-badge">
      <span class="brand-pill">Phase 01</span>
      <span class="brand-text">RESEARCH &amp; TOPIC DISCOVERY</span>
    </div>
    <div class="slide-counter"><span>02</span> / 07</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
    <div class="badge-category">📁 /research · 2 Repos</div>
    <h1 class="title-large">Steal What Already Works <span>Before Writing A Line</span></h1>
    <p class="subtext-clean">90% of content fails because of weak hooks. These two repos scrape viral outliers and generate fact-checked dossiers.</p>

    <!-- Repo 1 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">01</div>
          <div class="repo-name">Social Media Research Skills</div>
        </div>
        <div class="repo-badge">Viral Hook Scraper</div>
      </div>
      <div class="repo-url">
        <svg viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
        github.com/ScrapeCreators/social-media-research-skills
      </div>
      <div class="repo-desc">
        Connects to Apify &amp; Instagram/TikTok/X APIs. Scrapes rival profiles, calculates view-to-follower ratio outliers, and clusters winning hook frameworks into structured JSON.
      </div>
      <div class="repo-metric-pill">
        <strong>Superpower:</strong> Pulls 30 proven viral hooks in under 45 seconds
      </div>
    </div>

    <!-- Repo 2 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">02</div>
          <div class="repo-name">Local Deep Research</div>
        </div>
        <div class="repo-badge">Factual Deep Dossier</div>
      </div>
      <div class="repo-url">
        <svg viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
        github.com/LearningCircuit/local-deep-research
      </div>
      <div class="repo-desc">
        A locally hosted autonomous research agent that crawls high-trust documentation, academic sources, and technical specs to build a comprehensive, zero-hallucination script brief.
      </div>
      <div class="repo-metric-pill">
        <strong>Superpower:</strong> Generates fully cited 10-page research briefs on any technical topic
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="footer-left">AUTOGRAM ENGINE · PHASE 1 OF 4</div>
    <div class="footer-right">SWIPE FOR CREATION ➔</div>
  </div>
</body>
</html>
"""
    },

    # Slide 3: Create Part 1 (Audio & Visuals)
    {
        "filename": "slide_03.jpg",
        "html": f"""
<!DOCTYPE html>
<html>
<head><style>{SHARED_CSS}</style></head>
<body>
  <div class="header-bar">
    <div class="brand-badge">
      <span class="brand-pill">Phase 02A</span>
      <span class="brand-text">AUDIO &amp; VISUAL GENERATION</span>
    </div>
    <div class="slide-counter"><span>03</span> / 07</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
    <div class="badge-category">📁 /create · Part 1</div>
    <h1 class="title-large">Local Voice Cloning &amp; <span>Diffusion Imagery</span></h1>
    <p class="subtext-clean">Replace ElevenLabs ($99/mo) and Midjourney ($60/mo) with local open-source models running directly on your hardware.</p>

    <!-- Repo 3 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">03</div>
          <div class="repo-name">VoiceStudio</div>
        </div>
        <div class="repo-badge">Local ElevenLabs</div>
      </div>
      <div class="repo-url">github.com/debpalash/VoiceStudio</div>
      <div class="repo-desc">
        Self-hosted neural speech synthesis &amp; voice cloning workstation. Feeds on a 30s sample of your voice and outputs broadcast-quality, emotion-modulated speech without subscription limits.
      </div>
      <div class="repo-metric-pill"><strong>Saves:</strong> $99/month on voice API subscriptions</div>
    </div>

    <!-- Repo 4 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">04</div>
          <div class="repo-name">FLUX.2</div>
        </div>
        <div class="repo-badge">4K Diffusion Visuals</div>
      </div>
      <div class="repo-url">github.com/black-forest-labs/flux2</div>
      <div class="repo-desc">
        State-of-the-art open weights image diffusion. Renders pristine typography, hyper-detailed UI mockups, and scroll-stopping post covers from simple text briefs.
      </div>
      <div class="repo-metric-pill"><strong>Saves:</strong> $60/month on Midjourney credits</div>
    </div>

    <!-- Repo 5 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">05</div>
          <div class="repo-name">ACE-Step 1.5</div>
        </div>
        <div class="repo-badge">Original Music Generation</div>
      </div>
      <div class="repo-url">github.com/ace-step/ACE-Step-1.5</div>
      <div class="repo-desc">
        Generates custom, copyright-free background music and lo-fi tech beats tailored to your reel's exact pacing and BPM from a single text prompt.
      </div>
      <div class="repo-metric-pill"><strong>Saves:</strong> $25/month on Epidemic Sound or Suno</div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="footer-left">AUTOGRAM ENGINE · PHASE 2A OF 4</div>
    <div class="footer-right">SWIPE FOR VIDEO CODE ➔</div>
  </div>
</body>
</html>
"""
    },

    # Slide 4: Create Part 2 (Video & Podcasts)
    {
        "filename": "slide_04.jpg",
        "html": f"""
<!DOCTYPE html>
<html>
<head><style>{SHARED_CSS}</style></head>
<body>
  <div class="header-bar">
    <div class="brand-badge">
      <span class="brand-pill">Phase 02B</span>
      <span class="brand-text">CODE-RENDERED VIDEO &amp; PODCASTS</span>
    </div>
    <div class="slide-counter"><span>04</span> / 07</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
    <div class="badge-category">📁 /create · Part 2</div>
    <h1 class="title-large">Programmatic Video: <span>Never Open Premiere Again</span></h1>
    <p class="subtext-clean">Instead of dragging keyframes in CapCut or After Effects, define animations in code and render high-FPS vertical video automatically.</p>

    <!-- Repo 6 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">06</div>
          <div class="repo-name">HyperFrames</div>
        </div>
        <div class="repo-badge">HTML/CSS to Video</div>
      </div>
      <div class="repo-url">github.com/heygen-com/hyperframes</div>
      <div class="repo-desc">
        HeyGen's open-source framework. Renders responsive HTML/CSS/Tailwind and GSAP timelines directly into 60fps vertical reels via headless Chromium &amp; FFmpeg.
      </div>
      <div class="repo-metric-pill"><strong>Superpower:</strong> 100% deterministic pixel-perfect video renders</div>
    </div>

    <!-- Repo 7 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">07</div>
          <div class="repo-name">OpenCreator</div>
        </div>
        <div class="repo-badge">End-to-End Orchestrator</div>
      </div>
      <div class="repo-url">github.com/krillinai/OpenCreator</div>
      <div class="repo-desc">
        Unified agentic pipeline that links scriptwriting LLMs, image generation nodes, and voice synthesis into a single terminal command.
      </div>
      <div class="repo-metric-pill"><strong>Superpower:</strong> One prompt produces full scripts + assets</div>
    </div>

    <!-- Repo 8 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">08</div>
          <div class="repo-name">Podcastfy</div>
        </div>
        <div class="repo-badge">Doc to 2-Host Podcast</div>
      </div>
      <div class="repo-url">github.com/souzatharsis/podcastfy</div>
      <div class="repo-desc">
        Converts any long-form blog post, markdown doc, or PDF into an engaging 2-speaker conversational audio podcast ready for Spotify and YouTube.
      </div>
      <div class="repo-metric-pill"><strong>Superpower:</strong> NotebookLM audio overviews, fully open-source</div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="footer-left">AUTOGRAM ENGINE · PHASE 2B OF 4</div>
    <div class="footer-right">SWIPE FOR AUTO-EDITING ➔</div>
  </div>
</body>
</html>
"""
    },

    # Slide 5: Edit
    {
        "filename": "slide_05.jpg",
        "html": f"""
<!DOCTYPE html>
<html>
<head><style>{SHARED_CSS}</style></head>
<body>
  <div class="header-bar">
    <div class="brand-badge">
      <span class="brand-pill">Phase 03</span>
      <span class="brand-text">POST-PRODUCTION &amp; CUTTING</span>
    </div>
    <div class="slide-counter"><span>05</span> / 07</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
    <div class="badge-category">📁 /edit · 3 Repos</div>
    <h1 class="title-large">Auto-Cut, Karaoke Subs &amp; <span>Viral Repurposing</span></h1>
    <p class="subtext-clean">Turn 1 long-form video into 5 viral vertical clips with word-level karaoke subtitles and beat-synced cuts.</p>

    <!-- Repo 9 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">09</div>
          <div class="repo-name">OpenMontage</div>
        </div>
        <div class="repo-badge">Prompt-to-Cut AI Studio</div>
      </div>
      <div class="repo-url">github.com/calesthic/OpenMontage</div>
      <div class="repo-desc">
        An autonomous AI video editor. Takes raw video assets and an editorial prompt, finds climactic moments, trims dead silence, and outputs finished reels.
      </div>
      <div class="repo-metric-pill"><strong>Superpower:</strong> Cuts 1 hour of raw footage in 3 minutes</div>
    </div>

    <!-- Repo 10 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">10</div>
          <div class="repo-name">Short Video Factory</div>
        </div>
        <div class="repo-badge">Batch Subtitled Shorts</div>
      </div>
      <div class="repo-url">github.com/YTLS-LTN/short-video-factory</div>
      <div class="repo-desc">
        Batch generates 9:16 vertical shorts from topic keywords. Auto-transcribes with Whisper, burns dynamic word-by-word highlighted captions, and overlays B-roll.
      </div>
      <div class="repo-metric-pill"><strong>Superpower:</strong> Generates 10 reels in a single batch script</div>
    </div>

    <!-- Repo 11 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">11</div>
          <div class="repo-name">AI-YouTube-Shorts-Generator</div>
        </div>
        <div class="repo-badge">Long-to-Short Repurposer</div>
      </div>
      <div class="repo-url">github.com/Anil-matcha/AI-YouTube-Shorts-Generator</div>
      <div class="repo-desc">
        Downloads any long YouTube video, extracts the transcript, detects the highest retention spikes, re-frames to 9:16 portrait, and burns auto-captions.
      </div>
      <div class="repo-metric-pill"><strong>Superpower:</strong> Opus Clip features with 0 monthly cost</div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="footer-left">AUTOGRAM ENGINE · PHASE 3 OF 4</div>
    <div class="footer-right">SWIPE FOR AUTONOMOUS PUBLISHING ➔</div>
  </div>
</body>
</html>
"""
    },

    # Slide 6: Publish & Master Architecture
    {
        "filename": "slide_06.jpg",
        "html": f"""
<!DOCTYPE html>
<html>
<head><style>{SHARED_CSS}
.blueprint-box {{
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: 20px;
  padding: 24px;
  margin-top: 18px;
}}
.pipeline-flow {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 16px 0;
}}
.flow-step {{
  flex: 1;
  background: var(--bg-card-inner);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 16px 12px;
  text-align: center;
}}
.flow-step-num {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--orange);
  font-weight: 800;
  text-transform: uppercase;
  margin-bottom: 4px;
}}
.flow-step-name {{
  font-size: 15px;
  font-weight: 800;
  color: #FFF;
}}
.flow-arrow {{
  color: var(--orange);
  font-size: 20px;
  font-weight: 900;
}}
</style></head>
<body>
  <div class="header-bar">
    <div class="brand-badge">
      <span class="brand-pill">Phase 04</span>
      <span class="brand-text">DISTRIBUTION &amp; SCHEDULING</span>
    </div>
    <div class="slide-counter"><span>06</span> / 07</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
    <div class="badge-category">📁 /publish · 1 Repo + Full Loop</div>
    <h1 class="title-large">Autonomous Publishing: <span>Post Across All Networks</span></h1>
    <p class="subtext-clean">Once your content is rendered, an autonomous agent writes cross-platform captions and schedules posts without manual uploading.</p>

    <!-- Repo 12 -->
    <div class="repo-card">
      <div class="repo-header">
        <div class="repo-title-row">
          <div class="repo-icon">12</div>
          <div class="repo-name">Social Media Agent</div>
        </div>
        <div class="repo-badge">Multi-Platform Agent</div>
      </div>
      <div class="repo-url">github.com/langchain-ai/social-media-agent</div>
      <div class="repo-desc">
        Built by LangChain. Takes a single video deliverable or link, extracts the core message, and autonomously drafts &amp; schedules optimized posts for X (threads), LinkedIn (carousels), and YouTube Shorts.
      </div>
      <div class="repo-metric-pill"><strong>Superpower:</strong> 1 video asset becomes 4 distinct platform posts</div>
    </div>

    <!-- Master Architecture Blueprint -->
    <div class="blueprint-box">
      <div style="font-family: var(--font-mono); font-size: 13px; font-weight: 800; color: var(--orange); letter-spacing: 1px;">
        ⚙️ HOW THE 12 REPOS CONNECT END-TO-END
      </div>
      <div class="pipeline-flow">
        <div class="flow-step">
          <div class="flow-step-num">Research</div>
          <div class="flow-step-name">Social Skills</div>
        </div>
        <div class="flow-arrow">➔</div>
        <div class="flow-step">
          <div class="flow-step-num">Voice &amp; Art</div>
          <div class="flow-step-name">VoiceStudio + FLUX</div>
        </div>
        <div class="flow-arrow">➔</div>
        <div class="flow-step">
          <div class="flow-step-num">Render</div>
          <div class="flow-step-name">HyperFrames</div>
        </div>
        <div class="flow-arrow">➔</div>
        <div class="flow-step">
          <div class="flow-step-num">Publish</div>
          <div class="flow-step-name">Social Agent</div>
        </div>
      </div>
      <div style="font-size: 15px; color: var(--text-dim); line-height: 1.4;">
        Result: A 100% autonomous, zero-touch video pipeline producing 1 reel + 1 carousel daily on complete autopilot.
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="footer-left">AUTOGRAM ENGINE · COMPLETE LOOP</div>
    <div class="footer-right">SWIPE FOR DIRECT ACCESS ➔</div>
  </div>
</body>
</html>
"""
    },

    # Slide 7: Mega CTA
    {
        "filename": "slide_07.jpg",
        "html": f"""
<!DOCTYPE html>
<html>
<head><style>{SHARED_CSS}
.cta-mega-card {{
  background: var(--bg-card);
  border: 2px solid rgba(255, 85, 0, 0.4);
  border-radius: 28px;
  padding: 44px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(255, 85, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 22px;
}}
.cta-keyword-box {{
  background: #FFFFFF;
  border-radius: 18px;
  padding: 16px 44px;
  box-shadow: 0 10px 30px rgba(255, 85, 0, 0.35);
}}
.cta-keyword {{
  font-family: var(--font-mono);
  font-size: 56px;
  font-weight: 900;
  color: #090D16;
  letter-spacing: 4px;
}}
.deliverables-stack {{
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 10px 0;
}}
.deliv-item {{
  background: var(--bg-card-inner);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
}}
.deliv-num {{
  width: 36px;
  height: 36px;
  background: var(--orange-soft);
  border: 1px solid rgba(255, 85, 0, 0.3);
  border-radius: 8px;
  color: var(--orange);
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.deliv-text {{
  font-size: 17px;
  color: #FFFFFF;
  font-weight: 600;
}}
.deliv-text span {{
  color: var(--text-dim);
  font-size: 14px;
  display: block;
  font-weight: 400;
}}
.save-reminder {{
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  padding: 12px 24px;
  border-radius: 30px;
  color: var(--text-dim);
  font-size: 15px;
  font-weight: 600;
}}
</style></head>
<body>
  <div class="header-bar">
    <div class="brand-badge">
      <span class="brand-pill">Instant Access</span>
      <span class="brand-text">FREE DEVELOPER BUNDLE</span>
    </div>
    <div class="slide-counter"><span>07</span> / 07</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
    <div class="cta-mega-card">
      <div class="badge-category" style="margin-bottom: 0;">Automated DM Delivery</div>
      
      <h1 style="font-size: 46px; font-weight: 900; line-height: 1.15; color: #FFF;">
        Comment <span style="color: var(--orange);">"FACTORY"</span> Below
      </h1>
      
      <p style="font-size: 20px; color: var(--text-dim); max-width: 700px;">
        I'll instantly DM you the full setup bundle directly to your inbox:
      </p>

      <div class="cta-keyword-box">
        <div class="cta-keyword">"FACTORY"</div>
      </div>

      <div class="deliverables-stack">
        <div class="deliv-item">
          <div class="deliv-num">01</div>
          <div class="deliv-text">
            All 12 Direct GitHub Links
            <span>Clean repository list with installation commands for macOS &amp; Windows</span>
          </div>
        </div>

        <div class="deliv-item">
          <div class="deliv-num">02</div>
          <div class="deliv-text">
            The 1-Click Claude / ChatGPT Setup Prompt
            <span>Drop this into your AI client to configure the entire stack in under 5 minutes</span>
          </div>
        </div>

        <div class="deliv-item">
          <div class="deliv-num">03</div>
          <div class="deliv-text">
            Master Python Pipeline Orchestrator
            <span>The bridge script connecting research, voiceover, and video rendering</span>
          </div>
        </div>
      </div>

      <div class="save-reminder">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>
        Save this post for later reference · Share with a creator friend
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="footer-left">@SIGNHIFY.STUDIO · COMMENT "FACTORY" BELOW</div>
    <div class="footer-right">DONE · CHECK DMS 🚀</div>
  </div>
</body>
</html>
"""
    }
]

def render_all():
    print(f"Starting Playwright renderer for 7-slide carousel...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1.0
        )
        page = context.new_page()

        rendered_files = []
        for i, slide in enumerate(SLIDES_DATA, 1):
            out_file = OUTPUT_DIR / slide["filename"]
            artifact_file = ARTIFACT_DIR / slide["filename"]

            print(f"Rendering slide {i}/7: {slide['filename']}...")
            page.set_content(slide["html"], wait_until="networkidle")
            # Wait a brief moment for fonts to stabilize
            page.wait_for_timeout(400)

            page.screenshot(
                path=str(out_file),
                type="jpeg",
                quality=96,
                clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT}
            )

            # Copy to brain artifact directory as well
            artifact_file.write_bytes(out_file.read_bytes())

            rendered_files.append(str(out_file))
            print(f"✓ Saved {out_file} ({out_file.stat().st_size // 1024} KB)")

        browser.close()

    print(f"\nAll 7 slides successfully rendered to {OUTPUT_DIR} and {ARTIFACT_DIR}!")
    return rendered_files

if __name__ == "__main__":
    render_all()

