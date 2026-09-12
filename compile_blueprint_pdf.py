#!/usr/bin/env python3
"""
compile_blueprint_pdf.py - Compiles the Signhify Studio Master Blueprint into an executive PDF.
Outputs: BLUEPRINT.pdf
"""

import sys
import os
from pathlib import Path

def build_blueprint_pdf(output_path="BLUEPRINT.pdf"):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
        )
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

    # Color Palette: Deep Tech Indigo, Midnight Navy, Slate, Mint Emerald, Accent Cyan
    primary_color = colors.HexColor('#0F172A')   # Slate 900
    accent_color = colors.HexColor('#2563EB')    # Royal Blue 600
    sub_color = colors.HexColor('#475569')       # Slate 600
    emerald_color = colors.HexColor('#059669')   # Emerald 600
    card_bg = colors.HexColor('#F8FAFC')         # Slate 50
    border_color = colors.HexColor('#CBD5E1')    # Slate 300

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=accent_color,
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=accent_color,
        spaceBefore=8,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=5
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#0F172A')
    )
    code_style = ParagraphStyle(
        'CodeSnippet',
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )
    table_text = ParagraphStyle(
        'TableText',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#1E293B')
    )
    table_header = ParagraphStyle(
        'TableHead',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Header / Title Block
    story.append(Paragraph('SIGNHIFY STUDIO — MASTER BLUEPRINT', title_style))
    story.append(Paragraph('FULL A.I. ENGINEERING STUDIO · PRODUCTION SYSTEMS, PORTFOLIO & PROMPT VAULT', subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=8))

    # Executive Overview
    story.append(Paragraph('1. Executive Positioning: The Full A.I. Engineering Studio', h1_style))
    callout_data = [[
        Paragraph(
            '<b>Signhify Studio</b> is not a conventional marketing agency. We are a <b>FULL A.I. ENGINEERING STUDIO</b>. '
            'Traditional agencies sell billable human hours and manual guesswork. We engineer zero-marginal-cost software systems, '
            'autonomous multi-agent workflows, production RAG pipelines, and self-hosted publishing machines that compound enterprise attention 24/7.',
            callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[540])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#BFDBFE')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 8))

    # Live Portfolio Table
    story.append(Paragraph('2. Live Systems & Production Portfolio', h1_style))
    story.append(Paragraph('Inspect our verified, battle-tested software systems operating in production today:', body_style))

    portfolio_data = [
        [Paragraph('Production System', table_header), Paragraph('Core Architecture', table_header), Paragraph('Verification / Access', table_header)],
        [
            Paragraph('<b>Autogram Engine</b>', table_text),
            Paragraph('Zero-touch publishing engine: RSS/HN ingestion, LLM scoring, Playwright rendering (1080×1350), automated Graph API feed drops (7 Carousels / Day).', table_text),
            Paragraph('github.com/Warriorlegacy/Autogram', table_text)
        ],
        [
            Paragraph('<b>Autonomous Video Pipeline</b>', table_text),
            Paragraph('9:16 vertical short-form generator: Pexels portrait stock, Edge-TTS neural voiceover, burned Anton subtitles, FFmpeg concatenation (10 Videos / Day).', table_text),
            Paragraph('Live Reel: instagram.com/signhify.studio', table_text)
        ],
        [
            Paragraph('<b>In-House Auto-DM Funnel</b>', table_text),
            Paragraph('Self-hosted replacement for ManyChat: Meta Graph API private replies, keyword triggers (FOSS, PROMPT, BLUEPRINT), and 2-step follower-gating.', table_text),
            Paragraph('Autonomous background daemon', table_text)
        ],
        [
            Paragraph('<b>Mission Control Cockpit</b>', table_text),
            Paragraph('Real-time glassmorphism Flask dashboard: multi-provider LLM failover telemetry, scheduler status, and live prompt testing.', table_text),
            Paragraph('autogram-dashboard.onrender.com/dashboard', table_text)
        ],
        [
            Paragraph('<b>Theme-Reactive 3D Web Engine</b>', table_text),
            Paragraph('Modern immersive 5-theme web experience (quantum, cyberpunk, neumorphic, swiss, bento) with interactive ROI simulator.', table_text),
            Paragraph('autogram-ai.vercel.app', table_text)
        ],
    ]
    p_table = Table(portfolio_data, colWidths=[120, 260, 160])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, card_bg]),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 10))

    # Our Verified Websites
    story.append(Paragraph('3. Studio Ecosystem & Live Hubs', h1_style))
    websites_data = [
        [Paragraph('Hub / Destination', table_header), Paragraph('URL', table_header), Paragraph('Role in Ecosystem', table_header)],
        [Paragraph('<b>Studio Home</b>', table_text), Paragraph('https://signhify.studio', table_text), Paragraph('Official Studio Portal: Services, Case Studies & Inquiries', table_text)],
        [Paragraph('<b>Product Engine</b>', table_text), Paragraph('https://autogram-ai.vercel.app', table_text), Paragraph('Live Interactive Showcase & Enterprise ROI Simulator', table_text)],
        [Paragraph('<b>Mission Control</b>', table_text), Paragraph('https://autogram-dashboard.onrender.com', table_text), Paragraph('Live Pipeline Telemetry, Health Checks & Scheduler Daemon', table_text)],
        [Paragraph('<b>Open-Source Core</b>', table_text), Paragraph('https://github.com/Warriorlegacy/Autogram', table_text), Paragraph('Open Architecture, Documentation & Autonomous Workflows', table_text)],
    ]
    w_table = Table(websites_data, colWidths=[110, 230, 200])
    w_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, card_bg]),
    ]))
    story.append(w_table)
    story.append(Spacer(1, 10))

    # The $0 Autonomous Stack Table
    story.append(Paragraph('4. The Zero-Marginal-Cost Autonomous Stack ($0/Month)', h1_style))
    story.append(Paragraph('How Signhify Studio runs high-throughput autonomous media pipelines with $0 recurring cloud infrastructure fees:', body_style))

    stack_data = [
        [Paragraph('Layer', table_header), Paragraph('Tool / Provider', table_header), Paragraph('Operating Cost', table_header), Paragraph('Capability & Quota', table_header)],
        [Paragraph('<b>LLM Reasoning</b>', table_text), Paragraph('Gemini 2.5 Flash / Groq / Ollama', table_text), Paragraph('<b>$0.00</b>', table_text), Paragraph('14.4k req/day free tier + unlimited local compute', table_text)],
        [Paragraph('<b>AI Voiceover</b>', table_text), Paragraph('Microsoft Edge-TTS Neural', table_text), Paragraph('<b>$0.00</b>', table_text), Paragraph('Studio-grade multilingual neural voices, zero API keys', table_text)],
        [Paragraph('<b>Stock Footage</b>', table_text), Paragraph('Pexels Video Search API', table_text), Paragraph('<b>$0.00</b>', table_text), Paragraph('4K/HD portrait video clips with 200 req/hr allowance', table_text)],
        [Paragraph('<b>Assembly Engine</b>', table_text), Paragraph('FFmpeg + MoneyPrinterTurbo', table_text), Paragraph('<b>$0.00</b>', table_text), Paragraph('Hardware-accelerated 1080x1920 MP4 rendering', table_text)],
        [Paragraph('<b>Public Staging</b>', table_text), Paragraph('Uguu.se / Catbox / Cloudflare R2', table_text), Paragraph('<b>$0.00</b>', table_text), Paragraph('High-speed direct CDN endpoints for Meta ingestion', table_text)],
        [Paragraph('<b>Publishing API</b>', table_text), Paragraph('Meta Graph API (v23.0)', table_text), Paragraph('<b>$0.00</b>', table_text), Paragraph('Direct container publishing (carousels, stories, reels)', table_text)],
        [Paragraph('<b>Cloud Scheduler</b>', table_text), Paragraph('GitHub Actions Cloud Runners', table_text), Paragraph('<b>$0.00</b>', table_text), Paragraph('2,000 free runner minutes/month (PC-off proof)', table_text)],
    ]
    s_table = Table(stack_data, colWidths=[90, 170, 70, 210])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, card_bg]),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 10))

    # Page Break for Clean Layout
    story.append(PageBreak())

    # Master Production Prompt Pack
    story.append(Paragraph('5. The Master Production Prompt Pack', h1_style))
    story.append(Paragraph('Deploy these copy-paste system prompt architectures directly in your workflows:', body_style))

    prompts = [
        (
            'PROMPT 1: The AI Infrastructure & SaaS Auditor',
            'Audit every paid subscription and API bill in [TARGET_WORKFLOW]. For each tool, identify the single highest-rated '
            'self-hosted FOSS or local AI alternative. Return license, GitHub stars, 1-line Docker deployment command, '
            'hardware RAM requirements, and net annual dollar savings. Rank by ROI.'
        ),
        (
            'PROMPT 2: The Chain-of-Density Knowledge Synthesizer',
            'Read [INPUT_SOURCE]. Produce a 5-sentence technical summary. Then execute 3 iterative compression passes. '
            'In each pass, add 3-5 missing domain entities and technical metrics while maintaining exact character length. '
            'Output only the final hyper-dense, zero-fluff synthesis.'
        ),
        (
            'PROMPT 3: The 50-Second Viral Short-Form Video Machine',
            'Write a 50-second spoken Reels narration about [TECHNICAL_TOPIC]. Format: 3-second hook (violates an established industry assumption), '
            'Beat 1 (the underlying architectural flaw), Beat 2 (the breakthrough implementation with proof metric), '
            'Beat 3 (tactical command/code takeaway), CTA (comment [KEYWORD] to receive the repository). Length: 110-125 words.'
        ),
        (
            'PROMPT 4: The Contrarian Architecture Formulator',
            'Provide 5 contrarian, defensible architectural principles regarding [ENGINEERING_DOMAIN] that senior principal '
            'engineers strongly validate but junior developers routinely argue against. For each principle, supply the 1-sentence '
            'first-principles rationale and 1 real-world failure mode.'
        ),
        (
            'PROMPT 5: The Enterprise High-Ticket Offer Architecture',
            'Deconstruct [CLIENT_AI_PROBLEM]. Architect a 3-tier enterprise solution: Tier 1 (Self-hosted POC & audit), '
            'Tier 2 (Custom Agentic Pipeline & RAG System with SLA), Tier 3 (Fully Managed Zero-Marginal-Cost Autonomous Engine). '
            'Define deliverables, timeline, risk reversal, and pricing anchor.'
        )
    ]

    for title, p_text in prompts:
        p_data = [
            [Paragraph(f'<b>{title}</b>', ParagraphStyle('PT', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=accent_color))],
            [Paragraph(p_text, code_style)]
        ]
        t = Table(p_data, colWidths=[540])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FAFAFA')),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    # Hire The Studio Section
    story.append(Spacer(1, 6))
    story.append(Paragraph('6. Partner with Signhify Studio (Hire the Engineering Team)', h1_style))
    story.append(Paragraph('We engineer custom autonomous systems for founders, creators, and enterprise teams who demand leverage over labor:', body_style))

    offer_data = [
        [Paragraph('Studio Capability', table_header), Paragraph('Deliverables & Impact', table_header), Paragraph('Deployment Time', table_header)],
        [
            Paragraph('<b>Autonomous Content Engines</b>', table_text),
            Paragraph('Zero-touch multi-platform machines (Carousels, Stories, Reels) with automated research, rendering, and auto-DM lead capture.', table_text),
            Paragraph('7 – 10 Days', table_text)
        ],
        [
            Paragraph('<b>Custom Agentic Workflows</b>', table_text),
            Paragraph('Production multi-agent systems, document ingestion RAG pipelines, internal tooling automations, and CRM integrations.', table_text),
            Paragraph('2 – 3 Weeks', table_text)
        ],
        [
            Paragraph('<b>Private Model Deployments</b>', table_text),
            Paragraph('On-premise / private cloud LLM serving (DeepSeek, Llama 3, vLLM, Ollama) with strict data privacy and zero API leakage.', table_text),
            Paragraph('1 – 2 Weeks', table_text)
        ],
    ]
    o_table = Table(offer_data, colWidths=[130, 310, 100])
    o_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), emerald_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, card_bg]),
    ]))
    story.append(o_table)
    story.append(Spacer(1, 8))

    # Final CTA Footer
    cta_data = [[
        Paragraph(
            '<b>READY TO DEPLOY YOUR AUTONOMOUS SYSTEM?</b><br/>'
            'Direct Message the word <b>STUDIO</b> to <b>@signhify.studio</b> on Instagram, '
            'or initiate your project directly at <b>https://signhify.studio</b>.<br/>'
            '<i>© 2026 Signhify Studio — FULL A.I. ENGINEERING STUDIO. Stop posting. Start shipping.</i>',
            ParagraphStyle('CTA', fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=primary_color, alignment=1)
        )
    ]]
    cta_table = Table(cta_data, colWidths=[540])
    cta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#DCFCE7')),
        ('BOX', (0, 0), (-1, -1), 1, emerald_color),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cta_table)

    # Build Document
    doc.build(story)
    print(f"Successfully compiled {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "BLUEPRINT.pdf"
    build_blueprint_pdf(out)
