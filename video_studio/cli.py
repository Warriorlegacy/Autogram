"""Signhify video studio CLI.

    python -m video_studio build   --brief briefs/x.json
    python -m video_studio render  --brief briefs/x.json
    python -m video_studio qa      --video out/reel.mp4
    python -m video_studio package --brief briefs/x.json

Publishing is opt-in and disabled by default. No stage silently succeeds.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .brief import Brief, load_brief
from .publish import build_caption, write_package, extract_cover
from .qa import inspect, write_report
from .render import RenderError, check_project, mux_audio, render_project
from .storyboard import WORK_DIR, compile_storyboard, write_project

OUT_DIR = Path(__file__).parent / "output"


def _load(args) -> Brief:
    if args.brief:
        b = load_brief(args.brief)
    else:
        raise SystemExit("--brief is required")
    if args.slug:
        b.slug = args.slug
    return b


def _validate(b) -> int:
    """Shared fail-closed gate: banned copy, empty scenes, narration overrun."""
    from .storyboard import narration_fit
    hits = b.banned_hits()
    if hits:
        print(f"[FAIL] Banned brand phrases in audience copy: {hits}", file=sys.stderr)
        return 3
    if not b.scenes:
        print("[FAIL] brief has no scenes", file=sys.stderr)
        return 3
    over = narration_fit(b)
    if over:
        print("[FAIL] Scenes too short for their narration "
              "(lengthen the scene or shorten the line):", file=sys.stderr)
        for o in over:
            print(f"       scene {o['id']}: {o['duration']}s slot, needs {o['needed']}s "
                  f"(short by {o['short_by']}s)", file=sys.stderr)
        return 4
    return 0


def cmd_build(args) -> int:
    b = _load(args)
    rc = _validate(b)
    if rc:
        return rc
    sb = compile_storyboard(b)
    proj = write_project(b, sb)
    print(f"[OK] project: {proj}")
    print(f"[OK] scenes={len(sb.scenes)} captions={len(sb.captions)} total={sb.total}s endcard@{sb.endcard_at}s")
    return 0


def cmd_render(args) -> int:
    b = _load(args)
    rc = _validate(b)
    if rc:
        return rc
    sb = compile_storyboard(b)
    log: list[str] = []
    track = None
    out = OUT_DIR / b.slug
    out.mkdir(parents=True, exist_ok=True)
    if args.audio:
        # Synthesize first: the narration duration can extend the timeline, and
        # captions must be timed from the real speech, not the authored guess.
        from .audio import concat_wavs, synthesize_scenes
        print("[2/7] synthesizing narration (Kokoro, Apache-2.0) ...")
        files, speech = synthesize_scenes(b, sb, log)
        if files:
            sb.total = max(sb.total, round(speech + 0.25 * len(files), 3))
            track = concat_wavs(files, out / "audio" / "narration.wav")
            print(f"      narration: {len(files)} scenes, {speech}s speech, track={track}")
        else:
            print("      no narration text or no provider; continuing silent")

    proj = write_project(b, sb)

    print("[3/7] hyperframes check ...")
    gate = check_project(proj, log)
    print(f"      gate clean={gate['clean']}")
    if args.skip_gate and not gate["clean"]:
        print("      (--skip-gate: continuing despite gate failure)")

    print(f"[4/7] rendering {sb.width}x{sb.height} @{sb.fps}fps quality={args.quality} ...")
    video = render_project(proj, out / "reel.mp4", log, fps=sb.fps, quality=args.quality)
    print(f"      video: {video}")

    if args.audio:
        if track:
            print("[5/7] muxing narration (two-pass loudnorm) ...")
            mux_audio(video, track, out / "reel.mp4", log)
            print(f"      audio muxed: {track}")
        else:
            print("[5/7] no narration produced; continuing without audio")
            log.append("[audio] no track; render continues silently")

    print("[6/7] packaging ...")
    extract_cover(video, out / "cover.jpg")
    manifest = write_package(b, sb, out, video=video)

    print("[7/7] QA ...")
    rep = inspect(video, out / "qa_frames", expect_audio=bool(args.audio),
                  expect_duration=sb.total)
    write_report(rep, out / "qa_report.json", extra={"hyperframes_gate": gate["clean"],
                                                     "slug": b.slug})
    (out / "render.log").write_text("\n\n".join(log), encoding="utf-8")
    (out / "qa_report.md").write_text(_md(rep, sb, gate), encoding="utf-8")

    print(f"[DONE] {video}")
    print(f"       QA: {rep.verdict}  duration={rep.duration}s  {rep.width}x{rep.height}  audio={rep.audio_codec or 'none'}")
    if rep.defects:
        for d in rep.defects:
            print(f"       DEFECT: {d}")
        return 2

    if args.publish:
        return _publish_step(b, sb, out, manifest, args)
    return 0


def _cdn_url(slug: str) -> str:
    """PUBLIC_CDN_BASE is the repo root, so the artifact is at <base>/<slug>/reel.mp4."""
    base = (os.environ.get("PUBLIC_CDN_BASE") or "").strip()
    return f"{base.rstrip('/')}/{slug}/reel.mp4" if base else ""


def _mark_published(manifest: dict, out: Path, slug: str, res: dict, video_url: str) -> None:
    manifest["publishing"] = {"enabled": True, "reason": "published via --publish",
                              "slug": slug, "media_id": res.get("media_id"),
                              "published_at": res.get("timestamp"), "video_url": video_url}
    (out / "asset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _publish_step(b, sb, out: Path, manifest: dict, args) -> int:
    """[8/8] Publish — only ever reached with --publish, after QA passed."""
    from .instagram import PublishError, publish_reel
    video_url = args.video_url or _cdn_url(b.slug)
    dry = args.publish_dry_run or os.environ.get("PUBLISH_DRY_RUN", "").lower() in ("1", "true", "yes")
    print(f"[8/8] publishing {'(dry run) ' if dry else ''}slug={b.slug} ...")
    try:
        res = publish_reel(b.slug, video_url, build_caption(b, sb),
                           cover=args.cover_url or None, dry_run=dry, out_dir=out)
    except PublishError as e:
        print(f"[FAIL] publish refused: {e}", file=sys.stderr)
        return e.code
    if not dry and res.get("ok"):
        _mark_published(manifest, out, b.slug, res, video_url)
    print(f"[DONE] publish status={res.get('status')} media_id={res.get('media_id')}")
    return 0


def _md(rep, sb, gate) -> str:
    lines = [f"# QA — {rep.file}", "",
             f"- Verdict: **{rep.verdict}**",
             f"- HyperFrames gate clean: {gate['clean']}",
             f"- Spec: {rep.width}x{rep.height} @{rep.fps}fps, {rep.duration}s, "
             f"{rep.video_codec}/{rep.audio_codec or 'no audio'}, {rep.size_bytes} bytes", "",
             "## Checks", ""]
    for c in rep.checks:
        lines.append(f"- {'PASS' if c['pass'] else 'FAIL'} — {c['check']}: {c['detail']}")
    lines += ["", "## Frames extracted", ""]
    lines += [f"- `{p}`" for p in rep.frames_extracted] or ["- none"]
    lines += ["", "## Remaining defects", ""]
    lines += [f"- {d}" for d in rep.defects] or ["- none"]
    lines += ["", "Visual inspection of the extracted frames is still required; "
              "a passing automated gate is not a production verdict."]
    return "\n".join(lines)


def cmd_qa(args) -> int:
    rep = inspect(Path(args.video), Path(args.frames or "scratch/qa"), expect_audio=not args.no_audio)
    write_report(rep, Path(args.video).with_name("qa_report.json"))
    print(json.dumps({"verdict": rep.verdict, "duration": rep.duration,
                      "spec": f"{rep.width}x{rep.height}@{rep.fps}",
                      "defects": rep.defects}, indent=2))
    return 0 if rep.verdict == "PASS" else 2


def cmd_package(args) -> int:
    b = _load(args)
    sb = compile_storyboard(b)
    out = OUT_DIR / b.slug
    manifest = write_package(b, sb, out)
    print(json.dumps(manifest, indent=2))
    return 0


def cmd_generate(args) -> int:
    """AI-generate a batch of briefs. Writes to briefs/, optionally renders each."""
    from .ai import GenerationError, available_providers, generate_brief, generate_topics, record_topic
    print(f"[ai] providers: {', '.join(available_providers()) or 'NONE CONFIGURED'}")
    if not available_providers():
        print("[FAIL] Set GROQ_API_KEY or GEMINI_API_KEY in .env", file=sys.stderr)
        return 1
    try:
        topics = generate_topics(args.count)
    except GenerationError as e:
        print(f"[FAIL] topic generation: {e}", file=sys.stderr)
        return 1

    briefs_dir = Path(__file__).parent / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    made, failed = [], []
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] {topic.get('slug')}")
        try:
            brief = generate_brief(topic)
        except GenerationError as e:
            print(f"  FAIL {str(e)[:160]}", file=sys.stderr)
            failed.append(topic.get("slug"))
            continue
        rc = _validate(brief)
        if rc:
            print(f"  rejected by validation (exit {rc})", file=sys.stderr)
            failed.append(brief.slug)
            continue
        path = briefs_dir / f"{brief.slug}.json"
        path.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
        print(f"  OK {brief.slug} — {len(brief.scenes)} scenes, {brief.total_duration()}s -> {path.name}")
        record_topic(brief.slug)
        made.append(brief.slug)

        if args.render:
            print(f"  rendering {brief.slug} ...")
            rargs = argparse.Namespace(brief=str(path), slug=brief.slug,
                                       quality=args.quality, audio=args.audio,
                                       skip_gate=False, publish=False,
                                       publish_dry_run=False, video_url="", cover_url="")
            rc = cmd_render(rargs)
            if rc:
                print(f"  render exit {rc}", file=sys.stderr)

    print(f"\n[DONE] {len(made)} briefs written, {len(failed)} failed")
    if made:
        print("  " + ", ".join(made))
    return 0 if made else 1


def cmd_token_check(args) -> int:
    """Read-only credential health. Use in a cron job to alert before an outage."""
    from .instagram import token_health
    h = token_health()
    kind = h.get("token_kind") or "none"
    if h.get("expiry_known") and h.get("never_expires"):
        expiry = "never expires (Meta reports expires_at=0)"
    elif h.get("days_left") is not None:
        expiry = f"expires in {h['days_left']} days"
    else:
        expiry = "unknown (Meta did not report an expiry for this token)"
    print(f"token kind   : {kind}")
    print(f"account      : @{h.get('username') or '?'} (media {h.get('media_count')})")
    print(f"expiry       : {expiry}")
    print(f"quota used   : {h.get('quota_used')}/{h.get('quota_total')} (rolling 24h)")
    if not h.get("ok"):
        print(f"[FAIL] token unusable: {h.get('error')}", file=sys.stderr)
        return 5
    # A user token is the failure mode we are preventing: it dies with the
    # owner's login (error 190/460) and cannot be refreshed.
    if kind == "user":
        print("[WARN] publishing with a USER token. A password change kills it "
              "permanently (error 190/460, no refresh path). Prefer "
              "META_GRAPH_ACCESS_TOKEN (Page token).", file=sys.stderr)
        return 5
    dl = h.get("days_left")
    if dl is not None and dl < 7:
        print(f"[WARN] token expires in {dl} days — re-authorize now.", file=sys.stderr)
        return 5
    print("[OK] publishing credentials healthy")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="video_studio")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("build", "render", "package"):
        sp = sub.add_parser(name)
        sp.add_argument("--brief", required=True)
        sp.add_argument("--slug", default="")
        sp.set_defaults(fn=cmd_build if name == "build" else (cmd_render if name == "render" else cmd_package))
        if name == "render":
            sp.add_argument("--quality", default="draft", choices=["draft", "standard", "high"])
            sp.add_argument("--audio", action="store_true", help="synthesize + mux narration")
            sp.add_argument("--skip-gate", action="store_true")
            sp.add_argument("--publish", action="store_true",
                            help="publish the reel to Instagram after QA passes (off by default)")
            sp.add_argument("--publish-dry-run", action="store_true",
                            help="with --publish: print the exact Meta payloads, send nothing")
            sp.add_argument("--video-url", default="",
                            help="public https URL of reel.mp4; falls back to PUBLIC_CDN_BASE")
            sp.add_argument("--cover-url", default="",
                            help="public https URL of cover.jpg; Meta picks a frame if omitted")
    sq = sub.add_parser("qa")
    sq.add_argument("--video", required=True)
    sq.add_argument("--frames", default="")
    sq.add_argument("--no-audio", action="store_true")
    sq.set_defaults(fn=cmd_qa)
    st = sub.add_parser("token-check",
                        help="verify Instagram publishing credentials (read-only)")
    st.set_defaults(fn=cmd_token_check)
    sg = sub.add_parser("generate", help="AI-generate N content briefs (optionally render)")
    sg.add_argument("--count", type=int, default=7)
    sg.add_argument("--render", action="store_true", help="also render each brief")
    sg.add_argument("--quality", default="draft", choices=["draft", "standard", "high"])
    sg.add_argument("--audio", action="store_true")
    sg.set_defaults(fn=cmd_generate)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except (RenderError, FileNotFoundError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

