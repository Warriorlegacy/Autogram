"""Tests for the authoritative 60s Reel system (no network, no publishing)."""
import json
from pathlib import Path

from src.content.hyperframes_engine import HyperFramesEngine, TARGET_DURATION, TOTAL_FRAMES
from src.content import script60
from src.content import video60_pipeline as v60


def test_target_constants():
    assert TARGET_DURATION == 60.0
    assert TOTAL_FRAMES == 1800


def test_split_timeline_exact_60():
    bounds = HyperFramesEngine.split_timeline(60.0, 9)
    assert len(bounds) == 9
    assert bounds[0][0] == 0.0
    assert abs(bounds[-1][1] - 60.0) < 0.01
    total = sum(e - s for s, e in bounds)
    assert abs(total - 60.0) < 0.05


def test_scene_plan_duration_and_cta():
    plan = script60.build_scene_plan("word " * 140 + "Follow Signhify.studio for more.", "hook", 60.0, 9)
    assert plan["cta"] == "Follow Signhify.studio for more."
    assert len(plan["scenes"]) == 9
    total = sum(s["duration"] for s in plan["scenes"])
    assert abs(total - 60.0) < 0.05


def test_cta_and_wordcount(monkeypatch):
    monkeypatch.setattr(script60, "_llm_json", lambda *a, **k: None)  # hermetic: static fallback
    s = script60.generate_60s_script({"topic": "Pipecat voice pipelines", "pillar": "Tech Explainer"}, "Most people have never seen AI used this way.")
    assert "Follow Signhify.studio for more." in s["script"]
    assert 100 <= s["words"] <= 175  # static fallback may pad slightly under LLM range


def test_fact_gate_rejects_fake_stats():
    ok, _ = script60.fact_gate({}, "This boosts conversion by 320% guaranteed, world's fastest tool.")
    assert ok is False


def test_slot_idempotency_and_themes(tmp_path, monkeypatch):
    import datetime as dt
    day, slot = v60.resolve_slot(dt.datetime(2026, 9, 21, 6, 0), override="morning")
    assert (day, slot) == ("2026-09-21", "morning")
    assert v60.pick_theme("C", day, slot) == "C"
    assert v60.pick_theme("", day, slot) in ("A", "B", "C", "D", "E")


def test_hyperframes_60_compiles(tmp_path):
    eng = HyperFramesEngine(workspace_dir=tmp_path)
    plan = eng.build_scene_plan_60("Hello world. " * 30, "Test topic", 60.0, 9)
    d, plan_out = eng.compile_composition_60("Test topic", "Hello world. " * 30, plan, duration=60.0, target_dir=tmp_path, theme="B")
    html = (d / "index.html").read_text(encoding="utf-8")
    assert 'data-width="1080"' in html and 'data-height="1920"' in html
    assert "window.__timelines.marketing_reel" in html
    sp = json.loads((d / "scene_plan.json").read_text(encoding="utf-8"))
    assert abs(sum(s["duration"] for s in sp["scenes"]) - 60.0) < 0.05
    assert "320%" not in html  # no fabricated engagement stat


def test_mp3_outputs_use_mp3_codec():
    """All .mp3 writers must encode libmp3lame; AAC is allowed only for .m4a."""
    src = Path("src/content/audio60.py").read_text(encoding="utf-8")
    assert src.count("*MP3_CODEC") == 6  # espeak, offline, silent, atempo, pad, trim
    assert src.count('"-c:a", "aac"') == 2  # procedural_music + mix_voice_music (.m4a)


def test_workflow_deterministic_install_and_commit_order():
    """npm ci must be bare; memory must be staged before pull --rebase."""
    yml = Path(".github/workflows/daily-video.yml").read_text(encoding="utf-8")
    assert "npm ci || npm install" not in yml
    assert "\n        run: npm ci\n" in yml
    add_pos = yml.find("git add data/content-memory.json")
    pull_pos = yml.find("git pull --rebase")
    assert 0 <= add_pos < pull_pos


def test_llm_chain_skips_cleanly_without_keys(monkeypatch):
    for k in ("OPENCODE_API_KEY", "OPENCODE_BASE_URL", "OPENCODE_MODELS",
              "OPENROUTER_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    assert script60._llm_json("sys", "user") is None


def test_template_premium_3d_type():
    html = Path("renderer/templates/reels/marketing_promo.html.jinja2").read_text(encoding="utf-8")
    assert ".hook-title .ch" in html and 'id="stars"' in html and "rotationX" in html


def test_no_hardcoded_secrets():
    up = Path("src/storage/uploader.py").read_text(encoding="utf-8")
    assert "6d207e02198a847aa98d0a2a901485a5" not in up
    assert "f0ee2a304a71d5b2da983153c2284b73" not in up
    yml = Path(".github/workflows/daily-video.yml").read_text(encoding="utf-8")
    assert "PEXELS_API_KEY" not in yml or "exit 1" not in yml  # no hard Pexels gate
    assert "autogram_owner_vip_2026" not in yml
