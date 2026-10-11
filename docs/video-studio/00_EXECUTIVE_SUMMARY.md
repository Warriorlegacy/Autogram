# Video Studio — Executive Summary

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/00_EXECUTIVE_SUMMARY.md` |
| **Date** | 2026-10-11 |
| **Subject** | Signhify Studio 9:16 short-form video engine |
| **Status** | Real project, partially shipped. Not a pitch deck. |
| **Owner** | Piyush Raj Singh — AI systems engineer, Varanasi, India |

**Companion documents**

- `01_TECHNICAL_RESEARCH.md` — toolchain audit, licensing deep dive, source register (797 lines)
- `02_BRAND_AND_CONTENT_STRATEGY.md` — brand system, content strategy, hook library, concept rubric

---

## 1. What Was Built

Two artifacts exist as of 2026-10-11:

1. **A verified technical audit** (`01_TECHNICAL_RESEARCH.md`). It settles two decisions with evidence rather than preference: which composition engine owns this pipeline, and which competing engine is disqualified by license terms.
2. **An empirical production Reel.** The adopted toolchain was executed on this machine and produced a valid 1080×1920 H.264 + AAC MP4 that passed the tool's own QA gate. This is not a vendor claim — it was run and probed with `ffprobe`. **It has narration.** Kokoro-82M speaks all seven scenes; the track is measured, concatenated, loudness-normalised to EBU R128, and muxed into the MP4.

What does **not** exist yet: a published Reel. Everything from brief to packaged artifact works; nothing has gone to a live Instagram account. Topic selection and fact-checking are specified below as planned units, not presented as shipped.

---

## 2. The Stack Decision

Signhify Studio adopts the **HyperFrames CLI** (npm `hyperframes`, HeyGen, Apache-2.0, v0.8.58 installed) as the single composition and render engine, and drops Remotion from the critical path. HyperFrames renders locally with no account, no credits, and no vendor bill, and it ships a built-in QA gate (`hyperframes check` — runtime, layout, motion, WCAG AA contrast, snapshots) that the existing hand-rolled Python engine has no equivalent of. Remotion occupies the identical slot in this architecture but is source-available rather than open source, and its free tier ends at three employees — a cliff this studio is plausibly near, since `brand.json` describes commercial tiers, client work, and a full engineering studio. Apache-2.0 carries no employee threshold and no revenue threshold, so the license risk is zero at any org size. Every other link in the chain (FFmpeg, Kokoro-82M TTS) also has a free permissive-license alternative and is installed. Transcription turned out to be unnecessary: synthesizing **per scene** and measuring each scene's audio yields caption timing directly from real speech, so `faster-whisper` is not on the critical path.

---

## 3. Verified Capability List

Each row was confirmed by direct CLI inspection on the machine of record, not by documentation reading alone.

| Capability | Value | How verified |
|---|---|---|
| Engine | HyperFrames CLI, Apache-2.0 | `node_modules/hyperframes/package.json` |
| Installed version | v0.8.58 (latest published: 0.8.145) | `npm ls`, npm registry |
| Render resolution | 1080 × 1920 | `ffprobe` width / height |
| Frame rate | 30/1 fps | `ffprobe` `r_frame_rate` |
| Video codec | h264 | `ffprobe` |
| Reel duration | 45.5 s | `ffprobe` format duration |
| Audio codec | **AAC, 48 kHz, mono** | `ffprobe` stream 1 |
| Loudness | **−16.1 LUFS integrated, −1.5 dBFS true peak** | `ffmpeg -af ebur128=peak=true` |
| QA gate | Passed — 0 runtime, 0 layout, 0 motion, contrast 5/5 WCAG AA | `hyperframes check` + `qa.py` |
| Determinism | **Silent render only** — two runs byte-identical (SHA-256 `52F88E97…B61522E`). **Not re-verified with narration** | Two back-to-back renders, hashed |
| TTS | **Kokoro-82M installed and in use.** `kokoro-onnx` 0.4.7, weights in `models/kokoro/`. Default voice `af_heart`. Called as a **library** — the `hyperframes tts` CLI cannot find the venv Python and fails even with `HYPERFRAMES_PYTHON` set | `pip show`, `kokoro_available()`, `render.log` |
| Narration | 7 scenes, **36.78 s** of speech, 0.25 s silence between scenes, `apad`-padded to 45.5 s | `[audio] provider=kokoro scenes=7 narration=36.78s` |
| Transcription | **Not used.** Per-scene synthesis derives caption timing from measured speech, so `faster-whisper` is unnecessary here | `storyboard.json` caption cues |
| Brand source of truth | `data/brand.json` — 9 colour tokens, 5 font roles, 16 banned phrases | Read directly |

---

## 4. What Is Real vs What Is Planned

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1 | Toolchain audit | **Real** | `01_TECHNICAL_RESEARCH.md` | Two decisions settled with evidence |
| 2 | 1080×1920 H.264 render | **Real** | `ffprobe` output | Production composition, not a blank one |
| 3 | QA gate integration | **Real** | `hyperframes check` + `qa.py` both passed | Runs post-authoring, pre-delivery |
| 4 | License position | **Real** | Vendor `LICENSE.md`, npm metadata | Apache-2.0, no thresholds |
| 5 | Brand token source | **Real** | `data/brand.json` | Single source; do not re-declare hex |
| 6 | Brand-correct composition | **Real** | 7 rendered scenes, QA PASS | Reads the 9 published carousel slides |
| 7 | Blueprint grid + orange eyebrow chrome | **Real** | QA frames | |
| 8 | Caption pipeline | **Real** | 16 cues in `captions.srt` | Timed from measured speech, not a transcript |
| 9 | Voiceover pipeline | **Real** | `provider=kokoro`, −16.1 LUFS | Kokoro-82M installed, `af_heart`, 36.78 s speech |
| 10 | Scheduled publishing | **Planned** | — | `--publish` is implemented but **never run live** |
| 11 | Render-throughput SLA | **Planned** | — | Only `draft` measured, and only on the silent path |
| 12 | HyperFrames upgrade 0.8.58 → 0.8.145 | **Planned** | — | 87 patch versions; read release notes first |
| 13 | Production Reel (end to end) | **Real** | `output/signhify-prompt-to-3d-site/reel.mp4` | Renders, narrated, passes QA. **Not yet published** |
| 14 | Post-level Instagram analytics | **Impossible** | — | Profile is auth-walled; no data exists |

---

## 5. Cost Position

| Line item | Cost | Note |
|---|---|---|
| Composition + render engine | **$0** | Apache-2.0, local, no account, no credits |
| FFmpeg | **$0** | Installed 8.0.1 |
| Text-to-speech | **$0** | Kokoro-82M, local inference |
| Transcription | **$0** | faster-whisper, local |
| Fonts | **$0** | Plus Jakarta Sans, Inter, JetBrains Mono, Caveat, Anton |
| Cloud render | **$0** | Not used. Local CPU render only |
| **Running total** | **$0** | Approach A — code-driven |

The reference technique published in carousel slide 05 — *"100% Crisp Typography at $0 Compute Cost"*, via LLM-structured JSON rendered programmatically in Chromium — is the same economics applied to video. The pipeline is text, JSON, HTML, and local CPU. No metered API sits on the critical path.

The one line item that could become non-zero: publicly reachable hosting for the `video_url` that Meta's `media` endpoint requires. That depends on the existing uploader cascade and was not evaluated here.

---

## 6. Licensing Reasoning

| Dimension | HyperFrames CLI | Remotion |
|---|---|---|
| License | Apache-2.0, unconditional | Source-available, not OSI open source |
| Free tier | Unconditional | For-profit orgs with ≤3 employees |
| Above threshold | No change | Creators $25/seat/mo; Automators $0.01/render with $100/mo floor; Enterprise from $500/mo |
| Trigger | — | **Org size, not revenue** |
| QA tooling | `check` built in | None comparable found |
| TTS + captions | `tts`, `transcribe` | Not in the free band |

Commercial video creation is permitted free inside the ≤3-employee band. That band is the entire risk: `brand.json` positions Signhify Studio as a commercial engineering studio with paid tiers and client work. If the org ever exceeds three employees, Remotion becomes a billing line with a per-seat multiplier on every renderer.

**Decision:** build on HyperFrames. Keep the two existing Remotion compositions in `src/video/` on disk as reference only. Do not migrate them. A Remotion 5.0 license change is announced; its terms are unverified — read `LICENSE.md` before any 5.x upgrade.

---

## 7. Honest Limitations

These are recorded so nobody downstream mistakes a plan for a shipped feature.

**On the research itself**

- **`instagram.com/signhify.studio` was blocked by an auth wall at research time.** No post-level analysis is possible. No follower count, no engagement rate, no per-format retention, no top-post identification. Any future doc claiming these is fabricating them.
- **Handle discrepancy, unresolved.** `brand.json` and all 9 carousel watermarks say `@signhify.studio`. The website footer links Instagram as `/piyushrajsingh.golu` and LinkedIn as `/in/piyushraj-singh`. Which handle is live is unknown. On-screen chrome uses `@SIGNHIFY.STUDIO` because that is what 9 published assets already carry.
- **No metrics exist.** No signups, revenue, team size, testimonials, uptime, or churn were obtainable. None are asserted anywhere in these docs.
- **Competitor claims are marketing assertions.** "Lovable: Basic 2D only" and the rest of the pricing-page comparison are the site's own words, unverified.
- **Portfolio and Venture Lab were not exercised.** Four portfolio entries (Signhify AI, Veepee Engineers, GymFlow, AutoReels AI) and 10 Venture Lab apps were observed to exist. Functionality was not tested.

**On the toolchain**

- **Only the silent path has been timed.** 15.3 s for a 120-frame blank composition; ~55 s for the 40.5 s silent production Reel. The narrated path adds Kokoro synthesis and the mux on top and has not been re-timed. No per-Reel SLA is committed.
- **87 patch versions sit between the installed 0.8.58 and the current 0.8.145.** Breaking-change surface unknown. Read the release notes, then re-run the smoke test.
- **Only one voice has been heard.** Kokoro `af_heart` is the default and the sole voice used. It is Apache-2.0 and the pipeline is proven, but nobody has compared it against the brand voice array — *authoritative, architectural, hyper-practical, zero-fluff*. Audition the rest before scaling.
- **Determinism is unverified *with* narration.** The byte-identical SHA-256 pair was measured on the silent render. Kokoro is a local ONNX graph with no clock or RNG, so it is deterministic in principle, and `apad`/`-shortest` are deterministic filters — but that is reasoning, not a measurement. Diff two narrated runs before claiming reproducibility.
- **`hyperframes doctor` falsely reports TTS as "Not installed."** The CLI probes a Python it cannot locate — the packages are in `.venv`, not system Python — and fails even with `HYPERFRAMES_PYTHON` set. Re-verified 2026-10-11 on a machine where Kokoro had just shipped a Reel. `video_studio.audio.kokoro_available()` is the real check.
- **`models/` is ~337 MB and is not in the repo.** It is gitignored, so a fresh clone has no Kokoro weights and `--audio` degrades to a silent render until they are re-downloaded.
- **FFmpeg build variant unverified** (LGPL vs GPL). Only matters if binaries are redistributed.
- **Employee count vs the 3-employee Remotion threshold is internal and unchecked.** Confirm it. If above three, the Remotion conclusion hardens from "avoid" to "prohibited without payment".
- **A naming collision exists in the repo.** `src/content/hyperframes_engine.py` is a hand-rolled Python/Jinja2/Playwright engine that shares a name with HeyGen's Apache-2.0 product and is not it. It has no `check`, no TTS, no captions, no CLI. It is quarantined, not deleted — deletion waits until one production Reel publishes through the CLI path.

---

## 8. Reproduction Commands

Executed on the machine of record. Prefix with `npx ` if `hyperframes` is not on `PATH`.

### 8.1 Reproduce the shipped Reel

```powershell
# Confirm the Kokoro weights are present (gitignored — absent on a fresh clone)
.venv\Scripts\python.exe -c "from video_studio.audio import kokoro_available; print(kokoro_available())"

# Build + render + narrate + QA in one command
.venv\Scripts\python.exe -m video_studio.cli render `
  --brief video_studio/briefs/signhify-prompt-to-3d-site.json `
  --quality draft --audio
```

Seven stages: `[2/7]` narration → `[3/7]` check → `[4/7]` render → `[5/7]` mux → `[6/7]` package → `[7/7]` QA. Add `--publish` for an `[8/8]`.

### 8.2 Toolchain smoke test

```bash
# 1. Environment audit — version, browsers, ffmpeg, node
hyperframes doctor

# 2. Scaffold a throwaway composition to prove the toolchain
hyperframes init smoke --example blank

# 3. Render — 30 fps, draft quality
hyperframes render -f 30 -q draft

# 4. QA gate — runtime, layout, motion, contrast, snapshots
hyperframes check

# 5. Verify the output independently of the tool
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,codec_name,nb_frames \
  -of default=noprint_wrappers=1 smoke/out.mp4
```

That smoke path produces the 120-frame, 120-frame-duration blank composition. It proves the toolchain, **not** the shipped Reel — use §8.1 for that.

Expected probe output, matching the run that backed §3 — against the shipped Reel:

```
# video stream
width=1080
height=1920
r_frame_rate=30/1
codec_name=h264
duration=45.500000
# audio stream
codec_name=aac
sample_rate=48000
channels=1
```

And the loudness measurement:

```powershell
ffmpeg -hide_banner -nostats -i <reel.mp4> -af ebur128=peak=true -f null NUL
# Integrated loudness: I: -16.1 LUFS
# True peak:            Peak: -1.5 dBFS
```

Note: `hyperframes init` takes `--example`, not `--template`. `--template` errors out.

---

## 9. Next Build Units

In dependency order. Each is a gate, not a milestone claim.

| # | Unit | Done when |
|---|---|---|
| 1 | Audition the remaining Kokoro voices | A voice chosen against the brand voice array, not defaulted to |
| 2 | Re-verify determinism **with** narration | Two narrated renders hash identically |
| 3 | Music bed with ducking under speech | Loudness stays inside the EBU budget with music present |
| 4 | One published Reel | Container → poll → publish succeeds once against a throwaway account |
| 5 | Topic discovery + fact-checking | Briefs are chosen by a rubric, with a source manifest |
| 6 | Retire `src/content/hyperframes_engine.py` | Only after unit 4 ships |
| 7 | Upgrade 0.8.58 → 0.8.145 | Release notes read; smoke test re-passed |

Fail-closed applies here too. If the QA gate fails, the Reel does not ship. A gate that can be bypassed is not a gate.

---

*Compiled 2026-10-11 from direct inspection of this machine, `data/brand.json`, the 9 published carousel renders, and the live product site. Where a fact was not obtainable, it is marked unverified rather than estimated.*