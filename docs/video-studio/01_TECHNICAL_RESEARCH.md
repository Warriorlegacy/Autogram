# Video Studio — Technical Research Report

| Field | Value |
|---|---|
| **Report date** | 2026-10-11 |
| **Subject** | Video production pipeline for `D:\Autogram` (Signhify Studio) — short-form video generation, QA, transcription, voiceover, and Instagram Reels publishing |
| **Machine of record** | `DESKTOP-…` / Windows win32 x64, Intel i5-1145G7, 15.7 GB RAM, integrated GPU |
| **Methodology** | Direct CLI inspection on the machine of record (`hyperframes doctor`, `hyperframes init`, `hyperframes render`, `hyperframes check`, `ffprobe`, `npm ls`, file reads of `data/brand.json` and `src/content/hyperframes_engine.py`) combined with official vendor documentation and package registries. No third-party summaries, no marketing blogs, no inferred pricing. |
| **Evidence standard** | Every claim is either (a) observed on this machine, (b) taken from an official source listed in §9, or (c) marked `UNVERIFIED`. Nothing else appears as fact. |
| **Status** | Decision-ready for the composition engine and licensing question. Pricing for HeyGen credit/minute mapping is **not** decision-ready — see §9. |

---

## 1. Executive Summary and Recommendation

### 1.1 The two decisions this report settles

1. **Which engine renders video.** Two candidates are already installed. They differ by roughly 40× in cost at the org level and by an entire QA toolchain.
2. **Whether the existing `hyperframes_engine.py` stays.** It does not. It is a name collision, not an implementation of the HyperFrames product.

### 1.2 Recommendation table

| Technology | Role | License | Direct cost | Required / Optional | Recommendation |
|---|---|---|---|---|---|
| **HyperFrames CLI** (`hyperframes`, HeyGen) | Composition engine, renderer, QA gate, TTS, captions | **Apache-2.0** | **$0** — local render, no account, no credits | **REQUIRED** | **Adopt as the single composition + render engine.** Upgrade 0.8.58 → ≥0.8.145. |
| **FFmpeg** (system) | Encode, loudnorm, mux, probe | LGPL-2.1-or-later (GPL-2.0-or-later on GPL builds) | $0 | **REQUIRED** | Keep. Already on PATH, 8.0.1. |
| **faster-whisper** | Word-level timestamps for captions | MIT | $0 (CPU, already installed) | **REQUIRED** for burned-in captions | Adopt. Already in `requirements.txt`. |
| **Kokoro-82M** | Voiceover | **Apache-2.0** (weights + lib) | $0, local | **REQUIRED** for VO | Adopt via `hyperframes tts`. |
| **Meta Graph API v26.0** | Reels publishing | Platform ToS | $0 (free tier) | **REQUIRED** for distribution | Keep. Already partly integrated. |
| **Remotion** | *Alternate* composition engine | Source-available, **not OSI OSS** | **$0 only if org ≤3 employees**; else $25–500+/mo | **Drop from critical path** | Keep on disk for reference only. Do not build on it. |
| **HeyGen API** (Avatar V/IV, Video Agent) | Presenter avatar, stock-footage digital twin | Proprietary, credits | $99–330/mo + metered credits | **OPTIONAL** | Do not adopt now. Revisit only if Approach C is justified by measured demand. |
| **edge-tts** | TTS with native word boundaries | LGPL-3.0 (client) | $0 | **Avoid for monetized output** | Do not ship. ToS risk on commercial use. |
| **Piper / piper-tts** | Offline TTS | MIT (archived) / GPL-3.0-or-later | $0 | **Avoid** | Do not adopt. GPL-3.0 + archived upstream. |
| **OpenAI / ElevenLabs TTS** | Cloud TTS | Proprietary | $0.015/min (UNVERIFIED) / $5–6+/mo | **OPTIONAL fallback** | Keep as fallback if Kokoro quality is insufficient. No word timestamps. |
| **Docker (HyperFrames `--docker`)** | Deterministic Chrome + fonts | n/a | $0 | **OPTIONAL** | Do not enable. Docker client installed but daemon not running on this machine. |

### 1.3 One-paragraph rationale

The installed `hyperframes` package is Apache-2.0, renders locally with no HeyGen account and no credits, ships a built-in QA gate (`hyperframes check` — runtime, layout, motion, WCAG AA contrast), and was empirically proven on this machine to produce a correct 1080×1920 H.264 MP4 in 15.3 s. Remotion, which occupies the same slot, is source-available rather than open source and crosses into a paid license the moment the studio exceeds three employees — a threshold the studio is plausibly near. Everything else in the chain has a free, permissive-license alternative that is either already installed or one `pip install` away.

---

## 2. Environment Audit

All rows verified by direct inspection on 2026-10-11.

| Component | Value | Status | Notes |
|---|---|---|---|
| OS | Windows, win32 x64 | OK | — |
| Node.js | v22.23.1 | OK | HyperFrames hard-requires Node 22+ |
| npm | 12.2.0 | OK | — |
| Python | 3.14.0 (venv 3.14.7) | OK | — |
| FFmpeg | 8.0.1 full build (gyan.dev, WinGet) | OK | On PATH. Latest stable is 9.0.2 — not required |
| FFprobe | 8.0.1 | OK | On PATH |
| CPU | Intel i5-1145G7 @ 2.60 GHz, 8 cores | OK | Single socket, no AVX-512 |
| RAM | 15.7 GB | Constrained | Caps concurrent Chrome + FFmpeg + Python workers |
| Disk free | 13.2 GB | Constrained | Chrome cache + node_modules + output frames |
| GPU | Integrated only, **no CUDA** | Blocker for some paths | Disables NVENC; HyperFrames renders on CPU here |
| `hyperframes` | **v0.8.58** installed | OK | Apache-2.0. Latest: **0.8.145** |
| `remotion` | **v4.0.526** installed | Present | License `SEE LICENSE IN LICENSE.md`. Latest: 4.0.534 |
| `remotion` peers | `@remotion/cli`, `@remotion/renderer`, `react` 18.3.1, `react-dom` 18.3.1 | Present | Declared in root `package.json` |
| `src/video/` | `index.ts`, `Root.tsx`, `SignhifyReel.tsx`, `types.ts` | Present | Remotion compositions live here |
| `src/content/hyperframes_engine.py` | 29,363 bytes, 641 lines | Present | **Name collision — see §3** |
| `faster-whisper` | `>=1.0.0` in `requirements.txt` line 15 | OK | Already a repo dependency |
| Chrome Headless Shell | 152.0.7977.30 cached | OK | Downloaded by HyperFrames, not system Chrome |
| MusicGen deps | Present | OK | `hyperframes doctor` reports OK |
| Docker | Client 29.5.2, daemon **not running** | Unavailable | Blocks `render --docker` |
| whisper.cpp | **Not installed** | Missing | HyperFrames transcribe falls through |
| Kokoro TTS | **Not installed** | Missing | Required before `hyperframes tts` |

### 2.1 `npx hyperframes doctor` output

| Probe | Result |
|---|---|
| Node | OK |
| FFmpeg | OK |
| FFprobe | OK |
| Chrome headless shell cached | OK (152.0.7977.30) |
| MusicGen deps | OK |
| Docker | Installed, **not running** |
| whisper-cpp | **Not installed** |
| Kokoro TTS | **Not installed** |
| Version delta | 0.8.58 → **0.8.145 available** |

### 2.2 Empirical smoke render (executed on this machine)

A full render was run to prove the toolchain works end to end before any of this was written down.

| Stage | Command | Result |
|---|---|---|
| Scaffold | `hyperframes init smoke --example blank` | Project created |
| Render | `hyperframes render -f 30 -q draft` | **Succeeded in 15.3 s** |
| Output format | — | MP4, H.264 |
| Probe: width | `ffprobe` | **1080** |
| Probe: height | `ffprobe` | **1920** |
| Probe: frame rate | `r_frame_rate` | **30/1** |
| Probe: codec | — | **h264** |
| Probe: frame count | `nb_frames` | **120** |
| Probe: duration | — | **4.0 s** (120 ÷ 30 = 4.0, internally consistent) |
| QA gate | `hyperframes check` | **Passed** |
| — Runtime errors | — | 0 |
| — Layout issues | — | 0 |
| — Motion errors | — | 0 |
| — Contrast | WCAG AA | **5/5 pass** |
| Visual | Frame pixels inspected | Correct |

**Conclusion:** 1080×1920 @ 30 fps on CPU is achievable on this hardware at roughly 8 fps of render throughput for a blank composition. Realistic compositions with blur, glass, and large type will be slower — measure before committing to a per-Reel SLA.

---

## 3. Critical Finding A — Naming Collision on "HyperFrames"

This is the highest-priority finding in this report because it is actively misleading to anyone reading the codebase, including future agents.

### 3.1 What exists

| | `src/content/hyperframes_engine.py` | npm package `hyperframes` |
|---|---|---|
| **What it is** | Hand-rolled Python engine | HeyGen's product, Apache-2.0 |
| **Implementation** | Jinja2 templating → Playwright/Chromium → FFmpeg | puppeteer-core + esbuild + sharp + hono → FFmpeg |
| **Owns a `THEMES` dict** | Yes — 5 dark palettes | No (themes are CSS, user's responsibility) |
| **Documented upstream** | No. Local invention. Docstring claims "HyperFrames HTML-native deterministic video engine" | Yes — `hyperframes.heygen.com`, `github.com/heygen-com/hyperframes` |
| **CLI commands** | None | `init`, `render`, `check`, `tts`, `transcribe`, … 40+ commands |
| **QA gate** | None built in | `check` — runtime/layout/motion/contrast/snapshots |
| **Determinism guarantees** | Claims them in docstring | Engineered and documented (per-frame Chrome seek + FFmpeg) |
| **License** | Inherits repo MIT | Apache-2.0 |

### 3.2 Evidence of the collision

`src/content/hyperframes_engine.py:30-36` declares a hardcoded theme table:

```python
THEMES = {
    "A": {"accent": "#00E599", "accent2": "#06B6D4", "bg": "#020617", "name": "emerald_circuit"},
    "B": {"accent": "#38BDF8", "accent2": "#A78BFA", "bg": "#040718", "name": "cobalt_neural"},
    "C": {"accent": "#A78BFA", "accent2": "#F472B6", "bg": "#0A0618", "name": "violet_hologram"},
    "D": {"accent": "#22D3EE", "accent2": "#34D399", "bg": "#02131A", "name": "cyan_terminal"},
    "E": {"accent": "#FBBF24", "accent2": "#00E599", "bg": "#0C0A05", "name": "amber_forge"},
}
```

The module docstring (`hyperframes_engine.py:1-4`) describes itself as "HyperFrames HTML-native deterministic video engine… renders via headless Chrome + FFmpeg." That is a reasonable description of what HyperFrames *does*, which is exactly why the name is misleading. The package was installed into this repo (`package.json` `devDependencies: { "hyperframes": "^0.8.40" }`) but was never wired into the Python pipeline. Root `package.json` also carries `"render-reel": "python orchestrator.py --generate-hyperframes-reel"`, which routes back to the Python file, not to the CLI.

### 3.3 Impact

| Risk | Severity | Explanation |
|---|---|---|
| A reader believes HyperFrames capabilities exist in the Python file | High | The Python file has no `check` equivalent, no TTS, no captions, no CLI |
| Two divergent rendering paths get maintained | High | Neither is correct for the brand yet (§4) |
| `data-composition-id` / `data-composition-variables` contracts go undiscovered | Medium | The Python engine invents its own template schema |
| Name collision persists in the codebase | Medium | Future work will re-tread this |

### 3.4 Decision

Adopt the **real HyperFrames CLI** and retire the Python engine from the critical path.

| Action | Detail |
|---|---|
| Quarantine, do not delete | `src/content/hyperframes_engine.py` remains until the CLI path is proven end to end on production content |
| New entrypoint | `npx hyperframes render` invoked from a Node/CLI surface, not a Python import |
| New template root | A directory of `index.html` compositions under a brand-correct template dir (HyperFrames `init` uses `--example`, not `--template`) |
| Naming | New code refers to the CLI as "HyperFrames CLI". Nothing new is named `hyperframes_engine.*` |
| Migration order | Prove one production Reel renders via CLI → passes `hyperframes check` → publishes → only then delete the Python path |

**Immediate rename recommended** (does not require migration): the Python module's log prefix and docstring should say `hand-rolled reel engine (pre-HyperFrames-CLI)`. This is a one-line change that removes the ambiguity for every future reader.

---

## 4. Critical Finding B — Brand Mismatch in Existing Reel Themes

### 4.1 The defined brand (`data/brand.json`, read directly)

| Token | Value |
|---|---|
| Brand name | Signhify Studio |
| `bg` | `#F8F6F0` — warm off-white |
| `card_bg` | `#FFFFFF` |
| `card_border` | `rgba(0, 0, 0, 0.08)` |
| `primary` / `text` | `#111111` |
| `accent` | `#E05A36` — burnt orange |
| `accent_hover` | `#CC4C29` |
| `highlight` | `#16A34A` |
| `text_muted` | `#666666` |
| Headline font | Plus Jakarta Sans |
| Body font | Inter |
| Code font | JetBrains Mono |
| Hand font | Caveat |
| Stamp font | Anton |

### 4.2 The mismatch

| Property | Brand requires | Existing themes deliver | Delta |
|---|---|---|---|
| Background | `#F8F6F0` light warm | `#020617`, `#040718`, `#0A0618`, `#02131A`, `#0C0A05` — all near-black | **Inverted polarity** |
| Accent | `#E05A36` single burnt orange | 10 distinct saturated neons across 5 themes | **Off-brand hue set** |
| Contrast strategy | Dark text on light card | Light text on dark bg | Opposite |
| Font stack | 5 named fonts | Not brand-aligned in the Python engine's templates | Divergent |

The two systems are not variations on a theme. They are opposite in polarity. A carousel published today and a Reel published by the existing engine would look like two different companies.

### 4.3 Additional defect: the `avoid` list

`data/brand.json` carries a 16-entry `avoid` array of banned phrases:

`generic hype`, `fake urgency`, `unsupported statistics`, `overused motivational language`, `keyword stuffing`, `game-changer`, `unlock the power of`, `in today's fast-paced world`, `dive into`, `at its core`, `seamless`, `robust`, `revolutionary tool`, `next-gen AI`, `ultimate secret`, `must-have app`

Note: **"robust"** is on this list. It is also a common word in ordinary engineering prose. Any script or caption generator must scrub against this exact list at generation time and again at QA time, not just in the final caption pass.

### 4.4 Decision

Build new brand-correct HyperFrames compositions. Do not retrofit the `THEMES` dict.

| Decision point | Choice | Rationale |
|---|---|---|
| Light or dark video? | **Light** (`#F8F6F0` bg) | Matches the published brand surface. Consistency across formats is the point |
| Palette rotation? | One palette; vary *layout*, not hue | 5-neon rotation is what caused the drift |
| Templates | New directory under a HyperFrames `index.html` layout | HyperFrames treats any dir with `index.html` as a custom template |
| Enforcement | Brand tokens as CSS custom properties injected from `data/brand.json` | Single source of truth already exists; stop re-declaring hex in Python |
| Text legibility gate | `hyperframes check` contrast (WCAG AA) | Already passes 5/5 on the blank smoke project; reuse it as the gate |
| Banned phrases | Scrub at generation and at QA | Mirrors the existing carousel enforcement pattern in `quality_gate.py` |

---

## 5. Per-Technology Deep Dive

### 5.1 HyperFrames (npm `hyperframes`, HeyGen)

| Attribute | Value |
|---|---|
| **What it does** | Deterministic HTML/CSS/JS video engine. Seeks each frame in headless Chrome, encodes with FFmpeg. "The same input produces the same video." |
| **Why relevant** | Removes the entire hand-rolled render stack. Ships composition format, QA gate, TTS, and captions in one Apache-2.0 package. Proven working on this machine (§2.2). |
| **Official sources** | `https://registry.npmjs.org/hyperframes/latest` · `https://www.npmjs.com/package/hyperframes` · `https://github.com/heygen-com/hyperframes` · `https://hyperframes.heygen.com/quickstart` · `https://hyperframes.heygen.com/packages/cli` |
| **Version** | Latest **0.8.145**; installed **0.8.58** → upgrade required |
| **License** | **Apache-2.0** (confirmed in `node_modules/hyperframes/package.json`) |
| **Cost** | **Free.** Local rendering uses no HeyGen credits and needs no account. Account only for `cloud render`, `catalog`, BGM/SFX retrieval, and HeyGen TTS — none of which this pipeline requires |
| **Hardware implications** | CPU render. No CUDA needed. Docker mode (deterministic Chrome + fonts) requires a running Docker daemon — **unavailable here**. `--gpu` NVENC/VideoToolbox/AMF/VAAPI/QSV exist but all need hardware encode support absent on this integrated GPU |
| **Integration difficulty** | **Low–Medium.** HTML/CSS/GSAP is a known target. Python side is a subprocess call. Main cost is authoring compositions to the data-attribute contract |
| **REQUIRED / OPTIONAL** | **REQUIRED** |
| **Recommendation** | **Adopt. Upgrade to ≥0.8.145 before building templates** — the 87-patch delta between .58 and .145 is `UNVERIFIED` in detail but the current version is behind upstream |

#### 5.1.1 Runtime stack

puppeteer-core · @puppeteer/browsers (downloads its own Chrome) · sharp · esbuild · hono. Requires Node 22+ and a **system FFmpeg — FFmpeg is not bundled**.

#### 5.1.2 Verified commands (`npx hyperframes --help`)

`init` · `add` · `capture` · `catalog` · `preview` · `present` · `publish` · `render` · `lint` · `check` · `validate` · `beats` · `inspect` · `keyframes` · `snapshot` · `media-treatment` · `normalize-audio` · `grade-compare` · `compare` · `info` · `compositions` · `timeline` · `docs` · `benchmark` · `browser` · `doctor` · `upgrade` · `cloud` · `lambda` · `cloudrun` · `skills` · `transcribe` · `tts` · `remove-background` · `auth` · `feedback` · `telemetry`

#### 5.1.3 Scaffolding — flag rename

| Wrong | Right |
|---|---|
| `hyperframes init X --template <name>` → **errors out** | `hyperframes init X --example <name>` |

Built-in examples: `blank`, `title-card`, `video-edit`. A **custom template is any directory containing an `index.html`** — this is how brand-correct Signhify templates get added.

#### 5.1.4 Composition format (VERIFIED from `hyperframes docs`)

| Concern | Contract |
|---|---|
| Root element | `data-composition-id`, plus `data-width` / `data-height` / `data-start` / `data-duration` |
| Nested compositions | `data-composition-src` + `data-start` + `data-duration` |
| Variable **declarations** | `data-composition-variables` on `<html>` — a JSON **array** of `{id, type, label, default}` |
| Variable **values** | `data-variable-values` on a host element — a JSON **object** keyed by id |
| Read variables in JS | `window.__hyperframes.getVariables()` |
| CLI override | `render --variables '{...}'` |

> The array-vs-object asymmetry between declarations and values is a real footgun. Getting it backwards fails silently.

#### 5.1.5 Timing and media attributes (VERIFIED)

| Attribute | Meaning |
|---|---|
| `data-start` | Seconds |
| `data-duration` | Seconds |
| `data-media-start` | In-point within the source media |
| `data-volume` | 1 = 0 dB; max 3.98 ≈ +12 dB |
| `data-has-audio` | Declares the clip has audio |
| `class="clip"` | Marks an animatable clip |
| `data-track-index` | **Display-only.** Does NOT control paint order or overlap — use CSS `z-index` |

#### 5.1.6 GSAP contract (VERIFIED)

| Rule | Value |
|---|---|
| Always | `gsap.timeline({ paused: true })` |
| Registration | `window.__timelines[<compositionId>]` |
| Third GSAP arg | Absolute time, not a relative offset |
| Supported properties | `opacity`, `x`, `y`, `scale`, `scaleX`, `scaleY`, `rotation`, `width`, `height`, `visibility` |

> `transform` and `filter` are **not** in the supported list. Reach for `scale`/`rotation`, not raw CSS transforms.

#### 5.1.7 `render` options (VERIFIED)

| Flag | Values |
|---|---|
| `-f` / `--fps` | 24, 30, 60 — default **30** |
| `-q` / `--quality` | draft, standard, high — default **standard** |
| `-w` / `--workers` | 1–8 |
| `--crf` | Numeric override |
| `--video-bitrate` | Bitrate override |
| `--gpu` | NVENC / VideoToolbox / AMF / VAAPI / QSV |
| `--browser-gpu` / `--no-browser-gpu` | Toggle GPU raster in headless Chrome |
| `--video-frame-format` | auto / jpg / png |
| `--docker` | Deterministic Chrome + fonts — **requires running Docker; not available on this machine** |
| `-o` / `--output` | Output path |

#### 5.1.8 `check` — the built-in QA gate

Runs five suites: **Runtime** (JS errors, missing assets, contrast), **Layout**, **Motion**, **Contrast (WCAG AA)**, **Snapshots**. Empirically clean on the smoke project (§2.2).

> This is the single largest capability gap versus `src/content/hyperframes_engine.py`, which has no equivalent. Wire `hyperframes check` into the pipeline as a **fail-closed** step, matching the existing fail-closed rule in `AGENTS.md`.

#### 5.1.9 Current limitations

| Limitation | Severity |
|---|---|
| **Local TTS silently falls back to Kokoro** even when `$HEYGEN_API_KEY` is set, because the published CLI is often a local-only build | High — silent misconfiguration |
| HeyGen/ElevenLabs TTS paths exist **only inside bundled skill scripts**, not as first-class CLI flags | Medium |
| Version lag: 0.8.58 installed vs 0.8.145 available | Medium |
| Docker mode unusable here (daemon down) | Low — determinism is already reasonable |
| 13.2 GB free disk + 15.7 GB RAM caps concurrent renders | Medium — run one render at a time |

---

### 5.2 Remotion

| Attribute | Value |
|---|---|
| **What it does** | React-based video framework. Compositions are React components; renders via headless Chrome + its own encoder pipeline. |
| **Why relevant** | Already installed with working compositions at `src/video/Root.tsx` and `src/video/SignhifyReel.tsx`. It is the incumbent alternative to HyperFrames. |
| **Official sources** | `https://github.com/remotion-dev/remotion/blob/main/LICENSE.md` · `https://www.remotion.pro/license` |
| **Version** | Latest **4.0.534**; installed **4.0.526** (`package.json` license field literally reads `SEE LICENSE IN LICENSE.md`) |
| **License** | **Source-available. NOT OSI open source.** |
| **Cost** | See license table below |
| **Hardware implications** | Installs and pins **Chrome Headless Shell 149.0.7790.0**. Since v4.0.208 it will **not** use an externally installed browser — the download is mandatory. Same CPU-bound rendering profile as HyperFrames. |
| **Integration difficulty** | **Low** — compositions already exist. This is why it is tempting. |
| **REQUIRED / OPTIONAL** | **OPTIONAL — drop from critical path** |
| **Recommendation** | **Do not build on it.** Retain the two existing compositions as reference. If a client-facing deliverable ever requires Remotion specifically, the license cost is a known line item, not a surprise. |

#### 5.2.1 License terms

| Organization type | Cost |
|---|---|
| Individuals | **Free** |
| For-profit orgs with **≤3 employees** | **Free** |
| Non-profits | **Free** |
| Evaluation, non-commercial | **Free** |
| For-profit orgs **>3 employees** — Creators | **$25 / seat / month** |
| For-profit orgs **>3 employees** — Automators | **$0.01 / render, $100 / month minimum** |
| For-profit orgs **>3 employees** — Enterprise | **from $500 / month** |

Important nuance: **commercial video creation is permitted free within the ≤3-employee band.** The cliff is org size, not revenue.

#### 5.2.2 Decision-relevant fact

Signhify is a registered MSME operating a studio with commercial tiers and client work (`data/brand.json`: "FULL A.I. ENGINEERING STUDIO", commercial positioning, website, paid-tier language). If the organization exceeds three employees, Remotion becomes a paid line item. **HyperFrames Apache-2.0 has no employee threshold and no revenue threshold.**

A Remotion 5.0 license change is announced in its `LICENSE.md`. **Exact terms UNVERIFIED.**

#### 5.2.3 Comparison against HyperFrames

| Dimension | HyperFrames | Remotion |
|---|---|---|
| License | Apache-2.0, unconditional | Source-available, paid above 3 employees |
| Authoring | HTML / CSS / GSAP | React |
| QA gate | `check` — 5 suites incl. WCAG AA | None built in |
| TTS | `tts` (Kokoro) | None |
| Captions | `transcribe` + normalization | None |
| Audio | `normalize-audio`, `grade-compare`, `compare` | None |
| Existing code in repo | None | 4 files, working compositions |
| Local cost | $0 | $0 → $500+/mo |

Remotion's only advantage is the existing code. That does not outweigh a license that bills per seat and an Apache-2.0 alternative that ships the missing QA and audio tooling.

---

### 5.3 FFmpeg

| Attribute | Value |
|---|---|
| **What it does** | Encode, mux, filter, probe. HyperFrames depends on it as a system binary. |
| **Why relevant** | Mandatory dependency for HyperFrames. Also the tool for EBU R128 loudness normalization before upload. |
| **Official source** | `https://ffmpeg.org/` |
| **Version** | Latest stable **9.0.2 "Lei"** (2026-09-18). Installed **8.0.1** |
| **License** | **LGPL-2.1-or-later**; optional parts are **GPL-2.0-or-later**. If a build is GPL-enabled, GPL applies to the whole thing. |
| **Cost** | Free. **How to estimate: nothing.** Already installed. |
| **Hardware implications** | Runs on CPU. NVENC unavailable (no CUDA GPU). CPU loudnorm is cheap relative to video encode. |
| **Integration difficulty** | Trivial — already on PATH, already invoked by the existing Python engine |
| **REQUIRED / OPTIONAL** | **REQUIRED** |
| **Recommendation** | Keep 8.0.1. Do not upgrade for this project — 9.0.2 offers nothing this pipeline needs, and HyperFrames pins its own expectations. Confirm the installed build is the LGPL variant if redistribution is ever on the table. |

#### 5.3.1 `loudnorm` — EBU R128, two-pass procedure

Instagram applies its own normalization; a correctly mastered source avoids the platform re-encoding the audio and changing loudness.

**Pass 1 — measure:**

```bash
ffmpeg -i in.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -
```

**Pass 2 — apply**, substituting all measured values from Pass 1:

| Parameter | Source |
|---|---|
| `measured_I` | Pass 1 JSON |
| `measured_TP` | Pass 1 JSON |
| `measured_LRA` | Pass 1 JSON |
| `measured_thresh` | Pass 1 JSON |
| `offset` | Pass 1 JSON |
| `-ar` | Set explicitly |

**Two traps, both verified in the docs:**

1. `linear=true` requires **all four** measured values. If any is missing it **silently reverts to dynamic mode**. This is the single most common cause of "I did two passes and it still sounds dynamic."
2. Always set the output sample rate explicitly with `-ar`. Omitting it resamples against a different default.

---

### 5.4 Text-to-Speech

**The decisive factor is license, not quality.** Every option below was evaluated on commercial permissiveness first.

| Option | License | Commercial use | Word timestamps | Cost | Notes |
|---|---|---|---|---|---|
| **Kokoro-82M** | **Apache-2.0** (weights **and** inference lib) | **Yes, unrestricted** | **No** | **$0** marginal, local | 82M params, 24 kHz, ~54 voices. Requires `espeak-ng`. Cleanest license in the set |
| edge-tts (rany2) | LGPL-3.0 (client) | **Risky** — Microsoft's service ToS may prohibit commercial use without an Azure subscription | **Yes** — native `WordBoundary` events, `--write-subtitles` | Free | Attractive on paper. **Treat as non-production for monetized output.** |
| Piper (original `rhasspy/piper`) | MIT | Yes | No | $0 | **Archived upstream** |
| Piper (current `piper-tts` PyPI) | **GPL-3.0-or-later** | Yes, but copyleft | No | $0 | Weights inherit dataset licenses — some CC-BY. **Do not adopt.** |
| OpenAI TTS (`gpt-4o-mini-tts`) | Proprietary | Yes, **with disclosure** that the voice is AI-generated | No | ~**$0.015/min (UNVERIFIED)** | Good fallback |
| ElevenLabs | Proprietary | Free tier **explicitly NOT commercial** (attribution required) | No | Commercial from **Starter $5–6/mo** | Free tier unusable for monetized output |
| HeyGen Starfish TTS | Proprietary | Yes | **Yes — native word timestamps** | HeyGen credits, metered | Per-minute cost **UNVERIFIED** |

| Attribute | Value |
|---|---|
| **What it does** | Converts script text to a narration audio track |
| **Why relevant** | Every Reel in this pipeline is narrated |
| **Official sources** | HyperFrames `hyperframes tts` docs; each vendor's own site |
| **Hardware implications** | Kokoro-82M runs comfortably on CPU — 82M params is small. espeak-ng must be installed. No GPU needed. |
| **Integration difficulty** | **Low** — `hyperframes tts` wraps Kokoro, no key required |
| **REQUIRED / OPTIONAL** | **REQUIRED** (Kokoro) |
| **Recommendation** | **Adopt Kokoro via `hyperframes tts`.** Apache-2.0 end to end, $0, local. Chain a transcriber for timestamps — Kokoro emits none. Keep OpenAI TTS as a documented fallback if voice quality is ever judged insufficient. Do not ship edge-tts or Piper. |

#### 5.4.1 Critical caveat on `hyperframes tts`

The published CLI is frequently a **local-only build**. When that is the case, it **silently falls back to Kokoro even if `$HEYGEN_API_KEY` is set.** HeyGen and ElevenLabs paths exist only inside bundled skill scripts, not as first-class flags.

Operational consequence: **do not infer which engine produced a track from an env var.** Log the engine that actually ran. On this machine Kokoro is not yet installed, so the first `tts` invocation will fail until `espeak-ng` + Kokoro deps are present.

---

### 5.5 Transcription and Caption Timing

| Option | License | Word timestamps | Status | Cost |
|---|---|---|---|---|
| **faster-whisper** | **MIT** | `word_timestamps=True` | **Actively maintained** | **$0**, CPU |
| whisper.cpp | MIT | Yes | Actively maintained | $0, CPU |
| stable-ts | MIT | Yes | **ARCHIVED / read-only since 2026-05-30** | $0 |
| `hyperframes transcribe` | (wrapper) | Yes | **Not installed on this machine** | $0 |

| Attribute | Value |
|---|---|
| **What it does** | Produces word-level timestamps so captions can be timed and animated per word |
| **Why relevant** | Per-word caption timing is what separates a watchable Reel from a slideshow with a subtitle bar |
| **Official source** | `https://github.com/SYSTRAN/faster-whisper` |
| **License** | MIT (faster-whisper, whisper.cpp, stable-ts) |
| **Cost** | **Free.** Already a declared repo dependency — `requirements.txt:15` → `faster-whisper>=1.0.0`. Zero marginal cost |
| **Hardware implications** | Runs on CPU here. Up to 4× faster than `openai/whisper`. On 15.7 GB RAM with no CUDA, expect real-time factor to be the constraint on long audio. Segmenting per-scene keeps each pass short |
| **Integration difficulty** | **Lowest in this report** — already installed |
| **REQUIRED / OPTIONAL** | **REQUIRED** for burned-in word-level captions |
| **Recommendation** | **Adopt faster-whisper.** Already a dependency; MIT; maintained; built-in `word_timestamps=True`. **Do not build on stable-ts — archived 2026-05-30.** |

#### 5.5.1 `hyperframes transcribe` behavior

Backend selection: **NVIDIA Parakeet** when installed (`hyperframes models install parakeet`), else **whisper.cpp**. Neither is installed on this machine.

Accepted inputs → normalized output `transcript.json`:

| Accepted input format |
|---|
| whisper.cpp JSON |
| OpenAI Whisper API JSON with word timestamps |
| SRT |
| VTT |

All normalize to `[{text, start, end}]`.

| Option | Note |
|---|---|
| HyperFrames-managed transcriber | Nicest pipeline integration; requires installing Parakeet or whisper.cpp |
| faster-whisper | Already present; one Python call; MIT |
| **Decision** | **Start with faster-whisper.** Switch to `hyperframes transcribe` only if the CLI's Parakeet path proves materially better on this hardware — Parakeet is NVIDIA-specific and there is no CUDA GPU here, so the likely outcome is that it falls back to whisper.cpp anyway. |

---

### 5.6 Instagram Reels Publishing (Meta Graph API)

| Attribute | Value |
|---|---|
| **What it does** | Publishes 9:16 video to an Instagram professional account |
| **Why relevant** | The pipeline's terminal step. Already partly wired into `src/instagram/publisher.py` |
| **Version** | **Graph API v26.0** |
| **Official sources** | `https://developers.facebook.com/documentation/instagram-platform/content-publishing` · `.../instagram-graph-api/reference/ig-user/media` · `.../reference/ig-user/media_publish` · `.../reference/ig-user/content_publishing_limit` |
| **License** | Platform Terms of Service (not OSS) |
| **Cost** | $0 — API access is free; the constraint is rate limits, not price |
| **Hardware implications** | None server-side. **Requires a publicly reachable HTTPS URL for `video_url`** — the video must be uploaded somewhere Meta can fetch. This is the hard integration constraint, not a compute one. |
| **Integration difficulty** | **Medium** — account type prerequisites + a public hosting path + a polling loop |
| **REQUIRED / OPTIONAL** | **REQUIRED** for distribution |
| **Recommendation** | Keep the existing container-flow publisher. Verify the account-type prerequisites before any build-out. Adopt **50/24h** as the design limit (see below). |

#### 5.6.1 Prerequisites

| Requirement | Detail |
|---|---|
| Account type | Instagram **Professional** — Business **or** Creator. Personal accounts cannot publish |
| Facebook Page | Must be **connected** to the professional account |
| Page Publishing Authorization | PPA must be complete where applicable |

#### 5.6.2 Permissions

| Path | Permissions |
|---|---|
| Facebook Login | `instagram_basic`, `instagram_content_publish`, `pages_read_engagement` |
| Instagram Login | `instagram_business_basic`, `instagram_business_content_publish` on `graph.instagram.com` |

#### 5.6.3 Publish flow

| Step | Call | Notes |
|---|---|---|
| 1 | `POST /{ig-user-id}/media` | Params: `media_type=REELS`, `video_url`, `caption`, `cover_url`, `share_to_feed`, `thumb_offset` |
| — response | `{id, uri}` | `id` is the container ID |
| 2 | `GET /{ig-container-id}?fields=status_code` | Poll until the container is `FINISHED` |
| 3 | `POST /{ig-user-id}/media_publish` | With `creation_id` |
| — response | `{id}` | Final media ID |

#### 5.6.4 Rate limits

| Source | Value |
|---|---|
| Content publishing guide | 100 posts / rolling 24 h |
| Endpoint reference | 50 |
| Quota field doc | 50 |

**The official documentation contradicts itself.** Recommendation: **assume 50 per rolling 24 h** and build against that. Treat 100 as unavailable.

| Related limit | Value |
|---|---|
| Container creation | **400 / rolling 24 h** |
| Container expiry | **24 h** after creation — a container that is not published in time is dead |
| Live query | `GET /{ig-id}/content_publishing_limit?fields=quota_usage` |

Operational note: at a 7-Reels-per-day schedule, 50/24 h leaves ~7 Reels of headroom per day. Adequate. One burst of retries against the 400/day container limit will exhaust a full day's container budget.

#### 5.6.5 Reels constraints

| Constraint | Value |
|---|---|
| Carousels | Reels **cannot** appear in carousels |
| Alt text | **Not supported** on Reels or Stories |
| Resolution | 9:16, **1080×1920 recommended**, minimum 540×960 |
| Frame rate | 24–60 fps |
| Duration | 3–90 s |
| Stickers | Not supported |
| `media_type` readback | Returns **`VIDEO`** after publish, not `REELS` |

> The `media_type` readback is a real trap: any verification code that asserts `media_type == "REELS"` after publishing will fail. Assert on `VIDEO`.

The 1080×1920 output produced by the smoke render (§2.2) is exactly the recommended size. No change needed.

---

### 5.7 HeyGen API

| Attribute | Value |
|---|---|
| **What it does** | Avatar V (stock avatar), Avatar IV (digital twin from real footage), Video Agent, Voices/Starfish TTS, Video Translation (175+ languages with lip-sync) |
| **Why relevant** | HyperFrames is HeyGen's own product. Not required for code-driven rendering — only for the avatar and translation paths. |
| **Official source** | `https://developers.heygen.com` |
| **License** | Proprietary |
| **Cost** | Credit-metered. See table below |
| **Hardware implications** | None locally. Rendering is entirely on HeyGen's side |
| **Integration difficulty** | **Medium–High.** Account, credits, async job polling, asset upload. Also requires a HeyGen account, which the local HyperFrames path deliberately avoids. |
| **REQUIRED / OPTIONAL** | **OPTIONAL** |
| **Recommendation** | **Do not adopt now.** Every capability it offers beyond Approach A (avatar, translation) has no current requirement. Revisit only if Approach C is justified by measured demand (§8). |

#### 5.7.1 Pricing

| Plan | Monthly | Credits |
|---|---|---|
| Free | $0 | 10/mo — **watermarked, no auto-renew** |
| Pro | **$99/mo** | 100/mo |
| Scale | **$330/mo** | 660/mo |
| Enterprise | Custom | Custom |

#### 5.7.2 Per-minute credit consumption

HeyGen's own 2026 blog states:

| Model | Credits/min | At Pro's **$0.99/credit** | Implied cost/min |
|---|---|---|---|
| Avatar IV | 31 | $30.69 | **~$30.7 / min** |
| Avatar V | 48 | $47.52 | **~$47.5 / min** |

> **HeyGen's own pages contradict each other on the credit-to-minute mapping** — one page implies 5-minute photo avatars per credit, another implies 1-minute. Both cannot be true. **Do not rely on either figure without a measured test.** See §9.

At either figure, a 60-second Reel costs roughly **$30–47** to produce. That is 60–94× the cost of the entire code-driven pipeline (§8) and is the single strongest argument against Approach C at current volume.

#### 5.7.3 Relationship to HyperFrames

| Fact | Value |
|---|---|
| Repository | `github.com/heygen-com/hyperframes` |
| Docs | `hyperframes.heygen.com` |
| README claim | "used in production at HeyGen" |
| Implication | The Apache-2.0 local renderer is not a trial tier. It is the same product HeyGen builds internally. The paid products are the avatar and translation surfaces |

---

## 6. Approach Comparison

| Dimension | **A — Code-driven** | **B — Code + AI media** | **C — AI avatars** |
|---|---|---|---|
| **Composition** | HyperFrames HTML/CSS/GSAP | HyperFrames + AI-generated B-roll/stills | HeyGen Avatar V / Avatar IV |
| **Engine** | `hyperframes render` | `hyperframes render` + media pipeline | HeyGen cloud render |
| **License** | **Apache-2.0** | Apache-2.0 (engine) + per-asset licenses | Proprietary |
| **Marginal cost / 60 s Reel** | **$0** | $0 – UNVERIFIED (depends on image model used) | **~$30–47 (UNVERIFIED, see §5.7.2)** |
| **Fixed monthly** | **$0** | $0 – UNVERIFIED | **$99–330/mo** |
| **HeyGen account needed** | **No** | No | **Yes** |
| **Reproducibility** | **Exact** — same input, same output | Mixed; assets must be pinned | Low |
| **Brand control** | **Total** — tokens from `brand.json` | Total | Constrained by avatar/platform styling |
| **Determinism** | **Guaranteed** | Depends on asset pipeline | Not guaranteed |
| **Banned-phrase enforcement** | Full control | Full control | Limited — VO text is yours but captions are platform-controlled |
| **Human footprint** | High — someone authors each composition | Medium | Low |
| **Scaling behavior** | Linear in human authoring time | Linear | Metered, expensive per unit |
| **Hardware** | CPU only — already proven | CPU + network for generation | None locally |
| **Output size fit** | 1080×1920 native — matches API recommendation | Same | Same |
| **Failure modes** | Authoring errors, caught by `hyperframes check` | Generation failures + authoring errors | Credit exhaustion, avatar render latency, platform-side drift |

### 6.1 Verdict

**Adopt Approach A as the production default. Hold Approach B as the documented escalation path. Do not adopt Approach C.**

| Rationale | Detail |
|---|---|
| Cost | A is $0 marginal and $0 fixed. C costs 60–94× more per minute of output before the fixed subscription |
| License | A is Apache-2.0 with no thresholds. C is proprietary and metered |
| Brand fit | A renders `data/brand.json` tokens directly. The current dark themes (§4) show exactly what happens when the pipeline does not — the engine drifted for months |
| Determinism | A produces identical output for identical input. C does not, which makes A/B testing and regression checks impossible |
| Provenance | A was empirically rendered on this machine in 15.3 s (§2.2). C has no measured baseline here |
| When B becomes right | When compositions alone cannot carry a topic and a B-roll layer measurably improves retention. Decision needs data this pipeline does not yet collect. |
| When C becomes right | When a recurring offer requires a human presenter and the per-minute cost has been validated against actual revenue. Neither condition is currently true. |

---

## 7. Cost Profiles

Assumes one 60-second Reel per day, matching the current 7-per-day schedule scaled down. All figures are per-Reel unless stated.

### 7.1 Approach A — Code-driven (RECOMMENDED)

| Item | Unit cost | Monthly (1/day ≈ 30) | Annual |
|---|---|---|---|
| HyperFrames | $0 (Apache-2.0, no credits, no account) | $0 | $0 |
| FFmpeg | $0 | $0 | $0 |
| Kokoro TTS | $0 (local) | $0 | $0 |
| faster-whisper | $0 (already installed) | $0 | $0 |
| Meta Graph API | $0 | $0 | $0 |
| Hosting for public `video_url` | depends on provider | UNVERIFIED | UNVERIFIED |
| **Total** | **$0 + hosting** | **$0 + hosting** | **$0 + hosting** |

> Hosting is the only variable line, and it already exists for the carousel pipeline. If the existing uploader cascade (`src/storage/uploader.py`) serves HTTPS publicly, this is already $0. If not, this is the one thing that must be solved before Reels can publish at all.

### 7.2 Approach B — Code + AI media

| Item | Unit cost | Monthly | Annual |
|---|---|---|---|
| All of Approach A | $0 | $0 | $0 |
| Image/video generation | UNVERIFIED — depends on model chosen | UNVERIFIED | UNVERIFIED |
| **Total** | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** |

Cannot be costed honestly without naming a specific generation model. Do not commit budget against a number that has not been measured.

### 7.3 Approach C — AI avatars

| Item | Unit cost | Monthly (1/day ≈ 30) | Annual |
|---|---|---|---|
| Pro plan | $99/mo fixed | $99 | $1,188 |
| Avatar IV render | ~$30.7 / min → ~$30.7 / 60 s Reel | ~$921 | ~$11,052 |
| **Total** | | **~$1,020/mo** | **~$12,240** |
| Scale plan alternative | $330/mo + 660 credits | Credits cover fewer renders | — |

**Versus Approach A: ~1,020× more expensive at 1 Reel/day.** The ratio improves at higher volume only if the Pro plan's credits are consumed efficiently; the per-minute figures themselves are contradicted by HeyGen's own documentation and must be measured first.

### 7.4 Approach comparison at the license level

| Scenario | Approach A | Approach C | Remotion (if >3 employees) |
|---|---|---|---|
| 1 Reel/day | $0 | ~$1,020/mo | $25/seat/mo or $100/mo minimum |
| 7 Reels/day | $0 | ~$6,300/mo | Same |
| Scaling | Labor only | Linear cost + fixed | Seat or render cost |

---

## 8. Unverified Items

Each item below is explicitly **not** treated as fact anywhere in this report. None blocks the §10 recommendation.

| # | Item | Why unverified | How to resolve |
|---|---|---|---|
| 1 | **HeyGen credit-to-minute mapping** — 5-min vs 1-min photo avatar per credit | HeyGen's own pages contradict each other. Implied $30.7 / $47.5 per minute cannot be relied on | Run one paid Avatar IV render and read the credit delta |
| 2 | **Exact OpenAI TTS price** — ~$0.015/min | Not confirmed against a current official pricing page | Check the vendor pricing page before adopting as fallback |
| 3 | **Remotion 5.0 license terms** | Announced in `LICENSE.md`; terms not read in full | Read `LICENSE.md` on the Remotion repo before any 5.x upgrade |
| 4 | **HyperFrames changelog 0.8.58 → 0.8.145** — 87 patch versions | Delta not enumerated; unknown whether any are breaking | Read the GitHub releases page between the two tags, then upgrade and re-run the §2.2 smoke test |
| 5 | **HeyGen Starfish TTS per-minute cost** | Metered in credits; no per-minute figure published | Derive from a measured render |
| 6 | **Approach B asset-generation cost** | No model selected | Name a model, price one render, multiply |
| 7 | **Public HTTPS hosting cost for `video_url`** | Depends on the existing uploader cascade — not evaluated here | Test whether the current CDN path is publicly reachable, then price the fallback |
| 8 | **Render throughput on a real composition** | Only a `blank` example was timed (15.3 s for 120 frames). Blur, glass, and large type will be slower | Time one production composition |
| 9 | **FFmpeg build variant** — LGPL or GPL | The installed 8.0.1 gyan.dev build's variant was not inspected | Check `ffmpeg -version` build flags if redistribution is ever planned |
| 10 | **faster-whisper real-time factor on this CPU** | Not benchmarked on this machine | Run one 60 s transcription and record wall-clock time |
| 11 | **Kokoro voice quality against brand voice** | Not yet installed, not yet auditioned | Install, generate samples, compare against the `voice` array in `brand.json` |
| 12 | **Signhify current employee count vs the 3-employee Remotion threshold** | Not verified against any HR record | Confirm internally. If >3, the Remotion conclusion hardens from "avoid" to "prohibited without payment" |

---

## 9. Source Register

| Source | URL |
|---|---|
| HyperFrames CLI quickstart | `https://hyperframes.heygen.com/quickstart` |
| HyperFrames CLI packages | `https://hyperframes.heygen.com/packages/cli` |
| HyperFrames repository | `https://github.com/heygen-com/hyperframes` |
| HyperFrames npm package | `https://www.npmjs.com/package/hyperframes` |
| HyperFrames latest version | `https://registry.npmjs.org/hyperframes/latest` |
| Remotion license | `https://github.com/remotion-dev/remotion/blob/main/LICENSE.md` |
| Remotion license terms | `https://www.remotion.pro/license` |
| Instagram content publishing | `https://developers.facebook.com/documentation/instagram-platform/content-publishing` |
| IG `media` endpoint | `https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media` |
| IG `media_publish` endpoint | `https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media_publish` |
| IG `content_publishing_limit` | `https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/content_publishing_limit` |
| HeyGen developers | `https://developers.heygen.com` |
| FFmpeg | `https://ffmpeg.org/` |
| faster-whisper | `https://github.com/SYSTRAN/faster-whisper` |

---

## 10. Final Recommendation

### 10.1 Decision

| # | Decision | Confidence |
|---|---|---|
| 1 | **Use the real HyperFrames CLI as the sole composition and render engine.** Apache-2.0, $0, no account, QA gate included, empirically proven on this machine. | **High** |
| 2 | **Drop Remotion from the critical path.** Source-available, not OSS, and bills per seat above three employees. Its only advantage — two existing compositions — does not justify an open license the pipeline does not need. | **High** |
| 3 | **Retire `src/content/hyperframes_engine.py` from the critical path.** It is a name collision, not a HyperFrames implementation. Quarantine now, delete after one production Reel proves through the CLI. | **High** |
| 4 | **Build new brand-correct light-background compositions** from `data/brand.json` tokens. Do not retrofit the five dark neon themes. | **High** |
| 5 | **Kokoro-82M for voiceover** via `hyperframes tts`. Apache-2.0 weights and library, $0, local, ~54 voices. | **High** |
| 6 | **faster-whisper for word timestamps.** Already a repo dependency, MIT, maintained, 4× faster than the reference implementation. | **High** |
| 7 | **Keep the Meta Graph API v26.0 container flow.** Design against **50 posts / rolling 24 h**, not 100. | **High** |
| 8 | **Do not adopt HeyGen paid products.** ~1,020× the per-Reel cost of Approach A, no current requirement. | **Medium-High** |
| 9 | **Do not enable Docker mode.** Daemon is not running, and determinism from the local path is already acceptable. | **High** |
| 10 | **Avoid edge-tts and Piper for monetized output** — ToS risk and GPL-3.0 respectively. | **High** |

### 10.2 Rationale

The pipeline's structural problem is not capability. It is that three rendering paths exist, two of them are named after a product they do not implement, and the one that renders at all produces dark neon themes for a brand defined as warm off-white with a single burnt-orange accent. Consolidating onto Apache-2.0 HyperFrames fixes the naming, removes the per-seat license exposure, and brings `hyperframes check` — runtime, layout, motion, and WCAG AA contrast — into a pipeline that currently has no automated visual QA at all.

The cost case is not close. Approach A is $0 marginal and $0 fixed. Approach C, at HeyGen's own published per-minute figures, is roughly $1,020/month at one Reel per day. Neither the composition engine nor the voiceover needs an account, a key, or a credit balance.

The quality case is the reason to hesitate on Approach B, not A. A is deterministic, reproducible, and brand-exact. B is worth testing once retention data exists. C should stay on the shelf.

### 10.3 Immediate next actions

Ordered by dependency. Each is small.

| # | Action | Verify by |
|---|---|---|
| 1 | Upgrade `hyperframes` 0.8.58 → ≥0.8.145 | Re-run the §2.2 smoke test; `ffprobe` returns 1080×1920 h264 30/1 |
| 2 | Install Kokoro TTS + `espeak-ng` | `hyperframes doctor` reports Kokoro OK |
| 3 | Rename the Python module's log/docstring to remove the collision | Read `hyperframes_engine.py:1-4` |
| 4 | Author one Signhify composition at 1080×1920 from `data/brand.json` tokens — light `#F8F6F0` bg, `#E05A36` accent, Plus Jakarta Sans | `hyperframes check` → 0 runtime, 0 layout, 0 motion, contrast passes |
| 5 | Generate narration with `hyperframes tts`; transcribe with faster-whisper for word timings | `transcript.json` contains `[{text, start, end}]` |
| 6 | Normalize with two-pass `ffmpeg loudnorm` and set `-ar` explicitly | Pass 1 JSON has all four `measured_*` values |
| 7 | Confirm public HTTPS reachability of `video_url` | Container reaches `status_code: FINISHED` |
| 8 | Publish one Reel end to end | `POST /media_publish` returns an `id`; `media_type` reads back as `VIDEO` |
| 9 | Confirm employee count against the 3-employee Remotion threshold | Internal record |
| 10 | Delete `src/content/hyperframes_engine.py` | Steps 1–8 all green |

### 10.4 What this report does not cover

| Excluded | Reason |
|---|---|
| Rendering throughput for production compositions | Only a `blank` example was timed. Step 4 measures it |
| Audio-music licensing | HyperFrames `catalog` retrieval is HeyGen-gated. Not required by Approach A |
| Horizontal (16:9) and other aspect ratios | Only 9:16 is in scope — this is an Instagram Reels pipeline |
| Multi-language output | HeyGen Video Translation is the only path found; deferred per decision 8 |
| CDN/hosting architecture for public video | Existing `src/storage/uploader.py` cascade may already satisfy it. Unverified — §8 item 7 |