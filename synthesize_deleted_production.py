import os
import sys
import subprocess
import soundfile as sf
import numpy as np
from pathlib import Path
from kokoro_onnx import Kokoro
from faster_whisper import WhisperModel

MODEL_PATH = r"D:\Autogram\models\kokoro\kokoro-v1.0.onnx"
VOICES_PATH = r"D:\Autogram\models\kokoro\voices-v1.0.bin"

PROJECT_DIR = Path(r"d:\Autogram\docs\reel-studio-kit\projects\deleted-production")
PUBLIC_DIR = Path(r"d:\Autogram\docs\reel-studio-kit\public\reels\deleted-production")
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

TEXT = (
    "Claude... I think I just dropped the production database. "
    "The client's CEO is calling my phone. "
    "My hands are shaking. "
    "And there are two branches: production, and production DO NOT TOUCH. "
    "Instead of panicking, I ran one open-source Claude skill. "
    "It diffed our last forty merged PRs, recovered the schema state, and restored every table in three minutes. "
    "Stop stressing over fatal terminal errors. "
    "Comment RESTORE and I'll DM you the exact script."
)

raw_wav = PUBLIC_DIR / "raw_vo.wav"
master_wav = PUBLIC_DIR / "vo.wav"

print("1. Synthesizing voiceover with Kokoro ONNX (am_adam, speed=1.12)...")
kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
samples, sample_rate = kokoro.create(TEXT, voice="am_adam", speed=1.12, lang="en-us")
sf.write(str(raw_wav), samples, sample_rate)
print(f"✓ Raw voiceover saved: {raw_wav} ({len(samples)/sample_rate:.2f}s)")

print("\n2. Mastering voiceover with FFmpeg broadcast chain...")
ffmpeg_cmd = [
    "ffmpeg", "-y", "-i", str(raw_wav),
    "-af", (
        "highpass=f=80,"
        "equalizer=f=160:t=q:w=1.2:g=2.5,"
        "equalizer=f=3200:t=q:w=1.5:g=2.0,"
        "acompressor=threshold=-16dB:ratio=3.5:attack=15:release=120,"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    ),
    "-ar", "44100", "-ac", "1",
    str(master_wav)
]
subprocess.run(ffmpeg_cmd, check=True)
print(f"✓ Mastered vocal track saved: {master_wav}")

print("\n3. Transcribing word timestamps with faster-whisper (tiny)...")
whisper = WhisperModel("tiny", device="cpu", compute_type="int8")
segments, info = whisper.transcribe(str(master_wav), word_timestamps=True, language="en")

words = []
for seg in segments:
    for w in seg.words:
        cleaned = w.word.strip()
        if cleaned:
            words.append({
                "word": cleaned,
                "start": round(w.start, 3),
                "end": round(w.end, 3),
                "confidence": round(w.probability, 3)
            })

print(f"✓ Transcribed {len(words)} words over {info.duration:.2f}s")

# Save captions.words.json directly
import json
words_json_path = PUBLIC_DIR / "captions.words.json"
with open(words_json_path, "w", encoding="utf-8") as f:
    json.dump(words, f, indent=2)
print(f"✓ Word timestamps saved: {words_json_path}")

