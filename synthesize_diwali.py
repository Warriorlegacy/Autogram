import os
import sys
import shutil
import subprocess
import soundfile as sf
import numpy as np
from pathlib import Path
from kokoro_onnx import Kokoro

MODEL_PATH = r"D:\Autogram\models\kokoro\kokoro-v1.0.onnx"
VOICES_PATH = r"D:\Autogram\models\kokoro\voices-v1.0.bin"

PUBLIC_DIR = Path(r"d:\Autogram\docs\reel-studio-kit\public\reels\happy-diwali")
PROJECT_DIR = Path(r"d:\Autogram\docs\reel-studio-kit\projects\happy-diwali")
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_DIR.mkdir(parents=True, exist_ok=True)

SENTENCES = [
    "Happy Diwali to every engineer still pushing code in dark mode.",
    "May your inference latency stay under forty milliseconds, your GPUs never hit out of memory, and your token bills drop to zero.",
    "While everyone lights firecrackers outside, we are firing autonomous multi-agent swarms and compiling sixty frames per second video from terminal scripts.",
    "May Goddess Lakshmi bless your repository with zero merge conflicts, one hundred percent test passes, and automated revenue.",
    "From all of us at Signhify Studio, have an electric Diwali.",
    "Comment DIWALI and I will send our entire open source production vault straight to your DMs."
]

raw_wav = PUBLIC_DIR / "raw_vo.wav"
master_wav = PUBLIC_DIR / "vo.wav"

print("1. Synthesizing Happy Diwali voiceover with Kokoro ONNX (am_adam)...")
kokoro = Kokoro(MODEL_PATH, VOICES_PATH)

audio_chunks = []
sample_rate = 24000

for i, sent in enumerate(SENTENCES):
    print(f"   [{i+1}/{len(SENTENCES)}] {sent[:45]}...")
    samples, sample_rate = kokoro.create(sent, voice="am_adam", speed=1.12, lang="en-us")
    audio_chunks.append(samples)
    pause = np.zeros(int(sample_rate * 0.12), dtype=np.float32)
    audio_chunks.append(pause)

combined_samples = np.concatenate(audio_chunks)
sf.write(str(raw_wav), combined_samples, sample_rate)
duration = len(combined_samples) / sample_rate
print(f"✓ Raw voiceover saved: {raw_wav} ({duration:.2f}s)")

print("\n2. Mastering voiceover with FFmpeg broadcast chain...")
ffmpeg_cmd = [
    "ffmpeg", "-y", "-i", str(raw_wav),
    "-af", (
        "highpass=f=80,"
        "equalizer=f=160:t=q:w=1.2:g=2.5,"
        "equalizer=f=3200:t=q:w=1.5:g=2.0,"
        "acompressor=threshold=-16dB:ratio=3.5:attack=15:release=120,"
        "loudnorm=I=-16:TP=-1.5:LRA=10"
    ),
    "-ar", "44100",
    "-ac", "1",
    str(master_wav)
]
subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"✓ Mastered broadcast audio saved: {master_wav}")

# Also copy to projects dir
shutil.copyfile(master_wav, PROJECT_DIR / "vo.wav")
print(f"✓ Copied to: {PROJECT_DIR / 'vo.wav'}")

