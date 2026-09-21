# Signhify 60s Autonomous Reel Pipeline

Authoritative workflow: `.github/workflows/daily-video.yml` — 3 slots/day IST (10:30/14:30/20:30 = 05:00/09:00/15:00 UTC).
`daily_reels.yml` is deprecated (no schedule, no publish).

## Flow
Topic discovery (`script60.discover_topic`: live fetcher → curated fallback) → 7 hooks scored → 60s script
(125–155 words, ends `Follow Signhify.studio for more.`) → fact gate (rejects fake stats; rotates topic) →
scene JSON (9 scenes, timing from narration) → edge-tts → stretch/pad to exactly 60s → phrase SRT →
procedural music bed (FFmpeg, royalty-safe) ducked under speech → HyperFrames 60s composition (mandatory,
theme A–E rotation) → Remotion `SignhifyReel` (1800f/30fps/1080×1920, captions, watermark, end-card) →
FFmpeg fallback if Remotion CLI unavailable → QA gate (60s, 1080×1920, H264+AAC, 30fps) →
public URL (Supabase → engine cascade) → Reel publish (3 retries) → same MP4 to Story (best-effort,
`UNAVAILABLE_OR_FAILED` never fails the Reel) → memory record → artifacts.

## Pipecat
Full pipecat-ai (torch/WebRTC) is too heavy for batch Actions renders. `audio60.py` implements the same
frame stages (TextFrame → TTS → AudioRawFrame → timing) lightweight. Swap `synthesize()` internals for
pipecat services only if realtime voice is ever needed.

## Zero-cost
No Pexels key required (removed hard gate). TTS: edge-tts → espeak-ng → offline synth. Music: procedural.
Visuals: HyperFrames procedural CSS/GSAP. No GPU required.

## Run
- Dry run: `python scripts/run_60s_reel.py --slot morning --dry-run --topic "Pipecat voice pipelines"`
- Live: `python scripts/run_60s_reel.py --slot night` (needs IG_* secrets + owner license)
- Manual dispatch exposes: topic, pillar, dry_run, force_template, publish_reel, publish_story.

## Idempotency
Slot key `YYYY-MM-DD-morning|afternoon|night` in `output/<day>/<slot>/metadata.json` + content-memory
`slot_key`. Completed slots exit `SKIPPED_DUPLICATE`.
