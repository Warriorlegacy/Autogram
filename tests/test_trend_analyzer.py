import pytest
from src.research.trend_analyzer import trend_analyzer, VIRAL_GATE_THRESHOLD

def test_trend_analyzer_high_viral_scoring_saas_killer():
    candidate = {
        "topic": "Coolify: The Self-Hosted Vercel and Heroku Alternative",
        "angle": "Why Coolify replaces $200/mo Vercel bills",
        "pillar": "FOSS SaaS Alternatives",
        "source_type": "github_repository",
        "sources": ["https://github.com/coollabsio/coolify"],
        "stars": 42000,
        "evidence_strength": 0.98,
        "excerpt": "Self-host Next.js, Docker, databases on $5/mo VPS. 100% open source."
    }
    metrics = trend_analyzer.calculate_viral_metrics(candidate)
    assert metrics["approved_by_viral_gate"] is True
    assert metrics["viral_score"] >= 85.0
    assert "ULTRA-VIRAL" in metrics["viral_tier"] or "HIGH VIRAL" in metrics["viral_tier"]
    assert "Stop paying" in metrics["viral_hook"] or "Vercel" in metrics["viral_hook"]
    assert metrics["metrics"]["cost_asymmetry"] >= 20.0

def test_trend_analyzer_high_viral_scoring_prompt_framework():
    candidate = {
        "topic": "The Secret Chain-of-Density Prompt That Outperforms ChatGPT by 3.8x",
        "angle": "The prompt architecture that condenses dense entities in 5 passes",
        "pillar": "Local AI & Edge Compute",
        "source_type": "prompt_architecture",
        "sources": ["https://arxiv.org/abs/2309.04269"],
        "stars": 10000,
        "evidence_strength": 0.96,
        "excerpt": "Secret recursive prompt code for extreme entity density."
    }
    metrics = trend_analyzer.calculate_viral_metrics(candidate)
    assert metrics["approved_by_viral_gate"] is True
    assert metrics["viral_score"] >= 85.0
    assert metrics["metrics"]["save_share_urgency"] >= 15.0

def test_trend_analyzer_rejects_boring_slop():
    candidate = {
        "topic": "Getting Started with Python: Basics of Variables and Functions",
        "angle": "Introduction to programming concepts",
        "pillar": "Developer Power Tools & CLI",
        "source_type": "generic_tutorial",
        "sources": [],
        "stars": 10,
        "evidence_strength": 0.4,
        "excerpt": "A beginner tutorial on what is a variable in python."
    }
    metrics = trend_analyzer.calculate_viral_metrics(candidate)
    assert metrics["approved_by_viral_gate"] is False
    assert metrics["viral_score"] < VIRAL_GATE_THRESHOLD
    assert "REJECTED" in metrics["viral_tier"]
    assert metrics["rejection_reason"] is not None

def test_trend_analyzer_filter_candidates():
    candidates = [
        {
            "topic": "Stirling-PDF: 100% Local Powerful PDF Manipulation Suite",
            "excerpt": "Replace Adobe Acrobat Pro for $0 with 1-click docker run.",
            "stars": 91000,
            "source_type": "github_repository"
        },
        {
            "topic": "Minor bugfix release v1.2.4 patch notes",
            "excerpt": "Fixed a minor typo in documentation update.",
            "stars": 5,
            "source_type": "release_notes"
        },
        {
            "topic": "n8n Workflow Automation: Unlimited Zapier for $0",
            "excerpt": "Self-hosted fair-code alternative to Zapier $59/mo tiers.",
            "stars": 55000,
            "source_type": "github_repository"
        }
    ]
    approved, report = trend_analyzer.filter_viral_candidates(candidates, memory={})
    assert len(approved) == 2
    assert approved[0]["topic"] == "Stirling-PDF: 100% Local Powerful PDF Manipulation Suite" or approved[0]["topic"] == "n8n Workflow Automation: Unlimited Zapier for $0"
    assert report["approved_count"] == 2
    assert report["rejected_count"] == 1
