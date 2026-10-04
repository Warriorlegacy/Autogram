"""
Tests for the reusable 3D kinetic-type system (renderer/reels_shared/).

Offline, no rendering: assert CSS classes exist, JS API exists, the Jinja2
partial and demo template compile and reference the treatments correctly.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "renderer" / "reels_shared"
TEMPLATES = ROOT / "renderer" / "templates" / "reels"

CSS = (SHARED / "kinetic_type.css").read_text(encoding="utf-8")
JS = (SHARED / "kinetic_type.js").read_text(encoding="utf-8")


def test_css_has_three_treatments_and_helpers():
    for cls in (".kt-3d", ".kt-word", ".kt-layer", ".kt-accent", ".kt-accent2",
                ".kt-size-xl", ".kt-size-lg", ".kt-size-md",
                ".kt-glow-strong", ".kt-glow-soft", ".kt-shine"):
        assert cls in CSS, f"missing CSS class {cls}"
    # House extrusion shadows present in the default letter treatment
    assert "0 1px 0" in CSS and "0 6px 14px" in CSS
    assert ".ch" in CSS and ".ch.g" in CSS


def test_js_exposes_kinetic_text_api():
    assert "window.KineticText" in JS
    for fn in ("splitLetters", "splitWords", "buildLayers", "animate", "applyKineticText"):
        assert fn in JS, f"missing JS function {fn}"
    assert "data-kinetic" in JS
    assert "back.out" in JS  # spring-like ease used


def test_kinetic_head_partial_compiles_and_inlines():
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    # Provide the inlined file contents via template globals (the pipeline
    # reads the shared files and passes them in as read_kinetic_css/js).
    env.globals["read_kinetic_css"] = CSS
    env.globals["read_kinetic_js"] = JS
    out = env.get_template("_kinetic_head.html.jinja2").render()
    assert "kt-3d" in out and "KineticText" in out
    assert "Plus+Jakarta+Sans" in out  # Google Fonts import URL (spaces are +)


def test_kinetic_demo_compiles_and_references_treatments():
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    # _kinetic_head include resolves read_* globals; give it real content.
    env.globals["read_kinetic_css"] = CSS
    env.globals["read_kinetic_js"] = JS
    out = env.get_template("kinetic_demo.html.jinja2").render(audio_file="")
    assert "window.__timelines" in out
    assert "kinetic_demo" in out
    assert 'data-start="' in out and 'data-duration="' in out
    # each of the 3 treatments appears in markup
    assert "data-kinetic=\"letters\"" in out
    assert "data-kinetic=\"words\"" in out
    assert "data-kinetic=\"layers\"" in out
    # single caption per scene (sub-bar), narration not duplicated in body
    assert out.count("class=\"sub-bar") == 3
    assert "ApplyKineticText" in out or "applyKineticText" in out
