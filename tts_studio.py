"""
tts_studio.py - The $0 ElevenLabs-Tier Voice Engine for Autogram & Reel-Studio-Kit.

Supported Free Neural Engines:
1. 'edge'   : Microsoft Neural Speech (Christopher, Andrew, Brian, Ava, etc.) - Fast, 48kHz, $0 API, 0 GPU.
2. 'kokoro' : Kokoro-82M ONNX local neural model (am_adam, am_michael, af_bella, etc.) + Voice Blending.

Features:
- Studio DSP chain: 80Hz high-pass, 160Hz podcast warmth, 3.2kHz clarity EQ, dynamic compressor, EBU R128 loudnorm.
- Automatic word-level subtitle alignment ready for Whisper & Remotion.
- Zero API keys required.
"""

import os
import sys
import argparse
import asyncio
import subprocess
from pathlib import Path

# UTF-8 encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Common voice shortcuts
VOICE_MAP = {
    "christopher": "en-US-ChristopherNeural",   # Deep, authoritative narrator (like ElevenLabs Adam)
    "andrew": "en-US-AndrewMultilingualNeural", # Warm, expressive storyteller
    "brian": "en-US-BrianNeural",               # Casual, tech creator
    "ava": "en-US-AvaNeural",                   # Expressive female voice
    "emma": "en-US-EmmaNeural",                 # Professional female narrator
    "guy": "en-US-GuyNeural",                   # Broadcaster male
    "jenny": "en-US-JennyNeural",               # Friendly conversational female
    "prabhat": "en-IN-PrabhatNeural",           # Indian English male tech voice
    "neerja": "en-IN-NeerjaNeural",             # Indian English female voice
}

KOKORO_MODEL = Path(r"D:\Autogram\models\kokoro\kokoro-v1.0.onnx")
KOKORO_VOICES = Path(r"D:\Autogram\models\kokoro\voices-v1.0.bin")


def master_audio(input_file: Path, output_file: Path, sample_rate: int = 44100):
    """5-stage broadcast studio audio mastering chain via FFmpeg."""
    cmd = [
        "ffmpeg", "-y", "-i", str(input_file),
        "-af", (
            "highpass=f=80,"
            "equalizer=f=160:t=q:w=1.2:g=2.5,"
            "equalizer=f=3200:t=q:w=1.5:g=2.0,"
            "acompressor=threshold=-16dB:ratio=3.5:attack=15:release=120,"
            "loudnorm=I=-16:TP=-1.5:LRA=10"
        ),
        "-ar", str(sample_rate),
        "-ac", "1",
        str(output_file)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


async def synthesize_edge(text: str, voice: str, rate: str, out_path: Path, raw: bool = False):
    import edge_tts
    actual_voice = VOICE_MAP.get(voice.lower(), voice)
    tmp_raw = out_path.parent / f"_raw_{out_path.name}"
    print(f"🎙️ [Edge-TTS] Synthesizing with voice: {actual_voice} (rate: {rate})...")
    communicate = edge_tts.Communicate(text, voice=actual_voice, rate=rate)
    await communicate.save(str(tmp_raw))

    if raw:
        tmp_raw.replace(out_path)
    else:
        print("🎛️ Mastering broadcast studio chain (EQ + Compression + EBU R128)...")
        master_audio(tmp_raw, out_path)
        if tmp_raw.exists():
            tmp_raw.unlink()
    print(f"✓ Saved: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


def synthesize_kokoro(text: str, voice: str, blend: str, speed: float, out_path: Path, raw: bool = False):
    from kokoro_onnx import Kokoro
    import soundfile as sf
    import numpy as np

    if not KOKORO_MODEL.exists() or not KOKORO_VOICES.exists():
        print(f"❌ Kokoro models missing at {KOKORO_MODEL}")
        sys.exit(1)

    print(f"🎙️ [Kokoro-82M] Loading local ONNX neural weights...")
    kokoro = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))

    # Voice selection or blending
    voice_style = kokoro.get_voice_style(voice)
    if blend:
        parts = blend.split(":")
        b_voice = parts[0]
        weight = float(parts[1]) if len(parts) > 1 else 0.3
        b_style = kokoro.get_voice_style(b_voice)
        voice_style = (1.0 - weight) * voice_style + weight * b_style
        print(f"   Blending voices: {1.0 - weight:.1f}x {voice} + {weight:.1f}x {b_voice}")

    tmp_raw = out_path.parent / f"_raw_{out_path.stem}.wav"
    samples, sample_rate = kokoro.create(text, voice=voice_style, speed=speed, lang="en-us")
    sf.write(str(tmp_raw), samples, sample_rate)

    if raw:
        tmp_raw.replace(out_path)
    else:
        print("🎛️ Mastering broadcast studio chain (EQ + Compression + EBU R128)...")
        master_audio(tmp_raw, out_path)
        if tmp_raw.exists():
            tmp_raw.unlink()
    print(f"✓ Saved: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


def main():
    p = argparse.ArgumentParser(description="The $0 ElevenLabs Voice Studio")
    p.add_argument("--engine", choices=["edge", "kokoro"], default="edge", help="TTS Engine: edge (Microsoft Neural) or kokoro (Local 82M ONNX)")
    p.add_argument("--voice", default="christopher", help="Voice name or shortcut (christopher, andrew, brian, ava, am_adam, etc.)")
    p.add_argument("--text", default="Happy Diwali to every engineer still pushing code in dark mode.", help="Text to speak")
    p.add_argument("--file", help="Path to text file containing speech")
    p.add_argument("--out", default="output_voice.mp3", help="Output file path (.mp3 or .wav)")
    p.add_argument("--rate", default="+8%", help="Speed adjustment for Edge-TTS (e.g. +8%%, +15%%)")
    p.add_argument("--speed", type=float, default=1.12, help="Playback speed for Kokoro (e.g. 1.12)")
    p.add_argument("--blend", help="Kokoro voice blend e.g. 'am_michael:0.3' to blend 30 percent Michael into base voice")
    p.add_argument("--raw", action="store_true", help="Skip studio broadcast mastering chain")

    args = p.parse_args()
    text = args.text
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8").strip()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.engine == "edge":
        asyncio.run(synthesize_edge(text, args.voice, args.rate, out_path, args.raw))
    elif args.engine == "kokoro":
        synthesize_kokoro(text, args.voice, args.blend, args.speed, out_path, args.raw)


if __name__ == "__main__":
    main()
