# Signhify Studio — Video Production Engine
## Master Prompt Pack (PROMPT 00 → PROMPT 19)

---

## How to use this pack

This is a **master prompt library**. Each prompt below is a complete, copy-paste-ready
instruction block intended for a competent coding agent (Claude Code, OpenCode, Codex, or
equivalent) that has **never seen this project**.

Every prompt is self-contained: it names the repository, the real toolchain, the real file
paths, and the exact acceptance criteria. Nothing here is aspirational — every command has
been verified on this machine.

### The workflow

1. Read the header + the order table below.
2. Open the prompt by title (e.g. "PROMPT 07 — AI Content Research and Script Generation").
3. Copy **only** the content inside the fenced block under *Exact copy-paste prompt text*.
4. Paste it into an agent whose working directory is `D:\Autogram`.
5. Verify against the *Acceptance criteria* section — the agent must prove it, not assert it.
6. Move to the next prompt.

**Do not batch prompts.** Prompts 00–06 must each complete and be verified before 07 starts.
A later prompt built on unverified foundations produces confident, wrong output.

### Tag legend

| Tag | Meaning |
|---|---|
| `[AUDIT]` | Read-only investigation. Produces a report. Modifies nothing. |
| `[RESEARCH]` | Gathers external or document-grounded facts. Produces a written artifact. May require network. |
| `[PLANNING]` | Produces a specification or design. Writes docs/JSON, no running code. |
| `[CODE-CHANGING]` | Writes or modifies Python, HTML, CSS, JS. Runs commands. |
| `[RENDERS VIDEO]` | Produces an actual `.mp4` on disk. Must verify with ffprobe. |
| `[PUBLISHES CONTENT]` | Contacts Meta's API. Dry-run by default. Requires owner opt-in. |

### Dependency and execution order

| # | Prompt | Tag | Depends on | Produces | Safe to run in fresh clone? |
|---|---|---|---|---|---|
| 00 | Existing Environment and Repository Audit | `[AUDIT]` | — | `docs/video-studio/ENVIRONMENT_AUDIT.md` | Yes — run first, always |
| 01 | Deep Technical Research | `[RESEARCH]` | 00 | `docs/video-studio/HYPERFRAMES_RESEARCH.md` | Yes, after 00 |
| 02 | Signhify Brand and Content Identity | `[RESEARCH]` | 00 | `video_studio/brand_tokens.json`, `docs/video-studio/BRAND_IDENTITY.md` | Yes, after 00 |
| 03 | System Architecture and Technical Specification | `[PLANNING]` | 00, 01, 02 | `docs/video-studio/ARCHITECTURE.md` | Yes, after 01+02 |
| 04 | OpenCode Agent Configuration | `[CODE-CHANGING]` | 03 | `.opencode/agent/video-studio.md` | Yes, after 03 |
| 05 | HyperFrames Setup and Validation | `[CODE-CHANGING]` | 01 | `docs/video-studio/HYPERFRAMES_SMOKE_TEST.md`, `_smoke/` (deletable) | Yes — proves the toolchain |
| 06 | Premium Visual Design System | `[CODE-CHANGING]` | 02, 05 | `video_studio/templates/composition.html.jinja2`, `video_studio/design/tokens.css` | Yes, after 02 |
| 07 | AI Content Research and Script Generation | `[RESEARCH]` | 02, 06 | `video_studio/prompts/script.md`, `video_studio/briefs/<slug>.json` | Yes, after 06 |
| 08 | Storyboard and Timeline Generation | `[CODE-CHANGING]` | 03, 06, 07 | `video_studio/storyboard.py`, `video_studio/work/<slug>/storyboard.json` | Yes, after 07 |
| 09 | Asset Generation and Management | `[CODE-CHANGING]` | 06, 07 | `video_studio/assets.py`, `video_studio/work/<slug>/asset_manifest.json` | Yes, after 08 |
| 10 | Automated Video Production | `[RENDERS VIDEO]` | 05, 06, 08, 09 | `video_studio/compose.py`, `video_studio/render.py`, `video_studio/output/<slug>/reel.mp4` | Yes, after 09 — **first video** |
| 11 | Narration, Sound Design, Subtitle Sync | `[CODE-CHANGING]` | 10 | `video_studio/audio.py`, `output/<slug>/captions.srt` | Yes, after 10 |
| 12 | Automated Video Quality Assurance | `[AUDIT]` | 10, 11 | `video_studio/qa.py`, `output/<slug>/qa_report.md` | Yes, after 10 |
| 13 | Instagram Reel Packaging | `[PLANNING]` | 02, 11 | `video_studio/publish.py` (package half), `output/<slug>/cover.jpg`, `manifest.json` | Yes, after 11 |
| 14 | Official Instagram Publishing Integration | `[PUBLISHES CONTENT]` | 13 | `video_studio/publish.py` (publish half) | Yes — but **dry-run only** without owner keys |
| 15 | Fully Automated Production Workflow | `[CODE-CHANGING]` | 10, 11, 12, 13 | `video_studio/pipeline.py`, `video_studio/cli.py` | Yes, after 13 |
| 16 | Scheduled Execution and Failure Recovery | `[CODE-CHANGING]` | 15 | `video_studio/scheduler.py`, `video_studio/state.py` | Yes, after 15 |
| 17 | Analytics and Content Improvement | `[RESEARCH]` | 14, 15 | `video_studio/analytics.py`, `data/content-memory.json` update | After 14 has shipped ≥1 real post |
| 18 | New Video Production (operational) | `[RENDERS VIDEO]` | 15 | `video_studio/output/<slug>/` (full set) | Yes — **run this weekly** |
| 19 | End-to-End Production Audit | `[AUDIT]` | all | `docs/video-studio/E2E_AUDIT.md` | Yes — run monthly |

### Global hard rules (already embedded in every prompt below)

These are restated in each prompt so that no prompt can be run out of context.

- **Never fabricate** product capabilities, metrics, testimonials, customer results, or revenue.
- **Never print or commit** API keys or tokens. Placeholders only (`<YOUR_IG_ACCESS_TOKEN>`).
- **Never claim** a video was rendered, a test passed, or a reel was published unless a command
  in the transcript proves it. "Should work" is not verification.
- **Never bypass** Instagram authentication or platform security. No scraping tokens, no
  unofficial APIs, no browser-automation logins.
- **Do not activate paid APIs** without explicit owner authorization.
- **Respect the 16 banned phrases** from `data/brand.json` → `avoid`.
- **Inspect before modifying.** Preserve existing code and existing repo behavior.

---

### Banned phrases (the canonical `avoid` list — 16 entries)

Every prompt that writes copy, script, caption, or on-screen text must enforce this list.
Source of truth: `D:\Autogram\data\brand.json`, key `avoid`.

```
generic hype · fake urgency · unsupported statistics · overused motivational language
keyword stuffing · game-changer · unlock the power of · in today's fast-paced world
dive into · at its core · seamless · robust · revolutionary tool · next-gen AI
ultimate secret · must-have app
```

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 00 — Existing Environment and Repository Audit
# ═════════════════════════════════════════════════════════════════════════════

`[AUDIT]`

## 1. Prompt title
PROMPT 00 — Existing Environment and Repository Audit

## 2. Intended purpose
Establish ground truth about the machine, the installed toolchain, and the repository's
existing conventions **before any code is written**. Every later prompt depends on the
facts this one produces. It is read-only: it must not create, modify, or delete anything
except its own report file.

## 3. When to use it
- First, always, on a fresh clone or a new machine.
- Again whenever the environment changes (Node upgrade, Docker started, GPU added).
- As the pre-flight check before PROMPT 05 or PROMPT 10.

## 4. Required inputs
- Repository at `D:\Autogram` (Windows, x64).
- Shell: PowerShell 7+ (`pwsh`).
- Network access to npm registry (read-only).
- No credentials required. Do not read `.env` values — read only `.env.example`.

## 5. Exact copy-paste prompt text

````
You are auditing an existing repository before building a new video production engine.
Working directory: D:\Autogram
PowerShell 7+ on Windows x64.

OBJECTIVE
Produce a single factual report at docs/video-studio/ENVIRONMENT_AUDIT.md that records the
real state of the machine and repo. No speculation. Every line in the report must be
backed by a command you actually ran and whose output you actually observed.

STEP 1 — MACHINE BASELINE
Run and record exact output (do not round, do not paraphrase):
  node --version
  npm --version
  python --version
  if (Test-Path .venv) { .venv\Scripts\python.exe --version } else { ".venv MISSING" }
  ffmpeg -version   |  Select-Object -First 1
  ffprobe -version  |  Select-Object -First 1
  nproc
  (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
  docker version --format '{{.Server.Version}}'
    -> if this fails, record "Docker installed but NOT running". Do not try to start it.
  nvidia-smi
    -> if this fails, record "No CUDA GPU".
  Get-Command whisper-cli -ErrorAction SilentlyContinue
  Get-Command kokoro  -ErrorAction SilentlyContinue

STEP 2 — PYTHON PACKAGE INVENTORY
  .venv\Scripts\python.exe -m pip list --format=columns
Summarise: which of these are PRESENT vs ABSENT — requests, flask, playwright,
pydantic, pydantic-settings, jinja2, feedparser, pillow, pytest, numpy.
Explicitly state which are ABSENT. Absence is a finding, not a problem to fix here.

STEP 3 — HYPERFRAMES
  npx hyperframes --version
  npx hyperframes --help
Record the installed version and the COMPLETE list of subcommands exactly as printed.
Known-good baseline (installed at repo root, Apache-2.0):
  version 0.8.58; upstream latest 0.8.145.
  subcommands: init, add, capture, catalog, preview, present, publish, render, lint,
  check, validate, beats, inspect, keyframes, snapshot, media-treatment, normalize-audio,
  grade-compare, compare, info, compositions, timeline, docs, benchmark, browser, doctor,
  upgrade, cloud, lambda, cloudrun, skills, transcribe, tts, remove-background, auth,
  feedback, telemetry.
Then run, from D:\Autogram:
  npx hyperframes render --help
  npx hyperframes check --help
  npx hyperframes init --help
CRITICAL: confirm whether `init` accepts `--template` or `--example`.
VERIFIED FACT: the flag is `--example <blank|title-card|video-edit>`. `--template` was
renamed and errors out. Record the flag you actually observed.

STEP 4 — REPO CONVENTIONS
Read and summarise, do not summarise from memory, these files:
  AGENTS.md                 (if present)
  requirements.txt
  .env.example              (KEY NAMES ONLY — never print values, never print real values)
  data/brand.json           (keys: brand_name, handle, website, sign_off, avoid[])
  data/content-memory.json  (structure and record count)
  orchestrator.py           (top 80 lines: entrypoint pattern, license gate)
  dashboard_api.py          (top 60 lines: port, scheduler thread)
  src/auth/licensing.py     (what gates execution)
  .github/workflows/*.yml   (deployment surfaces, cron slots, secrets referenced)
Record:
  - How entrypoints are invoked (no pyproject.toml / setup.py — direct `python <file>.py`).
  - The license gate and the owner-bypass env var name.
  - Whether DRY_RUN defaults to true.
  - Existing directory layout of src/, renderer/, data/, assets/.
  - The exact repo-relative style: no linter, no formatter, no typechecker configured.

STEP 5 — ASSET INVENTORY
  Get-ChildItem assets -Filter "signhify*"          -> expect signhify-logo-vector.png
  Get-ChildItem assets -Filter "ig_signhify*" | Measure-Object   -> expect count 9
  Get-ChildItem assets -Filter "ig_signhify*" | Select-Object -First 1
    -> read dimensions of one carousel image; expect 1080x1350.
Record exact filenames and counts. Do not modify assets.

STEP 6 — GIT STATE
  git status --short
  git log --oneline -10
  git rev-parse --abbrev-ref HEAD
Record: is the worktree dirty? which branch? Is there an existing video_studio/ dir
or docs/video-studio/ work in progress? If video_studio/ already exists, list it fully
and STOP — do not overwrite. Report instead.

STEP 7 — WRITE THE REPORT
Create docs/video-studio/ENVIRONMENT_AUDIT.md with these exact sections:
  ## Machine        — versions table, cores, RAM, GPU, Docker state
  ## Python         — present/absent dependency table
  ## HyperFrames    — version, full subcommand list, render/check/init flag signatures
  ## Repository     — entrypoints, license gate, DRY_RUN default, layout, style
  ## Brand Source   — the exact handle, website, sign_off, and the 16 banned phrases
  ## Assets         — exact filenames + dimensions
  ## Git            — branch, dirty state, recent commits
  ## Blockers       — anything that will stop the build. If none, say "None".
  ## Commands for later prompts — copy-pasteable, verified lines only

RULES
  - Do not install anything. Do not run `npm install`, `pip install`, or `playwright install`.
  - Do not start Docker.
  - Do not read or print the contents of .env (only .env.example, and only key names).
  - If a command fails, record the exact error text under Blockers. Do not hide failures.
  - Do not guess. If you did not run it, you do not know it.

ACCEPTANCE
  - docs/video-studio/ENVIRONMENT_AUDIT.md exists.
  - It contains all 8 sections above.
  - Every factual claim is traceable to a command you ran.
  - No file in the repo other than that report was created or modified.
````

## 6. Expected output files
- `docs/video-studio/ENVIRONMENT_AUDIT.md` — the sole artifact.

## 7. Execution requirements
- Read-only. Single working directory `D:\Autogram`.
- No package installation, no service startup, no `.env` reads.
- Every fact must come from observed command output.

## 8. Dependencies on earlier prompts
None. This is the entry point.

## 9. Acceptance criteria
- Report contains: Machine, Python, HyperFrames, Repository, Brand Source, Assets, Git,
  Blockers, Commands for later prompts.
- The confirmed `hyperframes init` flag is recorded (`--example`, not `--template`).
- The 16 banned phrases are reproduced verbatim from `data/brand.json`.
- `git status --short` output shows only the new untracked report.

## 10. Verification instructions
```powershell
Test-Path docs\video-studio\ENVIRONMENT_AUDIT.md
git status --short
# Confirm no other tracked file changed:
git diff --stat
```
Re-run any single command from the report's final section yourself. If a line does not
reproduce, the report is wrong — fix it before proceeding.

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `npx hyperframes --help` is slow or errors | First run resolves the package | Wait; re-run. If it still fails, `npm ls hyperframes` in `D:\Autogram` and record the failure. |
| `docker version` hangs | Docker Desktop not running | Cancel with Ctrl+C. Record "installed but NOT running". Do not start it. |
| `.venv` missing | Repo never provisioned | Record as a Blocker. PROMPT 01+ still work; PROMPT 08+ need the venv. |
| `ffmpeg` not on PATH | No FFmpeg | Record as a Blocker. PROMPT 12 (QA) and 13 will fail until fixed. |
| `git status` shows many modified files | Dirty worktree from prior work | Do not reset. Record it under Git and ask the owner before touching anything. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 01 — Deep Technical Research
# ═════════════════════════════════════════════════════════════════════════════

`[RESEARCH]`

## 1. Prompt title
PROMPT 01 — Deep Technical Research

## 2. Intended purpose
Build an authoritative, verified reference for the **HyperFrames composition contract** —
the exact HTML attribute set, GSAP animation rules, variable system, and CLI semantics that
the entire video engine will be generated from. This document is the single source of truth
downstream; prompts 05–11 cite it instead of re-deriving it.

## 3. When to use it
- Immediately after PROMPT 00 reports `hyperframes 0.8.58` installed.
- Again after any HyperFrames version upgrade (0.8.58 → 0.8.145 upstream is a large delta).
- Before PROMPT 06 (design system) and PROMPT 08 (storyboard), both of which emit raw
  composition HTML.

## 4. Required inputs
- `docs/video-studio/ENVIRONMENT_AUDIT.md` from PROMPT 00.
- `npx hyperframes docs <topic>` (offline, bundled docs).
- Network access for `https://hyperframes.dev` documentation if reachable.
- The supplied verified-contract facts in the prompt block below (these are the baseline
  you are confirming, not inventing).

## 5. Exact copy-paste prompt text

````
You are producing the authoritative technical reference for a video engine that will emit
HyperFrames compositions programmatically.
Working directory: D:\Autogram
Toolchain: hyperframes 0.8.58 via `npx hyperframes` (Apache-2.0). Node v22.23.1.

TASK
Write docs/video-studio/HYPERFRAMES_RESEARCH.md. It must be precise enough that an agent
who has never seen HyperFrames can emit a valid 1080x1920 Reel composition with correct
animation and correct timing on the first attempt.

PRIMARY SOURCES — use these, in order:
  npx hyperframes docs            (list available topics)
  npx hyperframes docs composition
  npx hyperframes docs timing
  npx hyperframes docs animation
  npx hyperframes docs variables
  npx hyperframes docs audio
  npx hyperframes docs cli
  npx hyperframes doctor
  npx hyperframes info
  npx hyperframes render --help
  npx hyperframes check --help
  npx hyperframes snapshot --help
If bundled docs contradict the VERIFIED FACTS below, the VERIFIED FACTS win (they were
confirmed on this machine by an actual render). Record the contradiction explicitly in a
"Discrepancies" section — do not silently pick one.

VERIFIED FACTS — the composition contract (confirmed by smoke render):
STRUCTURE
  - Root element MUST carry data-composition-id, data-width, data-height,
    data-start, data-duration.
  - data-composition-id values are used as keys into window.__timelines — they must match
    the id used at registration.
  - Nested sub-compositions: data-composition-src="./child.html" plus data-start and
    data-duration.
  - Add class="clip" to every timed element.
TIMING
  - data-start and data-duration are in SECONDS (not frames, not ms).
  - data-media-start trims media in-window; use it for video/audio trim.
  - data-volume: 1 = 0 dB. Max useful value ~3.98 (+12 dB).
  - data-has-audio marks clips that contribute to the audio mix.
TRACKS — IMPORTANT CORRECTION
  - data-track-index is DISPLAY-ONLY for the Studio timeline UI.
  - It does NOT control paint order and does NOT prevent overlap between clips.
  - Overlap and stacking are controlled by CSS z-index only.
  - Document this loudly. Agents will otherwise trust it and produce z-order bugs.
VARIABLES
  - data-composition-variables lives on <html> and is a JSON ARRAY of objects
    {id, type, label, default}. NOT an object.
  - data-variable-values lives on a HOST element and is a JSON OBJECT keyed by id.
  - Read at runtime via window.__hyperframes.getVariables().
  - CLI override at render time:
      npx hyperframes render --variables '{"accentColor":"#E05A36"}'
GSAP
  - ALWAYS construct as gsap.timeline({paused:true}). Never autoplay.
  - Register on window.__timelines["<compositionId>"] — key must equal data-composition-id.
  - The third argument to .to()/.fromTo() is ABSOLUTE time in SECONDS, not a position
    offset and not a relative duration: tl.to(el, {opacity:1}, 1.5) means "at t=1.5s".
  - Supported animated properties ONLY:
      opacity, x, y, scale, scaleX, scaleY, rotation, width, height, visibility
    Any other property is silently ignored or breaks determinism. Document this table.
CLI — exact verified invocations
  npx hyperframes init <name> --example blank|title-card|video-edit
      (the flag is --example. --template was renamed and errors out.)
  npx hyperframes render -f 30 -q draft|standard|high -w 1-8 -o out.mp4
      [--crf N] [--video-bitrate 10M] [--gpu] [--browser-gpu|--no-browser-gpu]
      [--video-frame-format auto|jpg|png] [--docker]
  npx hyperframes check
      = the QA gate. Runs Runtime + Layout + Motion + Contrast (WCAG AA) + Snapshots.
      A passing smoke test reported "0 errors, 0 warnings" and "5/5 text checks pass
      WCAG AA". Treat any error or warning as a failure.
  Other verified subcommands: add, capture, catalog, preview, present, publish, lint,
  validate, beats, inspect, keyframes, snapshot, media-treatment, normalize-audio,
  grade-compare, compare, info, compositions, timeline, benchmark, browser, doctor,
  upgrade, cloud, lambda, cloudrun, skills, transcribe, tts, remove-background, auth,
  feedback, telemetry, docs.
MEDIA
  npx hyperframes transcribe  -> speech-to-text for subtitle generation
  npx hyperframes tts         -> local Kokoro-82M TTS. NOT INSTALLED on this machine.
    Record that as a dependency, and specify the install path, but do not install it
    unless the owner authorizes it (Kokoro pulls model weights from the network).
VERIFIED PERF BASELINE (use for capacity planning)
  1080x1920, 30 fps, H.264, 120 frames, 4.0 s rendered in 15.3 s on this machine
  (8-core i5-1145G7, 15.7 GB RAM, no CUDA GPU). That is ~7.8 s of wall time per second
  of video at 1080x1920/30 with no audio muxing. Document the extrapolation for a 30 s
  Reel: roughly 4 minutes at -w 4. Recommend -q draft for iteration, -q high only for
  final publish.

DOCUMENT STRUCTURE — docs/video-studio/HYPERFRAMES_RESEARCH.md:
  ## Version & Provenance
  ## Composition Contract      (the attribute table, copy-pasteable)
  ## Minimal Working Composition  (a complete index.html for a 4s 1080x1920 title card)
  ## GSAP Rules                (paused timeline, registration, absolute-time gotcha,
                                supported-property whitelist)
  ## Tracks and Z-Order        (the data-track-index correction, prominent)
  ## Variables                 (array vs object, runtime read, CLI override)
  ## CLI Reference             (every command above with a real example)
  ## Media & Audio             (video/audio tags, data-media-start, data-volume,
                                data-has-audio)
  ## QA Gate                   (what `check` validates; how to read its output)
  ## Performance Baseline      (the 15.3s measurement and its extrapolation)
  ## Discrepancies             (bundled docs vs verified facts — empty if none)
  ## Known Gaps                (anything you could not verify, stated plainly)

The Minimal Working Composition section MUST be a complete file that, written to
index.html alongside a package.json with hyperframes as a dependency, renders without
error. Keep it under 80 lines. Use Plus Jakarta Sans / Inter fallbacks, not webfonts.

RULES
  - Do not install anything. Do not `npm install`. Do not run `playwright install`.
  - Do not render video in this prompt. PROMPT 05 owns the smoke render.
  - Never claim a behaviour you did not read in docs/help output or the verified facts.
  - If docs and verified facts disagree, the verified facts win and you log the delta.

ACCEPTANCE
  - docs/video-studio/HYPERFRAMES_RESEARCH.md exists with all 10 sections.
  - It contains a complete, self-contained minimal composition.
  - The data-track-index correction appears in BOTH the Tracks section and the GSAP Rules
    section (it is the single most common agent mistake).
  - Kokoro/whisper absence is recorded as a dependency, not silently worked around.
````

## 6. Expected output files
- `docs/video-studio/HYPERFRAMES_RESEARCH.md`

## 7. Execution requirements
- Runs `npx hyperframes docs`, `--help`, `doctor`, `info`. No installs, no renders.
- Network only for upstream docs if bundled docs are insufficient.

## 8. Dependencies on earlier prompts
- PROMPT 00 (confirms toolchain present and Node/Python versions).

## 9. Acceptance criteria
- All 10 documented sections present.
- Complete minimal composition included and hand-verified for attribute correctness.
- `data-track-index` is documented as display-only, in two places.
- Discrepancies section exists even if empty.

## 10. Verification instructions
```powershell
Test-Path docs\video-studio\HYPERFRAMES_RESEARCH.md
Select-String -Path docs\video-studio\HYPERFRAMES_RESEARCH.md -Pattern "data-track-index"
Select-String -Path docs\video-studio\HYPERFRAMES_RESEARCH.md -Pattern "paused:\s*true"
Select-String -Path docs\video-studio\HYPERFRAMES_RESEARCH.md -Pattern "--example"
```
Then actually copy the Minimal Working Composition into a scratch dir and confirm it is
well-formed. PROMPT 05 will render it.

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `hyperframes docs <topic>` returns nothing | Topic name guessed wrong | Run `npx hyperframes docs` bare to list real topics first. |
| Bundled docs describe `--template` | Docs lag the binary | Verified fact (`--example`) wins. Log under Discrepancies. |
| Docs describe track-index as paint order | Stale docs | Verified fact wins; this is exactly why the correction is duplicated. |
| Agent writes `tl.to(el,{...}, "+=0.5")` | Misread absolute-time rule | Reject; third arg is absolute seconds. Re-run PROMPT 08 with the rule quoted inline. |
| Agent uses `boxShadow`/`filter` in a tween | Outside whitelist | Rewrite to opacity/transform only, or pre-render the effect as an image asset. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 02 — Signhify Brand and Content Identity
# ═════════════════════════════════════════════════════════════════════════════

`[RESEARCH]`

## 1. Prompt title
PROMPT 02 — Signhify Brand and Content Identity

## 2. Intended purpose
Distil `data/brand.json` plus the verified product facts from `signhify.dpdns.org` into a
**machine-readable token file** (`video_studio/brand_tokens.json`) that every renderer,
captioner, and prompt in the engine reads instead of hardcoding colors, fonts, or voice.
This is the anti-drift anchor.

## 3. When to use it
- After PROMPT 00, before PROMPT 06 (design system consumes these tokens).
- Re-run when `data/brand.json` changes — `brand_tokens.json` must never disagree with it.
- Before any caption generation (PROMPT 13) or on-screen text (PROMPT 07).

## 4. Required inputs
- `D:\Autogram\data\brand.json` (authoritative).
- `https://signhify.dpdns.org` (product facts; may be blocked).
- `assets/signhify-logo-vector.png` and 9 × `assets/ig_signhify.studio_*.jpg` (1080×1350).

## 5. Exact copy-paste prompt text

````
You are producing the single source of truth for Signhify Studio's brand identity as it
applies to AI-generated video.
Working directory: D:\Autogram

TASK
Create TWO files:
  (a) video_studio/brand_tokens.json   — machine-readable, consumed by the renderer
  (b) docs/video-studio/BRAND_IDENTITY.md — the human-readable rationale + copy rules

STEP 1 — READ THE AUTHORITATIVE SOURCE
Read D:\Autogram\data\brand.json. Do not retype it from memory. Extract:
  brand_name, handle, website, website_display, watermark, footer_text, sign_off,
  positioning, target_audience[], voice[], content_pillars[], follow_triggers{},
  avoid[], design.colors{}, design.fonts{}, timezone.

STEP 2 — VERIFY PRODUCT FACTS (network, best-effort)
Attempt to fetch https://signhify.dpdns.org. Use whatever fetch capability you have.
CONFIRMED FACTS (use these verbatim if the fetch fails or is blocked):
  - Product name: Signhify Website Builder from a Single Prompt.
  - Flow: type a prompt -> AI generates a scroll-reactive site with cinematic video,
    imagery and motion -> publish to a live URL in minutes.
  - Mechanism: generate ~8s of cinematic video, extract hundreds of frames, replay them
    in the native browser as 3D parallax on scroll. Stated by the product as:
    "No WebGL, no Three.js, no code - just native browser scroll with buttery-smooth
    frame interpolation."
  - Features: Multi-Video Continuation; Full-Stack Export (ZIP with frontend + backend
    starter including an Express API); Iterative Chat Editing; Product Injection;
    Adjustable FPS 10-40.
  - Specs: 400+ frames per site, ~8s source video, 10-40 FPS, ZIP deployable.
  - Pricing: Starter $5/mo (5 credits), Pro $50/mo (75 credits), Studio $100/mo
    (125 credits, labelled "Most Chosen"), Enterprise $200/mo (300 credits). Annual
    billing saves 20%.
  - Founder: Piyush Raj Singh, AI systems engineer, Varanasi, India. Registered MSME
    (UDYAM).
If the fetch SUCCEEDS, you may add detail — but any addition must be quoted from the page.
If the fetch FAILS or is BLOCKED, record exactly:
  "ACCESS LIMIT: signhify.dpdns.org was not reachable / blocked at research time.
   Product facts above are from prior verified capture. No live re-verification."
DO NOT FABRICATE ANY PRODUCT DETAIL. No invented metrics, no invented testimonials,
no invented customer names, no invented revenue.

STEP 3 — INSTAGRAM ACCESS LIMIT
Attempt to fetch https://instagram.com/signhify.studio.
KNOWN RESULT: it was BLOCKED at research time. Record:
  "ACCESS LIMIT: instagram.com/signhify.studio was blocked at research time. No live
   follower count, engagement rate, or post performance has been observed. Any analytics
   claim about the account MUST be labelled unverified."
Never infer account size from a blocked page. Never invent engagement data.

STEP 4 — WRITE video_studio/brand_tokens.json
Valid JSON, no comments, no trailing commas. Exact structure:

{
  "version": "1.0.0",
  "source": "data/brand.json",
  "brand": {
    "name": "Signhify Studio",
    "handle": "@signhify.studio",
    "website": "https://signhify.dpdns.org",
    "website_display": "signhify.dpdns.org",
    "watermark": "SIGNHIFY.STUDIO",
    "footer_text": "@SIGNHIFY.STUDIO · SIGNHIFY.DPDNS.ORG",
    "avatar_letter": "P",
    "sign_off": "My name is Piyush Raj Singh. Stop posting. Start shipping."
  },
  "colors": {
    "bg": "#F8F6F0",
    "card_bg": "#FFFFFF",
    "card_border": "rgba(0, 0, 0, 0.08)",
    "primary": "#111111",
    "accent": "#E05A36",
    "accent_hover": "#CC4C29",
    "highlight": "#16A34A",
    "text": "#111111",
    "text_muted": "#666666"
  },
  "fonts": {
    "headline": "'Plus Jakarta Sans', -apple-system, sans-serif",
    "body": "'Inter', -apple-system, sans-serif",
    "code": "'JetBrains Mono', monospace",
    "hand": "'Caveat', cursive",
    "stamp": "'Anton', 'Plus Jakarta Sans', sans-serif"
  },
  "video": {
    "width": 1080,
    "height": 1920,
    "aspect": "9:16",
    "fps_default": 30,
    "safe_area_top_px": 180,
    "safe_area_bottom_px": 320,
    "safe_area_side_px": 80,
    "max_duration_s": 60
  },
  "voice": ["authoritative","architectural","hyper-practical","zero-fluff",
            "contrarian","open-source-first"],
  "pillars": ["FOSS SaaS Alternatives","Trending GitHub Spotlight","Local AI & Edge Compute",
              "Developer Power Tools & CLI","Self-Hosted Architecture",
              "Open Source Economics & Contrarian"],
  "audience": ["Software Engineers & Systems Developers","Tech Founders & Solopreneurs",
               "DevOps & Self-Hosting Enthusiasts","AI Builders & Prompt Engineers"],
  "banned_phrases": [ ...the exact 16 strings from brand.json avoid[]... ],
  "cta": {
    "headline": "Follow signhify.studio for more daily AI architectures & self-hosted systems.",
    "subtext": "FULL A.I. ENGINEERING STUDIO · SIGNHIFY.STUDIO",
    "button_text": "FOLLOW SIGNHIFY.STUDIO FOR MORE →",
    "comment_lead_magnet": "Comment 'BLUEPRINT' or 'FOSS' for the full runnable code. Follow signhify.studio for more."
  },
  "product_facts": {
    "name": "Signhify Website Builder from a Single Prompt",
    "tagline": "Generate a cinematic scroll-reactive website from a single prompt and publish it to a live URL in minutes.",
    "mechanism": "Generate ~8s of cinematic video, extract hundreds of frames, replay them in the native browser as 3D parallax on scroll.",
    "no_code_claim": "No WebGL, no Three.js, no code - just native browser scroll with buttery-smooth frame interpolation.",
    "features": ["Multi-Video Continuation","Full-Stack Export","Iterative Chat Editing",
                 "Product Injection","Adjustable FPS (10-40)"],
    "specs": {"frames_per_site": "400+", "source_video_s": 8, "fps_range": "10-40",
              "export": "ZIP deployable"},
    "pricing": [
      {"tier":"Starter","monthly_usd":5,"credits":5},
      {"tier":"Pro","monthly_usd":50,"credits":75},
      {"tier":"Studio","monthly_usd":100,"credits":125,"badge":"Most Chosen"},
      {"tier":"Enterprise","monthly_usd":200,"credits":300}
    ],
    "annual_discount_pct": 20,
    "founder": {"name":"Piyush Raj Singh","role":"AI systems engineer",
                "location":"Varanasi, India","registration":"Registered MSME (UDYAM)"}
  },
  "access_limits": {
    "product_site_verified_at_research_time": false,
    "product_site_note": "<fill from STEP 2>",
    "instagram_blocked": true,
    "instagram_note": "instagram.com/signhify.studio was blocked at research time. No live analytics observed. Never fabricate post performance."
  },
  "assets": {
    "logo_png": "assets/signhify-logo-vector.png",
    "carousel_count": 9,
    "carousel_glob": "assets/ig_signhify.studio_*.jpg",
    "carousel_size": "1080x1350"
  }
}

STEP 5 — WRITE docs/video-studio/BRAND_IDENTITY.md
Sections:
  ## Voice        — 6 voice attributes, each with a "sounds like / does not sound like" example
  ## Banned Language — the 16 phrases, with a "why" and a substitute-word column
  ## Sign-off Rules — when the sign-off line is used (only on the final CTA frame)
  ## Pillar-to-Video Mapping — which of the 6 content pillars suits a Reel, and the
                              typical 15s/30s structure for each
  ## On-Screen Type Scale — headline/body/code/hand/stamp roles, relative sizes in px at
                            1080x1920, and the safe areas
  ## Caption Rules — Instagram caption structure, hashtag policy, banned-phrase sweep
  ## Product Fact Sheet — the confirmed facts from STEP 2, clearly marked verified/unverified
  ## Access Limits  — the Instagram block and the product-site reachability, verbatim

STEP 6 — VALIDATE
  .venv\Scripts\python.exe -c "import json;d=json.load(open('video_studio/brand_tokens.json',encoding='utf-8'));print(len(d['banned_phrases']),'banned');print(d['colors']['accent']);print(len(d['product_facts']['pricing']),'tiers')"
MUST print: 16 banned, #E05A36, 4 tiers.
Also diff the banned list against data/brand.json avoid[] and confirm 16/16 match.

RULES
  - brand_tokens.json must stay byte-consistent with data/brand.json on colors, fonts,
    handle, watermark, sign_off, and the avoid list. If they ever diverge, brand.json wins.
  - Never add a product feature, price, spec, or claim that is not in STEP 2's confirmed list.
  - Never claim Instagram analytics. The account was blocked.
  - Never hardcode a token or API key anywhere.

ACCEPTANCE
  - brand_tokens.json parses as valid JSON and prints 16 / #E05A36 / 4.
  - BRAND_IDENTITY.md has all 8 sections.
  - The 16 banned phrases match data/brand.json exactly.
  - Both access limits recorded verbatim, including the Instagram block.
````

## 6. Expected output files
- `video_studio/brand_tokens.json`
- `docs/video-studio/BRAND_IDENTITY.md`

## 7. Execution requirements
- Reads `data/brand.json`, `assets/`. Network fetch best-effort on the product site and
  Instagram (both may fail — failure is recorded, not worked around).
- Creates `video_studio/` directory if absent.

## 8. Dependencies on earlier prompts
- PROMPT 00 (environment known; confirms network/tooling state).

## 9. Acceptance criteria
- JSON valid, prints `16 banned`, `#E05A36`, `4 tiers`.
- Colors, fonts, handle, watermark, sign_off match `data/brand.json` exactly.
- All product facts traceable to the confirmed list; no embellishment.
- Instagram block recorded; no analytics claimed.

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -c "import json;d=json.load(open('video_studio/brand_tokens.json',encoding='utf-8'));assert d['banned_phrases']==json.load(open('data/brand.json',encoding='utf-8'))['avoid'];print('BANNED LIST MATCHES brand.json')"
.venv\Scripts\python.exe -c "import json;d=json.load(open('video_studio/brand_tokens.json',encoding='utf-8'));assert d['colors']['accent']=='#E05A36' and d['brand']['handle']=='@signhify.studio';print('TOKENS OK')"
Select-String -Path docs\video-studio\BRAND_IDENTITY.md -Pattern "blocked"
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Product site fetch blocked | Network restriction | Use confirmed facts; record access limit. Do not guess. |
| `json.load` throws | Comment or trailing comma in the JSON | Strip it. JSON has no comments. |
| Banned list length ≠ 16 | Agent paraphrased or deduped | Copy verbatim from `brand.json` `avoid[]`. Never retype. |
| Agent adds "$9/mo" or "50,000 users" | Fabrication drift | Reject. Only the 4 confirmed tiers exist. |
| Agent writes Instagram stats | Ignored the block note | Delete. The access limit is non-negotiable. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 03 — System Architecture and Technical Specification
# ═════════════════════════════════════════════════════════════════════════════

`[PLANNING]`

## 1. Prompt title
PROMPT 03 — System Architecture and Technical Specification

## 2. Intended purpose
Specify the `video_studio/` package completely — module boundaries, data contracts (brief
schema, storyboard schema, manifest schema), CLI surface, and failure semantics — **before
any of it is implemented**. Prompts 04–18 are implementations of this document.

## 3. When to use it
- After PROMPT 01 (HyperFrames contract known) and PROMPT 02 (tokens known).
- Before PROMPT 04 (agent config wraps it) and PROMPT 08 (first real code).
- Re-visit if the CLI surface needs a change; do not change it mid-implementation.

## 4. Required inputs
- `docs/video-studio/ENVIRONMENT_AUDIT.md` (PROMPT 00)
- `docs/video-studio/HYPERFRAMES_RESEARCH.md` (PROMPT 01)
- `video_studio/brand_tokens.json` + `docs/video-studio/BRAND_IDENTITY.md` (PROMPT 02)

## 5. Exact copy-paste prompt text

````
You are writing the build specification for a video production engine. You are NOT writing
the implementation yet. Working directory: D:\Autogram.

CONTEXT
Repo: D:\Autogram. Python 3.14 in .venv (3.14.7). Node v22.23.1. hyperframes 0.8.58 via
`npx hyperframes` from D:\Autogram. FFmpeg/ffprobe 8.0.1 on PATH. Windows x64, 8-core
i5-1145G7, 15.7 GB RAM, NO CUDA GPU. Docker installed but not running.
No pyproject.toml, no setup.py — modules are imported directly.
Read: docs/video-studio/ENVIRONMENT_AUDIT.md, docs/video-studio/HYPERFRAMES_RESEARCH.md,
video_studio/brand_tokens.json.

TASK
Write docs/video-studio/ARCHITECTURE.md — a complete, implementable specification.

1. DIRECTORY LAYOUT (exact)
  video_studio/
    __init__.py
    __main__.py            -> `python -m video_studio` entrypoint
    cli.py                 -> argparse; subcommands build|render|qa|package|publish|list
    brief.py               -> brief load + validate (the contract)
    storyboard.py          -> brief -> storyboard.json
    compose.py             -> storyboard + tokens -> HyperFrames project
    render.py              -> invoke `npx hyperframes render`
    audio.py               -> TTS / SRT generation / audio mux
    qa.py                  -> ffprobe + frame inspection + gate
    publish.py             -> cover/caption/manifest + Meta Graph publish
    analytics.py           -> pull IG insights, write content-memory
    scheduler.py           -> cron-like slot runner + retry/backoff
    state.py               -> durable run state (JSON, atomic writes)
    brand_tokens.json
    prompts/
      script.md            -> the script-writing system prompt
      captions.md          -> caption + hashtag system prompt
    templates/
      composition.html.jinja2   -> the brand design system (PROMPT 06 owns this)
      slide_title.html.jinja2
      slide_bullets.html.jinja2
      slide_code.html.jinja2
      slide_cta.html.jinja2
    design/
      tokens.css
    briefs/<slug>.json
    work/<slug>/           index.html, hyperframes.json, package.json, assets/
    output/<slug>/         reel.mp4, cover.jpg, captions.srt, caption.txt, script.md,
                           storyboard.json, brief.json, asset_manifest.json,
                           qa_report.md, render.log, manifest.json

2. CLI SURFACE (exact, argparse)
  python -m video_studio build    --brief <path> [--slug X] [--dry-run]
  python -m video_studio render   --brief <path> [--slug X] [--quality draft|standard|high]
                                  [--fps 30] [--no-audio] [--dry-run] [--work-dir D]
  python -m video_studio qa       --video <path> [--report <path>] [--strict]
  python -m video_studio package  --brief <path> [--slug X] [--dry-run]
  python -m video_studio publish  --slug X [--caption-file F] [--cover F] [--dry-run]
  python -m video_studio list
Global flags on every subcommand: --json (machine-readable output), --quiet.
EXIT CODES: 0 success; 1 runtime failure; 2 invalid brief / contract violation;
            3 QA gate failed; 4 publish skipped or blocked.

3. BRIEF SCHEMA (the contract — video_studio/briefs/<slug>.json)
Required:
  slug              string, ^[a-z0-9][a-z0-9-]{1,60}$   (also the folder name)
  topic             string, 10-140 chars, no banned phrase
  pillar            enum of the 6 brand pillars
  hook              string, <= 90 chars — the first 1.5 s on-screen line
  key_points        array of 3-6 strings, each <= 140 chars
  cta               string, <= 120 chars
  duration_s        int, 15..60
  aspect            "9:16" (only supported value in v1)
  source_url        string URL or null
  language          "en" (v1)
  narration         { "enabled": bool, "voice": string, "tone": string } or null
Optional:
  music             { "url": string|null, "gain": number 0..1, "duck_narration": bool }
  overlay_cta       bool (default true)
  sign_off          bool (default true)
  priority          int 1..5 (default 3)
  notes             string (free text, never rendered verbatim)
Validation MUST reject: missing required key, bad slug regex, duration out of range,
aspect != "9:16", fewer than 3 or more than 6 key_points, any banned phrase in topic /
hook / key_points / cta, a hook longer than 90 chars.
A validation failure prints the offending JSON path and exits 2. Never auto-fix silently.

4. STORYBOARD SCHEMA (video_studio/work/<slug>/storyboard.json)
  { "slug", "duration_s", "fps", "width": 1080, "height": 1920,
    "scenes": [ { "index": 0, "type": "hook|title|bullets|code|stat|cta",
                  "start_s": 0.0, "duration_s": 2.0,
                  "headline": str, "body": str|null, "code": str|null,
                  "bg": "<hex or token name>", "accent": "<hex or token name>",
                  "narration": str, "transition": "cut|fade|slide_up|wipe" } ] }
Invariants the generator MUST enforce and the QA gate MUST re-check:
  - scenes[0].type == "hook"
  - scenes[-1].type == "cta"  (when overlay_cta or sign_off is true)
  - sum(duration_s) == duration_s (within 0.05 s)
  - no scene duration < 0.8 s or > 12 s
  - start_s is the running sum of prior durations
  - 3 <= len(scenes) <= 9

5. COMPOSITION EMISSION RULES (from PROMPT 01 — do not restate wrongly)
  - index.html root carries data-composition-id, data-width="1080", data-height="1920",
    data-start="0", data-duration="<total_s>".
  - Every timed element has class="clip" plus data-start / data-duration in SECONDS.
  - Each scene maps to one <div class="scene clip" data-composition-id="scene-<i>"
    data-start data-duration> nested inside the root. The root references scenes with
    data-composition-src, OR scenes are inline children — pick ONE and document it.
  - GSAP: gsap.timeline({paused:true}) stored at
    window.__timelines["<root data-composition-id>"].
    Third arg to .to()/.fromTo() is ABSOLUTE SECONDS.
    Supported props ONLY: opacity, x, y, scale, scaleX, scaleY, rotation, width, height,
    visibility.
  - data-track-index is DISPLAY-ONLY. It does NOT control paint order and does NOT prevent
    overlap. Use CSS z-index. Document this in the spec as a hard rule.
  - CSS custom properties are generated from brand_tokens.json colors + fonts. No hardcoded
    hex in templates.
  - safe areas: 180 px top, 320 px bottom, 80 px sides. All text must respect them.

6. HYPERFRAMES INVOCATIONS (exact)
  Project scaffold (in work/<slug>/):
    npx hyperframes render -f <fps> -q <draft|standard|high> -w 4 -o <out/reel.mp4>
  QA gate (before packaging):
    npx hyperframes check
  Pass criteria: "0 errors, 0 warnings" AND all text checks pass WCAG AA contrast.
  Capture:
    npx hyperframes snapshot
  ALWAYS call `npx hyperframes check` and record its stdout verbatim to render.log.
  A check failure is a HARD STOP. Do not package or publish.
  Wall-time expectation: ~7.8 s of wall clock per second of video at 1080x1920/30
  (120 frames / 4.0 s rendered in 15.3 s on this machine). Default -w 4.

7. OUTPUT CONTRACT (video_studio/output/<slug>/)
  reel.mp4             1080x1920, H.264, yuv420p, CFR, target 30 fps
  cover.jpg            1080x1920 (NOT 1080x1350), extracted at the CTA scene, sRGB
  captions.srt         if narration enabled
  caption.txt          Instagram caption body
  script.md            human-readable script
  storyboard.json      as above
  brief.json           the resolved brief
  asset_manifest.json  every asset used: path, source (generated|downloaded|brand),
                       license note, sha256, bytes
  qa_report.md         ffprobe facts + frame inspection + PASS/FAIL per check
  render.log           verbatim stdout of `npx hyperframes check` + ffprobe output
  manifest.json        { slug, created_utc, duration_s, fps, width, height, bytes,
                         sha256, qa_status, published: false, ig_media_id: null }

8. FAILURE SEMANTICS
  - brief invalid           -> exit 2, no files written
  - hyperframes render fails-> render.log captures output, exit 1, no packaging
  - hyperframes check fails -> exit 3, qa_report.md written with FAIL, no packaging
  - qa (standalone) fails    -> exit 3
  - publish blocked/missing creds -> exit 4, manifest.published stays false
  - Every state write is atomic (write .tmp then os.replace). No partial JSON ever.
  - A crashed run must leave output/<slug>/manifest.json with published:false.

9. DEPENDENCY MAP
  Which env keys each stage reads. Read from os.environ only; never log values.
    IG_USER_ID, IG_ACCESS_TOKEN, META_API_VERSION (bump default to v26.0),
    INSTAGRAM_BUSINESS_ACCOUNT_ID, META_GRAPH_ACCESS_TOKEN, PUBLIC_CDN_BASE,
    DRY_RUN (default true), VIDEO_STUDIO_PUBLISH (default false — the explicit opt-in).
  Publishing is impossible unless VIDEO_STUDIO_PUBLISH=true AND DRY_RUN=false AND
  IG_USER_ID and IG_ACCESS_TOKEN are both non-empty.

10. DOCUMENT STRUCTURE for ARCHITECTURE.md
  ## Overview            ## Directory Layout (as a tree)
  ## CLI Reference        ## Brief Schema   ## Storyboard Schema
  ## Composition Emission Rules   ## HyperFrames Invocations
  ## Output Contract      ## Failure Semantics + exit codes
  ## Dependency Map + env keys   ## Module-by-module responsibility
  ## Extension Points (where to add a new scene type, a new pillar, a new QA check)

RULES
  - This is a SPEC. Do not create video_studio/*.py yet. PROMPT 08 onward implements it.
  - Every schema field must have a type, a default, and a validation rule.
  - Every env key must be named exactly as above.
  - No invented APIs. No invented CLI flags. If you are unsure, mark it OPEN QUESTION.

ACCEPTANCE
  - ARCHITECTURE.md has all 10 sections.
  - Brief schema has field-level types, defaults, and validation rules.
  - Storyboard invariants are enumerated and testable.
  - The data-track-index correction and the GSAP absolute-time rule both appear.
  - No .py implementation files created.
````

## 6. Expected output files
- `docs/video-studio/ARCHITECTURE.md`

## 7. Execution requirements
- Reads the three upstream documents. Writes one spec file. No code.

## 8. Dependencies on earlier prompts
- PROMPT 00, PROMPT 01, PROMPT 02.

## 9. Acceptance criteria
- All 10 sections present.
- Brief + storyboard schemas fully typed with validation rules.
- Exit-code table complete (0/1/2/3/4).
- Output contract lists all 11 artifacts.
- Zero `.py` files created.

## 10. Verification instructions
```powershell
Select-String -Path docs\video-studio\ARCHITECTURE.md -Pattern "data-track-index"
Select-String -Path docs\video-studio\ARCHITECTURE.md -Pattern "VIDEO_STUDIO_PUBLISH"
Select-String -Path docs\video-studio\ARCHITECTURE.md -Pattern "exit 3"
Get-ChildItem video_studio -Filter *.py -Recurse -ErrorAction SilentlyContinue   # must be empty
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Agent starts writing `.py` files | Spec/implementation boundary blur | Delete the files. Re-run with "this is a SPEC" repeated. |
| Env keys invented (`IG_TOKEN`) | Not grounded | Only the five documented keys exist. Correct them. |
| `--publish` default left true | Dangerous default | Must default off behind `VIDEO_STUDIO_PUBLISH`. |
| Cover spec says 1080×1350 | Confused with the carousel assets | Cover is 1080×1920. Carousels are 1080×1350. |
| Exit codes vague | Missing failure semantics | Enforce the 0/1/2/3/4 table. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 04 — OpenCode Agent Configuration
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]`

## 1. Prompt title
PROMPT 04 — OpenCode Agent Configuration

## 2. Intended purpose
Package the engine's operating rules into a **persistent agent definition** so that any
future session — human-driven or scheduled — executes video production with the same
constraints, the same file contracts, and the same safety rails without re-reading twenty
prompts.

## 3. When to use it
- After PROMPT 03 (the agent wraps the architecture spec).
- Whenever the pipeline's contracts change, so the agent never drifts from the spec.
- Before PROMPT 18, which assumes a configured agent.

## 4. Required inputs
- `docs/video-studio/ARCHITECTURE.md` (PROMPT 03).
- `AGENTS.md` at repo root (existing repo conventions the new agent must not contradict).
- `.opencode/` directory conventions if the repo already has any.

## 5. Exact copy-paste prompt text

````
You are adding a persistent agent definition to an existing repository.
Working directory: D:\Autogram

TASK
Create the OpenCode agent definition(s) for the Signhify Studio video production engine.
First inspect: does .opencode/ exist? does .opencode/agent/ exist? does opencode.json or
opencode.jsonc exist at the repo root? READ them before writing. Match the existing format
exactly. If .opencode/ does not exist, create it. Do not overwrite an existing config —
merge into it.

CREATE
(a) .opencode/agent/video-studio.md
    frontmatter: description, mode, tools, permission block.
    description (one paragraph, concrete): "Produces Signhify Studio Instagram Reels from
    a content brief using the HyperFrames render pipeline. Use for creating new videos,
    re-rendering, running QA, packaging, and publishing to Instagram. Owns the
    video_studio/ package."
    mode: primary
    tools: read, write, edit, bash, glob, grep
    permission: allow the read-only and video-studio commands listed below; ASK before
    anything that touches Meta's API with VIDEO_STUDIO_PUBLISH=true; DENY anything that
    reads or prints .env values, starts Docker, or installs packages without approval.

    System prompt body must include, in this order:
    1. ROLE — you operate the Signhify Studio video engine at D:\Autogram.
    2. ENVIRONMENT (fixed facts):
         hyperframes 0.8.58 via `npx hyperframes` from D:\Autogram (Apache-2.0);
         upstream latest 0.8.145.
         Node v22.23.1, npm 12.2.0, Python 3.14 (venv at .venv, 3.14.7),
         FFmpeg/ffprobe 8.0.1, Windows x64, 8-core i5-1145G7, 15.7 GB RAM, no CUDA GPU.
         Docker installed but NOT running. whisper-cpp NOT installed.
         Kokoro TTS NOT installed.
         Render baseline: 1080x1920 @30fps, 120 frames / 4.0 s in 15.3 s.
    3. FILE CONTRACT — the three trees:
         video_studio/briefs/<slug>.json
         video_studio/work/<slug>/   (index.html, hyperframes.json, package.json, assets/)
         video_studio/output/<slug>/ (reel.mp4, cover.jpg, captions.srt, caption.txt,
           script.md, storyboard.json, brief.json, asset_manifest.json, qa_report.md,
           render.log, manifest.json)
    4. COMMANDS — the exact CLI:
         python -m video_studio build   --brief <brief.json>
         python -m video_studio render  --brief <brief.json> [--quality draft|standard|high]
                                         [--fps 30] [--no-audio] [--dry-run] [--slug X]
         python -m video_studio qa      --video <path> [--report <path>] [--strict]
         python -m video_studio package --brief <brief.json> [--slug X] [--dry-run]
         python -m video_studio publish --slug X [--dry-run]
       plus raw hyperframes:
         npx hyperframes init <name> --example blank|title-card|video-edit
         npx hyperframes render -f 30 -q draft|standard|high -w 1-8 -o out.mp4
         npx hyperframes check
         npx hyperframes snapshot | inspect | lint | compositions | timeline | info
         npx hyperframes doctor | transcribe | tts | normalize-audio
    5. HYPERFRAMES RULES (non-negotiable):
         - `init` uses --example, NEVER --template (renamed; --template errors out).
         - data-start / data-duration are SECONDS.
         - data-track-index is DISPLAY-ONLY. It does NOT set paint order and does NOT
           prevent overlap. Use CSS z-index.
         - GSAP: gsap.timeline({paused:true}) stored on
           window.__timelines["<data-composition-id>"]. Third arg is ABSOLUTE SECONDS.
           Supported props only: opacity, x, y, scale, scaleX, scaleY, rotation, width,
           height, visibility.
         - data-composition-variables on <html> is a JSON ARRAY of
           {id,type,label,default}. data-variable-values is a JSON OBJECT keyed by id.
         - `npx hyperframes check` is the QA gate (Runtime + Layout + Motion + Contrast
           WCAG AA + Snapshots). "0 errors, 0 warnings" is the only pass.
    6. BRAND — read video_studio/brand_tokens.json. Never hardcode a hex or a font.
         Handle @signhify.studio, watermark SIGNHIFY.STUDIO,
         accent #E05A36, bg #F8F6F0, text #111111, highlight #16A34A, muted #666666.
         Fonts: Plus Jakarta Sans (headline), Inter (body), JetBrains Mono (code),
         Caveat (hand), Anton (stamp).
         Sign-off (final CTA frame only): "My name is Piyush Raj Singh.
         Stop posting. Start shipping."
    7. BANNED PHRASES — the 16 from data/brand.json avoid[]:
         generic hype, fake urgency, unsupported statistics, overused motivational
         language, keyword stuffing, game-changer, unlock the power of, in today's
         fast-paced world, dive into, at its core, seamless, robust, revolutionary tool,
         next-gen AI, ultimate secret, must-have app.
    8. HARD RULES:
         - Never fabricate product capabilities, metrics, testimonials, customer results,
           or revenue.
         - Never print or commit API keys or tokens. Placeholders only.
         - Never claim a video was rendered, a test passed, or a reel was published unless
           a command in the transcript proves it.
         - Never bypass Instagram auth or platform security.
         - Do not activate paid APIs without explicit owner authorization.
         - Respect the 16 banned phrases in every piece of generated copy.
         - Inspect before modifying. Preserve existing code.
         - instagram.com/signhify.studio was BLOCKED at research time. Never fabricate
           post performance, follower counts, or engagement. Label all analytics unverified.
    9. PUBLISHING GATE:
         Publishing runs ONLY when VIDEO_STUDIO_PUBLISH=true AND DRY_RUN=false AND
         IG_USER_ID and IG_ACCESS_TOKEN are both non-empty. Otherwise exit 4 with
         manifest.published=false. Never print any of these values.
    10. WORKFLOW — for every render task:
         inspect -> plan -> brief -> build -> render -> `npx hyperframes check` ->
         qa -> package -> (ask before) publish -> report with real command output.

(b) .opencode/agent/video-studio-qa.md  (optional, only if .opencode/agent/ exists)
    A read-only variant: permission denies write to video_studio/output/ and denies any
    Meta API call entirely. Same environment + HyperFrames rules.

VALIDATE
  - The agent file(s) parse as valid markdown with valid frontmatter.
  - If opencode.json/opencode.jsonc exists, it is valid JSONC after your merge.
  - grep your own output for the string "password", "token", "secret", "sk-" and confirm
    no real credential is present. Only env KEY NAMES may appear.

RULES
  - Do not modify AGENTS.md, orchestrator.py, dashboard_api.py, or anything in src/.
    This prompt only ADDS the agent config.
  - Do not create a build pipeline here. PROMPT 08 onward implements.
  - If .opencode/ or opencode.json already exists, MERGE. Never overwrite blindly.

ACCEPTANCE
  - .opencode/agent/video-studio.md exists with frontmatter + the 10 sections above.
  - All 6 hard rules and the 16 banned phrases present verbatim.
  - The --example (not --template) rule and the data-track-index correction present.
  - The publishing gate names VIDEO_STUDIO_PUBLISH / DRY_RUN / IG_USER_ID / IG_ACCESS_TOKEN.
  - No existing repo file was modified other than an intentional opencode.json merge.
````

## 6. Expected output files
- `.opencode/agent/video-studio.md`
- `.opencode/agent/video-studio-qa.md` (optional)
- Possibly a minimal merge into an existing `opencode.json` / `opencode.jsonc`.

## 7. Execution requirements
- Must inspect existing `.opencode/` and `opencode.json*` before writing. Merge, never clobber.
- Must not touch `src/`, `orchestrator.py`, `dashboard_api.py`, or `AGENTS.md`.

## 8. Dependencies on earlier prompts
- PROMPT 03 (architecture spec). Optionally 01 and 02 for the rule text.

## 9. Acceptance criteria
- Agent file has valid frontmatter and all 10 sections.
- All 6 hard rules, all 16 banned phrases, the `--example` rule, the `data-track-index`
  correction, and the publishing gate appear verbatim.
- No real credentials anywhere in the output.
- `git diff --stat` shows only intended additions.

## 10. Verification instructions
```powershell
Test-Path .opencode\agent\video-studio.md
Select-String -Path .opencode\agent\video-studio.md -Pattern "data-track-index"
Select-String -Path .opencode\agent\video-studio.md -Pattern "--example"
Select-String -Path .opencode\agent\video-studio.md -Pattern "VIDEO_STUDIO_PUBLISH"
git diff --stat
git status --short
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Agent overwrote `opencode.json` | Blind write | Restore with `git checkout -- opencode.json`, redo as merge. |
| Agent edited `src/` | Scope creep | `git checkout -- src/` and re-run with the exclusion restated. |
| Real token appears in the agent file | Copied from `.env` | Delete immediately. Rotate the key. Only key NAMES belong here. |
| `--template` appears | Copied from stale docs | Replace with `--example`. This is a verified correction. |
| Frontmatter invalid | Wrong schema | Compare to an existing `.opencode/agent/*.md` if one exists; match it. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 05 — HyperFrames Setup and Validation
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]` `[RENDERS VIDEO]`

## 1. Prompt title
PROMPT 05 — HyperFrames Setup and Validation

## 2. Intended purpose
Prove, on this machine, that the HyperFrames toolchain can scaffold a project and render a
1080×1920 MP4 that passes the QA gate. This is the **go/no-go gate** for the entire engine.
If it fails here, nothing downstream matters.

## 3. When to use it
- Immediately after PROMPT 01, before writing any real pipeline code.
- After any Node or hyperframes version change.
- Before PROMPT 10's first production render.

## 4. Required inputs
- `docs/video-studio/HYPERFRAMES_RESEARCH.md` (PROMPT 01).
- Network access to npm (hyperframes is already installed at repo root).
- Nothing else. No credentials, no `.env`.

## 5. Exact copy-paste prompt text

````
You are proving the render toolchain works before any pipeline is built. This is a
go/no-go gate. Working directory: D:\Autogram.

ENVIRONMENT (fixed, do not re-derive): hyperframes 0.8.58 via `npx hyperframes` from
D:\Autogram (Apache-2.0; upstream latest 0.8.145). Node v22.23.1, npm 12.2.0.
FFmpeg/ffprobe 8.0.1 on PATH. Windows x64, 8-core i5-1145G7, 15.7 GB RAM, NO CUDA GPU.
Docker installed but NOT running. Playwright Chromium should already be present.

STEP 1 — DOCTOR
  npx hyperframes doctor
  npx hyperframes --version
Record verbatim output. If `doctor` reports a missing browser, STOP and report the exact
remediation line it prints. Do NOT run `playwright install` without owner approval.

STEP 2 — SCAFFOLD (use the CORRECT flag)
  npx hyperframes init _smoke --example title-card
CRITICAL: the flag is --example, NOT --template. --template was renamed and errors out.
Record the exact output. If the command fails because the dir exists, remove `_smoke/`
and retry once. Inspect the generated files:
  _smoke/index.html, _smoke/hyperframes.json, _smoke/package.json
Print index.html in full. Identify:
  - the root data-composition-id
  - the data-width / data-height / data-start / data-duration values
  - how the GSAP timeline is constructed and where it is registered
  - whether gsap.timeline({paused:true}) is used
  - which animated properties are used

STEP 3 — CONVERT TO THE REEL FORMAT
Edit _smoke/index.html to be a 1080x1920 / 30 fps / 4 second composition:
  - root element gets data-width="1080" data-height="1920"
      data-start="0" data-duration="4"
  - keep the same data-composition-id and register
      window.__timelines["<that id>"]
  - every timed element has class="clip" and data-start / data-duration in SECONDS
  - ANIMATE ONLY these properties: opacity, x, y, scale, scaleX, scaleY, rotation,
    width, height, visibility.
  - the third argument to .to()/.fromTo() is ABSOLUTE SECONDS. `tl.to(el, {...}, 1.5)`
    means "at t = 1.5 s", not "+1.5 s from here".
  - DO NOT rely on data-track-index for stacking or overlap. It is DISPLAY-ONLY for the
    Studio timeline. Use CSS z-index.
  - fonts: Plus Jakarta Sans for the headline with a system fallback. DO NOT load webfonts
    from a CDN — outbound font loading can fail and will change typography.
  - colours: bg #F8F6F0, text #111111, accent #E05A36. Text must clear WCAG AA contrast
    against its background.

STEP 4 — QA GATE (must pass BEFORE render)
  cd _smoke ; npx hyperframes check ; cd ..
`check` runs Runtime + Layout + Motion + Contrast (WCAG AA) + Snapshots.
PASS condition: "0 errors, 0 warnings" AND all text checks pass WCAG AA.
A known-good smoke run reported exactly that plus "5/5 text checks pass WCAG AA".
If it reports ANY error or ANY warning, that is a FAILURE. Fix the HTML and re-run.
Do not proceed to render with a failing check. Record every check run verbatim.

STEP 5 — RENDER
  npx hyperframes render -f 30 -q draft -w 4 -o _smoke/out.mp4
Measure wall time with Measure-Command. The verified baseline on this machine was:
  1080x1920 @30fps, H.264, 120 frames, 4.0 s, rendered in 15.3 s.
Report the actual number. If it is more than 4x the baseline, investigate before
continuing.

STEP 6 — PROVE THE MP4 IS REAL
  ffprobe -v error -select_streams v:0 -show_entries
    stream=width,height,r_frame_rate,nb_frames,pix_fmt,codec_name
    -show_entries format=duration,size,format_name
    -of json _smoke/out.mp4
Requirements: width=1080, height=1920, r_frame_rate=30/1, pix_fmt=yuv420p,
codec_name=h264, duration ~4.0 (tolerate ±0.1), nb_frames ~120 (tolerate ±2).
Then extract 3 frames and confirm they are not blank/black:
  ffmpeg -y -i _smoke/out.mp4 -vf "select='eq(n\,0)+eq(n\,60)+eq(n\,110)'" -vsync 0
    _smoke/frame_%02d.png
Report each frame's mean luma. A black frame means mean luma < 8 — investigate the
timeline registration before shipping.

STEP 7 — QUALITY VARIANT PROBE
  npx hyperframes render -f 30 -q standard -w 4 -o _smoke/out_standard.mp4
Confirm it renders and record the size difference vs draft. Do NOT run -q high
(you have no CUDA GPU; it will be very slow).

STEP 8 — WRITE THE REPORT
Create docs/video-studio/HYPERFRAMES_SMOKE_TEST.md:
  ## Verdict            GO or NO-GO, one line, justified
  ## Doctor Output       verbatim
  ## Scaffold            the init command you ran and the generated file list
  ## Generated index.html  full source, annotated (root attrs, timeline registration)
  ## Check Output        verbatim, for EVERY check run including failures
  ## Render Timings      draft + standard wall times, vs the 15.3 s baseline
  ## ffprobe Proof       the full JSON
  ## Frame Luma          3 frames, mean luma values
  ## Corrected Flags     --example not --template, and any other flag change found
  ## Known Constraints   no GPU, docker down, kokoro/whisper absent, font fallbacks
  ## Reproduction        the exact commands, copy-pasteable from D:\Autogram

STEP 9 — CLEANUP DECISION
Leave _smoke/ in place if the verdict is GO (PROMPT 08 will reuse the pattern).
If the verdict is NO-GO, leave it in place for debugging but say so in the report.

RULES
  - Do NOT modify anything outside _smoke/ and the report file.
  - Do NOT run `npm install`, `pip install`, or `playwright install` without approval.
  - Do NOT start Docker.
  - Do NOT load webfonts from a CDN in the smoke composition.
  - Never write "rendered successfully" unless ffprobe confirms the file.

ACCEPTANCE
  - docs/video-studio/HYPERFRAMES_SMOKE_TEST.md exists with all 10 sections.
  - out.mp4 exists and ffprobe reports 1080x1920 / 30fps / h264 / yuv420p / ~4.0s / ~120 frames.
  - All 3 extracted frames have mean luma >= 8 (i.e. the video is not black).
  - `npx hyperframes check` reported "0 errors, 0 warnings" on the final HTML.
  - The verdict is stated as GO with evidence.
````

## 6. Expected output files
- `docs/video-studio/HYPERFRAMES_SMOKE_TEST.md`
- `_smoke/index.html`, `_smoke/hyperframes.json`, `_smoke/package.json` (scaffold)
- `_smoke/out.mp4`, `_smoke/out_standard.mp4`, `_smoke/frame_01..03.png`

## 7. Execution requirements
- `npx hyperframes` only, plus `ffprobe`/`ffmpeg`. No installs, no Docker.
- `-q draft` then `-q standard` only. No `high` (no CUDA GPU).
- `-w 4` default worker count.

## 8. Dependencies on earlier prompts
- PROMPT 01 (composition contract). PROMPT 00 indirectly (environment).

## 9. Acceptance criteria
- `npx hyperframes init _smoke --example title-card` succeeds (proving the flag).
- `npx hyperframes check` → "0 errors, 0 warnings" + WCAG AA text pass.
- `out.mp4` verified by ffprobe: 1080×1920, 30/1 fps, h264, yuv420p, ~4.0 s, ~120 frames.
- All 3 frames non-black (mean luma ≥ 8).
- Render wall time recorded and compared to the 15.3 s baseline.
- Nothing outside `_smoke/` and the report was touched.

## 10. Verification instructions
```powershell
ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames,pix_fmt,codec_name -show_entries format=duration -of json _smoke\out.mp4
Get-ChildItem _smoke\frame_*.png | Measure-Object | Select-Object -ExpandProperty Count
Set-Location _smoke ; npx hyperframes check ; Set-Location ..
git status --short
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `init` rejects `--template` | Renamed flag | Use `--example`. This is expected; not a real failure. |
| `check` reports a contrast warning | Text colour too close to bg | Move to `#111111` on `#F8F6F0`, or `#FFFFFF` on `#E05A36`. Re-check. |
| Render produces a black MP4 | `window.__timelines` key ≠ `data-composition-id` | The two strings must match exactly. Re-check the registration. |
| `paused:true` missing | Copied from an autoplay example | Must be `gsap.timeline({paused:true})`. Render is non-deterministic without it. |
| Frames overlap / wrong order | Agent used `data-track-index` | It is display-only. Use CSS `z-index`. |
| `doctor` says no browser | Playwright Chromium absent | Report the exact remediation. Ask owner before `playwright install chromium`. |
| Render far slower than 15.3 s | `-q high`, or `-w 8` thrashing, or Docker attempted | Use `-q draft -w 4`. Never pass `--docker` (Docker is not running). |
| `ffprobe` reports `nb_read_frames` 0 | File never written | The render command failed. Read `render.log`, do not assume success. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 06 — Premium Visual Design System
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]`

## 1. Prompt title
PROMPT 06 — Premium Visual Design System

## 2. Intended purpose
Build the **Jinja2 template set and CSS token layer** that every generated composition is
rendered from. This is where the brand stops being documentation and becomes pixels: the
burnt-orange-on-warm-off-white editorial system, the type scale, the motion primitives, and
the safe areas.

## 3. When to use it
- After PROMPT 02 (tokens exist) and PROMPT 05 (toolchain proven).
- Before PROMPT 07 (scripting must know the layouts it is writing copy for) and PROMPT 08
  (which emits HTML from these templates).
- Re-run when `brand_tokens.json` changes.

## 4. Required inputs
- `video_studio/brand_tokens.json` (PROMPT 02).
- `docs/video-studio/BRAND_IDENTITY.md` (PROMPT 02).
- `docs/video-studio/HYPERFRAMES_RESEARCH.md` (PROMPT 01) — for the animation contract.
- `_smoke/index.html` (PROMPT 05) — the working pattern to imitate.

## 5. Exact copy-paste prompt text

````
You are building the visual design system for a 1080x1920 Instagram Reel generator.
Working directory: D:\Autogram

INPUTS (read them first, do not retype from memory):
  video_studio/brand_tokens.json
  docs/video-studio/BRAND_IDENTITY.md
  docs/video-studio/HYPERFRAMES_RESEARCH.md
  _smoke/index.html            <- the proven-good composition from the smoke test

TASK — create these files:
  video_studio/design/tokens.css
  video_studio/templates/composition.html.jinja2
  video_studio/templates/scene_title.html.jinja2
  video_studio/templates/scene_bullets.html.jinja2
  video_studio/templates/scene_code.html.jinja2
  video_studio/templates/scene_stat.html.jinja2
  video_studio/templates/scene_cta.html.jinja2

STEP 1 — video_studio/design/tokens.css
Generate CSS custom properties from brand_tokens.json at build time (the Jinja template
injects them; this file is the static fallback + the reference). Define:
  --bg #F8F6F0          warm off-white canvas
  --card #FFFFFF        card surface
  --border rgba(0,0,0,0.08)
  --ink #111111         primary text
  --ink-muted #666666
  --accent #E05A36      burnt orange
  --accent-hover #CC4C29
  --highlight #16A34A    green, used ONLY for positive/verified markers
  --font-headline 'Plus Jakarta Sans', -apple-system, sans-serif
  --font-body 'Inter', -apple-system, sans-serif
  --font-code 'JetBrains Mono', monospace
  --font-hand 'Caveat', cursive
  --font-stamp 'Anton', 'Plus Jakarta Sans', sans-serif
Type scale at 1080x1920 (px): --fs-display 128, --fs-h1 96, --fs-h2 68, --fs-h3 52,
  --fs-body 40, --fs-caption 30, --fs-stamp 44, --fs-code 32.
Spacing: --sp-1 8 … --sp-12 192.
Radii: --r-sm 12, --r-md 24, --r-lg 40.
Safe areas (hard constants): --safe-top 180px, --safe-bottom 320px, --safe-side 80px.
FONT POLICY: declare the families with system fallbacks. Do NOT @import from Google Fonts
CDN in the CSS — the renderer may run with blocked outbound access and typography would
silently fall back. If webfonts are ever used they must be self-hosted under
video_studio/work/<slug>/assets/fonts/ with a documented license.

STEP 2 — video_studio/templates/composition.html.jinja2
The root template. Must emit:
  <!doctype html>
  <html lang="en" data-composition-variables='<JSON ARRAY of {id,type,label,default}>'>
  <body style="margin:0;background:{{ brand.colors.bg }}">
    <div id="root"
         data-composition-id="{{ composition_id }}"
         data-width="1080" data-height="1920"
         data-start="0" data-duration="{{ total_duration }}"
         data-has-audio="{{ 'true' if has_audio else 'false' }}"
         style="position:relative;width:1080px;height:1920px;overflow:hidden">
      {% for scene in scenes %}{% include scene.template %}{% endfor %}
    </div>
    {% if watermark %}
      <div class="watermark">{{ brand.brand.watermark }}</div>
    {% endif %}
  </body>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>window.__timelines = window.__timelines || {};</script>
  <script>{{ gsap_timeline_js }}</script>
  </html>

HARD RULES to encode as Jinja comments in the file:
  - data-start / data-duration are SECONDS.
  - data-track-index is DISPLAY-ONLY. It does NOT control paint order and does NOT prevent
    overlap. Use CSS z-index. (Write this prominently.)
  - Every timed element needs class="clip".
  - data-composition-variables on <html> is a JSON ARRAY of {id,type,label,default},
    not an object. Use |tojson on a Python list of dicts.
  - data-variable-values on a host element is a JSON OBJECT keyed by id.

Build the GSAP timeline from a Python-side `animations` list so the template stays dumb.
The emitted JS must be:
    const tl = gsap.timeline({ paused: true });
    window.__timelines["{{ composition_id }}"] = tl;
    tl.fromTo(el, {opacity:0, y:24}, {opacity:1, y:0, duration:0.45, ease:"power2.out"}, 0.0);
    ...
Each third argument is an ABSOLUTE time in SECONDS. Only animate: opacity, x, y, scale,
scaleX, scaleY, rotation, width, height, visibility.

Motion primitives (expose as Jinja macros / include partials):
  - rise:      fromTo opacity 0->1, y 24->0, 0.45 s, power2.out
  - wipe:      fromTo scaleX 0->1, transform-origin left, 0.4 s, power3.inOut
  - stampIn:   fromTo scale 1.6->1, rotation -6->0, opacity 0->1, 0.5 s, back.out(2)
  - hold:      no animation; element visible for its full duration
  - cutOut:    to opacity 0 over 0.25 s at the scene's final 0.25 s
  - counterUp: NOT supported — do not animate numeric text. Render the final value as
               static text and let the cut create the illusion. (GSAP props whitelist
               does not include text content.)

STEP 3 — SCENE TEMPLATES
All five take `scene` and `brand` and `tokens`. All respect the safe areas. All use
class="clip" plus data-start / data-duration in seconds.

scene_title.html.jinja2
  - 128 px headline in --font-headline, weight 800, letter-spacing -0.03em, line-height 0.95
  - optional 40 px sub-line in --ink-muted
  - accent rule: 8 px x 96 px bar in --accent above the headline
  - entrance: rise at scene start, hold, cutOut at scene end
  - Never exceed 3 text lines. Headline auto-shrinks via a Jinja `len` check:
    <=28 chars -> --fs-display; <=52 -> --fs-h1; else --fs-h2.

scene_bullets.html.jinja2
  - white card, --r-lg, 1 px --border, 48 px padding, centered in the safe area
  - each bullet: --fs-h3, preceded by a 16 px square bullet in --accent
  - max 4 bullets visible; if scene has more, the template must reduce and the storyboard
    generator (PROMPT 08) must split the scene instead
  - bullets stagger in 0.08 s apart via ABSOLUTE times

scene_code.html.jinja2
  - --card background, --font-code 32 px, --r-md, 48 px padding
  - 14 px --accent left border
  - NO syntax highlighting library — inline `<span class="tok-kw">` spans injected from
    Python (PROMPT 08 does the tokenising; this template only renders)
  - max 10 lines, 76 chars per line. Overflow must ellipsize, never wrap.
  - entrance: wipe

scene_stat.html.jinja2
  - giant number in --font-stamp 160 px in --accent, centred
  - label in --fs-body --ink-muted beneath
  - a small "VERIFIED" tag in --highlight when scene.verified is true; when false, the tag
    must say "UNVERIFIED" in --ink-muted. NEVER label an unverified number as verified.
  - entrance: stampIn

scene_cta.html.jinja2
  - watermark SIGNHIFY.STUDIO in --font-stamp 44 px, letter-spacing 0.18em, --ink
  - handle @signhify.studio in --font-body 40 px --ink-muted
  - site signhify.dpdns.org 30 px --ink-muted
  - the sign-off line in --font-hand 52 px --accent, ONLY when scene.sign_off is true:
    "My name is Piyush Raj Singh. Stop posting. Start shipping."
  - a button-shaped pill: background --accent, colour #FFFFFF, --r-md, label from
    brand.cta.button_text ("FOLLOW SIGNHIFY.STUDIO FOR MORE →")
  - entrance: rise

STEP 4 — WATERMARK
Always present on the CTA scene. Text SIGNHIFY.STUDIO. Bottom-left, inside the 320 px
bottom safe area, 60 px from the left edge. Never placed where Instagram's UI will cover it.

STEP 5 — ACCESSIBILITY (this is what `npx hyperframes check` grades)
  - Every text/background pair must clear WCAG AA (4.5:1 for body, 3:1 for large).
  - Verify these known-good pairs from the brand palette:
      #111111 on #F8F6F0  -> very high contrast, SAFE
      #FFFFFF on #E05A36  -> compute; if below 4.5:1 for small text, use it only at
                             --fs-h3 or larger (large-text threshold is 3:1).
      #666666 on #F8F6F0  -> compute; if below 4.5:1, only use at --fs-caption+ or
                             darken to #555555. Report the actual ratio.
      #16A34A on #F8F6F0  -> verify; if below 3:1, never use as text on bg, only as a
                             filled badge with white text.
  Write the computed ratios into a comment block in tokens.css. Do not guess ratios —
  compute them.

STEP 6 — PROVE IT RENDERS
Generate a fixed demo project from these templates:
  video_studio/work/_design-demo/
Then run, from D:\Autogram:
  cd video_studio/work/_design-demo ; npx hyperframes check ; cd D:\Autogram
PASS = "0 errors, 0 warnings" and all text checks pass WCAG AA.
Then render at draft:
  npx hyperframes render -f 30 -q draft -w 4 -o video_studio/output/_design-demo/demo.mp4
ffprobe it. 1080x1920, 30/1, h264, yuv420p. Extract 5 frames (one per scene type),
report mean luma for each (all must be >= 8).

STEP 7 — WRITE THE NOTES
Append to docs/video-studio/BRAND_IDENTITY.md a new section:
  ## Design System Implementation
listing: file paths, the type scale, the 5 scene types, the 5 motion primitives, the WCAG
ratio table, and the reason numeric text is never animated.

RULES
  - No hardcoded hex in any .jinja2 file. All colours come from brand_tokens.json via
    {{ brand.colors.* }} or CSS variables.
  - No CDN font imports.
  - Never render a number as VERIFIED unless the source data marks it verified.
  - Never use a banned phrase in any placeholder/example copy.
  - Do not modify _smoke/, src/, orchestrator.py, or dashboard_api.py.

ACCEPTANCE
  - 7 files created (tokens.css + 6 templates).
  - design-demo passes `npx hyperframes check` with 0 errors / 0 warnings + WCAG AA.
  - demo.mp4 ffprobes to 1080x1920 @30fps h264 yuv420p.
  - 5 frames extracted, all mean luma >= 8.
  - No hardcoded hex in any template.
  - The data-track-index and absolute-time rules appear as Jinja comments in
    composition.html.jinja2.
````

## 6. Expected output files
- `video_studio/design/tokens.css`
- `video_studio/templates/composition.html.jinja2`
- `video_studio/templates/scene_title.html.jinja2`
- `video_studio/templates/scene_bullets.html.jinja2`
- `video_studio/templates/scene_code.html.jinja2`
- `video_studio/templates/scene_stat.html.jinja2`
- `video_studio/templates/scene_cta.html.jinja2`
- `video_studio/work/_design-demo/` (throwaway project)
- `video_studio/output/_design-demo/demo.mp4`
- Appended `## Design System Implementation` section in `docs/video-studio/BRAND_IDENTITY.md`

## 7. Execution requirements
- Python (Jinja2 from the venv) renders; `npx hyperframes` validates and renders.
- `-q draft -w 4`. Never `--docker`, never `-q high`.
- No CDN fonts, no network at render time.

## 8. Dependencies on earlier prompts
- PROMPT 01 (animation contract), PROMPT 02 (tokens + brand rules),
  PROMPT 05 (working composition to imitate).

## 9. Acceptance criteria
- All 7 design files exist.
- `_design-demo` passes `npx hyperframes check` with zero errors and zero warnings.
- `demo.mp4` is 1080×1920 @30 fps H.264 yuv420p, verified by ffprobe.
- 5 frames extracted, mean luma ≥ 8 each.
- Computed WCAG ratios documented, not guessed.
- Zero hardcoded hex values in `.jinja2` files.

## 10. Verification instructions
```powershell
Get-ChildItem video_studio\templates\*.jinja2 | Measure-Object | Select-Object -ExpandProperty Count
Select-String -Path video_studio\templates\*.jinja2 -Pattern "#[0-9A-Fa-f]{6}"   # must be empty
ffprobe -v error -show_entries stream=width,height,r_frame_rate,pix_fmt,codec_name -of json video_studio\output\_design-demo\demo.mp4
Set-Location video_studio\work\_design-demo ; npx hyperframes check ; Set-Location D:\Autogram
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `check` reports contrast warnings | Muted/accent pair below AA | Read the computed ratios in tokens.css; darken the text or promote to large size. |
| Jinja `tojson` emits an object not an array | Variables built as a dict | Must be a Python **list** of dicts on `<html>`; dicts only for `data-variable-values`. |
| Scenes stack on top of each other | Agent used `data-track-index` | Display-only. Set explicit CSS `z-index` per scene index. |
| Animation appears at the wrong moment | Third arg treated as relative | It is ABSOLUTE seconds. Recompute from `scene.start_s`. |
| Frames blank / black | `window.__timelines` key mismatch | Must equal the root `data-composition-id` exactly. |
| GSAP does not fire | Timeline not paused | Must be `gsap.timeline({paused:true})` and assigned to `window.__timelines[id]`. |
| Text wraps/overflows vertically | Headline too long | Auto-shrink tiers in `scene_title`; PROMPT 08 must also cap `headline` length. |
| Fonts differ from design | CDN import blocked | Expected. System fallbacks are the design. Do not add CDN fonts. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 07 — AI Content Research and Script Generation
# ═════════════════════════════════════════════════════════════════════════════

`[RESEARCH]`

## 1. Prompt title
PROMPT 07 — AI Content Research and Script Generation

## 2. Intended purpose
Turn a **topic** (or a product URL) into a validated `brief.json` plus a human-readable
`script.md` — the two artifacts every downstream stage consumes. Also produce the reusable
system prompt that will do this at scale, with the banned-phrase enforcement and the
no-fabrication rules baked in.

## 3. When to use it
- After PROMPT 06 (the layouts are known, so copy can be written to fit them).
- Every time a new video is commissioned. This is the entry point for PROMPT 18.
- To regenerate copy without re-rendering: safe to re-run at any time.

## 4. Required inputs
- `video_studio/brand_tokens.json` + `docs/video-studio/BRAND_IDENTITY.md` (PROMPT 02)
- `video_studio/templates/*.jinja2` (PROMPT 06) — read them to learn the length limits
- `data/brand.json` (canonical banned phrases)
- Optionally a source URL for the topic

## 5. Exact copy-paste prompt text

````
You are the content engine for Signhify Studio's Instagram Reels.
Working directory: D:\Autogram

INPUT (read these first):
  video_studio/brand_tokens.json
  video_studio/templates/scene_title.html.jinja2      (headline length tiers)
  video_studio/templates/scene_bullets.html.jinja2    (max 4 bullets, per-bullet width)
  video_studio/templates/scene_code.html.jinja2       (max 10 lines, 76 chars)
  video_studio/templates/scene_cta.html.jinja2        (watermark + handle + site)
  data/brand.json                                     (avoid[] = the 16 banned phrases)

TASK — produce three things:
  (a) video_studio/prompts/script.md    the reusable system prompt
  (b) video_studio/briefs/<slug>.json   one production brief, for the topic given below
  (c) video_studio/work/<slug>/script.md  the human-readable script for that brief

SLUG for this run: {{SLUG}}
TOPIC for this run: {{TOPIC}}
SOURCE URL (may be empty): {{SOURCE_URL}}

STEP 1 — WRITE video_studio/prompts/script.md
This is the permanent system prompt used for every future video. It must instruct an LLM to
produce a brief matching this exact contract:

  BRIEF SCHEMA (all fields required unless marked optional):
    slug        ^[a-z0-9][a-z0-9-]{1,60}$       lowercase, hyphenated, == the folder name
    topic       10-140 chars
    pillar      one of: FOSS SaaS Alternatives | Trending GitHub Spotlight |
                Local AI & Edge Compute | Developer Power Tools & CLI |
                Self-Hosted Architecture | Open Source Economics & Contrarian
    hook        <= 90 chars      — the line on screen for the first 1.5 s
    key_points  array of 3-6 strings, each <= 140 chars
    cta         <= 120 chars
    duration_s  int 15..60
    aspect      "9:16"  (only supported value)
    source_url  URL or null
    language    "en"
    narration   {enabled: bool, voice: str, tone: str} or null
  OPTIONAL: music {url, gain 0..1, duck_narration}, overlay_cta (default true),
            sign_off (default true), priority (int 1..5, default 3), notes (string)

  HARD CONSTRAINTS the prompt must state:
    - The hook must land inside 1.5 seconds and create a concrete tension. No throat-clearing.
      Forbidden openers: "In this video", "Let's dive in", "Today we will", "Hey guys".
    - Every key_point must be independently checkable. If you cannot verify it, either drop
      it or mark it unverified in `notes`.
    - ZERO fabrication. Never invent: a statistic, a benchmark number, a pricing tier, a
      customer name, a testimonial, a user count, a revenue figure, a feature.
    - If a number is required and you do not have a source, do NOT include the number.
      Write the claim without it.
    - BANNED PHRASES (16) — never appear anywhere in the brief or the script:
      generic hype, fake urgency, unsupported statistics, overused motivational language,
      keyword stuffing, game-changer, unlock the power of, in today's fast-paced world,
      dive into, at its core, seamless, robust, revolutionary tool, next-gen AI,
      ultimate secret, must-have app.
    - VOICE: authoritative, architectural, hyper-practical, zero-fluff, contrarian,
      open-source-first. Short sentences. Specific nouns. No hedging adverbs.
    - Length caps exist because of the layout templates. Respect them exactly.
    - Output raw JSON only, no markdown fence, no commentary.

STEP 2 — PRODUCE THE BRIEF for {{TOPIC}}
Apply the system prompt. Then validate it yourself with a script:
  write a throwaway python check that asserts:
    - slug regex matches
    - len(topic) in 10..140, len(hook) <= 90, len(cta) <= 120
    - 3 <= len(key_points) <= 6, each <= 140 chars
    - 15 <= duration_s <= 60, aspect == "9:16"
    - pillar is one of the 6
    - NONE of the 16 banned phrases appears in topic/hook/key_points/cta (case-insensitive)
  Print PASS/FAIL per rule. If any rule fails, FIX THE COPY and re-check. Loop until green.
  Do not weaken a rule to make it pass.

STEP 3 — RESEARCH (only if SOURCE_URL is non-empty)
Attempt to fetch it. Record in `notes`:
  - the URL, the UTC timestamp, and whether the fetch succeeded
  - 3-5 facts extracted, each quoted or closely paraphrased from the page
  - an explicit VERIFIED / UNVERIFIED label per fact
If the fetch fails or is blocked, write exactly:
  "ACCESS LIMIT: <url> unreachable at <UTC timestamp>. Facts below are unverified."
Do not substitute recalled knowledge and present it as verified. Never fabricate a fact
about a third-party product.

STEP 4 — PRODUCT FACTS
The only product you may describe is Signhify, using ONLY these verified facts:
  - "Signhify Website Builder from a Single Prompt"
  - prompt -> scroll-reactive site with cinematic video, imagery, motion -> live URL in minutes
  - mechanism: ~8s cinematic video -> hundreds of frames -> native browser scroll replays them
    as 3D parallax. Product's own words: "No WebGL, no Three.js, no code - just native
    browser scroll with buttery-smooth frame interpolation."
  - features: Multi-Video Continuation, Full-Stack Export (ZIP with frontend + backend
    starter incl. Express API), Iterative Chat Editing, Product Injection, FPS 10-40
  - specs: 400+ frames/site, ~8s video, 10-40 FPS, ZIP deployable
  - pricing: Starter $5/mo (5 credits), Pro $50/mo (75), Studio $100/mo (125, "Most
    Chosen"), Enterprise $200/mo (300); annual saves 20%
  - founder: Piyush Raj Singh, AI systems engineer, Varanasi, India, Registered MSME (UDYAM)
Anything beyond this list is fabrication. If you want to state something else, leave it out.

STEP 5 — WRITE video_studio/work/<slug>/script.md
Human-readable, with these sections:
  # <title>
  ## Hook (0:00-0:01.5)
     the on-screen line, then the narration line
  ## Scene 2 ... Scene N
     for each: TIME RANGE / TYPE (title|bullets|code|stat|cta) /
               ON-SCREEN TEXT (exactly what renders) / NARRATION (what is spoken) /
               SOURCE (where the claim came from, or "UNVERIFIED")
  ## Caption (Instagram)
     first line as a standalone hook, blank line, body, blank line, hashtags
  ## Hashtags
     8-14 tags. Mix broad + niche. No banned phrases. No #gamechanger, no #seamless,
     no #nextgenai, no #unlockthepower.
  ## CTA
     from brand.cta — handle @signhify.studio, site signhify.dpdns.org
  ## Sign-off (final frame only)
     "My name is Piyush Raj Singh. Stop posting. Start shipping."
  ## Verification Notes
     every claim with its source; every ACCESS LIMIT encountered, verbatim

STEP 6 — BANNED-PHRASE SWEEP (mandatory, mechanical)
Run a script over script.md AND brief.json that searches for all 16 banned phrases,
case-insensitive, and also for common variants:
  "game changing", "game-changing", "revolutionary", "cutting-edge", "seamlessly",
  "unlock", "dive into", "at its core", "next gen", "next-gen", "must have", "must-have",
  "in today's", "ultimate secret", "power of"
Print the full scan report. It must come back clean. Fix and re-scan until clean.

STEP 7 — REPORT
Print: the brief JSON, the validation PASS/FAIL table, and the banned-phrase sweep result.

RULES
  - Never fabricate a capability, metric, testimonial, customer result, or revenue.
  - Never print or write an API key. None are needed for this prompt.
  - Never claim the script was fact-checked against a source you could not read.
  - Respect all 16 banned phrases in every string you write, including this report.
  - Do not create .py pipeline modules here. PROMPT 08 implements the validators.

ACCEPTANCE
  - video_studio/prompts/script.md exists and states the full brief contract + constraints.
  - video_studio/briefs/<slug>.json exists, parses, and passes every validation rule.
  - video_studio/work/<slug>/script.md exists with all 8 sections.
  - Banned-phrase sweep on both files: 0 hits, including the variant list.
  - Every factual claim carries a SOURCE line or the literal word UNVERIFIED.
````

## 6. Expected output files
- `video_studio/prompts/script.md`
- `video_studio/briefs/<slug>.json`
- `video_studio/work/<slug>/script.md`

## 7. Execution requirements
- Python (`.venv\Scripts\python.exe`) for the validation and sweep scripts.
- Network fetch only if `SOURCE_URL` is non-empty; failure is recorded, not bypassed.
- No installs.

## 8. Dependencies on earlier prompts
- PROMPT 02 (tokens, brand, banned phrases), PROMPT 06 (layout length limits).

## 9. Acceptance criteria
- Brief validates: slug regex, topic 10–140, hook ≤ 90, cta ≤ 120, 3–6 key_points each
  ≤ 140, duration 15–60, aspect `9:16`, pillar from the 6.
- Banned-phrase sweep on brief + script returns 0 hits across the 16 phrases and the
  variant list.
- Every claim in script.md has a SOURCE or is labelled UNVERIFIED.
- Sign-off appears exactly once, on the final frame.

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -c "import json;b=json.load(open('video_studio/briefs/<slug>.json',encoding='utf-8'));print(b['slug'],b['duration_s'],len(b['key_points']))"
Select-String -Path video_studio\work\<slug>\script.md -Pattern "game-changer|unlock the power|dive into|at its core|seamless|robust|next-gen|revolutionary tool|ultimate secret|must-have|fast-paced world" -CaseSensitive:$false
Select-String -Path video_studio\work\<slug>\script.md -Pattern "UNVERIFIED|SOURCE"
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Brief fails `hook <= 90` | Hook written as a paragraph | Rewrite as one line, ≤ 90 chars. The cap is the layout, not a preference. |
| Banned-phrase sweep finds "seamless" | Came from product copy | Rewrite. Even if the product uses the word, Signhify's own voice bans it. |
| Agent invents a benchmark | "just to make it concrete" | Delete the number. Never fabricate a statistic. |
| Agent states IG follower counts | Account was blocked | Delete. Unverified. Label ACCESS LIMIT instead. |
| Key point is vague filler | Length-cap pressure | Cut it. 3 real points beat 6 padded ones. Split into a second video instead. |
| Fetch blocked | Network restriction | Record ACCESS LIMIT verbatim; proceed with UNVERIFIED claims or drop them. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 08 — Storyboard and Timeline Generation
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]`

## 1. Prompt title
PROMPT 08 — Storyboard and Timeline Generation

## 2. Intended purpose
Implement `video_studio/storyboard.py`: the deterministic bridge from a validated brief to a
timed scene list. Every duration, every `start_s`, every z-index, and every absolute GSAP
keyframe time is computed here — no guessing downstream.

## 3. When to use it
- After PROMPT 07 (a real brief exists).
- Re-runnable at any time; pure function, no side effects beyond writing `storyboard.json`.
- Before PROMPT 09 (assets) and PROMPT 10 (compose).

## 4. Required inputs
- `docs/video-studio/ARCHITECTURE.md` (PROMPT 03) — schemas and invariants
- `video_studio/briefs/<slug>.json` + `video_studio/work/<slug>/script.md` (PROMPT 07)
- `video_studio/brand_tokens.json` (PROMPT 02)
- `video_studio/templates/*.jinja2` (PROMPT 06) — to respect layout limits

## 5. Exact copy-paste prompt text

````
You are implementing the storyboard generator for the video engine.
Working directory: D:\Autogram

READ FIRST:
  docs/video-studio/ARCHITECTURE.md          (sections: Brief Schema, Storyboard Schema)
  video_studio/brand_tokens.json
  video_studio/templates/scene_*.html.jinja2
  video_studio/briefs/<slug>.json
  video_studio/work/<slug>/script.md
Python: .venv\Scripts\python.exe (3.14.7). No new pip installs.

CREATE:
  video_studio/__init__.py
  video_studio/brief.py       brief loading + validation
  video_studio/storyboard.py  brief -> storyboard

REQUIREMENT 1 — video_studio/brief.py
  load_brief(path) -> dict
  validate_brief(brief) -> list[str]      # empty list == valid
  BriefError(Exception)
Validation rules (exit code 2 on failure, printing the offending JSON path):
  - required keys present: slug, topic, pillar, hook, key_points, cta, duration_s,
    aspect, source_url, language, narration
  - slug matches ^[a-z0-9][a-z0-9-]{1,60}$
  - 10 <= len(topic) <= 140
  - len(hook) <= 90
  - len(cta) <= 120
  - 3 <= len(key_points) <= 6, each len <= 140
  - 15 <= duration_s <= 60
  - aspect == "9:16"
  - pillar in brand_tokens.json pillars
  - none of the 16 banned phrases (case-insensitive) in topic, hook, key_points, cta
Never auto-fix. Never silently truncate. Report and exit 2.

REQUIREMENT 2 — video_studio/storyboard.py
  build_storyboard(brief) -> dict

Output schema (write to video_studio/work/<slug>/storyboard.json):
  { "slug", "duration_s", "fps": 30, "width": 1080, "height": 1920,
    "scenes": [ { "index", "type", "start_s", "duration_s", "headline", "body",
                  "code", "bg", "accent", "narration", "transition", "z_index",
                  "verified" } ] }

SCENE BUDGET RULES (derived from the layout templates, not invented):
  - hook:    1.5-2.5 s, 1 line, headline <= 28 chars at --fs-display
  - title:   2.5-4.0 s, headline <= 52 chars
  - bullets: 3.5-6.0 s, max 4 bullets each <= 140 chars
             if len(key_points) > 4 -> SPLIT across two bullets scenes, never truncate
  - code:    3.5-6.0 s, max 10 lines, <= 76 chars/line
  - stat:    2.0-3.0 s, one number + one label
  - cta:     3.0-4.0 s, always last when overlay_cta or sign_off is true
HARD INVARIANTS — compute and then assert:
  1. scenes[0].type == "hook"
  2. scenes[-1].type == "cta"   (when overlay_cta or sign_off)
  3. 3 <= len(scenes) <= 9
  4. every scene 0.8 s <= duration_s <= 12 s
  5. scenes[0].start_s == 0.0
  6. scenes[i].start_s == round(scenes[i-1].start_s + scenes[i-1].duration_s, 3)
  7. abs(sum(durations) - brief.duration_s) <= 0.05
  8. z_index == index (CSS stacking order — this is what actually controls paint order)
DISTRIBUTION ALGORITHM (deterministic, no RNG, no LLM call):
  - Reserve hook_d = clamp(1.5, 2.0) and cta_d = clamp(3.0, 4.0).
  - Remaining = duration_s - hook_d - cta_d. If Remaining < 1.5, raise StoryboardError
    naming the brief (the brief is too short for a hook AND a CTA).
  - Split Remaining across body scenes proportionally to their text weight
    (bullet count * 140 + headline len), then clamp each to its type's range.
  - Fix any rounding drift on the LAST body scene so the sum is exact.
  - Print the resulting timeline as a table to stdout.

TRANSITIONS:
  "cut" (default), "fade", "slide_up", "wipe". These are consumed by PROMPT 10 to choose
  the GSAP entrance primitive. Do NOT emit GSAP code here.

REQUIREMENT 3 — a self-check
Add `if __name__ == "__main__":` with an assert-based demo:
  - Build a synthetic valid brief (slug "demo-hook-test", topic "Testing the storyboard
    generator", pillar "Local AI & Edge Compute", hook "One prompt. One site.",
    key_points x3, cta "Follow @signhify.studio", duration_s 30, aspect "9:16").
  - Assert all 8 invariants.
  - Build a 5-key_point brief and assert it produces TWO bullets scenes, not one.
  - Build a duration_s=15 brief with overlay_cta=True and assert StoryboardError.
  - Assert a brief containing the banned phrase "game-changer" fails validation.
  Print "STORYBOARD SELF-CHECK PASS".

REQUIREMENT 4 — RUN IT
  .venv\Scripts\python.exe -m video_studio.storyboard video_studio/briefs/<slug>.json
Write video_studio/work/<slug>/storyboard.json. Print the timeline table.
Then validate the emitted JSON against the 8 invariants again, from the file.

RULES
  - Pure stdlib + jinja2 (already present). No new dependencies.
  - No randomness. No LLM calls. The storyboard must be reproducible byte-for-byte.
  - z_index comes from the scene index. data-track-index is DISPLAY-ONLY in HyperFrames
    and does NOT control stacking — write that as a comment in storyboard.py.
  - All GSAP times are ABSOLUTE SECONDS. Do not emit relative ("+=0.4") timings.
  - Respect the 16 banned phrases if you add any example strings.
  - Do not modify src/, orchestrator.py, dashboard_api.py, or _smoke/.

ACCEPTANCE
  - video_studio/brief.py and video_studio/storyboard.py exist and import cleanly.
  - `python -m video_studio.storyboard <brief>` writes a valid storyboard.json.
  - The 8 invariants hold on the emitted file.
  - A 5-key_point brief yields 2 bullets scenes.
  - A too-short brief raises StoryboardError.
  - A banned phrase in the brief fails validation.
  - "STORYBOARD SELF-CHECK PASS" printed.
````

## 6. Expected output files
- `video_studio/__init__.py`
- `video_studio/brief.py`
- `video_studio/storyboard.py`
- `video_studio/work/<slug>/storyboard.json`

## 7. Execution requirements
- `.venv\Scripts\python.exe` only. Stdlib + already-installed Jinja2.
- Deterministic — same brief in, byte-identical storyboard out.
- No network. No installs.

## 8. Dependencies on earlier prompts
- PROMPT 03 (schemas), PROMPT 07 (the brief being transformed).

## 9. Acceptance criteria
- Both modules import without error.
- Emitted `storyboard.json` passes all 8 invariants.
- 5 key points → 2 bullets scenes (no truncation).
- `duration_s=15` with CTA → `StoryboardError`.
- Banned phrase in brief → validation failure listing the field.
- `STORYBOARD SELF-CHECK PASS` printed.

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -m video_studio.storyboard video_studio\briefs\<slug>.json
.venv\Scripts\python.exe -c "import json;s=json.load(open('video_studio/work/<slug>/storyboard.json',encoding='utf-8'));sc=s['scenes'];assert sc[0]['type']=='hook';assert abs(sum(c['duration_s'] for c in sc)-s['duration_s'])<=0.05;assert all(0.8<=c['duration_s']<=12 for c in sc);print('INVARIANTS OK',len(sc),'scenes')"
.venv\Scripts\python.exe video_studio\storyboard.py
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `sum(durations) != duration_s` | Rounding drift | Apply leftover to the last body scene. Assert `<= 0.05`. |
| Only 4 bullets shown, 5 given | Single bullets scene | Split into two bullets scenes. PROMPT 06 caps display at 4. |
| `StoryboardError` on a valid brief | Remaining < 1.5 s | The brief genuinely cannot fit hook+CTA. Report the minimum viable duration. |
| Non-reproducible output | RNG or dict ordering | Remove `random`; sort keys in `json.dump`. |
| Key point text cut off | No per-type length clamp | Enforce 140 chars per bullet at generation, not at render. |
| Z-order wrong in preview | Used `data-track-index` | Display-only. `z_index` must be emitted and applied as CSS. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 09 — Asset Generation and Management
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]`

## 1. Prompt title
PROMPT 09 — Asset Generation and Management

## 2. Intended purpose
Implement `video_studio/assets.py`: resolve every image, font, audio, and code snippet a
composition needs into `work/<slug>/assets/`, and write an `asset_manifest.json` that records
**where every byte came from**. Provenance is the point — a Reel with an untraceable image
is a liability.

## 3. When to use it
- After PROMPT 08 (a storyboard exists and names what it needs).
- Before PROMPT 10 (composition references asset paths).
- Whenever brand assets change.

## 4. Required inputs
- `video_studio/work/<slug>/storyboard.json` (PROMPT 08)
- `video_studio/brand_tokens.json` (PROMPT 02)
- `assets/signhify-logo-vector.png`, 9 × `assets/ig_signhify.studio_*.jpg` (PROMPT 00 confirmed)
- `video_studio/prompts/script.md` (PROMPT 07)

## 5. Exact copy-paste prompt text

````
You are implementing asset resolution for the video engine.
Working directory: D:\Autogram
Python: .venv\Scripts\python.exe (3.14.7). Pillow is NOT installed — check before assuming
you have an image library. If you need image work that stdlib cannot do, report it as a
BLOCKER rather than installing anything.

READ FIRST:
  video_studio/brand_tokens.json
  video_studio/work/<slug>/storyboard.json
  video_studio/prompts/script.md

CONFIRMED BRAND ASSETS (verify existence, do not assume):
  assets/signhify-logo-vector.png
  assets/ig_signhify.studio_*.jpg   (exactly 9 files, 1080x1350 — these are CAROUSEL
                                     images, NOT Reel covers. Never use them as a
                                     1080x1920 cover.)
Verify with:
  Test-Path assets\signhify-logo-vector.png
  Get-ChildItem assets -Filter "ig_signhify*" | Measure-Object

CREATE: video_studio/assets.py
  resolve_assets(storyboard, brief, out_dir) -> dict   # writes asset_manifest.json
  AssetError(Exception)

RESOLUTION ORDER for every asset reference (first match wins):
  1. scene["code"]       -> assets/snippets/<slug>-<index>.txt   (source: generated)
  2. scene["image"]      -> if present in assets/ use it; else BLOCKER, do not invent
  3. watermark / logo    -> assets/signhify-logo-vector.png (source: brand)
  4. brand pattern bg    -> generate a CSS gradient in the template, NOT an image
                             (source: generated-css). Zero network cost.
  5. narration audio     -> produced by PROMPT 11; if absent, assets.py records
                             { "status": "deferred", "producer": "audio.py" } and
                             does NOT fail. (Kokoro TTS is NOT installed on this machine.)
  6. music               -> only if brief.music.url is set AND network is reachable.
                             NEVER bundle licensed music by default. If unreachable, record
                             a BLOCKER, do not substitute.

HARD RULE — NO PLACEHOLDER IMAGES.
There is no stock-photo fallback. If a required image cannot be resolved, the scene must
degrade to a text-only layout and asset_manifest.json must record
  { "degraded": true, "reason": "<what was missing>" }.
A generated gradient / typographic scene is always better than a downloaded placeholder.

MANIFEST SCHEMA — video_studio/work/<slug>/asset_manifest.json:
{
  "slug": "<slug>",
  "generated_utc": "<ISO8601>",
  "assets": [
    {
      "id": "watermark",
      "path": "assets/signhify-logo-vector.png",
      "kind": "image|font|audio|text|video",
      "source": "brand|generated|downloaded|deferred",
      "origin": "assets/signhify-logo-vector.png" | "url:<...>" | "generated by <module>",
      "license": "owned by Signhify Studio" | "CC0" | "UNKNOWN-REVIEW",
      "sha256": "<64 hex>",
      "bytes": 12345,
      "used_by_scenes": [0, 4],
      "notes": ""
    }
  ],
  "blockers": [ { "scene_index": 3, "kind": "image", "reason": "...", "degraded": true } ],
  "total_bytes": 123456
}
Every asset MUST have a sha256. Compute with hashlib (stdlib). An asset without a hash is
a bug, not an omission.

IMPLEMENTATION NOTES
  - Copy brand assets into work/<slug>/assets/ so the HyperFrames project is self-contained.
  - Never reference a path outside work/<slug>/ from index.html.
  - If a font is ever added, it MUST be a self-hosted woff2 under assets/fonts/ with a
    recorded license. Do NOT use a CDN font URL. Renderers may have no outbound network.
  - For code snippets, tokenise on the Python side (keywords, strings, comments, numbers)
    and let the scene_code template emit spans. No syntax-highlighting library.
  - asset_manifest.json must be written atomically (write .tmp, then os.replace).

SELF-CHECK (if __name__ == "__main__":)
  - resolve assets for the current storyboard
  - assert every entry has a sha256 of length 64
  - assert watermark source == "brand" and its bytes match assets/signhify-logo-vector.png
  - assert no entry's path starts with ".." (no path traversal)
  - assert blockers list is a list (empty is fine)
  - assert no CDN URL appears anywhere in asset_manifest.json (assert "http" not in
    any origin except explicit "url:" entries the owner approved)
  Print "ASSET SELF-CHECK PASS" and the total byte count.

RUN IT:
  .venv\Scripts\python.exe -m video_studio.assets video_studio/work/<slug>/storyboard.json
Print the manifest summary: count by source, total bytes, blockers.

RULES
  - Never fabricate an image, a URL, or a license. Unknown license -> "UNKNOWN-REVIEW".
  - Never download stock photography. There is no licensed stock in this repo.
  - Never install Pillow or any package. Report blockers instead.
  - Never use the 9 carousel JPGs (1080x1350) as 1080x1920 cover art.
  - Never put an API key in the manifest, a script, or a comment.

ACCEPTANCE
  - video_studio/assets.py exists and imports cleanly.
  - asset_manifest.json written for the current slug.
  - Every entry has sha256 (64 hex) and bytes.
  - "ASSET SELF-CHECK PASS" printed.
  - Zero CDN URLs in the manifest.
  - Missing images degrade to text-only scenes with a recorded blocker, not a placeholder.
````

## 6. Expected output files
- `video_studio/assets.py`
- `video_studio/work/<slug>/assets/` (copied + generated assets)
- `video_studio/work/<slug>/asset_manifest.json`

## 7. Execution requirements
- `.venv\Scripts\python.exe`. Stdlib `hashlib`, `shutil`, `json`, `pathlib`, `os`.
- No package installs — report blockers instead.
- Network only for explicitly-approved `brief.music.url`.

## 8. Dependencies on earlier prompts
- PROMPT 08 (storyboard), PROMPT 02 (brand assets), PROMPT 07 (script for code snippets).

## 9. Acceptance criteria
- `assets.py` imports and runs.
- Manifest has a sha256 and byte count for every entry.
- Self-check passes and prints `ASSET SELF-CHECK PASS`.
- No CDN URLs; no path traversal; no fabricated licenses.
- Missing images → recorded blocker + text-only scene.

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -m video_studio.assets video_studio\work\<slug>\storyboard.json
.venv\Scripts\python.exe -c "import json;m=json.load(open('video_studio/work/<slug>/asset_manifest.json',encoding='utf-8'));assert all(len(a['sha256'])==64 for a in m['assets']);print(len(m['assets']),'assets, all hashed')"
Get-ChildItem video_studio\work\<slug>\assets -Recurse | Measure-Object -Property Length -Sum
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Manifest entry has no `sha256` | Deferred/placeholder path skipped hashing | Hash on write, always. An unhashed asset is a bug. |
| Logo not found at `assets/` | Path drift | Confirm with `Test-Path`. Do not generate a substitute logo. |
| Cover ends up 1080×1350 | Carousel JPG used | Carousels are 1080×1350; covers are 1080×1920. Never cross them. |
| Agent "installs Pillow to fix it" | Scope creep | Reject. Report the blocker; PROMPT 12 can degrade. |
| Music URL unreachable | Network restriction | Record blocker. Do not substitute a random track. |
| `url:` entry appears unprompted | Agent browsed for stock | Delete. Only the brief's explicit `music.url` is approved. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 10 — Automated Video Production
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]` `[RENDERS VIDEO]`

## 1. Prompt title
PROMPT 10 — Automated Video Production

## 2. Intended purpose
Implement composition emission and rendering: `video_studio/compose.py` and
`video_studio/render.py`. This prompt produces the **first real `reel.mp4`** from a brief,
end to end, with the HyperFrames QA gate enforced.

## 3. When to use it
- After PROMPT 09 (assets resolved).
- The first execution of this prompt is the pipeline's milestone moment.
- Re-run for every new video, and for any iteration on layout or motion.

## 4. Required inputs
- `docs/video-studio/ARCHITECTURE.md` (PROMPT 03)
- `docs/video-studio/HYPERFRAMES_RESEARCH.md` (PROMPT 01)
- `video_studio/templates/*.jinja2` + `design/tokens.css` (PROMPT 06)
- `video_studio/storyboard.json` + `asset_manifest.json` (PROMPTs 08, 09)
- `npx hyperframes` 0.8.58 on PATH via the repo root

## 5. Exact copy-paste prompt text

````
You are implementing composition emission and rendering. This prompt must produce a real
1080x1920 MP4. Working directory: D:\Autogram
Python: .venv\Scripts\python.exe (3.14.7). hyperframes 0.8.58 via `npx hyperframes`.

CREATE:
  video_studio/compose.py    storyboard + templates -> work/<slug>/index.html + hyperframes.json
  video_studio/render.py     runs `npx hyperframes check` then `npx hyperframes render`

HYPERFRAMES CONTRACT — implement exactly, do not improvise:
  - Root element: data-composition-id, data-width="1080", data-height="1920",
    data-start="0", data-duration="<total>".
  - data-start / data-duration are in SECONDS.
  - Every timed element has class="clip".
  - data-track-index is DISPLAY-ONLY for the Studio timeline. It does NOT control paint
    order and does NOT prevent overlap. Use CSS z-index. Emit z_index from the storyboard
    as inline `style="z-index: N"`. Do NOT rely on data-track-index for stacking.
  - GSAP: `const tl = gsap.timeline({ paused: true });`
          `window.__timelines["<root data-composition-id>"] = tl;`
          Third argument to .to()/.fromTo() is ABSOLUTE SECONDS.
          tl.fromTo(el, {opacity:0,y:24}, {opacity:1,y:0,duration:0.45,ease:"power2.out"}, 1.2)
          Animating a scene that begins at start_s=1.2 -> use 1.2, not "+=1.2".
  - Supported animated properties ONLY: opacity, x, y, scale, scaleX, scaleY, rotation,
    width, height, visibility. Emit nothing else. Never animate text content or numbers.
  - data-composition-variables on <html> = JSON ARRAY of {id,type,label,default}.
    Build it as a Python LIST and render with |tojson.
  - data-variable-values on a host element = JSON OBJECT keyed by id.
  - Brand variables to expose: accentColor (default #E05A36), bgColor (#F8F6F0),
    inkColor (#111111), highlightColor (#16A34A), mutedColor (#666666).
  - Media (if narration exists): <video data-media-start="0" data-volume="1"
    data-has-audio="true" class="clip" ...>. data-volume: 1 = 0 dB, max ~3.98 (+12 dB).

COMPOSE — compose.compose(brief, storyboard, assets) -> None
  1. mkdir -p video_studio/work/<slug>/assets
  2. Write video_studio/work/<slug>/index.html from templates/composition.html.jinja2,
     including each scene template.
  3. Write video_studio/work/<slug>/hyperframes.json:
       { "name": "<slug>", "width": 1080, "height": 1920, "fps": 30,
         "duration_s": <total>, "entry": "index.html" }
  4. Write video_studio/work/<slug>/package.json:
       { "name": "<slug>", "private": true, "type": "module",
         "dependencies": { "hyperframes": "^0.8.58" } }
  5. Emit the GSAP timeline from an `animations` list built in Python. One entrance per
     scene at scene.start_s, plus a cutOut at (start_s + duration_s - 0.25).
     Transitions map: cut->rise, fade->fade, slide_up->rise with y offset, wipe->scaleX.
  6. No hardcoded hex anywhere in emitted HTML — all colours via CSS vars from tokens.css.
  7. Write index.html atomically (.tmp then os.replace).

RENDER — render.render(slug, quality="draft", fps=30, no_audio=False, dry_run=False) -> dict
  Run, cwd = D:\Autogram (hyperframes is installed at the repo root):
    STEP A — QA GATE FIRST, ALWAYS:
      subprocess.run(["npx","hyperframes","check"], cwd=work_dir, capture_output=True,
                     text=True, shell=True on Windows)
      Append stdout+stderr VERBATIM to video_studio/output/<slug>/render.log
      If the output does not contain "0 errors, 0 warnings" -> raise RenderError with the
      captured text. DO NOT RENDER. DO NOT PACKAGE. Exit code 3.
      A known-good run reported: "0 errors, 0 warnings" and "5/5 text checks pass WCAG AA".
    STEP B — RENDER:
      npx hyperframes render -f <fps> -q <draft|standard|high> -w 4
        -o <abs path>/video_studio/output/<slug>/reel.mp4
      NEVER pass --docker (Docker is not running).
      NEVER pass --gpu (no CUDA GPU on this machine).
      NEVER use -q high for iteration — it is very slow without CUDA.
      Capture stdout+stderr to render.log. Measure wall time.
    STEP C — VERIFY (do not trust the exit code alone):
      ffprobe -v error -select_streams v:0
        -show_entries stream=width,height,r_frame_rate,nb_frames,pix_fmt,codec_name
        -show_entries format=duration,size -of json <reel.mp4>
      ASSERT width==1080, height==1920, r_frame_rate=="<fps>/1",
pix_fmt=="yuv420p", codec_name=="h264",
             abs(duration - storyboard.total) <= 0.15, nb_frames within 2% of fps*duration.
      If any assertion fails -> raise RenderError, exit 1, leave render.log for debugging.
    STEP D — write video_studio/output/<slug>/manifest.json with:
      { slug, created_utc, duration_s, fps, width, height, bytes, sha256,
        qa_status: "PASS", published: false, ig_media_id: null }
      written atomically.

DRY RUN: --dry-run writes work/<slug>/index.html + hyperframes.json and renders NOTHING,
exits 0, and prints the exact commands it would have run.

EXECUTION REQUIREMENTS
  - hyperframes is invoked from D:\Autogram (repo root), NOT from work/<slug>/.
  - On Windows, subprocess needs shell=True for the npx shim.
  - Always pass `cwd=D:\Autogram` for npx, and capture both stdout and stderr.
  - Never shell-interpolate user text into a command string. Pass lists, not strings.
  - Timeout: 1800 s for render, 300 s for check. Kill and raise RenderError on timeout.

RUN IT:
  .venv\Scripts\python.exe -m video_studio.render video_studio/work/<slug>/storyboard.json --quality draft
  # (or add a thin __main__ that accepts a slug)
Then ffprobe the result yourself and print the JSON.

ACCEPTANCE
  - work/<slug>/index.html, hyperframes.json, package.json all exist and are valid.
  - index.html contains NO hardcoded hex outside the CSS variable block.
  - render.log contains the verbatim `npx hyperframes check` output showing
    "0 errors, 0 warnings".
  - video_studio/output/<slug>/reel.mp4 exists and ffprobes to 1080x1920 / <fps>/1 /
    h264 / yuv420p / duration matching the storyboard within 0.15 s.
  - manifest.json written with qa_status PASS and published false.
  - Nothing outside work/<slug>/ and output/<slug>/ was modified.

RULES
  - `npx hyperframes check` is a HARD GATE. A failing check never proceeds to render.
  - Never use --docker (Docker is not running) or --gpu (no CUDA GPU).
  - Never emit a GSAP tween on an unsupported property.
  - Never emit a relative ("+=...") third argument.
  - Never claim a render succeeded without ffprobe output in the transcript.
  - Never write or read an API key in this prompt.

DUMP index.html IN FULL when you finish, so the composition contract can be inspected.
````

## 6. Expected output files
- `video_studio/compose.py`, `video_studio/render.py`
- `video_studio/work/<slug>/index.html`, `hyperframes.json`, `package.json`
- `video_studio/output/<slug>/reel.mp4`, `render.log`, `manifest.json`

## 7. Execution requirements
- `npx hyperframes` from `D:\Autogram`. `ffprobe`/`ffmpeg` on PATH. `-w 4`, `-q draft`.
- `check` runs before `render`, always. Render timeout 1800 s, check timeout 300 s.
- Windows: `shell=True` for the npx shim; pass argument lists, never interpolated strings.

## 8. Dependencies on earlier prompts
- PROMPT 03 (contracts), PROMPT 06 (templates), PROMPT 08 (storyboard),
  PROMPT 09 (assets).

## 9. Acceptance criteria
- `index.html` emitted with the correct root attributes and no hardcoded hex.
- `render.log` shows `npx hyperframes check` → "0 errors, 0 warnings".
- `reel.mp4` ffprobes to 1080×1920, `<fps>/1`, h264, yuv420p, duration within 0.15 s.
- `manifest.json` has `qa_status: "PASS"`, `published: false`.
- Full `index.html` printed for inspection.

## 10. Verification instructions
```powershell
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,pix_fmt,codec_name -show_entries format=duration -of json video_studio\output\<slug>\reel.mp4
Select-String -Path video_studio\output\<slug>\render.log -Pattern "0 errors, 0 warnings"
Select-String -Path video_studio\work\<slug>\index.html -Pattern "paused:\s*true"
Select-String -Path video_studio\work\<slug>\index.html -Pattern "data-composition-id"
```
Independently confirm the GSAP key: every third argument in the emitted timeline must be
an absolute number greater than or equal to the scene's `start_s`, never a string starting
with `+` or `-` and never `">"`.

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `npx` not found | cwd wrong | Set `cwd=D:\Autogram`. hyperframes lives at the repo root. |
| `check` reports warnings | WCAG AA contrast or layout overflow | Fix the CSS/tokens, re-run. A warning is a failure — do not proceed. |
| Video renders black | `window.__timelines` key ≠ root `data-composition-id` | The two strings must match exactly. |
| Scenes overlap / wrong stack | `data-track-index` trusted for paint order | Display-only. Emit inline CSS `z-index` from `scene["z_index"]`. |
| Animation fires at the wrong time | Third arg treated as relative | Absolute seconds. Recompute from `start_s`. |
| `reel.mp4` is 0 bytes | Render crashed; exit code swallowed | Read `render.log`. Never trust exit code alone — ffprobe. |
| Render takes 15+ minutes | `-q high` or `--docker` | Use `-q draft -w 4`. Docker is not running; no GPU. |
| ffprobe duration ≠ storyboard total | Audio mux changed length, or a scene overran | Re-check `sum(duration_s)`; assert within 0.15 s. |
| `--docker` tried and hung | Copied from a doc example | Remove. Docker is installed but NOT running. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 11 — Narration, Sound Design, and Subtitle Synchronization
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]`

## 1. Prompt title
PROMPT 11 — Narration, Sound Design, and Subtitle Synchronization

## 2. Intended purpose
Implement `video_studio/audio.py`: produce narration, mix it with optional music, and emit
`captions.srt` synchronized to the storyboard. The pipeline must **degrade cleanly** when
neither Kokoro TTS nor whisper-cpp is installed — which is the current state of this machine.

## 3. When to use it
- After PROMPT 10 (a reel renders silently).
- Re-runnable; audio is an independent, re-runnable stage.
- Before PROMPT 13 (packaging needs captions) and PROMPT 12 (QA checks audio).

## 4. Required inputs
- `video_studio/work/<slug>/storyboard.json` (PROMPT 08)
- `video_studio/brief.json` → `narration` and `music` blocks
- FFmpeg/ffprobe 8.0.1 on PATH (verified present)
- `npx hyperframes tts` (Kokoro-82M — **NOT installed**)
- `npx hyperframes transcribe` (whisper-cpp — **NOT installed**)

## 5. Exact copy-paste prompt text

````
You are implementing narration, audio mixing, and subtitle generation.
Working directory: D:\Autogram. Python: .venv\Scripts\python.exe (3.14.7).
FFmpeg/ffprobe 8.0.1 on PATH.

KNOWN ENVIRONMENT STATE (verified — do not assume otherwise):
  - Kokoro TTS      : NOT INSTALLED. `npx hyperframes tts` will fail or require a download.
  - whisper-cpp     : NOT INSTALLED. `npx hyperframes transcribe` will fail.
  - Docker          : NOT RUNNING. Never pass --docker.
  - No CUDA GPU     : never pass --gpu.
  - Network may be restricted.

DESIGN PRINCIPLE — the pipeline MUST work with zero AI services installed.
Audio is an OPTIONAL enrichment, never a hard dependency. If narration is unavailable,
the video still renders, still passes QA, and still packages — silent.

CREATE: video_studio/audio.py
  build_audio(storyboard, brief, slug, dry_run=False) -> dict
  AudioError(Exception)
  probe_capabilities() -> dict     # which TTS/transcribe backends actually exist

STEP 1 — CAPABILITY PROBE (run this first, print the result)
  probe_capabilities() attempts, in order:
    (a) npx hyperframes tts --help          -> tts_backend = "kokoro"
    (b) shutil.which("kokoro")              -> tts_backend = "kokoro-cli"
    (c) any .wav/.mp3 already in work/<slug>/assets/audio/ -> tts_backend = "provided"
    (d) otherwise                            -> tts_backend = "none"
  Same shape for transcribe: whisper-cpp -> "provided" srt -> "none".
  Print a table. Do NOT install anything to improve the probe result.

STEP 2 — CAPTIONS (always produced, even with no TTS)
This is the path that must never fail. SRT timing comes from the storyboard, not from
speech recognition, because the storyboard IS the timing source of truth.
For each scene with non-empty `narration`:
  index: 1-based, in SRT order
  start: scene.start_s
  end:   scene.start_s + scene.duration_s
  text:  the narration, wrapped at <= 42 chars per line, max 2 lines,
        blank-line-split on sentence boundaries, no speaker labels
Output: video_studio/output/<slug>/captions.srt
FORMAT (exact, 1-indexed, comma decimal separator):
  1
  00:00:00,000 --> 00:00:02,000
  First line of narration

  2
  00:00:02,000 --> 00:00:05,500
  Second scene narration text
Validate the output: re-read the SRT and assert timestamps are monotonic non-decreasing,
the last end <= storyboard.duration_s + 0.5, and no block is empty.
Caption text MUST pass the 16-phrase banned sweep from data/brand.json.

STEP 3 — NARRATION (optional, degrades silently)
If probe_capabilities().tts_backend == "none":
  -> print "NARRATION UNAVAILABLE: no TTS backend installed (Kokoro not present)."
  -> record {"narration": {"status": "skipped", "reason": "no-tts-backend"}} in the run log
  -> DO NOT install Kokoro. DO NOT call a paid API. DO NOT block the render.
  -> return the dict with narration.status == "skipped"
If a backend exists, synthesize per-scene audio and record per-scene durations.
Report the actual synthesized durations; do not estimate. If a synthesized clip exceeds
its scene duration, log a WARNING (the storyboard timing wins — narration is trimmed to fit).

STEP 4 — MUSIC (optional, opt-in only)
Only if brief.music is non-null AND brief.music.url is a real URL AND it is reachable.
  - Download to work/<slug>/assets/audio/music.<ext> with a 60 s timeout.
  - If unreachable: log the blocker. NEVER substitute a different track.
  - Never bundle licensed music by default. Do not auto-select a royalty-free track.
  - If brief.music.duck_narration is true, use ffmpeg sidechaincompress to duck the music
    under narration. If narration was skipped, log that ducking was therefore skipped.
  - gain is 0..1 -> ffmpeg volume filter.

STEP 5 — MIX AND MUX (only if audio actually exists)
  ffmpeg -y -i reel.mp4 -i audio.wav [-i music.mp3]
    -filter_complex "[1:a]volume=1.0[n];[2:a]volume=<gain>,sidechaincompress=... [m];
                     [n][m]amix=inputs=2:duration=first:dropout_transition=0[a]"
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest reel_with_audio.mp4
  Then atomically replace video_studio/output/<slug>/reel.mp4.
  CRITICAL: if there is no audio at all, do NOT run ffmpeg. Leave reel.mp4 untouched.
  Verify the muxed file: ffprobe must report an audio stream, and the duration must not
  have drifted more than 0.15 s from the storyboard total.

STEP 6 — CAPTION.TXT
Write video_studio/output/<slug>/caption.txt — the plain caption body for Instagram:
  - first line: a standalone hook, <= 90 chars, on its own (this is the fold)
  - blank line
  - 3-6 short lines of body, hyper-practical, specific
  - blank line
  - 8-14 hashtags, no banned phrase, no #gamechanger #seamless #nextgenai #unlockthepower
  - the CTA from brand.cta (handle @signhify.studio, site signhify.dpdns.org)
  - sign-off ONCE at the very end:
    "My name is Piyush Raj Singh. Stop posting. Start shipping."
  Banned-phrase sweep is mandatory. Instagram's limit is 2200 characters; assert you are
  under it.

STEP 7 — SELF-CHECK (if __name__ == "__main__":)
  - build_audio(...) with narration disabled and music null
  - assert captions.srt exists, is non-empty, and is monotonic
  - assert status narration == "skipped"
  - assert caption.txt exists and is < 2200 chars
  - assert reel.mp4 was NOT modified (compare sha256 before/after)
  Print "AUDIO SELF-CHECK PASS (no-tts path)".

RUN IT for the current slug and print the capability table, the SRT path, and caption.txt.

RULES
  - NEVER install Kokoro, whisper-cpp, or any package. Report the absence instead.
  - NEVER call a paid API. No ElevenLabs, no OpenAI TTS, no cloud STT.
  - NEVER fabricate transcript timing. SRT times come from the storyboard, always.
  - NEVER substitute music the brief did not name.
  - Respect the 16 banned phrases in every caption and subtitle string.
  - Never print or write an API key.

ACCEPTANCE
  - audio.py exists, imports cleanly, runs.
  - Capability probe prints tts_backend and transcribe_backend honestly.
  - captions.srt exists, is valid SRT, monotonic, ends within 0.5 s of storyboard total.
  - caption.txt exists, under 2200 chars, passes the banned sweep.
  - "AUDIO SELF-CHECK PASS (no-tts path)" printed.
  - reel.mp4 byte-identical when no audio path is taken.
````

## 6. Expected output files
- `video_studio/audio.py`
- `video_studio/output/<slug>/captions.srt`
- `video_studio/output/<slug>/caption.txt`
- `video_studio/output/<slug>/script.md` (if PROMPT 07 did not write it here)
- Possibly `video_studio/work/<slug>/assets/audio/*`

## 7. Execution requirements
- FFmpeg/ffprobe 8.0.1 on PATH. FFmpeg only when audio actually exists.
- No TTS/STT installs. No paid APIs. Capability probe runs first, every time.

## 8. Dependencies on earlier prompts
- PROMPT 10 (reel.mp4 exists), PROMPT 08 (storyboard timing), PROMPT 07 (narration copy).

## 9. Acceptance criteria
- SRT valid, monotonic, non-empty, ends within 0.5 s of the storyboard total.
- `caption.txt` < 2200 chars, banned sweep clean, sign-off exactly once.
- `AUDIO SELF-CHECK PASS (no-tts path)` printed.
- `reel.mp4` unchanged (sha256 equal) when no audio path is taken.

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -m video_studio.audio video_studio\work\<slug>\storyboard.json
Get-Content video_studio\output\<slug>\captions.srt -TotalCount 12
(Get-Content video_studio\output\<slug>\caption.txt -Raw).Length
Select-String -Path video_studio\output\<slug>\caption.txt -Pattern "game-changer|seamless|unlock the power|dive into|at its core|robust|next-gen" -CaseSensitive:$false
ffprobe -v error -show_entries stream=codec_type -of csv=p=0 video_studio\output\<slug>\reel.mp4
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `npx hyperframes tts` errors | Kokoro not installed | Expected. Fall back to `tts_backend = "none"` and skip. Never install. |
| SRT out of order | Scenes emitted unsorted | Sort by `start_s` before writing. Assert monotonic. |
| Mux changes duration | `-shortest` with a longer audio track | Verify drift ≤ 0.15 s. If longer, trim narration to the storyboard total. |
| reel.mp4 gains no audio stream | ffmpeg not run, or map error | Read the command output. Verify with ffprobe `codec_type`. |
| Agent picks "royalty-free music" | Asset poaching | Delete. Only the brief's explicit URL is approved. |
| caption.txt over 2200 chars | Body too long | Trim body lines, keep hashtags, re-check. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 12 — Automated Video Quality Assurance
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]` `[AUDIT]`

## 1. Prompt title
PROMPT 12 — Automated Video Quality Assurance

## 2. Intended purpose
Implement `video_studio/qa.py`: an independent verifier that judges a finished MP4 **without
trusting the renderer**. It re-probes the file, extracts frames, measures contrast and
luma, and emits a `qa_report.md` with a hard PASS/FAIL. Exit 3 on failure.

## 3. When to use it
- After PROMPT 10/11, before PROMPT 13 (packaging).
- Standalone against any MP4: `python -m video_studio qa --video <path>`.
- On every render, and as a regression gate in PROMPT 19.

## 4. Required inputs
- `video_studio/output/<slug>/reel.mp4` or any MP4 path
- `video_studio/work/<slug>/storyboard.json` (for expected duration / scene count)
- `docs/video-studio/HYPERFRAMES_RESEARCH.md` (for what `npx hyperframes check` covers)
- FFmpeg/ffprobe 8.0.1 on PATH

## 5. Exact copy-paste prompt text

````
You are implementing the independent QA gate for the video engine.
Working directory: D:\Autogram. Python: .venv\Scripts\python.exe. FFmpeg/ffprobe 8.0.1.

CREATED FILES:
  video_studio/qa.py
  (plus video_studio/qa_rules.json if you prefer the thresholds in config — either way,
   the thresholds must be in ONE place and must be readable without opening code)

CORE PRINCIPLE
QA must be able to FAIL the renderer. Do not import compose.py or render.py and reuse their
in-memory values. Re-read the MP4 from disk and re-derive every fact. A gate that can only
pass is not a gate.

THRESHOLDS (single source of truth, in qa_rules.json)
  width                     1080          exact
  height                    1920          exact
  aspect_ratio_tolerance    0.01
  fps_tolerance             0.5  fps
  codec_name                h264
  pix_fmt                   yuv420p
  duration_tolerance_s      0.15          vs storyboard total, when a storyboard exists
  min_frame_mean_luma       8.0           below this a frame is effectively black
  max_frame_mean_luma       248.0         above this a frame is effectively white
  min_frame_luma_delta      10.0          min vs max sampled frame; too low = frozen/static
  contrast_min_ratio        4.5           WCAG AA for body text (3.0 for large)
  max_sample_frames         9
  min_file_bytes            50000

CHECK GROUP A — CONTAINER / ENCODING (ffprobe)
  ffprobe -v error -show_streams -show_format -of json <video>
  Assert: exactly 1 video stream; width, height, codec_name, pix_fmt, r_frame_rate,
  nb_frames (when present), duration, and file size.
  Also confirm constant frame rate if the stream exposes it.

CHECK GROUP B — DURATION & FRAME COUNT
  If a storyboard.json exists next to the video (or is passed via --storyboard),
  assert abs(probe_duration - storyboard.duration_s) <= duration_tolerance_s.
  assert abs(nb_frames - fps * duration) / (fps*duration) <= 0.02.
  If no storyboard: record "SKIPPED (no storyboard)" — do not guess the expected duration.

CHECK GROUP C — VISUAL SANITY (this catches the black-video and frozen-video bugs)
  Extract min_sample_frames frames evenly across the duration:
    ffmpeg -y -i <video> -vf "fps=<fps>,scale=64:64" -frames:v <n> -f image2 %d.png
  Then, WITHOUT Pillow (it is NOT installed), compute mean luma per frame by parsing the
  raw bytes:
    ffmpeg -v error -i <frame>.png -f rawvideo -pix_fmt gray -  > frame.gray
    mean = sum(bytes) / len(bytes)
  Assertions:
    - every frame mean_luma >= 8.0                 (not black)
    - every frame mean_luma <= 248.0               (not blown out)
    - (max_mean - min_mean) >= 10.0               (the video actually changes)
  If Pillow IS importable, you may use it — but the raw-bytes path MUST work without it.
  Record every frame's mean luma in the report. A video that renders black MUST FAIL here.

CHECK GROUP D — CONTRAST (WCAG AA)
  For each sampled frame, compute a crude contrast proxy from the gray histogram:
  the ratio between the 95th-percentile and 5th-percentile luminance, adjusted for the
  standard sRGB transfer function, giving an approximate WCAG ratio.
  Assert the frame's estimated max ratio >= contrast_min_ratio (4.5), OR record the frame
  as "LOW CONTRAST (review visually)".
  This check is ADVISORY and MUST be labelled as an estimate in the report. The
  authoritative contrast check is `npx hyperframes check`, which grades real text nodes.
  Do not present this estimate as a WCAG certification.

CHECK GROUP E — HYPERFRAMES COMPOSITION GATE (only if a work dir is supplied)
  If --work <dir> is given and <dir>/index.html exists:
    run `npx hyperframes check` with cwd=D:\Autogram
    capture stdout+stderr
    PASS only if the output contains "0 errors, 0 warnings"
  If --work is not supplied: record "SKIPPED (no --work)".
  NEVER pass --docker. NEVER pass --gpu.

CHECK GROUP F — DELIVERABLES
  If the slug output dir is supplied, assert these exist and are non-empty:
    reel.mp4, cover.jpg, captions.srt (if narration), caption.txt, script.md,
    storyboard.json, brief.json, asset_manifest.json, manifest.json
  Any missing deliverable is a FAIL. If --strict is passed, any FAIL exits 3.
  Without --strict, a FAIL still exits 3 but the report is written first.

REPORT — video_studio/output/<slug>/qa_report.md
  # QA Report — <slug>
  ## Verdict            PASS or FAIL, plus the exit code
  ## Input File         path, sha256, bytes
  ## Environment        ffmpeg/ffprobe version, python version, platform
  ## A. Container       the raw ffprobe JSON + PASS/FAIL per field
  ## B. Duration        measured vs expected, delta, PASS/FAIL
  ## C. Visual Sanity   a table of frame index / timestamp / mean luma / verdict
  ## D. Contrast        estimated ratios, clearly labelled ESTIMATE
  ## E. HyperFrames Gate  verbatim output, or SKIPPED with the reason
  ## F. Deliverables    each file, present?, bytes
  ## Failures           every failed assertion, with the measured value and the threshold
  ## Recommendation     one concrete next action (re-render at draft / fix tokens / etc.)

EXIT CODES
  0 = PASS.  3 = FAIL.  1 = could not read the file (ffprobe failed / missing).

SELF-CHECK (if __name__ == "__main__":)
  Build 3 tiny fixtures with ffmpeg and assert qa() catches each:
    (a) correct 1080x1920 4 s h264 yuv420p clip that changes content -> PASS
    (b) a solid-color clip (mean luma delta 0)           -> FAIL on check C
    (c) a 640x360 clip                                    -> FAIL on check A
  Print "QA SELF-CHECK PASS (3/3 caught)".
  A QA gate that cannot be made to fail is broken. Prove you can make it fail.

RUN IT:
  .venv\Scripts\python.exe -m video_studio.qa --video video_studio/output/<slug>/reel.mp4
                                                   --work video_studio/work/<slug>
  --storyboard video_studio/work/<slug>/storyboard.json
Print the verdict and exit code.

RULES
  - No new dependencies. stdlib + ffmpeg CLI. Pillow optional, never required.
  - Never modify reel.mp4. QA is read-only on inputs.
  - Never claim PASS without the measured numbers in the report.
  - Never present the contrast estimate as a WCAG audit.
  - Never pass --docker or --gpu.
  - Do not print or read API keys.

ACCEPTANCE
  - qa.py exists, imports, runs against the real reel.mp4.
  - qa_report.md exists with all 9 sections and a verdict.
  - Self-check catches all 3 planted failures; "QA SELF-CHECK PASS (3/3 caught)" printed.
  - Exit code is 0 for the real reel and 3 for each planted failure.
  - The black/frozen-video check provably fires (prove with a solid-color fixture).
````

## 6. Expected output files
- `video_studio/qa.py`
- `video_studio/qa_rules.json` (thresholds in one place)
- `video_studio/output/<slug>/qa_report.md`
- Temporary `*.gray` / `*.png` frame files (delete after measuring)

## 7. Execution requirements
- FFmpeg/ffprobe CLI + stdlib. Pillow optional, never required.
- Read-only on inputs. `-q 1` ffmpeg error output suppressed except for real failures.
- Never `--docker`, never `--gpu`.

## 8. Dependencies on earlier prompts
- PROMPT 10 (reel.mp4), PROMPT 11 (captions), PROMPT 01 (what `check` covers).

## 9. Acceptance criteria
- Self-check catches 3 planted failures → `QA SELF-CHECK PASS (3/3 caught)`.
- Real reel gets a verdict with measured numbers.
- Exit 0 on pass, 3 on fail, 1 on unreadable input.
- Contrast section explicitly labelled ESTIMATE.
- No dependency on renderer in-memory state.

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -m video_studio.qa --video video_studio\output\<slug>\reel.mp4 --work video_studio\work\<slug>
$LASTEXITCODE    # expect 0
ffprobe -v error -show_streams -show_format -of json video_studio\output\<slug>\reel.mp4
Get-Content video_studio\output\<slug>\qa_report.md -TotalCount 25
```
Then deliberately corrupt a copy (e.g. a solid-colour 1080×1920 clip) and confirm exit 3.

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `Image` import error | Pillow assumed | Use the raw-gray-bytes path. It is the required fallback. |
| `nb_frames` absent in ffprobe | Some encodes omit it | Use `-count_frames`, or skip that assertion and record "not reported". |
| Black frames but exit 0 | Check C not implemented | The luma check is mandatory. A black video must FAIL. |
| QA passes everything, ever | Gate is a rubber stamp | Re-run the self-check; it must catch the solid-colour fixture. |
| Contrast estimate flagged on a good video | Crude histogram method | It's advisory. Note it; rely on `npx hyperframes check` for text. |
| `npx hyperframes check` hangs | Called from the wrong cwd | `cwd=D:\Autogram`. 300 s timeout. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 13 — Instagram Reel Packaging
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]`

## 1. Prompt title
PROMPT 13 — Instagram Reel Packaging

## 2. Intended purpose
Turn a rendered, QA-passed reel into a **publishable package**: the 1080×1920 cover image,
the finalized `caption.txt`, and the `manifest.json` that every later stage reads. No
network, no Meta API — this stage is always safe to run.

## 3. When to use it
- After PROMPT 12 returns PASS.
- Before PROMPT 14 (publishing needs cover + caption + manifest).
- Re-runnable on its own to refresh a cover or rewrite a caption.

## 4. Required inputs
- `video_studio/output/<slug>/reel.mp4` + `qa_report.md` (PASS)
- `video_studio/output/<slug>/storyboard.json`, `brief.json`, `caption.txt`
- `video_studio/brand_tokens.json` (PROMPT 02)
- FFmpeg/ffprobe 8.0.1 on PATH

## 5. Exact copy-paste prompt text

````
You are implementing Instagram Reel packaging.
Working directory: D:\Autogram. Python: .venv\Scripts\python.exe. FFmpeg/ffprobe 8.0.1.

CREATE: video_studio/packaging.py
  package(slug, dry_run=False) -> dict

PRECONDITION — fail closed
  package() MUST refuse (exit 3) if:
    - reel.mp4 is missing
    - qa_report.md is missing
    - qa_report.md verdict is FAIL
  Never package an unverified video. Packaging is not a way to skip QA.

STEP 1 — COVER IMAGE (the detail people get wrong)
Instagram Reel covers are 1080x1920 (9:16). They are NOT the 1080x1350 carousel size.
  # Find the CTA scene so the cover is the brand frame, not a random mid-video frame.
  read storyboard.json -> scenes[-1] must be type "cta" -> its start_s
  # Extract the frame at the MIDDLE of the CTA scene (most readable, avoids entrance motion)
  t = start_s + duration_s / 2
  ffmpeg -y -ss <t> -i reel.mp4 -frames:v 1 -q:v 2 cover.jpg
Requirements — ASSERT each one:
  - ffmpeg output resolution is exactly 1080x1920   (verify with ffprobe)
  - the JPEG is sRGB
  - mean luma of the cover is >= 8 (it is not a black frame)
  - file size >= 20 KB (a 2 KB JPEG is a blank frame)
If the CTA scene is absent, fall back to the middle of the reel and record that in the
manifest. NEVER use assets/ig_signhify.studio_*.jpg — those are 1080x1350 carousel
images and using one as a Reel cover crops badly.

STEP 2 — CAPTION
Load output/<slug>/caption.txt (from PROMPT 11). If missing, generate it from the brief
using brand.cta.
FINAL VALIDATION — all must pass or packaging fails:
  - length <= 2200 characters (Instagram's hard limit)
  - first line <= 90 characters and is a standalone hook
  - 8-14 hashtags
  - ZERO hits from the 16 banned phrases (case-insensitive), plus these variants:
    game changing, game-changing, revolutionary, cutting-edge, seamlessly, unlock,
    dive into, at its core, next gen, next-gen, must have, must-have, in today's,
    ultimate secret, power of
  - the handle @signhify.studio appears exactly once as the CTA
  - the sign-off "My name is Piyush Raj Singh. Stop posting. Start shipping."
    appears EXACTLY ONCE, at the very end
Print the banned sweep report. It must be clean.

STEP 3 — MANIFEST
Write video_studio/output/<slug>/manifest.json atomically:
{
  "slug": "<slug>",
  "created_utc": "<ISO8601>",
  "pipeline_version": "1.0.0",
  "brief": { "topic": "...", "pillar": "...", "duration_s": 30, "language": "en" },
  "video": { "file": "reel.mp4", "width": 1080, "height": 1920, "fps": 30,
             "codec": "h264", "pix_fmt": "yuv420p", "duration_s": 30.0,
             "bytes": 123, "sha256": "<64 hex>" },
  "cover": { "file": "cover.jpg", "width": 1080, "height": 1920,
             "bytes": 123, "sha256": "<64 hex>", "frame_at_s": 27.5,
             "source_scene": "cta" },
  "caption": { "file": "caption.txt", "chars": 812, "hashtags": 11,
               "banned_phrase_hits": 0 },
  "qa": { "verdict": "PASS", "report": "qa_report.md" },
  "published": false,
  "ig_media_id": null,
  "published_utc": null
}
CRITICAL: "published" MUST be false and "ig_media_id" MUST be null here. This stage has
no network access. Setting either to anything else is a fabrication.

STEP 4 — FINAL INVENTORY + REPORT
Print the package contents table: filename, bytes, sha256 (first 12 chars), and a note.
Copy every deliverable from PROMPT 08's output contract that is not yet present:
  script.md, storyboard.json, brief.json, asset_manifest.json, qa_report.md, render.log
If one is genuinely missing, report it as MISSING — do not fabricate an empty file.

STEP 5 — DRY RUN
`--dry-run` runs every check and prints exactly what it would write, writing nothing.
Default (no flag) writes the files.

RULES
  - NO network calls in this prompt. Packaging never touches Meta.
  - published is ALWAYS false here. PROMPT 14 is the only thing that flips it.
  - Never use a 1080x1350 carousel image as a 1080x1920 cover.
  - Never ship a caption that fails the banned sweep. Fix the copy, do not lower the bar.
  - Never fabricate a deliverable that does not exist.
  - Never print or write API keys.

ACCEPTANCE
  - packaging.py exists, imports, runs.
  - cover.jpg exists at exactly 1080x1920, >= 20 KB, mean luma >= 8.
  - caption.txt <= 2200 chars, passes the full banned sweep including variants.
  - manifest.json has sha256 for video and cover, published=false, ig_media_id=null.
  - Packaging refuses to run when qa_report.md says FAIL (prove this with a fixture).
  - No network traffic.
````

## 6. Expected output files
- `video_studio/packaging.py`
- `video_studio/output/<slug>/cover.jpg` (1080×1920)
- `video_studio/output/<slug>/manifest.json`
- `video_studio/output/<slug>/caption.txt` (validated, possibly rewritten)

## 7. Execution requirements
- FFmpeg for the cover frame; stdlib for hashing and validation.
- Zero network. Never touches Meta.
- Fails closed on a FAIL QA verdict (exit 3).

## 8. Dependencies on earlier prompts
- PROMPT 12 (QA PASS), PROMPT 11 (caption), PROMPT 08 (storyboard for CTA timing),
  PROMPT 02 (brand CTA).

## 9. Acceptance criteria
- `cover.jpg` verified 1080×1920 via ffprobe, ≥ 20 KB, non-black.
- `caption.txt` ≤ 2200 chars, 0 banned hits, sign-off exactly once at the end.
- `manifest.json` has video + cover sha256, `published: false`, `ig_media_id: null`.
- Packaging exits 3 when the QA verdict is FAIL.
- No network requests made.

## 10. Verification instructions
```powershell
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 video_studio\output\<slug>\cover.jpg
(Get-Item video_studio\output\<slug>\cover.jpg).Length
(Get-Content video_studio\output\<slug>\caption.txt -Raw).Length
Select-String -Path video_studio\output\<slug>\caption.txt -Pattern "game-changer|seamless|unlock|dive into|at its core|next-gen|revolutionary|must-have|fast-paced" -CaseSensitive:$false
.venv\Scripts\python.exe -c "import json;m=json.load(open('video_studio/output/<slug>/manifest.json',encoding='utf-8'));assert m['published'] is False and m['ig_media_id'] is None;print('MANIFEST OK')"
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| cover.jpg is 2 KB / black | Extraction timestamp past the end, or `-ss` after `-i` | Put `-ss` **before** `-i` for fast seek; re-probe. |
| Cover is 1080×1350 | Wrong source used | The 9 carousel JPGs are 1080×1350. Extract from reel.mp4 instead. |
| Caption fails the sweep | Body copy contained a banned phrase | Rewrite the copy. Do not lower the threshold. |
| Packaging runs on a FAIL reel | Precondition not checked | Re-add the qa_report verdict gate. Packaging is not a QA bypass. |
| `published` is true | Someone flipped it early | It belongs to PROMPT 14 only. Reset to false. |
| Manifest sha256 wrong | File changed after hashing | Hash at write time, atomically, as the last step. |---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 14 — Official Instagram Publishing Integration
# ═════════════════════════════════════════════════════════════════════════════

`[PUBLISHES CONTENT]`

## 1. Prompt title
PROMPT 14 — Official Instagram Publishing Integration

## 2. Intended purpose
Implement the official Meta Graph API Reels publishing flow in `video_studio/publish.py` —
**disabled by default behind an explicit opt-in flag**, dry-run first, never printing a
token. This is the only prompt in the pack that talks to a third-party production system.

## 3. When to use it
- After PROMPT 13 produced a valid package.
- Only when the owner has supplied credentials AND explicitly enabled publishing.
- Never in CI, never in a test run, never without opt-in.

## 4. Required inputs
- `video_studio/output/<slug>/manifest.json`, `reel.mp4`, `cover.jpg`, `caption.txt` (PROMPT 13)
- Environment (values NEVER printed, NEVER committed):
  - `IG_USER_ID` — the Instagram Professional account's numeric ID
  - `IG_ACCESS_TOKEN` — token with `instagram_business_content_publish` scope
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID`
  - `META_GRAPH_ACCESS_TOKEN`
  - `META_API_VERSION` — default `v26.0`
  - `PUBLIC_CDN_BASE` — **public https base URL** where Meta can fetch the MP4 and cover
  - `DRY_RUN` — default `true`
  - `VIDEO_STUDIO_PUBLISH` — default `false`; the explicit owner opt-in

## 5. Exact copy-paste prompt text

````
You are implementing the official Instagram Reels publishing flow.
Working directory: D:\Autogram. Python: .venv\Scripts\python.exe. `requests` is installed.

THIS IS THE ONLY PROMPT IN THIS PACK THAT TOUCHES A THIRD-PARTY PRODUCTION SYSTEM.
Read every gate below twice before writing a line of code.

ACCOUNT REQUIREMENT
Publishing requires an Instagram PROFESSIONAL account (Business or Creator) connected to
a Facebook Page. A personal account CANNOT publish Reels via this API. If the account is
personal, report that clearly and stop. Do not attempt any workaround.

THE GATE — publishing is impossible unless ALL FOUR are true:
  1. VIDEO_STUDIO_PUBLISH == "true"     (explicit owner opt-in; default is absent/false)
  2. DRY_RUN            != "true"       (default is true)
  3. IG_USER_ID         is non-empty
  4. IG_ACCESS_TOKEN    is non-empty
If any is false -> print exactly which gate failed, leave manifest.published == false,
and EXIT 4. Do not call the API. Do not "just test it".

CREATE: video_studio/publish.py
  publish(slug, caption=None, cover=None, dry_run=None) -> dict
  PublishError(Exception)
  preflight(slug) -> dict              # checks the gate + payload, makes NO network call
  MetaGraphClient                      # thin requests wrapper

STEP 1 — PREFLIGHT (no network)
  - Read manifest.json. Refuse unless qa.verdict == "PASS" and published == false.
  - Compute the public URLs:
      video_url = f"{PUBLIC_CDN_BASE}/output/<slug>/reel.mp4"
      cover_url = f"{PUBLIC_CDN_BASE}/output/<slug>/cover.jpg"
    VALIDATE before calling Meta:
      * both URLs parse
      * both are HTTPS (Meta will reject http for production; localhost is NOT public)
      * HTTP HEAD each URL and confirm 200 + Content-Type + Content-Length > 0
    If HEAD fails, STOP. A local file:// path or an unreachable localhost URL WILL fail at
    Meta with an opaque error. Say so explicitly.
  - Print a redacted readiness summary: slug, video_url, cover_url, caption length,
    estimated publish window. NEVER print IG_USER_ID or any token, not even partially.
  - In dry-run, stop here and exit 0.

STEP 2 — THE GRAPH FLOW (exact, v26.0)
  a) CREATE CONTAINER
     POST https://graph.facebook.com/{META_API_VERSION}/{IG_USER_ID}/media
     form fields:
       media_type    = REELS
       video_url     = <public https mp4>
       caption       = <caption.txt, <= 2200 chars>
       cover_url     = <public https jpg, optional but recommended>
       share_to_feed = true
       thumb_offset  = <seconds into the video for the cover frame>
     -> response: { id: "<container_id>" }

  b) POLL FOR READINESS
     GET https://graph.facebook.com/{META_API_VERSION}/{container_id}?fields=status_code
     Poll every 10 s, up to 10 minutes (Meta's own guidance is 5 min; be patient).
     status_code "FINISHED" -> proceed.
     "ERROR" or "EXPIRED"  -> abort, log the container status, exit 1.
     Poll with a monotonic clock. Never poll in a tight loop.

  c) PUBLISH
     POST https://graph.facebook.com/{META_API_VERSION}/{IG_USER_ID}/media_publish
     form field: creation_id = <container_id>
     -> response: { id: "<ig_media_id>" }

  d) UPDATE THE MANIFEST (only on a real success)
     manifest["published"]        = true
     manifest["ig_media_id"]      = <returned id>
     manifest["published_utc"]    = <ISO8601>
     manifest["published_permalink"] = <https://www.instagram.com/reel/<shortcode>>
       ONLY if the API actually returned enough data to construct it. If you cannot
       construct it, set the field to null. NEVER fabricate a permalink.

STEP 3 — QUOTA (enforce locally, before any network call)
  - Assume 50 published posts per rolling 24 hours. Take the SAFE number: official Meta
    docs conflict (one page states 100; the endpoint and quota pages state 50).
  - 400 containers per 24 h. Containers EXPIRE after 24 h — if a container is not published
    within 24 h it is gone; re-create it.
  - Before publishing, count successful publishes in the last 24 h from local manifests.
  - If >= 50, exit 4 with a clear "RATE LIMIT REACHED" message. Do not attempt anyway.
  - Print the current count. Read it from local manifests, never from a guessed number.

STEP 4 — ERROR HANDLING
  - HTTP 4xx: log status + the Meta error `message` and `code`. Do not retry 4xx.
  - HTTP 5xx / connection error: retry up to 3 times with exponential backoff
    (2 s, 8 s, 32 s + jitter). Never more than 3.
  - OAuth errors (190, 102): the token is bad, wrong account, or missing the
    instagram_business_content_publish scope. Report clearly. DO NOT attempt to refresh
    or obtain a new token. That is the owner's job.
  - Never print a token, ever, in any log, exception message, traceback, or HTTP body dump.
    Implement a redaction filter that scrubs the known token value from every log line.

STEP 5 — TESTS (must run WITHOUT real credentials)
  Write tests using a mocked requests session. Cover:
    - gate blocks when VIDEO_STUDIO_PUBLISH is false        -> exit 4, zero network calls
    - gate blocks when DRY_RUN is true                     -> exit 4, zero network calls
    - gate blocks when IG_ACCESS_TOKEN is empty            -> exit 4, zero network calls
    - preflight rejects an http:// (non-https) video_url   -> raises PublishError
    - preflight rejects an unreachable public URL          -> raises PublishError
    - full flow returns an ig_media_id                     -> manifest.published true
    - container status ERROR                              -> exit 1, published stays false
    - quota >= 50 in 24 h                                 -> exit 4, zero network calls
  Assert zero real HTTP requests in every blocked-path test.
  Print "PUBLISH SELF-CHECK PASS (8/8, 0 live calls)".

STEP 6 — DOCUMENT IT
Append a section to docs/video-studio/ARCHITECTURE.md:
  ## Publishing
  - the four gates
  - the three-step flow with the exact endpoint paths
  - the quota numbers and their conservative source
  - the error table
  - an explicit statement that the token is never logged, and how redaction works

RULES — NON-NEGOTIABLE
  - NEVER hardcode a token, user id, or any credential in source, config, or a comment.
    Use os.environ. Placeholders only: <YOUR_IG_ACCESS_TOKEN>.
  - NEVER print a token, even masked, even in an error path.
  - NEVER bypass authentication, scrape a session, use an unofficial client, or
    automate a browser login. Official Graph API only.
  - NEVER publish without VIDEO_STUDIO_PUBLISH=true AND DRY_RUN=false.
  - NEVER publish a video whose qa.verdict is not PASS.
  - NEVER claim a Reel was published unless media_publish returned an id, and show it.
  - NEVER activate a paid API or add a billing-related call without owner authorization.
  - NEVER fabricate a permalink, a post id, or an engagement figure.
  - Do not modify .env or .env.example. Read keys from os.environ only.
  - Default DRY_RUN behaviour must be preserved for the whole repo.

ACCEPTANCE
  - publish.py exists with preflight() that makes ZERO network calls.
  - "PUBLISH SELF-CHECK PASS (8/8, 0 live calls)" printed.
  - Every blocked-path test asserts zero HTTP requests.
  - A live publish is NOT attempted unless all four gates pass.
  - No credential appears anywhere in the source. grep confirms it.
````

## 6. Expected output files
- `video_studio/publish.py`
- `video_studio/tests/test_publish.py` (or an equivalent mocked test module)
- Appended `## Publishing` section in `docs/video-studio/ARCHITECTURE.md`
- On a real (opt-in) publish only: updated `video_studio/output/<slug>/manifest.json`

## 7. Execution requirements
- `requests` (installed). No new packages.
- All 8 self-checks run against a **mocked session**. Zero live calls.
- `preflight()` is pure — no network.

## 8. Dependencies on earlier prompts
- PROMPT 13 (the package being published), PROMPT 03 (env key names).

## 9. Acceptance criteria
- `PUBLISH SELF-CHECK PASS (8/8, 0 live calls)` printed.
- All four gates enforced and independently tested.
- Quota check (50/24h) enforced locally before any network call.
- Token redaction implemented and exercised by a test.
- Zero credentials in source (`Select-String` for the token value returns nothing).

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -m pytest video_studio\tests\test_publish.py -v
# Prove the default is safe:
$env:VIDEO_STUDIO_PUBLISH="false"; .venv\Scripts\python.exe -m video_studio.publish <slug>
$LASTEXITCODE    # expect 4, and zero network calls
# Prove nothing leaks:
Select-String -Path video_studio\publish.py -Pattern "EA[A-Za-z0-9]{20,}|access_token\s*=\s*[\"'][A-Za-z0-9]{20,}"
# `?access_token=` is required in the URL and is fine; a hardcoded literal value is not.
```
Read `publish.py` line by line and confirm no branch logs a token.

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Meta error `9007` / "media not reachable" | Video URL is localhost or http | Meta must fetch it over public https. Surface this in `preflight`. |
| Container stuck `IN_PROGRESS` | Video too large or the URL is slow | Poll up to 10 min, then abort and log. Never loop forever. |
| OAuth error 190/102 | Token wrong scope or expired | Report. Do NOT refresh or re-auth. That is the owner's action. |
| Publish succeeds but the manifest still says false | Manifest written before the API call | Write the manifest AFTER `media_publish` returns an id. |
| Log contains the token | Missing redaction filter | Add the scrub filter and re-run the leak test. Rotate the token if it ever hit a log. |
| Rate limited | Past 50 posts/24h | Exit 4, print the local count, stop. Never retry-storm. |
| Account is personal | Not a Professional account | State clearly that a Business/Creator account linked to a Page is required. Stop. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 15 — Fully Automated Production Workflow
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]`

## 1. Prompt title
PROMPT 15 — Fully Automated Production Workflow

## 2. Intended purpose
Wire the existing stages into one orchestrator and one CLI: `video_studio/pipeline.py` and
`video_studio/cli.py`, exposed as `python -m video_studio`. One brief in, one QA-verified
package out, with correct failure semantics at every boundary.

## 3. When to use it
- After PROMPTs 08–14 (all stages exist).
- Before PROMPT 16 (scheduling) and PROMPT 18 (operational production).
- This is the prompt that makes the engine usable by a non-engineer.

## 4. Required inputs
- `docs/video-studio/ARCHITECTURE.md` (PROMPT 03)
- Existing modules: `brief.py`, `storyboard.py`, `assets.py`, `compose.py`, `render.py`,
  `audio.py`, `qa.py`, `packaging.py`, `publish.py`
- `video_studio/briefs/<slug>.json`

## 5. Exact copy-paste prompt text

````
You are wiring the video engine's stages into one orchestrator and one CLI.
Working directory: D:\Autogram. Python: .venv\Scripts\python.exe (3.14.7).
hyperframes 0.8.58 via `npx hyperframes` from D:\Autogram. FFmpeg/ffprobe 8.0.1.
No CUDA GPU. Docker installed but NOT running. Kokoro TTS and whisper-cpp NOT installed.

READ FIRST:
  docs/video-studio/ARCHITECTURE.md   (especially the Failure Semantics + exit-code table)
  video_studio/brief.py, storyboard.py, assets.py, compose.py, render.py,
            audio.py, qa.py, packaging.py, publish.py

CREATE:
  video_studio/pipeline.py    stage orchestration with correct failure boundaries
  video_studio/cli.py         argparse CLI
  video_studio/__main__.py    so `python -m video_studio` works

STEP 1 — pipeline.py
  run_stage(name, fn) -> dict   wraps a stage: logs to output/<slug>/render.log,
                                  records timing, converts an exception into the right exit code
  STAGES, in order:
    validate  brief.load_brief + brief.validate_brief          -> exit 2 on failure
    storyboard storyboard.build_storyboard -> work/<slug>/storyboard.json
    assets    assets.resolve_assets -> work/<slug>/asset_manifest.json
    compose   compose.compose -> work/<slug>/{index.html,hyperframes.json,package.json}
    qa_gate   npx hyperframes check; require "0 errors, 0 warnings"   -> exit 3 on failure
    render    npx hyperframes render -f <fps> -q <quality> -w 4
    verify    ffprobe + assertions on the produced MP4            -> exit 1 on failure
    audio     audio.build_audio (degrades silently when no TTS exists)
    qa        qa.run on the finished MP4                         -> exit 3 on FAIL
    package   packaging.package                                  -> exit 3 if QA verdict is FAIL
    publish   publish.publish                                   -> exit 4 if any gate is closed
  RULES:
    - Stages are skipped if their output already exists and is newer than its input,
      UNLESS --force. This makes the pipeline resumable AND idempotent.
    - qa_gate runs BEFORE render. A failing check NEVER renders.
    - verify runs AFTER render and re-probes from disk. Never trust an exit code alone.
    - package refuses if the QA verdict is not PASS. Packaging is not a QA bypass.
    - publish runs ONLY when explicitly requested and all four gates are open.
    - Every stage writes its log lines to output/<slug>/render.log (append).
    - Any stage failure stops the pipeline, leaves every prior artifact intact, and
      leaves manifest.published == false.

STEP 2 — cli.py (argparse)
  python -m video_studio build   --brief <path> [--slug X] [--force] [--dry-run] [--json] [--quiet]
  python -m video_studio render  --brief <path> [--slug X] [--quality draft|standard|high]
                                 [--fps 30] [--no-audio] [--force] [--dry-run] [--json] [--quiet]
  python -m video_studio qa      --video <path> [--work <dir>] [--storyboard <path>]
                                 [--report <path>] [--strict] [--json]
  python -m video_studio package --brief <path> [--slug X] [--force] [--dry-run] [--json]
  python -m video_studio publish --slug X [--caption-file F] [--cover F] [--dry-run] [--json]
  python -m video_studio list [--json]
  EXIT CODES: 0 success | 1 runtime failure | 2 invalid brief | 3 QA gate failed |
              4 publish skipped or blocked
  --json prints a machine-readable result object on stdout and NOTHING else, so the
  output is safe to pipe. --quiet suppresses the human banner.
  --dry-run prints every action it WOULD take and performs none of them: no file writes
  to output/, no npx calls, no network.

STEP 3 — __main__.py
  `from .cli import main; raise SystemExit(main())`

STEP 4 — HUMAN OUTPUT
  Each stage prints exactly one banner line:
    [1/10] validate ... ok (12 ms)
    [6/10] qa_gate ... PASS  (0 errors, 0 warnings)
    [7/10] render  ... ok  38.2 s  -> video_studio/output/<slug>/reel.mp4
  On failure, print the stage name, the exception, and the exit code. Do not print a
  traceback unless --json is absent AND the error is unexpected.

STEP 5 — SELF-CHECK (if __name__ == "__main__":)
  Using a temp work dir and the real brief at video_studio/briefs/<slug>.json:
    1. `build --dry-run` makes ZERO writes to output/ and exits 0.
    2. `build` writes index.html + hyperframes.json + package.json + storyboard.json +
       asset_manifest.json and ZERO files in output/.
    3. A brief containing the banned phrase "game-changer" -> exit 2, no files written.
    4. `build --force` regenerates identically (byte-for-byte) -> determinism.
    5. `qa --video <nonexistent>` -> exit 1.
  Print "PIPELINE SELF-CHECK PASS (5/5)".

RUN IT:
  .venv\Scripts\python.exe -m video_studio build --brief video_studio/briefs/<slug>.json
  .venv\Scripts\python.exe -m video_studio build --brief video_studio/briefs/<slug>.json --dry-run
  .venv\Scripts\python.exe -m video_studio render --brief video_studio/briefs/<slug>.json --quality draft
  .venv\Scripts\python.exe -m video_studio qa --video video_studio/output/<slug>/reel.mp4 --work video_studio/work/<slug>
  .venv\Scripts\python.exe -m video_studio package --brief video_studio/briefs/<slug>.json
  .venv\Scripts\python.exe -m video_studio publish --slug <slug>          # expect exit 4
  .venv\Scripts\python.exe -m video_studio list
Print each command and its real exit code.

ACCEPTANCE
  - `python -m video_studio` works for build / render / qa / package / publish / list.
  - Exit codes 0/1/2/3/4 behave exactly as specified.
  - `build` writes nothing to output/. `render` writes reel.mp4 + render.log.
  - --dry-run on render writes nothing and makes zero npx calls and zero network calls.
  - `publish` without the opt-in exits 4 and touches nothing.
  - "PIPELINE SELF-CHECK PASS (5/5)" printed.

RULES
  - Do not modify the existing stage modules. Orchestrate them; do not rewrite them.
  - Never skip `npx hyperframes check`. It is the gate.
  - Never use --docker or --gpu.
  - Never publish unless explicitly asked AND all four gates are open.
  - Never print a token or an API key.
  - Every write is atomic (.tmp + os.replace).
````

## 6. Expected output files
- `video_studio/pipeline.py`
- `video_studio/cli.py`
- `video_studio/__main__.py`
- Runtime artifacts only: `video_studio/work/<slug>/` and `video_studio/output/<slug>/`

## 7. Acceptance criteria
- `python -m video_studio build|render|qa|package|publish|list` all functional.
- Exit codes 0/1/2/3/4 correct per stage and per failure class.
- `build` writes nothing into `output/`; `render` writes `reel.mp4` + `render.log`.
- `--dry-run` on `render` writes nothing and makes zero npx calls and zero network calls.
- `publish` without the opt-in exits 4 and touches nothing.
- `build --force` regenerates byte-identical output (determinism).
- Every stage failure leaves `manifest.published == false`.

## 8. Dependencies on earlier prompts
- PROMPTs 08–14 (all stage modules implemented), PROMPT 03 (exit-code table).

## 9. Verification instructions
```powershell
.venv\Scripts\python.exe -m video_studio build --brief video_studio\briefs\<slug>.json
.venv\Scripts\python.exe -m video_studio render --brief video_studio\briefs\<slug>.json --quality draft
$LASTEXITCODE                                                          # expect 0
.venv\Scripts\python.exe -m video_studio qa --video video_studio\output\<slug>\reel.mp4 --work video_studio\work\<slug>
.venv\Scripts\python.exe -m video_studio package --brief video_studio\briefs\<slug>.json
.venv\Scripts\python.exe -m video_studio publish --slug <slug> ; $LASTEXITCODE   # expect 4
.venv\Scripts\python.exe -m video_studio list
Get-ChildItem video_studio\output\<slug> | Select-Object Name, Length
```
Run `build --force` twice and diff `work/<slug>/storyboard.json` — it must be identical.

## 10. Acceptance gate (full)
Every row must hold:
- `build` writes `work/<slug>/{index.html,hyperframes.json,package.json,storyboard.json,asset_manifest.json}` and NOTHING in `output/`.
- `render` runs `npx hyperframes check` BEFORE `npx hyperframes render`; a failing check exits 3 without rendering.
- `qa` on a good reel exits 0; on a solid-colour 1080×1920 fixture exits 3; on a missing file exits 1.
- `package` refuses when the QA verdict is FAIL (exit 3).
- `publish --dry-run` exits 0 and makes zero network calls.
- `publish` without the opt-in exits 4.
- `--dry-run` on `render` writes no `output/` files, makes zero npx calls, and exits 0.
- `build --force` twice produces a byte-identical `storyboard.json`.

## 11. Common failure cases and recovery
| Symptom | Cause | Recovery |
|---|---|---|
| `qa_gate` runs after render | Stage list ordered wrong | Move `qa_gate` before `render`. The gate precedes the work it guards. |
| `package` runs on a FAIL reel | No verdict check | Re-add the `qa.verdict == "PASS"` precondition. Packaging is not a QA bypass. |
| Re-running overwrites good work | No resume logic | Add "skip if fresh, unless `--force`" per stage. |
| `--dry-run` still wrote a file | Flag not threaded through | `--dry-run` must propagate into every stage: zero writes, zero npx. |
| Exit code always 0 | Exceptions swallowed | Map each exception class to its exit code. Never return 0 after a failure. |
| `--json` output has stray prints | Debug logging not routed | All logs to stderr; `--json` writes only the result object to stdout. |
| A stage hangs | Missing subprocess timeout | check 300 s, render 1800 s; kill and fail with exit 1. |
| Pipeline re-runs everything each call | Resume logic absent | Compare mtimes; skip fresh stages unless `--force`. |
| A stage half-wrote its output then died | Non-atomic write | `.tmp` + `os.replace` in every stage that writes. |
| `list` shows stale slugs | Reads a directory instead of state | Read `video_studio/briefs/` and `state/run-state.json`. |
# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 16 — Scheduled Execution and Failure Recovery
# ═════════════════════════════════════════════════════════════════════════════

`[CODE-CHANGING]`

## 1. Prompt title
PROMPT 16 — Scheduled Execution and Failure Recovery

## 2. Intended purpose
Implement `video_studio/scheduler.py` and `video_studio/state.py`: a 7-slot daily runner with
durable state, idempotency locks, exponential backoff, and crash recovery — so a failed run
is resumable and never double-publishes.

## 3. When to use it
- After PROMPT 15 (the CLI exists).
- Before PROMPT 17 (analytics need run history) and PROMPT 18 (weekly production).
- Timezone is `Asia/Kolkata` (the repo-wide default, from `data/brand.json`).

## 4. Required inputs
- `video_studio/cli.py` (PROMPT 15)
- `data/brand.json` → `timezone` = `Asia/Kolkata`, `default_posting_time` = `20:00`
- `data/schedule.json` (existing repo artifact)

## 5. Exact copy-paste prompt text

````
You are implementing scheduling and failure recovery for the video engine.
Working directory: D:\Autogram. Python: .venv\Scripts\python.exe.

CREATE:
  video_studio/state.py      durable run state, atomic writes, idempotency locks
  video_studio/scheduler.py  slot runner, retry/backoff, resume

STEP 1 — state.py
State file: video_studio/state/run-state.json
{
  "runs": {
    "<slug>": {
      "status": "pending|running|rendered|qa_passed|qa_failed|packaged|
                 published|failed|cancelled",
      "stage": "<current stage name>",
      "attempts": 0,
      "last_error": null,
      "first_seen_utc": "...",
      "updated_utc": "...",
      "lock_pid": null,
      "lock_acquired_utc": null,
      "ig_media_id": null,
      "published": false
    }
  },
  "publish_history": [ { "slug", "ig_media_id", "published_utc" } ]
}
  load_state() / save_state(state) — ATOMIC. Write .tmp, then os.replace(). A crash never
  leaves a half-written state file.
  acquire_lock(slug, pid) -> bool   — refuses if a lock is held by a LIVE process
  release_lock(slug)
  is_published(slug) -> bool        — the idempotency guarantee: never publish twice

STEP 2 — scheduler.py
  SLOTS (7/day, Asia/Kolkata): 08:00, 10:30, 13:00, 15:30, 18:00, 20:00, 21:30
  The 20:00 slot is the default_posting_time from data/brand.json.
  next_slot(now) -> datetime        — the next upcoming slot in Asia/Kolkata
  claim_slot(now) -> Optional[str]  — returns the slug due for THIS slot, or None.
    Slot->slug assignment lives in data/schedule.json. If unassigned, claim_slot returns
    None and logs "no brief assigned". It MUST NOT invent a topic.

  run_once(slug) -> dict            — invokes the CLI pipeline for one slug
  run_due(now, dry_run=False) -> list[dict]
  retry_policy(attempts) -> seconds
    attempts 1 -> 60 s, 2 -> 300 s, 3 -> 900 s, 4+ -> give up, status "failed".
    Cap at 4 attempts. Never infinite retries.

  RESUME LOGIC (the important part)
  On startup, sweep state:
    status "running" + a DEAD lock holder -> mark "failed", last_error "process died",
      and make it eligible for retry.
    status "running" + a LIVE lock holder  -> skip it (another process owns it).
    status "published"                     -> never run again.
    status "rendered"/"qa_passed"          -> resume from the NEXT stage, not from the top.

  IDEMPOTENCY
  Before the publish stage, check is_published(slug). If true, skip publishing entirely and
  log "already published". This is the guarantee that a resumed or duplicated run cannot
  double-post.

STEP 3 — DRY RUN
  `--dry-run` prints the decision for every slot and slug (CLAIM / SKIP-already-published /
  SKIP-busy / CLAIM-resume / NO-BRIEF) and makes zero pipeline calls and zero network
  calls. Nothing is written.

STEP 4 — SELF-CHECK (if __name__ == "__main__":)
  Use a temporary state file in the OS temp dir. Assert:
    - acquire_lock then acquire_lock again by the same pid -> False
    - release_lock then acquire_lock -> True
    - save_state is atomic (write, kill mid-write simulation is NOT needed; just assert
      os.replace is used and the tmp file is removed)
    - is_published flips correctly after marking a run published
    - retry_policy(4) returns None (give up)
    - next_slot from 07:00 IST returns 08:00 same day; from 21:45 IST returns 08:00 NEXT day
  Print "SCHEDULER SELF-CHECK PASS".

RUN:
  .venv\Scripts\python.exe -m video_studio.scheduler --dry-run
  .venv\Scripts\python.exe -m video_studio.scheduler --once

RULES
  - All time arithmetic in Asia/Kolkata. Never use the machine's local timezone implicitly.
  - Never invent a topic. An unassigned slot is skipped, not filled.
  - Never publish an already-published slug. This is absolute.
  - Never retry more than 4 times. Never retry a 4xx error.
  - State writes are atomic. A corrupt state file must never be possible.
  - Respect DRY_RUN. --dry-run performs no writes and no network.
  - No new dependencies. stdlib zoneinfo + json.

ACCEPTANCE
  - state.py and scheduler.py exist, import cleanly.
  - "SCHEDULER SELF-CHECK PASS" printed.
  - --dry-run prints slot decisions and makes zero writes / zero network calls.
  - A slug already in publish_history is skipped by is_published.
  - Locking prevents concurrent runs of the same slug.
  - Slot math verified across a day boundary in Asia/Kolkata.
````

## 6. Expected output files
- `video_studio/state.py`
- `video_studio/scheduler.py`
- `video_studio/state/run-state.json` (created at runtime)
- Updated `data/schedule.json` if slot assignments change

## 7. Execution requirements
- Stdlib `zoneinfo`, `json`, `os`, `datetime`. No new dependencies.
- All slot math in `Asia/Kolkata`.
- Atomic state writes via `.tmp` + `os.replace`.

## 8. Dependencies on earlier prompts
- PROMPT 15 (the CLI being scheduled), PROMPT 14 (publish history for idempotency).

## 9. Acceptance criteria
- `SCHEDULER SELF-CHECK PASS` printed.
- `--dry-run` performs zero writes and zero network calls.
- `is_published()` blocks a second publish of the same slug.
- Locks block concurrent runs of one slug; dead locks are reclaimed.
- `next_slot` verified at 07:00 → 08:00 same day and 21:45 → 08:00 next day.

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -m video_studio.scheduler --dry-run
.venv\Scripts\python.exe video_studio\scheduler.py
Get-Content video_studio\state\run-state.json
# Prove idempotency:
Select-String -Path video_studio\scheduler.py -Pattern "is_published"
```
Re-run `--dry-run` twice; the output must be identical (deterministic).

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Slot fires at the wrong hour | Machine TZ used implicitly | Force `ZoneInfo("Asia/Kolkata")` everywhere. Verify across midnight. |
| Same slug rendered twice | Lock released on crash without a state write | Make state save the last operation before releasing the lock. |
| Double-publish after resume | Idempotency check missing before publish | `is_published()` must gate the publish stage unconditionally. |
| Corrupt `run-state.json` | Non-atomic write | `.tmp` + `os.replace`. Never write JSON in place. |
| Slot with no brief gets a made-up topic | Agent improvisation | Return `None`. Log "no brief assigned". Never invent content. |
| Infinite retry loop | Unbounded backoff | Cap at 4 attempts, then `failed`. Surface it for a human. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 17 — Analytics and Content Improvement
# ═════════════════════════════════════════════════════════════════════════════

`[RESEARCH]`

## 1. Prompt title
PROMPT 17 — Analytics and Content Improvement

## 2. Intended purpose
Implement `video_studio/analytics.py`: pull official Instagram Insights via the Graph API,
fold the results into `data/content-memory.json`, and produce a content-improvement brief
that measurably changes the next batch of briefs. **Unverified data must never enter the
memory file as fact.**

## 3. When to use it
- After PROMPT 14 has published at least one real Reel.
- Monthly, or after every ~10 posts.
- Before the next content batch is planned.

## 4. Required inputs
- `video_studio/state/run-state.json` → `publish_history` (PROMPT 16)
- Environment: `IG_USER_ID`, `IG_ACCESS_TOKEN`, `META_API_VERSION` (default `v26.0`)
- `data/content-memory.json` (existing repo ledger)
- `video_studio/brand_tokens.json`

## 5. Exact copy-paste prompt text

````
You are implementing the analytics and content-improvement loop.
Working directory: D:\Autogram. Python: .venv\Scripts\python.exe. `requests` installed.

CRITICAL CONTEXT — VERIFIED LIMITATION
  instagram.com/signhify.studio was BLOCKED at research time.
  We have NEVER observed the account's live follower count, engagement rate, or any post's
  performance from the public web.
  THEREFORE: every number that reaches content-memory.json MUST come from the official
  Graph API Insights endpoint for a media id WE published. If Insights is unreachable,
  if the token lacks the required scope, or if we have no publish history, the run must
  produce a NO-DATA report and write NOTHING to content-memory.json.
  NEVER estimate. NEVER infer. NEVER seed with a placeholder number that could later be
  mistaken for an observation.

CREATE: video_studio/analytics.py
  fetch_insights(slug, dry_run=False) -> dict | None
  update_content_memory(records) -> None
  recommend_next(records, n=5) -> list[dict]
  NO_DATA_REPORT_MARKER = "NO_DATA"

STEP 1 — DISCOVER WHAT WE ACTUALLY PUBLISHED
  Read video_studio/state/run-state.json -> publish_history.
  Only slugs with a non-null ig_media_id are eligible. If the list is empty, print
  NO_DATA and exit 0 without touching any file.

STEP 2 — FETCH INSIGHTS (official API only)
  For each eligible ig_media_id, call:
    GET https://graph.facebook.com/{META_API_VERSION}/{ig_media_id}/insights
        ?metric=plays,reach,likes,comments,saves,shares,total_interactions,watch_time
        &access_token=<IG_ACCESS_TOKEN>
  Handle:
    - 200 with data            -> keep only the metrics actually returned. Meta may not
                                  return every metric for every media type. Do NOT
                                  substitute 0 for a missing metric; record null.
    - OAuth 190/102 (no scope) -> print NO_DATA with the reason. Write nothing.
    - 4xx / 5xx                -> retry 5xx up to 3 times (2/8/32 s backoff). Give up and
                                  record the failure. NEVER invent a number.
  Record for each metric whether it came from the API or was absent.

STEP 3 — DERIVED METRICS (only where the denominator exists)
    interaction_rate = total_interactions / plays          (null if plays is 0 or null)
    save_rate        = saves / plays                       (null if plays is 0 or null)
    share_rate       = shares / plays                      (null if plays is 0 or null)
    retention_proxy  = watch_time / (plays * duration_s)   (null if plays is 0 or null)
  Guard every division. A null denominator yields null, never 0, never Infinity.

STEP 4 — WRITE TO data/content-memory.json
  Follow the EXISTING schema in that file. Inspect it first and match it exactly; do not
  invent a new shape. Each new record carries:
    slug, ig_media_id, published_utc, topic, pillar, duration_s,
    metrics { ... with null for anything not observed ... },
    derived { ... guarded ratios ... },
    source: "graph_api_insights"            <- REQUIRED. Anything else is a red flag.
  Records with source != "graph_api_insights" MUST NOT be written by this module.
  Write atomically (.tmp + os.replace). Back up the previous file to
  data/content-memory.backup.json first.

STEP 5 — recommend_next()
  Produce up to 5 concrete brief recommendations, each as a partial JSON matching the brief
  schema, justified by an observed metric:
    - Pillar performance: rank the 6 pillars by median interaction_rate over records with
      >= 5 posts. Propose MORE of the top performers. If fewer than 5 posts per pillar,
      say "insufficient data" for that pillar and DO NOT rank it.
    - Length: if saves/retention are stronger for a duration band, propose that band.
    - Hook: if plays is materially higher for reels whose first 1.5 s contains a question
      or a number, propose more. Only claim this if >= 3 reels share each pattern.
    - Drop what underperforms: any pillar in the bottom third over >= 5 posts should be
      paused, with the reason.
  Every recommendation MUST cite the record(s) it is derived from. A recommendation with no
  supporting record is forbidden.
  If total records < 5, return NO_DATA and recommend nothing. Five posts is the minimum
  for a directional read; below that, refuse to guess.

STEP 6 — REPORT
  Print a table: slug | published_utc | plays | reach | interactions | saves | shares
  Then the derived ratios, then the recommendations with their evidence.
  If there is no data, print:
    NO_DATA — <reason>. content-memory.json was not modified.

STEP 7 — TESTS (no network)
  Mock the requests session. Assert:
    - empty publish_history -> NO_DATA, zero network calls, zero file writes
    - insights 403/no-scope  -> NO_DATA, zero file writes
    - a metric missing from the API response stays null, is NOT coerced to 0
    - plays == 0 -> interaction_rate is null, not ZeroDivisionError
    - 4 records in publish_history -> recommend_next returns NO_DATA (below the 5 minimum)
    - the token never appears in any log line
  Print "ANALYTICS SELF-CHECK PASS (6/6, 0 live calls)".

RULES
  - NEVER fabricate an analytics number. Null is a valid, honest answer.
  - NEVER use the public Instagram page as a data source — it is blocked, and scraping it
    would be a policy violation anyway.
  - NEVER seed content-memory.json with placeholder metrics.
  - NEVER publish a recommendation without citing its source records.
  - Never print the access token. Implement redaction.
  - Respect the 16 banned phrases in any recommendation text.
  - Never rewrite existing records. Append only, atomically.

ACCEPTANCE
  - analytics.py exists, imports, runs.
  - "ANALYTICS SELF-CHECK PASS (6/6, 0 live calls)" printed.
  - With an empty publish_history: NO_DATA printed, zero network calls, content-memory.json
    byte-identical (verify with git diff).
  - Missing metrics stay null; division by zero yields null.
  - recommend_next refuses to rank below 5 records per pillar.
````

## 6. Expected output files
- `video_studio/analytics.py`
- `data/content-memory.json` (appended only, when real data exists)
- `data/content-memory.backup.json`
- A printed analytics report (optionally saved to `video_studio/output/_analytics.md`)

## 7. Execution requirements
- `requests`, stdlib only. Official Graph API only. No scraping, no third-party analytics.
- Atomic writes with a prior backup.

## 8. Dependencies on earlier prompts
- PROMPT 14 (real publishes → real media ids), PROMPT 16 (`publish_history`),
  PROMPT 02 (brand + pillars).

## 9. Acceptance criteria
- `ANALYTICS SELF-CHECK PASS (6/6, 0 live calls)` printed.
- Empty history → NO_DATA, zero writes (`git diff --stat data/content-memory.json` empty).
- Missing metrics → `null`, never `0`.
- `plays == 0` → null derived ratios, no exception.
- Recommendations cite their source records; below 5 records/pillar → NO_DATA.
- No fabricated numbers anywhere.

## 10. Verification instructions
```powershell
.venv\Scripts\python.exe -m pytest video_studio\tests\test_analytics.py -v
.venv\Scripts\python.exe -m video_studio.analytics --dry-run
git diff --stat data\content-memory.json      # must be empty with no publish history
Select-String -Path video_studio\analytics.py -Pattern "source.*graph_api_insights"
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Insights 403 | Token lacks `instagram_read_insights` | NO_DATA + reason. Do NOT request the scope automatically. |
| Metrics come back as 0 | Missing field coerced to 0 | Keep it `null`. 0 and "not reported" mean different things. |
| content-memory.json corrupted | Non-atomic write | `.tmp` + `os.replace` + a backup. Restore from the backup. |
| Agent "estimates" a follower count | Blocked page temptation | Forbidden. Null is the answer. |
| Recommendations with no evidence | Model filled the gap | Delete. Every recommendation must cite records. |
| Token leaked into a log | Missing redaction | Add the scrub filter, rotate the token if it leaked. |
| Records below 5 being ranked | Threshold ignored | Enforce the minimum. Five is not a magic number, it's a floor. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 18 — New Video Production (operational)
# ═════════════════════════════════════════════════════════════════════════════

`[RENDERS VIDEO]`

## 1. Prompt title
PROMPT 18 — New Video Production (operational: topic or product URL → full rendered Reel)

## 2. Intended purpose
The **end-user command**. Given a topic or a product URL, produce a complete, QA-verified,
packaged Reel with no further human input. This is the prompt a non-engineer runs.

## 3. When to use it
- Anytime a new Reel is needed.
- Weekly, on the scheduler's cadence (PROMPT 16).
- For the very first production run after the engine is proven.

## 4. Required inputs
- **Exactly one of**: a topic string, or a product URL.
- The whole engine (PROMPTs 06–15) already working.
- `data/content-memory.json` (for anti-repetition).

## 5. Exact copy-paste prompt text

````
Produce a complete Instagram Reel for Signhify Studio, from a topic to a finished,
QA-verified, packaged MP4 — with no further human input.

WORKING DIRECTORY: D:\Autogram
PYTHON: .venv\Scripts\python.exe (3.14.7)
TOOLCHAIN: hyperframes 0.8.58 via `npx hyperframes` from D:\Autogram.
            FFmpeg/ffprobe 8.0.1 on PATH. No CUDA GPU. Docker NOT running.
            Kokoro TTS NOT installed. whisper-cpp NOT installed.

INPUT FROM THE USER (one of):
  TOPIC:  {{TOPIC}}
  URL:    {{PRODUCT_URL}}     (may be empty)

PIPELINE — execute these stages in order. Do not skip ahead.

STAGE 0 — ANTI-REPETITION
  Read data/content-memory.json (and video_studio/briefs/*.json).
  If the requested topic overlaps an existing slug or an existing pillar topic, say so and
  propose a sharper angle BEFORE generating. If it is a duplicate, STOP and ask.
  Never publish two Reels on the same topic.

STAGE 1 — RESEARCH
  If URL is non-empty: fetch it. Record the URL, the UTC timestamp, and success/failure.
  Extract 3-5 facts, each labelled VERIFIED or UNVERIFIED, quoted or closely paraphrased.
  ON FAILURE write exactly:
    "ACCESS LIMIT: <url> unreachable at <UTC timestamp>. Facts below are unverified."
  DO NOT FABRICATE. No invented specs, pricing, users, revenue, testimonials, or results.

STAGE 2 — SCRIPT (per video_studio/prompts/script.md)
  Produce the brief. Enforce:
    - slug ^[a-z0-9][a-z0-9-]{1,60}$
    - topic 10-140 chars | hook <= 90 | cta <= 120
    - 3-6 key_points, each <= 140 chars
    - duration_s 15-60 | aspect "9:16" | pillar from the 6 brand pillars
    - ZERO banned phrases (case-insensitive) in topic/hook/key_points/cta
  Write video_studio/briefs/<slug>.json and video_studio/work/<slug>/script.md.
  Run a validator script and print PASS/FAIL per rule. Fix until green. Never lower a rule.

STAGE 3 — BUILD (no render)
  .venv\Scripts\python.exe -m video_studio build --brief video_studio/briefs/<slug>.json
  Produces: work/<slug>/{index.html, hyperframes.json, package.json, storyboard.json,
            asset_manifest.json}

STAGE 4 — RENDER + QA GATE
  .venv\Scripts\python.exe -m video_studio render --brief video_studio/briefs/<slug>.json
                                          --quality draft --fps 30
  Internally this MUST:
    - run `npx hyperframes check` FIRST; require "0 errors, 0 warnings". A failure exits 3
      and NOTHING is rendered. A warning is a failure.
    - render with -q draft -w 4. NEVER --docker. NEVER --gpu.
    - ffprobe the result and assert 1080x1920, 30/1 fps, h264, yuv420p, duration within
      0.15 s of the storyboard total.
  Then: .venv\Scripts\python.exe -m video_studio qa
          --video video_studio/output/<slug>/reel.mp4 --work video_studio/work/<slug>
  Require verdict PASS.

STAGE 5 — ITERATE IF NEEDED (max 2 attempts)
  If QA fails, read qa_report.md, fix the CAUSE (tokens, template, storyboard timing,
  asset path), and re-render. Two attempts only, then stop and report the blocker.
  Never lower a threshold to force a PASS.

STAGE 6 — PACKAGE
  .venv\Scripts\python.exe -m video_studio package --brief video_studio/briefs/<slug>.json
  Produces: output/<slug>/{cover.jpg (1080x1920), caption.txt, manifest.json}
            plus reel.mp4, captions.srt, script.md, storyboard.json, brief.json,
            asset_manifest.json, qa_report.md, render.log

STAGE 7 — DO NOT PUBLISH
  Leave manifest.published = false and manifest.ig_media_id = null.
  Publishing requires the owner's explicit go-ahead AND the four gates in PROMPT 14.
  Stop here and hand the package to the owner.

STAGE 8 — REPORT (this is what the user reads)
  ## Reel Ready — <slug>
  Topic / Pillar / Duration / FPS / Resolution
  ## Hook           the first 1.5 s line
  ## Timeline       a table of scenes: # | type | start | dur | on-screen text
  ## Assets         count by source; every blocker listed
  ## QA             verdict + the measured ffprobe numbers + frame luma summary
  ## Cover          cover.jpg path, resolution, extracted at t=<n>s
  ## Caption        the full caption.txt, verbatim
  ## Files          a table of every file in output/<slug>/ with bytes and sha256
  ## Blockers       anything that degraded. If none: "None."
  ## Next Step      "To publish: `python -m video_studio publish --slug <slug>` after
                     enabling VIDEO_STUDIO_PUBLISH=true and setting DRY_RUN=false."
  ## Verification    the exact commands you ran and their real output (ffprobe JSON, the
                     `npx hyperframes check` result, the QA verdict)

HARD RULES
  - Never fabricate a capability, metric, testimonial, customer result, or revenue.
  - Never print or commit an API key or token.
  - Never claim it rendered / passed / published without real command output in the report.
  - Never bypass Instagram auth or platform security.
  - Do not activate a paid API without explicit owner authorization.
  - Respect the 16 banned phrases in every string of copy.
  - Inspect before modifying. Preserve existing code.
  - instagram.com/signhify.studio was BLOCKED at research time — never fabricate post
    performance.

ACCEPTANCE
  - video_studio/output/<slug>/reel.mp4 exists and ffprobes to 1080x1920 / 30fps / h264 /
    yuv420p / duration within 0.15 s of the storyboard.
  - qa_report.md verdict is PASS.
  - cover.jpg is 1080x1920 (not 1080x1350).
  - caption.txt is <= 2200 chars with 0 banned-phrase hits.
  - manifest.json exists with published=false and ig_media_id=null.
  - render.log contains the verbatim "0 errors, 0 warnings" check output.
  - The STAGE 8 report contains REAL command output, not a description of it.
````

## 6. Expected output files
The complete `video_studio/output/<slug>/` set (11 artifacts) plus
`video_studio/briefs/<slug>.json` and `video_studio/work/<slug>/` (project + assets).

## 7. Execution requirements
- `python -m video_studio` for build/render/qa/package. Never a manual hand-build.
- `-q draft -w 4`; no `--docker`, no `--gpu`, no `-q high`.
- Network only for the optional URL fetch and (if configured) TTS. Neither is required.

## 8. Dependencies on earlier prompts
- PROMPT 15 (the CLI), with 08–14 implemented beneath it. PROMPT 07's system prompt is the
  content gate.

## 9. Acceptance criteria
- `reel.mp4` ffprobes correctly; `qa_report.md` PASS.
- `cover.jpg` is 1080×1920.
- `caption.txt` ≤ 2200 chars, zero banned-phrase hits.
- `manifest.json` has `published: false`, `ig_media_id: null`.
- `render.log` shows "0 errors, 0 warnings".
- STAGE 8 report contains real ffprobe JSON and the real QA verdict.

## 10. Verification instructions
```powershell
ffprobe -v error -show_streams -show_format -of json video_studio\output\<slug>\reel.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 video_studio\output\<slug>\cover.jpg
Select-String -Path video_studio\output\<slug>\render.log -Pattern "0 errors, 0 warnings"
Select-String -Path video_studio\output\<slug>\qa_report.md -Pattern "PASS"
.venv\Scripts\python.exe -c "import json;m=json.load(open('video_studio/output/<slug>/manifest.json',encoding='utf-8'));assert m['published'] is False;print('NOT PUBLISHED — correct')"
Get-ChildItem video_studio\output\<slug> | Select-Object Name, Length
```

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| `npx hyperframes check` warns | Contrast or layout | Fix the cause. A warning is a failure — do not render over it. |
| QA fails on frame luma delta | Video is effectively frozen | The timeline is not animating. Verify `window.__timelines` key matches `data-composition-id`. |
| Scenes overlap | `data-track-index` trusted | Display-only. Use CSS z-index from `scene["z_index"]`. |
| render.mp4 is 0 bytes | Render crashed silently | Read `render.log`. Never trust the exit code alone — ffprobe. |
| Cover is 1080×1350 | Wrong asset | Extract from reel.mp4; the carousel JPGs are the wrong size. |
| Voiceover missing | Kokoro not installed | Expected. The pipeline is designed to ship silent. Do not install. |
| Two attempts both fail QA | Real defect, not a flake | STOP. Report the blocker with qa_report.md contents. Do not force a PASS. |
| Script fabricates a statistic | Model drift | Delete the number and re-run the banned/fabrication sweep. |

---

# ═════════════════════════════════════════════════════════════════════════════
# PROMPT 19 — End-to-End Production Audit
# ═════════════════════════════════════════════════════════════════════════════

`[AUDIT]`

## 1. Prompt title
PROMPT 19 — End-to-End Production Audit

## 2. Intended purpose
Verify that the whole engine still works, still fails closed, and still tells the truth —
after months of accumulated changes. This is the audit that catches silent drift: brand
tokens that drifted from `brand.json`, a QA gate that stopped failing, a publish path that
lost its gate, copy that crept banned phrases back in.

## 3. When to use it
- Monthly.
- After any `hyperframes` or Node upgrade.
- Before any release, deploy, or handover.
- Immediately after any suspected regression.

## 4. Required inputs
- The entire `video_studio/` package.
- All upstream docs in `docs/video-studio/`.
- `data/brand.json` (the authority for brand drift checks).
- At least one existing `video_studio/output/<slug>/` for artifact verification.
- `npx hyperframes` on PATH.

## 5. Exact copy-paste prompt text

````
You are auditing a video production engine end to end. Assume nothing works until you
prove it. Working directory: D:\Autogram.

SCOPE — audit these nine axes. Report on each.

AXIS 1 — ENVIRONMENT TRUTH
  Re-run the key probes: node --version, npm --version, .venv\Scripts\python.exe --version,
  ffmpeg -version, npx hyperframes --version, docker version, nvidia-smi.
  Compare against docs/video-studio/ENVIRONMENT_AUDIT.md.
  Report every drift. Installed hyperframes is 0.8.58; upstream latest is 0.8.145 — report
  the delta and whether the engine depends on any removed behaviour.

AXIS 2 — BRAND DRIFT (the most common silent regression)
  Write a script that compares, field by field:
    video_studio/brand_tokens.json  vs  data/brand.json
  Check: handle, watermark, sign_off, footer_text, positioning, every color, every font,
  and the `avoid` list (must be exactly 16, identical strings).
  Then grep EVERY .py, .jinja2, .css, and .md under video_studio/ and templates for:
    - hardcoded hex colours outside design/tokens.css
    - hardcoded font names outside tokens.css
    - any of the 16 banned phrases in template defaults, example copy, or docstrings
  Report every hit with file:line.

AXIS 3 — THE QA GATE STILL FAILS
  A gate that cannot fail is a broken gate. Prove QA still fails:
    (a) render a 1080x1920 SOLID-COLOUR 4 s clip -> qa() must exit 3 on the luma-delta check
    (b) create a 640x360 clip              -> qa() must exit 3 on the container check
    (c) point qa at a nonexistent path     -> qa() must exit 1
  Run PROMPT 12's self-check. Report the actual exit codes, not an expectation.

AXIS 4 — HYPERFRAMES CONTRACT COMPLIANCE
  Scan every generated index.html under video_studio/work/:
    - root has data-composition-id, data-width, data-height, data-start, data-duration
    - every timed element has class="clip"
    - data-start/data-duration are plausible SECONDS (0 <= start, 0 < duration,
      start+duration <= total + 0.5)
    - gsap.timeline({paused:true}) is present and assigned to
      window.__timelines["<data-composition-id>"]
    - every GSAP third argument is a NUMBER. Flag any ">", "+=...", "-=...", or "<".
    - only whitelisted props animate: opacity, x, y, scale, scaleX, scaleY, rotation,
      width, height, visibility. Flag anything else.
    - `npx hyperframes check` currently reports "0 errors, 0 warnings" for each project.
  Report a per-project table.

AXIS 5 — THE PUBLISH GATE STILL HOLDS
  Confirm in source that publishing requires ALL FOUR:
    VIDEO_STUDIO_PUBLISH=true, DRY_RUN!=true, IG_USER_ID non-empty, IG_ACCESS_TOKEN
    non-empty.
  Then PROVE it, without live credentials:
    - unset VIDEO_STUDIO_PUBLISH -> publish exits 4 with ZERO network calls
    - DRY_RUN=true                -> publish exits 4 with ZERO network calls
  Grep the entire repo for hardcoded credentials:
    Select-String -Recurse -Pattern "EA[A-Za-z0-9]{20,}" and similar token shapes.
  Report every hit. A single hit is a CRITICAL finding.

AXIS 6 — OUTPUT ARTIFACT INTEGRITY
  For each existing video_studio/output/<slug>/:
    - all 11 expected artifacts present and non-empty
    - reel.mp4 ffprobes to 1080x1920, h264, yuv420p, duration matching storyboard (+/-0.15s)
    - cover.jpg is 1080x1920 (flag any 1080x1350 — a carousel image leaked in)
    - manifest.json has a valid sha256 for video AND cover, and sha256 matches the file NOW
    - qa_report.md verdict is PASS
    - caption.txt <= 2200 chars, sign-off exactly once, 0 banned-phrase hits
    - manifest.published is true IFF ig_media_id is non-null
  Report a per-slug table.

AXIS 7 — BANNED-PHRASE SWEEP (live content)
  Sweep video_studio/work/*/script.md, video_studio/output/*/caption.txt, and every
  captions.srt for the 16 banned phrases plus variants:
    game changing, game-changing, revolutionary, cutting-edge, seamlessly, unlock,
    dive into, at its core, next gen, next-gen, must have, must-have, in today's,
    ultimate secret, power of
  Report every hit with file:line. Any hit is a FAIL for that artifact.

AXIS 8 — FABRICATION AUDIT
  Grep all generated copy and all source prompts for:
    - invented statistics ("X% faster", "10x", specific numbers with no source)
    - invented testimonials, customer names, logos
    - invented revenue, user counts, or follower counts
    - any Instagram performance claim
  For each hit, determine whether it is traceable to a verified source (the confirmed
  product-fact list, the Graph API insights in content-memory.json) or fabricated.
  Report FABRICATED CLAIMS as CRITICAL.
  Note: instagram.com/signhify.studio was BLOCKED at research time. Any claim about the
  account's real performance is fabricated unless it cites a graph_api_insights record.

AXIS 9 — REPRODUCIBILITY
  Pick the most recent slug. Re-run its render from scratch at -q draft into a temp dir.
  Confirm: identical storyboard.json (byte-for-byte), identical script/brief (byte-for-byte),
  and a reel.mp4 with the same duration, fps, and codec.
  Report any nondeterminism. Randomness or timestamps in generated JSON is a defect —
  the pipeline must be deterministic.

WRITE THE REPORT — docs/video-studio/E2E_AUDIT.md
  ## Verdict          PASS / PASS-WITH-FINDINGS / FAIL, with the count of each severity
  ## Summary           a table: Axis | Status | Findings | Severity
  ## Findings          each as: ID, SEVERITY (CRITICAL/HIGH/MEDIUM/LOW), file:line,
                      what is wrong, the exact evidence, and the concrete fix
  ## Drift             environment and brand drift vs the upstream docs
  ## Remediation Order  a numbered, dependency-ordered fix list. Fix CRITICALs first.
  ## Appendix          raw ffprobe JSON, check outputs, sweep output, exit codes

RULES
  - This prompt is READ-ONLY on the engine. Do not fix anything. Report only.
  - Do not install packages, do not start Docker, do not run playwright install.
  - Do not make any live API call. All credentialed paths must be proven with mocks or
    with the gate blocked.
  - Never print a token. If you find one in source, report the file:line and the fact that a
    credential is exposed — DO NOT reproduce the value. Recommend rotation.
  - Never fabricate a finding. If you cannot evidence it, say UNVERIFIED.
  - Respect the 16 banned phrases in the report's own prose.

ACCEPTANCE
  - docs/video-studio/E2E_AUDIT.md exists with all 8 sections.
  - All 9 axes have a PASS/FAIL status backed by real command output.
  - Axis 3 proves QA still fails, with actual exit codes (3, 3, 1).
  - Axis 5 proves the publish gate still blocks, with zero network calls.
  - Every finding has file:line, evidence, and a fix.
  - Nothing in video_studio/ was modified by this audit (verify with git status).
````

## 6. Expected output files
- `docs/video-studio/E2E_AUDIT.md`
- Temporary QA fixtures under the OS temp dir (solid-colour and wrong-size clips)

## 7. Execution requirements
- Read-only against `video_studio/`. `git status` must be clean of engine changes afterward.
- Mocked or gate-blocked credential paths only. Zero live API calls.
- No installs, no Docker startup, no `playwright install`.

## 8. Dependencies on earlier prompts
- All of them. This is the terminal audit.

## 9. Acceptance criteria
- All 9 axes reported with real command output.
- QA proven to fail (exit 3, 3, 1 for the three fixtures).
- Publish gate proven to block with zero network calls.
- Brand drift between `brand_tokens.json` and `data/brand.json` is zero.
- Every finding has `file:line`, evidence, and a concrete fix.
- `git status` shows no modifications to `video_studio/`.

## 10. Verification instructions
```powershell
git status --short
git diff --stat video_studio\
Select-String -Path docs\video-studio\E2E_AUDIT.md -Pattern "CRITICAL"
Select-String -Path docs\video-studio\E2E_AUDIT.md -Pattern "## Drift"
# Re-run the three critical axes yourself:
.venv\Scripts\python.exe -m video_studio.qa --video <solid-colour-fixture> ; $LASTEXITCODE   # expect 3
$env:VIDEO_STUDIO_PUBLISH="false"; .venv\Scripts\python.exe -m video_studio.publish <slug> ; $LASTEXITCODE  # expect 4
```
If you cannot reproduce the reported exit codes, the audit is wrong — re-run it.

## 11. Common failure cases and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| QA exits 0 on a solid-colour clip | The luma-delta check was removed or weakened | Restore it. A gate that cannot fail is not a gate. This is a CRITICAL finding. |
| `brand_tokens.json` colors differ from `brand.json` | Manual edit | `data/brand.json` is authoritative. Regenerate tokens from it. |
| Hardcoded hex in a template | Convenience edit | Move it to `tokens.css` and reference `brand_tokens.json`. |
| Publish succeeded without the opt-in | Gate removed | Restore all four gates and re-run the self-check. CRITICAL. |
| A credential appears in source | Leaked during an earlier debug | Do NOT reproduce the value. Recommend immediate rotation, then remove from source. |
| Banned phrase in a caption | Copy regression | Fix the caption, re-sweep. Consider blocking the phrase in `brief.py` validation. |
| Re-render produced a different storyboard.json | Non-determinism (RNG or timestamps) | Remove `random`; exclude wall-clock timestamps from generated JSON. |
| Environment drift block is empty | Probes not actually run | Re-run each probe and paste the real output. |
| Audit modified `video_studio/` | Scope creep | `git checkout -- video_studio\` and re-run read-only. |

---

## Appendix A — Quick reference: every real command in this pack

```powershell
# Toolchain
npx hyperframes --version                        # 0.8.58 (Apache-2.0); upstream 0.8.145
npx hyperframes doctor
npx hyperframes init _smoke --example title-card  # --example, NOT --template
npx hyperframes render -f 30 -q draft -w 4 -o out.mp4
npx hyperframes check                            # QA gate: Runtime+Layout+Motion+Contrast+Snapshots
npx hyperframes snapshot
npx hyperframes inspect
npx hyperframes lint
npx hyperframes compositions
npx hyperframes timeline
npx hyperframes info
npx hyperframes docs <topic>
npx hyperframes transcribe                       # whisper-cpp NOT installed
npx hyperframes tts                              # Kokoro NOT installed
npx hyperframes normalize-audio

# Video verification
ffprobe -v error -show_streams -show_format -of json <file.mp4>
ffmpeg -y -ss <t> -i <in> -frames:v 1 -q:v 2 <out.jpg>

# Engine CLI
python -m video_studio build   --brief video_studio/briefs/<slug>.json
python -m video_studio render  --brief video_studio/briefs/<slug>.json --quality draft --fps 30
python -m video_studio qa      --video video_studio/output/<slug>/reel.mp4 --work video_studio/work/<slug>
python -m video_studio package --brief video_studio/briefs/<slug>.json
python -m video_studio publish --slug <slug>          # blocked unless all 4 gates pass
python -m video_studio list
python -m video_studio.scheduler --dry-run
python -m video_studio.analytics --dry-run
```

## Appendix B — Sign-off for agents running this pack

Run the full pack in order. Prove every claim with a command. When something is blocked,
unavailable, or unverified — say so in plain words and move on. A short honest report
beats a long confident one, every time.

- Do not fabricate. Ever.
- Do not print a credential. Ever.
- Do not publish without the owner's explicit go-ahead.
- Respect the 16 banned phrases.

`My name is Piyush Raj Singh. Stop posting. Start shipping.`
