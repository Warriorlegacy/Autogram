"""
tests/test_hyperframes_templates.py
Validates every HyperFrames reel template (legacy + new premium 3D scene
templates) through Jinja2 with representative 60s values, and verifies the
engine's template mapping is coherent.

Covers:
  - render succeeds for every template (old + new)
  - output contains the seekable GSAP timeline registration (window.__timelines)
  - scenes carry data-start/data-duration attributes
  - brand text (Signhify Studio) is present
  - each scene element has a corresponding subtitle element
  - scene bodies render the short headline (no full-narration duplication)
  - TEMPLATE_FILES has a valid file for every theme
  - every new visual_type maps to an existing template file
"""

from pathlib import Path

import pytest

from src.content.hyperframes_engine import (
    HyperFramesEngine,
    TEMPLATE_FILES,
    VISUAL_TEMPLATE_MAP,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "renderer" / "templates" / "reels"

ALL_TEMPLATES = [
    "marketing_promo.html.jinja2",
    "avatar_presenter.html.jinja2",
    "neural_network.html.jinja2",
    "data_flow.html.jinja2",
    "terminal_code.html.jinja2",
    "comparison.html.jinja2",
    "growth_chart.html.jinja2",
]

# Representative 60s scene starts/durations (5 acts summing to 60.0).
SCENE_STARTS = [0.0, 7.2, 21.6, 40.8, 51.0]
SCENE_DURATIONS = [7.2, 14.4, 19.2, 10.2, 9.0]
assert abs(sum(SCENE_DURATIONS) - 60.0) < 0.01


def _render(template_name: str, *, logo: str = "", audio: str = "") -> str:
    """Render a template through Jinja2 with the engine's exact variable set."""
    engine = HyperFramesEngine(workspace_dir=REPO_ROOT / "workspace" / "test_templates")
    template = engine.env.get_template(template_name)
    narrations = {
        1: "Run the deploy command in the terminal to ship the build.",
        2: "The neural network model learns from nodes and layers.",
        3: "Our data pipeline automates the flow from input to output.",
        4: "This replaces the old manual way with a new automated process.",
        5: "Grow to 100K users with 10x faster scaling.",
    }
    ctx = {
        "topic": "AI Automation: Scale your workflow",
        "total_duration": 60.0,
        "audio_file": audio,
        "logo_file": logo,
        "hook_alert": "SYSTEM ACTIVATION",
        "hook_title": "AI Automation",
        "theme_css": engine.theme_css("A"),
        "proof_metric": "3D",
    }
    for i in range(1, 6):
        ctx[f"scene{i}_narration"] = narrations[i]
        ctx[f"scene{i}_headline"] = engine._scene_headline(narrations[i], i - 1, 5)
        ctx[f"scene{i}_start"] = SCENE_STARTS[i - 1]
        ctx[f"scene{i}_duration"] = SCENE_DURATIONS[i - 1]
    return template.render(**ctx)


@pytest.mark.parametrize("template_name", ALL_TEMPLATES)
@pytest.mark.parametrize("logo,audio", [("", ""), ("logo.jpeg", ""), ("", "voice.mp3"), ("logo.jpeg", "voice.mp3")])
def test_template_renders_with_contract(template_name, logo, audio):
    """Every template renders and satisfies the HyperFrames interface contract."""
    html = _render(template_name, logo=logo, audio=audio)

    # Render succeeded and is a full document
    assert html.strip()
    assert "data-composition-id=" in html
    assert 'data-width="1080"' in html and 'data-height="1920"' in html

    # Seekable GSAP timeline registration
    assert "window.__timelines" in html
    assert "gsap.timeline" in html

    # Scene timing attributes
    assert 'data-start="0"' in html
    assert "data-duration=" in html

    # Brand + safe zone
    assert "Signhify Studio" in html
    assert "safe-zone" in html

    # Subtitles: each of the 5 scenes has a synced sub element
    for i in range(1, 6):
        assert f'id="sub-{i}"' in html

    # Audio block only when audio_file set
    if audio:
        assert "<audio" in html
        assert f'src="{audio}"' in html
    else:
        assert "<audio" not in html

    # Logo reference only when logo_file set
    if logo:
        assert logo in html


@pytest.mark.parametrize("template_name", ALL_TEMPLATES)
def test_no_full_narration_duplication_in_new_templates(template_name):
    """Scene bodies must NOT repeat the full narration (that lives in the
    single sub-bar). The body shows the short headline instead."""
    html = _render(template_name)
    engine = HyperFramesEngine(workspace_dir="")
    narrations = {
        1: "Run the deploy command in the terminal to ship the build.",
        2: "The neural network model learns from nodes and layers.",
        3: "Our data pipeline automates the flow from input to output.",
        4: "This replaces the old manual way with a new automated process.",
        5: "Grow to 100K users with 10x faster scaling.",
    }
    # Split at the sub-container: everything before it is the scene body
    # region; the sub-bar caption region is after it.
    before_subs, after_subs = html.split('class="sub-container"', 1)
    assert len(html.split('class="sub-container"')) == 2
    for i in range(1, 6):
        narration = narrations[i]
        headline = engine._scene_headline(narration, i - 1, 5)
        # The sub-bar region carries the full narration exactly once
        assert narration in after_subs, f"{template_name} sub-{i} missing narration"
        # The scene body region must NOT contain the full narration
        assert before_subs.count(narration) == 0, (
            f"{template_name} scene {i}: full narration appears in the scene body — "
            "only the headline should be there"
        )
        # The headline (or static body text) is present in the scene region
        if headline not in html:
            # legacy CTA scenes use static branded text instead of the headline
            assert "signhify.dpdns.org" in html or "Build Your 3D Site" in html


def test_scene_elements_have_subtitles():
    """Every scene element has a matching sub-<n> element with same timing."""
    html = _render("neural_network.html.jinja2")
    # Scene elements (data-track-index=1) and subs (data-track-index=2) both
    # carry data-start/data-duration; verify 5 of each exist.
    assert html.count('data-track-index="1"') == 5
    assert html.count('data-track-index="2"') == 5
    # Timing values are shared between scene and its sub
    for i, (start, dur) in enumerate(zip(SCENE_STARTS, SCENE_DURATIONS), 1):
        assert f'data-start="{start}"' in html
        assert f'data-duration="{dur}"' in html


def test_theme_template_files_all_exist():
    """TEMPLATE_FILES must map every theme letter to an existing template file."""
    for theme, template_name in TEMPLATE_FILES.items():
        assert (TEMPLATE_DIR / template_name).exists(), (
            f"theme {theme} -> {template_name} missing"
        )


def test_visual_types_map_to_existing_templates():
    """Every visual_type in the mapping resolves to an existing template file."""
    for visual_type, template_name in VISUAL_TEMPLATE_MAP.items():
        assert (TEMPLATE_DIR / template_name).exists(), (
            f"visual_type {visual_type} -> {template_name} missing"
        )


def test_new_scene_kinds_covered_by_visual_map():
    """The new scene kinds must all map to templates."""
    for kind in ("3d_neural", "3d_dataflow", "3d_terminal", "3d_compare", "3d_chart"):
        assert kind in VISUAL_TEMPLATE_MAP
        assert HyperFramesEngine.template_for_visual(kind) in ALL_TEMPLATES


def test_engine_compiles_60_with_new_templates(tmp_path):
    """compile_composition_60 succeeds with each new template and writes a
    valid composition + scene plan."""
    engine = HyperFramesEngine(workspace_dir=tmp_path)
    script = (
        "Run the deploy command in the terminal to ship the build. "
        "The neural network model learns from nodes and layers. "
        "Our data pipeline automates the flow from input to output. "
        "This replaces the old manual way with a new automated process. "
        "Grow to 100K users with 10x faster scaling."
    )
    for template_name in ALL_TEMPLATES:
        out = tmp_path / template_name.replace(".jinja2", "")
        out.mkdir(parents=True, exist_ok=True)
        plan = engine.build_scene_plan_60(script, "AI Automation", 60.0, 9)
        comp, plan_out = engine.compile_composition_60(
            "AI Automation", script, plan, duration=60.0,
            target_dir=out, template_name=template_name, theme="F",
        )
        html = (comp / "index.html").read_text(encoding="utf-8")
        assert "window.__timelines" in html
        assert "Signhify Studio" in html
        assert (comp / "scene_plan.json").exists()


def test_content_aware_visual_scoring():
    """Keyword scoring assigns the right visual kind per narration."""
    engine = HyperFramesEngine(workspace_dir="")
    cases = [
        ("Run npm deploy and push the build", "3d_terminal"),
        ("The neural network model has nodes", "3d_neural"),
        ("The data pipeline automates the flow", "3d_dataflow"),
        ("This replaces the old manual way", "3d_compare"),
        ("Grow to 100K users with 10x scaling", "3d_chart"),
        ("Nothing relevant here at all", "3d_showcase"),
    ]
    for text, expected in cases:
        assert engine._scene_visual(text, 1, 9) == expected, text
