import pytest
from src.research.fetcher import fetcher
from src.research.scorer import scorer
from src.content.generator import generator
from src.content.fact_checker import fact_checker
from src.content.quality_gate import quality_gate

def test_source_fetcher():
    sources = fetcher.acquire_sources(live_fetch=False)
    assert len(sources) > 0
    assert "source_title" in sources[0]
    assert "url" in sources[0]

def test_topic_scorer():
    candidates = [
        {
            "topic": "Context Caching Architecture in Multi-Agent Pipelines",
            "pillar": "AI Tool Breakdown",
            "evidence_strength": 0.95,
            "novelty_score": 0.90,
            "practicality_score": 0.92,
            "save_share_score": 0.88,
            "saturation_risk": 0.1,
            "sources": ["https://example.com/test"]
        },
        {
            "topic": "10 Generic AI Tools You Must Check Out",
            "pillar": "AI Tool Breakdown",
            "evidence_strength": 0.5,
            "novelty_score": 0.3,
            "practicality_score": 0.4,
            "save_share_score": 0.3,
            "saturation_risk": 0.9,
            "sources": ["https://example.com/test2"]
        }
    ]
    result = scorer.select_best_topic(candidates)
    assert result["winner"]["topic"] == "Context Caching Architecture in Multi-Agent Pipelines"
    assert result["winner"]["calculated_score"] > 80

def test_content_generation_and_qa():
    topic = {
        "topic": "Why Multi-Agent Systems Beat Giant Prompts",
        "pillar": "AI Tool Breakdown",
        "angle": "State management and validation over monolithic prompts"
    }
    sources = [{"source_id": "SRC-TEST-01", "source_title": "Multi-Agent Research", "excerpt": "Benchmarked across 500 tasks."}]

    carousel = generator.generate_carousel(topic, sources)
    assert "slides" in carousel
    assert len(carousel["slides"]) >= 7
    assert len(carousel["slides"]) <= 10

    # Fact check
    fc_result = fact_checker.verify_carousel(carousel, sources)
    assert fc_result["pass"] is True

    # Quality gate
    qa_result = quality_gate.evaluate(carousel)
    assert qa_result["score"] >= 80
    assert qa_result["approved"] is True

def test_all_six_pillars_generation():
    pillars = [
        "AI Tool Breakdown",
        "Prompting & Workflow",
        "Marketing Psychology",
        "Tech Industry Explainer",
        "Career & Skills",
        "Myth-Bust / Contrarian"
    ]
    sources = [{"source_id": "SRC-TEST-01", "source_title": "Benchmark Research", "excerpt": "Empirical evidence from production."}]

    for pillar in pillars:
        topic = {"topic": f"Deep Dive on {pillar}", "pillar": pillar, "angle": "Operational breakdown"}
        carousel = generator.generate_carousel(topic, sources)
        assert len(carousel["slides"]) >= 7
        qa = quality_gate.evaluate(carousel)
        assert qa["approved"] is True, f"Pillar '{pillar}' failed QA: {qa['rejection_reasons']}"

