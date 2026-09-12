#!/usr/bin/env python3
"""
compile_pdf.py - Converts the Autonomous Video Pipeline Guide into a styled PDF manual.
Outputs: Autonomous_Video_Pipeline.pdf
"""

import sys
import os

def build_pipeline_pdf(output_path="Autonomous_Video_Pipeline.pdf"):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()

    t_style = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1A365D'))
    subtitle_style = ParagraphStyle('Sub', fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#4A5568'), spaceAfter=8)
    h1_style = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#2B6CB0'), spaceBefore=10, spaceAfter=4)
    h2_style = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#2D3748'), spaceBefore=6, spaceAfter=2)
    b_style = ParagraphStyle('B', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#2D3748'), spaceAfter=4)
    c_style = ParagraphStyle('C', fontName='Courier', fontSize=6.5, leading=8.5, textColor=colors.HexColor('#1A202C'))

    story = [
        Paragraph('Autonomous Short-Form Video Pipeline Specification', t_style),
        Paragraph('Zero-marginal-cost content engine for autonomous YouTube Shorts & Instagram Reels.', subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E0"), spaceAfter=8),

        Paragraph('1. Core System Architecture', h1_style),
        Paragraph('Orchestrates local/free LLMs, MoneyPrinterTurbo (FastAPI/FFmpeg), Edge-TTS, and official social media publishing APIs.', b_style),
        Preformatted('''[Scheduler] -> [1. Script Generation (Ollama / Groq Free)]
            -> [2. Video Rendering Engine (MoneyPrinterTurbo :8080)]
               - Microsoft Edge-TTS (Zero-cost neural voices)
               - Pexels API (Stock video footage)
               - FFmpeg (9:16 vertical render & subtitle burning)
            -> [3. Temporary Cloud Staging (Cloudflare R2 / S3 / Catbox)]
            -> [4a. YouTube Data API v3 (Shorts Direct Resumable Upload)]
            -> [4b. Meta Graph API (Reels Container & Publish)]''', c_style),
        Spacer(1, 6),

        Paragraph('2. Free & Unlimited LLM Engine Selection ($0.00)', h1_style),
        Table([
            ['Engine', 'Cost', 'Quota', 'Protocol', 'Primary Advantage'],
            ['Ollama (Self-Hosted)', '$0.00', 'Unlimited', 'HTTP :11434', 'Zero rate limits, runs locally on host hardware.'],
            ['Groq Cloud', '$0.00', '14,400 RPD', 'OpenAI REST', '500+ tokens/sec, no local compute required.'],
            ['Google Gemini Free', '$0.00', '1,500 RPD', 'Google REST', 'High reasoning, strict 15 RPM throttling.']
        ], colWidths=[100, 40, 60, 80, 260], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')])
        ]),
        Spacer(1, 6),

        Paragraph('3. Headless MoneyPrinterTurbo API Configuration (config.toml)', h1_style),
        Preformatted('''[app]
listen_host = "0.0.0.0"
listen_port = 8080
endpoint = "http://127.0.0.1:8080"
llm_provider = "ollama"
ollama_base_url = "http://127.0.0.1:11434"
ollama_model_name = "qwen2.5:7b"
video_source = "pexels"
pexels_api_keys = ["YOUR_PEXELS_KEY"]
voice_name = "en-US-ChristopherNeural"
subtitle_provider = "edge"''', c_style),
        Spacer(1, 4),

        PageBreak(),

        Paragraph('4. Master Orchestrator Architecture (pipeline_runner.py & orchestrator.py)', h1_style),
        Paragraph('The pipeline unifies YouTube Shorts and Instagram Reels publishing into a single autonomous flow:', b_style),
        Preformatted('''import os, time, json, requests
from src.content.generator import generator
from src.content.mpt_client import mpt_client
from src.storage.uploader import uploader
from src.instagram.publisher import publisher
from src.youtube.shorts_publisher import youtube_publisher

def execute_autonomous_run(topic):
    # 1. Script generation via Ollama / Groq fallback
    meta = generator.generate_reel_script(topic, "AI Tool Breakdown")

    # 2. Render 9:16 vertical video via local MoneyPrinterTurbo
    dest_path = f"output/reel_{int(time.time())}.mp4"
    video_file = mpt_client.render_reel(script=meta["narration"], subject=meta["subject"], dest=dest_path)

    # 3. Stage video to S3/R2/Catbox (Public HTTPS URL required by Meta Graph API)
    public_url = uploader.upload_video_file(video_file, "today")

    # 4. Upload to YouTube Shorts via YouTube Data API v3
    yt_id = youtube_publisher.upload_short(
        video_path=video_file,
        title=meta.get("title", f"{topic} #Shorts"),
        description=meta.get("caption", ""),
        tags=meta.get("hashtags", [])
    )

    # 5. Publish to Instagram Reels via Meta Graph API
    ig_media_id = publisher.publish_reel(public_url, meta["caption"])
    return {"youtube_id": yt_id, "instagram_media_id": ig_media_id}''', c_style),
        Spacer(1, 6),

        Paragraph('5. Production Constraints & Operational Guardrails', h1_style),
        Paragraph('• <b>Rendering Load:</b> Limit FFmpeg rendering to 2 concurrent tasks per 8 CPU cores to prevent out-of-memory crashes.<br/>'
                  '• <b>YouTube API Quota:</b> 10,000 units/day default allocation (~1,600 units per upload = maximum 6 autonomous uploads daily).<br/>'
                  '• <b>Instagram Reels Transcoding:</b> Container status polling requires up to 180s for Meta video ingestion before publishing.<br/>'
                  '• <b>Disk Retention:</b> Daily cleanup purges rendered MP4s older than 48 hours to preserve SSD headroom.', b_style),
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceAfter=6),
        Paragraph('<i>Autogram Zero-Touch Engine — Autonomous Video Generation Specification</i>', b_style)
    ]

    doc.build(story)
    print(f"[SUCCESS] {output_path} generated successfully.")
    return output_path

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "Autonomous_Video_Pipeline.pdf"
    build_pipeline_pdf(out)
