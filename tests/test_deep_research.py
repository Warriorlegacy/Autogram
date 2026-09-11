import pytest
from src.research.deep_researcher import deep_researcher

def test_deep_research_saas_contrast():
    topic = {
        "topic": "Coolify: The Self-Hosted Vercel and Heroku Alternative",
        "pillar": "FOSS SaaS Alternatives",
        "url": "https://github.com/coollabsio/coolify"
    }
    dossier = deep_researcher.research_topic(topic)
    assert dossier["deep_research_conducted"] is True
    assert "Vercel" in dossier["replaces_saas"]
    assert "curl" in dossier["deployment_command"] or "docker" in dossier["deployment_command"]
    assert len(dossier["honest_tradeoffs"]) > 0
    assert len(dossier["research_evidence"]) > 0

def test_deep_research_prompt_framework():
    topic = {
        "topic": "The Chain-of-Density Prompt Architecture for Executive Summaries",
        "pillar": "Local AI & Edge Compute"
    }
    dossier = deep_researcher.research_topic(topic)
    assert dossier["deep_research_conducted"] is True
    assert "Chain-of-Density" in dossier.get("prompt_framework", "")
    assert "density" in dossier.get("mechanism", "").lower()

def test_deep_research_n8n():
    topic = {
        "topic": "n8n Workflow Automation",
        "pillar": "FOSS SaaS Alternatives"
    }
    dossier = deep_researcher.research_topic(topic)
    assert "Zapier" in dossier["replaces_saas"]
    assert "docker" in dossier["deployment_command"]
