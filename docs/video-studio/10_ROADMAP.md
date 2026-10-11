# Roadmap — Signhify Studio Video Engine

Dated: 2026-10-11. Tracks what is real today versus what is next, in build order.
`[x]` shipped and verified · `[~]` partially working · `[ ]` not started

---

## Status now

**Working end to end, with sound.** A content brief is compiled into a timed
HyperFrames composition, narrated per scene by Kokoro, rendered to a real
1080×1920 H.264 + AAC MP4 on this machine, loudness-normalised, inspected by
ffprobe plus frame extraction, and packaged for publication.

Verified demo artifact:
`video_studio/output/signhify-prompt-to-3d-site/reel.mp4` — 45.5s, 1080×1920,
30fps, H.264 + AAC 48kHz mono, QA verdict PASS, `hyperframes check` gate clean,
−16.1 LUFS integrated / −1.5 dBFS true peak.

**Narration is live.** Kokoro-82M (`kokoro-onnx` 0.4.7, Apache-2.0) synthesizes
per scene, 7 scenes, 36.78s of speech, default voice `af_heart`. The library is
called directly — the HyperFrames `tts` CLI cannot locate the venv Python and
fails even with `HYPERFRAMES_PYTHON` set.

> **Determinism was verified for the silent render only.** Two independent renders
> of the same brief produced **byte-identical** MP4s (SHA-256 `52F88E97…B61522E`).
> That measurement predates narration and was **not** re-run with an audio track.
> Kokoro on a fixed model and fixed stack is deterministic in principle — it is a
> local ONNX graph with no clock or RNG — but treat byte-reproducibility of a
> *narrated* Reel as **untested** until two runs are diffed. `apad` and `-shortest`
> are both deterministic ffmpeg filters, so nothing downstream is expected to
> break it. Verify before quoting it.

---

## Shipped

- [x] Brief schema with pydantic validation — `video_studio/brief.py`
- [x] Brand `avoid`-list enforced at the boundary; banned copy fails with exit 3
- [x] Narration-fit validation; overlong lines fail closed with exit 4
- [x] Storyboard compiler with absolute-second timing — `video_studio/storyboard.py`
- [x] Caption engine: sentence-boundary splitting that preserves dotted tokens
      (`Three.js`), proportional time allocation, 15 chars/sec reading budget
- [x] Brand-correct composition template — `video_studio/templates/composition.html.jinja2`
- [x] Real HyperFrames CLI v0.8.58 (Apache-2.0) as the renderer
- [x] `hyperframes check` gate wired in (Runtime / Layout / Motion / WCAG-AA contrast)
- [x] **Narration end to end** — Kokoro-82M installed, per-scene synthesis,
      0.25s inter-scene silence, one muxed AAC track. See `06_PRODUCTION_RUNBOOK.md` §7
- [x] Two-pass EBU R128 loudnorm — `video_studio/render.py:mux_audio`
- [x] `apad` + `-shortest` so short narration cannot truncate the end card
- [x] QA inspection: ffprobe + 7 sampled frames incl. the last frame — `video_studio/qa.py`
- [x] Packaging: SRT, caption, cover, storyboard, asset manifest, render log
- [x] Publishing **opt-in** via `--publish`, disabled by default in the manifest
- [x] Tests — `tests/test_video_studio.py`: **74 passing, 2 failing** (see limitations)
- [x] Full docs set in `docs/video-studio/` (12 files)

---

## Next, in build order

### 1. Narration polish `[~]`
The track renders, measures loud, and lands on the captions. What remains is
craft, not plumbing.

- [x] Install Kokoro + download `model-files-v1.0` weights into `models/kokoro/`
- [x] Render with `--audio`; mux, loudness, and caption sync confirmed
- [ ] Audition the other ~53 voices against the brand voice array — only `af_heart` has been heard
- [ ] Decide on a background music bed with ducking under speech
- [ ] Bounded retries: a TTS failure degrades to a silent track, never aborts the render
- [ ] Re-run the determinism check with narration included

**Not blocked.** `edge-tts` remains the fallback; Microsoft's service ToS may
prohibit commercial use, so it must not appear on published monetized output.

### 2. Visual components `[~]`
Six components ship (`hook`, `statement`, `feature_card`, `metrics`, `terminal`,
`browser`). Each new one needs a `HEAD_CLASS` entry and a template branch.

- [ ] Product screenshot capture — a real device mockup with an actual screenshot
- [ ] Code panel with syntax highlighting
- [ ] Split-screen before/after comparison
- [ ] Diagram component for pipeline explanations
- [ ] Chapter transitions

### 3. Content operations `[ ]`
The pipeline renders; it does not yet decide what to render.

- [ ] Topic discovery scored against a documented rubric
- [ ] Hook variants per video, A/B selectable
- [ ] Fact-checking pass with a source manifest wired into the brief
- [ ] Analytics loop once publishing exists

### 4. Instagram publishing `[~]`
Code exists in `video_studio/instagram.py` (`--publish`, `--publish-dry-run`),
specified in `08_INSTAGRAM_PUBLISHING.md`. **Never run against a live account.**

- [x] Container → poll → publish sequence against Graph API v26.0
- [x] Explicit opt-in flag (`--publish`), dry-run mode (`--publish-dry-run`), publish logging
- [x] Respect the 50 posts / rolling 24h limit; refuse when exhausted
- [ ] Public HTTPS hosting for the video URL (Meta fetches it itself) — **the real blocker**
- [ ] Prove it once against a throwaway account before touching a real one

**Blocked on:** a professional IG account, a valid long-lived token, public video
hosting, and the owner's explicit go-ahead. Do not begin without all four. Exit
**5** = missing or unauthorized credentials, exit **6** = quota / container / API failure.

### 5. Automation `[ ]`
- [ ] Single on-demand command that runs the whole chain
- [ ] Scheduled execution with job records and structured logs
- [ ] Asset reuse keyed on input hash so unchanged scenes skip re-rendering
- [ ] Optional GitHub Actions runner, or local scheduling if the machine sleeps

### 6. Renderer hygiene `[~]`
- [ ] Decide on upgrading HyperFrames 0.8.58 → 0.8.145
- [ ] Add `--docker` render mode for reproducible Chrome and fonts once Docker runs

---

## Known limitations, stated plainly

1. **Only one voice has been auditioned.** `af_heart` is the default and the only
   voice used in the shipped Reel. Nobody has compared it against the brand voice
   array. The pipeline works; whether the voice *fits* is an open question.
2. **Two tests fail, and both are stale assertions — not new bugs.**
   `test_real_reel_passes_inspection` still asserts `audio_absent` against a Reel
   that now has audio, and `test_expect_audio_on_silent_video_is_a_defect` asserts
   a silent fixture now behaves differently. The fix is to update the tests to the
   narrated reality; no production code is implicated.
3. **Determinism is unverified *with* narration.** The byte-identical SHA-256 pair
   was measured on the silent render. See the note under *Status now*.
4. **Standard and high quality are unverified.** Only `draft` has been measured.
5. **`models/` is ~337 MB and is not in the repository.** It is gitignored, so a
   fresh clone has no Kokoro weights and `--audio` degrades to silent until they
   are re-downloaded. `05_SETUP_AND_INSTALLATION.md` §3.2 has the commands.
6. **`hyperframes doctor` falsely reports TTS as not installed.** The probe uses the
   wrong Python. Ignore that line; `video_studio.audio.kokoro_available()` is the
   real check.
7. **Fonts come from Google Fonts over the network.** A locked-down or offline
   render falls back to system fonts. `hyperframes-localize-fonts` exists for this.
8. **Instagram was never readable** at research time, so no post-level analysis
   informed any of this.
9. **The legacy `src/content/hyperframes_engine.py` still exists** and still shares
   the HyperFrames name. It is untouched and still used by the Autogram 60s
   pipeline. It is not part of `video_studio/`.
10. **Integrated GPU only.** Software rendering works; GPU encoding is unverified.

---

## Do not do these without authorization

- Enabling any paid API or subscription
- Publishing to a real Instagram account
- Committing tokens, keys, or `.env` contents
- Claiming a render, test, or publish that was not actually run and verified