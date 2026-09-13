"""
Run audit report generator (Makerzz P8 gate).

Compiles the final run report into runs/<run_id>/report.json (always) and a
styled PDF (report.pdf) when reportlab is available.

Report contract — numbers only from APIs/receipts; anything missing is
explicitly marked "unavailable", NEVER fabricated:

  - input brief & research sources
  - ranked angles & decisions taken
  - shipped assets (slides, video paths, captions)
  - exact publish receipts & remote post IDs
  - ledger debits & credit breakdown
  - analytics snapshots or explicit unavailable markers
"""

import json
from datetime import datetime
from pathlib import Path


def generate_report(run_dir: Path, run_state: dict) -> dict:
    """
    Compile the P8 report from durable artifacts in the run workspace.
    Never invents data: every section reads actual artifacts or marks unknown.
    """
    run_dir = Path(run_dir)
    brief = run_state.get("brief", {})
    stages = run_state.get("stages", {})

    report = {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat(),
        "run_id": run_state.get("run_id"),
        "input_snapshot": {
            "brief": brief,
            "mode": run_state.get("mode"),
            "policy": run_state.get("policy"),
        },
        "stage_decisions": {
            phase: {
                "status": stage.get("status"),
                "attempt": stage.get("attempt"),
                "charged_credits": stage.get("charged_credits", 0),
                "error": stage.get("error"),
            }
            for phase, stage in stages.items()
        },
        "research_sources": _read_json(run_dir / "scan.json", {}).get("signals", []),
        "ranked_angles": _read_json(run_dir / "scan.json", {}).get("ranked_angles", []),
        "calendar_summary": {
            "total_items": _read_json(run_dir / "calendar.json", {}).get("total_items", 0),
            "timezone": _read_json(run_dir / "calendar.json", {}).get("timezone"),
        },
        "content_shipped": {
            "script_verified": _read_json(run_dir / "script_verification.json", {}).get("passed"),
            "script_word_count": _read_json(run_dir / "script_verification.json", {}).get("word_count"),
            "slides_rendered": len(list((run_dir / "slides").glob("slide_*.jpg")))
            if (run_dir / "slides").exists()
            else 0,
            "carousel_plan_present": (run_dir / "carousel_plan.json").exists(),
            "edit_plan_present": (run_dir / "edit_plan.json").exists(),
        },
        "publish_receipts": _read_json(run_dir / "publish_receipt.json", None)
        or {"status": "not published", "availability": "unavailable"},
        "credit_breakdown": _credit_breakdown(stages),
        "analytics": {
            "availability": "unavailable",
            "note": "Platform analytics are fetched post-publication; this report never fabricates metrics.",
        },
        "unknowns": _collect_unknowns(run_dir),
        "next_recommendations": _recommendations(run_dir),
    }

    # Persist report.json (P8 gate artifact)
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Optional styled PDF
    _render_pdf(report, run_dir / "report.pdf")
    return report


def _credit_breakdown(stages: dict) -> dict:
    total = sum(int(s.get("charged_credits", 0)) for s in stages.values())
    return {
        "by_stage": {
            phase: int(s.get("charged_credits", 0))
            for phase, s in stages.items()
            if int(s.get("charged_credits", 0)) > 0
        },
        "total_charged": total,
    }


def _collect_unknowns(run_dir: Path) -> list[str]:
    unknowns = []
    scan = _read_json(run_dir / "scan.json", {})
    for sig in scan.get("signals", []):
        ev = sig.get("engagement_evidence", {})
        if ev.get("availability") == "unavailable":
            unknowns.append(f"Engagement metrics unavailable for: {sig.get('topic', '')[:80]}")
    return unknowns


def _recommendations(run_dir: Path) -> list[str]:
    scan = _read_json(run_dir / "scan.json", {})
    recs = []
    for blind_spot in scan.get("blind_spots", [])[:3]:
        recs.append(blind_spot)
    angles = scan.get("ranked_angles", [])
    if angles:
        recs.append(f"Prioritize top angle next cycle: {angles[0].get('angle', '')[:100]}")
    return recs


def _read_json(path: Path, default):
    if not Path(path).exists():
        return default
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def _render_pdf(report: dict, out_path: Path) -> None:
    """Styled PDF via reportlab when available; silently skips otherwise."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import inch
    except ImportError:
        return  # PDF is optional; report.json is the canonical artifact

    try:
        doc = SimpleDocTemplate(str(out_path), pagesize=letter)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "RunTitle", parent=styles["Title"], fontSize=18, spaceAfter=12
        )
        head_style = ParagraphStyle(
            "SectionHead", parent=styles["Heading2"], fontSize=12, spaceBefore=10
        )
        mono = ParagraphStyle("Mono", parent=styles["BodyText"], fontName="Courier", fontSize=8)

        story = [
            Paragraph("Makerzz Run Audit Report", title_style),
            Paragraph(f"Run ID: {report.get('run_id')}", styles["Normal"]),
            Paragraph(f"Generated: {report.get('generated_at')}", styles["Normal"]),
            Spacer(1, 0.2 * inch),
        ]

        story.append(Paragraph("Stage Decisions", head_style))
        for phase, dec in report.get("stage_decisions", {}).items():
            story.append(Paragraph(
                f"{phase}: {dec.get('status')} (attempt {dec.get('attempt')}, "
                f"credits {dec.get('charged_credits')})",
                styles["Normal"],
            ))

        story.append(Paragraph("Credit Breakdown", head_style))
        cb = report.get("credit_breakdown", {})
        story.append(Paragraph(f"Total charged: {cb.get('total_charged', 0)} credits", mono))

        story.append(Paragraph("Analytics", head_style))
        story.append(Paragraph(
            report.get("analytics", {}).get("note", "Metrics unavailable."),
            styles["Normal"],
        ))

        doc.build(story)
    except Exception:
        # PDF failure must never fail the run — report.json is canonical
        pass
