# Video Studio — System Architecture

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/03_SYSTEM_ARCHITECTURE.md` |
| **Date** | 2026-10-11 |
| **Package** | `video_studio/` at repo root, `D:\Autogram\video_studio` |
| **Engine** | HyperFrames CLI v0.8.58 (Apache-2.0) + FFmpeg 8.0.1 |
| **Reference artifact** | `video_studio/output/signhify-prompt-to-3d-site/reel.mp4` — 40.5 s, PASS |
| **Companions** | `01_TECHNICAL_RESEARCH.md`, `04_COSTS_AND_LICENSING.md`, `05_SETUP_AND_INSTALLATION.md`, `06_PRODUCTION_RUNBOOK.md`, `09_TROUBLESHOOTING.md` |

Status labels used throughout: **[I]** implemented and verified on this machine · **[P]** partial · **[N]** planned, not built.

---

## 1. Architecture Diagram

```
                        video_studio/briefs/<slug>.json      (human-authored input)
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ 1. brief.py        Brief (pydantic v2)                                    │
 │                    load_brand() → data/brand.json                         │
 │                    banned_hits() → 16-entry avoid-list scan              │
 │                    slug regex guard · accent #RRGGBB guard · fps 24–60    │
 └──────────────────────────────────────────────────────────────────────────┘
                                    │  Brief
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ 2. storyboard.py   compile_storyboard()                                   │
 │                    · absolute start times, cumulative over scenes         │
 │                    · end card = min(4.5, max(3.0, body*0.16))            │
 │                    · build_captions() — split on ./? , clamp to 15 ch/s   │
 │                    write_project()  → Jinja2 StrictUndefined             │
 │                    · index.html · hyperframes.json · meta.json            │
 │                    · package.json · assets/logo.png                      │
 └──────────────────────────────────────────────────────────────────────────┘
                                    │  video_studio/work/<slug>/index.html
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ 3. templates/composition.html.jinja2                                     │
 │      data-composition-id="root" · data-start=0 · data-duration=total     │
 │      CSS tokens from data/brand.json · blueprint grid · persistent chrome │
 │      ONE paused GSAP timeline, absolute-time .to()/.fromTo()/.set()       │
 │      window.__timelines["root"] = tl                                     │
 └──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ 4. render.py       npx --yes hyperframes check      → GATE               │
 │                    · Runtime · Layout · Motion · Contrast WCAG AA ·      │
 │                      Snapshots                                            │
 │                    gate["clean"] = ("Check passed" in stdout)            │
 └──────────────────────────────────────────────────────────────────────────┘
                                    │  gate clean?  → else RenderError (exit 1)
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ 5. render.py       npx --yes hyperframes render -f 30 -q draft -o reel    │
 │                    headless Chrome, seek-per-frame → FFmpeg libx264       │
 │                    zero-byte guard                                        │
 └──────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │ --audio  [P] currently broken │  no --audio  (shipped path)
                    ▼                                ▼
 ┌──────────────────────────────┐      ┌────────────────────────────────────┐
 │ 6. audio.py                  │      │ 7. publish.py  write_package()     │
 │  _kokoro() → npx hf tts      │      │    captions.srt                     │
 │  _edge()   → edge-tts        │      │    caption.txt                      │
 │  render.py:mux_audio()       │      │    storyboard.json                  │
 │   pass 1 loudnorm measure    │      │    brief.json                       │
 │   pass 2 loudnorm apply      │      │    asset_manifest.json              │
 │   I=-16 TP=-1.5 LRA=11       │      │      → publishing.enabled = false  │
 │   aac 192k / 48k / faststart │      │  extract_cover() t=0.9 s          │
 └──────────────────────────────┘      └────────────────────────────────────┘
                    └───────────────┬────────────────┘
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ 8. qa.py           ffprobe → streams + format                           │
 │                    10 assertions · verdict PASS/FAIL                      │
 │                    extract_frames(): 6 body samples + LAST frame @ dur-0.08│
 │                    → video_studio/output/<slug>/qa_frames/               │
 └──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        video_studio/output/<slug>/   reel.mp4 · cover.jpg · captions.srt
                                      caption.txt · storyboard.json
                                      brief.json · asset_manifest.json
                                      qa_report.json · qa_report.md
                                      render.log · qa_frames/
                                    │
                                    ▼
                        9. publish  [N] NOT IMPLEMENTED
                           Meta Graph API container → poll → publish
                           spec: 08_INSTAGRAM_PUBLISHING.md
```

---

## 2. Stage Inventory

| # | Stage | Module | State | Fails at |
|---|---|---|---|---|
| 1 | Validate brief | `brief.py` | **[I]** | `cli.py` returns 3 on banned phrase / no scenes |
| 2 | Compile storyboard | `storyboard.py` | **[I]** | raises → exit 1 |
| 3 | Emit HyperFrames project | `storyboard.py` | **[I]** | raises → exit 1 |
| 4 | HyperFrames QA gate | `render.py:check_project` | **[I]** | nonzero exit raises → exit 1 |
| 5 | Render MP4 | `render.py:render_project` | **[I]** | nonzero exit or 0-byte → exit 1 |
| 6a | TTS synthesis | `audio.py:synthesize_narration` | **[P]** broken | `NameError` — see §11 |
| 6b | Loudnorm + mux | `render.py:mux_audio` | **[P]** untested | raises → exit 1 |
| 7 | Cover + package | `publish.py` | **[I]** | raises → exit 1 |
| 8 | Video QA + frames | `qa.py:inspect` | **[I]** | `cmd_render` returns 2 on any defect |
| 9 | Instagram publish | — | **[N]** | not written; `publishing.enabled = false` |

---

## 3. Data Contract — The Brief

`brief.py:Brief`, a pydantic v2 `BaseModel`. JSON at `video_studio/briefs/<slug>.json`.

### 3.1 Top-level fields

| Field | Type | Required | Default | Constraint | Consumed by |
|---|---|---|---|---|---|
| `slug` | str | **yes** | — | non-empty; every char in `[A-Za-z0-9-_]` | `work/<slug>`, `output/<slug>`, `#root` composition id |
| `title` | str | **yes** | — | — | `<title>`, end-card `h2`, `build_caption()` |
| `pillar` | str | no | `"product"` | — | metadata only; not rendered |
| `hook` | str | **yes** | — | — | end-card `p`, `build_caption()` line 1 |
| `cta` | str | no | `"Follow @signhify.studio for more."` | — | end-card `.cta` button, caption last line |
| `accent` | str | no | `""` → `brand.json` accent | if set: exactly `#RRGGBB` | `:root{--accent}` in the template |
| `notes` | str | no | `""` | — | authoring only; not rendered |
| `width` | int | no | `1080` | — | `html,body`, root `data-width` |
| `height` | int | no | `1920` | — | `html,body`, root `data-height` |
| `fps` | int | no | `30` | `24 ≤ fps ≤ 60` | `render -f`, QA `fps_supported` |
| `target_duration` | float | no | `40.0` | `> 0` | **advisory only — not enforced** (§3.4) |
| `narration_enabled` | bool | no | `true` | — | **advisory only — not read anywhere** (§3.4) |
| `sources` | list[str] | no | `[]` | — | provenance record; not rendered |
| `scenes` | list[Scene] | **yes** (≥1) | `[]` | empty → exit 3 | everything visual |

### 3.2 Scene fields

| Field | Type | Default | Rendered by |
|---|---|---|---|
| `id` | str | required | element `id`, caption cue ids, counter id `cnt-<id>` |
| `visual` | str | required | selects the template branch (§6.1) and `HEAD_CLASS` |
| `duration` | float | required, `> 0` | `data-duration`, timeline math |
| `narration` | str | `""` | caption source, TTS source, `captions.srt` |
| `headline` | str | `""` | `.headline {{ head_class }}` |
| `subtext` | str | `""` | `.subtext` |
| `eyebrow` | str | `""` | `.eyebrow` — orange mono label |
| `bullets` | list[str] | `[]` | `feature_card` cards, `terminal` lines |
| `metrics` | list[{`v`,`k`}] | `[]` | `metrics` row — `.v` big numeral, `.k` mono label |
| `source_url` | str | `""` | `browser` chrome URL pill; falls back to `signhify.dpdns.org` |

### 3.3 Validators that actually fire

| Guard | Location | Behaviour |
|---|---|---|
| `slug` charset | `brief.py:67` | `ValueError` — "slug must be alphanumeric with -/_ only" |
| `accent` hex | `brief.py:74` | `ValueError` unless `#` + 6 hex digits |
| `fps` range | `brief.py:60` | pydantic constraint 24–60 |
| `duration > 0` | `brief.py:40` | pydantic constraint |
| `caption.end > caption.start` | `brief.py:28` | validator on the unused standalone `Caption` model |
| banned phrases | `brief.py:80` `banned_hits()` | not a validator — called explicitly by `cli.py` |

**Banned-phrase scope.** `banned_hits()` lowercases and concatenates `title`, `hook`, `cta`, and per scene `narration`, `headline`, `subtext`, `eyebrow`, and joined `bullets`. It does **not** scan `sources`, `notes`, `pillar`, or metric labels.

### 3.4 Fields that are accepted but unused

| Field | Reality |
|---|---|
| `target_duration` | Never read by any module. `Storyboard.total` is derived from scene durations. The real brief sets `38`; the rendered file is `40.5 s`. Not an error — just advisory drift. |
| `narration_enabled` | Never read. `--audio` is the only switch. |
| `pillar` | Metadata only. |
| `brief.sources` | Copied into `output/<slug>/brief.json`; no validation that a claim has a source. |

---

## 4. Data Contract — Storyboard Output

Dataclasses in `storyboard.py`. Serialized verbatim to `output/<slug>/storyboard.json`.

### 4.1 `Storyboard`

| Field | Type | Derivation |
|---|---|---|
| `slug`, `width`, `height`, `fps` | str/int | copied from the brief |
| `total` | float | `body + end_dur`, see §5.2 |
| `endcard_at` | float | `body` — the sum of scene durations |
| `endcard_head` | str | `brief.title` |
| `endcard_sub` | str | `brief.hook` |
| `counter` | str | `f"{len(raw):02d}"` — **written into the JSON but not used by the template**; the visible counter is per-scene (`N / 7`) |
| `scenes` | list[CompiledScene] | see §4.2 |
| `captions` | list[CaptionCue] | see §4.3 |
| `audio` | str \| None | `write_project(audio_rel=...)`; stripped by `_to_dict()` before Jinja render, then set on `sb` for the template's media block |
| `accent` | str | `brief.accent or brand.colors.accent` |
| `cta` | str | `brief.cta` |

### 4.2 `CompiledScene`

| Field | Derivation |
|---|---|
| `id`, `visual`, `narration`, `headline`, `subtext`, `eyebrow`, `bullets`, `metrics`, `source_url` | verbatim from the brief scene |
| `start` | cumulative sum of prior durations, rounded to 3 dp |
| `duration` | `min(start + brief_duration, endcard_at) - start` — clamped so no scene runs into the end card |
| `start_plus_dur` | `end - 0.35` — the fade-out cue, deliberately 0.35 s early |
| `head_class` | `HEAD_CLASS.get(visual, "")` → `""` or `"sm"` (84 px headline) |

### 4.3 `CaptionCue`

| Field | Derivation |
|---|---|
| `id` | `f"cap-{scene_id}-{index}"` |
| `text` | one sentence-ish fragment |
| `start` | `scene.start + i * span` where `span = scene.duration / fragment_count` |
| `dur` | `min(span, len(text) / 15.0)` |
| `end` | `min(start + dur, scene.start + scene.duration - 0.05)` |

---

## 5. The Timing Model

### 5.1 Absolute seconds, paused timeline

There is no playhead and no relative chaining. Every animation is written as an absolute position on one paused GSAP timeline.

```js
const tl = gsap.timeline({paused:true});
tl.to(els,  {opacity:1, duration:0.42},             4.0);   // scene fades in
tl.fromTo(els, {y:46}, {y:0, duration:0.55, ...},   4.0);   // and rises
tl.to(els,  {opacity:0, duration:0.38},             8.15);  // fades out before its end
window.__timelines["root"] = tl;
tl.seek(0);
```

The third argument to `gsap.to` / `.fromTo` is **absolute timeline seconds**, not an offset. HyperFrames advances the timeline frame by frame; nothing in the composition runs on `requestAnimationFrame` or a wall clock.

### 5.2 Duration derivation

```
body     = Σ scene.duration
end_dur  = min(4.5, max(3.0, body * 0.16))      # never more than ~16% of body, capped 4.5 s
endcard_at = body
total      = body + end_dur
```

Real numbers for `signhify-prompt-to-3d-site`:

| Scene | brief duration | start | compiled duration | fade-out cue (`start_plus_dur`) |
|---|---|---|---|---|
| `hook` | 4.0 | 0.0 | 4.0 | 3.65 |
| `problem` | 4.5 | 4.0 | 4.5 | 8.15 |
| `mechanism` | 7.0 | 8.5 | 7.0 | 15.15 |
| `no-webgl` | 5.0 | 15.5 | 5.0 | 20.15 |
| `proof` | 6.0 | 20.5 | 6.0 | 26.15 |
| `export` | 5.5 | 26.5 | 5.5 | 31.65 |
| `price` | 4.0 | 32.0 | 4.0 | 35.65 |
| **body** | **36.0** | | | `endcard_at = 36.0` |
| **end card** | 4.5 | 36.0 | 4.5 | `end_dur = min(4.5, max(3.0, 36*0.16)) = 4.5` |
| **total** | **40.5** | | | matches `ffprobe` exactly |

### 5.3 HyperFrames attribute contract

| Attribute | Meaning | Set in |
|---|---|---|
| `data-composition-id="root"` | root composition id; the timeline registers under this id | template line 122 |
| `data-start` / `data-duration` | **seconds**, absolute | every scene, caption, counter |
| `data-width` / `data-height` | render canvas | root only |
| `data-track-index` | **display-only.** Does not order paint or overlap | scenes only |
| `class="clip"` | marks an animatable clip | **not used** — see §11.3 |

**Paint order is CSS `z-index`.** Template z-map: grid `0` · scenes `10` · chrome `90` · accent bar `95` · captions `120` · end card `130`.

### 5.4 Caption reading budget

`_read_speed()` returns a hard-coded **15.0 chars/sec** (mobile-first). Cue hold time is `min(scene_span, len/15)`. The clamp means a scene whose narration is longer than 15 ch/s × duration gets **silently truncated in hold time, not flagged**. Exact measured rates across all 11 cues of the shipped Reel:

| Cue | chars | hold (s) | chars/sec | Bound by | |
|---|---|---|---|---|---|
| `cap-hook-0` | 21 | 1.400 | 15.00 | text | ok |
| `cap-hook-1` | 23 | 1.533 | 15.00 | text | ok |
| `cap-problem-0` | 66 | 4.400 | 15.00 | text | ok |
| `cap-mechanism-0` | 118 | 6.950 | **16.98** | **scene** | **over** |
| `cap-no-webgl-0` | 9 | 0.600 | 15.00 | text | ok |
| `cap-no-webgl-1` | 9 | 0.600 | 15.00 | text | ok |
| `cap-no-webgl-2` | 3 | 0.200 | 15.00 | text | ok (but split defect, §11.4) |
| `cap-no-webgl-3` | 44 | 1.200 | **36.67** | **scene** | **over, 2.4×** |
| `cap-proof-0` | 121 | 5.950 | **20.34** | **scene** | **over** |
| `cap-export-0` | 79 | 5.267 | 15.00 | text | ok |
| `cap-price-0` | 69 | 3.950 | **17.47** | **scene** | **over** |

The rate is either exactly 15.00 (text-bound: narration fits the scene) or above 15 (scene-bound: it does not). **4 of 11 cues are scene-bound in the shipped artifact and no assertion catches it.** Human-inspection item: `07_VIDEO_QUALITY_CHECKLIST.md` §6.

---

## 6. Composition Template

### 6.1 Visual types

Driven by `data-scene="{{ sc.visual }}"` and the `{% if %}` chain in `composition.html.jinja2`.

| `visual` | Branch | Extra layout class | Body rendered from |
|---|---|---|---|
| `hook` | base only | — | `eyebrow` + `headline` + `subtext` |
| `statement` | base only | — | `eyebrow` + `headline` + `subtext` |
| `feature_card` | `.cards` stack | `.inner` | `bullets[]` → one white card each, orange/green dot |
| `metrics` | `.metricrow` | `.inner` | `metrics[]` → big accent numeral + mono key |
| `terminal` | `.terminal` | `.inner` | `bullets[]` → `<br>`-joined mono lines on `#0B0B0C` |
| `browser` | `.browser` | `.inner` | `source_url` in the URL pill + 3 placeholder bars |
| `end_card` | **not a scene type** | — | reserved, fixed 4.5 s block emitted outside the scene loop |

`HEAD_CLASS` maps `feature_card`, `metrics`, `terminal`, `browser`, `end_card` → `"sm"` (84 px headline); `hook` and `statement` → `""` (104 px).

### 6.2 Always-present chrome

| Element | Content | z-index | Animated? |
|---|---|---|---|
| `#grid` | 64 px blueprint grid, `rgba(0,0,0,.035)` | 0 | no |
| `.accentbar` | 10 px `#E05A36` bar at the very top | 95 | no |
| `.chrome.tl` | `© 2026` | 90 | no |
| `.chrome.tc` | `@signhify.studio` | 90 | no |
| `.chrome.counters` | one `N / total` span per scene, only the active one visible | 90 | opacity only |
| `#captions` | burned-in caption chips, `bottom: 300px` | 120 | hard cut, no fade |

### 6.3 Per-scene motion

Three nested passes, all absolute:

| Pass | What | Timing |
|---|---|---|
| 1 | scene fades in + rises 46 px | at `start`, 0.42 s / 0.55 s |
| 2 | each direct child rises 26 px, staggered `0.12 + i * 0.07` | at `start` |
| 3 | scene fades out | at `start_plus_dur`, 0.38 s |
| 4 | counter span on at `start`, off at `start_plus_dur` | `tl.set()` only |

### 6.4 End card

`display:none` → `display:flex` at `endcard_at`, opacity to 1 over 0.5 s, then logo (`scale 0.86`, `back.out(1.7)`), `h2`, `.cta`, `.site` on staggered offsets. Final line:

```js
tl.set(ec, {opacity:1}, TOTAL - 0.02);   // hold to the last frame
```

This is what stops the last frame from being empty — verified at `frame_06_t40.42s.jpg`.

---

## 7. On-Disk Layout

```
D:\Autogram\
├── data\brand.json                       ← single source of brand truth
├── assets\signhify-logo-vector.png       ← copied into each work project
├── requirements.txt
├── .venv\Scripts\python.exe              ← 3.14.7; has jinja2/pydantic/pillow
├── video_studio\
│   ├── __init__.py                       ← empty
│   ├── cli.py         brief.py       storyboard.py
│   ├── render.py      qa.py          publish.py    audio.py
│   ├── templates\composition.html.jinja2          ← 231 lines
│   ├── briefs\
│   │   └── signhify-prompt-to-3d-site.json        ← INPUT
│   ├── work\                                          ← GENERATED, rmtree'd each build
│   │   └── <slug>\
│   │       ├── index.html                           ← rendered composition
│   │       ├── hyperframes.json                     ← paths + media.autoProxy
│   │       ├── meta.json                            ← id / name / createdAt (hardcoded date)
│   │       ├── package.json                         ← check / render / snapshot scripts
│   │       └── assets\logo.png                      ← copied from repo assets/
│   └── output\                                         ← ARTIFACTS
│       └── <slug>\
│           ├── reel.mp4                    ← the deliverable
│           ├── cover.jpg                   ← t = 0.9 s frame
│           ├── captions.srt                ← from CaptionCue[]
│           ├── caption.txt                 ← hook / title / hashtags / cta
│           ├── storyboard.json             ← compiled timing, auditable
│           ├── brief.json                  ← the input, normalized
│           ├── asset_manifest.json         ← publishing.enabled = false
│           ├── qa_report.json              ← machine verdict
│           ├── qa_report.md                ← same, human-readable
│           ├── render.log                  ← every subprocess + exit + wall-clock
│           └── qa_frames\frame_NN_t<ts>s.jpg
```

**`work/<slug>` is destroyed and rewritten on every `build` and every `render`** (`storyboard.py:154-155` `shutil.rmtree`). Edit the brief or the template, never the generated `index.html`.

---

## 8. HyperFrames Gate

`render.py:check_project` runs `npx --yes hyperframes check` in the project dir and decides cleanliness by **substring match**:

```python
return {"gate": "hyperframes check", "clean": "Check passed" in out, "output": out[-2500:]}
```

Suites: **Runtime · Layout · Motion · Contrast (WCAG AA) · Snapshots**.

Real output on the shipped project (`render.log`):

| Suite | Result |
|---|---|
| Runtime | 0 errors, 0 warnings |
| Layout | 0 errors, 0 warnings, **2 info** — `text_occluded` for `div.chrome.tl` and `div.chrome.tc` inside `#endcard` at t=38.25 s |
| Motion | 0 errors, 0 warnings |
| Contrast | **36/36 text checks pass WCAG AA** |
| Snapshots | disabled |
| Verdict | `Check passed`, exit 0, **21.3 s** |

The two Layout infos are **expected**: the end card (`z-index:130`, opaque `--bg`) deliberately covers the chrome (`z-index:90`) for the final 4.5 s. Frame `frame_06_t40.42s.jpg` confirms the result is correct.

Two advisory notice classes appear as `?` lines but do **not** affect the verdict: `timed_element_missing_clip_class` and `nested_structure_needs_subcomposition`. They are Studio/linter ergonomics hints, not runtime errors.

**Known fragility:** the gate verdict depends on the literal string `"Check passed"`. A HyperFrames version bump that changes that wording silently reports `clean: false` or, worse, `clean: true` on a failing run. See `09_TROUBLESHOOTING.md`.

---

## 9. Determinism

### 9.1 Fully deterministic

| Stage | Why |
|---|---|
| `brief.py` validation | Pure function of the JSON + `data/brand.json` |
| `compile_storyboard` | Pure arithmetic over scene durations. No clock, no RNG |
| `build_captions` | Pure function of narration text |
| `write_project` → `index.html` | Jinja2 `StrictUndefined`, `autoescape=False`, fixed template. `logo.png` is a byte copy |
| `hyperframes check` | Deterministic static + runtime analysis |
| `hyperframes render` | **Seek-per-frame.** HyperFrames opens headless Chrome, seeks the paused GSAP timeline to `frame_index / fps`, screenshots, and pipes frames to FFmpeg `libx264`. There is no wall-clock sampling and no rAF race, so identical input produces an identical stream |

`meta.json.createdAt` and `asset_manifest.generated` are **hardcoded to `2026-10-11`** (`storyboard.py:176`, `publish.py:63`). That makes the metadata stable rather than "now" — convenient for diffing, wrong if you rely on it as a build timestamp.

### 9.2 Conditionally deterministic

| Input | Condition |
|---|---|
| Google Fonts (Plus Jakarta Sans, Inter, JetBrains Mono) | Template fetches from `fonts.googleapis.com`. Offline → fallback stacks (`system-ui`, `monospace`). **Network is on the critical path** |
| GSAP 3.14.2 | Fetched from `cdn.jsdelivr.net`. Same offline caveat |
| Chrome Headless Shell | Downloaded by HyperFrames. A different Chrome build changes rasterization and therefore pixel output, though not composition logic |
| FFmpeg | `libx264` encoder version and CPU flags change bitstream bytes |

**Determinism claim, stated precisely:** identical brief + identical HyperFrames version + identical Chrome build + network access to the font and GSAP CDNs → identical MP4 bytes. Change any of those and you get a different file. Do not treat "deterministic" as "byte-identical forever."

### 9.3 Non-deterministic by nature

| Stage | Provider | Effect |
|---|---|---|
| TTS | `audio.py:_kokoro` → `npx hyperframes tts` (Kokoro-82M) | Model inference; same input generally stable but not guaranteed |
| TTS | `audio.py:_edge` → `edge-tts` (Microsoft) | **Network service.** Different voice, different audio, every call |
| Font rasterization | OS font cache / Chrome | First render after a font download may differ from later ones |

### 9.4 Not built

Word-level caption timing from `faster-whisper` is specified in `01_TECHNICAL_RESEARCH.md` §5.5 and is a dependency in `requirements.txt`, but `video_studio` computes caption times arithmetically. No transcription stage exists.

---

## 10. Extension Guide

### 10.1 Add a new visual component

Two edits. Nothing else.

**Step 1 — `storyboard.py:22-23`**, register the headline size:

```python
HEAD_CLASS = {"hook": "", "feature_card": "sm", "metrics": "sm", "terminal": "sm",
              "browser": "sm", "end_card": "sm", "statement": "", "timeline": "sm"}
```

**Step 2 — `composition.html.jinja2`**, add a branch to the `{% elif %}` chain at line ~151:

```jinja
{% elif sc.visual == 'timeline' %}
  <div class="timeline">
    {% for b in sc.bullets %}<div class="tline"><span class="dot"></span>{{ b }}</div>{% endfor %}
  </div>
```

**Step 3 — the `.inner` padding list**, line 132. Dense components need the tighter bottom padding:

```jinja
{% if sc.visual in ('feature_card','terminal','browser','metrics','timeline') %} inner{% endif %}
```

**Step 4 — CSS.** Add the class inside the `<style>` block. No z-index change needed; `.scene` is already at `10` and its children inherit stacking.

**Step 5 — verify:**

```powershell
.venv\Scripts\python.exe -m video_studio.cli build  --brief video_studio/briefs\<slug>.json
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs\<slug>.json
```

Then **open the extracted frames.** A component that compiles is not a component that looks right.

### 10.2 Add a narration provider

`audio.py` is interface-first. One function, one chain entry.

```python
def _myprovider(project: Path, text: str) -> Path | None:
    """One line: what it is, what it costs, what licence it carries."""
    if not shutil.which("some-binary"):
        return None
    try:
        out = project / "voice.wav"
        r = subprocess.run([...], capture_output=True, timeout=600, cwd=str(project))
        if r.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return out
    except Exception:
        pass
    return None
```

Register at `audio.py:70`:

```python
wav = _kokoro(proj, text) or _edge(proj, text) or _myprovider(proj, text)
```

Contract: return a 48 kHz mono WAV `Path`, or `None`. Return `None` on any failure — the caller deliberately renders silently rather than failing the pipeline. **Fix `WORK_DIR` on line 69 before using any of this** (§11.1).

### 10.3 Add a QA check

`qa.py:inspect`, after the existing `rep.check(...)` block at line 103:

```python
rep.check("pixel_format", (v.get("pix_fmt") or "") == "yuv420p", v.get("pix_fmt", "none"))
```

`QAReport.check()` appends to `checks` and, on failure, appends to `defects`. `cmd_render` returns **2** if `defects` is non-empty. `cmd_qa` returns 0 only when `verdict == "PASS"`. Nothing else needs changing — `qa_report.json`, `qa_report.md`, and the CLI exit code all derive from it.

A check that can be bypassed is not a check. Do not add a check with a default-true predicate.

### 10.4 Add a CLI subcommand

`cli.py:main` builds all four subcommands in one loop over `("build","render","package")`, with `render` getting extra flags via `if name == "render"`. Add a fourth name to the tuple and give it a `fn`, or add a separate `sub.add_parser(...)` block like `qa`. Exit codes are the return values of the `cmd_*` functions.

---

## 11. Known Defects in the Current Build

These are live in the code as written on 2026-10-11. None is documented elsewhere.

### 11.1 `audio.py:69` — `NameError` on every `--audio` run

```python
from .storyboard import Storyboard        # line 16 — WORK_DIR is NOT imported
...
proj = WORK_DIR / brief.slug              # line 69 — NameError
```

Confirmed: `"WORK_DIR" in dir(audio)` → `False`.

**Effect:** `render --audio` dies with `NameError: name 'WORK_DIR' is not defined` at step `[3/5]`, after the video has already rendered.

**Fix (one line):**

```python
from .storyboard import WORK_DIR, Storyboard
```

`storyboard.py:19` already exports it. Nothing else imports it.

### 11.2 `render.py:20` — `RenderError` used before it is defined

```python
_NPX = shutil.which("npx") or ...
if _NPX is None:
    raise RenderError("npx not found on PATH")   # line 20
HF = [_NPX, "--yes", "hyperframes"]

class RenderError(RuntimeError):                  # line 24
    pass
```

**Effect:** if `npx` is missing the module raises `NameError: name 'RenderError' is not defined` instead of the intended message. Move the class above the `_NPX` lookup, or raise `RuntimeError` inline.

### 11.3 `class="clip"` is never emitted

HyperFrames warns `timed_element_missing_clip_class` on every scene and caption span. The runtime hides elements outside their time range regardless, so the render is correct — but Studio and the GSAP clip-ownership linter cannot recognise them as clips. Adding `clip` to the class attribute on `.scene`, `.cap`, and `.chrome.cnt` silences all 18 notices.

### 11.4 The caption splitter breaks on `Three.js`

`build_captions` splits on every `.` and `?`. The shipped `no-webgl` scene narration

> `No WebGL. No Three.js. Just native scroll with frame interpolation.`

produces four cues, including a standalone **`js.`** held for **0.2 s** (`cap-no-webgl-2`, 18.00–18.20 s). It is burned into the MP4 and written to `captions.srt` cue 7. Guard decimals with a regex, or split only on `. ` followed by a capital letter.

### 11.5 The module docstring documents a command that does not exist

`cli.py:3-6` says `python -m video_studio build …`. There is no `video_studio/__main__.py`, so:

```
.venv\Scripts\python.exe -m video_studio
→ No module named video_studio.__main__; 'video_studio' is a package and cannot be directly executed
```

The working invocation is `python -m video_studio.cli <subcommand>`. Adding a two-line `__main__.py` makes the documented command work:

```python
from .cli import main
raise SystemExit(main())
```

### 11.6 Malformed brief JSON produces a traceback, not exit 3

`main()` catches only `(RenderError, FileNotFoundError)`. A `pydantic.ValidationError` from `Brief.model_validate` propagates and exits **1** with a stack trace, not the documented **3**. Exit 3 currently covers only banned phrases and an empty scene list.

### 11.7 `qa_report.md` prints a misleading detail string

`container_valid` passes, and its `detail` reads `"no video stream"` — the failure message, emitted unconditionally at `qa.py:90`. The check logic is right; the detail string is wrong on the success path.

---

## 12. Exit-Code Contract

| Code | Meaning | Raised by |
|---|---|---|
| **0** | Success — build written, render written, QA verdict PASS, no defects | `cmd_build`, `cmd_render`, `cmd_package`, `cmd_qa` |
| **1** | Render error — `hyperframes check` or `render` nonzero exit, zero-byte output, missing brief file, or an uncaught exception | `main()` except clause, `RenderError` |
| **2** | QA fail — `qa.py` recorded at least one defect | `cmd_render` (`rep.defects`), `cmd_qa` (`verdict != "PASS"`) |
| **3** | Brief validation fail — banned brand phrase in audience copy, or `scenes` is empty | `cmd_build`, `cmd_render` |

`cmd_package` always returns 0 unless it raises. `qa_report.json` carries `"verdict"` and `"defects"` for programmatic checks; `qa_report.md` carries the same for humans.

---

## 13. Verified Artifact Reference

`video_studio/output/signhify-prompt-to-3d-site/reel.mp4`, probed with `ffprobe -v error -print_format json -show_streams -show_format`:

| Field | Value |
|---|---|
| `width` × `height` | 1080 × 1920 |
| `display_aspect_ratio` | 9:16 |
| `codec_name` / `profile` | h264 / Constrained Baseline, level 40 |
| `pix_fmt` | yuv420p |
| `color_space` / `primaries` / `transfer` | bt709 / bt709 / bt709 |
| `r_frame_rate` / `avg_frame_rate` | 30/1 · 30/1 |
| `nb_frames` | 1215 (= 40.5 × 30, exact) |
| `duration` | 40.500000 |
| `nb_streams` | **1 — video only. No audio track.** |
| `size` | 2,213,568 bytes |
| video `bit_rate` | 436,043 bps (draft quality) |
| encoder | `Lavc62.11.100 libx264`, muxer `Lavf62.3.100` |
| container tags | `hyperframes_renderer: hyperframes`, `hyperframes_version: 0.0.0-dev` |
| wall-clock | `hyperframes check` 21.3 s · `hyperframes render` 33.3 s |

**There is no audio track.** Kokoro TTS is not installed and `--audio` was not passed. The video is silent by design of the current run, not by failure. See `06_PRODUCTION_RUNBOOK.md` §7.

---

## 14. Reading Order

| If you are | Read |
|---|---|
| Installing | `05_SETUP_AND_INSTALLATION.md` |
| Operating the pipeline | `06_PRODUCTION_RUNBOOK.md` |
| Reviewing a render | `07_VIDEO_QUALITY_CHECKLIST.md` |
| Debugging | `09_TROUBLESHOOTING.md` |
| Costing or licensing | `04_COSTS_AND_LICENSING.md` |
| Shipping to Instagram | `08_INSTAGRAM_PUBLISHING.md` |
| Changing the code | this file, §10 |
| Justifying the stack | `01_TECHNICAL_RESEARCH.md` |