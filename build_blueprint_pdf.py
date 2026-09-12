#!/usr/bin/env python3
"""build_blueprint_pdf.py — regenerates BLUEPRINT.pdf from the studio source data.

Run:  python build_blueprint_pdf.py
Out:  BLUEPRINT.pdf (repo root) — the follower-gated asset DM'd by the auto-DM engine.
Requires: reportlab (pip install reportlab).
"""

import os
import sys

try:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except ImportError:
    print("Installing reportlab...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "BLUEPRINT.pdf")

CYAN = HexColor("#00E5FF")
INK = HexColor("#0B1220")
MUTED = HexColor("#475569")
BG_DARK = HexColor("#0B1220")


def build() -> str:
    doc = SimpleDocTemplate(PDF_PATH, pagesize=letter,
                            leftMargin=44, rightMargin=44, topMargin=44, bottomMargin=44)
    ss = getSampleStyleSheet()
    title = ParagraphStyle("Title2", parent=ss["Heading1"], fontSize=24, leading=28,
                           textColor=INK, spaceAfter=2, fontName="Helvetica-Bold")
    sub = ParagraphStyle("Sub", parent=ss["Normal"], fontSize=10, leading=14,
                         textColor=MUTED, spaceAfter=8)
    h2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, leading=17,
                        textColor=HexColor("#0E7490"), spaceBefore=14, spaceAfter=6,
                        fontName="Helvetica-Bold")
    body = ParagraphStyle("Body", parent=ss["Normal"], fontSize=9.5, leading=14,
                          textColor=INK, spaceAfter=5)
    small = ParagraphStyle("Small", parent=ss["Normal"], fontSize=8, leading=11,
                           textColor=MUTED, spaceAfter=3)
    mono = ParagraphStyle("Mono", parent=ss["Code"], fontSize=7.5, leading=10.5,
                          fontName="Courier", textColor=INK, spaceAfter=4,
                          backColor=HexColor("#F1F5F9"), borderPadding=6)

    def tbl(rows, widths):
        t = Table(rows, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 11),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), HexColor("#F8FAFC")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    story = [
        Paragraph("THE SIGNHIFY STUDIO BLUEPRINT", title),
        Paragraph("Systems, stacks &amp; prompts behind a fully autonomous AI content engine — free forever.", sub),
        Paragraph("Signhify Studio is a FULL AI ENGINEERING STUDIO — signhify.studio · @signhify.studio", small),
        HRFlowable(width="100%", thickness=1.5, color=CYAN, spaceAfter=10),

        Paragraph("1. Live Portfolio", h2),
        tbl([
            ["System", "What it does"],
            ["Autogram Engine", "Zero-touch IG machine: research, virality gate, carousels, stories, reels, auto-publish + auto-DM (24 drops/day)."],
            ["$0 Video Pipeline", "MoneyPrinterTurbo + edge-TTS + Pexels + FFmpeg to 9:16 reels, auto-published."],
            ["Mission-Control Dashboard", "Live cockpit: queue, scheduler daemon, provider hub, prompt library."],
            ["3D Theme-Reactive Landing", "5-theme immersive site with ROI simulator."],
        ], [130, 350]),
        Paragraph("Inspect: github.com/Warriorlegacy/Autogram · autogram-dashboard.onrender.com/dashboard · autogram-ai.vercel.app", small),

        Paragraph("2. Websites", h2),
        Paragraph("signhify.studio (studio home) · autogram-ai.vercel.app (product) · autogram-dashboard.onrender.com/dashboard (live demo) · github.com/Warriorlegacy/Autogram (open engine)", body),

        Paragraph("3. The $0 Autonomy Stack", h2),
        tbl([
            ["Layer", "Tool (free)"],
            ["LLM reasoning", "Groq free tier, Gemini free, local Ollama"],
            ["Voiceover", "Microsoft edge-TTS, no key"],
            ["Footage", "Pexels free API"],
            ["Assembly", "FFmpeg + MoneyPrinterTurbo, local"],
            ["Hosting", "IMGBB free API, catbox.moe / 0x0.st"],
            ["Publishing", "Meta Graph API, no SaaS middleman"],
            ["Scheduling", "GitHub Actions + cron-job.org + Task Scheduler"],
            ["Captions", "Anton (OFL), burned in"],
        ], [130, 350]),

        Paragraph("4. Prompt Pack (copy-paste starters)", h2),
        Paragraph("<b>P1 — The $0 Auditor.</b> List every paid tool in [WORKFLOW]. For each, name the best self-hosted FOSS replacement, license, stars, and the 1-line deploy command. Rank by yearly savings.", body),
        Paragraph("<b>P2 — Chain-of-Density Summarizer.</b> Summarize [ARTICLE] in 5 sentences. Rewrite 3x, each denser — same length, more entities, zero filler. Return only the final.", body),
        Paragraph("<b>P3 — Reel Script Machine.</b> 50-second Reels script on [TOPIC]: 3-second hook, 3 beats with proof-points, last-line CTA. 110-130 words. No stage directions.", body),
        Paragraph("<b>P4 — Contrarian Takes.</b> 5 defensible contrarian takes on [NICHE], one line each with the 1-sentence reason.", body),
        Paragraph("<b>P5 — Carousel Architect.</b> 8 slides on [TOPIC]: sub-8-word hook, one idea + proof chip per slide, final-slide CTA commenting [KEYWORD].", body),

        Paragraph("5. Hire the Studio", h2),
        Paragraph("Autonomous content engines · short-form video pipelines · agentic workflows &amp; integrations. DM the word STUDIO to @signhify.studio — or start at signhify.studio.", body),
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8),
        Paragraph("© 2026 Signhify Studio — FULL AI ENGINEERING STUDIO. Ship systems, not posts. signhify.studio", small),
    ]
    doc.build(story)
    print(f"[OK] Generated {PDF_PATH}")
    return PDF_PATH


if __name__ == "__main__":
    build()
