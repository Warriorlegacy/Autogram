"""
Autogram Dashboard API Server (dashboard_api.py)
Lightweight Flask API that powers the owner dashboard UI.
Endpoints: status, run pipeline, view logs, manage .env, view output.
"""

import json
import os
import re
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "output"
MEMORY_PATH = BASE_DIR / "data" / "content-memory.json"
DB_PATH = BASE_DIR / "autopilot.db"

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
CORS(app)

# ─── Live pipeline log buffer ────────────────────────────────────────────────
pipeline_log: list[str] = []
pipeline_status: str = "idle"   # idle | running | done | error
pipeline_proc = None
pipeline_lock = threading.Lock()

# ─── Helpers ─────────────────────────────────────────────────────────────────

def read_env() -> dict:
    """Parse .env file into a dict."""
    env = {}
    if not ENV_PATH.exists():
        return env
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip()
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

def get_output_runs() -> list[dict]:
    """List all pipeline output run folders with manifest data."""
    runs = []
    if not OUTPUT_DIR.exists():
        return runs
    for d in sorted(OUTPUT_DIR.iterdir(), reverse=True):
        if not d.is_dir() or d.name == "generated_images":
            continue
        manifest_f = d / "manifest.json"
        caption_f  = d / "caption.txt"
        slides = sorted(d.glob("slide_*.jpg"))
        entry = {
            "date": d.name,
            "slides": [s.name for s in slides],
            "slides_count": len(slides),
            "has_caption": caption_f.exists(),
            "caption": caption_f.read_text(encoding="utf-8")[:300] if caption_f.exists() else "",
        }
        if manifest_f.exists():
            try:
                entry.update(json.loads(manifest_f.read_text(encoding="utf-8")))
            except Exception:
                pass
        runs.append(entry)
    return runs

# ─── API Routes ───────────────────────────────────────────────────────────────

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
    return jsonify({
        "engine": "online",
        "version": "v2.4",
        "dry_run": env.get("DRY_RUN", "true"),
        "ig_user_id": env.get("IG_USER_ID", ""),
        "ig_account": "@signhify.studio",
        "llm_provider": env.get("LLM_PROVIDER", "auto"),
        "llm_model": env.get("LLM_MODEL", "gemini-2.0-flash"),
        "cdn_base": env.get("PUBLIC_CDN_BASE", "http://localhost:8000"),
        "gemini_key_set": bool(env.get("GEMINI_API_KEY", "").strip()),
        "groq_key_set": bool(env.get("GROQ_API_KEY", "").strip()),
        "s3_configured": bool(env.get("S3_BUCKET", "").strip()),
        "recent_posts_count": len(recent),
        "last_post_date": recent[0]["date"] if recent else None,
        "last_post_topic": recent[0]["topic"] if recent else None,
        "last_post_score": recent[0]["score"] if recent else None,
        "total_runs": len(get_output_runs()),
        "posting_time": env.get("POSTING_TIME", "19:30"),
        "timezone": env.get("TIMEZONE", "Asia/Kolkata"),
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/api/env", methods=["GET"])
def api_env_get():
    env = read_env()
    SENSITIVE = {"IG_ACCESS_TOKEN", "GEMINI_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY",
                 "CLAUDE_API_KEY", "S3_SECRET_KEY", "META_APP_SECRET", "AUTOGRAM_SECRET_SALT",
                 "AUTOGRAM_OWNER_KEY"}
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
        return jsonify({"status": pipeline_status, "log": pipeline_log[-200:]})

@app.route("/api/pipeline/run", methods=["POST"])
def api_pipeline_run():
    global pipeline_status, pipeline_log, pipeline_proc
    data = request.json or {}
    mode = data.get("mode", "dry-run")  # "dry-run" | "live"

    with pipeline_lock:
        if pipeline_status == "running":
            return jsonify({"ok": False, "error": "Pipeline already running"}), 409
        pipeline_status = "running"
        pipeline_log = [f"[{datetime.now().strftime('%H:%M:%S')}] Starting pipeline ({mode.upper()})..."]

    def run_in_thread():
        global pipeline_status, pipeline_proc
        python = str(BASE_DIR / ".venv" / "Scripts" / "python.exe")
        cmd = [python, str(BASE_DIR / "orchestrator.py")]
        if mode == "dry-run":
            cmd.append("--dry-run")
        else:
            cmd.append("--run-all")

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

    threading.Thread(target=run_in_thread, daemon=True).start()
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

@app.route("/output/<date>/<filename>")
@app.route("/api/output/<date>/<filename>")
def api_output_file(date, filename):
    folder = OUTPUT_DIR / date
    return send_from_directory(str(folder), filename)

@app.route("/dashboard")
@app.route("/dashboard.html")
def dashboard():
    return send_from_directory(str(BASE_DIR), "dashboard.html")

@app.route("/")
def root():
    return send_from_directory(str(BASE_DIR), "index.html")

if __name__ == "__main__":
    print("=" * 60)
    print("  Autogram Dashboard API — http://localhost:5050/dashboard")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5050, debug=False)
