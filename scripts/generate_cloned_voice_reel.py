"""
Generate Cloned Voice Narration & Suno-Style Procedural Music for the Viral Reel
Slug: ai-content-factory
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, "D:/Autogram")
import numpy as np
import soundfile as sf
import subprocess

from src.avatar_engine.voice import build_profile, condition_speech, read_wav
from src.documentary.music import generate, duck, Mood, SR

REPO_ROOT = Path("D:/Autogram")
BRIEF_PATH = REPO_ROOT / "video_studio" / "briefs" / "ai-content-factory.json"
OUTPUT_DIR = REPO_ROOT / "video_studio" / "output" / "ai-content-factory"
AUDIO_DIR = OUTPUT_DIR / "audio"
SCENES_DIR = AUDIO_DIR / "audio"
REF_VOICE = REPO_ROOT / "docs" / "cloned-voice" / "15813e50-6c36-424e-9dae-97c56120f9e0.mp3"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
SCENES_DIR.mkdir(parents=True, exist_ok=True)

# 1. Profile reference voice
print("[1/5] Profiling user cloned voice sample...")
profile = build_profile(REF_VOICE, work_dir=AUDIO_DIR / "_ref_work")
print(f"       -> Median F0: {profile.median_f0_hz:.1f}Hz, Centroid: {profile.spectral_centroid_hz:.1f}Hz")

# 2. Synthesize each scene with Kokoro/Edge and condition to user clone
brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
scene_files = []

print("[2/5] Synthesizing & conditioning scene voiceovers...")
for sc in brief["scenes"]:
    sid = sc["id"]
    text = sc["narration"]
    raw_wav = SCENES_DIR / f"{sid}_raw.wav"
    cond_wav = SCENES_DIR / f"{sid}.wav"
    
    # Try Kokoro first
    from kokoro_onnx import Kokoro
    from video_studio.audio import KOKORO_MODEL, KOKORO_VOICES
    
    k = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    # am_adam or am_puck has an energetic crisp foundation
    samples, sr = k.create(text, "am_adam", speed=1.05, lang="en-us")
    sf.write(str(raw_wav), np.asarray(samples), sr)
    
    # Condition to match user's cloned voice pitch & tone
    condition_speech(raw_wav, profile, cond_wav)
    scene_files.append(cond_wav)
    print(f"       -> Synthesized scene: {sid} ({len(samples)/sr:.2f}s)")

# 3. Concatenate narration track with scene spacing
print("[3/5] Assembling full narration master track...")
chunks = []
target_sr = 24000

for f in scene_files:
    data, sr = sf.read(str(f), dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != target_sr:
        # resample via ffmpeg or simple interp
        tmp = f.with_suffix(".24k.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(f), "-ar", str(target_sr), str(tmp)], check=True)
        data, sr = sf.read(str(tmp), dtype="float32")
    chunks.append(data)
    # Natural 0.25s pause
    chunks.append(np.zeros(int(target_sr * 0.25), dtype="float32"))

narration_master = np.concatenate(chunks)
narration_path = AUDIO_DIR / "narration.wav"
sf.write(str(narration_path), narration_master, target_sr)
total_duration = len(narration_master) / target_sr
print(f"       -> Full narration track: {total_duration:.2f}s at {narration_path}")

# 4. Generate Suno-Style Upbeat Tech Synth Track
print("[4/5] Generating upbeat tech procedural score...")
music_mood = Mood(
    key="A",
    root_octave=2,
    pad_gain=0.25,
    bass_gain=0.35,
    bell_gain=0.15,
    brightness=0.65,
    chord_seconds=6.0,
    bell_every=2
)
music_track = generate(total_duration + 3.0, music_mood, "ai-content-factory")

# 5. Mix: Duck music under narration by -14dB
print("[5/5] Mixing and ducking score under voiceover...")
# Resample narration to 48kHz for final mix
narr_48k_path = AUDIO_DIR / "narration_48k.wav"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(narration_path), "-ar", "48000", str(narr_48k_path)], check=True)
narr_48k, _ = sf.read(str(narr_48k_path), dtype="float32")

# Pad or trim music to match narration length
n_samples = len(narr_48k)
if len(music_track) < n_samples:
    music_track = np.pad(music_track, (0, n_samples - len(music_track)))
else:
    music_track = music_track[:n_samples]

ducked_music = duck(music_track, narr_48k, sr=SR, depth=0.65)
narr_stereo = np.stack([narr_48k, narr_48k], axis=1) if narr_48k.ndim == 1 else narr_48k
final_mix = narr_stereo * 0.95 + ducked_music * 0.35

final_mix_path = AUDIO_DIR / "final_reel_audio.wav"
sf.write(str(final_mix_path), final_mix, SR)
print(f"[OK] Master Mixed Audio produced: {final_mix_path}")
print("Ready for HyperFrames video composition!")
