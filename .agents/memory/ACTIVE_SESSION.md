# ACTIVE SESSION STATE LEDGER

## 1. PROJECT OBJECTIVE
- Build and operate an automated, zero-cost Instagram Reels generation and publishing engine.
- Maintain a zero-token persistent memory system for AI pair-programming agents (Antigravity, OpenCode, Claude Code).

## 2. CURRENT STAGE & STATUS
- **Stage**: Multimodal Video Generation + Kinetic Highlight Subtitles + Agent Memory Persistence.
- **Specification Document**: [`AI_AGENT_MASTER_SPECIFICATION.md`](file:///d:/Autogram/AI_AGENT_MASTER_SPECIFICATION.md) created and validated.
- **AST Architecture Map**: Generated at [`.agents/memory/ARCHITECTURE_MAP.md`](file:///d:/Autogram/.agents/memory/ARCHITECTURE_MAP.md).
- **Video Engine**: Edge-TTS (voice), Faster-Whisper (int8 word timestamps), Pollinations.ai FLUX (9:16 background), ASS kinetic subtitles, FFmpeg zoompan.
- **Hugging Face Token**: Configured in `.env` (`HUGGINGFACE_API_KEY` & `HF_TOKEN`) for ZeroGPU video spaces & model inference.

## 3. KEY ARTIFACTS & ACTIVE FILES
- [`AI_AGENT_MASTER_SPECIFICATION.md`](file:///d:/Autogram/AI_AGENT_MASTER_SPECIFICATION.md): Complete architecture, code, and roadmap.
- [`scripts/generate_repo_map.py`](file:///d:/Autogram/scripts/generate_repo_map.py): AST symbol compressor for zero-token context loading.
- [`.agents/memory/ARCHITECTURE_MAP.md`](file:///d:/Autogram/.agents/memory/ARCHITECTURE_MAP.md): Compressed codebase structural map (< 10 KB).
- [`.agents/workflows/start.md`](file:///d:/Autogram/.agents/workflows/start.md): Session startup protocol for AI agents.

## 4. IMMEDIATE NEXT ACTIONS FOR RESUMING AGENT
1. **DO NOT** run recursive file searches or directory listings.
2. Read this file (`ACTIVE_SESSION.md`) and check [`ARCHITECTURE_MAP.md`](file:///d:/Autogram/.agents/memory/ARCHITECTURE_MAP.md) for symbol definitions.
3. Review pending user tasks before taking actions.

## 5. SESSION UPDATE — 2026-09-13: REELS SPEC IMPLEMENTED
- **Implemented** `scripts/pipeline_reels.py` (spec §3.2 API: generate_reel_content/synthesize_speech/download_visual/to_ass_time/compile_word_level_ass/render_ffmpeg/execute_reels_pipeline). Delegates to `src.content.generator` (OpenRouter :free) + `src.content.image_generator` (Pollinations 9:16) — no duplicated provider logic.
- **Implemented** `scripts/storage_helper.py` (spec §3.3: Supabase upload, engine-cascade + transfer.sh fallback) and `scripts/publish_instagram.py` (spec §3.4: delegates to `src.instagram.publisher.publish_reel`).
- **Infra:** `requirements.txt` += openai/faster-whisper/supabase/gradio_client; `src/config.py` += SUPABASE_URL/KEY, REELS_VOICE; `.env.example` += OPENROUTER/HF/SUPABASE/spec-alias keys; new `Dockerfile` (ffmpeg+libass); new `.github/workflows/daily_reels.yml` (13:00 UTC); `workspace/` + gitignore.
- **Verified:** `tests/test_reels_spec.py` (3 passed) + `test_reel_pipeline.py` + `test_orchestrator.py` (12 passed). Repo map regenerated.
- **Next:** set repo secrets (OPENROUTER_API_KEY, SUPABASE_URL/KEY, INSTAGRAM_BUSINESS_ACCOUNT_ID, META_GRAPH_ACCESS_TOKEN), then Actions → Daily Instagram Reels Autopilot → Run workflow for first automated post.

## 6. SESSION UPDATE — 2026-09-13: FIRST LIVE REEL PUBLISHED
- **Live post:** https://www.instagram.com/reel/DdOT4htDwn-/ (media 17902027863354024, VIDEO, @signhify.studio, topic: Ripgrep vs Grep, 29-word Nemotron narration, 1080x1920/30fps/26s, 57 karaoke ASS events, hosted on catbox).
- **Fixes found live:** (a) spec's OpenRouter :free slugs (glm-5.3-flash, gemini-2.0-flash-exp, llama-3.3-70b) now 404 — FREE_MODELS rotated to nemotron-3-super-120b / nex-n2.5-pro / gemma-4-31b (verified via /models); same rotation applied to `src/content/generator.py`. (b) `scripts/publish_instagram.py` env-alias bug: `setdefault(..., '')` shadowed real `.env` values and forced a mock publish — now only bridges non-empty spec vars. First publish attempt returned mock ID; re-ran live after fix and verified via Graph API.
- **Ops notes:** Pollinations returned 576x1024 (upscaled to 1080x1920 by filter — fine); pip installed faster-whisper + gradio_client; IG quota was 17/25 before post.
- **Next:** wire first-comment automation + schedule daily_reels.yml secrets for hands-free daily posts.

## 7. SESSION UPDATE — 2026-09-13: 10X CRON + GEMINI KEY ROTATION
- **Gemini key rotated** in `.env` (verified live: 200, 50 models). GitHub secret `GEMINI_API_KEY` must be updated by hand for Actions runs.
- **New `.github/workflows/reels-10x.yml`:** 10 UTC crons (07:30–22:00 IST) → pipeline_reels → catbox/Supabase → publish. Concurrency queue (no double-posts), pip + Whisper caches, deterministic slot topic rotation (21/21 unique topics over 3 days, verified offline), artifacts per run. Also listens to `repository_dispatch` (publish-reel) so cron-job.org can trigger it as backup — no cron-job.org jobs created (needs a fresh GitHub PAT; hardcoded one in setup_cronjob_org.py untrusted).
- **Retired** `daily_reels.yml` schedule → manual-only (was an 11th daily post).
- **Watchouts logged:** Meta ~25 publishes/24h is SHARED with daily-video/post/story workflows — pause them or quota guard will skip slots. Minutes ≈1800/mo vs 2000 free.

## 8. SESSION UPDATE — 2026-09-13: SCALED TO 1 REEL/DAY
- `daily_reels.yml` schedule re-enabled (1 cron: 13:00 UTC = 18:30 IST). `reels-10x.yml` schedule parked (manual + dispatch only) — uncomment to scale back up. YAML re-validated. Minutes now ≈180/mo; quota pressure gone.
