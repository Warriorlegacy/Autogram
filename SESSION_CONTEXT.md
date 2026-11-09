# 🛰️ AUTOGRAM — MASTER SESSION CONTEXT & AGENT HANDOVER (HERMES AGENT READY)

> **Document Version:** 3.0  
> **Timestamp:** 2026-11-08  
> **Target Audience:** Hermes Agent / Autonomous AI Coding Agents / Claude Code  
> **Primary Workspace:** `D:\Autogram`  
> **Host Operating System:** Windows 11 (64-bit)  
> **Virtual Environment:** `D:\Autogram\.venv\Scripts\python.exe` (Python 3.12 / 3.14)

---

## 1. Executive Summary & Project Purpose

**Autogram** is a production-grade, zero-touch Instagram content publishing engine and monetization ecosystem built for **Signhify Studio** (`signhify.dpdns.org`, founded by Piyush Raj Singh).

It performs end-to-end autonomous media creation across three core content formats:
1. **Dark-Mode IDE Directory Carousels (1080×1350):** 7–10 slide high-value developer tool cheat sheets rendered via Playwright.
2. **Viral Vertical Skits & Contrarian Tech Reels (1080×1920 @ 60fps):** Code-rendered Remotion videos featuring Studio Adam / Kokoro TTS voiceovers, faster-whisper word-level lip sync, dynamic animations, and safe-zone compliance.
3. **Automated System Architecture Stories & Posts (1080×1920 & 1080×1350):** High-density infrastructure flowcharts that trigger high-ticket inbound agency inquiries.
4. **Follow-Gated ManyChat DM Automation:** Automated keyword listening that verifies user follow status on `@signhify.studio` before unlocking repositories, qualification branching, and booking discovery calls.

---

## 2. Repository Layout & Critical Directories

```
d:\Autogram/
├── orchestrator.py                 # CLI Master Pipeline & Scheduled Daemon (--schedule, --dry-run, --run-all)
├── dashboard_api.py                # Flask Web Dashboard + background scheduler daemon (Port 5050)
├── autopilot.db                    # SQLite primary database (runs, metrics, publications)
├── requirements.txt                # Python dependencies (no setup.py / pyproject.toml)
├── .env                            # Environment variables & API keys (Owner bypass enabled)
│
├── src/                            # Engine Core
│   ├── auth/licensing.py           # HMAC-SHA256 license gate (AUTOGRAM_OWNER_KEY bypass)
│   ├── research/fetcher.py         # Real-time RSS, HackerNews Algolia, GitHub trending ingestion
│   ├── research/scorer.py          # 6-pillar rotation, viral scoring, anti-repetition memory
│   ├── content/generator.py        # Multi-LLM fallback chain (Gemini, Copilot, OpenRouter, OpenAI)
│   ├── content/quality_gate.py     # Score 0–100, banned phrase enforcement (data/brand.json)
│   ├── content/script_writer.py    # Captions, hashtags, Reel scripts
│   ├── storage/uploader.py         # S3 / Cloudflare R2 / Free CDN cascade
│   ├── instagram/publisher.py      # Meta Graph API container flow (Carousel, Reel, Story)
│   └── analytics/optimizer.py      # Content memory ledger & performance optimizer
│
├── renderer/                       # Playwright Carousel Renderer (1080x1350)
│   ├── render.py                   # Playwright headless chromium automation
│   └── css/design-system.css       # 850+ lines master dark-mode stylesheet
│
├── docs/reel-studio-kit/           # Remotion React Engine (1080x1920 @ 60fps Reels)
│   ├── package.json                # Remotion 4.0.538 dependencies
│   ├── src/
│   │   ├── brand.ts                # Brand colors (#0A0D12, #FF5500, #00E599), fonts, handle
│   │   ├── layout.ts               # SAFE_BOX, CAPTION_BOTTOM, SAFE.top (250px), SAFE.bottom (420px)
│   │   ├── timing.ts               # Timing helper (t.at, t.atText, t.duration)
│   │   └── reels/                  # Reel compositions
│   │       ├── registry.ts         # Central registry of all active reels
│   │       ├── deleted-production/ # Day 01: "Claude. I Deleted Production" (COMPLETED)
│   │       └── claude-vs-premiere/ # Day 02: "Claude > Premiere Pro?" (COMPLETED)
│   ├── public/reels/               # Public assets (vo.wav, captions.words.json, mouth.json)
│   └── out/                        # Rendered MP4 deliverables & contact sheets
│
├── video_studio/                   # HyperFrames CLI Integration (HeyGen Apache-2.0 wrapper)
│   ├── cli.py                      # python -m video_studio.cli (build, render, qa, package)
│   ├── briefs/                     # Authoring contracts (<slug>.json)
│   └── templates/                  # Jinja2 HTML templates
│
├── data/                           # Runtime State Files
│   ├── brand.json                  # Brand voice, pillars, handle, avoid-phrases (Fail-Closed)
│   ├── schedule.json               # Active publishing queue & daily slots
│   ├── content-memory.json         # Anti-repetition historical ledger
│   └── dm_automation_state.json    # Scanned comments & dispatched DMs
│
└── output/                         # Local Render Output Artifacts
    ├── carousel-factory/           # 7-Slide Content Factory Carousel (1080x1350 JPEGs)
    └── architecture-pipeline/      # System Architecture Story & Post JPEGs
```

---

## 3. Critical Runtime Quirks & Rules (Hermes Agent Must Know)

1. **License Gate Bypass (Mandatory):**
   * All execution is blocked by `src/auth/licensing.py`.
   * **Bypass:** Ensure `AUTOGRAM_OWNER_KEY=autogram_owner_vip_2026` is present in `.env`. The system runs with unlimited free owner privileges.
2. **Fail-Closed Banned Phrase Guard:**
   * `data/brand.json` defines forbidden words under `avoid` (e.g. *robust, seamless, game-changer, dive in, leverage*).
   * Any script or brief containing these phrases will exit with code `3` or fail the quality gate. Never delete or bypass this check.
3. **Remotion Windows Low-Memory Flags (CRITICAL):**
   * Standard Remotion renders will crash with `malloc of size 7281920 failed` on Windows due to x264 lookahead buffers across multiple CPU threads.
   * **Always use these exact flags:**
     ```powershell
     npx remotion render <id> out/<id>.mp4 --disallow-parallel-encoding --disable-shared-memory-capture --x264-preset=veryfast --crf=20
     ```
4. **ONNX & Whisper Process Isolation:**
   * Running Kokoro ONNX TTS and `faster-whisper` in the same Python process triggers `mkl_malloc` heap allocation failures. Always run them in separate CLI subprocess calls.
5. **Instagram Safe-Zone Boundaries:**
   * Canvas: `1080 × 1920`.
   * Top Safe Zone: Keep top `250px` clear of essential text (Instagram header overlay).
   * Bottom Safe Zone: Keep bottom `420px` clear of essential text (Captions, audio tag, UI buttons).
   * Use `tools/check.mjs <id>` to verify safe-zone compliance.

---

## 4. Current Content Pipeline & Production Status

| Asset ID | Format | Topic / Title | Status | Trigger Word | File Deliverable |
|---|---|---|---|---|---|
| **CAROUSEL-01** | 7-Slide Carousel | **12 Open-Source GitHub Repos That Run Your Content Factory** | ✅ **RENDERED & QUEUED** | `FACTORY` | `d:\Autogram\output\carousel-factory\slide_01.jpg` – `07.jpg` |
| **REEL-01** | 9:16 Reel (23.14s) | **Claude. I Deleted Production (Dev Panic Skit)** | ✅ **RENDERED & QUEUED** | `RESTORE` | `d:\Autogram\docs\reel-studio-kit\out\deleted-production.mp4` |
| **REEL-02** | 9:16 Reel (29.82s) | **Claude > Premiere Pro? (0% Premiere, 100% Code Motion)** | ✅ **RENDERED & QUEUED** | `HYPER` | `d:\Autogram\docs\reel-studio-kit\out\claude-vs-premiere.mp4` |
| **STORY-01** | 9:16 Story Graphic | **How We Fully Automate It (Autonomous Architecture Pipeline)** | ✅ **RENDERED & QUEUED** | `PIPELINE` | `d:\Autogram\output\architecture-pipeline\story_automation_pipeline_1080x1920.jpg` |
| **POST-01** | 4:5 Feed Graphic | **How We Fully Automate It (Feed Post Version)** | ✅ **RENDERED** | `SYSTEM` | `d:\Autogram\output\architecture-pipeline\post_automation_pipeline_1080x1350.jpg` |
| **REEL-03** | 9:16 Reel (~28s) | **I Replaced A $5,000/Mo Video Editor With 1 Open-Source Script** | 🟡 **READY FOR PRODUCTION** | `CUT` | Target: `src/reels/replaced-editor/Reel.tsx` (OpenMontage showcase) |

---

## 5. ManyChat Follow-Gated Automations

All four active campaigns have production-ready ManyChat JSON flow definitions in the workspace root:

1. `manychat_flow_restore.json`:
   * **Trigger:** `RESTORE`
   * **Mechanism:** Strict Follower Gate (`user.is_follower == true`). Unfollowers must click `[I'm Following! ✅]` to verify before receiving the terminal rollback script.
   * **Qualification:** 120s delay → Team DevOps ($15-min Cal demo) vs Solo Dev.
2. `manychat_flow_factory.json`:
   * **Trigger:** `FACTORY`
   * **Mechanism:** Delivers the 12 Open-Source Repositories Cheat Sheet + Claude Setup Prompt.
3. `manychat_flow_hyper.json`:
   * **Trigger:** `HYPER`
   * **Mechanism:** Delivers HyperFrames repository link + Claude GSAP motion prompt.
4. `manychat_flow_pipeline.json`:
   * **Trigger:** `PIPELINE` or `SYSTEM`
   * **Mechanism:** Delivers the full Architecture Blueprint PDF + enterprise pipeline audit booking.

---

## 6. How to Run & Control the System (Hermes Action Guide)

### 1. Launch Publisher Daemon (Local Background Terminal)
```powershell
cd D:\Autogram
.\.venv\Scripts\python.exe orchestrator.py --schedule
```

### 2. Run Diagnostics & Health Check
```powershell
cd D:\Autogram
.\.venv\Scripts\python.exe orchestrator.py --test
```

### 3. Render 7-Slide Carousel
```powershell
cd D:\Autogram
.\.venv\Scripts\python.exe render_factory_carousel.py
```

### 4. Render Architecture Infographic Story & Post
```powershell
cd D:\Autogram
.\.venv\Scripts\python.exe render_architecture_system.py
```

### 5. Remotion Reel Development Workflow
```powershell
cd D:\Autogram\docs\reel-studio-kit

# 1. Typecheck compositions
npm run typecheck

# 2. Render MP4 with low-memory safety flags
npx remotion render claude-vs-premiere out/claude-vs-premiere.mp4 --disallow-parallel-encoding --disable-shared-memory-capture --x264-preset=veryfast --crf=20

# 3. Verify safe-zones & build contact sheet
npm run check -- claude-vs-premiere
```

---

## 7. Next Up for Hermes Agent: Day 03 Reel Production Plan

* **Topic:** *"I Replaced A $5,000/Mo Video Editor With 1 Open-Source Script"*
* **Key Open-Source Repo:** `github.com/calesthio/OpenMontage`
* **Hook:** *"A video editor wanted to charge my agency five thousand dollars a month to cut long podcasts into shorts. Instead, I ran one open-source Python script."*
* **The Stack:** Whisper diarization + silence removal + auto face-tracking + kinetic captions in 90 seconds.
* **ManyChat Trigger:** `CUT`
