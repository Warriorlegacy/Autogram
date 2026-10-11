# Video Studio — Production Runbook

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/06_PRODUCTION_RUNBOOK.md` |
| **Date** | 2026-10-11 |
| **Scope** | Day-to-day operation: write a brief → build → render → inspect → package → iterate |
| **Companions** | `03_SYSTEM_ARCHITECTURE.md` (contracts), `07_VIDEO_QUALITY_CHECKLIST.md` (human gate), `09_TROUBLESHOOTING.md` (failures) |

**State labels:** **[I]** implemented and verified · **[P]** partial · **[N]** not built.

---

## 1. The Four Commands

Run from `D:\Autogram`. All use the venv interpreter.

```powershell
# 1. BUILD — validate the brief, compile the storyboard, write the HyperFrames project
.venv\Scripts\python.exe -m video_studio.cli build --brief video_studio/briefs/<slug>.json

# 2. RENDER — gate + render + package + QA, all five steps
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/<slug>.json --quality draft

# 3. QA — inspect an existing MP4 on its own
.venv\Scripts\python.exe -m video_studio.cli qa --video video_studio/output/<slug>/reel.mp4 --frames video_studio/output/<slug>/qa_frames --no-audio

# 4. PACKAGE — regenerate captions/caption/manifest only, no render
.venv\Scripts\python.exe -m video_studio.cli package --brief video_studio/briefs/<slug>.json
```

> **`-m video_studio.cli` is the documented form.** `video_studio/__main__.py` now exists, so the bare `-m video_studio` works as well; the note that it did not was true when written and is no longer.

### 1.1 Flags

| Subcommand | Flag | Values | Default | Effect |
|---|---|---|---|---|
| `build` / `render` / `package` | `--brief` | path | **required** | brief JSON; relative paths resolve from repo root |
| | `--slug` | string | `""` | overrides `brief.slug`, so one brief can produce many variants |
| `render` | `--quality` | `draft` · `standard` · `high` | `draft` | HyperFrames encode tier |
| `render` | `--audio` | flag | off | synthesize narration + mux — **SHIPPED**, §7 |
| `render` | `--skip-gate` | flag | off | continue when `hyperframes check` fails. **Diagnostic only** |
| `render` | `--publish` | flag | off | `[8/8]` publish to Instagram. Only ever reached after QA returns PASS, §7.4 |
| | `--publish-dry-run` | flag | off | resolve every Meta call but publish nothing |
| | `--video-url` | url | `$PUBLIC_CDN_BASE/<slug>/reel.mp4` | publicly reachable MP4. Meta's crawler must fetch it or `media` fails |
| | `--cover-url` | url | none | cover image for the container |
| `qa` | `--video` | path | **required** | the MP4 to inspect |
| | `--frames` | dir | `scratch/qa` | where extracted JPEGs go |
| | `--no-audio` | flag | off | expect **no** audio track. Use it for the shipped pipeline |

### 1.2 Exit codes

| Code | Meaning |
|---|---|
| **0** | Success. QA verdict PASS, no defects |
| **1** | Render error, or an uncaught exception (including malformed brief JSON) |
| **2** | QA fail — at least one defect recorded in `qa.py` |
| **3** | Brief validation fail — banned brand phrase, or `scenes` is empty |
| **4** | Narration overrun — a scene is too short to speak *and* read its own narration (§7.1) |
| **5** | Publish credentials missing, or the token/account is not authorized (`CredentialsError`) |
| **6** | Publish refused or failed — quota exhausted, container `FAILED`, or the API returned an error (`PublishError`) |

Codes 5 and 6 are only reachable via `--publish`, which runs after QA. A QA failure returns 2 and never reaches the publish step.

`--skip-gate` does **not** change any exit code. It only suppresses the gate's exception.

---

## 2. Writing a Brief

Drop a JSON file at `video_studio/briefs/<slug>.json`. Nothing else. `slug` must match the filename by convention and must be `[A-Za-z0-9-_]+`.

### 2.1 Top-level shape

```json
{
  "slug": "short-kebab-case",
  "title": "End-card headline",
  "pillar": "product",
  "hook": "One verifiable claim. Also the end-card subtext.",
  "cta": "Follow @signhify.studio for more",
  "accent": "#E05A36",
  "target_duration": 38,
  "sources": ["https://signhify.dpdns.org/", "data/brand.json"],
  "notes": "Authoring note. Never rendered.",
  "scenes": [ ... ]
}
```

| Field | Required | Notes |
|---|---|---|
| `slug` | **yes** | `[A-Za-z0-9-_]` only. Becomes the folder name and `#root` composition id |
| `title` | **yes** | End-card `h2` |
| `hook` | **yes** | End-card `p`, caption line 1, `build` output line 2 |
| `pillar` | no | Metadata only. Never rendered |
| `cta` | no | End-card button. Default `"Follow @signhify.studio for more."` |
| `accent` | no | `#RRGGBB` or empty. Empty → `brand.json` `#E05A36` |
| `target_duration` | no | **Advisory only. Not enforced anywhere.** Set it to your intent, not your expectation of validation |
| `sources` | no | Copied into `brief.json`. Not validated against claims |
| `notes` | no | Never rendered |
| `width` / `height` | no | 1080 / 1920. Leave at defaults |
| `fps` | no | 30. Constrained 24–60 |
| `narration_enabled` | no | **Never read by any module.** `--audio` is the only switch |

### 2.2 Scene shape

```json
{
  "id": "hook",
  "visual": "hook",
  "duration": 4.0,
  "eyebrow": "prompt to site",
  "headline": "I typed one sentence.",
  "subtext": "A website built itself.",
  "narration": "I typed one sentence. A website built itself.",
  "bullets": [],
  "metrics": [],
  "source_url": ""
}
```

| Field | Required | Used by |
|---|---|---|
| `id` | **yes** | Element id, counter id, caption cue prefix. **Must be unique and CSS-safe** — no spaces, no dots |
| `visual` | **yes** | Selects the template branch — see §2.3 |
| `duration` | **yes** | Seconds, `> 0`. Sum of all scenes = `endcard_at` |
| `eyebrow` | no | Orange mono label above the headline. Uppercase is applied by CSS |
| `headline` | no | 104 px (`hook`/`statement`) or 84 px (everything else) |
| `subtext` | no | 42 px muted |
| `narration` | no | Caption source, TTS source, `captions.srt`. Split on `.` and `?` — see §5.3 |
| `bullets` | no | `feature_card` cards · `terminal` lines. **3 max per card; keep ≤ 3 total for one beat** |
| `metrics` | no | `metrics[]` — `{"v": "400+", "k": "frames per site"}` |
| `source_url` | no | `browser` URL pill. Falls back to `signhify.dpdns.org` |

### 2.3 Scene `visual` types

All six are implemented. Pick by what the beat has to show.

| `visual` | Renders | `head_class` | Use for | Source brief |
|---|---|---|---|---|
| **`hook`** | eyebrow + 104 px headline + subtext | `""` | The opening claim. **First scene only** | `hook` |
| **`statement`** | eyebrow + 104 px headline + subtext | `""` | A single declarative beat — a claim, a limit, a price | `problem`, `no-webgl`, `price` |
| **`feature_card`** | headline + a vertical stack of white cards, one per `bullets[]`, alternating orange/green dot | `"sm"` | Numbered steps, a checklist, a mechanism broken into moves | `mechanism` |
| **`metrics`** | a row of white tiles — `metrics[].v` in 88 px accent, `metrics[].k` in mono | `"sm"` | Verified numbers. **2–3 tiles only** — 4+ overflows at 1080 wide | `proof` |
| **`terminal`** | a dark `#0B0B0C` panel, `bullets[]` joined by `<br>`, mono 32 px | `"sm"` | Commands, file trees, config, shell output | *(none yet — see §9)* |
| **`browser`** | a white browser chrome with 3 dots, a URL pill (`source_url`), and 3 placeholder bars | `"sm"` | "Here is the artefact / here is the page" | `export` |

`end_card` is **not a scene type.** It is emitted automatically after the last scene, always 3.0–4.5 s. Do not put it in `scenes`.

Layout note: `feature_card`, `metrics`, `terminal`, `browser` get the `.inner` class, which tightens bottom padding from 320 px to 260 px. Dense components need that room. `hook` and `statement` use the default 200/80/320 padding.

### 2.4 Copy rules, enforced

`cli.py` runs `Brief.banned_hits()` before anything else and returns **exit 3** on a hit. The scan covers `title`, `hook`, `cta`, and per scene `narration`, `headline`, `subtext`, `eyebrow`, `bullets` — lowercased.

The 16 banned phrases from `data/brand.json → avoid`:

```
generic hype            fake urgency             unsupported statistics
overused motivational   keyword stuffing         game-changer
unlock the power of     in today's fast-paced world
dive into               at its core              seamless
robust                  revolutionary tool       next-gen AI
ultimate secret         must-have app
```

**`robust` is the trap.** It is ordinary engineering vocabulary and survives a casual read.

Not covered by the scanner — check these by eye:

| Field | Scanned? |
|---|---|
| `sources[]` | No |
| `notes` | No |
| `pillar` | No |
| `metrics[].v` / `metrics[].k` | **No** |

### 2.5 Claim rules

Every number and capability claim must trace to `signhify.dpdns.org`, to `data/brand.json`, or to something you observed. The full fabrication ban — 12 items, including any follower or engagement figure, any revenue or customer count, any speedup multiple, and any competitor capability claim — is in `02_BRAND_AND_CONTENT_STRATEGY.md` §9.2.

`instagram.com/signhify.studio` was auth-walled at research time. **No post-level data exists. Never invent one.**

---

## 3. Worked Example — `signhify-prompt-to-3d-site.json`

The real brief that produced the reference Reel. Full file at `video_studio/briefs/signhify-prompt-to-3d-site.json`.

### 3.1 The brief

```json
{
  "slug": "signhify-prompt-to-3d-site",
  "title": "One Prompt. A 3D Website.",
  "pillar": "product",
  "hook": "I typed one sentence. A website built itself.",
  "cta": "Follow @signhify.studio for more",
  "accent": "#E05A36",
  "target_duration": 38,
  "sources": [
    "https://signhify.dpdns.org/",
    "https://signhify.dpdns.org/pricing",
    "data/brand.json"
  ],
  "notes": "Every claim below is quoted from signhify.dpdns.org. No invented metrics, customers, or results.",
  "scenes": [
    {
      "id": "hook", "visual": "hook", "duration": 4.0,
      "eyebrow": "prompt to site",
      "headline": "I typed one sentence.",
      "subtext": "A website built itself.",
      "narration": "I typed one sentence. A website built itself."
    },
    {
      "id": "problem", "visual": "statement", "duration": 4.5,
      "eyebrow": "the gap",
      "headline": "Scroll sites are expensive to build.",
      "subtext": "WebGL, shaders, a whole team. Most of it is skipped.",
      "narration": "Scroll driven sites usually mean WebGL, shaders, and a whole team."
    },
    {
      "id": "mechanism", "visual": "feature_card", "duration": 7.0,
      "eyebrow": "the method",
      "headline": "Three moves.",
      "bullets": [
        "Generate an eight second cinematic video",
        "Extract the frames into a scroll sequence",
        "Native browser scroll replays it as parallax"
      ],
      "narration": "Signhify generates an eight second video, extracts the frames, and lets native browser scroll replay them as parallax."
    },
    {
      "id": "no-webgl", "visual": "statement", "duration": 5.0,
      "eyebrow": "the result",
      "headline": "No WebGL. No Three.js.",
      "subtext": "Just native scroll with frame interpolation.",
      "narration": "No WebGL. No Three.js. Just native scroll with frame interpolation."
    },
    {
      "id": "proof", "visual": "metrics", "duration": 6.0,
      "eyebrow": "published specs",
      "headline": "What you ship",
      "metrics": [
        { "v": "400+", "k": "frames per site" },
        { "v": "10-40", "k": "adjustable fps" },
        { "v": "8s", "k": "source video" }
      ],
      "narration": "Over four hundred frames per site, adjustable between ten and forty frames per second, from an eight second source video."
    },
    {
      "id": "export", "visual": "browser", "duration": 5.5,
      "eyebrow": "you own it",
      "headline": "You get the code.",
      "subtext": "A ZIP with the frontend, plus a backend starter.",
      "source_url": "signhify.dpdns.org",
      "narration": "You export a ZIP with the frontend and a backend starter, under an MIT license."
    },
    {
      "id": "price", "visual": "statement", "duration": 4.0,
      "eyebrow": "entry point",
      "headline": "Plans start at five dollars a month.",
      "subtext": "Five credits. Full source ownership.",
      "narration": "Plans start at five dollars a month, with full source code ownership."
    }
  ]
}
```

### 3.2 What each scene teaches

| # | Scene | `visual` | Duration | Beat |
|---|---|---|---|---|
| 1 | `hook` | hook | 4.0 s | The claim. One verifiable fact in the first 1.5 s |
| 2 | `problem` | statement | 4.5 s | Name the cost of the conventional path |
| 3 | `mechanism` | feature_card | 7.0 s | Three steps as three cards |
| 4 | `no-webgl` | statement | 5.0 s | The differentiator, stated plainly |
| 5 | `proof` | metrics | 6.0 s | Three published specs |
| 6 | `export` | browser | 5.5 s | The artefact — you get the code |
| 7 | `price` | statement | 4.0 s | Entry point. Exact verified inclusion: $5/mo, 5 credits, MIT ownership |

This is the mandatory structure from `02_BRAND_AND_CONTENT_STRATEGY.md` §6: hook → turn → mechanism → proof → limit → CTA. The **limit beat is mandatory**; a video that claims only strengths reads as marketing and is scrolled past by engineers. Scene 2 (`problem`) and scene 4 (`no-webgl`) carry the honest framing here.

### 3.3 Compile result

```powershell
.venv\Scripts\python.exe -m video_studio.cli build --brief video_studio/briefs/signhify-prompt-to-3d-site.json
```

```
[OK] project: D:\Autogram\video_studio\work\signhify-prompt-to-3d-site
[OK] scenes=7 captions=16 total=45.5s endcard@41.0s
```

Timing arithmetic:

| Quantity | Value | Derivation |
|---|---|---|
| `body` | 36.0 s | 4.0 + 4.5 + 7.0 + 5.0 + 6.0 + 5.5 + 4.0 |
| `end_dur` | 4.5 s | `min(4.5, max(3.0, 36.0 × 0.16))` = `min(4.5, 5.76)` |
| `endcard_at` | 36.0 s | = `body` |
| `total` | **40.5 s** | 36.0 + 4.5 |

Note `target_duration: 38` in the brief and `40.5` actual. The field is advisory and nothing validates it — the scene durations decide. **Set scene durations to your target; do not trust `target_duration` to hold you to it.**

---

## 4. Render

```powershell
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/signhify-prompt-to-3d-site.json --quality draft
```

```
[2/7] synthesizing narration (Kokoro, Apache-2.0) ...
      narration: 7 scenes, 36.78s speech, track=...\audio\narration.wav
[3/7] hyperframes check ...
      gate clean=True
[4/7] rendering 1080x1920 @30fps quality=draft ...
      video: D:\Autogram\video_studio\output\signhify-prompt-to-3d-site\reel.mp4
[5/7] muxing narration (two-pass loudnorm) ...
[6/7] packaging ...
[7/7] QA ...
[DONE] D:\Autogram\video_studio\output\signhify-prompt-to-3d-site\reel.mp4
       QA: PASS  duration=45.5s  1080x1920  audio=aac
```

Step `[1/7]` is the brief validation gate (`_validate`), which prints nothing on success — it returns a code. Stages 2 and 5 are **narration**; stages 2–7 are skipped or replaced when `--audio` is absent, leaving a silent render. Add `--publish` and the run gains `[8/8] publishing`.

Expected wall-clock: **~55 s** without `--audio` for a 40.5 s Reel — `hyperframes check` 21.3 s, `hyperframes render` 33.3 s, extraction + packaging ~2 s. Add Kokoro synthesis and the mux on top; the shipped 45.5 s narrated Reel is longer than that baseline, so re-measure before quoting a number.

### 4.1 What the seven steps do

| Step | Action | Detail |
|---|---|---|
| 1 | `_validate` | Banned phrases → exit 3; empty `scenes` → exit 3; narration overrun → exit 4. Prints nothing on success |
| 2 | `audio.synthesize_scenes` | **Narration. Skipped without `--audio`.** One wav per narrated scene, Kokoro `af_heart`, then concatenated with 0.25 s inter-scene silence |
| 3 | `hyperframes check` | Runtime · Layout · Motion · WCAG AA contrast · Snapshots. Nonzero exit → `RenderError`, exit **1** |
| 4 | `hyperframes render -f 30 -q draft -o reel.mp4` | headless Chrome, seek-per-frame → libx264. Zero-byte guard |
| 5 | `render.mux_audio` | **Narration.** Skipped without `--audio`. Two-pass `loudnorm`, then `apad` + `-shortest` |
| 6 | `extract_cover(t=0.9s)` + `write_package` | cover.jpg · captions.srt · caption.txt · storyboard.json · brief.json · asset_manifest.json |
| 7 | `qa.inspect` | ffprobe + 10 assertions + 7 extracted frames → `qa_report.json`, `qa_report.md`, `render.log` |
| 8 | `publish` | `--publish` only, and only after step 7 returns PASS |

### 4.2 Quality tiers

| Tier | Use for | Measured |
|---|---|---|
| **`draft`** | **All iteration.** Composition, copy, timing | **33.3 s · 436 kbps · 2,213,568 bytes** |
| `standard` | Candidate review renders | **UNVERIFIED** — not run on this machine |
| `high` | Publishing | **UNVERIFIED** — not run on this machine |

`draft` is fast enough to iterate against but visibly soft on large type. Use `standard` for anything a human other than you will judge, and `high` only for the final cut. Re-measure the wall-clock at those tiers before quoting any timing.

### 4.3 `--skip-gate`

```powershell
.venv\Scripts\python.exe -m video_studio.cli render --brief <brief> --skip-gate
```

Only when you are deliberately debugging the gate itself. `--skip-gate` still does not flip a QA defect to exit 0 — it only stops a failing `hyperframes check` from raising.

---

## 5. Reading the Artifacts

Everything lands in `video_studio/output/<slug>/`.

### 5.1 The manifest

```
output/<slug>/
├── reel.mp4                    the deliverable
├── cover.jpg                   frame at t = 0.9 s
├── captions.srt                burned-in caption track, from CaptionCue[]
├── caption.txt                 Instagram caption: hook / title / hashtags / cta
├── storyboard.json             compiled timing — the audit trail
├── brief.json                  the input, normalized
├── asset_manifest.json         spec + publishing flag
├── qa_report.json              machine verdict
├── qa_report.md                same, human-readable
├── render.log                  every subprocess, exit code, wall-clock
├── audio/                      narration.wav + per-scene wavs. Gitignored (§7)
└── qa_frames/                  7 JPEGs for human inspection
```

### 5.2 `qa_report.md` — what to read first

```
# QA — ...\reel.mp4

- Verdict: **PASS**
- HyperFrames gate clean: True
- Spec: 1080x1920 @30.0fps, 40.5s, h264/no audio, 2213568 bytes
```

That sample is a **silent** render — no `--audio`. The shipped narrated Reel reports `- Spec: 1080x1920 @30.0fps, 45.5s, h264/aac, 3129123 bytes` instead.

Three lines to check every time:

| Line | Healthy value | What a bad value means |
|---|---|---|
| `Verdict` | **PASS** | `FAIL` → read `Remaining defects` below |
| `HyperFrames gate clean` | **True** | `False` → the composition has a runtime/layout/motion problem even if QA passed |
| `…audio` | `aac` when `--audio` was passed | `no audio` when it was not — confirm the flag reached the run |

The ten assertions `qa.py` runs: `container_valid` · `dimensions` · `aspect_9_16` · `fps_supported` · `duration_in_range` · `duration_matches_plan` · `video_codec_h264` · `audio_present` / `audio_absent` · `nonzero_size` · `frames_extractable`.

> **`PASS` is not a production verdict.** `qa.py` inspects container metadata and extracts frames. It does not look at them. `cli.py` writes this line into every report: *"Visual inspection of the extracted frames is still required; a passing automated gate is not a production verdict."*

### 5.3 `captions.srt` — check these three things

```
1
00:00:00,000 --> 00:00:01,909
I typed one sentence.
...
16
00:00:38,132 --> 00:00:40,950
month, with full source code ownership.
```

| Check | Rule | What breaks it |
|---|---|---|
| **Reading rate** | **≤ 15 chars/sec** | Narration longer than the scene allows. The clamp silently shortens hold time — no assertion catches it |
| **Split quality** | One cue per readable line | The splitter used to break on **every** `.`, turning `Three.js` into `No Three.` + `js.` **Fixed in the shipped narrated artifact** — `Three.js` is one cue now |
| **Span** | Cue never exceeds its scene | Guaranteed by `min(start+dur, scene.start + scene.duration − 0.05)` |

Measured on the **shipped narrated Reel** — every one of the 16 cues:

| Cue | chars | hold (s) | chars/sec | Bound by | |
|---|---|---|---|---|---|
| `cap-hook-0` | 21 | 1.909 | 11.00 | text | under |
| `cap-hook-1` | 23 | 2.041 | 11.27 | text | under |
| `cap-problem-0` | 32 | 2.215 | 14.45 | text | under |
| `cap-problem-1` | 33 | 2.235 | 14.77 | text | under |
| `cap-mechanism-0` | 62 | 4.504 | 13.77 | text | under |
| `cap-mechanism-1` | 55 | 3.946 | 13.94 | text | under |
| `cap-no-webgl-0` | 9 | 0.692 | 13.01 | text | under |
| `cap-no-webgl-1` | 12 | 0.923 | 13.00 | text | under |
| `cap-no-webgl-2` | 44 | 3.335 | 13.19 | text | under |
| `cap-proof-0` | 61 | 4.357 | 14.00 | text | under |
| `cap-proof-1` | 52 | 3.714 | 14.00 | text | under |
| `cap-proof-2` | 6 | 0.379 | **15.83** | **scene** | **over — marginal** |
| `cap-export-0` | 34 | 2.397 | 14.18 | text | under |
| `cap-export-1` | 44 | 3.053 | 14.41 | text | under |
| `cap-price-0` | 29 | 2.132 | 13.60 | text | under |
| `cap-price-1` | 39 | 2.818 | 13.84 | text | under |

**How to read this.** The hold time is `min(scene_span, len/15)` — so a cue is either **text-bound** (narration fits the scene, lands at or under 15 ch/s, healthy) or **scene-bound** (narration does not fit, hold time is truncated, rate goes above 15 and the text is genuinely too fast to read). There is no third case.

> **Narration fixed this defect.** The earlier silent render carried **4 of 11** cues over budget, the worst at **36.67 ch/s** (`cap-no-webgl-3`) — unreadable at arm's length. Per-scene synthesis changed the split: that scene is now three cues, not four, and the longest line is 13.19 ch/s. The shipped Reel is **1 of 16** over, and that one — `cap-proof-2`, 6 characters in 0.379 s at 15.83 ch/s — is marginal, not unreadable.

Fix a remaining over-budget cue by shortening the narration (always correct — the caption is the script) or lengthening the scene. Never fix it by raising `_read_speed()`.

### 5.4 `caption.txt`

```
I typed one sentence. A website built itself.

One Prompt. A 3D Website. — built from a single prompt.

#signhifystudio #vibecoding #ai3d #webdev #buildinpublic #startupindia

Follow @signhify.studio for more
```

Built by `publish.py:build_caption`. The hashtag set is a hardcoded module-level list. Edit `HASHTAGS` in `publish.py:15` to change it, then re-run `package`.

### 5.5 `asset_manifest.json`

```json
{
  "slug": "signhify-prompt-to-3d-site",
  "generated": "2026-10-11",
  "video": "...\\reel.mp4",
  "spec": { "width": 1080, "height": 1920, "fps": 30, "duration": 40.5, "aspect": "9:16", "codec": "h264" },
  "publishing": { "enabled": false, "reason": "opt-in via --publish; never default" },
  "assets": []
}
```

`publishing.enabled` is **hardcoded `false`** at `publish.py:67`. There is no `--publish` flag. Publishing is not implemented and not authorized — `08_INSTAGRAM_PUBLISHING.md`.

`generated` and `meta.json.createdAt` are both hardcoded `2026-10-11`. Convenient for diffing, wrong as a build timestamp.

### 5.6 `render.log`

Two entries per run, each with the command, the exit code, and the wall-clock:

```
$ C:\Program Files\nodejs\npx.CMD --yes hyperframes check
[exit=0 21.3s]
...
?  Check passed

$ C:\Program Files\nodejs\npx.CMD --yes hyperframes render -f 30 -q draft -o ...\reel.mp4
[exit=0 33.3s]
```

Also read the `[audio]` lines. `"no TTS provider available"` means a silent render that still exited 0.

Note that `render.py:_run` logs the **last 6,000 characters of stdout** on success and the last 2,500 of **stderr** on failure. Long render progress output is truncated by design.

---

## 6. Inspecting Frames

This is the step that finds real defects. Both defects fixed on this build were found by looking at these JPEGs, not by reading a report.

### 6.1 Where they are

`video_studio/output/<slug>/qa_frames/`:

```
frame_00_t5.79s.jpg     frame_04_t28.93s.jpg
frame_01_t11.57s.jpg    frame_05_t34.71s.jpg
frame_02_t17.36s.jpg    frame_06_t40.42s.jpg
frame_03_t23.14s.jpg
```

### 6.2 Where they come from

`qa.py:extract_frames` samples **6 body frames evenly across the duration, plus the last frame at `duration − 0.08 s`**:

```python
marks = [dur * (i + 1) / (count + 1) for i in range(count)] + [max(dur - 0.08, 0.0)]
```

The last frame is sampled on purpose. An empty final frame is the most common silent packaging defect, and the template guards against it with `tl.set(ec, {opacity:1}, TOTAL - 0.02)`.

For the reference Reel: 40.5 s → body samples at 5.79 / 11.57 / 17.36 / 23.14 / 28.93 / 34.71, plus 40.42.

**The sampling is even, not scene-aligned.** It will usually catch every scene in a 6–8 scene video, but it is not guaranteed. For a careful review, extract your own at scene boundaries:

```powershell
ffmpeg -v error -ss 8.6 -i video_studio\output\<slug>\reel.mp4 -frames:v 1 -q:v 2 -y scratch\at-mechanism-start.jpg
ffmpeg -v error -ss 15.6 -i video_studio\output\<slug>\reel.mp4 -frames:v 1 -q:v 2 -y scratch\at-no-webgl-start.jpg
```

Boundaries from `storyboard.json` — `start`, and `start + 0.6 s` to land past the fade-in.

### 6.3 What to look at

| Check | How to tell |
|---|---|
| **Eyebrow marker** | Must be clean text in `#E05A36` mono. A tofu box or a duplicated glyph means a CSS `content` pseudo-element is colliding with the brief's own marker |
| **Scene counter** | Must read the **active** scene (`6 / 7` mid-video), never a static total |
| **Headline overflow** | 3 lines maximum. A 4th line runs into the subtext |
| **Card fit** | `metrics` with 4+ tiles overflows at 1080 wide |
| **Caption chip** | Legible, inside the frame, not over the bottom chrome |
| **Chrome** | `© 2026` · `@SIGNHIFY.STUDIO` · counter — all present, all mono, all `#666666` |
| **Last frame** | The end card, fully opaque, **not** the empty `#F8F6F0` background |

Full checklist: `07_VIDEO_QUALITY_CHECKLIST.md`.

### 6.4 The two defects this process caught

| # | Defect | Symptom in the frame | Fix |
|---|---|---|---|
| 1 | Eyebrow rendered a tofu box **plus** a duplicate asterisk | `.eyebrow::before { content: '\2723' }` in CSS collided with the brief's own `✳` marker, and the glyph was not in JetBrains Mono | Removed the CSS pseudo-element. The eyebrow now renders the brief's text alone |
| 2 | Scene counter read a meaningless static `07` | The counter was a single element showing the scene **count** | One span per scene, `tl.set()` on at `start`, off at `start_plus_dur` — it now tracks the active scene |

Neither would have been caught by `hyperframes check` or `qa.py`. Both were caught by opening the JPEGs. That is the argument for the checklist.

---

## 7. Narration (`--audio`) — **SHIPPED**

> **Resolved.** The `NameError: name 'WORK_DIR' is not defined` defect is gone. `audio.py` was rewritten to synthesize **per scene** instead of per reel.

```powershell
.venv\Scripts\python.exe -m pip install kokoro-onnx soundfile
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/<slug>.json --quality draft --audio
```

Narration is synthesized **per scene**, and each scene's wav is measured. That measurement is what lets the timeline extend to fit real speech rather than an authored guess, and it is why captions land on the voice instead of drifting from it. The wavs are concatenated with **0.25 s of silence between scenes** and written to `video_studio/output/<slug>/audio/`.

> **Not `work/<slug>/`.** `write_project()` runs `shutil.rmtree()` on the work directory on every build *and* every render. Narration written there was being deleted between the synth and mux steps. `output/<slug>/audio/` survives because `write_project()` never touches it. `audio/` is gitignored — it is regenerable and already muxed into `reel.mp4`.

`render.py:mux_audio` runs two-pass `loudnorm` (I = −16 LUFS, TP = −1.5 dBTP, LRA = 11) then muxes AAC 192 kbps / 48 kHz mono with `+faststart`. The video stream is copied — no re-encode.

Two ffmpeg details that are not optional:

| Detail | Why |
|---|---|
| Write to `reel_mux.mp4`, then `tmp.replace(dest)` | ffmpeg refuses in-place edits — muxing a file onto itself dies with `Output file #0 does not contain any stream` / `same as Input #0 - exiting` |
| `-af loudnorm=...,apad -shortest` | `apad` pads a short narration with silence; `-shortest` then ends the output at the **video** length. Without this a narration shorter than the video truncates the reel and cuts the end card |

**Measured on the shipped Reel** (`signhify-prompt-to-3d-site`, 45.5 s, 7 narrated scenes): speech **36.78 s**, Kokoro `af_heart`, integrated loudness **−16.1 LUFS**, true peak **−1.5 dBFS** (`ffmpeg -af ebur128=peak=true`). The narration track is 38.53 s including the 0.25 s inter-scene gaps, then padded to 45.5 s.

### 7.0 Do not use `hyperframes tts`

The HyperFrames CLI's own `tts` command does **not** work on this machine. It shells out to a Python interpreter it cannot locate — `kokoro-onnx` lives in `.venv`, not system Python — and it still fails with `HYPERFRAMES_PYTHON` set explicitly. The symptom is misleading: it reports the package is missing when it is installed.

`video_studio` therefore calls the `kokoro_onnx` **library directly**. Fewer moving parts, and the per-scene measurement the caption timing depends on is not reachable through the CLI. Full error text and workarounds: `09_TROUBLESHOOTING.md` §3.

### 7.4 Publishing (`--publish`)

`--publish` adds an `[8/8]` stage that runs **only after QA returns PASS** — a failed gate returns 2 and never reaches it. The MP4 must be publicly reachable by Meta's crawler; the URL defaults to `$PUBLIC_CDN_BASE/<slug>/reel.mp4`.

Use `--publish-dry-run` first. It resolves every Meta call and publishes nothing. `asset_manifest.json` is only rewritten to `publishing.enabled: true` on a real success. Exit **5** is missing or unauthorized credentials; exit **6** is quota exhausted, container `FAILED`, or an API error. Spec: `08_INSTAGRAM_PUBLISHING.md`.

### 7.1 Scene duration must relate to narration length

`build_captions` gives a cue `min(scene_span, len(text) / 15)` seconds. That clamp hides a mismatch instead of reporting it. Budget narration at **≤ 15 chars per second of scene**, which is roughly **2.2 words per second** — natural speech pace with no headroom.

| Scene duration | Max narration |
|---|---|
| 4.0 s | 60 chars (~10 words) |
| 4.5 s | 67 chars (~11 words) |
| 5.0 s | 75 chars (~12 words) |
| 5.5 s | 82 chars (~13 words) |
| 6.0 s | 90 chars (~15 words) |
| 7.0 s | 105 chars (~17 words) |

Three ways to fix an over-budget cue, in order of preference:

| Fix | Effect |
|---|---|
| **Shorten the narration** | Cheapest. Always correct — the caption is the script |
| **Lengthen the scene** | Costs runtime. Only worth it if the beat needs the dwell time |
| **Split the sentence into two cues** | Requires editing the splitter; the current one is naive |

### 7.2 If TTS audio outruns the visuals

`compile_storyboard` still accepts a `narration_duration` argument, but **`cmd_render` does not use it.** It calls `compile_storyboard(b)` with the default `None` and then stretches the compiled storyboard directly, after synthesis:

```python
files, speech = synthesize_scenes(b, sb, log)
if files:
    sb.total = max(sb.total, round(speech + 0.25 * len(files), 3))
```

So the timeline **does** grow to fit real speech when narration runs long — the `narration_duration` parameter is the vestigial path, not this one. `qa.py` then checks the rendered duration against `sb.total` via `duration_matches_plan`, so a mismatch is a QA defect (exit 2), not a silent truncation.

If narration outruns the video anyway, `apad` pads and `-shortest` ends the output at the video length — the audio is cut, not the video. Read `render.log` to see which provider actually produced a track; never infer it from an env var.

---

## 8. Iteration

### 8.1 The loop

```
1. edit video_studio/briefs/<slug>.json          ← or templates/composition.html.jinja2
2. python -m video_studio.cli build --brief …    ← 1 s. validates + compiles
3. python -m video_studio.cli render --brief … --quality draft
4. open output/<slug>/qa_frames/*.jpg
5. read output/<slug>/qa_report.md
```

**`work/<slug>/` is destroyed on every `build` and every `render`** (`shutil.rmtree`, `storyboard.py:154`). Never hand-edit `work/<slug>/index.html` — it will be gone. Edit the brief or the template.

| Change | Where | Re-render needed? |
|---|---|---|
| Copy, headline, duration, scene order | brief JSON | Yes |
| Add a bullet or metric | brief JSON | Yes |
| Change the accent colour | brief `accent`, or `data/brand.json` | Yes |
| Brand token — fonts, grid, colours, chrome | `templates/composition.html.jinja2` `<style>` | Yes, **all** briefs |
| Layout, motion, z-order | `composition.html.jinja2` | Yes |
| New visual type | `storyboard.py:HEAD_CLASS` **+** a template branch | Yes — §8.2 |
| Caption speed budget | `storyboard.py:72` `_read_speed()` | Yes |
| QA assertion | `qa.py:inspect` | No — re-run `qa` only |

### 8.2 Adding a scene visual in one sentence

Add the name to `HEAD_CLASS` in `storyboard.py:22`, add an `{% elif sc.visual == 'x' %}` branch in `composition.html.jinja2`, add it to the `.inner` list at line 132 if it is dense, and add CSS. Four edits, no other module. Full walkthrough: `03_SYSTEM_ARCHITECTURE.md` §10.1.

### 8.3 Bounded-retry policy — **mandatory**

> **Maximum 2 repair attempts per defect. Then escalate to a human. Never loop render-and-repair.**

This matches the repo's fail-closed rule in `AGENTS.md`: *"If the quality gate fails after 2 retries, the pipeline raises `RuntimeError` and does not publish."* A gate that can be bypassed is not a gate.

| Attempt | Action | Then |
|---|---|---|
| **1** | Read the actual defect. Read `render.log` and the extracted frame. Form one hypothesis | If fixed → re-render. If not → attempt 2 |
| **2** | Try a different hypothesis. Check the brief, then the template, then `data/brand.json` | If fixed → re-render. If not → **escalate** |
| **3+** | **STOP.** | Not permitted |

| Repeated failure | Escalate to |
|---|---|
| Same defect after 2 attempts | Human review of the brief + template. The fix is probably not in either |
| `hyperframes check` fails with a message not in `09_TROUBLESHOOTING.md` | Read the HyperFrames message verbatim. Do not add `--skip-gate` as a response |
| Render succeeds but looks wrong every time | The composition is wrong, not the render. Stop rendering; fix the template |
| QA flips between PASS and FAIL on identical input | Determinism is broken — Chrome or FFmpeg changed. Check `hyperframes doctor` |

**A render that takes 33 s is cheap. A render-and-review loop that never converges is not.** Two attempts is the budget, and it is a real budget.

### 8.4 Before shipping a candidate

```powershell
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/<slug>.json --quality standard
.venv\Scripts\python.exe -m video_studio.cli qa --video video_studio\output\<slug>\reel.mp4 --frames video_studio\output\<slug>\qa_frames --no-audio
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,nb_frames -of default=noprint_wrappers=1 video_studio\output\<slug>\reel.mp4
```

Then work `07_VIDEO_QUALITY_CHECKLIST.md` top to bottom. The automated gate is necessary and not sufficient.

---

## 9. Untested Paths

Honest inventory. Do not assume these work.

| Path | State | Note |
|---|---|---|
| `terminal` scene visual | **[I]** in the template, **never rendered** | No brief uses it. Add one and check the frames before relying on it |
| `statement` / `hook` with `bullets` | Not rendered | Bullets only render under `feature_card` and `terminal` |
| `metrics` with 4+ tiles | Not tested | Likely overflows at 1080 wide |
| `--quality standard` / `--quality high` | **UNVERIFIED** | Never run. Wall-clock and bitrate unknown |
| `--audio` end to end | **[S] shipped and measured** | 45.5 s narrated Reel, −16.1 LUFS, −1.5 dBFS true peak, QA PASS |
| `mux_audio` | **[S] executed** | Runs on every `--audio` render. `apad` + `-shortest` verified — narration shorter than video does not truncate the end card |
| `--publish` | **[I] implemented, never run live** | `--publish-dry-run` path only. No Reel has been published from this pipeline |
| `compile_storyboard(narration_duration=…)` | **[N] dead code** | `cli.py` never passes it; it stretches `sb.total` directly instead (§7.2) |
| `narration_enabled` | **[N] dead field** | Never read |
| `target_duration` | **[N] dead field** | Never read |
| `Brief.target_duration` mismatch | Unflagged | The reference brief says 38; output is 40.5 |
| `Caption` pydantic model | **[N] dead** | `brief.py:23` defines it; `build_captions` uses its own dataclass |
| Storyboard `counter` field | **[N] dead** | Written to JSON, never used by the template |
| `--slug` override | **[I]** | Works; untested in production |
| Instagram publishing | **[N]** | Not implemented. Not authorized |

---

## 10. One-Page Procedure

```
BEFORE
  □ Concept scores ≥ 4.00 on the rubric (02_BRAND_AND_CONTENT_STRATEGY.md §11), verifiability ≥ 3
  □ Every claim traces to signhify.dpdns.org, data/brand.json, or something observed
  □ Zero banned phrases — the build enforces it, exit 3
  □ Narration ≤ 15 chars/sec per scene
  □ Scene ids unique and CSS-safe

BUILD
  .venv\Scripts\python.exe -m video_studio.cli build  --brief video_studio/briefs/<slug>.json
  □ scenes=N captions=N total=Ns endcard@Ns
  □ exit 0

RENDER
  .venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/<slug>.json --quality draft
  □ gate clean=True
  □ QA: PASS
  □ exit 0
  □ ≤ 2 repair attempts per defect, then escalate — 08 §8.3

INSPECT  (the part that finds real defects)
  □ open every JPEG in output/<slug>/qa_frames/
  □ first frame · every scene transition · last frame
  □ no tofu glyphs · counter tracks the active scene
  □ no headline overflow · captions legible
  □ captions.srt: ≤ 15 chars/sec, no broken splits
  □ full pass of 07_VIDEO_QUALITY_CHECKLIST.md

RE-RENDER AT PUBLISH QUALITY
  .venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/<slug>.json --quality standard
  □ re-run the frame inspection on the new render

SHIP
  □ reel.mp4 · cover.jpg · captions.srt · caption.txt · qa_report.md all present
  □ ffprobe confirms 1080×1920, 30/1, h264, 3–90 s
  □ asset_manifest.json publishing.enabled == false  ← still false. Shipping is a manual, human decision.
```

---

*Compiled 2026-10-11 from `video_studio/cli.py`, `brief.py`, `storyboard.py`, `render.py`, `qa.py`, `publish.py`, `audio.py`, the reference brief, and the reference artifact. Every command was executed on the machine of record and its real output recorded above. Every defect listed was found by running the code, not by reading it.*