---
description: Run the full Reel production workflow from a brief — validate, build, render, QA, report. Usage: /produce-reel <brief-slug-or-path>
agent: build
---

# Produce a Reel — end to end

Argument: `$ARGUMENTS` — a brief path (`video_studio/briefs/<slug>.json`) or a bare slug.

If `$ARGUMENTS` is empty, list `video_studio/briefs/*.json` and ask which slug to run. If the brief does not exist, hand off to the **video-content-strategist** to author it — do not invent one.

All commands run from `D:\Autogram` with the venv interpreter. The system Python lacks jinja2 and pydantic.

---

## 0. Preflight

```powershell
ffmpeg -version
ffprobe -version
node --version          # must be 22+
npx --yes hyperframes@0.8.58 doctor
```

Only `Node.js`, `FFmpeg`, `FFprobe`, and `Chrome` block a render. `✗ Docker running` is expected and irrelevant — `--docker` is never used. `✗ TTS (Kokoro)` blocks `--audio` only.

## 1. Validate + compile — `build`

```powershell
.venv\Scripts\python.exe -m video_studio.cli build --brief video_studio/briefs/<slug>.json
```

Capture the printed line verbatim: `scenes=N captions=N total=Ns endcard@Ns`.

- **Exit 3** — a `data/brand.json` `avoid` phrase in `title`/`hook`/`cta`/`narration`/`headline`/`subtext`/`eyebrow`/`bullets`, or `scenes` is empty. Reword the copy. **Never** edit `data/brand.json` to shrink the list, and never bypass the guard. Watch for `robust` and `seamless`.
- **Exit 4** — a scene is too short to speak *and* read its own narration at 15 chars/sec. Lengthen the scene or shorten the line. Never raise `_read_speed()`.

## 2. Render

```powershell
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/<slug>.json --quality draft
```

Five steps: `hyperframes check` → `hyperframes render` → narration (skipped without `--audio`) → cover + package → QA.

Exit `1` = render error. `--skip-gate` is diagnostic only — it changes no exit code and is never a fix.

`draft` is for all iteration (~33 s, visibly soft). `standard` for anything a human other than you will judge. `high` only for the final cut. Both are **UNVERIFIED** on this machine — re-measure before quoting a timing.

## 3. QA

```powershell
.venv\Scripts\python.exe -m video_studio.cli qa --video video_studio/output/<slug>/reel.mp4 --frames video_studio/output/<slug>/qa_frames --no-audio
```

Exit `0` = PASS, `2` = FAIL. Independent verification:

```powershell
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,nb_frames -of default=noprint_wrappers=1 video_studio\output\<slug>\reel.mp4
```

Expect `width=1080 height=1920 r_frame_rate=30/1 codec_name=h264`, duration 3–90 s.

## 4. Inspect — **the step that finds real defects**

**Open every JPEG in `video_studio/output/<slug>/qa_frames/`.** `qa.py` extracts frames; it never looks at them.

- eyebrow renders clean text — no tofu glyph, no duplicate marker
- scene counter reads the **active** scene, not a static total
- headline ≤ 3 lines · cards fit at 1080 wide · caption chip clear of bottom chrome
- last frame is the fully opaque end card
- `captions.srt`: ≤ 15 chars/sec, no broken splits (`Three.js` → `No Three.` + `js.` is a shipped bug)

Also read `output/<slug>/render.log`. `[audio] no TTS provider available` means a `--audio` render that **exited 0 and shipped silent**.

## 5. Report

```
SLUG · <slug>
BRIEF      scenes=N captions=N total=Ns endcard@Ns   (build exit 0)
GATE       clean=True|False                            (hyperframes check)
QA         PASS|FAIL  <W>x<H> @<fps>  <dur>s  <codec>/<audio>
FRAMES     <N> extracted in output/<slug>/qa_frames/ — inspected: yes|no
CAPTIONS   max <N> ch/s over <N> cues
REPORT     render.log: <one line>
EXIT       <code>
```

Then work `docs/video-studio/07_VIDEO_QUALITY_CHECKLIST.md` top to bottom.

> **A passing automated gate is not a production verdict.** If you did not open the JPEGs, say `inspected: no` and do not call it shippable.

---

## Exit codes

| Code | Meaning | Do next |
|---|---|---|
| `0` | Pass — QA PASS, no defects | Final cut at `--quality standard`, re-inspect |
| `1` | Render error / uncaught exception | `09_TROUBLESHOOTING.md` |
| `2` | QA fail — defect in `qa_report.md` | Fix, re-render. **Max 2 attempts per defect, then escalate** |
| `3` | Brief invalid — banned phrase or no scenes | Reword copy in the brief |
| `4` | Narration overrun | Lengthen the scene or shorten the line |

Never loop render-and-repair. Two attempts is a real budget.

---

## Dry run — no render

Full validation and compilation, zero render cost. Use it to check copy, avoid-list hits, narration fit, and caption timing before spending ~33 s per render.

```powershell
# validate the brief + compile the storyboard + write the project
.venv\Scripts\python.exe -m video_studio.cli build --brief video_studio/briefs/<slug>.json

# inspect the compiled caption timing without rendering
Get-Content video_studio\work\<slug>\index.html | Select-String 'data-scene|data-composition-id|__timelines'
```

`build` is the dry run: it runs the identical `_validate()` gate `render` runs, including the banned-phrase and narration-overrun checks, and it writes `work/<slug>/` without touching `output/<slug>/`.

To rehearse the caption split without rendering, build once and read `work/<slug>/` — never hand-edit the generated `index.html`; it is destroyed on the next build or render.

**Dry run does not prove the render will pass.** The gate, `ffprobe` assertions, and the visual defects found on the reference build all require a real render. Say so in your report.

---

## Shipping

Re-render the final cut, re-run `qa`, re-inspect the frames, then hand off the package. **Do not publish.** `publish.py` produces files and never sends them; there is no `--publish` flag, and `asset_manifest.json` hardcodes `publishing.enabled: false`. Uploading to Instagram is the owner's manual decision.

Package-only refresh (no render):

```powershell
.venv\Scripts\python.exe -m video_studio.cli package --brief video_studio/briefs/<slug>.json
```