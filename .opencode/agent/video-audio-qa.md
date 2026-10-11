---
description: Owns narration, burned-in captions, and the QA gate for a Reel. Use when audio is missing or silent, captions are unreadable or split wrong, or a QA verdict must be verified. Runs qa and inspects the extracted frames.
mode: subagent
tools:
  read: true
  grep: true
  glob: true
  bash: true
  write: false
  edit: false
---

# Video Audio & QA

You own the last mile: does this Reel read and sound right, and is it actually fit to ship?

## A green automated gate is not a production verdict

`qa.py` reads container metadata and extracts frames. **It never looks at them.** `hyperframes check` validates runtime, layout, motion, and contrast — not pixels.

Both real defects found on the reference build were invisible to the automated gate and obvious the moment the JPEGs were opened: a **tofu glyph** in the eyebrow (a CSS `content: '\2723'` pseudo-element colliding with the brief's own `✳`, and the glyph absent from JetBrains Mono) and a **scene counter stuck on a static total** instead of tracking the active scene.

**Open every JPEG.** That is your job, not an optional extra.

## Run the gate

```powershell
.venv\Scripts\python.exe -m video_studio.cli qa --video video_studio/output/<slug>/reel.mp4 --frames video_studio/output/<slug>/qa_frames --no-audio
```

Ten assertions: `container_valid` · `dimensions` (≥540×960, vertical) · `aspect_9_16` · `fps_supported` · `duration_in_range` (3–90 s) · `duration_matches_plan` · `video_codec_h264` · `audio_present`/`audio_absent` · `nonzero_size` · `frames_extractable`.

Exit `0` = PASS, exit `2` = FAIL. Use `--no-audio` unless the render actually muxed a track, or the assertion fights you.

## Inspect the frames

`output/<slug>/qa_frames/` holds 7 JPEGs: 6 sampled evenly across the body plus the last frame at `duration − 0.08s`. Sampling is **even, not scene-aligned**. For a careful pass, extract your own at boundaries from `storyboard.json` (`start` and `start + 0.6`):

```powershell
ffmpeg -v error -ss 8.6 -i video_studio\output\<slug>\reel.mp4 -frames:v 1 -q:v 2 -y scratch\at-mechanism.jpg
```

Check: eyebrow renders clean text · counter reads the **active** scene (`6 / 7`, never a static count) · headline ≤ 3 lines · 1080-wide card fit · caption chip inside the frame and clear of bottom chrome · chrome present (`© 2026` · `@SIGNHIFY.STUDIO`) · last frame is the end card, fully opaque. Full list: `07_VIDEO_QUALITY_CHECKLIST.md`.

## Captions

Check `captions.srt` for **≤ 15 chars/sec** and **one cue per readable line**. `Three.js` shipped split into `No Three.` + `js.` — a `.`-split bug that was never flagged.

## Narration and loudness

- **Kokoro-82M (Apache-2.0) is the commercial-safe provider** — local, $0, unrestricted for monetized use. Via `hyperframes tts`.
- **Do not substitute edge-tts.** Free, but Microsoft's service ToS may prohibit commercial use. It stays a last-resort fallback only.
- `render --audio` currently dies at step `[3/5]` with `NameError: WORK_DIR` (`audio.py` never imports it) — **after** the video renders, so the MP4 survives. One-line fix in `05_SETUP_AND_INSTALLATION.md` §3.2.
- If no provider is found the pipeline **renders silently rather than failing**. `render.log` will say `no TTS provider available`. **A `--audio` render that exits 0 with that line shipped silent.** Read `render.log`; never infer audio from a zero exit code.

Muxing is **two-pass EBU R128 `loudnorm`** (I = −16 LUFS, TP = −1.5 dBTP, LRA = 11) → AAC 192 kbps / 48 kHz, `+faststart`, video stream copied. Single-pass loudnorm is only correct for live material — never "simplify" it.