import pytest
from pathlib import Path
from orchestrator import run_pipeline

def test_full_pipeline_dry_run():
    manifest = run_pipeline(dry_run=True)
    assert manifest is not None
    assert "content_id" in manifest
    assert "slides_count" in manifest
    assert manifest["slides_count"] >= 7
    assert manifest["status"] == "SIMULATED_PUBLISH"
    assert manifest["qa_score"] >= 80

    # Verify generated output files
    today = manifest["date"]
    out_dir = Path("output") / today
    assert (out_dir / "content.json").exists()
    assert (out_dir / "caption.txt").exists()
    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "slide_01.jpg").exists()
