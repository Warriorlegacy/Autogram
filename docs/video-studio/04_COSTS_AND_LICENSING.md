# Video Studio — Costs and Licensing

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/04_COSTS_AND_LICENSING.md` |
| **Date** | 2026-10-11 |
| **Machine of record** | Windows 11 x64, i5-1145G7 @ 2.60 GHz (8c/4t), 15.7 GB RAM, 13.2 GB free, integrated GPU, **no CUDA** |
| **Measured artifact** | `video_studio/output/signhify-prompt-to-3d-site/reel.mp4` — 40.5 s, 2,213,568 bytes |
| **Companions** | `01_TECHNICAL_RESEARCH.md` (toolchain audit), `03_SYSTEM_ARCHITECTURE.md` |

Evidence standard: every cost below is either **measured on this machine**, **quoted from a vendor's own published page**, or tagged **UNVERIFIED**. Nothing else appears as a number.

---

## 1. Three Profiles

| | **A — Local / open source** | **B — Hybrid** | **C — Premium** |
|---|---|---|---|
| **Status today** | **In production use** | Available, unbuilt | Not adopted |
| **Composition + render** | HyperFrames local | HyperFrames local | HeyGen cloud render / avatar |
| **Narration** | **Kokoro-82M local, installed** | One cloud TTS fallback | HeyGen Starfish |
| **Stock media** | none | generated B-roll / stills | licensed stock + avatar |
| **Marginal cost / 40 s Reel** | **$0** | **$0 + UNVERIFIED** | **~$20–32 UNVERIFIED** (see §5) |
| **Fixed monthly** | **$0** | $0 | $99–330/mo |
| **Setup complexity** | Low — one venv, one `npx` | Medium — keys, quotas, retries | High — account, credits, async polling |
| **Hardware** | This machine is sufficient | Same, plus network | None locally |
| **Reproducibility** | **Exact**, same inputs → same file | Mixed; assets must be pinned | Low |
| **Licence exposure** | **None.** Apache-2.0 / LGPL / MIT throughout | Per-asset terms must be checked per media | Proprietary, metered |
| **Blocking prerequisite** | none | image/video model selection + pricing | account + credit purchase |

### 1.1 Recommendation

**Start on Profile A and stay there until a measured retention delta says otherwise.**

The decision rule, stated once: *move to B when a specific concept measurably fails without a media layer and succeeds with one; move to C when a recurring offer genuinely requires a human presenter and the per-minute cost has been validated against real revenue.* Neither condition is currently true. No retention data exists — `instagram.com/signhify.studio` was auth-walled at research time.

---

## 2. Per-Tool Licence and Cost

| Tool | Licence | Commercial use | Cost | Status here | Notes |
|---|---|---|---|---|---|
| **HyperFrames CLI** | **Apache-2.0** | Unconditional. No employee or revenue threshold | **$0** — local render, no account, no credits | **[I]** v0.8.58 installed; latest **0.8.145** | Same product HeyGen builds internally. Paid tiers are avatar/translation, not the renderer |
| **FFmpeg** | **LGPL-2.1-or-later** (GPL-2.0-or-later on GPL builds) | Yes | $0 | **[I]** 8.0.1 full build, `www.gyan.dev` | Avoid GPL-enabled builds if binaries are ever redistributed. Build variant of the installed binary is **UNVERIFIED** |
| **jinja2** | BSD-3-Clause | Yes | $0 | **[I]** 3.1.6 | Template render only |
| **pydantic** | MIT | Yes | $0 | **[I]** 2.13.5 | Brief validation |
| **pillow** | MIT-CMU (HPND) | Yes | $0 | **[I]** | In `requirements.txt`; not currently on the video path |
| **Python** | PSF | Yes | $0 | **[I]** venv 3.14.7 | System 3.14.0 lacks the deps |
| **Node.js** | MIT | Yes | $0 | **[I]** v22.23.1 | HyperFrames hard-requires 22+ |
| **GSAP 3.14.2** | Standard "no charge" GreenSock licence | Yes for this use | $0 | **[I]** CDN-loaded | Free tier covers standard use. Re-check on commercial scale-up |
| **Google Fonts** (Plus Jakarta Sans, Inter, JetBrains Mono) | SIL OFL 1.1 | Yes | $0 | **[I]** | Loaded at render time from `fonts.googleapis.com` |
| **Kokoro-82M** | **Apache-2.0** (weights **and** inference lib) | **Yes, unrestricted** | **$0** | **[S] INSTALLED and in use** | `kokoro-onnx` 0.4.7 + weights in `models/kokoro/`. ~54 voices, 24 kHz, CPU-only. `espeakng-loader` 0.2.4 supplies the phonemizer — no system `espeak-ng` needed. Default voice `af_heart`. **Repo source of truth: `video_studio/audio.py`** |
| **faster-whisper** | MIT | Yes | $0 | **[I]** in `requirements.txt` | Word timestamps. **Not wired into `video_studio` yet.** Not needed for the shipped pipeline — narration is synthesized per scene, so caption timing derives from measured speech instead of transcription |
| **soundfile** | BSD-3-Clause | Yes | $0 | **[I]** 0.14.0 | Writes the per-scene wavs. Ships with `kokoro-onnx` |
| **edge-tts** | LGPL (client) | **Risky** | $0 | **[I]** installed, **[N]** unused | Microsoft's service ToS may prohibit commercial use without an Azure subscription. Do not ship on monetized output |
| **Piper** (original `rhasspy/piper`) | MIT | Yes | $0 | not installed | **Archived upstream** |
| **Piper** (`piper-tts` on PyPI) | **GPL-3.0-or-later** | Yes, copyleft | $0 | not installed | **Do not adopt.** Some voice weights inherit CC-BY dataset terms |
| **OpenAI TTS** | Proprietary | Yes, **with AI-voice disclosure** | **~$0.015/min — UNVERIFIED** | not installed | Documented fallback only. No word timestamps |
| **ElevenLabs** | Proprietary | **Free tier explicitly NOT commercial** | commercial from ~**$5/mo** Starter | not installed | Free tier unusable for monetized output |
| **HeyGen API** | Proprietary | Yes | $99–330/mo + metered credits | not adopted | See §5 |
| **Remotion** | **Source-available. NOT OSI open source** | Conditional | see §6 | v4.0.526 installed, off the critical path | Free only below the employee threshold |
| **Meta Graph API** | Platform ToS | Yes | **$0** — free tier; constrained by rate limits, not price | **[N]** publishing not implemented | API access itself is free |
| **Docker** (`hyperframes --docker`) | n/a | n/a | $0 | installed, **daemon not running** | Deterministic Chrome + fonts. Not enabled |

---

## 3. The Licensing Decision, in Full

### 3.1 HyperFrames — adopted

| Attribute | Value |
|---|---|
| Package | npm `hyperframes` (HeyGen) |
| Licence | **Apache-2.0**, confirmed in `node_modules/hyperframes/package.json` |
| Threshold | **None.** No employee count. No revenue band. No seat fee |
| Cost | **$0** for local render. An account is needed only for `cloud render`, `catalog`, BGM/SFX retrieval, and HeyGen TTS — none of which this pipeline uses |
| Runtime | puppeteer-core · @puppeteer/browsers · sharp · esbuild · hono |
| System deps | Node 22+, a **system** FFmpeg (not bundled), outbound HTTPS for fonts + GSAP |
| Hardware | CPU render. `--gpu` (NVENC/VideoToolbox/AMF/VAAPI/QSV) needs hardware this machine lacks |

Apache-2.0 is the reason this was chosen over the incumbent. It is a licence whose terms do not change shape as the studio grows.

### 3.2 Remotion — the near-miss

Remotion occupies the identical architectural slot and the repo already contains working compositions at `src/video/Root.tsx` and `src/video/SignhifyReel.tsx`. That is the entire argument for it, and it does not survive the licence.

| Organisation type | Cost |
|---|---|
| Individuals | Free |
| For-profit orgs with **≤ 3 employees** | Free |
| Non-profits | Free |
| Evaluation / non-commercial | Free |
| For-profit orgs **> 3 employees** — Creators | **$25 / seat / month** |
| For-profit orgs **> 3 employees** — Automators | **$0.01 / render, $100 / month minimum** |
| For-profit orgs **> 3 employees** — Enterprise | **from $500 / month** |

Three points that matter:

1. **The cliff is org size, not revenue.** Commercial video creation is permitted free inside the ≤3-employee band. Revenue does not cross it; hiring does.
2. **Signhify is plausibly near that line.** `data/brand.json` describes a "FULL A.I. ENGINEERING STUDIO" with commercial tiers ($5 / $50 / $100 / $200 per month), client work, a public website, and a founder wearing two hats. Actual headcount is **UNVERIFIED** — confirm internally.
3. **Remotion ships no QA gate.** It has no equivalent of `hyperframes check` (Runtime / Layout / Motion / WCAG AA contrast / Snapshots). That tooling would have to be built or bought.

Remotion also pins Chrome Headless Shell 149.0.7790.0 and, since v4.0.208, refuses an externally installed browser.

**Decision: keep the two compositions on disk as reference. Do not build on them. Do not migrate.** If the org is confirmed above three employees, the conclusion hardens from "avoid" to "prohibited without payment."

**Remotion 5.0 licence terms are announced in `LICENSE.md` and are UNVERIFIED.** Read the file before any 5.x upgrade.

### 3.3 The name collision — still unresolved

`src/content/hyperframes_engine.py` (29,363 bytes, 641 lines) is a **hand-rolled Python/Jinja2/Playwright engine**, not an implementation of HeyGen's product. It declares its own five dark neon `THEMES`, invents its own template schema, and has no `check`, no TTS, no captions, no CLI.

It is **quarantined, not deleted.** Deletion is gated on one production Reel rendering, passing QA, and publishing through the CLI path. Renaming its log prefix and docstring to `hand-rolled reel engine (pre-HyperFrames-CLI)` costs one line and removes the ambiguity for every future reader.

### 3.4 Narration — decided on licence, not on quality

| Option | Licence | Commercial | Word timestamps | Cost | Verdict |
|---|---|---|---|---|---|
| **Kokoro-82M** | Apache-2.0 | **Unrestricted** | No | $0 | **ADOPTED — in production use** |
| edge-tts | LGPL client | **Risky** — Microsoft service ToS | **Yes**, native `WordBoundary` | $0 | Fallback only. **Do not ship on monetized output** |
| Piper (archived) | MIT | Yes | No | $0 | Archived |
| Piper (PyPI) | GPL-3.0 | Yes, copyleft | No | $0 | Do not adopt |
| OpenAI TTS | Proprietary | Yes, with disclosure | No | ~$0.015/min **UNVERIFIED** | Fallback |
| ElevenLabs | Proprietary | Free tier **non-commercial** | No | from ~$5/mo | Fallback, paid |
| HeyGen Starfish | Proprietary | Yes | **Yes** | credits, per-minute **UNVERIFIED** | Not needed |

Three operational notes:

- **The HyperFrames `tts` CLI is not used, and does not work here.** It shells out to a Python it cannot locate — `kokoro-onnx` lives in `.venv`, not system Python — and it still fails with `HYPERFRAMES_PYTHON` set. The error misreports the package as missing. `video_studio/audio.py` calls the `kokoro_onnx` library directly instead. Symptom and workaround: `09_TROUBLESHOOTING.md` §3.
- The published `hyperframes` CLI is frequently a **local-only build** and will **silently fall back to Kokoro even when `$HEYGEN_API_KEY` is set.** Never infer which engine produced a track from an environment variable — log the engine that actually ran. `render.log` carries an explicit `[audio] provider=…` line for this reason.
- Kokoro emits **no word timestamps.** That has not blocked shipping: narration is synthesized **per scene** and each scene's wav is measured, so caption timing comes from real speech duration rather than a transcription pass. If per-*word* timing is ever needed, a `faster-whisper` stage has to be bolted on.

### 3.5 FFmpeg

Two-pass `loudnorm` (I = −16 LUFS, TP = −1.5 dBTP, LRA = 11) is implemented in `render.py:mux_audio`. Two traps are baked into the design:

1. `linear=true` requires **all four** measured values. If any is missing, FFmpeg **silently reverts to dynamic mode** — the single most common cause of "I did two passes and it still sounds dynamic." `mux_audio` supplies defaults (`-24`, `-2`, `7`, `-32`) so the parameter is always present.
2. The output sample rate is set explicitly with `-ar 48000`. Omitting it resamples against a different default.

FFmpeg 9.0.2 is the current stable release. Do not upgrade for this project — 8.0.1 works and HyperFrames pins its own expectations. Confirm the installed build is the LGPL variant **only if** binaries are ever redistributed.

---

## 4. Profile A — Cost Model, Measured

### 4.1 Render time

Measured on the machine of record, from `render.log`:

| Stage | Command | Wall-clock |
|---|---|---|
| QA gate | `hyperframes check` | **21.3 s** |
| Render | `hyperframes render -f 30 -q draft` | **33.3 s** |
| **Total pipeline** | brief → artifacts on disk | **~55 s** |
| QA frame extraction | 7 × `ffmpeg` single-frame grabs | ~2 s |
| Package write | 6 small JSON/text files | <1 s |

Throughput: **1,215 frames / 33.3 s = 36.5 fps of render throughput**, CPU-only, integrated GPU, no CUDA.

Earlier reference points:

| Composition | Frames | Duration | Wall-clock | Throughput |
|---|---|---|---|---|
| `blank` smoke | 120 | 4.0 s | **15.3 s** | 7.8 fps |
| `signhify-prompt-to-3d-site` (real) | 1,215 | 40.5 s | **33.3 s** | 36.5 fps |

The second is faster per frame than the first. The 15.3 s smoke figure includes Chrome cold-start and first-run overhead; the real render amortises it across 1,215 frames. **Do not quote 15.3 s as a production SLA.** Quote 55 s end-to-end for a 40 s draft, and re-measure at `standard` and `high`.

### 4.2 Quality tiers

Unmeasured on this machine. Only `draft` has been run.

| Tier | CRF/bitrate effect | Extrapolated wall-clock | Status |
|---|---|---|---|
| `draft` | Measured: **436 kbps**, 2,213,568 bytes | **33.3 s** (measured) | **[I]** verified |
| `standard` | Higher bitrate, more encode time | **UNVERIFIED** | not run |
| `high` | Highest bitrate, slowest | **UNVERIFIED** | not run |

A 40.5 s Reel at `draft` is ~2.2 MB. At a plausible 6 Mbps publishing bitrate the same duration would be ~30 MB. **UNVERIFIED** — no `standard` or `high` render has been produced, so no number for those tiers may be quoted as fact.

### 4.3 Disk per video

Measured, `video_studio/output/signhify-prompt-to-3d-site/`:

| Artifact | Bytes | Note |
|---|---|---|
| `reel.mp4` | 2,213,568 | draft quality |
| `cover.jpg` | 97,357 | t = 0.9 s, `-q:v 2` |
| `qa_frames/` × 7 | 650,419 | 75 KB – 137 KB each |
| `storyboard.json` | 5,802 | |
| `brief.json` | 3,793 | |
| `render.log` | 17,153 | grows with console output |
| `qa_report.md` | 1,498 | |
| `qa_report.json` | 2,181 | |
| `captions.srt` | 980 | |
| `caption.txt` | 216 | |
| `asset_manifest.json` | 423 | |
| **Total** | **≈ 3.0 MB** | |
| `work/<slug>/` (regenerated, not accumulated) | ~60 KB + logo | `rmtree`'d on every build |

**~3 MB per draft video.** 13.2 GB free disk therefore holds well over 1,000 drafts before cleanup — disk is not the constraint; RAM (15.7 GB, shared with Chrome) is.

### 4.4 Marginal cost of a 40 s Reel

| Line | Cost |
|---|---|
| HyperFrames | $0 |
| FFmpeg | $0 |
| Python deps | $0 |
| Fonts | $0 |
| GSAP | $0 |
| TTS (Kokoro-82M, installed) | $0 |
| Transcription (faster-whisper, CPU) | $0 |
| Meta Graph API | $0 |
| **Marginal total** | **$0** |
| Machine time | 55 s wall-clock on hardware already owned |

At 7 Reels/day: **7 × 55 s = 6.4 minutes of machine time per day.** At 30/month: ~28 minutes/month.

**The one line that can become non-zero:** public HTTPS hosting for the `video_url` that Meta's `media` endpoint requires. The existing uploader cascade in `src/storage/uploader.py` may already satisfy it — **UNVERIFIED.** Resolve before any publish attempt; see `08_INSTAGRAM_PUBLISHING.md`.

### 4.5 Total cost of ownership

| Item | One-time | Recurring |
|---|---|---|
| Everything above | $0 | $0 |
| Public hosting for `video_url` | UNVERIFIED | UNVERIFIED |

**Profile A's marginal cost per 40 s Reel is $0.** The only cost is the authoring hours, which are the same at any price point.

---

## 5. Profile B — Hybrid

Profile A plus one or more external generation APIs for B-roll, stills, or a narration fallback.

**Cannot be costed honestly without naming a specific model.** Naming a category and producing a number would be invention. The pipeline's own `image_generator.py` already has a nine-provider fallback chain — pricing it means picking one provider and pricing one render, not averaging a list.

| Line | Cost |
|---|---|
| All of Profile A | $0 |
| Image / video generation | **UNVERIFIED** — model not selected |
| Cloud TTS fallback | **UNVERIFIED** — OpenAI ~$0.015/min unconfirmed; ElevenLabs from ~$5/mo |
| **Marginal total** | **$0 + UNVERIFIED** |

When B becomes right: when a composition cannot carry a topic on its own and a media layer measurably improves retention. That decision needs data this pipeline does not collect.

---

## 6. Profile C — Premium (Not Adopted)

### 6.1 HeyGen API

| Plan | Monthly | Credits | Note |
|---|---|---|---|
| Free | $0 | 10/mo | **Watermarked, no auto-renew** |
| Pro | **$99/mo** | 100/mo | |
| Scale | **$330/mo** | 660/mo | |
| Enterprise | Custom | Custom | |

Per HeyGen's own 2026 blog, at Pro's **$0.99/credit**:

| Model | Credits/min | Implied cost/min |
|---|---|---|
| Avatar IV | 31 | **~$30.7 / min** |
| Avatar V | 48 | **~$47.5 / min** |

> **HeyGen's own pages contradict each other on the credit-to-minute mapping.** One page implies 5-minute photo avatars per credit, another implies 1-minute. Both cannot be true. **UNVERIFIED — do not rely on either figure without a measured paid render.**

### 6.2 Cost at volume

Taking the 40.5 s reference Reel and HeyGen's own (contradicted) figures:

| Volume | Profile A | Profile C (Avatars) | Ratio |
|---|---|---|---|
| 1 Reel/day | $0 | ~$400/mo fixed + metered — **UNVERIFIED** | — |
| 30 Reels/month, 60 s each | $0 | Pro $99 + 30 renders × ~$30.7 ≈ **~$1,020/mo** | ~1,020× |
| 7 Reels/day, 60 s each | $0 | ~**~$6,300/mo** | — |

The 60-second figure is used because that is HeyGen's published per-minute denominator. At 40 s it is proportionally lower. The point is the order of magnitude, and the order of magnitude is not close.

### 6.3 Why not

| Reason | Detail |
|---|---|
| **Cost** | ~1,000× Profile A at realistic volume, before any fixed subscription |
| **Determinism** | Cloud render is not reproducible. Profile A is byte-stable for identical inputs, which is what makes regression checks and A/B tests possible at all |
| **No requirement** | Nothing in the content strategy needs a human presenter. The audience is engineers, who scroll past talking heads |
| **Brand control** | Caption styling and framing are platform-controlled on the avatar path; the brand system in `02_BRAND_AND_CONTENT_STRATEGY.md` is unenforceable there |
| **Account dependency** | Requires a HeyGen account, which the local HyperFrames path deliberately avoids |

Remains a documented line item, not a rejection. If a recurring client offer requires a presenter, the cost is a known number rather than a surprise.

---

## 7. Unverified — Do Not Quote These as Fact

| # | Item | Why unverified | How to resolve |
|---|---|---|---|
| 1 | **HeyGen credit-to-minute mapping** | HeyGen's own pages contradict each other | Run one paid Avatar IV render, read the credit delta |
| 2 | **OpenAI TTS ~$0.015/min** | Not confirmed against a current pricing page | Check the vendor page before adopting as a fallback |
| 3 | **HeyGen Starfish TTS per-minute** | Metered in credits; no published per-minute figure | Derive from a measured render |
| 4 | **Profile B asset-generation cost** | No model selected | Name a model, price one render, multiply |
| 5 | **Public HTTPS hosting cost for `video_url`** | Depends on `src/storage/uploader.py`, not evaluated | Test whether the current CDN path is publicly reachable, then price the fallback |
| 6 | **`standard` / `high` render wall-clock and bitrate** | Only `draft` has been run on a real composition | Render once at each tier, record wall-clock and `ffprobe` `bit_rate` |
| 7 | **FFmpeg build variant — LGPL or GPL** | The installed 8.0.1 gyan.dev build's flags were not inspected | `ffmpeg -version` — only matters if binaries are redistributed |
| 8 | **faster-whisper real-time factor on this CPU** | Not benchmarked here | Run one 60 s transcription, record wall-clock |
| 9 | **Kokoro voice quality vs the brand `voice` array** | **Installed and shipping, but only one voice has been heard.** `af_heart` is the default and the sole voice used in the shipped Reel | Audition the remaining voices against `authoritative, architectural, hyper-practical, zero-fluff, contrarian, open-source-first`. One voice proves the pipeline works, not that the voice fits the brand |
| 10 | **Remotion 5.0 licence terms** | Announced in `LICENSE.md`, not read in full | Read the file before any 5.x upgrade |
| 11 | **HyperFrames 0.8.58 → 0.8.145 changelog** | 87 patch versions; breaking-change surface unknown | Read GitHub releases between the tags, then re-render the reference brief and diff |
| 12 | **Signhify headcount vs the 3-employee Remotion threshold** | Internal, unchecked | Confirm internally. Above 3 and Remotion becomes a billing line |
| 13 | **GSAP licence terms at commercial scale** | Standard "no charge" licence covers this use today | Re-read `gsap.com` standard-license terms when revenue or seats grow |

---

## 8. What Was Measured, and What It Was Not

| Claim | State | Evidence |
|---|---|---|
| 1080×1920, 30 fps, H.264 renders on this machine | **Measured** | `ffprobe` on `reel.mp4` |
| 40.5 s, 2,213,568 bytes, 436 kbps | **Measured** | `ffprobe` |
| `hyperframes check` passes, 21.3 s, 36/36 contrast | **Measured** | `render.log` |
| `hyperframes render` 33.3 s for 1,215 frames | **Measured** | `render.log` |
| End-to-end pipeline ~55 s | **Measured** | sum of the above + extraction |
| ~3 MB disk per draft video | **Measured** | directory listing |
| 7 Reels/day ≈ 6.4 min machine time/day | **Derived** from measured figures | 7 × 55 s |
| Production-composition render SLA | **Not committed** | Only `draft` on one composition has been timed |
| Instagram post performance | **No data** | `instagram.com/signhify.studio` auth-walled at research time |
| Business metrics of any kind | **None exist** | Never obtained, never asserted |
| Any follower / engagement / retention figure | **No data** | Same |

---

## 9. Licensing Summary Card

| Decision | Answer |
|---|---|
| Composition + render engine | **HyperFrames CLI**, Apache-2.0, $0, no thresholds |
| Encoder / normaliser | **FFmpeg 8.0.1**, LGPL-2.1-or-later, avoid GPL builds |
| Narration | **Kokoro-82M**, Apache-2.0, $0, local — **installed, in production use** |
| Word timestamps | **faster-whisper**, MIT, already a dependency — **not wired in.** Per-scene synthesis makes it unnecessary for captions |
| Do not ship | **edge-tts** (Microsoft ToS risk on monetized output) · **Piper PyPI** (GPL-3.0) · **ElevenLabs free tier** (explicitly non-commercial) |
| Do not build on | **Remotion** — source-available, bills per seat above 3 employees, no QA gate |
| Do not adopt | **HeyGen paid products** — ~1,000× the per-Reel cost, no current requirement |
| Quarantine, do not delete | `src/content/hyperframes_engine.py` — name collision, gated on one production Reel |
| Open-source rendering | `hyperframes_engine.py` is NOT HyperFrames. Do not confuse them |
| Distribution | Meta Graph API v26.0, $0. Design against **50 posts / 24 h** |
| Publishing status | **NOT IMPLEMENTED, NOT AUTHORIZED.** `asset_manifest.json` carries `publishing.enabled = false` |
| Tokens | Never hardcoded. Never committed. Placeholders only — see `08_INSTAGRAM_PUBLISHING.md` |
| Profile to start | **A.** $0 marginal. Move only on measured evidence |

---

*Compiled 2026-10-11 from `render.log`, `ffprobe` output on the reference artifact, `node_modules/hyperframes/package.json`, `data/brand.json`, `requirements.txt`, and the vendor pages in `01_TECHNICAL_RESEARCH.md` §9. Every price not measured on this machine or quoted from a named vendor page appears in §7 and appears nowhere else in this document.*