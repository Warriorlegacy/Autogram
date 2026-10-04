"""60s reel music + SFX engine: procedural royalty-safe beds, scene SFX, narration ducking.

Everything is synthesized locally (FFmpeg lavfi sources + stdlib wave/struct) — no
samples, no network. The master-spec music brief (HOOK 0-2 / PROBLEM 2-7 / REVEAL 7-15 /
EXPLANATION 15-28 / ESCALATION 28-40 / PAYOFF 40-48 / CTA 48-60) is encoded as an
energy envelope: quiet intro, gradual build, peak near 40-48s, clean tail.

Design notes
------------
- `build_music` writes a layered lavfi bed to AAC (.m4a) 96k stereo 44100. Deterministic
  for a given (style, seed): every synthesis parameter and the anoisesrc noise seed are
  derived from a seeded RNG, and lavfi sources are deterministic under a fixed seed.
- `sfx_library` writes short WAVs (stdlib wave/struct) so downstream can place them
  without one giant ffmpeg graph; 44.1k mono, durations in seconds.
- `mix_full` mixes voice + music + placed SFX with a real sidechain duck (music keyed
  off the voice track), then loudnorm I=-16 / TP=-1.5. Fail-soft: an empty sfx_plan is
  the same voice+music mix as today; every SFX is placed with adelay+apad so a bad file
  can only drop that one hit, never the whole mix.

ponytail: lavfi-only synthesis means no melodic pitch variation beyond the 5 styles
(no key/scale engine); upgrade path is a seeded MIDI->soundfont render if that ceiling
ever matters.
"""
from __future__ import annotations

import logging
import math
import random
import struct
import wave
from pathlib import Path

logger = logging.getLogger(__name__)

SR = 44100
STYLES = ("futuristic_electronic", "cinematic_synth", "dark_tech", "cyber_ambient", "minimal_pulse")

# Master-spec scene timing (seconds). Transitions between these moments get SFX in
# mix_full when a scene_plan is provided.
SCENE_TIMING = (0, 2, 7, 15, 28, 40, 48, 60)

# Seconds of the clip where the energy envelope is at its peak (payoff).
PAYOFF_START, PAYOFF_END = 40.0, 48.0

# Intro fade-in and tail-out length, in seconds.
INTRO_FADE = 1.5
TAIL_FADE = 4.0


def _seed_rng(seed: int | None) -> random.Random:
    """Deterministic RNG; None -> fixed default so output stays reproducible."""
    return random.Random(0 if seed is None else seed)


def _t_expr(duration: float) -> str:
    """Piecewise-linear energy gain for the whole bed, as an ffmpeg volume expression.

    Ramp from INTRO_FADE to PAYOFF_START, hold at 1.0 through PAYOFF_END, then decay to
    zero across TAIL_FADE. `max(0,...)` keeps pre-intro samples silent instead of
    phase-inverted; `min(1,...)` guards overshoot before the peak.
    """
    return (
        f"max(0,min(1,(t-{INTRO_FADE})/{PAYOFF_START}))"
        f"*min(1,1-max(0,(t-{PAYOFF_END})/{TAIL_FADE}))"
    )


def _style_params(style: str, rng: random.Random) -> dict:
    """Per-style synthesis parameters (deterministic per RNG)."""
    p = {
        "tone_freqs": [55.0, 110.0, 165.0, 220.0],
        "tone_vols": [0.045, 0.028, 0.018, 0.012],
        "pulse_freq": 55.0,
        "pulse_vol": 0.10,
        "noise_vol": 0.16,
        "noise_low": 500.0,
        "noise_high": 2600.0,
        "tremolo": 0.35,
        "tremolo_f": 0.35,
        "echo": 0.22,
        "echo_d": 0.42,
    }
    if style == "futuristic_electronic":
        p.update(tone_freqs=[55.0, 110.0, 165.0, 220.0, 330.0],
                 tone_vols=[0.045, 0.028, 0.016, 0.012, 0.008],
                 pulse_vol=0.10, noise_vol=0.15, tremolo=0.38, tremolo_f=0.40)
    elif style == "cinematic_synth":
        p.update(tone_freqs=[55.0, 82.5, 110.0, 165.0, 220.0],
                 tone_vols=[0.055, 0.030, 0.020, 0.012, 0.010],
                 pulse_vol=0.07, noise_vol=0.06, noise_low=300.0, noise_high=1400.0,
                 tremolo=0.18, tremolo_f=0.18, echo=0.34, echo_d=0.5)
    elif style == "dark_tech":
        p.update(tone_freqs=[41.2, 55.0, 82.5, 110.0, 164.8],
                 tone_vols=[0.060, 0.040, 0.026, 0.014, 0.010],
                 pulse_vol=0.13, noise_vol=0.20, noise_low=400.0,
                 noise_high=3200.0, tremolo=0.30, tremolo_f=0.25, echo=0.20, echo_d=0.3)
    elif style == "cyber_ambient":
        p.update(tone_freqs=[55.0, 73.4, 110.0, 146.8, 220.0],
                 tone_vols=[0.045, 0.030, 0.022, 0.016, 0.012],
                 pulse_vol=0.06, noise_vol=0.24, noise_low=350.0, noise_high=4000.0,
                 tremolo=0.30, tremolo_f=0.12, echo=0.40, echo_d=0.6)
    elif style == "minimal_pulse":
        p.update(tone_freqs=[55.0, 110.0],
                 tone_vols=[0.050, 0.030],
                 pulse_vol=0.16, noise_vol=0.05, tremolo=0.45,
                 tremolo_f=0.5, echo=0.12, echo_d=0.25)
    # Per-seed jitter keeps beds from all sounding identical; the RNG keeps one seed
    # bit-identical across runs.
    p["tone_vols"] = [round(v * rng.uniform(0.9, 1.1), 5) for v in p["tone_vols"]]
    for k in ("pulse_vol", "noise_vol", "tremolo", "echo", "echo_d"):
        p[k] = round(p[k] * rng.uniform(0.9, 1.1), 4)
    p["tremolo_f"] = round(p["tremolo_f"] * rng.uniform(0.85, 1.15), 4)
    return p


def build_music(topic: str, style: str = "futuristic_electronic", duration: float = 60.0,
                out_path: str = "", seed: int | None = None) -> str:
    """Procedural royalty-safe music bed with a payoff energy envelope.

    `out_path` defaults to ./music_bed_{style}_{seed or 0}.m4a. Deterministic given seed.
    """
    from src.content import audio60  # local import keeps this module standalone-safe

    if style not in STYLES:
        style = STYLES[0]
    if not out_path:
        out_path = f"music_bed_{style}_{seed or 0}.m4a"
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    rng = _seed_rng(seed)
    p = _style_params(style, rng)
    t_expr = _t_expr(duration)

    inputs: list[str] = []
    n = len(p["tone_freqs"])
    parts: list[str] = []
    for i, f in enumerate(p["tone_freqs"]):
        # Triangle wave via aevalsrc (this FFmpeg build has no triangle source filter).
        inputs += ["-f", "lavfi", "-i",
                   f"aevalsrc=exprs='(2/PI)*asin(sin(2*PI*{f}*t))':s={SR}:d={duration}"]
        parts.append(f"[{i}:a]tremolo=f={p['tremolo_f']}:d={p['tremolo']},"
                     f"volume='{p['tone_vols'][i]}*{t_expr}'[t{i}]")
    # sub pulse + pink-noise bed; the noise gets a fixed seed derived from the RNG
    inputs += ["-f", "lavfi", "-i", f"sine=frequency={p['pulse_freq']}:sample_rate={SR}",
               "-f", "lavfi", "-i",
               f"anoisesrc=d={duration}:c=pink:r={SR}:a=0.5:seed={rng.randrange(1, 2 ** 31)}"]
    join = "".join(f"[t{i}]" for i in range(n))
    fc = (
        f"{join}amix=inputs={n}:normalize=0[tones];"
        f"[{n}:a]volume={p['pulse_vol']}[pulse];"
        f"[{n + 1}:a]lowpass=f={p['noise_high']},highpass=f={p['noise_low']},"
        f"volume={p['noise_vol']}[noise];"
        f"[tones][pulse]amix=inputs=2:normalize=0[bed1];"
        f"[bed1][noise]amix=inputs=2:normalize=0[bed2];"
        f"[bed2]aecho=0.8:0.9:{p['echo_d']}:{p['echo']},"
        f"aformat=sample_rates={SR}:channel_layouts=stereo[mix]"
    )
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[mix]",
           "-t", str(duration), "-c:a", "aac", "-b:a", "96k", "-ar", str(SR), str(out)]
    audio60._ffmpeg(cmd, timeout=120)
    return str(out)


def _write_wav(path: Path, samples: list[float]) -> None:
    """Write mono 16-bit 44.1k WAV from float samples in [-1, 1]."""
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for s in samples:
            v = max(-1.0, min(1.0, s))
            frames += struct.pack("<h", int(v * 32767))
        w.writeframes(bytes(frames))


def _envelope(n: int, attack: float, release: float) -> list[float]:
    """Linear attack/release gain over n samples."""
    out = [1.0] * n
    a = max(1, int(attack * SR))
    r = max(1, int(release * SR))
    for i in range(min(a, n)):
        out[i] = i / a
    for i in range(max(0, n - r), n):
        out[i] = max(0.0, (n - i) / r)
    return out


def sfx_library(out_dir: str, seed: int | None = None) -> dict:
    """Generate the 5 canonical SFX WAVs. Returns {name: path}.

    whoosh      filtered noise sweep, ~1.1s
    impact      low thump + transient, ~0.8s
    riser       rising tone/sweep, ~2.0s
    blip        short digital beep, ~0.3s
    data_sweep  quick pitch glide, ~0.6s
    """
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    rng = _seed_rng(seed)
    out = {}
    for name, fn in (
        ("whoosh", _sfx_whoosh), ("impact", _sfx_impact), ("riser", _sfx_riser),
        ("blip", _sfx_blip), ("data_sweep", _sfx_data_sweep),
    ):
        path = d / f"{name}.wav"
        fn(path, rng)
        out[name] = str(path)
    return out


def _sfx_whoosh(path: Path, rng: random.Random) -> None:
    n = int(1.1 * SR)
    # white noise through a short moving-average lowpass, plus a center-swell envelope
    win = max(1, int(0.004 * SR))
    buf: list[float] = [0.0] * n
    acc = 0.0
    for i in range(n):
        acc += (rng.random() * 2 - 1) * 0.5
        if i >= win:
            acc -= buf[i - win]
        buf[i] = acc / win
    env = _envelope(n, 0.12, 0.45)
    samples = [buf[i] * env[i] * 0.8 for i in range(n)]
    _write_wav(path, samples)


def _sfx_impact(path: Path, rng: random.Random) -> None:
    n = int(0.8 * SR)
    samples = [0.0] * n
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 14.0)
        thump = math.sin(2 * math.pi * 58 * t) * env
        crack = (rng.random() * 2 - 1) * math.exp(-t * 60.0) * 0.6
        samples[i] = thump * 0.9 + crack
    _write_wav(path, samples)


def _sfx_riser(path: Path, rng: random.Random) -> None:
    n = int(2.0 * SR)
    samples = [0.0] * n
    for i in range(n):
        t = i / SR
        prog = i / n
        f = 120.0 + 1800.0 * prog * prog  # accelerating sweep up
        env = max(0.0, (prog ** 1.6) * (1.0 - max(0.0, (t - 1.75) / 0.25)))
        shimmer = (rng.random() * 2 - 1) * 0.05 * prog
        samples[i] = (math.sin(2 * math.pi * f * t) * 0.5 + shimmer) * env
    _write_wav(path, samples)


def _sfx_blip(path: Path, rng: random.Random) -> None:
    n = int(0.3 * SR)
    f = rng.choice((660.0, 880.0, 990.0, 1320.0))
    env = _envelope(n, 0.002, 0.12)
    samples = [math.sin(2 * math.pi * f * (i / SR)) * env[i] * 0.7 for i in range(n)]
    _write_wav(path, samples)


def _sfx_data_sweep(path: Path, rng: random.Random) -> None:
    n = int(0.6 * SR)
    f0, f1 = 400.0, 2400.0
    env = _envelope(n, 0.01, 0.18)
    samples = []
    phase = 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * (i / n)  # linear frequency glide
        phase += 2 * math.pi * f / SR
        samples.append(math.sin(phase) * env[i] * 0.6)
    _write_wav(path, samples)


def _scene_transitions(scene_plan: dict | None) -> list[float]:
    """Timestamps (midpoint between scenes) where SFX should fire; [] if none."""
    if not scene_plan:
        return []
    scenes = scene_plan.get("scenes") or []
    if not scenes:
        return []
    out = []
    for a, b in zip(scenes, scenes[1:]):
        try:
            out.append(round((a["end"] + b["start"]) / 2.0, 2))
        except (KeyError, TypeError):
            continue
    return out


def mix_full(voice_path: str, music_path: str, sfx_plan: dict, out_path: str,
             scene_plan: dict | None = None) -> str:
    """Mix voice + music (+ optional SFX at scene transitions) into one AAC file.

    Music is ducked under narration with a sidechaincompressor keyed on the voice
    track; the whole bus is normalized to I=-16 / TP=-1.5. An empty sfx_plan degrades
    gracefully to the plain voice+music mix (same behavior as today).
    """
    from src.content import audio60

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # SFX apad must cover the full voice clip; use probed voice duration (60s in the
    # reel pipeline) so non-60 inputs still mix correctly.
    total = audio60.probe_duration(voice_path) or 60.0

    times = _scene_transitions(scene_plan)
    sfx_paths = [p for p in (Path(v) for v in sfx_plan.values()) if p.exists()] if sfx_plan else []
    if sfx_paths and times:
        # Each SFX is placed at a transition (cycled); adelay keeps it exact, apad
        # extends it to the full clip so amix length follows the voice input.
        sfx_filters, sfx_inputs, sfx_count = [], [], 0
        for i, sp in enumerate(sfx_paths):
            t_ms = int(times[i % len(times)] * 1000)
            sfx_inputs += ["-i", str(sp)]
            sfx_filters.append(
                f"[{2 + i}:a]aformat=sample_rates={SR}:channel_layouts=stereo,"
                f"apad=whole_dur={total},adelay={t_ms}|{t_ms}[sfx{i}]")
            sfx_count += 1
        mix_in = "".join(f"[sfx{i}]" for i in range(sfx_count))
        fc = (
            f"[0:a]aformat=sample_rates={SR}:channel_layouts=stereo,asplit[vmix][vkey];"
            f"[1:a]aformat=sample_rates={SR}:channel_layouts=stereo[music];"
            f"[music][vkey]sidechaincompress=threshold=0.05:ratio=6:attack=25:"
            f"release=400:makeup=2[duck];"
            + ";".join(sfx_filters) + ";"
            f"{mix_in}amix=inputs={sfx_count}:normalize=0[sfxbus];"
            f"[vmix][duck][sfxbus]amix=inputs=3:duration=first:normalize=0,"
            f"loudnorm=I=-16:TP=-1.5:LRA=11[mix]"
        )
        cmd = ["ffmpeg", "-y", "-i", voice_path, "-i", music_path, *sfx_inputs,
               "-filter_complex", fc, "-map", "[mix]", "-c:a", "aac", "-b:a", "160k",
               "-ar", str(SR), str(out)]
        audio60._ffmpeg(cmd, timeout=120)
        return str(out)

    # --- Plain voice+music (also the graceful path for empty sfx_plan) ---
    audio60._ffmpeg(
        ["ffmpeg", "-y", "-i", voice_path, "-i", music_path, "-filter_complex",
         "[1:a]volume=0.18[bed];[0:a][bed]amix=inputs=2:duration=first:dropout_transition=2,"
         "loudnorm=I=-16:TP=-1.5:LRA=11[mix]",
         "-map", "[mix]", "-c:a", "aac", "-b:a", "160k", "-ar", str(SR), str(out)],
        timeout=120)
    return str(out)
