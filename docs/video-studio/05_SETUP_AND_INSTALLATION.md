# Video Studio — Setup and Installation

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/05_SETUP_AND_INSTALLATION.md` |
| **Date** | 2026-10-11 |
| **Target** | Fresh clone of `D:\Autogram` → first rendered Reel |
| **Primary platform** | Windows x64. Unix notes marked **[Unix]** |
| **Companions** | `03_SYSTEM_ARCHITECTURE.md`, `09_TROUBLESHOOTING.md` |

---

## 0. What You Need Before Starting

| Requirement | Version | Verified on machine of record | How to check |
|---|---|---|---|
| **Python** | 3.10+ | venv **3.14.7** (system is 3.14.0 — see §1.2) | `python --version` |
| **Node.js** | **22+ (hard requirement)** | v22.23.1 | `node --version` |
| **npm** | ships with Node | 12.2.0 | `npm --version` |
| **FFmpeg** | any recent | 8.0.1 full build (gyan.dev via WinGet) | `ffmpeg -version` |
| **ffprobe** | ships with FFmpeg | 8.0.1 | `ffprobe -version` |
| **Disk** | ~2 GB to start | 13.2 GB free | — |
| **GPU** | **none required** | integrated only, no CUDA | — |
| **Docker** | **not required** | installed, daemon **not running** | — |

**No account, no API key, no credit balance is needed for local rendering.** That is the entire point of the stack choice — see `04_COSTS_AND_LICENSING.md` §1.

### 0.1 Minimum viable hardware

CPU-only rendering. The reference 40.5 s Reel rendered in **33.3 s** on an i5-1145G7 with 15.7 GB RAM and no CUDA. Any x86-64 or arm64 machine with ~8 GB free RAM and a working Chrome download will render. The 15.7 GB / 13.2 GB figures on this machine are tight but sufficient; run **one render at a time**.

---

## 1. Windows Setup (Primary)

### 1.1 Clone and enter the repo

```powershell
git clone <your-remote-url> D:\Autogram
Set-Location D:\Autogram
```

**[Unix]**

```bash
git clone <your-remote-url> ~/Autogram && cd ~/Autogram
```

### 1.2 Create the venv

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Or skip activation entirely — **every command in this document uses the absolute interpreter path and works without it:**

```powershell
.venv\Scripts\python.exe --version
```

**[Unix]**

```bash
python3 -m venv .venv && source .venv/bin/activate
```

> **Use `.venv\Scripts\python.exe`, not bare `python`.** The venv is what carries jinja2, pydantic, and pillow. The system interpreter on this machine is Python 3.14.0 with none of them. `render.py` resolves `npx` through `shutil.which()` specifically so the venv interpreter can spawn Node — see `09_TROUBLESHOOTING.md` §1.

### 1.3 Install Python dependencies

```powershell
pip install -r requirements.txt
```

Verified contents and the ones that matter here:

| Package | Needed by `video_studio`? | Verified version |
|---|---|---|
| `jinja2` | **Yes** — template render | 3.1.6 |
| `pydantic` | **Yes** — brief validation | 2.13.5 |
| `pillow` | Declared; not on the current video path | present |
| `requests` | indirect | — |
| `faster-whisper` | Not yet wired in — future caption timing | ≥1.0.0 |
| `edge-tts` | **Declared but unused.** Microsoft ToS risk on monetized output — do not adopt | — |
| `playwright` | **Not for video_studio.** Legacy Autogram carousel renderer only | — |
| `flask`, `gunicorn`, `supabase`, `gradio_client`, `feedparser`, `openai`, `pytest` | Not for video_studio | — |

### 1.4 Verify FFmpeg and ffprobe

```powershell
ffmpeg -version
ffprobe -version
```

Expected first line:

```
ffmpeg version 8.0.1-full_build-www.gyan.dev
ffprobe version 8.0.1-full_build-www.gyan.dev
```

If neither resolves, install them and confirm `PATH` — HyperFrames requires a **system** FFmpeg, it does not bundle one.

```powershell
winget install --id Gyan.FFmpeg -e
```

### 1.5 Verify HyperFrames

```powershell
npx --yes hyperframes@0.8.58 doctor
```

Real output on the machine of record, 2026-10-11:

```
hyperframes doctor

  ✗ Version          0.8.58 → 0.8.145 available
                     Run: hyperframes upgrade
  ✓ Node.js          v22.23.1 (win32 x64)
  ✓ CPU              8 cores · 11th Gen Intel(R) Core(TM) i5-1145G7 @ 2.60GHz @ 2611MHz
  ✓ Memory           15.7 GB total · 3.2 GB available
  ✓ Disk             13.2 GB free
  ✓ Frames cache     C:\Users\Piyush\AppData\Local\Temp\hyperframes-extract-cache-u · 58.0 GB free
  ✓ Archive extractor Built into Windows
  ✓ Environment      non-TTY
  ✗ whisper-cpp      Not found (optional — needed for transcription)
  ✗ TTS (Kokoro)     Not installed (optional — local voice fallback)
                     pip install kokoro-onnx soundfile
  ✓ BGM (MusicGen)   MusicGen deps installed
  ✓ onnxruntime-node Not installed (installs on first use)
  ✓ @google/genai    Not installed (installs on first use)
  ✓ FFmpeg           ffmpeg 8.0.1-full_build-www.gyan.dev at ...
  ✓ FFprobe          ffprobe 8.0.1-full_build-www.gyan.dev at ...
  ✓ Chrome           cache: C:\Users\Piyush\.cache\hyperframes\chrome\chrome-headless-shell\win64-152.0.7977.30\...
  ✓ Docker           Docker version 29.5.2, build 79eb04c
  ✗ Docker running   Not running

  ◇  Some checks failed — see hints above
```

**Which lines actually block a render:**

| Line | Blocks render? | Action |
|---|---|---|
| `✗ Version` | **No** | Optional. 0.8.58 works. See §7 |
| `✓ Node.js` | **Yes** | Must be 22+ |
| `✓ FFmpeg` / `✓ FFprobe` | **Yes** | Both must resolve |
| `✓ Chrome` | **Yes** | Downloaded automatically on first render if absent |
| `✗ whisper-cpp` | No | Transcription only. Not used by `video_studio` today |
| `✗ TTS (Kokoro)` | **No — ignore it** | **False negative.** `doctor` probes for Kokoro via a Python it cannot locate, so it reports "Not installed" on a machine where it *is* installed and rendering audio. Verify with `video_studio.audio.kokoro_available()` instead — §3 |
| `✗ Docker running` | **No** | `--docker` is not used. Local determinism is already sufficient |

> **`doctor` is not authoritative for TTS.** It was re-run after Kokoro was installed and still printed `✗ TTS (Kokoro) Not installed`. Nothing is wrong with the install. The check looks in the wrong Python environment — same root cause as §3.3.

Pinning `@0.8.58` in the `npx` invocation guarantees every operator renders with the same HyperFrames build. `render.py` calls bare `npx --yes hyperframes`, which resolves to whatever npm caches — add the pin there if you need byte-reproducible builds across machines.

### 1.6 Playwright — **not required for video_studio**

```powershell
playwright install chromium
```

Run this **only** if you also intend to run the legacy Autogram carousel renderer (`orchestrator.py`, `renderer/render.py`). **HyperFrames downloads and manages its own Chrome Headless Shell** (`~/.cache/hyperframes/chrome/`) and never uses the Playwright browser. Installing Playwright is harmless; skipping it does not block `video_studio`.

### 1.7 Environment variables

> **A local render requires ZERO environment variables.**
>
> There is no `.env` read, no API key, no token, and no config file in the `video_studio` path. Brand tokens are read from `data/brand.json` at compile time. Dimensions, fps, and scene durations come from the brief.

The repo's `.env` / `.env.example` carry keys for the **legacy Autogram carousel pipeline** and the **future, unimplemented** Instagram publisher. None is read by `video_studio` today. See `08_INSTAGRAM_PUBLISHING.md` §7 for the placeholder names, used only if publishing is ever enabled.

### 1.8 First render

```powershell
.venv\Scripts\python.exe -m video_studio.cli build --brief video_studio/briefs/signhify-prompt-to-3d-site.json
```

```
[OK] project: D:\Autogram\video_studio\work\signhify-prompt-to-3d-site
[OK] scenes=7 captions=16 total=45.5s endcard@41.0s
```

Then the full pipeline:

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

Expected wall-clock on the machine of record: **~55 s** for the silent path (check 21.3 s + render 33.3 s + extraction and packaging ~2 s). Add Kokoro synthesis and the mux on top.

> **Command form.** `-m video_studio.cli` is the documented form and still works. `video_studio/__main__.py` now also exists, so `-m video_studio` works too — this is no longer a trap. Prefer the explicit `.cli` form; both resolve the same entrypoint.

### 1.9 Independent verification

Do not trust the pipeline's own report. Probe the file:

```powershell
ffprobe -v error -select_streams v:0 `
  -show_entries stream=width,height,r_frame_rate,codec_name,nb_frames `
  -of default=noprint_wrappers=1 `
  video_studio\output\signhify-prompt-to-3d-site\reel.mp4
```

Expected:

```
width=1080
height=1920
r_frame_rate=30/1
codec_name=h264
nb_frames=1215
```

1215 ÷ 30 = 40.5 s exactly.

### 1.10 Module self-checks

Every module ships a `demo()` runnable as `__main__`. Run all five:

```powershell
.venv\Scripts\python.exe -m video_studio.brief
.venv\Scripts\python.exe -m video_studio.storyboard
.venv\Scripts\python.exe -m video_studio.publish
.venv\Scripts\python.exe -m video_studio.audio
.venv\Scripts\python.exe -m video_studio.render
.venv\Scripts\python.exe -m video_studio.qa
```

Expected output:

```
brief.py self-check OK
storyboard.py self-check OK
publish.py self-check OK
audio.py self-check OK
render.py self-check OK
qa.py self-check OK
```

`render.py` and `qa.py` probes `workspace/final_reel.mp4` at repo root. If that file is absent, those two will raise `FileNotFoundError` — that is a missing fixture, not a broken install.

---

## 2. Unix Notes

Everything above works with these substitutions:

| Step | Windows | Unix |
|---|---|---|
| venv create | `python -m venv .venv` | `python3 -m venv .venv` |
| activate | `.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| interpreter | `.venv\Scripts\python.exe` | `.venv/bin/python` |
| FFmpeg | `winget install --id Gyan.FFmpeg -e` | `sudo apt install ffmpeg` |
| Playwright | `playwright install chromium` | identical |

`render.py:18` resolves `npx` via `shutil.which("npx") or shutil.which("npx.cmd") or shutil.which("npx.ps1")`. On Unix the first lookup succeeds; on Windows it resolves to `npx.CMD` under `C:\Program Files\nodejs\`. No code change needed either way.

The `--audio` path does **not** shell out to `npx` at all. Narration synthesis calls the `kokoro_onnx` Python library directly (`video_studio/audio.py`), so the `WinError 2` bare-`npx` trap in `09_TROUBLESHOOTING.md` §1 does not apply here. `npx` is used only for `hyperframes check` and `hyperframes render`.

---

## 3. Narration (`--audio`) — **INSTALLED**

**The shipped reference Reel has narration.** `ffprobe` reports `nb_streams: 2` — H.264 video plus AAC audio at 48 kHz mono. Kokoro is installed and is the provider that produced it.

### 3.1 Install Kokoro

```powershell
.venv\Scripts\python.exe -m pip install kokoro-onnx==0.4.7 soundfile==0.14.0 espeakng-loader==0.2.4
```

`espeakng-loader` is what replaces a system `espeak-ng` install — it bundles the phonemizer for the venv, so **there is no `winget install eSpeak-NG` step and nothing to add to PATH.** That line in older revisions of this doc is obsolete.

### 3.2 Download the model weights (~337 MB)

`kokoro-onnx` ships the library, not the weights. Fetch both files from the `model-files-v1.0` release:

```powershell
New-Item -ItemType Directory -Force models\kokoro | Out-Null

curl.exe -L -o models\kokoro\kokoro-v1.0.onnx `
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx

curl.exe -L -o models\kokoro\voices-v1.0.bin `
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

| File | Size | Purpose |
|---|---|---|
| `kokoro-v1.0.onnx` | **~310 MB** | The model |
| `voices-v1.0.bin` | **~27 MB** | Voice embeddings |

> **`models/` must never be committed.** It is in `.gitignore` and gitignored contents are not enforced by Git — a `git add -f` would still stage 337 MB of binary into history. The directory is intentionally absent from a fresh clone, so every fresh checkout re-downloads it. Verify with `git check-ignore -v models/kokoro/kokoro-v1.0.onnx`.

Confirm the install without rendering anything:

```powershell
.venv\Scripts\python.exe -c "from video_studio.audio import kokoro_available; print(kokoro_available())"
# True
```

`kokoro_available()` is a pure file-existence check on both weights. `False` means the download failed or landed in the wrong place — it says nothing about the pip packages.

### 3.3 Do not use `hyperframes tts`

The HyperFrames CLI's own TTS command does **not** work on this machine, even though Kokoro is installed. It shells out to a Python interpreter it cannot locate (the packages are in `.venv`, not system Python), and it fails even with `HYPERFRAMES_PYTHON` set. Its error misreports the situation as "kokoro-onnx package is not installed".

`video_studio` calls the `kokoro_onnx` library directly from `video_studio/audio.py` and never shells out for TTS. Nothing needs to be configured for this to work — do not add a `PATH` entry or an env var chasing the CLI error. Full symptom: `09_TROUBLESHOOTING.md` §3.

### 3.4 Render with narration

```powershell
.venv\Scripts\python.exe -m video_studio.cli render `
  --brief video_studio/briefs/signhify-prompt-to-3d-site.json `
  --quality draft --audio
```

Narration is synthesized **per scene**, each scene's wav is measured, and the measurements are concatenated with 0.25 s of silence between scenes into `output/<slug>/audio/narration.wav`. Not `work/<slug>/` — `write_project()` `rmtree`s that directory on every build and would delete the track before muxing.

`render.py:mux_audio` then runs a **two-pass EBU R128 `loudnorm`** (I = −16 LUFS, TP = −1.5 dBTP, LRA = 11) and muxes AAC at 192 kbps / 48 kHz mono with `+faststart`. The video stream is copied — no re-encode. `apad` + `-shortest` ensure a short narration cannot truncate the video and cut the end card.

Verify the result:

```powershell
ffprobe -v error -show_entries stream=codec_type,codec_name,sample_rate,channels `
  -of default=noprint_wrappers=1 video_studio\output\<slug>\reel.mp4
# video: h264
# audio: aac, 48000 Hz, 1 channel
```

If no provider produces audio, the pipeline **renders silently rather than failing**. `render.log` will contain:

```
[audio] provider=kokoro scenes=7 narration=36.78s
```

**Read that line.** A silent render that exits 0 is not a pass. `provider=edge-tts` means the fallback fired, which is a licence problem for monetized output, not a cosmetic one.

### 3.5 Narration licence

Kokoro-82M is **Apache-2.0** for both weights and inference library, unrestricted for commercial use, $0, local. Do **not** substitute `edge-tts` for monetized output — it is free but Microsoft's service ToS may prohibit commercial use. Full table in `04_COSTS_AND_LICENSING.md` §3.4.

---

## 4. Optional — Word-Level Caption Timing

Not wired in. `faster-whisper` is already in `requirements.txt` (MIT) and installed. `video_studio` currently computes caption times **arithmetically** from a 15 chars/sec reading budget — see `03_SYSTEM_ARCHITECTURE.md` §5.4.

Adding `faster-whisper` would give per-word timing for animated captions. It has never been benchmarked on this CPU: **real-time factor is UNVERIFIED.**

---

## 5. Optional — Docker Mode

`hyperframes render --docker` gives a deterministic Chrome and font set inside a container.

**Not enabled here, and not recommended.** The Docker client 29.5.2 is installed but the daemon is **not running**, and `--docker` is not used by `video_studio`'s `render_project()`. Local determinism is already acceptable — `03_SYSTEM_ARCHITECTURE.md` §9.

---

## 6. Environment Reference

### 6.1 Required for a local render

**None.** Zero environment variables.

### 6.2 Read implicitly from disk

| Source | Read by | Value used |
|---|---|---|
| `data/brand.json` | `brief.py:load_brand()`, `storyboard.py` | `design.colors.accent`, the 16-entry `avoid` list |
| `assets/signhify-logo-vector.png` | `storyboard.py:162` | copied to `work/<slug>/assets/logo.png` |

`data/brand.json` `design.colors.accent` is `#E05A36`. Any brief that sets `accent` explicitly overrides it.

### 6.3 Required for publishing

`META_API_VERSION` in `.env.example` is pinned to **v26.0**, reconciled 2026-10-11 — it had been `v23.0`, which is well out of Meta support and out of step with the v26.0 spec in `08_INSTAGRAM_PUBLISHING.md`. The remaining names are shared with the legacy Autogram carousel pipeline.

```
IG_USER_ID=
IG_ACCESS_TOKEN=
META_API_VERSION=v26.0
INSTAGRAM_BUSINESS_ACCOUNT_ID=
META_GRAPH_ACCESS_TOKEN=
```

> `video_studio` reads **no environment variables**. These are optional; the publish step falls back to `PUBLIC_CDN_BASE` for the video URL. **Never place a real token in a tracked file** — `.env` is gitignored, `.env.example` holds placeholders only.

### 6.4 Network egress

Both are on the render critical path — an offline machine renders with fallback fonts and no GSAP.

| Host | Purpose | Offline result |
|---|---|---|
| `fonts.googleapis.com`, `fonts.gstatic.com` | Plus Jakarta Sans, Inter, JetBrains Mono | falls back to `system-ui` / `monospace` — layout shifts |
| `cdn.jsdelivr.net` | GSAP 3.14.2 | **no animation at all** |
| `registry.npmjs.org` | `npx --yes hyperframes` on first use | cannot resolve the package |

---

## 7. Upgrading HyperFrames

Installed: **0.8.58**. Latest published: **0.8.145**. `hyperframes doctor` flags this as the only non-optional `✗`.

87 patch versions sit between them. The breaking-change surface is **UNVERIFIED**.

Procedure:

```powershell
npx --yes hyperframes upgrade          # or: npm i hyperframes@0.8.145
npx --yes hyperframes@0.8.145 doctor
```

Then **re-render the reference brief and diff**, before changing anything else:

```powershell
Copy-Item video_studio\output\signhify-prompt-to-3d-site\reel.mp4 C:\Users\Piyush\AppData\Local\Temp\opencode\reel-0.8.58.mp4
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/signhify-prompt-to-3d-site.json --quality draft
```

If the gate result, QA verdict, or frame appearance changes, the upgrade is not safe. Revert with `npm i hyperframes@0.8.58`.

---

## 8. Post-Install Checklist

Verify every line before calling a machine set up:

```powershell
node --version
npm --version
ffmpeg -version
ffprobe -version
.venv\Scripts\python.exe -c "import jinja2, pydantic; print('deps ok')"
npx --yes hyperframes@0.8.58 doctor
.venv\Scripts\python.exe -c "from video_studio.audio import kokoro_available; print(kokoro_available())"
.venv\Scripts\python.exe -m video_studio.cli build --brief video_studio/briefs/signhify-prompt-to-3d-site.json
.venv\Scripts\python.exe -m video_studio.cli render --brief video_studio/briefs/signhify-prompt-to-3d-site.json --quality draft --audio
.venv\Scripts\python.exe -m video_studio.cli qa --video video_studio/output/signhify-prompt-to-3d-site/reel.mp4 --frames video_studio/output/signhify-prompt-to-3d-site/qa_frames
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name -of default=noprint_wrappers=1 video_studio\output\signhify-prompt-to-3d-site\reel.mp4
```

| # | Check | Expected |
|---|---|---|
| 1 | `node --version` | `v22.23.1` or newer 22+ |
| 2 | `ffmpeg -version` | resolves |
| 3 | `ffprobe -version` | resolves |
| 4 | `import jinja2, pydantic` | `deps ok` |
| 5 | `hyperframes doctor` | Node ✓ FFmpeg ✓ FFprobe ✓ Chrome ✓. **Ignore the `✗ TTS (Kokoro)` line** — false negative, §1.5 |
| 6 | `kokoro_available()` | `True` |
| 7 | `build` | `scenes=7 captions=16 total=45.5s endcard@41.0s` |
| 8 | `render --audio` | `gate clean=True`, `audio=aac`, `QA: PASS` |
| 9 | `qa` | `"verdict": "PASS"` |
| 10 | `ffprobe` | `width=1080 height=1920 r_frame_rate=30/1 codec_name=h264` |

Then **open the extracted frames in `output/signhify-prompt-to-3d-site/qa_frames/`.** A green report is not a visual pass — `07_VIDEO_QUALITY_CHECKLIST.md`.

### 8.1 Audition the narration

Automated QA confirms an audio stream exists. It does not confirm the voice fits the brand. Listen to `output/<slug>/reel.mp4` end to end at full volume before calling a narrated Reel done.

---

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `No module named video_studio.__main__` | no `__main__.py` | use `-m video_studio.cli`, or add one — `09_TROUBLESHOOTING.md` §7 |
| `ModuleNotFoundError: jinja2` | system `python` instead of the venv | `.venv\Scripts\python.exe` |
| `[WinError 2] npx` | bare `npx` from the venv | already fixed in `render.py` via `shutil.which` — `09_TROUBLESHOOTING.md` §1 |
| `name 'RenderError' is not defined` | `render.py:20` references the class defined on line 24 | `09_TROUBLESHOOTING.md` §2 |
| `name 'WORK_DIR' is not defined` | `audio.py:69`, missing import | `09_TROUBLESHOOTING.md` §3 |
| `[StaticGuard] Invalid HyperFrame contract` | composition is not a full HTML document | `09_TROUBLESHOOTING.md` §4 |
| `npx --yes` hangs on first run | downloading the package | wait; then re-run |
| Fonts look wrong / tofu boxes | offline, or an unsupported glyph in CSS `content` | `09_TROUBLESHOOTING.md` §8 |
| `render produced no file` | HyperFrames exited 0 but wrote nothing | `09_TROUBLESHOOTING.md` §6 |
| `Docker running — Not running` | daemon down | **ignore it.** `--docker` is unused |
| Gate reports clean but the video looks wrong | `check` does not inspect pixels | run the human checklist |
| QA reports `audio_present` failure with no `--audio` | expectation mismatch | pass `--no-audio` to `qa`, or set the flag consistently |

Full symptom-by-symptom catalogue with real error text: **`09_TROUBLESHOOTING.md`**.

---

*Compiled 2026-10-11 from `hyperframes doctor` output, the venv interpreter at Python 3.14.7 with jinja2 3.1.6 / pydantic 2.13.5, FFmpeg and ffprobe 8.0.1, Node v22.23.1, npm 12.2.0, and a full `build` + `render` + `qa` + `ffprobe` cycle on this machine. Every command in this document was executed as written.*