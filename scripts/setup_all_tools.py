"""
Multi-Repository Setup & Hub Installer for Autogram & AI Content Factory
Clones and sets up all 12+ open-source content creation toolkits.
"""

import os
import sys
import subprocess
from pathlib import Path

TOOLS_DIR = Path("D:/Autogram/tools")
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

REPOSITORIES = [
    # Category 1: Research
    ("social-media-research-skills", "https://github.com/ScrapeCreators/social-media-research-skills.git", "Research viral hooks from competitor channels"),
    ("local-deep-research", "https://github.com/LearningCircuit/local-deep-research.git", "Local deep research agent for any technical topic"),
    
    # Category 2: Create
    ("hyperframes", "https://github.com/heygen-com/hyperframes.git", "Code-to-video programmatic engine (HTML + GSAP)"),
    ("OpenCreator", "https://github.com/krillinai/OpenCreator.git", "Full script, image, and voice studio"),
    ("flux", "https://github.com/black-forest-labs/flux.git", "FLUX.1/2 high-contrast image generation"),
    ("VoiceStudio", "https://github.com/debpalash/VoiceStudio.git", "Local voice cloning & dubbing studio"),
    ("ACE-Step-1.5", "https://github.com/ace-step/ACE-Step-1.5.git", "Text-to-original-music synthesis model"),
    ("podcastfy", "https://github.com/souzatharsis/podcastfy.git", "Article/PDF to conversational AI podcast generator"),
    
    # Category 3: Edit
    ("OpenMontage", "https://github.com/calesthio/OpenMontage.git", "Claude Code full video production crew (prompt to cut)"),
    ("short-video-factory", "https://github.com/YILS-LIN/short-video-factory.git", "Batch short-form video assembly with subs"),
    ("AI-Youtube-Shorts-Generator", "https://github.com/Anil-matcha/AI-Youtube-Shorts-Generator.git", "Automated YouTube Shorts generator"),
    
    # Category 4: Publish
    ("social-media-agent", "https://github.com/langchain-ai/social-media-agent.git", "Autonomous multi-platform post scheduler"),
    
    # Category 5: Code-Rendered Motion Graphics & Cartoons
    ("ClaudeAnimationBase", "https://github.com/JohnHeibel/ClaudeAnimationBase.git", "p5.js 2D cartoon animation kit with 31 rigged emotions"),
    ("lemo-opuscar", "https://github.com/lemomo-ai/lemo-opuscar.git", "59 code-rendered film styles for Claude Code"),
    ("pdoom-video", "https://github.com/mexicat/pdoom-video.git", "Three.js word-synced 3D kinetic typography video engine")
]

print("=====================================================================", flush=True)
print("🚀 CLONING & INITIALIZING ALL AI CONTENT FACTORY REPOSITORIES", flush=True)
print("=====================================================================", flush=True)

results = {}

for name, url, desc in REPOSITORIES:
    dest = TOOLS_DIR / name
    print(f"\n[*] Processing '{name}' ({desc})...", flush=True)
    if dest.exists() and (dest / ".git").exists():
        print(f"    -> Already installed at {dest}", flush=True)
        results[name] = "INSTALLED"
        continue
    
    print(f"    -> Cloning shallow from {url}...", flush=True)
    try:
        proc = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(dest)],
            capture_output=True, text=True, timeout=120
        )
        if proc.returncode == 0:
            print(f"    -> SUCCESS: Installed to {dest}", flush=True)
            results[name] = "SUCCESS"
        else:
            print(f"    -> FAILED: {proc.stderr.strip()[:160]}", flush=True)
            results[name] = f"FAIL: {proc.stderr.strip()[:80]}"
    except Exception as e:
        print(f"    -> ERROR: {e}", flush=True)
        results[name] = f"ERR: {e}"

# Generate unified hub manifest
manifest_lines = [
    "# 🛠️ Autogram AI Content Factory Tools Hub",
    "",
    "All repositories installed locally under `D:/Autogram/tools/`:",
    "",
    "| Repository | Category | Status | Capabilities |",
    "|---|---|---|---|"
]

for name, url, desc in REPOSITORIES:
    status = results.get(name, "UNKNOWN")
    manifest_lines.append(f"| [`{name}`]({url}) | {desc.split()[0]} | `{status}` | {desc} |")

manifest_path = TOOLS_DIR / "README.md"
manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
print("\n[OK] Generated Tools Hub README at:", manifest_path, flush=True)

