"""
In-House Instagram Auto-DM & Comment-Reply Automation Engine (src/instagram/dm_automator.py).
Replaces third-party SaaS (ManyChat) with an autonomous, zero-cost, self-hosted system.
Monitors posts for viral triggers ("FOSS", "WEB", "MUSIC", "SWARM", "PROMPT", "BLUEPRINT"),
posts randomized public replies to boost reach, and sends automated Private Reply DMs
with high-converting blueprints and templates directly via Meta Graph API.
"""

import json
import logging
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

from src.config import settings
from src.db.database import db

logger = logging.getLogger(__name__)

STATE_FILE = Path(__file__).parent.parent.parent / "data" / "dm_automation_state.json"
FOLLOW_GATE_FILE = Path(__file__).parent.parent.parent / "data" / "dm_follow_gate.json"

# Public links to the Signhify Studio blueprint (accessible without GitHub auth)
BLUEPRINT_MD_URL = "https://autogram-dashboard.onrender.com/BLUEPRINT.md"
BLUEPRINT_PDF_URL = "https://autogram-dashboard.onrender.com/BLUEPRINT.pdf"

# NOTE (platform limit, stated honestly): Meta's Instagram Graph API exposes no
# followers-list endpoint, so silent follow-verification is impossible via the
# official API. The enforceable gate is this two-step claim flow: first trigger
# comment -> public "follow + reply FOLLOWED" ask (link withheld, user marked
# PENDING); follow-up claim comment -> blueprint DM delivered + PENDING cleared.

# Trigger keywords and matching rules
TRIGGERS = {
    "FOSS": {
        "patterns": [r"\bfoss\b", r"\bself-host(ed|ing)?\b", r"\bdocker\b", r"\bsetup\b"],
        "public_replies": [
            "Just sent the full Docker setup & GitHub link to your DMs! 🚀",
            "Check your DMs! The 1-click self-host blueprint is on the way ⚡",
            "Sent! Enjoy the free alternative. Let me know if you hit any setup snags 🛠️",
            "DM sent! Stop paying SaaS bills and start shipping 📦"
        ],
        "dm_text": (
            "Hey builder! 👋\n\n"
            "Here is the complete self-hosting blueprint and 1-line Docker setup from our recent breakdown:\n\n"
            "📦 GitHub Master Vault: https://github.com/signhify/open-source-vault\n"
            "⚡ 1-Line Commands & Configs: https://github.com/signhify/open-source-vault/blob/main/quickstart.md\n\n"
            "Stop paying $100s/mo in SaaS bills. Follow @signhify.studio for daily battle-tested open source tools! 🚀"
        )
    },
    "PROMPT": {
        "patterns": [r"\bprompt\b", r"\bcode\b", r"\bfilm\b", r"\bvideo\b", r"\bmegaprompt\b", r"\bchatgpt\b", r"\bsecret\b"],
        "public_replies": [
            "Sent you the AI video-as-code prompt pack! Check DMs 🎬",
            "Check your DMs! Promptbase video prompt pack is on the way ⚡",
            "Just sent the complete prompt code & variables to your DMs! 🔥",
            "DM sent! Replace [INPUT_DATA] before running 🧠"
        ],
        "dm_text": (
            "Here is the AI video-as-code prompt pack! 🎬\n\n"
            "⚡ Master Prompt Vault & Store: https://promptbase.shop\n"
            "🧠 GitHub Prompt Vault: https://github.com/signhify/prompt-vault\n"
            "📋 Tested On: GPT-4o, Claude 3.5 Sonnet, Midjourney, Kling, Runway\n\n"
            "Make sure to replace scene variables before generating.\n"
            "Follow @promptbase.shop_ for daily tested AI prompt architectures! ⚡"
        )
    },
    "BLUEPRINT": {
        "patterns": [r"\bblueprint\b", r"\bvault\b", r"\bstudio\b", r"\bportfolio\b", r"\bservices\b", r"\bsystem\b", r"\bworks\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' in your DMs to instantly unlock the Blueprint & Prompt Pack ⚡",
            "Almost yours! Hit Follow on @signhify.studio and reply 'DONE' — the full blueprint & PDF lands in your DMs 📩",
            "This blueprint is for our community 🔐 Follow @signhify.studio + reply 'DONE' and check your inbox!"
        ],
        "delivery_replies": [
            "Verified! 🚀 Sent the full Signhify Studio AI Engineering Blueprint & Master Vault to your DMs! Check your inbox 📥",
            "You're in! 🔓 Check your DMs for the full Signhify Studio Blueprint + PDF guide ⚡",
            "Sent to your DMs! Enjoy the free AI engineering architecture & master prompts 🧠"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! 👋\n\n"
            "Here is how to unlock the SIGNHIFY STUDIO AI Engineering Blueprint & Master Prompt Vault:\n\n"
            "🔒 Step 1: Follow @signhify.studio (this blueprint is reserved for our community)\n"
            "👉 Step 2: Reply with the word 'DONE' or 'FOLLOWED' right here (or comment on the post)\n\n"
            "The moment you reply, your private blueprint link & PDF will instantly unlock! ⚡"
        ),
        "dm_text": (
            "Welcome to the inner circle! 🔓\n\n"
            "Here is the complete SIGNHIFY STUDIO Blueprint — our works, portfolio, "
            "verified websites, $0 autonomous stack and copy-paste master prompt pack:\n\n"
            "📕 Full Blueprint (read online): " + BLUEPRINT_MD_URL + "\n"
            "📄 Blueprint PDF: " + BLUEPRINT_PDF_URL + "\n\n"
            "Built by Signhify Studio — FULL AI ENGINEERING STUDIO.\n"
            "We engineer autonomous multi-agent pipelines, production RAG & fine-tuned LLMs, and zero-marginal-cost content systems.\n"
            "🌐 Website: https://signhify.studio\n"
            "⚡ App: https://autogram-ai.vercel.app\n"
            "💼 Hire Us / Inquiries: partner@signhify.studio"
        )
    },
    "WEB": {
        "patterns": [r"\bweb\b", r"\b3d\b", r"\bsite\b", r"\bwebsite\b"],
        "public_replies": [
            "Just sent you the 1-hour 3D website build blueprint! Check your DMs 🚀",
            "Check your DMs! 3D site template & guide is on its way ⚡",
            "Sent! Build something that stands out from flat templates 🛠️",
            "DM sent! The 3D scroll-film template is waiting for you 🎨"
        ],
        "dm_text": (
            "Hey builder! 👋\n\n"
            "Here is the 1-hour 3D website build blueprint and custom film site templates:\n\n"
            "🌐 33 Interactive 3D Templates: https://promptbase.shop/templates\n"
            "🎬 Custom 3D Film Sites & Portfolio: https://promptbase.shop/work\n\n"
            "1-Hour Build Breakdown:\n"
            "1. Clone the WebGL / Three.js 3D scene starter\n"
            "2. Connect interactive scroll-driven camera motion\n"
            "3. Deploy responsive 3D web experience in under 60 minutes\n\n"
            "Build something that stands out from flat templates! Follow @promptbase.shop_ for daily 3D builds ⚡"
        )
    },
    "MUSIC": {
        "patterns": [r"\bmusic\b", r"\bsuno\b", r"\bacestep\b", r"\bace\b", r"\bsong\b"],
        "public_replies": [
            "Sent! The complete local ACE-Step 1.5 setup guide is in your DMs 🎵",
            "Check your DMs! Run Suno-quality music on your laptop for $0 🎧",
            "DM sent! Enjoy unlimited local AI music generation 🚀"
        ],
        "dm_text": (
            "Here is the complete local ACE-Step 1.5 setup guide! 🎵\n\n"
            "Run Suno-quality AI music generation on your laptop for $0:\n\n"
            "📦 GitHub Repository: https://github.com/ace-step/ACE-Step-1.5\n\n"
            "Step-by-step local setup:\n"
            "1. git clone https://github.com/ace-step/ACE-Step-1.5\n"
            "2. cd ACE-Step-1.5\n"
            "3. uv sync\n"
            "4. python app.py --port 7860\n"
            "5. Open http://localhost:7860\n\n"
            "Enjoy unlimited local AI music generation with zero subscription fees! 🚀"
        )
    },
    "SWARM": {
        "patterns": [r"\bsend\b", r"\bswarm\b", r"\bagents?\b", r"\boutbound\b", r"\bgtm\b"],
        "public_replies": [
            "Just sent the 4-agent outbound swarm architecture to your DMs! 🤖",
            "Check your DMs! The autonomous lead gen & dispatch blueprint is sent ⚡",
            "DM sent! Stop doing manual outreach in 2026 📦"
        ],
        "dm_text": (
            "Here is the 4-agent outbound swarm architecture and autonomous dispatch guide! 🤖\n\n"
            "Stop doing manual outreach in 2026. Deploy autonomous lead gen and multi-channel dispatch:\n\n"
            "📦 AutoGTM Swarm Architecture: https://github.com/Warriorlegacy/autogtm\n"
            "⚡ Autonomous Dispatch Guide: https://github.com/Warriorlegacy/autogtm/blob/main/docs/ARCHITECTURE.md\n\n"
            "4-Agent Swarm Overview:\n"
            "1. Scout Agent: Snipes public intent signals (Reddit, HN, local directories)\n"
            "2. Verifier Agent: 5-tier waterfall socket validation\n"
            "3. Auditor Agent: Headless site speed, conversion leak & tech stack audit\n"
            "4. Dispatcher Agent: Cascading zero-cost SMTP/REST relays & contact form automation\n\n"
            "Deploy autonomous outbound pipelines at zero marginal cost! 🚀"
        )
    },
    "CLIENT": {
        "patterns": [r"\bclient\b", r"\bagency\b", r"\bhunt\b", r"\bleads?\b", r"\boutsource\b"],
        "public_replies": [
            "Sent! The complete $100k/mo client acquisition system is in your DMs 💼",
            "Check your DMs! B2B lead generation & client fulfillment blueprint is sent ⚡",
            "DM sent! Scale your client hunt without hiring SDRs 🚀"
        ],
        "dm_text": (
            "Here is the complete B2B client acquisition blueprint & fulfillment pipeline! 💼\n\n"
            "We automated 100% of our outbound hunting, qualification, and fulfillment:\n\n"
            "🌐 Signhify Studio Client Portal: https://signhify.studio\n"
            "⚡ Book Architecture Call: https://calendly.com/signhify/ai-architecture\n"
            "📦 AutoGTM Fulfillment API: https://github.com/Warriorlegacy/AutoGTM\n\n"
            "1. Automated lead harvesting & DNS verification\n"
            "2. Personalized multi-channel outreach (Gmail SMTP / REST relays)\n"
            "3. Real-time credit ledger & automated Stripe fulfillment\n\n"
            "Follow @signhify.studio for daily high-ticket client systems! 🚀"
        )
    },
    "CAREER": {
        "patterns": [r"\bcareer\b", r"\bjob\b", r"\bhiring\b", r"\bremote\b", r"\binterview\b"],
        "public_replies": [
            "Sent! The $80,000+ remote AI engineering blueprint is in your DMs 🎯",
            "Check your DMs! Portfolio architectures & ATS bypass blueprints sent ⚡",
            "DM sent! Real production repos beat cold applications every time 💻"
        ],
        "dm_text": (
            "Here is the $80,000+ remote AI engineering blueprint & portfolio repo! 🎯\n\n"
            "Cold applications are broken. Here is how we showcase production systems:\n\n"
            "💻 Master GitHub Repositories: https://github.com/Warriorlegacy\n"
            "⚡ Taubin Algebraic Regression Suite: https://github.com/Warriorlegacy/taubin-fit\n"
            "📄 Candidate Portfolio: https://github.com/Warriorlegacy/portfolio\n\n"
            "Key Principles:\n"
            "1. Build verifiable artifacts (100% test passing, live CI/CD)\n"
            "2. Automate ATS pre-filling via Playwright with zero drift\n"
            "3. Showcase real production code, not generic tutorial projects\n\n"
            "Good luck with your search! 🚀"
        )
    },
    "FACTORY": {
        "patterns": [r"\bfactory\b", r"\bcontent\b", r"\bautomation\b", r"\breels?\b", r"\bvideo\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' to unlock the 12 GitHub Repos & Content Factory sheet ⚡",
            "Almost yours! Hit Follow on @signhify.studio & reply 'DONE' — the full 12-repo sheet lands in your DMs 📩",
            "This factory stack is reserved for our community 🔐 Follow @signhify.studio + reply 'DONE' to get it!"
        ],
        "delivery_replies": [
            "Verified! 🚀 Sent the full 12 GitHub Repos & AI Content Factory Cheat Sheet to your DMs! Check inbox 📥",
            "You're in! 🔓 Check your DMs for the 12 open-source repo links & setup commands ⚡",
            "Sent to your DMs! Enjoy the free autonomous AI content factory stack 🎬"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! 🎬\n\n"
            "Here is how to unlock the 12 GitHub Repos & AI Content Factory Cheat Sheet:\n\n"
            "🔒 Step 1: Follow @signhify.studio (this resource is reserved for our engineering community)\n"
            "👉 Step 2: Reply with the word 'DONE' or 'FOLLOWED' right here in DMs\n\n"
            "The moment you reply, your clickable GitHub links sheet & setup guide will unlock instantly! ⚡"
        ),
        "dm_text": (
            "Welcome to the AI Content Factory! 🔓🎬\n\n"
            "Here is the verified 12 Open-Source GitHub Repos Master Cheat Sheet:\n\n"
            "1. Remotion: https://github.com/remotion-dev/remotion\n"
            "2. HyperFrames: https://github.com/heygen-com/hyperframes\n"
            "3. Kokoro-82M: https://github.com/hexgrad/kokoro\n"
            "4. Whisper.cpp: https://github.com/ggerganov/whisper.cpp\n"
            "5. OpenMontage: https://github.com/calesthio/OpenMontage\n"
            "6. Bark TTS: https://github.com/suno-ai/bark\n"
            "7. Stable Diffusion WebUI: https://github.com/AUTOMATIC1111/stable-diffusion-webui\n"
            "8. Coqui TTS: https://github.com/coqui-ai/TTS\n"
            "9. FFmpeg: https://github.com/FFmpeg/FFmpeg\n"
            "10. AutoGTM Swarm: https://github.com/Warriorlegacy/AutoGTM\n"
            "11. Playwright: https://github.com/microsoft/playwright\n"
            "12. Autogram Engine: https://github.com/signhify/autogram\n\n"
            "📦 Full Guide: https://signhify.dpdns.org/factory-guide\n\n"
            "Build once, publish autonomously! Follow @signhify.studio for daily open-source AI tools! 🚀"
        )
    },
    "RESTORE": {
        "patterns": [r"\brestore\b", r"\bdatabase\b", r"\bproduction\b", r"\brollback\b", r"\bpanic\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' to unlock the terminal recovery script ⚡",
            "Almost yours! Follow @signhify.studio & reply 'DONE' — the Claude rollback guide lands in your DMs 📩",
            "This script is for our community 🔐 Follow @signhify.studio + reply 'DONE' to get the full script!"
        ],
        "delivery_replies": [
            "Verified! 🚀 Sent the terminal DB rollback script & Claude skill to your DMs! Check inbox 📥",
            "You're in! 🔓 Check your DMs for the schema recovery guide ⚡"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! 🚨\n\n"
            "Here is how to unlock the Terminal Database Recovery Script & Claude Skill:\n\n"
            "🔒 Step 1: Follow @signhify.studio (this script is reserved for our engineering community)\n"
            "👉 Step 2: Reply with 'DONE' or 'FOLLOWED' right here in DMs\n\n"
            "The moment you reply, your private GitHub repo link will unlock instantly! ⚡"
        ),
        "dm_text": (
            "Here is the exact Terminal Database Recovery Script & Claude Skill! 🚨\n\n"
            "```bash\n"
            "# 1. Diff migration cache against last 40 merged PRs\n"
            "git log --merges -n 40 --name-only --oneline | grep -E 'migrations/|prisma/|schema.sql'\n\n"
            "# 2. Run Claude Code autonomous schema reconstructor\n"
            "claude \"Audit git diff for schema regressions, reconstruct lost tables from migration cache, and output dry-run SQL rollback\"\n"
            "```\n\n"
            "🛠️ GitHub Master Repo: https://github.com/stars/signhify/lists/production-recovery\n"
            "📜 Full Rollback Guide: https://signhify.dpdns.org/restore-guide\n\n"
            "Stop stressing over fatal terminal errors. Follow @signhify.studio for daily developer tools! 🚀"
        )
    },
    "HYPER": {
        "patterns": [r"\bhyper\b", r"\bhyperframes\b", r"\bpremiere\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' to unlock the HyperFrames repo & Claude video prompt ⚡",
            "Almost yours! Hit Follow on @signhify.studio & reply 'DONE' — the code-to-video starter kit lands in your DMs 📩",
            "Reserved for our engineering community 🔐 Follow @signhify.studio + reply 'DONE' to grab the setup!"
        ],
        "delivery_replies": [
            "Verified! 🚀 Sent the HyperFrames repo + Claude video prompt to your DMs! Check inbox 📥",
            "You're in! 🔓 Check your DMs for the code-to-video workflow & setup prompt ⚡"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! 🎬\n\n"
            "Here is how to unlock the HyperFrames + Claude Code Video Workflow:\n\n"
            "🔒 Step 1: Follow @signhify.studio (reserved for our creator & dev community)\n"
            "👉 Step 2: Reply with 'DONE' or 'FOLLOWED' right here in DMs\n\n"
            "The moment you reply, your private repo link and Claude prompt will unlock! ⚡"
        ),
        "dm_text": (
            "Here is the open-source HyperFrames + Claude Video Generation Stack! 🎬\n\n"
            "📦 Core Repository: https://github.com/heygen-com/hyperframes\n\n"
            "⚡ 1-Line Terminal Render:\n"
            "npx --yes hyperframes render --project ./my-reel --output reel.mp4\n\n"
            "🤖 Claude Setup Prompt:\n"
            "\"Act as a motion designer. Write an index.html file utilizing GSAP 3.12 and Tailwind CSS adhering strictly to a 1080x1920 vertical canvas. Divide into 4 sequential scene blocks timed to a 30s voiceover track.\"\n\n"
            "📂 Video Boilerplate Guide: https://signhify.dpdns.org/hyperframes-guide\n\n"
            "Follow @signhify.studio for more code-rendered video stacks! 🚀"
        )
    },
    "PIPELINE": {
        "patterns": [r"\bpipeline\b", r"\barchitect(ure)?\b", r"\bschematic\b", r"\binfrastructure\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' to unlock the Full Architecture Schematic & API Guide ⚡",
            "Almost yours! Follow @signhify.studio & reply 'DONE' — the full pipeline integration schematic lands in your DMs 📩",
            "This schematic is for our engineering community 🔐 Follow @signhify.studio + reply 'DONE' to get it!"
        ],
        "delivery_replies": [
            "Verified! 🚀 Sent the full Autogram Architecture Schematic & Integration Guide to your DMs! Check inbox 📥",
            "You're in! 🔓 Check your DMs for the 4-stage pipeline blueprint & Docker configs ⚡"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! ⚡\n\n"
            "Here is how to unlock the Autogram Zero-Touch Architecture Schematic & API Integration Guide:\n\n"
            "🔒 Step 1: Follow @signhify.studio (this blueprint is reserved for our community)\n"
            "👉 Step 2: Reply with 'DONE' or 'FOLLOWED' right here in DMs\n\n"
            "The moment you reply, your full high-res schematic and GitHub code will unlock! 🚀"
        ),
        "dm_text": (
            "Welcome to the Architecture Breakdown! ⚡📐\n\n"
            "Here is the complete Autogram Zero-Touch Video Production Pipeline:\n\n"
            "📐 4-Stage Engine Breakdown:\n"
            "1. Ingestion & Scoring: RSS feeds + Hacker News Algolia API + 6-Pillar Rotation\n"
            "2. Content Synthesis: Multi-LLM fallback chain (Claude 3.5 Sonnet / GPT-4o / Gemini 1.5 Pro)\n"
            "3. Audio & Motion Engine: Kokoro-82M ONNX + Whisper word alignment + Remotion/HyperFrames 60fps\n"
            "4. Zero-Touch Publish: Meta Graph API v26.0 Container Flow + Automated Comment-to-DM Engine\n\n"
            "📄 High-Res System Architecture Blueprint: https://signhify.dpdns.org/architecture\n"
            "📦 GitHub Core Pipeline: https://github.com/signhify/autogram\n\n"
            "Built by Signhify Studio. Follow @signhify.studio for daily production-grade AI architectures! 🚀"
        )
    },
    "CUT": {
        "patterns": [r"\bcut\b", r"\bmontage\b", r"\beditor\b", r"\bopenmontage\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' to unlock the OpenMontage prompt-to-cut repo ⚡",
            "Almost yours! Follow @signhify.studio & reply 'DONE' — the auto-editor script lands in your DMs 📩",
            "Reserved for our creator community 🔐 Follow @signhify.studio + reply 'DONE' to get the full script!"
        ],
        "delivery_replies": [
            "Verified! 🚀 Sent the OpenMontage auto-editor repo & setup command to your DMs! Check inbox 📥",
            "You're in! 🔓 Check your DMs for the prompt-to-cut setup guide ⚡"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! 🎬\n\n"
            "Here is how to unlock the OpenMontage Prompt-to-Cut Engine & Setup Guide:\n\n"
            "🔒 Step 1: Follow @signhify.studio (reserved for our creator & dev community)\n"
            "👉 Step 2: Reply with 'DONE' or 'FOLLOWED' right here in DMs\n\n"
            "The moment you reply, your private GitHub repo link and setup guide will unlock! ⚡"
        ),
        "dm_text": (
            "Here is the OpenMontage Prompt-to-Cut Engine! 🎬\n\n"
            "📦 GitHub Repository: https://github.com/calesthio/OpenMontage\n\n"
            "⚡ 1-Line Execution:\n"
            "python openmontage.py --input podcast.mp4 --vad --auto-crop --subtitles\n\n"
            "📜 Setup & Config Guide: https://signhify.dpdns.org/openmontage-guide\n\n"
            "Follow @signhify.studio for more open-source AI video engines! 🚀"
        )
    },
    "VOICE": {
        "patterns": [r"\bvoice\b", r"\bkokoro\b", r"\bclone\b", r"\bspeech\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' to unlock the $0 Local Kokoro-82M Voice Clone repo ⚡",
            "Almost yours! Follow @signhify.studio & reply 'DONE' — the zero-cost voice clone setup lands in your DMs 📩",
            "Reserved for our audio & AI community 🔐 Follow @signhify.studio + reply 'DONE' to grab the setup!"
        ],
        "delivery_replies": [
            "Verified! 🚀 Sent the Kokoro-82M ONNX voice clone repo & setup commands to your DMs! Check inbox 📥",
            "You're in! 🔓 Check your DMs for the local voice clone setup guide ⚡"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! 🎙️\n\n"
            "Here is how to unlock the $0 Local Voice Clone (Kokoro-82M ONNX) Setup Guide:\n\n"
            "🔒 Step 1: Follow @signhify.studio (this setup is reserved for our community)\n"
            "👉 Step 2: Reply with 'DONE' or 'FOLLOWED' right here in DMs\n\n"
            "The moment you reply, your local setup script and ONNX models will unlock instantly! ⚡"
        ),
        "dm_text": (
            "Here is the $0 Local Kokoro-82M ONNX Voice Clone Engine! 🎙️⚡\n\n"
            "Stop paying $50+/mo in ElevenLabs subscriptions. Run broadcast-grade speech locally for $0:\n\n"
            "📦 GitHub Repository: https://github.com/hexgrad/kokoro\n"
            "⚡ Kokoro ONNX Wrapper: https://github.com/thewh1teagle/kokoro-onnx\n\n"
            "🚀 1-Line Local Run:\n"
            "pip install kokoro-onnx soundfile\n"
            "python -c \"import kokoro_onnx; kokoro_onnx.speak('Autogram running locally at zero cost.')\"\n\n"
            "📜 Full Studio Audio Mastering Guide: https://signhify.dpdns.org/voice-guide\n\n"
            "Follow @signhify.studio for daily open-source AI breakthroughs! 🚀"
        )
    },
    "DOCS": {
        "patterns": [r"\bdocs?\b", r"\bdocumentar(y|ies)\b", r"\bremotion\b", r"\blip\s*sync\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' to unlock the 30-Minute AI Documentary Engine ⚡",
            "Almost yours! Follow @signhify.studio & reply 'DONE' — the Remotion documentary code lands in your DMs 📩",
            "Reserved for our video dev community 🔐 Follow @signhify.studio + reply 'DONE' to get the full engine!"
        ],
        "delivery_replies": [
            "Verified! 🚀 Sent the Remotion Documentary Code & 5-Layer Stack to your DMs! Check inbox 📥",
            "You're in! 🔓 Check your DMs for the full documentary pipeline repo ⚡"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! 🎬\n\n"
            "Here is how to unlock the 30-Minute AI Documentary Engine & Remotion Boilerplate:\n\n"
            "🔒 Step 1: Follow @signhify.studio (reserved for our developer community)\n"
            "👉 Step 2: Reply with 'DONE' or 'FOLLOWED' right here in DMs\n\n"
            "The moment you reply, your private Remotion repo and automation scripts will unlock! ⚡"
        ),
        "dm_text": (
            "Here is the 30-Minute AI Documentary Production Engine! 🎬🏛️\n\n"
            "Zero manual editing. Code full multi-scene documentaries in React:\n\n"
            "📦 Remotion Core Engine: https://github.com/remotion-dev/remotion\n"
            "⚡ Signhify Doc-Engine Boilerplate: https://github.com/signhify/doc-engine\n\n"
            "🛠️ The 5-Layer Stack:\n"
            "1. Kokoro-82M: Broadcast narration synthesis\n"
            "2. Whisper.cpp: Per-word timestamp alignment\n"
            "3. Rhubarb: Phoneme lip-sync mouth animation\n"
            "4. Remotion: 60fps code-rendered visual composition\n"
            "5. FFmpeg: EBU R128 loudness mastering & hardware encoding\n\n"
            "📜 Full Documentary Production Architecture: https://signhify.dpdns.org/doc-guide\n\n"
            "Follow @signhify.studio for more code-rendered video workflows! 🚀"
        )
    },
    "DIWALI": {
        "patterns": [r"\bdiwali\b", r"\bfestive\b", r"\blakshmi\b", r"\bgift\b", r"\bvault\b"],
        "gated": True,
        "gate_replies": [
            "🔒 Sent you a DM! Follow @signhify.studio & reply 'DONE' to unlock the Diwali Open-Source Master Vault 🪔⚡",
            "Happy Diwali! Hit Follow on @signhify.studio & reply 'DONE' — the full production repo vault lands in your DMs 📩",
            "This festive vault is for our builder community 🔐 Follow @signhify.studio + reply 'DONE' to grab it! 🪔"
        ],
        "delivery_replies": [
            "Verified! 🪔 Sent the full Signhify Studio Diwali Open-Source Master Vault to your DMs! Check inbox 📥",
            "Happy Diwali! 🔓 Check your DMs for the complete open-source repo starter pack & prompt vault ⚡",
            "Sent to your DMs! Enjoy the free open-source AI engineering suite 🪔🚀"
        ],
        "claim_patterns": [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"],
        "gate_dm_text": (
            "Hey {username}! 🪔 Happy Diwali!\n\n"
            "Here is how to unlock the SIGNHIFY STUDIO Diwali Open-Source Production Vault & Master Starter Pack:\n\n"
            "🔒 Step 1: Follow @signhify.studio (this festive vault is reserved for our engineering community)\n"
            "👉 Step 2: Reply with 'DONE' or 'FOLLOWED' right here in DMs\n\n"
            "The moment you reply, your complete open-source repo links and architecture blueprints will unlock instantly! ⚡"
        ),
        "dm_text": (
            "Happy Diwali from all of us at Signhify Studio! 🪔✨\n\n"
            "May your latency stay under 40ms, your GPUs never hit OOM, and your tokens cost $0!\n\n"
            "Here is your complete Diwali Open-Source Production Vault:\n\n"
            "📦 1. Remotion Video-as-Code Engine: https://github.com/remotion-dev/remotion\n"
            "⚡ 2. Kokoro-82M Local Voice Engine: https://github.com/hexgrad/kokoro\n"
            "🎬 3. HyperFrames 60fps Code Motion: https://github.com/heygen-com/hyperframes\n"
            "🤖 4. AutoGTM 4-Agent Lead Swarm: https://github.com/Warriorlegacy/AutoGTM\n"
            "✂️ 5. OpenMontage AI Video Cutter: https://github.com/calesthio/OpenMontage\n"
            "📜 6. Signhify Master Architecture Guide: https://signhify.dpdns.org/architecture\n\n"
            "Build once, automate everything, and ship fearlessly in 2026! Follow @signhify.studio for daily open source engineering! 🚀"
        )
    }
}

FOLLOW_CLAIM_PATTERNS = [r"\bfollowed\b", r"\bfollowing\b", r"\bdone\b", r"\bfollow\s*back\b", r"✅"]


class InstagramDMAutomator:
    """
    Autonomous Instagram Comment-Reply and Private Reply (Auto-DM) engine.
    Uses Meta's official Instagram Graph API:
    - POST /{comment-id}/replies  (Public reply)
    - POST /{ig-user-id}/messages  (Private Reply DM to commenter)
    """

    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{settings.meta_api_version}"
        self.user_id = settings.ig_user_id
        self.token = settings.ig_access_token
        self.dry_run = settings.dry_run
        self.send_initial_gate_dm = True
        self.state_file = STATE_FILE
        self._init_state()

    def _init_state(self):
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(json.dumps({"processed_comments": {}}, indent=2), encoding="utf-8")

    def _load_gate(self) -> dict:
        """Loads pending follow-gate claims {username_lower: {requested_at, delivered}}."""
        try:
            if FOLLOW_GATE_FILE.exists():
                return json.loads(FOLLOW_GATE_FILE.read_text(encoding="utf-8")).get("pending", {})
        except Exception:
            pass
        return {}

    def _save_gate(self, pending: dict) -> None:
        try:
            FOLLOW_GATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            FOLLOW_GATE_FILE.write_text(json.dumps({"pending": pending}, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to persist follow-gate state: {e}")

    def is_follower_verified(self, username: str) -> bool:
        """Returns True if the user has already completed the follow gate."""
        key = (username or "").lower().strip()
        if not key:
            return False
        # 1. Check in-memory/JSON gate file
        entry = self._load_gate().get(key, {})
        if entry.get("delivered"):
            return True
        # 2. Check DB verified_followers table
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM verified_followers WHERE username = ?", (key,))
                if cursor.fetchone():
                    return True
        except Exception:
            pass
        return False

    def mark_gate_pending(self, username: str, keyword: str = "BLUEPRINT") -> None:
        pending = self._load_gate()
        key = (username or "").lower().strip()
        if key and (key not in pending or pending[key].get("delivered")):
            pending[key] = {"requested_at": time.time(), "delivered": False, "keyword": keyword}
            self._save_gate(pending)

    def is_gate_pending(self, username: str) -> bool:
        entry = self._load_gate().get((username or "").lower().strip(), {})
        return bool(entry) and not entry.get("delivered")

    def mark_gate_delivered(self, username: str) -> None:
        pending = self._load_gate()
        key = (username or "").lower().strip()
        if key in pending:
            pending[key]["delivered"] = True
            self._save_gate(pending)
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO verified_followers (username, source) VALUES (?, ?)",
                    (key, "auto_dm_claim")
                )
                conn.commit()
        except Exception as e:
            logger.debug(f"DB verified_followers update skipped: {e}")

    @staticmethod
    def is_follow_claim(text: str) -> bool:
        text_lower = (text or "").lower()
        return any(re.search(p, text_lower) for p in FOLLOW_CLAIM_PATTERNS)

    def load_processed_comments(self) -> set[str]:
        """Loads set of previously handled comment IDs to prevent duplicate DMs."""
        processed = set()
        # 1. Check database if available
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT comment_id FROM auto_dm_log")
                for row in cursor.fetchall():
                    processed.add(row[0])
        except Exception:
            pass

        # 2. Check JSON state file fallback
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                processed.update(data.get("processed_comments", {}).keys())
            except Exception:
                pass

        return processed

    def record_processed_comment(
        self,
        comment_id: str,
        media_id: str,
        username: str,
        comment_text: str,
        keyword: str,
        public_reply_id: str,
        dm_status: str
    ):
        """Persists processed comment to DB and state file."""
        # 1. DB persistence
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO auto_dm_log 
                (comment_id, media_id, username, comment_text, keyword, public_reply_id, dm_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (comment_id, media_id, username, comment_text, keyword, public_reply_id, dm_status))
                conn.commit()
        except Exception as e:
            logger.debug(f"DB auto_dm_log persistence skipped: {e}")

        # 2. JSON state file persistence
        try:
            data = {"processed_comments": {}}
            if self.state_file.exists():
                try:
                    data = json.loads(self.state_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            data["processed_comments"][comment_id] = {
                "media_id": media_id,
                "username": username,
                "keyword": keyword,
                "public_reply_id": public_reply_id,
                "dm_status": dm_status,
                "timestamp": time.time()
            }
            self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to update auto_dm_state.json: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on processed comments and DMs from DB or state file."""
        stats = {
            "total_dms_sent": 0,
            "total_comments_handled": 0,
            "by_keyword": {k: 0 for k in TRIGGERS.keys()},
            "recent_actions": []
        }
        # Try DB first
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM auto_dm_log WHERE dm_status = 'DM_SENT'")
                stats["total_dms_sent"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM auto_dm_log")
                stats["total_comments_handled"] = cursor.fetchone()[0]

                cursor.execute("SELECT keyword, COUNT(*) FROM auto_dm_log GROUP BY keyword")
                for kw, cnt in cursor.fetchall():
                    if kw:
                        stats["by_keyword"][kw] = cnt

                cursor.execute("""
                SELECT comment_id, media_id, username, comment_text, keyword, dm_status, created_at 
                FROM auto_dm_log ORDER BY created_at DESC LIMIT 15
                """)
                for row in cursor.fetchall():
                    stats["recent_actions"].append({
                        "comment_id": row[0],
                        "media_id": row[1],
                        "username": row[2],
                        "comment_text": row[3],
                        "keyword": row[4],
                        "dm_status": row[5],
                        "timestamp": str(row[6])
                    })
                return stats
        except Exception as e:
            logger.debug(f"DB read for DM stats failed, falling back to JSON: {e}")

        # JSON fallback
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                processed = data.get("processed_comments", {})
                stats["total_comments_handled"] = len(processed)
                for cid, item in processed.items():
                    if item.get("dm_status") == "DM_SENT":
                        stats["total_dms_sent"] += 1
                    kw = item.get("keyword")
                    if kw in stats["by_keyword"]:
                        stats["by_keyword"][kw] += 1
                    elif kw:
                        stats["by_keyword"][kw] = 1
                    stats["recent_actions"].append({
                        "comment_id": cid,
                        "media_id": item.get("media_id"),
                        "username": item.get("username"),
                        "comment_text": "",
                        "keyword": kw,
                        "dm_status": item.get("dm_status"),
                        "timestamp": item.get("timestamp")
                    })
                stats["recent_actions"] = stats["recent_actions"][-15:]
            except Exception:
                pass

        return stats

    def fetch_recent_media_ids(self, limit: int = 5) -> List[str]:
        """Fetches recent published media IDs for @signhify.studio."""
        if self.dry_run or not self.token or not self.user_id:
            logger.info("[DRY-RUN] Simulating media fetch for recent posts.")
            return ["mock_media_12345"]

        url = f"{self.base_url}/{self.user_id}/media"
        params = {
            "fields": "id,caption,timestamp",
            "limit": limit,
            "access_token": self.token
        }
        try:
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            items = resp.json().get("data", [])
            return [item["id"] for item in items if "id" in item]
        except Exception as e:
            logger.error(f"Failed to fetch recent Instagram media: {e}")
            return []

    def fetch_comments_for_media(self, media_id: str) -> List[Dict[str, Any]]:
        """Fetches top-level comments on a given Instagram media post."""
        if self.dry_run or str(media_id).startswith("mock"):
            logger.info(f"[DRY-RUN] Simulating comments fetch for media {media_id}")
            ts = int(time.time() * 1000) % 10000
            return [
                {"id": f"sim_c_{ts}_foss", "text": "FOSS please!", "username": "builder_alex"},
                {"id": f"sim_c_{ts}_web", "text": "Can you send the 3D website template?", "username": "web_dev_pro"},
                {"id": f"sim_c_{ts}_music", "text": "Send the Suno music AI guide!", "username": "beat_maker"},
                {"id": f"sim_c_{ts}_swarm", "text": "SWARM please! Need the outbound agents", "username": "growth_hacker"},
                {"id": f"sim_c_{ts}_prompt", "text": "Can you send the PROMPT code?", "username": "prompt_engineer_99"}
            ]

        url = f"{self.base_url}/{media_id}/comments"
        params = {
            "fields": "id,text,username,timestamp",
            "access_token": self.token
        }
        try:
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            logger.error(f"Failed to fetch comments for media {media_id}: {e}")
            return []

    def send_public_reply(self, comment_id: str, message: str) -> str:
        """Publishes a randomized public comment reply to boost algorithmic reach."""
        if self.dry_run or str(comment_id).startswith("sim_"):
            sim_reply_id = f"mock_reply_{int(time.time()*1000)%100000}"
            logger.info(f"[DRY-RUN] Simulated public comment reply to {comment_id}: '{message}' (ID: {sim_reply_id})")
            return sim_reply_id

        url = f"{self.base_url}/{comment_id}/replies"
        data = {
            "message": message,
            "access_token": self.token
        }
        resp = requests.post(url, data=data, timeout=20)
        resp.raise_for_status()
        reply_id = resp.json().get("id", "")
        logger.info(f"Published public reply to comment {comment_id}: Reply ID = {reply_id}")
        return reply_id

    def send_private_dm(self, comment_id: str, message_text: str) -> bool:
        """
        Sends a private DM to the commenter using Meta's Private Replies API:
        POST /{ig-user-id}/messages with recipient: {"comment_id": comment_id}
        """
        if self.dry_run or str(comment_id).startswith("sim_"):
            logger.info(f"[DRY-RUN] Simulated sending private DM for comment {comment_id}")
            return True

        url = f"{self.base_url}/{self.user_id}/messages"
        payload = {
            "recipient": {
                "comment_id": comment_id
            },
            "message": {
                "text": message_text
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "access_token": self.token
        }
        try:
            resp = requests.post(url, params=params, json=payload, headers=headers, timeout=25)
            if resp.status_code == 200:
                logger.info(f"Successfully sent automated private DM for comment {comment_id}!")
                return True
            else:
                logger.warning(f"Private DM returned status {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending private DM for comment {comment_id}: {e}")
            return False

    def match_keyword(self, comment_text: str) -> Optional[str]:
        """Matches comment text against configured trigger patterns (FOSS, PROMPT, BLUEPRINT, WEB, MUSIC, SWARM)."""
        text_lower = comment_text.lower().strip()
        for trigger_key, cfg in TRIGGERS.items():
            for pattern in cfg["patterns"]:
                if re.search(pattern, text_lower):
                    return trigger_key
        return None

    def process_comment(self, comment: Dict[str, Any], media_id: str) -> Optional[Dict[str, Any]]:
        """Evaluates a single comment and executes auto-reply + DM if matched."""
        comment_id = comment.get("id")
        text = comment.get("text", "")
        username = comment.get("username", "user")

        if not comment_id:
            return None

        # Follow-claim fast path: a pending user saying FOLLOWED/DONE unlocks
        # the gated resource even though the claim carries no trigger keyword.
        if self.is_follow_claim(text) and self.is_gate_pending(username):
            pending_entry = self._load_gate().get((username or "").lower().strip(), {})
            kw = pending_entry.get("keyword", "BLUEPRINT")
            if kw not in TRIGGERS:
                kw = "BLUEPRINT"
            return self._deliver_gated_blueprint(
                comment_id, media_id, username, text, kw
            )

        matched_key = self.match_keyword(text)
        if not matched_key:
            return None  # No action needed for generic comments

        cfg = TRIGGERS[matched_key]
        logger.info(f"Trigger matched! Comment '{text}' by @{username} matched keyword [{matched_key}].")

        # Follow-gated premium assets (BLUEPRINT / FACTORY / HYPER / CUT / VOICE / DOCS / PIPELINE):
        # withhold the link until the user claims the follow. Dual-Touchpoint: initial gate DM + public ask.
        # Once verified or claimed -> deliver links + clear.
        if cfg.get("gated"):
            if self.is_follower_verified(username) or self.is_follow_claim(text) or self.is_gate_pending(username):
                return self._deliver_gated_blueprint(
                    comment_id, media_id, username, text, matched_key
                )
            gate_reply = random.choice(cfg["gate_replies"])
            public_reply_id = "sim_reply"
            try:
                public_reply_id = self.send_public_reply(comment_id, gate_reply)
            except Exception as e:
                logger.warning(f"Could not send gate reply to comment {comment_id}: {e}")

            # Send initial private DM with follow instructions (links strictly withheld)
            if getattr(self, "send_initial_gate_dm", True):
                gate_dm_tmpl = cfg.get("gate_dm_text", "")
                if gate_dm_tmpl:
                    gate_dm = gate_dm_tmpl.replace("{username}", username)
                    try:
                        self.send_private_dm(comment_id, gate_dm)
                    except Exception as e:
                        logger.debug(f"Could not send initial gate DM for comment {comment_id}: {e}")

            self.mark_gate_pending(username, matched_key)
            self.record_processed_comment(
                comment_id=comment_id, media_id=media_id, username=username,
                comment_text=text, keyword=matched_key,
                public_reply_id=public_reply_id, dm_status="GATE_PENDING"
            )
            return {
                "comment_id": comment_id, "username": username, "keyword": matched_key,
                "public_reply_id": public_reply_id, "dm_status": "GATE_PENDING"
            }

        public_reply_text = random.choice(cfg["public_replies"])
        dm_text = cfg["dm_text"]

        # 1. Post randomized public reply
        public_reply_id = "sim_reply"
        try:
            public_reply_id = self.send_public_reply(comment_id, public_reply_text)
        except Exception as e:
            logger.warning(f"Could not send public reply to comment {comment_id}: {e}")

        # 2. Brief typing pause to respect Meta humanization rules
        time.sleep(0.05 if self.dry_run else random.uniform(1.0, 2.5))

        # 3. Send private DM
        dm_sent = False
        try:
            dm_sent = self.send_private_dm(comment_id, dm_text)
        except Exception as e:
            logger.warning(f"Could not send private DM for comment {comment_id}: {e}")

        status_str = "DM_SENT" if dm_sent else "PUBLIC_ONLY"
        self.record_processed_comment(
            comment_id=comment_id,
            media_id=media_id,
            username=username,
            comment_text=text,
            keyword=matched_key,
            public_reply_id=public_reply_id,
            dm_status=status_str
        )

        return {
            "comment_id": comment_id,
            "username": username,
            "keyword": matched_key,
            "public_reply_id": public_reply_id,
            "dm_status": status_str
        }

    def _deliver_gated_blueprint(
        self, comment_id: str, media_id: str, username: str, text: str, keyword: str
    ) -> Dict[str, Any]:
        """DMs the blueprint links to a follow-claimed user and clears PENDING."""
        cfg = TRIGGERS[keyword]
        replies_pool = cfg.get("delivery_replies") or cfg.get("public_replies") or cfg["gate_replies"]
        public_reply_id = "sim_reply"
        try:
            public_reply_id = self.send_public_reply(comment_id, random.choice(replies_pool))
        except Exception as e:
            logger.warning(f"Could not send claim acknowledgement to comment {comment_id}: {e}")

        dm_sent = False
        try:
            dm_sent = self.send_private_dm(comment_id, cfg["dm_text"])
        except Exception as e:
            logger.warning(f"Could not send blueprint DM for comment {comment_id}: {e}")

        if dm_sent:
            self.mark_gate_delivered(username)
        status_str = "DM_SENT" if dm_sent else "PUBLIC_ONLY"
        self.record_processed_comment(
            comment_id=comment_id, media_id=media_id, username=username,
            comment_text=text, keyword=keyword,
            public_reply_id=public_reply_id, dm_status=status_str
        )
        return {
            "comment_id": comment_id, "username": username, "keyword": keyword,
            "public_reply_id": public_reply_id, "dm_status": status_str
        }

    def scan_and_automate(self, limit_posts: int = 5) -> Dict[str, Any]:
        """
        Scans recent Instagram posts, discovers new comments, and executes auto-DMs.
        Returns detailed summary of actions taken.
        """
        logger.info("==================================================")
        logger.info(" Starting Instagram Auto-DM & Comment-Reply Scan")
        logger.info("==================================================")

        processed_ids = self.load_processed_comments()
        media_ids = self.fetch_recent_media_ids(limit=limit_posts)
        
        actions_taken = []
        total_comments_checked = 0

        for mid in media_ids:
            comments = self.fetch_comments_for_media(mid)
            for c in comments:
                cid = c.get("id")
                if not cid or cid in processed_ids:
                    continue  # Already processed

                total_comments_checked += 1
                result = self.process_comment(c, media_id=mid)
                if result:
                    actions_taken.append(result)
                    processed_ids.add(cid)

        summary = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "media_scanned": len(media_ids),
            "comments_checked": total_comments_checked,
            "actions_executed": len(actions_taken),
            "details": actions_taken
        }

        logger.info(
            f"Auto-DM Scan Finished: {len(actions_taken)} automated responses dispatched "
            f"across {total_comments_checked} new comments."
        )
        return summary


dm_automator = InstagramDMAutomator()
