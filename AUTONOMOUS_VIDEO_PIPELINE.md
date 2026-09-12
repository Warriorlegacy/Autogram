# Autonomous Short-Form Video Generation & Publishing Pipeline
### Technical Specification & Implementation Guide for AI Agents

---

## 1. System Overview & Architecture

This document specifies the architecture, configuration, and code required to deploy a zero-marginal-cost, fully autonomous short-form video generation and distribution pipeline for YouTube Shorts and Instagram Reels.

```
┌──────────────────────────────────────────────────────────┐
│                      Task Scheduler                      │
│                (APScheduler / Cron / n8n)                │
└─────────────────────────────┬────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│                 1. LLM Script Generation                 │
│      Ollama (Local Qwen 2.5 / Llama 3.1) [Unlimited]     │
│                 or Groq Free Cloud API                   │
└─────────────────────────────┬────────────────────────────┘
                              │ Script, Title, Tags, Captions
                              ▼
┌──────────────────────────────────────────────────────────┐
│             2. Video Synthesis Engine                    │
│             (MoneyPrinterTurbo API :8080)                │
│  ├─ Voiceover:  Edge-TTS (Microsoft Neural Voices)       │
│  ├─ Visuals:    Pexels Stock Video API (Free)            │
│  ├─ Subtitles:  Edge Timestamp Parser / faster-whisper   │
│  └─ Assembly:   FFmpeg (9:16 vertical render)            │
└─────────────────────────────┬────────────────────────────┘
                              │ Rendered MP4 Video
                              ▼
┌──────────────────────────────────────────────────────────┐
│            3. Public Object Storage Staging              │
│       Cloudflare R2 / AWS S3 / Catbox (Presigned URL)    │
└──────────────────────┬──────────────────────┬────────────┘
                       │                      │
                       ▼                      ▼
┌───────────────────────────────┐  ┌───────────────────────┐
│     4a. YouTube Data API v3   │  │ 4b. Meta Graph API    │
│       (Upload to Shorts)      │  │ (Publish to IG Reels) │
└───────────────────────────────┘  └───────────────────────┘
```

---

## 2. LLM Engine Options (Free & Unlimited Tiers)

| Provider | Cost | Daily Limits | Integration Type | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **Ollama (Self-Hosted)** | **$0.00** | **Unlimited** (Zero rate limits) | Local HTTP (`:11434`) | Production autonomy, infinite generations, zero external dependencies. |
| **Groq Cloud** | **$0.00** | 14,400 requests/day | OpenAI-compatible REST | Ultra-fast inference (500+ tok/s) on cloud without GPU load. |
| **Google Gemini API** | **$0.00** | 1,500 requests/day | Native REST / SDK | High reasoning quality within standard free quotas. |

### Recommended Local Setup (Ollama)
```bash
# Install Ollama and pull qwen2.5:7b
ollama run qwen2.5:7b
```

---

## 3. MoneyPrinterTurbo (MPT) Headless Configuration

MoneyPrinterTurbo executes video assembly by delegating script analysis, audio synthesis, footage acquisition, and subtitle burning to FFmpeg.

### Configuration (`config.toml`)

```toml
[app]
listen_host = "0.0.0.0"
listen_port = 8080
endpoint = "http://127.0.0.1:8080"

# --- LLM CONFIGURATION (OLLAMA) ---
llm_provider = "ollama"
ollama_base_url = "http://127.0.0.1:11434"
ollama_model_name = "qwen2.5:7b"

# --- STOCK MEDIA CONFIGURATION ($0) ---
video_source = "pexels"
pexels_api_keys = ["YOUR_PEXELS_API_KEY"]

# --- VOICE & SUBTITLES ($0) ---
voice_name = "en-US-ChristopherNeural"
subtitle_provider = "edge"
```

### Launch Headless Server

```bash
# Windows
start_mpt.bat

# Or manual terminal
cd /d D:\MoneyPrinterTurbo
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 1
```

---

## 4. Complete Orchestration Pipeline (`pipeline_runner.py`)

This standalone Python engine coordinates script generation, video rendering, cloud staging, and cross-platform publishing.

```bash
python pipeline_runner.py --now
```

---

## 5. Production Constraints & Operational Guardrails

1. **Rendering Load:** Limit FFmpeg rendering to 2 concurrent tasks per 8 CPU cores to prevent out-of-memory crashes.
2. **YouTube API Quota:** 10,000 units/day default allocation (1,600 units per upload = max 6 uploads/day).
3. **Artifact Retention:** Rendered MP4s older than 48 hours are automatically purged to prevent disk saturation.
