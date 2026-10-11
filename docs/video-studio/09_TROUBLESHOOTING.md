# Video Studio — Troubleshooting

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/09_TROUBLESHOOTING.md` |
| **Date** | 2026-10-11 |
| **Scope** | Errors actually hit while building this pipeline, plus the traps in the code as written |
| **Companions** | `05_SETUP_AND_INSTALLATION.md`, `03_SYSTEM_ARCHITECTURE.md` §11 |

Every error below was observed on this machine. Nothing here is hypothetical.

---

## 0. Diagnostic Block

Run these before anything else. Copy-paste, Windows, from `D:\Autogram`.

```powershell
# 0.1 — interpreter and deps
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe -c "import jinja2, pydantic; print('jinja2', jinja2.__version__, '| pydantic', pydantic.VERSION)"

# 0.2 — Node / npm / npx
node --version
npm --version
(Get-Command npx).Source

# 0.3 — FFmpeg / ffprobe
ffmpeg -version | Select-Object -First 1
ffprobe -version | Select-Object -First 1

# 0.4 — HyperFrames health
npx --yes hyperframes@0.8.58 doctor

# 0.5 — the two generated trees
Get-ChildItem video_studio\work
Get-ChildItem video_studio\output
Get-ChildItem video_studio\output\<slug>\qa_frames

# 0.6 — module self-checks (all six should print OK)
.venv\Scripts\python.exe -m video_studio.brief
.venv\Scripts\python.exe -m video_studio.storyboard
.venv\Scripts\python.exe -m video_studio.publish
.venv\Scripts\python.exe -m video_studio.audio
.venv\Scripts\python.exe -m video_studio.render
.venv\Scripts\python.exe -m video_studio.qa

# 0.7 — the artifact, independent of the pipeline's own report
ffprobe -v error -print_format json -show_streams -show_format video_studio\output\<slug>\reel.mp4

# 0.8 — the last render's log
Select-String -Path video_studio\output\<slug>\render.log -Pattern '^\$ |^\[exit=|Check passed|\[audio\]'
```

**Reading the results:**

| Probe | Healthy | If not |
|---|---|---|
| 0.1 | `Python 3.14.7` + `jinja2 3.1.6 \| pydantic 2.13.5` | §2 |
| 0.2 | `v22.23.1`, `12.2.0`, an `npx.CMD` path | §2, §1 |
| 0.3 | `8.0.1-full_build-www.gyan.dev` on both | §2 |
| 0.4 | `✓ Node.js` `✓ FFmpeg` `✓ FFprobe` `✓ Chrome` | §2, §10 |
| 0.6 | six `OK` lines | the module's own `demo()` is where the fault is |
| 0.8 | two `$ ` command lines, `[exit=0]`, `Check passed` | §5, §6 |

---

## 1. `[WinError 2] npx` — the Windows spawn trap

**Symptom.** `render.py` raised on the very first render:

```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

with the command it was trying to run visible in the traceback as `['npx', '--yes', 'hyperframes', 'check']`.

**Cause.** `subprocess.run(["npx", ...])` does **not** use `PATHEXT` on Windows. `npx` is actually `npx.cmd` (and `npx.ps1`). Python's `subprocess` looks for a literal file named `npx` with no extension, does not find one, and raises. It worked fine in a terminal — the terminal resolves `npx.cmd` — and failed only from inside the venv interpreter.

**Fix — already applied**, `render.py:17-21`:

```python
# Resolve npx via PATH-independent lookup so the venv Python can spawn it on Windows.
_NPX = shutil.which("npx") or shutil.which("npx.cmd") or shutil.which("npx.ps1")
if _NPX is None:
    raise RenderError("npx not found on PATH")
HF = [_NPX, "--yes", "hyperframes"]
```

`shutil.which("npx")` **does** consult `PATHEXT`, so it resolves to `C:\Program Files\nodejs\npx.CMD` on this machine. Confirmed in `render.log`:

```
$ C:\Program Files\nodejs\npx.CMD --yes hyperframes check
$ C:\Program Files\nodejs\npx.CMD --yes hyperframes render -f 30 -q draft -o ...
```

**Still broken.** `audio.py:_kokoro` calls bare `npx`:

```python
r = subprocess.run(["npx", "--yes", "hyperframes", "tts", text, "-o", str(out)], ...)
```

Same trap, same machine. Fix it the same way — import the already-resolved handle from `render.py`:

```python
from .render import _NPX as _NPX
...
subprocess.run([_NPX, "--yes", "hyperframes", "tts", text, "-o", str(out)], ...)
```

Verify npx resolution independently:

```powershell
(Get-Command npx).Source
.venv\Scripts\python.exe -c "import shutil; print(shutil.which('npx'))"
```

---

## 2. `NameError: name 'RenderError' is not defined`

**Symptom.** With `npx` removed from `PATH`, the intended clear error was replaced by:

```
NameError: name 'RenderError' is not defined
```

**Cause.** `render.py` uses the class 4 lines before defining it:

```python
_NPX = shutil.which("npx") or shutil.which("npx.cmd") or shutil.which("npx.ps1")
if _NPX is None:
    raise RenderError("npx not found on PATH")     # line 20
HF = [_NPX, "--yes", "hyperframes"]

class RenderError(RuntimeError):                    # line 24
    pass
```

The `raise` only executes when `npx` is missing — which is exactly the situation where the class does not exist yet.

**Fix.** Move the class above the `_NPX` lookup, or raise `RuntimeError` inline. One-line reorder.

---

## 3. `NameError: name 'WORK_DIR' is not defined` — **RESOLVED**

> **Historical.** `render --audio` used to die at the mux step, after the video had rendered:
>
> ```
> [2/5] rendering 1080x1920 @30fps quality=draft ...
>       video: ...\reel.mp4
> [3/5] muxing narration (two-pass loudnorm) ...
> NameError: name 'WORK_DIR' is not defined
> ```
>
> **Cause.** `audio.py` imported only `Storyboard`, then referenced `WORK_DIR` when choosing an output path.
>
> **Resolution.** `audio.py` was rewritten. It no longer uses `WORK_DIR` at all — narration now goes to `video_studio/output/<slug>/audio/`. That move was deliberate: `write_project()` runs `shutil.rmtree()` on `work/<slug>/` on every build and every render, which would have deleted the freshly synthesized track between the synth and mux steps.

If you hit a `NameError` in `audio.py`, you are running an older checkout. Confirm with `git log -1 -- video_studio/audio.py`.

**The shipped reference Reel has an audio track.** `ffprobe` reports `nb_streams: 2` — h264 video plus AAC at 48 kHz mono, −16.1 LUFS integrated, −1.5 dBFS true peak.

### 3.1 `hyperframes tts` reports "kokoro-onnx package is not installed" — it **is** installed

**Symptom.** Either the HyperFrames CLI's TTS command or `hyperframes doctor` says Kokoro is missing, on a machine where it is installed and demonstrably working:

```
✗ TTS (Kokoro)     Not installed (optional — local voice fallback)
                   pip install kokoro-onnx soundfile
```

**Cause.** The CLI shells out to a **Python interpreter it cannot locate**. `kokoro-onnx` is installed in `D:\Autogram\.venv`, not in system Python. The probe therefore reports a missing package when the package is present. Setting `HYPERFRAMES_PYTHON` does not fix it — it fails even when that variable points at the venv interpreter.

**Confirm the install is genuinely fine before touching anything:**

```powershell
.venv\Scripts\python.exe -c "import kokoro_onnx, soundfile; print('ok')"
.venv\Scripts\python.exe -c "from video_studio.audio import kokoro_available; print(kokoro_available())"
```

If both succeed, **ignore the CLI's report.** This was re-verified on 2026-10-11: `hyperframes doctor` printed `✗ TTS (Kokoro) Not installed` on a machine where Kokoro had just produced a finished narrated Reel.

**Workaround — which is what the pipeline already does.** `video_studio/audio.py` calls the `kokoro_onnx` **library directly** and never invokes `hyperframes tts`. Nothing needs fixing, and there is no env var or `PATH` entry to add. Do not chase this by reinstalling the package; it is already correct.

`kokoro_available()` is a file-existence check on `models/kokoro/kokoro-v1.0.onnx` and `models/kokoro/voices-v1.0.bin`. `False` means the **weights** are missing — see `05_SETUP_AND_INSTALLATION.md` §3.2 — not that pip failed.

---

## 3.2. ffmpeg refuses an in-place mux

**Symptom.** `mux_audio` fails with one of:

```
Output file #0 does not contain any stream
same as Input #0 - exiting
```

**Cause.** The mux was writing the audio back onto the same `reel.mp4` it was reading. ffmpeg cannot read and write the same file in one pass — it detects the collision and exits.

**Fix — already applied** in `render.py:mux_audio`: write to a sibling temp file, then replace.

```python
tmp = dest.with_name(dest.stem + "_mux.mp4")
_run(["ffmpeg", ..., str(tmp)], REPO_ROOT, log, timeout=900)
tmp.replace(dest)
```

**If you see `reel_mux.mp4` left behind in `output/<slug>/`,** the ffmpeg process was killed mid-run. The original `reel.mp4` is untouched in that case — `tmp.replace()` never ran. Delete the temp file and re-run.

### 3.3 Why `apad` and `-shortest` are both required

Narration is usually shorter than the video. Without `apad`, the audio stream ends early and `-shortest` cuts the **video** to match — **truncating the end card**, which is the last thing a viewer sees. `apad` pads the narration with silence; `-shortest` then ends the output at the video's length.

```
-af loudnorm=...,apad -shortest
```

Symptom of getting this wrong: a Reel that plays to the right length but cuts off during the closing card, with no error and QA still reporting `PASS` — `duration_matches_plan` only compares container duration, not content. Watch the last QA frame.

---

## 4. `[StaticGuard] Invalid HyperFrame contract`

**Symptom.** The HyperFrames gate rejected a generated composition:

```
[StaticGuard] Invalid HyperFrame contract: Composition starts with a bare element
instead of a proper HTML document
```

**Cause.** Not a missing `<!doctype html>` — the template had one. The real cause was the Jinja header comment. It was written as:

```jinja
{% raw %}
{# ============================================================================
   SIGNHIFY MOTION SYSTEM ...
   ============================================================================ #}
{% endraw %}
```

`{% raw %}` tells Jinja *"do not interpret the contents."* So the `{# … #}` inside it was **emitted as literal text** rather than stripped. The rendered `index.html` began with a paragraph of comment prose, and the first thing in the file was not the document element. StaticGuard parsed it, found a bare text node before any root, and refused.

A Jinja comment inside `{% raw %}` is a comment that is never removed. The two mechanisms are mutually exclusive.

**Fix.** Use a plain Jinja comment, which Jinja strips at render time:

```jinja
{# ============================================================================
   SIGNHIFY MOTION SYSTEM - reusable vertical video composition.
   ============================================================================ #}
<!doctype html>
<html lang="en">
```

An HTML comment `<!-- … -->` also works and survives into the output, but a Jinja `{# … #}` is cleaner — it leaves no residue in the generated file.

**Verify.** After any template edit, check the first bytes of the generated file:

```powershell
Get-Content video_studio\work\<slug>\index.html -TotalCount 3
```

Expected: a blank line, then `<!doctype html>`, then `<html lang="en">`. A leading newline is fine. **Any prose before `<!doctype html>` is the bug.**

**How this was caught.** The HyperFrames gate raised on a real defect in real generated output. It is the strongest single argument for keeping `hyperframes check` as a fail-closed step rather than an advisory.

---

## 5. `ImportError: cannot import name 'build_package'`

**Symptom.**

```
ImportError: cannot import name 'build_package' from 'video_studio.publish'
```

**Cause.** A naming mismatch between modules. `cli.py` imported `build_package` from `publish.py`, but the function in `publish.py` is named `write_package`. Python resolves imports at module load, so the whole CLI failed before any subcommand ran — including `--help`.

**Fix — already applied.** `cli.py:18` now reads:

```python
from .publish import write_package, extract_cover
```

and calls `write_package(...)` at `cli.py:84` and `cli.py:134`.

**Lesson for future renames.** In a package with no `pyproject.toml` and no install step, every module is imported directly. A rename in one module breaks all callers at import time, which at least fails loudly. Grep before renaming:

```powershell
Select-String -Path video_studio\*.py -Pattern "build_package|write_package"
```

---

## 6. Render produces a 0-byte file

**Symptom.**

```
[ERROR] render produced no file: D:\Autogram\video_studio\output\<slug>\reel.mp4
```

exit **1**.

**Cause.** `hyperframes render` exited 0 but wrote nothing, or wrote to a path different from the one requested. `render.py:50-51` is the guard:

```python
if not out_path.exists() or out_path.stat().st_size == 0:
    raise RenderError(f"render produced no file: {out_path}")
```

**Diagnose in order:**

| Step | Command | Reading |
|---|---|---|
| 1 | `Select-String -Path video_studio\output\<slug>\render.log -Pattern '^\$ |^\[exit='` | Did `render` actually exit 0? |
| 2 | `Get-ChildItem video_studio\work\<slug>\reel.mp4` | HyperFrames may have written to its default location instead of `-o` |
| 3 | `Get-ChildItem video_studio\work\<slug>` | Is `index.html` present and non-zero? |
| 4 | `Get-ChildItem "$env:TEMP\hyperframes*" -Recurse -ErrorAction SilentlyContinue` | Frame cache — an empty cache means Chrome never launched |

**Most common real cause:** the **gate passed but the composition is broken**, so HyperFrames had zero frames to encode and returned success. Cross-check `render.log` — if `Check passed` is missing, the gate failed silently under `--skip-gate`.

**Second most common:** disk full. `hyperframes doctor` reports the frames cache location and its free space. 13.2 GB is enough for one render; a leaked cache from repeated runs is not.

**Never work around this.** A 0-byte file is fail-closed behaviour working correctly. Do not `--skip-gate` your way past it.

---

## 7. Fonts missing / tofu glyphs

**Symptom.** A box `□` where a character should be. Seen on this build: the eyebrow rendered **both** a tofu box **and** a duplicate asterisk.

**Cause 1 — CSS `content` collides with brief text.** The template had:

```css
.eyebrow::before { content: '\2723'; }   /* ✳ */
```

and the brief also supplied an eyebrow marker. The glyph was emitted twice, and `U+2723` is **not present in JetBrains Mono** — so the browser substituted a tofu box on top of the duplicate.

**Fix — already applied.** The `::before` pseudo-element was removed. `.eyebrow` now renders the brief's text alone, in the mono face, in `#E05A36`.

**Rule: one source per glyph.** If a marker is in the CSS, it is not in the brief. If it is in the brief, it is not in the CSS.

**Cause 2 — offline.** The template fetches Google Fonts and GSAP from CDNs:

| Host | Provides | Offline result |
|---|---|---|
| `fonts.googleapis.com` / `fonts.gstatic.com` | Plus Jakarta Sans, Inter, JetBrains Mono | falls back to `system-ui` / `monospace` — layout shifts, metrics change |
| `cdn.jsdelivr.net` | GSAP 3.14.2 | **no animation at all** — every scene stays at opacity 0 |

**Cause 3 — the glyph genuinely is not in the family.** `✳ U+2723` is not in JetBrains Mono. Verify before adding any symbol to CSS or copy.

**Diagnose:**

```powershell
Select-String -Path video_studio\work\<slug>\index.html -Pattern 'content:'
```

Any `content:` in the generated CSS is a candidate. Compare the rendered eyebrow in `qa_frames/` against the brief's `eyebrow` value.

---

## 8. Text does not animate

**Symptom.** The composition renders, but every element is at opacity 0, or nothing moves.

### 8.1 `__timelines is not defined`

```
Uncaught ReferenceError: window.__timelines is not defined
```

**Cause.** The composition assigns to `window.__timelines[<id>]` without ensuring the object exists. If HyperFrames has not pre-seeded it in your execution context, the assignment throws and **every later line in that script block never runs** — which is why the whole composition goes static, not just one animation.

**Defensive fix** — always initialise before assigning:

```js
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({paused: true});
...
window.__timelines["root"] = tl;
tl.seek(0);
```

The current template (`composition.html.jinja2:227`) writes only `window.__timelines["root"] = tl;` and **works**, because HyperFrames seeds the object in the render context. The initialiser costs one line and removes the dependency on that assumption.

### 8.2 Timeline registered under the wrong id

**Cause.** The registry key must equal the `data-composition-id` on the root element. Template root is `data-composition-id="root"`; the registration is `window.__timelines["root"]`. Mismatch means HyperFrames finds no timeline and every element renders at its CSS default.

```powershell
Select-String -Path video_studio\work\<slug>\index.html -Pattern 'data-composition-id|window\.__timelines'
```

The two strings must match exactly.

### 8.3 Timeline not paused

**Cause.** `gsap.timeline()` without `{paused: true}` starts running against the wall clock. HyperFrames seeks frames deterministically; an unpaused timeline fights the seek and motion is non-deterministic or absent.

**Rule:** `gsap.timeline({paused:true})`, always. And **the third argument to `.to` / `.fromTo` is absolute timeline seconds**, not a relative offset. Relative chaining (`"-=0.2"`) is what produces motion that does not match the composition.

### 8.4 Animating a property GSAP does not support

The documented set is `opacity`, `x`, `y`, `scale`, `scaleX`, `scaleY`, `rotation`, `width`, `height`, `visibility`.

**`transform` and `filter` are not supported.** Use `scale` / `rotation`, not raw CSS transform strings. An unsupported property is silently ignored — the element renders at its CSS default with no error anywhere.

### 8.5 Timing attribute units

`data-start` and `data-duration` are **seconds**, not frames or milliseconds. `data-duration="4000"` is 4,000 seconds. The clip is clipped to `endcard_at` by the compiler, so the symptom is an element that never appears rather than a hang.

### 8.6 z-index, not track index

`data-track-index` is **display-only**. It does not order paint and does not control overlap. Two elements that should stack must have CSS `z-index` set explicitly. Template z-map: grid `0` · scenes `10` · chrome `90` · accent bar `95` · captions `120` · end card `130`.

---

## 9. QA FAIL on audio when no narration was produced

**Symptom.**

```
- FAIL — audio_present: audio codec none
```

exit **2**.

**Cause.** `cmd_render` calls:

```python
rep = inspect(video, out / "qa_frames", expect_audio=bool(args.audio), ...)
```

So `--audio` sets the expectation. If synthesis then produces nothing — no provider, missing model weights — the file has no audio and the check fails. `expect_audio=True` plus no audio track always fails.

**The three states, and which is which:**

| State | Meaning |
|---|---|
| `audio_absent` PASS | `--audio` not passed. Correct when you deliberately rendered silent |
| `audio_present` FAIL | `--audio` was passed and no track was produced. **A real failure** — check `kokoro_available()` and the `[audio] provider=…` line in `render.log` |
| `audio_present` PASS | Narration worked |

**Fix for a standalone QA run against a deliberately silent Reel:**

```powershell
.venv\Scripts\python.exe -m video_studio.cli qa --video video_studio\output\<slug>\reel.mp4 --frames video_studio\output\<slug>\qa_frames --no-audio
```

Without `--no-audio`, `cmd_qa` defaults to `expect_audio=True`. The **shipped Reel has audio**, so it does **not** need `--no-audio` — pass that flag only for a silent artifact. Using it on a narrated Reel masks a genuine `audio_present` check.

**`cmd_render` has no `--no-audio` flag.** It infers the expectation from `--audio`. There is no way to render with `--audio` and accept a silent result — which is correct fail-closed behaviour. Fix the audio path instead; do not add a flag that lets a failed narration pass.

**Also check `render.log`:**

```
[audio] no TTS provider available; rendering without narration
```

A silent render that exits 0 is not a pass. This line is the only record that TTS was attempted and failed.

---

## 10. HyperFrames version drift

**Symptom.**

```
✗ Version          0.8.58 → 0.8.145 available
                     Run: hyperframes upgrade
```

**Why it matters.** `render.py:21` calls bare `npx --yes hyperframes`, which resolves to whatever npm has cached. An unattended upgrade on another machine changes the renderer under you.

**Pin it.** For reproducible builds, pin the version in the call:

```python
HF = [_NPX, "--yes", "hyperframes@0.8.58"]
```

Verify a pin works:

```powershell
npx --yes hyperframes@0.8.58 --version
```

Confirmed: prints `0.8.58`.

**Upgrade procedure:**

```powershell
Copy-Item video_studio\output\<slug>\reel.mp4 $env:TEMP\reel-0.8.58.mp4
npx --yes hyperframes upgrade
npx --yes hyperframes doctor
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio\briefs\<slug>.json --quality draft
ffprobe -v error -print_format json -show_streams video_studio\output\<slug>\reel.mp4
```

Compare against the saved copy. If the gate result, QA verdict, or frame appearance changes, the upgrade is not safe. Revert with `npm i hyperframes@0.8.58`.

**87 patch versions sit between the two tags.** The breaking-change surface is **UNVERIFIED**. Read the GitHub releases between the tags before upgrading in anger.

### 10.1 The gate verdict is a substring match

`render.py:42`:

```python
return {"gate": "hyperframes check", "clean": "Check passed" in out, ...}
```

If an upgrade changes that wording, `clean` flips — and it can flip to `True` on a **failing** run if the string happens to appear in an error message. **Do not treat `gate clean=True` as authoritative after a version bump.** Read `render.log` and confirm `?  Check passed` is present with the suite summaries above it.

### 10.2 Advisory notices that do not block

The reference project emits both of these on every run. Neither affects the verdict:

| Notice | Count | Meaning |
|---|---|---|
| `timed_element_missing_clip_class` | 18 | Timed elements lack `class="clip"`. Runtime hides them correctly regardless. Studio and the GSAP clip-ownership linter cannot recognise them. Adding `clip` to `.scene`, `.cap`, `.chrome.cnt` silences all 18 |
| `nested_structure_needs_subcomposition` | 7 | Scenes are top-level timeline elements containing nested divs. Studio's timeline shows one row per top-level element. Advisory ergonomics only |

Also expected, and correct: two `text_occluded` infos at t = 38.25 s for `div.chrome.tl` and `div.chrome.tc` inside `#endcard`. The end card is opaque and covers the chrome for the final 4.5 s by design.

**Healthy gate output on the reference project:**

```
Runtime
  ? 0 errors, 0 warnings
Layout
  0 error(s), 0 warning(s), 2 info(s)
Motion
  ? 0 errors, 0 warnings
Contrast
  ? 36/36 text checks pass WCAG AA
Snapshots
  ? disabled

?  Check passed
```

---

## 11. Docker mode requires a running Docker

**Symptom.**

```
✓ Docker           Docker version 29.5.2, build 79eb04c
✗ Docker running   Not running
                     Start Docker Desktop or run: sudo systemctl start docker
```

**Reality.** This is the **only non-optional `✗` besides Version**, and it is the one that does not matter.

`hyperframes render --docker` gives a deterministic Chrome and font set inside a container. `render.py:render_project` **never passes `--docker`**. Determinism from the local path is already sufficient — `03_SYSTEM_ARCHITECTURE.md` §9. The daemon being down has no effect on any command in this documentation.

Start Docker Desktop only if you have decided to use `--docker` deliberately. Do not start it to "fix" this line.

---

## 12. `python -m video_studio` — **RESOLVED**

> **Historical.** This used to fail:
>
> ```
> .venv\Scripts\python.exe: No module named video_studio.__main__; 'video_studio' is a
> package and cannot be directly executed
> ```
>
> `python -m <package>` requires a `__main__.py`; `python -m <package>.<module>` does not. `cli.py`'s docstring documented the form that could not work.
>
> **Resolution.** `video_studio/__main__.py` now exists and delegates to `cli.main`. Both forms work:

```powershell
.venv\Scripts\python.exe -m video_studio.cli build --brief video_studio/briefs\<slug>.json
.venv\Scripts\python.exe -m video_studio     # equivalent
```

Prefer the explicit `-m video_studio.cli` form — it is unambiguous and does not depend on `__main__.py` staying present.

---

## 13. Brief validation

### 13.1 Exit 3 — banned phrase

```
[FAIL] Banned brand phrases in audience copy: ['game-changer']
```

**Not a bug.** `Brief.banned_hits()` (`brief.py:80`) scans `title`, `hook`, `cta`, and per-scene `narration`, `headline`, `subtext`, `eyebrow`, `bullets` against the 16-entry `avoid` list in `data/brand.json`.

**`robust` is the trap** — ordinary engineering vocabulary that survives a casual read.

**Not scanned:** `sources`, `notes`, `pillar`, and `metrics[].v` / `metrics[].k`. Check those by eye.

### 13.2 Exit 3 — no scenes

```
[FAIL] brief has no scenes
```

### 13.3 Exit 1 with a traceback, not exit 3

**Symptom.** A malformed brief produces a `pydantic.ValidationError` stack trace and exits **1**.

**Cause.** `cli.py:159` catches only `(RenderError, FileNotFoundError)`:

```python
except (RenderError, FileNotFoundError) as e:
```

`ValidationError` propagates. Exit 3 currently covers banned phrases and an empty scene list only — not schema violations.

**Fix** — widen the catch:

```python
from pydantic import ValidationError
...
except (RenderError, FileNotFoundError, ValidationError) as e:
    print(f"[ERROR] {e}", file=sys.stderr)
    return 3
```

### 13.4 Slug rejected

```
ValueError: slug must be alphanumeric with -/_ only, got 'bad slug!'
```

The slug becomes the folder name, the `#root` composition id, and element ids. Spaces, dots, and slashes all break downstream lookups.

### 13.5 Accent rejected

```
ValueError: accent must be #RRGGBB, got 'E05A36'
```

The leading `#` is mandatory. Leave `accent` empty to inherit `data/brand.json`'s `#E05A36`.

---

## 14. Caption defects the pipeline does not catch

Neither `qa.py` nor `hyperframes check` inspects caption quality. Both of these are present in the shipped artifact.

### 14.1 Sentence splitting breaks on decimals and acronyms

`build_captions` (`storyboard.py:83`) splits on **every** `.` and `?`:

```python
parts = [p.strip() for p in narration.replace("?", "?\n").replace(".", ".\n").split("\n")]
```

Input:

> `No WebGL. No Three.js. Just native scroll with frame interpolation.`

The earlier silent render split this into four cues, including a standalone **`js.`** held for **0.2 s**. **Fixed in the shipped narrated artifact** — it is now three cues and `Three.js` stays intact. The splitter still breaks on a bare `.`, so the class of defect remains; the current brief simply does not trigger it.

**Fix, if it recurs.** Split only on a period followed by whitespace and a capital letter:

```python
import re
parts = [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z])", narration) if len(p.strip()) > 1]
```

### 14.2 Reading rate exceeds 15 chars/sec

Hold time is `min(scene_span, len(text) / 15)`. When narration does not fit its scene, the hold is truncated and the rate goes above 15 — **silently**.

**Resolved on the shipped Reel.** Per-scene synthesis retimed the cues. The old figures below are kept only to show the delta:

| Cue | chars | hold | chars/sec | now |
|---|---|---|---|---|
| `cap-mechanism-0` | 118 | 6.950 s | 16.98 | 62 chars / 4.504 s = **13.77** — under |
| `cap-no-webgl-3` | 44 | 1.200 s | **36.67** | cue no longer exists; scene is now 3 cues, longest 13.19 |
| `cap-proof-0` | 121 | 5.950 s | 20.34 | 61 chars / 4.357 s = **14.00** — under |
| `cap-price-0` | 69 | 3.950 s | 17.47 | 29 chars / 2.132 s = **13.60** — under |

**Was 4 of 11 cues over budget; now 1 of 16.** The one remaining — `cap-proof-2`, 6 characters in 0.379 s at **15.83 ch/s** — is marginal and still unflagged by any assertion.

**Fix the content, not the measurement.** Shorten the narration or lengthen the scene. Never raise `_read_speed()`.

**Optional assertion** — add to `qa.py:inspect`:

```python
fast = [c.id for c in sb.captions if len(c.text) / c.dur > 15.01]
```

### 14.3 Cue held for less than 1 second

Any cue under 1.0 s cannot be read at 30 fps, regardless of character count. `cap-no-webgl-2` holds for 0.2 s.

---

## 15. Other runtime failures

| Symptom | Cause | Fix |
|---|---|---|
| `[WinError 2] ffmpeg` | Same `PATHEXT` trap as `npx` | `ffmpeg.exe` resolves normally; if it fails, add the FFmpeg bin directory to `PATH` and open a new shell |
| `ffprobe failed on …` | `render.py:56` — `probe()` raises `RenderError` on nonzero exit | Usually a truncated or zero-byte MP4. `Get-ChildItem` the file |
| `render.py` `demo()` / `qa.py` `demo()` raise `FileNotFoundError` | Both probe `workspace/final_reel.mp4` at repo root | A missing fixture, not a broken install. The file exists on the machine of record |
| `frames_extractable` FAIL | Fewer than 3 frames extracted — usually a 0-byte or corrupt MP4 | `ffprobe` the file directly |
| `duration_matches_plan` FAIL | Rendered duration differs from `sb.total` by ≥ 1 s | Check `endcard_at` arithmetic in `storyboard.json`; a scene may be extending past `endcard_at` |
| `aspect_9_16` FAIL | `abs(w/h − 9/16) >= 0.02` | `width` / `height` in the brief are not 1080 / 1920 |
| `fps_supported` FAIL | fps is not in `{24, 25, 30, 50, 60}` | Brief `fps` outside 24–60, or a non-integer frame rate from `r_frame_rate` |
| Brief edited but the render is unchanged | You edited `work/<slug>/index.html`, which is `rmtree`'d on the next build | Edit `briefs/<slug>.json` or `templates/composition.html.jinja2` |
| `qa_report.json` timestamp older than `reel.mp4` | QA ran against a previous render | Re-run `qa`, or run `render` again |
| Manifest says `"video": null` after `package` | `cmd_package` calls `write_package(b, sb, out)` without `video=` | Expected. `package` only writes the sidecar artifacts |
| Chrome download stalls on first render | First run downloads Chrome Headless Shell (~150 MB) | Wait. Subsequent runs use the cache in `~/.cache/hyperframes/` |
| `hyperframes` picks up a different version on another machine | `render.py:21` calls bare `npx` | Pin it — §10 |

---

## 16. Escalation

**Maximum 2 repair attempts per defect. Then stop and escalate.** `06_PRODUCTION_RUNBOOK.md` §8.3.

| Repeated failure | Escalate to |
|---|---|
| Same defect after 2 attempts | Human review of the brief and the template. The fix is probably in neither |
| `hyperframes check` fails with a message not in this document | Read the HyperFrames message **verbatim**. Do not reach for `--skip-gate` |
| Renders correctly but looks wrong every time | The composition is wrong, not the render. Stop rendering; fix the template |
| QA flips between PASS and FAIL on identical input | Determinism is broken — Chrome or FFmpeg changed. Re-run `hyperframes doctor` |
| An error not listed here | Capture the **full** command, the **full** stderr, the exit code, and the relevant `render.log` block. Reproduce with `build` alone before blaming `render` |

`work/<slug>/index.html` is **generated**. Read it to debug; never edit it. It is destroyed and rewritten on every `build` and every `render`.

---

*Compiled 2026-10-11 from real failures on the machine of record, plus defects found by static reading of `cli.py`, `brief.py`, `storyboard.py`, `render.py`, `qa.py`, `publish.py`, and `audio.py`. Every error string above was observed; every fix marked "already applied" is present in the code as written. Every fix marked open is still open.*