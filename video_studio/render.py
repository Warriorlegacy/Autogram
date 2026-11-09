"""Render a generated HyperFrames project to a verified 9:16 MP4.

Wraps the real HyperFrames CLI (Apache-2.0) + FFmpeg. Every subprocess call
is logged and every nonzero exit raises — no silent failures.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

from .brief import REPO_ROOT

OUTPUT_DIR = Path(__file__).parent / "output"


class RenderError(RuntimeError):
    pass


# Resolve npx via PATH-independent lookup so the venv Python can spawn it on Windows.
_NPX = shutil.which("npx") or shutil.which("npx.cmd") or shutil.which("npx.ps1")
if _NPX is None:
    raise RenderError("npx not found on PATH")


def installed_hyperframes_version() -> str:
    """Exact version of the hyperframes package installed in this repo.

    Fails closed. `npx --yes hyperframes` (bare) resolves whatever npm has
    cached or finds on PATH, which silently rendered production reels on a
    DIFFERENT version than the one installed here -- measured in
    docs/video-studio/REMOTION_HYPERFRAMES_BENCHMARK.md (installed 0.8.58 vs
    a global 0.7.52 on PATH). Pinning keeps renders reproducible.
    """
    pkg = REPO_ROOT / "node_modules" / "hyperframes" / "package.json"
    if not pkg.exists():
        raise RenderError(
            "hyperframes is not installed in this repo; run `npm install` "
            "before rendering (do not fall back to a global CLI)"
        )
    return json.loads(pkg.read_text(encoding="utf-8"))["version"]


HF = [_NPX, "--yes", f"hyperframes@{installed_hyperframes_version()}"]


def _run(cmd: list[str], cwd: Path, log: list[str], timeout: int = 1800) -> str:
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    tail = (proc.stdout or "")[-6000:]
    log.append(f"$ {' '.join(cmd)}\n[exit={proc.returncode} {time.time()-t0:.1f}s]\n{tail}")
    if proc.returncode != 0:
        raise RenderError(f"{' '.join(cmd)} exited {proc.returncode}\n{(proc.stderr or '')[-2500:]}")
    return proc.stdout or ""


def check_project(proj: Path, log: list[str]) -> dict:
    """Run HyperFrames' built-in gate: Runtime + Layout + Motion + Contrast.

    A failing check is a QA verdict, NOT a crash. This returns clean=False with
    the findings so the caller can decide. It previously let `_run` raise on
    the nonzero exit, which meant `clean` was unreachable, `--skip-gate` was
    dead code, and every qa_report recorded gate=True regardless of reality.
    """

    cmd = HF + ["check"]
    log.append(f"$ {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, cwd=str(proj), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=600)
    except subprocess.TimeoutExpired as exc:
        raise RenderError(f"hyperframes check timed out in {proj}") from exc

    out = proc.stdout or ""
    log.append(f"[exit={proc.returncode}]\n{out[-6000:]}")
    clean = proc.returncode == 0 and "Check passed" in out

    # Surface the actionable lines; stderr carries npm noise, stdout carries findings.
    findings = [
        ln.strip() for ln in out.splitlines()
        if ln.strip().startswith(("x ", "✗", "- ", "L ")) or " error" in ln
    ]
    return {
        "gate": "hyperframes check",
        "clean": clean,
        "exit_code": proc.returncode,
        "findings": findings[-20:],
        "output": out[-2500:],
    }


def render_project(proj: Path, out_path: Path, log: list[str], fps: int = 30,
                   quality: str = "draft") -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _run(HF + ["render", "-f", str(fps), "-q", quality, "-o", str(out_path)], proj, log)
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RenderError(f"render produced no file: {out_path}")
    return out_path


def probe(path: Path) -> dict:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_streams", "-show_format", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if p.returncode != 0:
        raise RenderError(f"ffprobe failed on {path}: {p.stderr[-1500:]}")
    return json.loads(p.stdout)


def mux_audio(video: Path, audio: Path, dest: Path, log: list[str],
              lufs: str = "-16") -> Path:
    """Two-pass loudnorm: measure, then apply. Single-pass is only correct for live."""
    if not shutil.which("ffmpeg"):
        raise RenderError("ffmpeg not on PATH")
    dest.parent.mkdir(parents=True, exist_ok=True)
    meas = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio),
         "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    blob = meas.stderr or ""
    i = blob.rfind("{")
    stats = json.loads(blob[i:blob.rfind("}") + 1]) if i >= 0 else {}
    second = (f"loudnorm=I={lufs}:TP=-1.5:LRA=11"
              f":measured_I={stats.get('input_i','-24')}"
              f":measured_TP={stats.get('input_tp','-2')}"
              f":measured_LRA={stats.get('input_lra','7')}"
              f":measured_thresh={stats.get('input_thresh','-32')}"
              f":offset={stats.get('target_offset','0')}:linear=true")
    # apad pads narration with silence to the video's length; -shortest then keeps
    # the VIDEO duration, so the end card is never cut by a shorter narration.
    tmp = dest.with_name(dest.stem + "_mux.mp4")
    _run(["ffmpeg", "-y", "-hide_banner", "-nostats", "-i", str(video), "-i", str(audio),
          "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
          "-af", second + ",apad", "-shortest", "-movflags", "+faststart", str(tmp)],
         REPO_ROOT, log, timeout=900)
    tmp.replace(dest)
    return dest


def demo() -> None:
    f = probe(Path("workspace/final_reel.mp4"))
    assert f["streams"], "no streams in existing render"


if __name__ == "__main__":
    demo()
    print("render.py self-check OK")