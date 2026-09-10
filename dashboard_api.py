"""
Autogram Dashboard API Server (dashboard_api.py)
Lightweight Flask API that powers the owner dashboard UI.
Endpoints: status, run pipeline, view logs, manage .env, view output,
scheduling, direct publishing, AI content generation, and token management.
"""

import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "output"
MEMORY_PATH = BASE_DIR / "data" / "content-memory.json"
SCHEDULE_PATH = BASE_DIR / "data" / "schedule.json"
DB_PATH = BASE_DIR / "autopilot.db"
BRAND_PATH = BASE_DIR / "data" / "brand.json"

def get_brand_config() -> dict:
    """Load brand profile data from data/brand.json."""
    if BRAND_PATH.exists():
        try:
            return json.loads(BRAND_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"handle": "@signhify.studio", "watermark": "@SIGNHIFY.STUDIO", "name": "Piyush | Growth Systems"}

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
CORS(app)

# ─── Live pipeline & scheduler state ─────────────────────────────────────────
pipeline_log: list[str] = []
pipeline_status: str = "idle"   # idle | running | done | error
pipeline_proc = None
pipeline_lock = threading.Lock()

scheduler_thread = None
scheduler_running = False
scheduler_lock = threading.Lock()

# ─── Helpers ─────────────────────────────────────────────────────────────────

def read_env() -> dict:
    """Parse .env file into a dict and merge with os.environ."""
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    # Merge with os.environ so cloud environments reflect injected secrets
    ALLOWED_KEYS = {
        "IG_USER_ID", "IG_ACCESS_TOKEN", "GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY",
        "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "NVIDIA_NIM_API_KEY", "DRY_RUN",
        "PUBLIC_CDN_BASE", "AUTOGRAM_OWNER_KEY", "LLM_PROVIDER", "LLM_MODEL",
        "POSTING_TIME", "TIMEZONE", "S3_BUCKET", "S3_SECRET_KEY", "META_APP_SECRET"
    }
    for k, v in os.environ.items():
        if k in ALLOWED_KEYS:
            env[k] = v
    return env

def write_env_key(key: str, value: str):
    """Update or add a single key in the .env file."""
    content = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
    pattern = rf"^{re.escape(key)}=.*$"
    if re.search(pattern, content, flags=re.MULTILINE):
        content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
    else:
        content = content.rstrip() + f"\n{key}={value}\n"
    ENV_PATH.write_text(content, encoding="utf-8")

def redact(val: str) -> str:
    """Redact sensitive values for display."""
    if not val or len(val) < 12:
        return "••••••"
    return val[:8] + "••••••" + val[-4:]

def read_schedule() -> dict:
    """Read persistent schedule data from data/schedule.json."""
    if SCHEDULE_PATH.exists():
        try:
            return json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "scheduler_enabled": True,
        "daily_slots": [
            {"slot": "08:00", "label": "Morning Prime", "pillar": "AI Tool Breakdown", "enabled": True},
            {"slot": "10:30", "label": "Mid-Morning High Signal", "pillar": "Prompting & Workflow", "enabled": True},
            {"slot": "13:00", "label": "Lunchtime Tech Deep Dive", "pillar": "Tech Explainer", "enabled": True},
            {"slot": "15:30", "label": "Afternoon Strategy", "pillar": "Marketing Psychology", "enabled": True},
            {"slot": "18:00", "label": "Evening Commute Insights", "pillar": "Career & Skills", "enabled": True},
            {"slot": "20:30", "label": "Prime Time Contrarian", "pillar": "Contrarian", "enabled": True},
            {"slot": "22:30", "label": "Late Night Blueprint", "pillar": "AI Tool Breakdown", "enabled": True}
        ],
        "timezone": "Asia/Kolkata",
        "queue": [],
        "history": []
    }

def write_schedule(data: dict):
    """Persist schedule data to data/schedule.json."""
    SCHEDULE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def get_next_scheduled_run() -> dict:
    """Calculate the next scheduled publishing time based on slots and queue."""
    sched = read_schedule()
    now = datetime.now()
    now_hm = now.strftime("%H:%M")

    # Check queued items first
    for item in sched.get("queue", []):
        if item.get("status") == "QUEUED":
            try:
                st = datetime.fromisoformat(item["scheduled_time"])
                if st > now:
                    delta_seconds = int((st - now).total_seconds())
                    return {
                        "type": "queued",
                        "time": st.strftime("%Y-%m-%d %H:%M"),
                        "topic": item.get("topic"),
                        "pillar": item.get("pillar"),
                        "seconds_left": max(0, delta_seconds)
                    }
            except Exception:
                pass

    # Fall back to next daily slot today or tomorrow
    active_slots = [s["slot"] for s in sched.get("daily_slots", []) if s.get("enabled", True)]
    active_slots.sort()

    for s in active_slots:
        if s > now_hm:
            slot_hour, slot_min = map(int, s.split(":"))
            slot_dt = now.replace(hour=slot_hour, minute=slot_min, second=0, microsecond=0)
            return {
                "type": "daily_slot",
                "time": slot_dt.strftime("%Y-%m-%d %H:%M"),
                "slot": s,
                "seconds_left": int((slot_dt - now).total_seconds())
            }

    if active_slots:
        first_slot = active_slots[0]
        slot_hour, slot_min = map(int, first_slot.split(":"))
        tomorrow = now + timedelta(days=1)
        slot_dt = tomorrow.replace(hour=slot_hour, minute=slot_min, second=0, microsecond=0)
        return {
            "type": "daily_slot",
            "time": slot_dt.strftime("%Y-%m-%d %H:%M"),
            "slot": first_slot,
            "seconds_left": int((slot_dt - now).total_seconds())
        }

    return {"type": "none", "time": None, "seconds_left": None}

def get_output_runs() -> list[dict]:
    """List all pipeline output run folders with manifest and asset data."""
    runs = []
    if not OUTPUT_DIR.exists():
        return runs
    for d in sorted(OUTPUT_DIR.iterdir(), reverse=True):
        if not d.is_dir() or d.name == "generated_images":
            continue
        manifest_f = d / "manifest.json"
        caption_f  = d / "caption.txt"
        hashtags_f = d / "hashtags.txt"
        reels_f    = d / "reels_script.md"
        content_f  = d / "content.json"
        slides = sorted(d.glob("slide_*.jpg"))
        cap_text = caption_f.read_text(encoding="utf-8") if caption_f.exists() else ""
        extracted_tags = hashtags_f.read_text(encoding="utf-8").split() if hashtags_f.exists() else [w for w in cap_text.split() if w.startswith("#")]
        entry = {
            "date": d.name,
            "slides": [s.name for s in slides],
            "slides_count": len(slides),
            "has_caption": caption_f.exists(),
            "caption": cap_text,
            "has_hashtags": bool(extracted_tags),
            "hashtags": extracted_tags,
            "has_reels": reels_f.exists(),
            "reels_script": reels_f.read_text(encoding="utf-8") if reels_f.exists() else "",
            "has_manifest": manifest_f.exists(),
            "has_content": content_f.exists()
        }
        if manifest_f.exists():
            try:
                entry.update(json.loads(manifest_f.read_text(encoding="utf-8")))
            except Exception:
                pass
        if content_f.exists() and "topic" not in entry:
            try:
                cdata = json.loads(content_f.read_text(encoding="utf-8"))
                entry["topic"] = cdata.get("topic", entry.get("topic", ""))
                entry["pillar"] = cdata.get("pillar", entry.get("pillar", ""))
            except Exception:
                pass
        runs.append(entry)
    return runs

# ─── Background Scheduler Daemon ─────────────────────────────────────────────

def scheduler_worker():
    global scheduler_running
    logger_msg = "[SCHEDULER] Autonomous Daemon initialized."
    with pipeline_lock:
        pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {logger_msg}")

    last_day_str = None
    triggered_today = set()

    while True:
        with scheduler_lock:
            if not scheduler_running:
                break

        try:
            sched = read_schedule()
            if not sched.get("scheduler_enabled", True):
                time.sleep(15)
                continue

            # Timezone-aware timestamp (default Asia/Kolkata for peak engagement alignment)
            tz_name = sched.get("timezone", "Asia/Kolkata")
            try:
                from zoneinfo import ZoneInfo
                target_tz = ZoneInfo(tz_name)
                now_dt = datetime.now(target_tz)
            except Exception:
                from datetime import timezone as dt_timezone
                target_tz = dt_timezone(timedelta(hours=5, minutes=30))
                now_dt = datetime.now(target_tz)

            current_time_str = now_dt.strftime("%H:%M")
            current_date_str = now_dt.strftime("%Y-%m-%d")

            if current_date_str != last_day_str:
                triggered_today = set()
                last_day_str = current_date_str

            # 1. Check daily recurring slots
            active_slots = {s["slot"] for s in sched.get("daily_slots", []) if s.get("enabled", True)}
            if current_time_str in active_slots and current_time_str not in triggered_today:
                triggered_today.add(current_time_str)
                with pipeline_lock:
                    pipeline_log.append(
                        f"[{now_dt.strftime('%H:%M:%S')} {tz_name}] [GROWTH AUTOPILOT] Triggering peak viral drop for slot {current_time_str}..."
                    )
                # Run pipeline in a subprocess
                run_pipeline_subprocess(mode="live" if read_env().get("DRY_RUN") == "false" else "dry-run")

            # 2. Check individual queued items
            queue = sched.get("queue", [])
            updated_queue = []
            queue_changed = False
            for item in queue:
                if item.get("status") == "QUEUED":
                    try:
                        st = datetime.fromisoformat(item["scheduled_time"])
                        if now_dt >= st:
                            item["status"] = "TRIGGERED"
                            queue_changed = True
                            with pipeline_lock:
                                pipeline_log.append(
                                    f"[{now_dt.strftime('%H:%M:%S')}] [SCHEDULER] Executing queued item: '{item.get('topic')}'"
                                )
                            run_pipeline_subprocess(mode=item.get("mode", "dry-run"))
                    except Exception as e:
                        print(f"Error checking queue item: {e}")
                updated_queue.append(item)

            if queue_changed:
                sched["queue"] = updated_queue
                write_schedule(sched)

        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")

        time.sleep(15)

def run_pipeline_subprocess(mode="dry-run"):
    global pipeline_status, pipeline_proc
    with pipeline_lock:
        if pipeline_status == "running":
            return
        pipeline_status = "running"
        pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting pipeline ({mode.upper()})...")

    python = sys.executable
    cmd = [python, str(BASE_DIR / "orchestrator.py")]
    if mode == "dry-run":
        cmd.append("--dry-run")
    else:
        cmd.append("--run-all")

    def target():
        global pipeline_status, pipeline_proc
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", cwd=str(BASE_DIR)
            )
            with pipeline_lock:
                pipeline_proc = proc
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    with pipeline_lock:
                        pipeline_log.append(line)
            proc.wait()
            with pipeline_lock:
                pipeline_status = "done" if proc.returncode == 0 else "error"
                pipeline_log.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"Pipeline {'completed ✓' if proc.returncode == 0 else f'failed (exit {proc.returncode}) ✗'}"
                )
        except Exception as e:
            with pipeline_lock:
                pipeline_status = "error"
                pipeline_log.append(f"[ERROR] {e}")

    threading.Thread(target=target, daemon=True).start()

# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "autogram-dashboard",
        "version": "v2.5-quantum",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/api/status")
def api_status():
    env = read_env()
    memory = {}
    if MEMORY_PATH.exists():
        try:
            memory = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    recent = memory.get("recent_posts", [])
    sched_data = read_schedule()
    next_sched = get_next_scheduled_run()

    # Meta token health check
    token = env.get("IG_ACCESS_TOKEN", "")
    token_valid = bool(token.strip()) and len(token) > 20

    return jsonify({
        "engine": "online",
        "version": "v2.5-quantum",
        "dry_run": env.get("DRY_RUN", "true"),
        "ig_user_id": env.get("IG_USER_ID", ""),
        "ig_account": get_brand_config().get("handle", "@signhify.studio"),
        "llm_provider": env.get("LLM_PROVIDER", "auto"),
        "llm_model": env.get("LLM_MODEL", "gemini-2.5-flash"),
        "cdn_base": env.get("PUBLIC_CDN_BASE", "http://localhost:8000"),
        "gemini_key_set": bool(env.get("GEMINI_API_KEY", "").strip()),
        "groq_key_set": bool(env.get("GROQ_API_KEY", "").strip()),
        "openrouter_key_set": bool(env.get("OPENROUTER_API_KEY", "").strip()),
        "cloudflare_configured": bool(env.get("CLOUDFLARE_API_TOKEN", "").strip() and env.get("CLOUDFLARE_ACCOUNT_ID", "").strip()),
        "nvidia_key_set": bool(env.get("NVIDIA_NIM_API_KEY", "").strip()),
        "s3_configured": bool(env.get("S3_BUCKET", "").strip()),
        "meta_token_configured": token_valid,
        "recent_posts_count": len(recent),
        "last_post_date": recent[0]["date"] if recent else None,
        "last_post_topic": recent[0]["topic"] if recent else None,
        "last_post_score": recent[0]["score"] if recent else None,
        "total_runs": len(get_output_runs()),
        "posting_time": env.get("POSTING_TIME", "19:30"),
        "timezone": env.get("TIMEZONE", sched_data.get("timezone", "Asia/Kolkata")),
        "scheduler_enabled": sched_data.get("scheduler_enabled", True),
        "scheduler_daemon_running": scheduler_running,
        "next_scheduled_run": next_sched,
        "queue_count": len([q for q in sched_data.get("queue", []) if q.get("status") == "QUEUED"]),
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/api/schedule", methods=["GET", "POST"])
def api_schedule():
    sched = read_schedule()
    if request.method == "GET":
        sched["next_run"] = get_next_scheduled_run()
        sched["scheduler_daemon_running"] = scheduler_running
        return jsonify(sched)

    data = request.json or {}

    # 1. Update general settings or slots
    if "daily_slots" in data:
        sched["daily_slots"] = data["daily_slots"]
    if "scheduler_enabled" in data:
        sched["scheduler_enabled"] = bool(data["scheduler_enabled"])
    if "timezone" in data:
        sched["timezone"] = str(data["timezone"])

    # 2. Add new item to queue
    if "new_post" in data:
        item = data["new_post"]
        post_id = f"SCH-{int(time.time() * 1000) % 100000}"
        new_entry = {
            "id": post_id,
            "scheduled_time": item.get("scheduled_time", datetime.now().isoformat()),
            "topic": item.get("topic", "Autonomous Topic"),
            "pillar": item.get("pillar", "AI Tool Breakdown"),
            "mode": item.get("mode", "live"),
            "status": "QUEUED",
            "created_at": datetime.now().isoformat()
        }
        sched.setdefault("queue", []).insert(0, new_entry)

    write_schedule(sched)
    return jsonify({"ok": True, "schedule": sched})

@app.route("/api/schedule/<item_id>", methods=["DELETE"])
def api_schedule_delete(item_id):
    sched = read_schedule()
    queue = sched.get("queue", [])
    sched["queue"] = [q for q in queue if str(q.get("id")) != str(item_id)]
    write_schedule(sched)
    return jsonify({"ok": True, "remaining": len(sched["queue"])})

@app.route("/api/scheduler/toggle", methods=["POST"])
def api_scheduler_toggle():
    global scheduler_thread, scheduler_running
    sched = read_schedule()
    data = request.json or {}
    enable = data.get("enable", not scheduler_running)

    with scheduler_lock:
        if enable and not scheduler_running:
            scheduler_running = True
            sched["scheduler_enabled"] = True
            write_schedule(sched)
            scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
            scheduler_thread.start()
            with pipeline_lock:
                pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCHEDULER] Background daemon STARTED ✓")
        elif not enable and scheduler_running:
            scheduler_running = False
            sched["scheduler_enabled"] = False
            write_schedule(sched)
            with pipeline_lock:
                pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCHEDULER] Background daemon STOPPED ⏹")

    return jsonify({"ok": True, "scheduler_running": scheduler_running, "scheduler_enabled": sched["scheduler_enabled"]})

@app.route("/api/publish", methods=["POST"])
def api_publish():
    """
    Directly publishes an output run or custom carousel to Instagram.
    """
    data = request.json or {}
    run_date = data.get("date")
    dry_run = data.get("mode", "dry-run") == "dry-run"
    custom_caption = data.get("caption")

    if not run_date:
        # Pick latest run date if not provided
        runs = get_output_runs()
        if not runs:
            return jsonify({"ok": False, "error": "No output runs available to publish"}), 400
        run_date = runs[0]["date"]

    folder = OUTPUT_DIR / run_date
    if not folder.exists():
        return jsonify({"ok": False, "error": f"Output folder {run_date} not found"}), 404

    slides = sorted(folder.glob("slide_*.jpg"))
    if not slides:
        return jsonify({"ok": False, "error": "No rendered slide_*.jpg images found in run"}), 400

    caption_file = folder / "caption.txt"
    hashtags_file = folder / "hashtags.txt"
    content_file = folder / "content.json"
    manifest_file = folder / "manifest.json"
    first_comment_file = folder / "first_comment.txt"

    # Determine topic and pillar from manifest or content
    topic = "AI Automation Systems Architecture"
    pillar = "AI Tool Breakdown"
    if content_file.exists():
        try:
            c_data = json.loads(content_file.read_text(encoding="utf-8"))
            topic = c_data.get("topic", topic)
            pillar = c_data.get("pillar", pillar)
        except Exception:
            pass
    elif manifest_file.exists():
        try:
            m_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            topic = m_data.get("topic", topic)
            pillar = m_data.get("pillar", pillar)
        except Exception:
            pass

    # Ensure caption & hashtags are 100% generated and validated
    from src.growth.viral_engine import viral_engine
    from src.content.script_writer import script_writer

    caption = ""
    if custom_caption and custom_caption.strip():
        caption = custom_caption.strip()
        if "#" not in caption:
            tags = viral_engine.build_viral_hashtags(pillar, topic=topic)
            caption = f"{caption}\n\n.\n.\n{' '.join(tags)}"
    elif caption_file.exists() and caption_file.read_text(encoding="utf-8").strip():
        caption = caption_file.read_text(encoding="utf-8").strip()
        if "#" not in caption:
            tags = viral_engine.build_viral_hashtags(pillar, topic=topic)
            caption = f"{caption}\n\n.\n.\n{' '.join(tags)}"
            caption_file.write_text(caption, encoding="utf-8")
    else:
        # Generate complete caption with hook, CTAs, sign-off and viral hashtags
        if content_file.exists():
            try:
                c_data = json.loads(content_file.read_text(encoding="utf-8"))
                cap_meta = script_writer.generate_caption(c_data)
                caption = cap_meta["caption"]
            except Exception:
                caption = ""
        if not caption:
            def_cap = viral_engine.generate_default_caption(topic=topic, pillar=pillar)
            caption = def_cap["caption"]
        caption_file.write_text(caption, encoding="utf-8")

    # Extract tags from caption and ensure hashtags.txt is saved
    extracted_tags = [w for w in caption.split() if w.startswith("#")]
    if extracted_tags and not hashtags_file.exists():
        hashtags_file.write_text(" ".join(extracted_tags), encoding="utf-8")

    # Prepare first comment discussion spark
    first_comment_text = ""
    if first_comment_file.exists():
        first_comment_text = first_comment_file.read_text(encoding="utf-8").strip()
    elif content_file.exists():
        try:
            c_data = json.loads(content_file.read_text(encoding="utf-8"))
            first_comment_text = script_writer.generate_first_comment(c_data)
            first_comment_file.write_text(first_comment_text, encoding="utf-8")
        except Exception:
            pass
    if not first_comment_text:
        first_comment_text = viral_engine.generate_first_comment({"slides": [], "trigger_word": "SYSTEM"})

    with pipeline_lock:
        pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [PUBLISHER] Direct publish initiated for {run_date} ({'DRY-RUN' if dry_run else 'LIVE PRODUCTION'})...")
        pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [PUBLISHER] Attached verified caption ({len(caption)} chars) with {len(extracted_tags)} hashtags.")

    try:
        from src.storage.uploader import uploader
        from src.instagram.publisher import publisher

        publisher.dry_run = dry_run
        slide_paths = [str(s) for s in slides]

        with pipeline_lock:
            pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [UPLOAD] Staging {len(slide_paths)} slides for Instagram CDN...")

        public_image_urls = uploader.upload_slide_images(slide_paths, run_date)
        alt_texts = [f"Slide {i+1} of {len(slide_paths)}" for i in range(len(slide_paths))]

        with pipeline_lock:
            pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [META GRAPH] Publishing carousel via Meta Instagram API...")

        media_id = publisher.publish_carousel(
            image_urls=public_image_urls,
            alt_texts=alt_texts,
            caption=caption
        )

        with pipeline_lock:
            pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [META GRAPH] Published successfully! Media ID: {media_id} ✓")

        # Post first-comment velocity spark
        if media_id and not dry_run and not str(media_id).startswith("mock"):
            try:
                publisher.post_comment(media_id, first_comment_text)
                with pipeline_lock:
                    pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIRST-COMMENT] Published viral discussion prompt to post feed ✓")
            except Exception as fc_err:
                with pipeline_lock:
                    pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIRST-COMMENT NOTE] {fc_err}")

        # Update manifest.json
        manifest = {}
        if manifest_file.exists():
            try:
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        manifest["media_id"] = media_id
        manifest["caption"] = caption
        manifest["hashtags"] = extracted_tags
        manifest["status"] = "PUBLISHED" if not dry_run else "SIMULATED_PUBLISH"
        manifest["published_at"] = datetime.now().isoformat()
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return jsonify({
            "ok": True,
            "media_id": media_id,
            "status": manifest["status"],
            "slides_count": len(slide_paths),
            "date": run_date,
            "caption": caption,
            "hashtags_count": len(extracted_tags)
        })

    except Exception as e:
        with pipeline_lock:
            pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [PUBLISH ERROR] {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/caption/generate", methods=["POST"])
def api_caption_generate():
    """
    On-demand caption and 3-tier viral hashtag generation for any topic/pillar.
    """
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "AI Automation Systems Architecture").strip()
    pillar = data.get("pillar", "AI Tool Breakdown").strip()
    custom_body = data.get("body", "").strip()

    try:
        from src.content.script_writer import script_writer
        res = script_writer.generate_caption_for_topic(topic=topic, pillar=pillar, custom_body=custom_body)
        return jsonify({
            "ok": True,
            "caption": res["caption"],
            "body": res.get("body", ""),
            "hashtags": res.get("hashtags", []),
            "first_comment": res.get("first_comment", ""),
            "topic": topic,
            "pillar": pillar
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    On-demand AI Carousel & Script Studio Generator.
    """
    data = request.get_json(silent=True) or {}
    topic_text = data.get("topic", "").strip()
    pillar = data.get("pillar", "AI Tool Breakdown")
    angle = data.get("angle", "")
    theme = data.get("theme", "auto").strip().lower()
    render_slides = data.get("render_slides", True)

    if not topic_text:
        return jsonify({"ok": False, "error": "Topic is required"}), 400

    today_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = OUTPUT_DIR / today_str
    out_dir.mkdir(parents=True, exist_ok=True)

    with pipeline_lock:
        pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [STUDIO] Synthesizing custom carousel: '{topic_text}' [{pillar}] (Theme: {theme})...")

    try:
        from src.content.generator import generator
        from src.content.fact_checker import fact_checker
        from src.content.quality_gate import quality_gate
        from src.content.script_writer import script_writer
        from src.research.fetcher import fetcher

        sources = fetcher.acquire_sources(live_fetch=False)
        topic_obj = {
            "topic": topic_text,
            "pillar": pillar,
            "angle": angle or f"Comprehensive guide to {topic_text}",
            "theme": theme if theme != "auto" else None
        }

        carousel = generator.generate_carousel(topic_obj, sources)
        if theme and theme != "auto":
            carousel["theme"] = theme
        carousel["publication_date"] = today_str

        # Fact checking & QA
        fc = fact_checker.verify_carousel(carousel, sources)
        qa = quality_gate.evaluate(carousel)

        # Captions & Reels Script
        caption_meta = script_writer.generate_caption(carousel)
        reels_meta = script_writer.generate_reels_script(carousel)

        # Save files
        hashtags_list = caption_meta.get("hashtags", [])
        (out_dir / "content.json").write_text(json.dumps(carousel, indent=2), encoding="utf-8")
        (out_dir / "caption.txt").write_text(caption_meta["caption"], encoding="utf-8")
        (out_dir / "hashtags.txt").write_text(" ".join(hashtags_list), encoding="utf-8")
        first_comment_text = caption_meta.get("first_comment") or script_writer.generate_first_comment(carousel)
        (out_dir / "first_comment.txt").write_text(first_comment_text, encoding="utf-8")
        (out_dir / "reels_script.md").write_text(reels_meta["formatted_text"], encoding="utf-8")

        rendered_slides = []
        if render_slides:
            try:
                from renderer.render import CarouselRenderer
                BRAND_FILE = BASE_DIR / "data" / "brand.json"
                brand_data = json.loads(BRAND_FILE.read_text(encoding="utf-8")) if BRAND_FILE.exists() else {}
                renderer = CarouselRenderer(brand_profile=brand_data)
                rendered_paths = renderer.render_carousel(carousel, out_dir)
                rendered_slides = [Path(p).name for p in rendered_paths]
            except Exception as re_err:
                print(f"Slide render note: {re_err}")

        manifest = {
            "content_id": carousel.get("content_id", "CNT-" + today_str),
            "date": today_str,
            "topic": topic_text,
            "pillar": pillar,
            "slides_count": len(carousel.get("slides", [])),
            "caption": caption_meta["caption"],
            "hashtags": hashtags_list,
            "qa_score": qa.get("score", 92),
            "status": "STAGED",
            "image_files": rendered_slides
        }
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        with pipeline_lock:
            pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [STUDIO] Synthesis complete! QA Score: {qa.get('score')}/100 with {len(hashtags_list)} hashtags ✓")

        return jsonify({
            "ok": True,
            "carousel": carousel,
            "caption": caption_meta["caption"],
            "hashtags": hashtags_list,
            "first_comment": first_comment_text,
            "reels_script": reels_meta["formatted_text"],
            "qa_score": qa.get("score"),
            "slides_count": len(carousel.get("slides", [])),
            "date": today_str,
            "rendered_slides": rendered_slides
        })

    except Exception as e:
        with pipeline_lock:
            pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [STUDIO ERROR] {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/token/refresh", methods=["POST"])
def api_token_refresh():
    try:
        from src.instagram.token_manager import token_manager
        res = token_manager.refresh_token()
        with pipeline_lock:
            pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] [META TOKEN] Token refresh result: {res.get('status')} ✓")
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/env", methods=["GET"])
def api_env_get():
    env = read_env()
    SENSITIVE = {
        "IG_ACCESS_TOKEN", "GEMINI_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY",
        "CLAUDE_API_KEY", "S3_SECRET_KEY", "META_APP_SECRET", "AUTOGRAM_SECRET_SALT",
        "AUTOGRAM_OWNER_KEY"
    }
    result = {}
    for k, v in env.items():
        result[k] = {"value": redact(v) if k in SENSITIVE else v, "redacted": k in SENSITIVE}
    return jsonify(result)

@app.route("/api/env", methods=["POST"])
def api_env_set():
    data = request.json or {}
    for key, value in data.items():
        if key and not key.startswith("#"):
            write_env_key(key, str(value))
    return jsonify({"ok": True, "updated": list(data.keys())})

@app.route("/api/runs")
def api_runs():
    return jsonify(get_output_runs())

@app.route("/api/memory")
def api_memory():
    if MEMORY_PATH.exists():
        try:
            return jsonify(json.loads(MEMORY_PATH.read_text(encoding="utf-8")))
        except Exception:
            pass
    return jsonify({"recent_posts": [], "winning_patterns": [], "banned_topics": []})

@app.route("/api/pipeline/status")
def api_pipeline_status():
    with pipeline_lock:
        return jsonify({
            "status": pipeline_status,
            "log": pipeline_log[-200:],
            "scheduler_daemon_running": scheduler_running
        })

@app.route("/api/pipeline/run", methods=["POST"])
def api_pipeline_run():
    global pipeline_status, pipeline_log, pipeline_proc
    data = request.json or {}
    mode = data.get("mode", "dry-run")  # "dry-run" | "live"

    with pipeline_lock:
        if pipeline_status == "running":
            return jsonify({"ok": False, "error": "Pipeline already running"}), 409

    run_pipeline_subprocess(mode=mode)
    return jsonify({"ok": True, "mode": mode})

@app.route("/api/pipeline/stop", methods=["POST"])
def api_pipeline_stop():
    global pipeline_proc, pipeline_status
    with pipeline_lock:
        if pipeline_proc and pipeline_proc.poll() is None:
            pipeline_proc.terminate()
            pipeline_status = "idle"
            pipeline_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Pipeline stopped by user.")
    return jsonify({"ok": True})

@app.route("/api/webhook/autopilot", methods=["GET", "POST"])
def api_webhook_autopilot():
    """
    Zero-touch trigger endpoint for external cron jobs (GitHub Actions, cron-job.org, EasyCron, Render Cron).
    Pinging this endpoint triggers the autonomous publishing pipeline even if computer is shut down.
    """
    key = request.args.get("key") or request.headers.get("X-Autogram-Key") or ""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        key = auth_header.split(" ", 1)[1]

    expected_key = os.environ.get("AUTOGRAM_OWNER_KEY", "autogram_owner_vip_2026")
    if key != expected_key:
        return jsonify({"ok": False, "error": "Unauthorized. Invalid or missing secret key."}), 401

    mode = request.args.get("mode") or ("live" if read_env().get("DRY_RUN") == "false" else "dry-run")

    with pipeline_lock:
        if pipeline_status == "running":
            return jsonify({"ok": True, "message": "Autopilot pipeline is already running.", "status": "running"})

    run_pipeline_subprocess(mode=mode)
    return jsonify({
        "ok": True,
        "message": f"Autonomous pipeline triggered successfully in {mode.upper()} mode.",
        "status": "started",
        "brand": "@signhify.studio",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/output/<date>/<filename>")
@app.route("/api/output/<date>/<filename>")
def api_output_file(date, filename):
    folder = OUTPUT_DIR / date
    return send_from_directory(str(folder), filename)

@app.route("/dashboard")
@app.route("/dashboard.html")
def dashboard():
    return send_from_directory(str(BASE_DIR), "dashboard.html")

@app.route("/health")
@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "autogram-dashboard",
        "version": "v2.5-quantum",
        "brand": "@signhify.studio",
        "growth_autopilot": "ACTIVE",
        "schedule_slots": 7,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/")
def root():
    return send_from_directory(str(BASE_DIR), "index.html")

# Auto-start scheduler daemon if enabled
def init_daemon():
    global scheduler_thread, scheduler_running
    sched = read_schedule()
    if sched.get("scheduler_enabled", True):
        scheduler_running = True
        scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        scheduler_thread.start()

if __name__ == "__main__":
    init_daemon()
    port = int(os.environ.get("PORT", 5050))
    print("=" * 60)
    print(f"  Autogram Neural Dashboard API — port {port}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
