import json
import os
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

REPO_ROOT = Path(r"d:\Autogram")
AUDIO_DIR = REPO_ROOT / "video_studio" / "output" / "ai-content-factory" / "audio"
VIDEO_IN = REPO_ROOT / "video_studio" / "output" / "ai-content-factory" / "reel.mp4"
VIDEO_OUT = REPO_ROOT / "video_studio" / "output" / "ai-content-factory" / "reel.mp4"

SR = 48000
TOTAL_DURATION = 46.0  # matches the video duration exactly

# Scene cues (in seconds)
SCENE_CUES = [
    {"id": "factory-hook", "start": 0.30},
    {"id": "factory-research-voice", "start": 9.30},
    {"id": "factory-code-video", "start": 17.30},
    {"id": "factory-production", "start": 25.80},
    {"id": "factory-cta", "start": 34.30},
]

def build_voice_track():
    total_samples = int(TOTAL_DURATION * SR)
    voice_track = np.zeros(total_samples, dtype=np.float32)
    
    for cue in SCENE_CUES:
        scene_id = cue["id"]
        start_sec = cue["start"]
        start_idx = int(start_sec * SR)
        
        wav_path = AUDIO_DIR / f"{scene_id}_cloned.wav"
        if not wav_path.exists():
            raise FileNotFoundError(f"Missing {wav_path}")
            
        data, file_sr = sf.read(str(wav_path), dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
            
        # Resample to 48000 if needed
        if file_sr != SR:
            import scipy.signal
            num_samples = int(len(data) * float(SR) / file_sr)
            data = scipy.signal.resample(data, num_samples)
            
        # Apply a subtle 15ms fade-in and fade-out to prevent clicks
        fade_len = int(0.015 * SR)
        if len(data) > 2 * fade_len:
            data[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
            data[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)
            
        end_idx = min(total_samples, start_idx + len(data))
        voice_track[start_idx:end_idx] = data[:end_idx - start_idx]
        print(f"Placed '{scene_id}' at {start_sec:.2f}s - {start_sec + len(data)/SR:.2f}s (samples: {start_idx} to {end_idx})")
        
    voice_path = AUDIO_DIR / "user_cloned_voice_track.wav"
    sf.write(str(voice_path), voice_track, SR)
    print(f"Saved complete voice track: {voice_path} ({TOTAL_DURATION}s)")
    return voice_path

def generate_background_music(dest_path: Path):
    from src.content.music60 import build_music
    print("Synthesizing procedural dark-tech background score...")
    build_music(topic="AI Content Factory", style="dark_tech", duration=TOTAL_DURATION, out_path=str(dest_path), seed=42)
    print(f"Music bed generated: {dest_path}")
    return dest_path

def mix_tracks(voice_path: Path, music_path: Path, output_path: Path):
    print("Mixing voice and music with sidechain ducking and EBU R128 loudnorm...")
    
    # FFmpeg filtergraph:
    # [1:a] volume=0.22, asplit=2[m_duck][m_dry];
    # [0:a] asplit=2[v_orig][v_sidechain];
    # [m_duck][v_sidechain] sidechaincompress=threshold=0.08:ratio=6:attack=20:release=300[ducked_m];
    # [v_orig][ducked_m] amix=inputs=2:duration=first:dropout_transition=2[mixed];
    # [mixed] loudnorm=I=-16:TP=-1.5:LRA=11[normed]
    filtergraph = (
        "[1:a]volume=0.20[m_duck];"
        "[0:a]asplit=2[v_orig][v_sidechain];"
        "[m_duck][v_sidechain]sidechaincompress=threshold=0.08:ratio=6:attack=20:release=300[ducked_m];"
        "[v_orig][ducked_m]amix=inputs=2:duration=first:dropout_transition=2[mixed];"
        "[mixed]loudnorm=I=-16:TP=-1.5:LRA=11[normed]"
    )
    
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-nostats",
        "-i", str(voice_path),
        "-i", str(music_path),
        "-filter_complex", filtergraph,
        "-map", "[normed]",
        "-ar", "48000",
        "-ac", "2",
        str(output_path)
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg mix failed:\n{res.stderr}")
    print(f"Mixed master audio track saved: {output_path}")
    return output_path

def mux_to_video(video_path: Path, audio_path: Path, dest_path: Path):
    print("Muxing finalized audio track into video...")
    tmp_out = dest_path.with_name("reel_cloned_temp.mp4")
    
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-nostats",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(tmp_out)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg mux failed:\n{res.stderr}")
        
    tmp_out.replace(dest_path)
    print(f"Successfully muxed into {dest_path}")
    return dest_path

def main():
    voice_track = build_voice_track()
    music_bed = AUDIO_DIR / "procedural_bgm.m4a"
    generate_background_music(music_bed)
    
    master_audio = AUDIO_DIR / "final_reel_audio.wav"
    mix_tracks(voice_track, music_bed, master_audio)
    
    mux_to_video(VIDEO_IN, master_audio, VIDEO_OUT)
    print("All steps completed successfully!")

if __name__ == "__main__":
    main()
