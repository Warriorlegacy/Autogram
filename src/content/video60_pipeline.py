"""Autonomous 60s Reel pipeline: script -> voice -> HyperFrames -> Remotion -> QA -> Reel -> Story.

Slot key: YYYY-MM-DD + slot (morning/afternoon/night). Idempotent: a completed
slot exits cleanly without republishing. Dry-run executes render+QA, skips publish.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
THEMES = ["A", "B", "C", "D", "E"]


def resolve_slot(now: datetime | None = None, override: str | None = None) -> tuple[str, str]:
    now = now or datetime.now()
    day = now.strftime("%Y-%m-%d")
    if override in ("morning", "afternoon", "night"):
        return day, override
    h = now.hour
    slot = "morning" if h < 12 else "afternoon" if h < 17 else "night"
    # GitHub cron runs in UTC: 05->morning, 09->afternoon, 15->night IST mapping
    gh = os.getenv("SLOT_HINT", "")
    if gh in ("morning", "afternoon", "night"):
        slot = gh
    return day, slot


def slot_dir(day: str, slot: str) -> Path:
    p = REPO_ROOT / "output" / day / slot
    p.mkdir(parents=True, exist_ok=True)
    return p


def slot_complete(day: str, slot: str) -> dict | None:
    meta = slot_dir(day, slot) / "metadata.json"
    if meta.exists():
        try:
            d = json.loads(meta.read_text(encoding="utf-8"))
            if d.get("status") == "PUBLISHED" and d.get("reel_media_id"):
                return d
        except Exception:
            pass
    # content-memory cross-check
    try:
        mem = json.loads((REPO_ROOT / "data" / "content-memory.json").read_text(encoding="utf-8"))
        key = f"{day}-{slot}"
        for p in mem.get("recent_posts", []):
            if p.get("slot_key") == key and p.get("status") == "PUBLISHED":
                return p
    except Exception:
        pass
    return None


def pick_theme(force: str = "", day: str = "", slot: str = "") -> str:
    if force in THEMES:
        return force
    order = {"morning": 0, "afternoon": 1, "night": 2}
    try:
        mem = json.loads((REPO_ROOT / "data" / "content-memory.json").read_text(encoding="utf-8"))
        n = len(mem.get("recent_posts", []))
    except Exception:
        n = 0
    return THEMES[(n + order.get(slot, 0)) % len(THEMES)]


def ffprobe_info(path: str) -> dict:
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,avg_frame_rate,codec_name,pix_fmt,duration",
             "-show_entries", "format=duration,size,bit_rate",
             "-of", "json", path], text=True, timeout=15)
        return json.loads(out)
    except Exception as e:
        return {"error": str(e)}


def qa_final(path: str) -> tuple[bool, str, dict]:
    """FFprobe/FFmpeg QA: 60s, 1080x1920, H264+AAC, 30fps, audio present, sane size."""
    info = ffprobe_info(path)
    if "error" in info and not Path(path).exists():
        return False, f"missing output ({info['error']})", info
    try:
        fmt = info.get("format", {})
        vs = (info.get("streams", []) or [{}])[0]
        dur = float(fmt.get("duration") or vs.get("duration") or 0)
        w, h = int(vs.get("width", 0)), int(vs.get("height", 0))
        fps_s = vs.get("avg_frame_rate", "30/1")
        num, den = (fps_s.split("/") + ["1"])[:2]
        fps = float(num) / float(den or 1)
        size = Path(path).stat().st_size
        # audio present?
        a = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name", "-of", "csv=p=0", path],
            text=True, timeout=10).strip()
        checks = {
            "duration": dur, "width": w, "height": h, "fps": round(fps, 2),
            "vcodec": vs.get("codec_name"), "pix": vs.get("pix_fmt"),
            "acodec": a, "bytes": size,
        }
        if not (58.0 <= dur <= 62.5):
            return False, f"duration {dur:.1f}s not ~=60s", checks
        if (w, h) != (1080, 1920):
            return False, f"resolution {w}x{h} != 1080x1920", checks
        if vs.get("codec_name") != "h264":
            return False, f"vcodec {vs.get('codec_name')} != h264", checks
        if not a:
            return False, "no audio stream", checks
        if size < 200_000:
            return False, f"suspiciously small ({size}b)", checks
        if abs(fps - 30) > 1.5:
            return False, f"fps {fps:.1f} != 30", checks
        return True, "ok", checks
    except Exception as e:
        return False, f"qa exception: {e}", info


def _ffmpeg_fallback(hf_mp4: str, voice_mix: str, srt: str, out: str, logo: str = "") -> str:
    """Deterministic FFmpeg fallback when Remotion CLI is unavailable.

    HyperFrames video (loop/trim to 60) + mixed audio + burned captions + watermark.
    """
    vf = ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
          "eq=contrast=1.06:saturation=1.12")
    # burn captions if srt exists
    filt = vf
    inputs = ["-stream_loop", "-1", "-i", hf_mp4, "-i", voice_mix]
    if Path(srt).exists():
        esc = srt.replace("\\", "/").replace(":", "\\:")
        filt += f",subtitles='{esc}':force_style='FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,BorderStyle=1,Outline=2,Shadow=1,MarginV=380,Alignment=2'"
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", f"[0:v]{filt}[v]",
           "-map", "[v]", "-map", "1:a", "-t", "60",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-c:a", "aac", "-b:a", "160k", "-pix_fmt", "yuv420p",
           "-r", "30", "-movflags", "+faststart", out]
    if logo and Path(logo).exists():
        # subtle watermark overlay instead of complex logo burn
        cmd = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", hf_mp4, "-i", voice_mix,
               "-i", logo, "-filter_complex",
               f"[0:v]{vf}[base];[2:v]scale=120:120[wm];[base][wm]overlay=880:180:format=auto,"
               f"subtitles='{srt.replace(chr(92), '/').replace(':', chr(92)+':')}'[v]" if Path(srt).exists()
               else f"[0:v]{vf}[base];[2:v]scale=120:120[wm];[base][wm]overlay=880:180[v]",
               "-map", "[v]", "-map", "1:a", "-t", "60",
               "-c:v", "libx264", "-preset", "medium", "-crf", "19",
               "-c:a", "aac", "-b:a", "160k", "-pix_fmt", "yuv420p",
               "-r", "30", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True, timeout=600, capture_output=True)
    return out


def try_remotion(hf_mp4: str, voice_mix: str, plan: dict, hook: str, theme: str, out: str) -> tuple[bool, str]:
    """Attempt `npx remotion render`; return (ok, status). Never raises."""
    try:
        props = {"scenes": plan["scenes"][:12], "hyperframesVideo": str(Path(hf_mp4).resolve()),
                 "voiceover": str(Path(voice_mix).resolve()), "theme": theme,
                 "hook": hook, "cta": "Follow Signhify.studio for more."}
        prop_file = Path(out).parent / "remotion_props.json"
        prop_file.write_text(json.dumps(props), encoding="utf-8")
        cmd = ["npx", "--yes", "remotion", "render", "src/video/index.ts", "SignhifyReel",
               out, "--props", str(prop_file), "--codec", "h264", "--crf", "19",
               "--width", "1080", "--height", "1920", "--fps", "30",
               "--duration-in-frames", "1800"]
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), timeout=1500,
                           capture_output=True, text=True)
        if r.returncode == 0 and Path(out).exists() and Path(out).stat().st_size > 200_000:
            return True, "remotion-cli"
        logger.warning(f"remotion render failed rc={r.returncode}: {(r.stderr or r.stdout)[-1500:]}")
        return False, f"remotion-cli-rc{r.returncode}"
    except FileNotFoundError:
        return False, "remotion-not-installed"
    except subprocess.TimeoutExpired:
        return False, "remotion-timeout"
    except Exception as e:
        logger.warning(f"remotion attempt failed: {e}")
        return False, f"remotion-error:{e}"


def run_60s_slot(topic_override: str = "", pillar: str | None = None, dry_run: bool = False,
                 force_template: str = "", publish_reel: bool = True,
                 publish_story: bool = True, slot_hint: str = "") -> dict:
    t0 = time.time()
    if slot_hint:
        os.environ["SLOT_HINT"] = slot_hint
    day, slot = resolve_slot(override=slot_hint or None)
    key = f"{day}-{slot}"
    outdir = slot_dir(day, slot)
    report: dict = {"run_id": os.getenv("GITHUB_RUN_ID", f"local-{int(t0)}"),
                    "slot": slot, "slot_key": key, "dry_run": dry_run}

    # License: owner scheduled publishing must not be blocked; clients need valid key.
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.auth.licensing import get_active_license_status
        lic = get_active_license_status()
        report["license"] = lic.get("tier")
        if not lic.get("valid") and not dry_run:
            raise PermissionError(f"license gate: {lic.get('reason')}")
    except PermissionError:
        raise
    except Exception as e:
        logger.warning(f"license check skipped ({e})")

    if (done := slot_complete(day, slot)) and not dry_run:
        logger.info(f"slot {key} already PUBLISHED; exiting idempotently")
        return {**report, "status": "SKIPPED_DUPLICATE", "existing": done}

    from src.content.script60 import select_topic_script
    from src.content import audio60
    from src.content.hyperframes_engine import HyperFramesEngine, TARGET_DURATION

    theme = pick_theme(force_template, day, slot)
    report["theme"] = theme

    # 1-8. Topic/hooks/script/scene/caption
    front = select_topic_script(pillar, topic_override or None)
    report.update({k: front[k] for k in ("topic", "pillar", "hook", "words", "llm_provider", "script_hash")})
    (outdir / "topic.json").write_text(json.dumps({k: front[k] for k in
        ("topic", "pillar", "angle", "source", "hook", "hooks")}, indent=2), encoding="utf-8")
    (outdir / "script.json").write_text(json.dumps(
        {"script": front["script"], "words": front["words"]}, indent=2), encoding="utf-8")
    (outdir / "scene_plan.json").write_text(json.dumps(front["scene_plan"], indent=2), encoding="utf-8")
    (outdir / "caption.txt").write_text(front["caption"] + "\n", encoding="utf-8")

    # 9-10. Voiceover + fit to 60
    audio = audio60.synthesize(front["script"], str(outdir / "voiceover_raw.mp3"))
    report["voice_provider"] = audio.provider
    voice60, _ = audio60.stretch_to_60(audio.path)
    report["voice_duration"] = audio60.probe_duration(voice60)

    # 12. Captions (phrase-level, synced to scene_plan)
    srt = audio60.phrase_captions(front["scene_plan"], str(outdir / "captions.srt"))

    # 13. Music (procedural, royalty-safe) + mix under speech
    music = audio60.procedural_music(str(outdir / "music_bed.m4a"))
    mixed = audio60.mix_voice_music(voice60, music, str(outdir / "mixed_audio.m4a"))

    # 11/14. HyperFrames 60s composition (mandatory render path)
    hf_dir = outdir / "hyperframes"
    eng = HyperFramesEngine(workspace_dir=hf_dir)
    comp_dir, plan60 = eng.compile_composition_60(
        topic=front["topic"], script_text=front["script"],
        scene_plan=[dict(s) for s in front["scene_plan"]["scenes"]],
        audio_path=mixed, duration=TARGET_DURATION, target_dir=hf_dir, theme=theme)
    hf_mp4 = str(outdir / "hyperframes_scenes.mp4")
    hf_res = eng.render_reel(topic=front["topic"], script_text=front["script"],
                             audio_path=mixed, output_path=hf_mp4,
                             duration=TARGET_DURATION, timeout=900,
                             template_name=__import__("src.content.hyperframes_engine", fromlist=["TEMPLATE_FILES"])  # noqa
                             .TEMPLATE_FILES.get(theme, "marketing_promo.html.jinja2"))
    report["hyperframes_status"] = "ok"
    report["hyperframes_mp4"] = hf_res["video_path"]

    # 15. Remotion composition, fallback to FFmpeg
    final = str(outdir / "final_reel.mp4")
    ok, rem_status = try_remotion(hf_res["video_path"], mixed, front["scene_plan"], front["hook"], theme, final)
    report["remotion_status"] = rem_status
    if not ok:
        logo = str(REPO_ROOT / "assets" / "signhify-logo-vector.jpeg")
        _ffmpeg_fallback(hf_res["video_path"], mixed, srt, final, logo if Path(logo).exists() else "")
        report["remotion_status"] = rem_status + "+ffmpeg-fallback"

    # 17/23. QA gate (fail-closed)
    passed, reason, checks = qa_final(final)
    report.update({"qa": reason, "qa_checks": checks,
                   "final_duration": checks.get("duration"),
                   "video_bytes": checks.get("bytes")})
    if not passed:
        report["status"] = "QA_FAILED"
        (outdir / "metadata.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        raise RuntimeError(f"QA rejected final_reel.mp4: {reason} {checks}")

    video_hash = hashlib.sha256(Path(final).read_bytes()[:1_000_000]).hexdigest()[:16]
    report["video_hash"] = video_hash

    # 19-22. Hosting + Reel + Story (same MP4)
    reel_id, story_id, story_status, public_url = None, None, "SKIPPED", ""
    if dry_run or not publish_reel:
        report["status"] = "DRY_RUN_OK"
    else:
        sys.path.insert(0, str(REPO_ROOT))
        from scripts.storage_helper import upload_to_supabase
        from src.instagram.publisher import publisher
        public_url = upload_to_supabase(final)
        report["public_url"] = public_url
        for attempt in range(3):  # exponential backoff
            try:
                reel_id = publisher.publish_reel(public_url, front["caption"])
                break
            except Exception as e:
                logger.warning(f"reel publish attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt * 10)
        if not reel_id:
            raise RuntimeError("reel publish failed after 3 attempts")
        report["reel_media_id"] = reel_id
        if publish_story:
            try:
                story_id = publisher.publish_story(public_url)
                story_status = "PUBLISHED"
            except Exception as e:
                story_status = f"UNAVAILABLE_OR_FAILED: {e}"
        report["story_status"] = story_status
        report["story_media_id"] = story_id
        report["status"] = "PUBLISHED"

    # Memory record (idempotency + anti-repetition)
    try:
        mem_f = REPO_ROOT / "data" / "content-memory.json"
        mem = json.loads(mem_f.read_text(encoding="utf-8")) if mem_f.exists() else {"recent_posts": []}
        mem.setdefault("recent_posts", []).insert(0, {
            "date": day, "slot_key": key, "slot": slot, "pillar": front["pillar"],
            "topic": f"[Reel60] {front['topic']}", "hook": front["hook"],
            "template": theme, "script_hash": front["script_hash"], "video_hash": video_hash,
            "reel_media_id": reel_id, "story_media_id": story_id,
            "status": report.get("status"), "score": 95.0})
        mem["recent_posts"] = mem["recent_posts"][:120]
        mem_f.write_text(json.dumps(mem, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning(f"memory update failed: {e}")

    report["elapsed_s"] = round(time.time() - t0, 1)
    (outdir / "metadata.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (outdir / "publish_result.json").write_text(json.dumps(
        {k: report.get(k) for k in ("status", "reel_media_id", "story_media_id",
                                    "story_status", "public_url", "slot_key")}, indent=2), encoding="utf-8")
    # Concise production log (no secrets)
    for k in ("run_id", "slot", "topic", "hook", "words", "voice_provider", "voice_duration",
              "theme", "remotion_status", "final_duration", "video_bytes",
              "status", "reel_media_id", "story_status"):
        logger.info(f"REPORT {k}={report.get(k)}")
    return report
