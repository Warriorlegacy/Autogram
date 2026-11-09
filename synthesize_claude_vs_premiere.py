import os
import sys
import subprocess
import soundfile as sf
from pathlib import Path
import onnxruntime as ort
from kokoro_onnx import Kokoro

MODEL_PATH = r"D:\Autogram\models\kokoro\kokoro-v1.0.onnx"
VOICES_PATH = r"D:\Autogram\models\kokoro\voices-v1.0.bin"

PUBLIC_DIR = Path(r"d:\Autogram\docs\reel-studio-kit\public\reels\claude-vs-premiere")
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

TEXT = (
    "Why are video editors still paying thirty-five dollars a month to manually cut keyframes? "
    "What you are watching right now was not edited in Premiere or After Effects. "
    "Every single frame, subtitle, and impact cut was drawn in code by Claude. "
    "Using the open-source HyperFrames engine, Claude writes HTML and GSAP animation code, compiles the audio, and outputs a vertical MP4 in forty-five seconds. "
    "Zero timeline scrubbing. Zero rendering lag. Just pure code. "
    "Comment HYPER and I will DM you the free GitHub repo and setup prompt."
)

raw_wav = PUBLIC_DIR / "raw_vo.wav"
master_wav = PUBLIC_DIR / "vo.wav"

print("1. Synthesizing voiceover with Kokoro ONNX...")
opts = ort.SessionOptions()
opts.enable_mem_pattern = False
opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
opts.intra_op_num_threads = 1
opts.inter_op_num_threads = 1

sess = ort.InferenceSession(MODEL_PATH, sess_options=opts, providers=["CPUExecutionProvider"])
kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
kokoro.sess = sess

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
