# Video Studio — Quality Checklist

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/07_VIDEO_QUALITY_CHECKLIST.md` |
| **Date** | 2026-10-11 |
| **When to run** | **AFTER** the automated gate passes, **BEFORE** a Reel is called production-ready |
| **Reference** | `video_studio/output/signhify-prompt-to-3d-site/` |

> ## The rule
>
> **Never call a video production-ready without inspecting the extracted frames in `qa_frames/`.**
>
> `hyperframes check` inspects the DOM and the runtime. `qa.py` inspects container metadata and extracts JPEGs. **Neither looks at a pixel.** Both defects that were found and fixed on the reference Reel — a tofu box plus a duplicated eyebrow marker, and a static meaningless `07` scene counter — were invisible to every automated check and obvious the moment a frame was opened.

---

## 0. Before You Start

| # | Precondition | Verify with |
|---|---|---|
| ☐ | `qa_report.md` shows `Verdict: PASS` | read the file |
| ☐ | `HyperFrames gate clean: True` | read the file |
| ☐ | `qa_frames/` contains 7 JPEGs | `Get-ChildItem video_studio\output\<slug>\qa_frames` |
| ☐ | You are reviewing the render you think you are | compare file timestamps against the last `render` call |
| ☐ | Quality tier is `draft` or better | `render.log` shows the `-q` flag |

```powershell
Get-ChildItem video_studio\output\<slug>\qa_frames
Get-Content video_studio\output\<slug>\qa_report.md -TotalCount 6
Select-String -Path video_studio\output\<slug>\render.log -Pattern 'hyperframes render -f'
```

**Open every JPEG in `qa_frames/`.** Seven files, about two minutes. Skip this and §1–§3 are worthless.

---

## 1. Opening Frame

The first 1.5 seconds decide retention. One verifiable fact, or nothing.

- ☐ **Frame at t = 0.0 is not empty.** No black, no `#F8F6F0` void, no half-faded scene
- ☐ **Headline is present and complete** — not mid-fade-in, not clipped
- ☐ **Chrome is already on** at frame 1: `© 2026` · `@SIGNHIFY.STUDIO` · counter. It never animates in
- ☐ **Eyebrow reads as clean text** in `#E05A36` mono, uppercase
- ☐ **No logo on the opening frame.** The logo is a close, not an open
- ☐ **The claim is verifiable.** One fact, stated as fact
- ☐ **No countdown, no "before you scroll", no deadline.** `fake urgency` is on the banned list
- ☐ **Background is `#F8F6F0` warm off-white**, never pure white, never dark

Extract the true first frame yourself — the automatic sampler starts at `dur/(count+1)`, not at 0:

```powershell
ffmpeg -v error -ss 0 -i video_studio\output\<slug>\reel.mp4 -frames:v 1 -q:v 2 -y scratch\at-0.0.jpg
ffmpeg -v error -ss 1.5 -i video_studio\output\<slug>\reel.mp4 -frames:v 1 -q:v 2 -y scratch\at-1.5.jpg
```

---

## 2. Every Scene Transition

Read `storyboard.json` for the boundaries, then check each one.

| Scene | start | end | Sample at `start + 0.6` | At `end − 0.2` |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

- ☐ **New scene is fully opaque** 0.6 s in
- ☐ **Previous scene is fully gone** — no ghost, no double-exposure, no leftover children
- ☐ **Counter matches the scene you are in.** `2 / 7` while scene 2 is on screen. Never a static total
- ☐ **Eyebrow changes** if the beat changed. A repeated eyebrow across consecutive scenes reads as a bug
- ☐ **No layout jump** — content rises and fades, it does not slide across the frame
- ☐ **No element crosses the counter or collides with the top chrome**
- ☐ **First 0.42 s is not empty.** The fade-in starts at `start`, so `start + 0.2` must already show content

```powershell
# boundaries straight from the compiled storyboard
Select-String -Path video_studio\output\<slug>\storyboard.json -Pattern '"id"|"start"|"duration"'
```

---

## 3. Text Overflow

The most common silent defect. `hyperframes check` reports layout errors, not text that merely looks wrong.

- ☐ **Headline ≤ 3 lines** at 104 px (`hook`, `statement`) or 84 px (all others)
- ☐ **No 4th line** running into the subtext
- ☐ **No horizontal clipping.** Headline `max-width` is 960 px with an 80 px side margin — text that hits the edge is too long
- ☐ **Subtext ≤ 3 lines**, 42 px muted
- ☐ **`feature_card`: ≤ 3 bullets.** A 4th card pushes the stack past the bottom padding
- ☐ **`feature_card`: ≤ 24 words per card.** Break long bullets, do not shrink type
- ☐ **`metrics`: 2–3 tiles only.** A 4th wraps or clips at 1080 wide
- ☐ **Terminal lines fit.** `.terminal` is `overflow:hidden` at mono 32 px — long lines vanish without warning
- ☐ **No text on the grid.** Type sits on a white card, never directly on the blueprint substrate
- ☐ **Eyebrow never wraps** to a second line

If a headline is too long, **break the line**. Do not shrink the type — the type scale is the brand system.

---

## 4. Contrast

`hyperframes check` runs WCAG AA and reported **36/36 pass** on the reference Reel. Confirm it still says so in `render.log`, then check what the automated gate cannot see.

- ☐ `render.log` contains `36/36 text checks pass WCAG AA` (count may differ)
- ☐ `render.log` contains `Check passed`
- ☐ **Body text ≥ 4.5:1**, large type ≥ 3:1 — the gate enforces this; do not override
- ☐ **Muted copy `#666666` on `#F8F6F0` is legible** at 1080 wide, not just mathematically
- ☐ **Orange `#E05A36` eyebrow** reads on the off-white background, not just "passes"
- ☐ **Caption chip is `rgba(17,17,17,.90)` on `#fff`** — high contrast, check the edges
- ☐ **Terminal copy `#E8E8E8` on `#0B0B0C`** — the one dark surface in the system
- ☐ **Green `#16A34A` used only for machine truth** — verification chips, confirmed numbers, the logo border. Never decorative
- ☐ **Orange is ≤ 4% of frame area.** If a frame shows more orange than ink it is wrong
- ☐ **Ink dominates.** `#111111` around 10%, background ~85%

---

## 5. Captions and Safe Areas

### 5.1 Legibility

- ☐ **Every scene has burned-in captions.** Autoplay is silent by default
- ☐ **Caption ≥ 44 px**, 56 px preferred. Template is 42 px — check it reads
- ☐ **≤ 7 words per caption line**
- ☐ **No caption crosses the bottom chrome**
- ☐ **Caption chips do not overlap each other** or the headline
- ☐ **Caption text is not clipped** by the `max-width` of `#captions` (`left:70px; right:70px`)
- ☐ **Hard cuts, not fades.** Captions appear instantly — a faded caption reads late
- ☐ **No orphaned fragment.** A cue must be a complete readable line

### 5.2 Reading rate — **the defect the gate does not catch**

Hold time is `min(scene_span, len(text)/15)`. A cue is **text-bound** at exactly 15.00 chars/sec (healthy) or **scene-bound** above 15 (genuinely too fast). Read every cue in `captions.srt` and divide.

- ☐ **No scene-bound cue** — every cue sits at 15.00 chars/sec
- ☐ **No cue above 15.00 chars/sec**
- ☐ **No cue holding for less than 1.0 s**
- ☐ **No fragment from a broken sentence split** — see the `js.` defect below

Measured on the reference Reel — **4 of 11 cues are over budget**:

| Cue | chars | hold | chars/sec | |
|---|---|---|---|---|
| `cap-mechanism-0` | 118 | 6.950 s | **16.98** | over |
| `cap-no-webgl-3` | 44 | 1.200 s | **36.67** | **2.4× — unreadable** |
| `cap-proof-0` | 121 | 5.950 s | **20.34** | over |
| `cap-price-0` | 69 | 3.950 s | **17.47** | over |

Fix by shortening the narration or lengthening the scene. **Never fix it by raising `_read_speed()`** — that is the measurement, not the budget.

- ☐ **`captions.srt` splits are clean.** The splitter breaks on every `.`, so `Three.js` becomes `No Three.` + `js.` — **this defect is present in the shipped `captions.srt` as cue 7**, burned into the MP4, held for 0.2 s

### 5.3 Safe areas at 1080 × 1920

| Zone | Range | Check |
|---|---|---|
| Top reserved | y 0–110 | Chrome only |
| Primary safe | y 180–1560 | **Everything load-bearing** |
| Bottom reserved | y 1560–1920 | CTA, footer chrome |
| Side margin | x 80–1000 | Hard content boundary |
| Right rail | x 960–1080 | Nothing meaningful |

- ☐ No load-bearing text outside the primary safe zone
- ☐ Nothing critical in the right rail — platform UI can cover it
- ☐ Captions sit above y 1560 (`bottom:300px`, so they land around y 1450–1620)
- ☐ End-card CTA button is fully inside the frame

These are engineering conventions with headroom, **not** published Instagram specifications. Platform UI changes without notice.

---

## 6. Mobile-First Readability

Watch it on a phone, or shrink the preview. Desktop-previewing a vertical video is how unreadable type ships.

- ☐ **Headline readable at 1/4 scale** on a 6-inch screen
- ☐ **Body/subtext readable at 1/4 scale** — 30 px floor at 1080 wide
- ☐ **Chrome readable** — 18 px floor
- ☐ **One claim per frame.** The 9:16 format licenses a longer beat, not a denser frame
- ☐ **≤ 24 words per card**, ≤ 3 lines
- ☐ **Commands and numbers lead the frame** — the one thing all four audiences can use
- ☐ **Sound is optional.** Every frame is comprehensible muted

The target is four audiences at once — software engineers, founders, self-hosters, AI builders. A frame only one of them can read is a frame three of them scroll past.

---

## 7. Audio

> **The reference Reel has NO audio track.** `ffprobe` reports `nb_streams: 1`. Kokoro TTS is not installed, `--audio` was not passed, and `render --audio` currently raises `NameError` (`09_TROUBLESHOOTING.md` §3). Tick the "current state" column honestly.

| # | Check | Current state |
|---|---|---|
| ☐ | Audio track present | ☐ Expected · ☐ **Absent by design** · ☐ **Absent by failure** |
| ☐ | If present: `qa_report.md` shows `aac`, not `no audio` | |
| ☐ | If present: codec AAC, 48 kHz, 192 kbps | |
| ☐ | If present: integrated **−16 LUFS**, TP **−1.5 dBTP**, LRA 11 | |
| ☐ | Narration is intelligible on a phone speaker | |
| ☐ | Narration does not outrun the visuals — `render.log` shows the real provider and duration | |
| ☐ | Music ducks under narration, or there is no music | |
| ☐ | No clipping — waveform peaks below 0 dBFS | |
| ☐ | Audio does not simply stop — no abrupt cut before the end card | |
| ☐ | `render.log` shows no `[audio] no TTS provider available` | |
| ☐ | The ending is not cut mid-word | |

```powershell
ffprobe -v error -select_streams a -show_entries stream=codec_name,sample_rate,channels,bit_rate -of default=noprint_wrappers=1 video_studio\output\<slug>\reel.mp4
Select-String -Path video_studio\output\<slug>\render.log -Pattern '\[audio\]'
ffmpeg -v error -i video_studio\output\<slug>\reel.mp4 -af ebur128 -f null -   # measured LUFS
```

**Silence is a legitimate ship state.** A silent Reel with burned-in captions passes this section. A Reel that *should* have audio and does not is a failure — distinguish the two and say which it is.

---

## 8. Factual Accuracy

The fabrication ban. `02_BRAND_AND_CONTENT_STRATEGY.md` §9.2 lists all 12 items.

- ☐ **Every number traces to a named source** — `signhify.dpdns.org`, `data/brand.json`, or something observed
- ☐ **Pricing matches `02_BRAND_AND_CONTENT_STRATEGY.md` §1.4 exactly** — $5 / $50 / $100 / $200, credits 5 / 75 / 125 / 300
- ☐ **Frame counts, FPS ranges, credit values match §1.4.** No invented specs
- ☐ **No follower, like, view, save, or engagement number anywhere.** The Instagram profile was auth-walled — no data exists
- ☐ **No signups, revenue, MRR, churn, or customer count**
- ☐ **No team size or headcount**
- ☐ **No customer name, logo, or testimonial.** None exist
- ☐ **No uptime, SLA, or availability claim**
- ☐ **No speedup multiple** — "10× faster", "3× cheaper". No comparative benchmark was run
- ☐ **No competitor capability claim.** "Lovable is 2D only" is the site's own marketing assertion, unverified
- ☐ **No post-level performance claim** about any past Reel or carousel
- ☐ **`brief.json` → `sources[]` covers every non-obvious claim**
- ☐ **MIT ownership claim is true** — `100% MIT code ownership` is a published subhead line
- ☐ **Banned-phrase scan clean** — the build enforces this on `title`/`hook`/`cta`/scene copy, but **not** on `metrics[].v`, `metrics[].k`, `sources`, or `notes`

**"robust" is the trap.** It is on the 16-entry `avoid` list and it is ordinary engineering vocabulary.

---

## 9. Branding

- ☐ **Background is `#F8F6F0`** on every frame. One palette, varied layout — never varied hue
- ☐ **Blueprint grid present** — 64 px, `rgba(0,0,0,.035)`, full bleed
- ☐ **Orange `#E05A36` accent bar** at the very top
- ☐ **Chrome present on every body frame**: `© 2026` · `@SIGNHIFY.STUDIO` · `N / 7` counter
- ☐ **Chrome is monospace, 26 px, `#666666`**, letter-spaced, uppercase
- ☐ **Chrome never animates.** It is present from frame 1 and does not move
- ☐ **Eyebrow is mono, uppercase, `#E05A36`, above the headline** on every scene that has one
- ☐ **White cards `#FFFFFF`** with `rgba(0,0,0,.08)` border and 28 px radius, soft shadow
- ☐ **Fonts: Plus Jakarta Sans (headline) · Inter (body) · JetBrains Mono (chrome/code)**
- ☐ **No tofu glyphs.** Every character renders in the intended family. A missing glyph is a silent visual failure
- ☐ **No duplicate glyph or marker.** Check the eyebrow specifically — a CSS `content` pseudo-element colliding with the brief's own marker produced a tofu box **plus** a duplicate asterisk on the first pass
- ☐ **Green `#16A34A` only for machine truth** — verified chips, confirmed numbers, the logo border
- ☐ **Logo is green and stays green.** Never recolour it to match the orange accent
- ☐ **Logo appears only on the end card** (and the avatar). Never inside a scene
- ☐ **Counter tracks the active scene**, not the total. The first pass rendered a meaningless static `07`
- ☐ **End card holds to the final frame** — `tl.set(ec, {opacity:1}, TOTAL - 0.02)`

A viewer who screenshots any single frame still gets the handle. That is the whole point of the persistent chrome.

---

## 10. Packaging

| Artifact | File | Check |
|---|---|---|
| Video | `reel.mp4` | ☐ Present · ☐ 3–90 s · ☐ non-zero |
| Cover | `cover.jpg` | ☐ Present · ☐ **a clean hero frame, not a mid-transition mush** · ☐ `t = 0.9 s` sits inside scene 1 |
| Caption | `caption.txt` | ☐ Hook · ☐ Title · ☐ Hashtags · ☐ CTA · ☐ Zero banned phrases |
| Captions | `captions.srt` | ☐ Valid SRT · ☐ Cue numbering contiguous · ☐ Timestamps monotonic · ☐ §5.2 reading rate |
| Manifest | `asset_manifest.json` | ☐ `spec` matches the actual file · ☐ **`publishing.enabled` is `false`** |
| Storyboard | `storyboard.json` | ☐ `total` matches `ffprobe` duration |
| Brief | `brief.json` | ☐ Round-trips the input |

- ☐ **Hashtags are the intended set.** Currently hardcoded at `publish.py:15`: `#signhifystudio #vibecoding #ai3d #webdev #buildinpublic #startupindia`
- ☐ **CTA is one action.** Two CTAs is zero CTAs
- ☐ **`publishing.enabled` is still `false`.** Shipping is a manual, human decision
- ☐ **No token, key, or secret in any artifact**

---

## 11. Platform Compliance

| # | Requirement | Value | Check |
|---|---|---|---|
| ☐ | Aspect | **9:16** vertical | ☐ |
| ☐ | Dimensions | **1080 × 1920** recommended (min 540 × 960) | ☐ |
| ☐ | Frame rate | **24–60 fps** (24 / 25 / 30 / 50 / 60) | ☐ |
| ☐ | Duration | **3–90 s** | ☐ |
| ☐ | Video codec | **H.264** | ☐ |
| ☐ | Pixel format | `yuv420p` | ☐ |
| ☐ | Audio codec | **AAC** (when an audio track exists) | ☐ |
| ☐ | Container | MP4, `+faststart` | ☐ |
| ☐ | Colour | bt709 primaries / transfer / matrix | ☐ |

```powershell
ffprobe -v error -print_format json -show_streams -show_format video_studio\output\<slug>\reel.mp4
```

Reference artifact, measured 2026-10-11:

| Field | Value |
|---|---|
| `width` × `height` | 1080 × 1920 |
| `display_aspect_ratio` | 9:16 |
| `codec_name` / `profile` | h264 / Constrained Baseline, level 40 |
| `pix_fmt` | yuv420p |
| `r_frame_rate` | 30/1 |
| `nb_frames` | 1215 (= 40.5 × 30, exact) |
| `duration` | 40.500000 |
| `nb_streams` | **1 — no audio track** |
| `size` | 2,213,568 bytes |
| video `bit_rate` | 436,043 bps (draft) |
| colour | bt709 / bt709 / bt709 |

Additional platform facts:

- ☐ **Reels cannot appear in carousels**
- ☐ **Alt text is not supported** on Reels or Stories — do not rely on it for accessibility
- ☐ **`media_type` reads back as `VIDEO` after publish**, not `REELS`. Any verification asserting `== "REELS"` will fail
- ☐ **50 published posts / rolling 24 h** is the design limit — Meta's docs conflict (100 vs 50). Assume 50

---

## 12. Final Sign-Off

Only now. Every box above is ticked, or explicitly waived with a reason.

```powershell
ffprobe -v error -select_streams v:0 `
  -show_entries stream=width,height,r_frame_rate,codec_name,nb_frames `
  -of default=noprint_wrappers=1 video_studio\output\<slug>\reel.mp4
```

- ☐ Every JPEG in `qa_frames/` was opened and inspected
- ☐ Scene-bound transitions were sampled at `start + 0.6` and `end − 0.2`
- ☐ Caption reading rate checked cue by cue against `captions.srt`
- ☐ Every claim traced to a source
- ☐ Zero banned phrases, including in `metrics` labels
- ☐ Audio state is known and stated: present, absent-by-design, or absent-by-failure
- ☐ `asset_manifest.json` → `publishing.enabled` is `false`
- ☐ Published at `standard` or `high`, not `draft`
- ☐ **Repair attempts on any defect ≤ 2.** Beyond that, escalate to a human — `06_PRODUCTION_RUNBOOK.md` §8.3
- ☐ Second reviewer has looked at it, or the waiver is written down

**Reviewer:** ________________  **Date:** ____________

**Verdict:** ☐ Production-ready  ☐ Rework  ☐ Escalate

**Waivers (what was not checked, and why):**

---

## 13. Known Defects in the Reference Reel

Documented so nobody re-discovers them as new. Full detail: `03_SYSTEM_ARCHITECTURE.md` §11, `09_TROUBLESHOOTING.md`.

| # | Defect | Status | Impact |
|---|---|---|---|
| 1 | `captions.srt` cue 7 is `js.` held 0.2 s — the splitter breaks on the `.` in `Three.js` | **Open** | Visible in the MP4 |
| 2 | 4 of 11 cues exceed 15 chars/sec; worst is 36.67 ch/s | **Open** | Unreadable at arm's length |
| 3 | No audio track — Kokoro not installed, `--audio` not passed | **Open by design** | Legitimate ship state |
| 4 | `render --audio` raises `NameError: WORK_DIR` | **Open** | Blocks narration |
| 5 | 18 `timed_element_missing_clip_class` advisories | **Open, cosmetic** | Studio/linter ergonomics only; render is correct |
| 6 | 7 `nested_structure_needs_subcomposition` infos | **Open, cosmetic** | Studio timeline ergonomics only |
| 7 | 2 `text_occluded` infos on chrome under the end card at t = 38.25 s | **Expected** | The end card deliberately covers the chrome |
| 8 | `qa_report.md` prints `container_valid: no video stream` on success | **Open, cosmetic** | Detail string is wrong; the check logic is right |
| 9 | `brief.json` `target_duration: 38` vs actual `40.5` | **Open, cosmetic** | Field is never read |
| 10 | `--quality standard` / `high` never run | **Unverified** | Wall-clock and bitrate unknown |

---

*Compiled 2026-10-11 from `data/brand.json`, `02_BRAND_AND_CONTENT_STRATEGY.md`, `ffprobe` output on the reference artifact, and `ffprobe` / Meta Graph API constraints for Instagram Reels. Every threshold in this checklist is either a published platform requirement, a studio convention marked as such, or a measured value from the reference render — nothing is estimated.*