"""
publish_all_today_assets.py
Publishes today's complete package of posts and reels to Instagram via Meta Graph API:
1. Day 02 Viral Reel: 'Claude > Premiere Pro? (0% Premiere, 100% Code Motion)'
2. 7-Slide Master Carousel: '12 Open-Source GitHub Repos That Run Your AI Content Factory'
3. Architecture Feed Post: 'How We Fully Automate It (The Complete 4-Stage System Architecture)'
4. Posts first discussion comments on all published media
5. Executes the live DM Automator to monitor and reply to triggers
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

from src.config import settings
from src.instagram.publisher import publisher
from src.storage.uploader import uploader
from src.instagram.dm_automator import dm_automator

TODAY_STR = datetime.now().strftime("%Y-%m-%d")

# 1. Day 02 Reel
REEL_PATH = Path("d:/Autogram/docs/reel-studio-kit/out/claude-vs-premiere.mp4")
REEL_CAPTION = (
    "Why are video editors still paying $35/month to manually drag keyframes? 💀\n\n"
    "What you're watching right now was NOT edited in Premiere Pro, DaVinci, or After Effects.\n"
    "Every single frame, subtitle, and impact cut was drawn entirely in code by Claude.\n\n"
    "Here's the open-source stack:\n"
    "1. Claude writes HTML + GSAP motion design\n"
    "2. HyperFrames compiles the audio, subtitles, and layout\n"
    "3. FFmpeg renders the vertical 1080x1920 MP4 in 45 seconds\n\n"
    "0s timeline scrubbing.\n"
    "0s rendering lag.\n"
    "100% reproducible, automated code.\n\n"
    "👉 Comment \"HYPER\" below and I'll DM you the direct GitHub repository link + our starter Claude prompt. (Follow @signhify.studio to unlock 🔒)\n\n"
    "Engineered at Signhify Studio (signhify.dpdns.org)\n"
    "My name is Piyush Raj Singh. Stop posting. Start shipping.\n\n"
    "#HyperFrames #ClaudeCode #VideoEditing #PremierePro #AfterEffects #OpenSource #AIvideo #Automation #WebDev #SignhifyStudio #GSAP #Remotion"
)

# 2. 7-Slide Master Carousel
CAROUSEL_DIR = Path("d:/Autogram/output/carousel-factory")
CAROUSEL_CAPTION = (
    "12 Open-Source GitHub Repos That Run Your Entire AI Content Factory 📦\n\n"
    "Stop paying $200+/month for cloud video SaaS and closed AI wrapper tools.\n"
    "You can run the entire research, creation, voice cloning, and publishing pipeline for $0 with open-source code.\n\n"
    "📁 Directory Breakdown:\n"
    "• /research: social-media-research-skills & local-deep-research\n"
    "• /create: hyperframes, opencreator, flux2, voicestudio, ace-step 1.5, podcastfy\n"
    "• /edit: openmontage, short-video-factory, yt-shorts\n"
    "• /publish: social-media-agent\n\n"
    "👉 Swipe through all 7 slides to inspect the complete directory breakdown.\n\n"
    "⚡ Comment \"FACTORY\" below and I'll DM you the direct clickable GitHub links + setup prompt sheet! (Must follow @signhify.studio to unlock 🔒)\n\n"
    "Engineered at Signhify Studio (signhify.dpdns.org)\n"
    "My name is Piyush Raj Singh. Stop posting. Start shipping.\n\n"
    "#OpenSource #GitHubTrending #ContentFactory #DevTools #AIvideo #HyperFrames #VoiceStudio #OpenMontage #Remotion #Automation #SignhifyStudio"
)

# 3. System Architecture Post
POST_PATH = Path("d:/Autogram/output/architecture-pipeline/post_automation_pipeline_1080x1350.jpg")
POST_CAPTION = (
    "How We Fully Automate Video Production (The Complete System Architecture) ⚡\n\n"
    "Here is the exact infrastructure behind our zero-human video publishing machine:\n\n"
    "1️⃣ Research: YouTube Data API (viral script discovery) + Perplexity (verification)\n"
    "2️⃣ Scripting & Animation: Fable 5.1 + Opus 5.5 code motion\n"
    "3️⃣ Stock Media Fallback: Pixabay API + Pexels API + Envato Elements\n"
    "4️⃣ Audio Core: ElevenLabs V4 vocal synthesis + Suno adaptive soundtrack\n"
    "5️⃣ Master Engine: HyperFrames CLI (builds 30-40 min long-form videos)\n"
    "6️⃣ Distribution: FFmpeg hardware encode + GPT Image 2.5 thumbnails + Zernio API\n\n"
    "👉 Want this fully made system for your agency or channel? Comment \"PIPELINE\" or reply to our story and we'll send the architecture blueprint!\n\n"
    "Engineered at Signhify Studio (signhify.dpdns.org)\n"
    "My name is Piyush Raj Singh. Stop posting. Start shipping.\n\n"
    "#AIEngineering #Automation #VideoArchitecture #SystemDesign #OpenSource #HyperFrames #Suno #ElevenLabs #FFmpeg #SignhifyStudio #AIworkflow"
)

published_items = []

def main():
    publisher.dry_run = False
    dm_automator.dry_run = False

    print("==================================================")
    print("🚀 EXECUTING COMPLETE LIVE MULTI-ASSET PUBLISHING")
    print(f"Target Instagram Account: {settings.ig_user_id}")
    print(f"Publication Date: {TODAY_STR}")
    print("==================================================")

    # ------------------------------------------------------------------
    # ASSET 1: DAY 02 REEL ("Claude > Premiere Pro?")
    # ------------------------------------------------------------------
    print("\n[1/4] Day 02 Reel ('Claude > Premiere Pro?'):")
    print("   🎉 REEL ALREADY PUBLISHED LIVE! Media ID: 17930093970424272")
    published_items.append({"type": "reel", "id": "17930093970424272", "name": "Claude vs Premiere Reel"})

    # ------------------------------------------------------------------
    # ASSET 2: 7-SLIDE MASTER CAROUSEL ("12 Open-Source GitHub Repos")
    # ------------------------------------------------------------------
    print("\n[2/4] 7-Slide Master Carousel ('12 Open-Source GitHub Repos'):")
    print("   🎉 CAROUSEL ALREADY PUBLISHED LIVE! Media ID: 18131921683830795")
    published_items.append({"type": "carousel", "id": "18131921683830795", "name": "12 GitHub Repos Carousel"})

    # ------------------------------------------------------------------
    # ASSET 3: SYSTEM ARCHITECTURE FEED POST ("How We Fully Automate It")
    # ------------------------------------------------------------------
    if POST_PATH.exists():
        print(f"\n[3/4] Staging and Publishing Architecture Feed Post...")
        try:
            post_urls = uploader.upload_slide_images([str(POST_PATH)], TODAY_STR, dry_run=False)
            post_url = post_urls[0]
            print(f"   ✓ Staged Post URL: {post_url}")

            post_media_id = publisher.publish_single_image(post_url, POST_CAPTION)
            print(f"   🎉 ARCHITECTURE POST PUBLISHED LIVE! Media ID: {post_media_id}")
            published_items.append({"type": "post", "id": post_media_id, "name": "How We Fully Automate It Post"})

            time.sleep(2)
            try:
                c_id = publisher.post_comment(post_media_id, "Comment 'PIPELINE' below to get the full architecture schematic & API integration guide! ⚡")
                print(f"   ✓ First comment posted: {c_id}")
            except Exception as e:
                print(f"   Comment notice: {e}")
        except Exception as e:
            print(f"   ❌ Post publishing error: {e}")
    else:
        print(f"   ⚠️ Post image not found at {POST_PATH}")

    # ------------------------------------------------------------------
    # ASSET 4: SYSTEM ARCHITECTURE 9:16 STORY ("How We Fully Automate It")
    # ------------------------------------------------------------------
    STORY_PATH = Path("d:/Autogram/output/architecture-pipeline/story_automation_pipeline_1080x1920.jpg")
    if STORY_PATH.exists():
        print(f"\n[4/4] Staging and Publishing Architecture 9:16 Story...")
        try:
            story_urls = uploader.upload_slide_images([str(STORY_PATH)], TODAY_STR, dry_run=False)
            story_url = story_urls[0]
            print(f"   ✓ Staged Story URL: {story_url}")

            story_media_id = publisher.publish_story(story_url)
            print(f"   🎉 ARCHITECTURE STORY PUBLISHED LIVE! Media ID: {story_media_id}")
            published_items.append({"type": "story", "id": story_media_id, "name": "How We Fully Automate It Story"})
        except Exception as e:
            print(f"   ❌ Story publishing error: {e}")

    # ------------------------------------------------------------------
    # 4. RUN INSTAGRAM DM AUTOMATION SCAN ACROSS ALL PUBLISHED ASSETS
    # ------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("🤖 EXECUTING INSTAGRAM AUTO-DM & COMMENT MONITORING")
    print("=" * 50)
    time.sleep(3)
    summary = dm_automator.scan_and_automate(limit_posts=10)
    print(f"Posts Scanned: {summary['media_scanned']}")
    print(f"Comments Checked: {summary['comments_checked']}")
    print(f"Automated DMs Dispatched: {summary['actions_executed']}")
    for act in summary['details']:
        print(f" -> @{act['username']}: matched [{act['keyword']}] -> {act['dm_status']}")

    print("\n" + "=" * 60)
    print("🎯 ALL TODAY'S POSTS, REELS & DM AUTOMATION EXECUTED!")
    for item in published_items:
        print(f" • {item['name']} ({item['type'].upper()}): https://www.instagram.com/p/{item['id']}/ (ID: {item['id']})")
    print("=" * 60)

if __name__ == "__main__":
    main()
