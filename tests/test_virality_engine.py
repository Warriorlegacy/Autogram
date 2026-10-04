"""Deterministic offline tests for the virality engine (no network, no LLM)."""
import json
from pathlib import Path

import pytest

from src.content import script60
from src.content import virality_engine as ve

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_templates_json_has_exactly_12_with_required_keys():
    data = json.loads((REPO_ROOT / "data" / "templates.json").read_text(encoding="utf-8"))
    templates = data["reel_content_templates"]
    assert len(templates) == 12
    required = {"id", "name", "narrative_structure", "visual_grammar",
                "hook_patterns", "cta_hints"}
    for t in templates:
        assert required.issubset(t.keys()), f"template {t.get('id')} missing keys"
    # ids unique and registry matches the file
    assert len({t["id"] for t in templates}) == 12
    assert set(ve.TEMPLATES) == {t["id"] for t in templates}
    tpl = ve.get_template("3_ai_tools")
    assert tpl is not None and tpl["name"] == "3 AI Tools"


def test_weights_sum_to_one():
    assert abs(sum(ve.WEIGHTS.values()) - 1.0) < 1e-9
    assert abs(sum(ve.TOPIC_WEIGHTS.values()) - 1.0) < 1e-9


def test_score_concept_exact_weighted_math():
    concept = {"hook_strength": 80, "curiosity": 60, "information_value": 90,
               "visual_novelty": 70, "retention_potential": 85,
               "shareability": 75, "replayability": 65, "cta_quality": 100}
    res = ve.score_concept(concept)
    expected = (80 * .20 + 60 * .15 + 90 * .15 + 70 * .15 + 85 * .15
                + 75 * .10 + 65 * .05 + 100 * .05)
    assert res["total"] == round(expected, 2) == 77.5
    # per-metric contribution == score * weight
    for metric, w in ve.WEIGHTS.items():
        b = res["breakdown"][metric]
        assert b["weight"] == w
        assert b["contribution"] == round(concept[metric] * w, 2)


def test_score_concept_perfect_and_missing_defaults():
    assert ve.score_concept({k: 100 for k in ve.WEIGHTS})["total"] == 100.0
    # empty concept -> all metrics default to 50 -> total 50
    assert ve.score_concept({})["total"] == 50.0
    # 0-10 scale auto-detected and scaled to 0-100
    ten_scale = ve.score_concept({k: 9 for k in ve.WEIGHTS})
    assert ten_scale["total"] == 90.0


def test_gate_boundary_74_9_vs_75_0():
    ok, reason = ve.gate_concept(74.9)
    assert ok is False and "below" in reason
    ok, reason = ve.gate_concept(75.0)
    assert ok is True and "passes" in reason
    # concept dict totalling exactly 75.0
    concept = {"hook_strength": 100, "curiosity": 100, "information_value": 100}
    res = ve.score_concept(concept)
    assert res["total"] == 75.0
    assert ve.gate_concept(concept) == (True, "passes virality gate (75.0/100)")
    # 74.9 via a raw score
    assert ve.gate_concept(74.9)[0] is False


def test_topic_scoring_weights():
    topic = {"trend": 100, "curiosity": 100, "utility": 100,
             "visual_potential": 100, "shareability": 100, "brand_fit": 100}
    res = ve.score_topic(topic, memory=None)
    assert res["topic_score"] == 100.0
    assert res["novelty_penalty"] == 0.0
    assert res["breakdown"]["trend"]["contribution"] == 20.0
    assert res["breakdown"]["shareability"]["contribution"] == 15.0

    flat = ve.score_topic({k: 50 for k in ve.TOPIC_WEIGHTS})
    assert flat["topic_score"] == 50.0


def test_topic_novelty_penalty_from_memory():
    topic = {"topic": "RAG with reranking", "trend": 100, "curiosity": 100,
             "utility": 100, "visual_potential": 100, "shareability": 100,
             "brand_fit": 100}
    memory = {"recent_posts": [{"topic": "[Reel60] RAG with reranking: why retrieval order matters",
                                "hook": "..."}]}
    res = ve.score_topic(topic, memory=memory)
    assert res["base"] == 100.0
    assert res["novelty_penalty"] == ve.NOVELTY_PENALTY == 25.0
    assert res["topic_score"] == 75.0
    # no memory -> no penalty
    assert ve.score_topic(topic, memory={"recent_posts": []})["topic_score"] == 100.0


def test_topic_alias_keys_and_select_best_topic():
    # camelCase alias visualPotential maps onto visual_potential
    alias = ve.score_topic({"visualPotential": 100})
    canonical = ve.score_topic({"visual_potential": 100})
    assert alias["topic_score"] == canonical["topic_score"]

    cands = [
        {"topic": "Fresh local LLM tool", "trend": 90, "curiosity": 90,
         "utility": 90, "visual_potential": 90, "shareability": 90, "brand_fit": 90},
        {"topic": "Old repeated topic", "trend": 90, "curiosity": 90,
         "utility": 90, "visual_potential": 90, "shareability": 90, "brand_fit": 90},
    ]
    memory = {"recent_posts": [{"topic": "Old repeated topic", "hook": ""}]}
    sel = ve.select_best_topic(cands, memory=memory)
    assert sel["winner"]["topic"] == "Fresh local LLM tool"
    assert sel["winner"]["topic_score"] == 90.0
    assert len(sel["scores"]) == 2


def test_psychology_classifier_heuristic():
    cases = {
        "AI is replacing junior developer jobs": "FEAR",
        "How RAG reranking actually works": "CURIOSITY",
        "The 2027 future of local AI": "FUTURE",
        "Open source model just dropped": "DISCOVERY",
        "Why everyone is wrong about context windows": "CONTROVERSY",
    }
    for text, expected in cases.items():
        r = ve.classify_psychology({"topic": text, "angle": ""}, use_llm=False)
        assert r["trigger"] == expected, f"{text} -> {r['trigger']}"
        assert r["guidance"] and r["source"] == "heuristic"
        assert r["trigger"] in ve.PSYCH_TRIGGERS


def test_psychology_classifier_llm_enrichment(monkeypatch):
    monkeypatch.setattr(script60, "_llm_json", lambda *a, **k: {"trigger": "AWE"})
    r = ve.classify_psychology({"topic": "any topic", "angle": ""}, use_llm=True)
    assert r["trigger"] == "AWE" and r["source"] == "llm"
    # invalid LLM trigger -> heuristic fallback
    monkeypatch.setattr(script60, "_llm_json", lambda *a, **k: {"trigger": "BOGUS"})
    r = ve.classify_psychology({"topic": "How RAG works", "angle": ""}, use_llm=True)
    assert r["trigger"] == "CURIOSITY" and r["source"] == "heuristic"


def test_ab_test_falls_back_without_llm(monkeypatch):
    monkeypatch.setattr(script60, "_llm_json", lambda *a, **k: None)
    monkeypatch.setattr(script60, "_recent_texts", lambda n=60: [])
    topic = {"topic": "Pipecat voice pipelines", "pillar": "Tech Explainer",
             "angle": "low-latency voice agents"}
    res = ve.ab_test(topic)
    assert res["provider"] == "static"
    assert res["combinations_scored"] == 90  # 10 hooks x 3 scripts x 3 visuals
    best = res["best"]
    assert best is not None
    assert best["hook"] and best["script"] and best["visual"]
    assert "Follow Signhify.studio for more." in best["script"]
    assert isinstance(best["total"], (int, float)) and 0 <= best["total"] <= 100
    assert len(res["hooks"]) == 10 and len(res["scripts"]) == 3 and len(res["visuals"]) == 3


def test_select_topic_script_min_score_wiring(monkeypatch):
    """min_score=0 keeps current behavior (virality None); min_score>0 scores
    and rotates on a low-scoring concept (mirrors fact_gate rotation)."""
    monkeypatch.setattr(script60, "_recent_texts", lambda n=60: [])
    monkeypatch.setattr(script60, "discover_topic",
                        lambda p=None, o=None: {"topic": "Test Topic", "pillar": "Tech Explainer",
                                                "angle": "a", "source": "test"})
    monkeypatch.setattr(script60, "generate_hooks",
                        lambda topic, n=7: [{"text": "h", "score": 9}] * n)
    monkeypatch.setattr(script60, "build_scene_plan",
                        lambda *a, **k: {"scenes": [], "duration": 60.0})

    calls = {"n": 0}

    def fake_script(topic, hook):
        calls["n"] += 1
        if calls["n"] == 1:  # first concept scores below the gate -> rotation
            return {"script": "hi", "words": 1, "provider": "static",
                    "fact_ok": True, "fact_reason": "ok"}
        return {"script": ("word " * 140) + "Follow Signhify.studio for more.",
                "words": 145, "provider": "static", "fact_ok": True, "fact_reason": "ok"}

    monkeypatch.setattr(script60, "generate_60s_script", fake_script)

    # default behavior: no virality key content
    r0 = script60.select_topic_script()
    assert r0["virality"] is None
    assert r0["source"] == "test"

    # min_score active: low first concept rotates to a fresh fallback topic
    calls["n"] = 0
    r1 = script60.select_topic_script(min_score=75.0)
    assert r1["source"] == "virality_gate_rotation"
    assert calls["n"] == 2
    assert r1["virality"] is not None
    assert r1["virality"]["passed"] is True
    assert r1["virality"]["total"] >= 75.0
    assert set(r1["virality"]["breakdown"]) == set(ve.WEIGHTS)
