"""
tests/test_video_studio.py
Tests the Signhify video studio: brief validation, storyboard timing, template
compilation, the QA gate, packaging, and CLI wiring.

No network, no npx/ffmpeg render. The only ffmpeg work is frame extraction from
an already-rendered artifact, and that test skips when the artifact is absent.
"""

import json
from pathlib import Path

import pytest

from video_studio import brief as brief_mod
from video_studio import instagram as ig_mod
from video_studio import qa as qa_mod
from video_studio import storyboard as sb_mod
from video_studio.brief import Brief, Caption, Scene, banned_phrases
from video_studio.cli import _mark_published, main
from video_studio.instagram import (CredentialsError, PublishError, credentials,
                                    publish_reel)
from video_studio.publish import _ts, build_caption, write_package, write_srt
from video_studio.qa import inspect, write_report
from video_studio.storyboard import CaptionCue, compile_storyboard

REPO_ROOT = brief_mod.REPO_ROOT
REEL = REPO_ROOT / "video_studio" / "output" / "signhify-prompt-to-3d-site" / "reel.mp4"
QA_DEMO_REEL = REPO_ROOT / "workspace" / "final_reel.mp4"

needs_reel = pytest.mark.skipif(not REEL.exists(), reason="no rendered reel artifact")


@pytest.fixture
def work_dir(tmp_path, monkeypatch):
    """Redirect write_project output so tests never touch video_studio/work."""
    d = tmp_path / "work"
    monkeypatch.setattr(sb_mod, "WORK_DIR", d)
    return d


def brief_data(**over):
    d = {
        "slug": "t-demo",
        "title": "Signhify",
        "hook": "A plain, specific hook.",
        "scenes": [
            {"id": "a", "visual": "hook", "duration": 4.0, "narration": "One. Two."},
            {"id": "b", "visual": "metrics", "duration": 5.0, "headline": "Proof",
             "metrics": [{"v": "400+", "k": "frames"}]},
        ],
    }
    d.update(over)
    return d


def write_brief(tmp_path, **over):
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief_data(**over)), encoding="utf-8")
    return p


def make_brief(**over):
    return Brief.model_validate(brief_data(**over))


# --- 1. brief schema ------------------------------------------------------


def test_valid_brief_parses(tmp_path):
    b = Brief.model_validate(brief_data())
    assert b.slug == "t-demo"
    assert [s.id for s in b.scenes] == ["a", "b"]
    assert b.total_duration() == 9.0
    assert b.width == 1080 and b.height == 1920


def test_load_brief_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        brief_mod.load_brief(tmp_path / "nope.json")


@pytest.mark.parametrize("slug", ["bad slug", "bad/slug", "bad!slug", "", "slug with spaces"])
def test_slug_rejects_illegal_chars(slug):
    # Slug becomes a directory name, so anything path-hostile must fail here.
    with pytest.raises(ValueError):
        Brief(slug=slug, title="T", hook="H")


@pytest.mark.parametrize("accent", ["red", "E05A36", "#FFF", "#GGGGGG", "#E05A361"])
def test_accent_rejects_non_hex(accent):
    with pytest.raises(ValueError):
        Brief(slug="ok", title="T", hook="H", accent=accent)


def test_accent_accepts_hex_and_empty():
    assert Brief(slug="ok", title="T", hook="H", accent="#E05A36").accent == "#E05A36"
    assert Brief(slug="ok", title="T", hook="H").accent == ""


def test_caption_rejects_bad_timing():
    with pytest.raises(ValueError):
        Caption(text="x", start=-1.0, end=1.0)
    with pytest.raises(ValueError):
        Caption(text="x", start=1.0, end=0.5)
    with pytest.raises(ValueError):
        Caption(text="x", start=1.0, end=0.0)
    assert Caption(text="x", start=1.0, end=2.0).end == 2.0


@pytest.mark.parametrize("dur", [0, -1.0])
def test_scene_rejects_nonpositive_duration(dur):
    with pytest.raises(ValueError):
        Scene(id="s", visual="hook", duration=dur)


# --- 2. brand avoid-list guard -------------------------------------------


def test_banned_phrases_come_from_brand_json():
    bp = banned_phrases()
    assert len(bp) > 3
    assert "game-changer" in bp
    assert all(p == p.strip().lower() for p in bp)


@pytest.mark.parametrize("phrase", ["game-changer", "seamless", "dive into", "unlock the power of"])
def test_banned_hits_flags_real_brand_phrases(phrase):
    assert phrase in banned_phrases(), f"{phrase!r} is no longer on the brand avoid-list"
    b = Brief(slug="bad", title="T", hook=f"Copy that says {phrase} here.", scenes=[])
    assert phrase in b.banned_hits()


def test_banned_hits_scans_scene_copy_not_just_the_hook():
    b = Brief(slug="bad", title="T", hook="Clean hook.",
              scenes=[Scene(id="s", visual="hook", duration=1.0, headline="A game-changer tool")])
    assert b.banned_hits() == ["game-changer"]


def test_clean_brief_has_no_banned_hits():
    assert make_brief().banned_hits() == []


# --- 3. storyboard timing -------------------------------------------------


def test_scene_starts_are_contiguous_and_monotonic():
    sb = compile_storyboard(make_brief())
    assert sb.scenes[0].start == 0.0
    for prev, cur in zip(sb.scenes, sb.scenes[1:]):
        assert cur.start == pytest.approx(prev.start + prev.duration)
    assert all(sb.scenes[i].start <= sb.scenes[i + 1].start for i in range(len(sb.scenes) - 1))


def test_every_scene_ends_at_or_before_endcard():
    sb = compile_storyboard(make_brief())
    for s in sb.scenes:
        assert s.start + s.duration <= sb.endcard_at + 1e-6, s


def test_endcard_at_equals_scene_duration_sum():
    b = make_brief()
    sb = compile_storyboard(b)
    assert sb.endcard_at == pytest.approx(b.total_duration())


def test_total_reserves_endcard_time():
    sb = compile_storyboard(make_brief())
    assert sb.total > sb.endcard_at


def test_caption_timing_is_within_scene_windows():
    sb = compile_storyboard(make_brief())
    windows = {s.id: (s.start, s.start + s.duration) for s in sb.scenes}
    assert sb.captions
    for c in sb.captions:
        assert c.start < c.end
        scene = windows[c.id.split("-")[1]]
        assert c.start >= scene[0] - 1e-6
        assert c.end <= scene[1] + 1e-6
        assert c.end <= sb.total + 1e-6


def test_long_narration_extends_total():
    b = make_brief()
    base = compile_storyboard(b)
    longer = compile_storyboard(b, narration_duration=60.0)
    assert longer.total > base.total
    assert longer.total >= 60.0


# --- 4. caption edge cases ------------------------------------------------


def test_empty_narration_produces_no_cues():
    b = make_brief(scenes=[{"id": "a", "visual": "hook", "duration": 4.0, "narration": ""}])
    assert compile_storyboard(b).captions == []


def test_short_narration_produces_exactly_one_cue():
    b = make_brief(scenes=[{"id": "a", "visual": "hook", "duration": 4.0, "narration": "Hi"}])
    cues = compile_storyboard(b).captions
    assert len(cues) == 1
    assert cues[0].text == "Hi"


def test_punctuation_splits_into_multiple_cues():
    b = make_brief(scenes=[{"id": "a", "visual": "hook", "duration": 9.0,
                            "narration": "One. Two. Three."}])
    cues = compile_storyboard(b).captions
    assert [c.text for c in cues] == ["One.", "Two.", "Three."]
    assert [c.start for c in cues] == sorted(c.start for c in cues)


# --- 5. template compilation ---------------------------------------------


@pytest.fixture
def project(tmp_path, work_dir):
    b = make_brief()
    return b, sb_mod.write_project(b, compile_storyboard(b))


def test_write_project_emits_expected_files(project):
    _, proj = project
    for name in ("index.html", "hyperframes.json", "meta.json", "package.json"):
        assert (proj / name).exists(), name


def test_index_html_starts_with_doctype(project):
    # Regression: a Jinja comment's trailing newline used to precede the doctype,
    # which made the StaticGuard reject every generated composition.
    html = (project[1] / "index.html").read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>")


def test_index_html_has_no_leaked_jinja_syntax(project):
    # Regression: the template's own header comment once rendered into the output.
    html = (project[1] / "index.html").read_text(encoding="utf-8")
    assert "{#" not in html
    assert "{%" not in html


def test_index_html_is_wired_for_hyperframes(project):
    html = (project[1] / "index.html").read_text(encoding="utf-8")
    assert 'data-composition-id="root"' in html
    assert 'window.__timelines["root"]' in html
    assert "gsap.timeline({paused:true})" in html
    assert "#E05A36" in html  # brand accent, default applied when brief omits it


def test_index_html_references_logo_when_copied(project):
    _, proj = project
    html = (proj / "index.html").read_text(encoding="utf-8")
    if (proj / "assets" / "logo.png").exists():
        assert "assets/logo.png" in html


# --- 6. QA gate -----------------------------------------------------------


def test_missing_file_fails(tmp_path):
    rep = inspect(tmp_path / "nope.mp4", tmp_path / "frames")
    assert rep.verdict == "FAIL"
    assert rep.defects


def test_zero_byte_file_fails(tmp_path):
    empty = tmp_path / "empty.mp4"
    empty.write_bytes(b"")
    rep = inspect(empty, tmp_path / "frames")
    assert rep.verdict == "FAIL"
    assert rep.defects


def test_write_report_round_trips(tmp_path):
    rep = inspect(tmp_path / "nope.mp4", tmp_path / "frames")
    p = write_report(rep, tmp_path / "qa" / "qa_report.json", extra={"slug": "x"})
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["verdict"] == "FAIL"
    assert data["slug"] == "x"


@needs_reel
def test_real_reel_passes_inspection(tmp_path):
    rep = inspect(REEL, tmp_path / "frames", expect_audio=True)
    assert rep.verdict == "PASS", rep.defects
    assert (rep.width, rep.height) == (1080, 1920)
    assert rep.video_codec == "h264"
    assert rep.duration == pytest.approx(45.5, abs=1.0)
    assert len(rep.frames_extracted) >= 3
    assert all(Path(f).stat().st_size > 0 for f in rep.frames_extracted)


@needs_reel
def test_real_reel_carries_narration_audio(tmp_path):
    """The demo Reel is muxed with Kokoro narration (AAC)."""
    rep = inspect(REEL, tmp_path / "frames", expect_audio=True)
    assert rep.audio_codec == "aac"


@needs_reel
def test_expect_audio_on_silent_video_is_a_defect(tmp_path):
    """A video WITHOUT an audio stream must be flagged when audio is expected.

    Builds a genuinely silent 1s clip with ffmpeg; reusing an existing artifact
    is fragile because most renders carry a track.
    """
    import subprocess
    silent = tmp_path / "silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    "color=c=black:s=540x960:d=1:r=30", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", str(silent)], capture_output=True, timeout=120)
    assert silent.exists(), "ffmpeg failed to build the silent fixture"
    rep = inspect(silent, tmp_path / "frames", expect_audio=True)
    assert rep.verdict == "FAIL"
    assert any("audio_present" in d for d in rep.defects)


# --- 7. SRT + caption packaging ------------------------------------------


def cue(id, text, start, end):
    return CaptionCue(id=id, text=text, start=start, end=end, dur=round(end - start, 3))


def test_ts_formatting():
    assert _ts(0) == "00:00:00,000"
    assert _ts(59.999) == "00:00:59,999"
    assert _ts(3661.5) == "01:01:01,500"


def test_srt_formats_a_cue_at_a_known_time(tmp_path):
    p = write_srt([cue("c0", "Hello.", 1.5, 2.25)], tmp_path / "captions.srt")
    assert p.read_text(encoding="utf-8").splitlines()[:2] == ["1", "00:00:01,500 --> 00:00:02,250"]


def test_srt_blocks_are_numbered_and_monotonic(tmp_path):
    b = make_brief(scenes=[
        {"id": "a", "visual": "hook", "duration": 6.0, "narration": "One. Two."},
        {"id": "b", "visual": "metrics", "duration": 6.0, "narration": "Three. Four."},
    ])
    sb = compile_storyboard(b)
    assert len(sb.captions) >= 4
    lines = write_srt(sb.captions, tmp_path / "captions.srt").read_text(encoding="utf-8").splitlines()
    blocks = [lines[i:i + 4] for i in range(0, len(lines), 4)]  # index, ts, text, blank
    assert [blk[0] for blk in blocks] == [str(i) for i in range(1, len(blocks) + 1)]
    stamps = [blk[1] for blk in blocks]
    assert stamps == sorted(stamps)


def test_build_caption_is_clean_and_keeps_the_cta():
    b = make_brief()
    cap = build_caption(b, compile_storyboard(b))
    assert b.banned_hits() == []
    assert b.cta in cap
    assert all(p not in cap.lower() for p in banned_phrases())


# --- 8. packaging is inert by default -------------------------------------


def test_write_package_keeps_publishing_disabled(tmp_path):
    b = make_brief()
    sb = compile_storyboard(b)
    out = tmp_path / "pkg"
    manifest = write_package(b, sb, out)

    # Safety-critical: nothing may post unless a caller explicitly opts in.
    assert manifest["publishing"]["enabled"] is False
    assert json.loads((out / "asset_manifest.json").read_text(encoding="utf-8"))["publishing"]["enabled"] is False
    assert manifest["spec"]["duration"] == sb.total
    for name in ("captions.srt", "caption.txt", "storyboard.json", "brief.json", "asset_manifest.json"):
        assert (out / name).exists(), name


# --- 9. CLI wiring --------------------------------------------------------


def test_cli_build_writes_project(tmp_path, work_dir):
    brief_file = write_brief(tmp_path)
    assert main(["build", "--brief", str(brief_file)]) == 0
    assert (work_dir / "t-demo" / "index.html").exists()


def test_cli_build_rejects_banned_phrases(tmp_path, work_dir):
    brief_file = write_brief(tmp_path, hook="This is a game-changer.")
    assert main(["build", "--brief", str(brief_file)]) == 3
    assert not (work_dir / "t-demo").exists()


def test_cli_build_rejects_scene_less_brief(tmp_path, work_dir):
    brief_file = write_brief(tmp_path, scenes=[])
    assert main(["build", "--brief", str(brief_file)]) == 3


def test_cli_qa_on_missing_video_returns_two(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["qa", "--video", "nonexistent.mp4"]) == 2
    assert (tmp_path / "qa_report.json").exists()


# --- 10. self-check demos -------------------------------------------------


def test_demo_brief():
    assert brief_mod.demo().banned_hits() == []


def test_demo_storyboard():
    sb_mod.demo()


def test_demo_publish():
    publish_demo = __import__("video_studio.publish", fromlist=["demo"]).demo
    publish_demo()


@pytest.mark.skipif(not QA_DEMO_REEL.exists(), reason="workspace/final_reel.mp4 absent")
def test_demo_qa(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)  # demo() reads workspace/final_reel.mp4 relatively
    real = qa_mod.extract_frames
    monkeypatch.setattr(qa_mod, "extract_frames",
                        lambda v, out, count=6: real(v, tmp_path / "demo_frames", count))
    qa_mod.demo()



# --- caption timing regressions (defects found by measuring real output) ---

def test_split_cues_keeps_dotted_tokens_intact():
    """Naive '.' splitting broke 'Three.js' into two broken cues."""
    parts = sb_mod._split_cues("No WebGL. No Three.js. Just native scroll.")
    assert parts == ["No WebGL.", "No Three.js.", "Just native scroll."]


def test_split_cues_balances_an_overlong_sentence():
    parts = sb_mod._split_cues(
        "Signhify generates an eight second video, extracts the frames, "
        "and lets native browser scroll replay them as parallax.")
    assert len(parts) == 2
    assert all(p.strip() for p in parts)


def test_cues_respect_reading_speed_budget():
    """Even slots starved long cues; time is now allocated proportionally."""
    b = Brief(slug="rate", title="T", hook="H", scenes=[
        Scene(id="a", visual="hook", duration=8.0,
              narration="Signhify generates an eight second video and extracts the frames. "
                        "Short.")])
    sb = compile_storyboard(b)
    over = [(c.id, len(c.text) / c.dur) for c in sb.captions
            if len(c.text) / c.dur > sb_mod._read_speed() + 0.01]
    assert not over, over


def test_narration_fit_flags_overlong_narration():
    """A scene that cannot speak AND read its line in time must fail closed."""
    b = Brief(slug="fit", title="T", hook="H", scenes=[
        Scene(id="short", visual="hook", duration=1.0,
              narration="Signhify generates an eight second video, extracts every frame, "
                        "and replays them natively across a browser scroll timeline.")])
    over = sb_mod.narration_fit(b)
    assert over and over[0]["id"] == "short"
    assert over[0]["short_by"] > 0
    assert main(["build", "--brief", str(_write(b, tmp_path := Path(b.caption[0] if False else "scratch/nf.json")))]) == 4


def test_narration_fit_accepts_a_healthy_brief():
    b = Brief(slug="ok", title="T", hook="H", scenes=[
        Scene(id="a", visual="hook", duration=8.0, narration="No WebGL. No Three.js.")])
    assert sb_mod.narration_fit(b) == []


def _write(b: Brief, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(b.model_dump_json(indent=2), encoding="utf-8")
    return path


# --- 11. Instagram Reels publishing (opt-in, fail-closed, no secrets) ------

IG_ENV_VARS = ("IG_USER_ID", "IG_ACCESS_TOKEN", "META_API_VERSION",
               "INSTAGRAM_BUSINESS_ACCOUNT_ID", "META_GRAPH_ACCESS_TOKEN",
               "PUBLIC_CDN_BASE", "PUBLISH_DRY_RUN")
PUBLIC_VIDEO_URL = "https://cdn.example.com/t-demo/reel.mp4"
SECRET = "EAAB-super-secret-token-value"


@pytest.fixture
def ig_env(monkeypatch):
    """Strip every Instagram/CDN var, then let a test set only what it needs."""
    for name in IG_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.fixture
def no_network(monkeypatch):
    """Any HTTP call from the publisher is a test failure, not a slow test."""
    def boom(*a, **k):
        raise AssertionError("test attempted a network call")

    monkeypatch.setattr(ig_mod.requests, "post", boom)
    monkeypatch.setattr(ig_mod.requests, "get", boom)
    return monkeypatch


def test_credentials_reports_missing_names_only(ig_env):
    with pytest.raises(CredentialsError) as e:
        credentials()
    msg = str(e.value)
    for name in ("IG_USER_ID", "INSTAGRAM_BUSINESS_ACCOUNT_ID",
                 "IG_ACCESS_TOKEN", "META_GRAPH_ACCESS_TOKEN"):
        assert name in msg


def test_credentials_error_never_contains_a_value(ig_env):
    ig_env.setenv("IG_USER_ID", "17841400000000000")
    with pytest.raises(CredentialsError) as e:
        credentials()
    assert "17841400000000000" not in str(e.value)


def test_credentials_resolves_env_and_default_version(ig_env):
    ig_env.setenv("IG_USER_ID", "178414")
    ig_env.setenv("IG_ACCESS_TOKEN", SECRET)
    creds = credentials()
    assert creds["api_version"] == "v26.0"
    assert creds["access_token"] == SECRET
    ig_env.setenv("META_API_VERSION", "v25.0")
    assert credentials()["api_version"] == "v25.0"


def test_credentials_accepts_the_spec_aliases(ig_env):
    ig_env.setenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "178414")
    ig_env.setenv("META_GRAPH_ACCESS_TOKEN", SECRET)
    assert credentials()["ig_user_id"] == "178414"


def test_publish_reel_dry_run_sends_nothing(ig_env, no_network, tmp_path, capsys):
    ig_env.setenv("IG_USER_ID", "178414")
    ig_env.setenv("IG_ACCESS_TOKEN", SECRET)
    res = publish_reel("t-demo", PUBLIC_VIDEO_URL, "A caption. #tag", dry_run=True, out_dir=tmp_path)
    assert res["ok"] is True
    assert res["dry_run"] is True
    assert res["media_id"] is None
    printed = capsys.readouterr().out
    assert "media_publish" in printed and SECRET not in printed


def test_publish_result_json_never_holds_a_token(ig_env, no_network, tmp_path):
    ig_env.setenv("IG_USER_ID", "178414")
    ig_env.setenv("IG_ACCESS_TOKEN", SECRET)
    publish_reel("t-demo", PUBLIC_VIDEO_URL, "A caption.", dry_run=True, out_dir=tmp_path)
    row = json.loads((tmp_path / "publish_result.json").read_text(encoding="utf-8"))
    assert set(row) <= {"timestamp", "container_id", "media_id", "status", "ok", "error"}
    assert row["ok"] is True and row["status"] == "DRY_RUN"
    assert SECRET not in json.dumps(row)


def test_dry_run_does_not_flip_the_manifest_flag(ig_env, no_network, tmp_path):
    b = make_brief()
    sb = compile_storyboard(b)
    out = tmp_path / "pkg"
    write_package(b, sb, out)
    publish_reel(b.slug, PUBLIC_VIDEO_URL, build_caption(b, sb), dry_run=True, out_dir=out)
    reread = json.loads((out / "asset_manifest.json").read_text(encoding="utf-8"))
    assert reread["publishing"]["enabled"] is False


@pytest.mark.parametrize("url", ["file:///D:/Autogram/reel.mp4",
                                 "http://localhost:8000/reel.mp4",
                                 "https://127.0.0.1/reel.mp4",
                                 "D:/Autogram/output/t-demo/reel.mp4", ""])
def test_publish_reel_refuses_a_non_public_video_url(ig_env, no_network, tmp_path, url):
    ig_env.setenv("IG_USER_ID", "178414")
    ig_env.setenv("IG_ACCESS_TOKEN", SECRET)
    with pytest.raises(PublishError) as e:
        publish_reel("t-demo", url, "A caption.", dry_run=False, out_dir=tmp_path)
    assert "https" in str(e.value)
    assert not (tmp_path / "publish_result.json").exists()  # refused before anything ran


def test_live_publish_without_credentials_uses_exit_code_five(ig_env, no_network, tmp_path):
    with pytest.raises(CredentialsError) as e:
        publish_reel("t-demo", PUBLIC_VIDEO_URL, "A caption.", dry_run=False, out_dir=tmp_path)
    assert e.value.code == 5


def test_quota_exhaustion_refuses_before_any_request(ig_env, no_network, monkeypatch, tmp_path):
    ig_env.setenv("IG_USER_ID", "178414")
    ig_env.setenv("IG_ACCESS_TOKEN", SECRET)
    monkeypatch.setattr(ig_mod, "publishing_quota", lambda: {"quota_usage": ig_mod.POSTS_PER_24H})
    with pytest.raises(PublishError) as e:
        publish_reel("t-demo", PUBLIC_VIDEO_URL, "A caption.", dry_run=False, out_dir=tmp_path)
    assert "quota" in str(e.value)


def test_api_failure_is_exit_code_six_and_gets_recorded(ig_env, monkeypatch, tmp_path):
    ig_env.setenv("IG_USER_ID", "178414")
    ig_env.setenv("IG_ACCESS_TOKEN", SECRET)
    monkeypatch.setattr(ig_mod, "publishing_quota", lambda: {"quota_usage": 0})

    def boom(*a, **k):
        raise ig_mod.requests.RequestException("connection reset")

    monkeypatch.setattr(ig_mod.requests, "post", boom)
    with pytest.raises(PublishError) as e:
        publish_reel("t-demo", PUBLIC_VIDEO_URL, "A caption.", dry_run=False, out_dir=tmp_path)
    assert e.value.code == 6
    assert SECRET not in str(e.value)
    row = json.loads((tmp_path / "publish_result.json").read_text(encoding="utf-8"))
    assert row["ok"] is False and row["status"] == "FAILED" and row["media_id"] is None


def test_mark_published_records_the_media_id(tmp_path):
    b = make_brief()
    out = tmp_path / "pkg"
    manifest = write_package(b, compile_storyboard(b), out)
    _mark_published(manifest, out, b.slug,
                    {"media_id": "17900000000000001", "timestamp": "2026-10-11T09:00:00+00:00"},
                    PUBLIC_VIDEO_URL)
    reread = json.loads((out / "asset_manifest.json").read_text(encoding="utf-8"))
    assert reread["publishing"]["enabled"] is True
    assert reread["publishing"]["media_id"] == "17900000000000001"


# --- AI generation: gates and safety (no network; provider calls are stubbed) ---

def test_ai_brief_rejects_banned_copy(monkeypatch):
    """A generated brief carrying a banned phrase must never be returned."""
    import json as _json
    from video_studio import ai

    bad = {
        "slug": "x", "title": "T", "hook": "This is a game-changer",
        "scenes": [{"id": "s", "visual": "hook", "duration": 6.0,
                    "narration": "This is a game-changer indeed."}]}
    monkeypatch.setattr(ai, "complete", lambda *a, **k: _json.dumps(bad))
    monkeypatch.setattr(ai, "_load_dotenv_override", lambda: None)
    with pytest.raises(ai.GenerationError):
        ai.generate_brief({"slug": "x", "title": "T", "hook": "h", "angle": "a"}, retries=0)


def test_ai_fit_scene_durations_preserves_copy(monkeypatch):
    """Timing repair may grow a scene, never alter the narration words."""
    from video_studio import ai
    b = Brief(slug="f", title="T", hook="H",
              scenes=[Scene(id="a", visual="statement", duration=2.0,
                            narration="Signhify generates an eight second video and extracts frames.")])
    before = b.scenes[0].narration
    notes = ai._fit_scene_durations(b)
    assert notes, "expected a timing repair note"
    assert b.scenes[0].narration == before
    assert b.scenes[0].duration > 2.0
    assert not narration_fit_module(b), "repair must make the scene fit"


def narration_fit_module(b):
    from video_studio.storyboard import narration_fit
    return narration_fit(b)


def test_ai_provider_chain_order():
    """The chain is measured order; the benchmarked winner must lead."""
    from video_studio.ai import PROVIDER_CHAIN
    assert PROVIDER_CHAIN[0][0] == "groq/qwen3.8-27b"
    for _name, fn, env in PROVIDER_CHAIN:
        assert callable(fn) and env


def test_ai_raises_when_no_provider_configured(monkeypatch):
    from video_studio import ai
    for var in ("GROQ_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(ai, "_load_dotenv_override", lambda: None)
    assert ai.available_providers() == []
    with pytest.raises(ai.GenerationError):
        ai.complete("hi", "sys")


def test_scene_tolerates_null_optional_fields():
    """An LLM emits null for unused optionals constantly; that must not fail."""
    sc = Scene.model_validate({"id": "a", "visual": "hook", "duration": 4.0,
                               "headline": None, "subtext": None,
                               "source_url": None, "bullets": None})
    assert sc.headline == "" and sc.subtext == "" and sc.bullets == []
    m = Scene.model_validate({"id": "b", "visual": "metrics", "duration": 4.0,
                              "metrics": ["400+ frames per site"]})
    assert m.metrics[0]["v"] == "400+" and m.metrics[0]["k"] == "frames per site"


def test_captions_meet_reading_budget_by_construction():
    """Every cue gets at least its own reading time, never less."""
    from video_studio.storyboard import build_captions, _read_speed
    scenes = [{"id": "a", "start": 0.0, "duration": 12.0,
               "narration": "Short one. And now a considerably longer sentence that "
                            "needs far more reading time than the short one."}]
    for c in build_captions(scenes, 30):
        assert len(c.text) / c.dur <= _read_speed() + 0.01, c
