import os
import shutil
import time
from pathlib import Path
import soundfile as sf
import numpy as np
from gradio_client import Client, handle_file
from dotenv import load_dotenv

load_dotenv(r"d:\Autogram\.env")

HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")

REF_AUDIO = r"d:\Autogram\docs\cloned-voice\15813e50-6c36-424e-9dae-97c56120f9e0.mp3"
REF_TEXT = (
    "This is your voice clone preview, take a quick listen, hi, I'm excited you're here, "
    "this is your voice clone preview, take a quick listen, a great voice clone should sound "
    "clear, energetic and just like you, close your eyes, does it sound like you're talking? "
    "If you like what you hear, let's make your first video."
)

SCENES = [
    {
        "id": "factory-hook",
        "start": 0.0,
        "max_dur": 8.5,
        "text": "Stop paying monthly fees for video tools. Twelve open-source GitHub repositories can run your entire content factory.",
    },
    {
        "id": "factory-research-voice",
        "start": 9.0,
        "max_dur": 7.5,
        "text": "ScrapeCreators extracts viral hooks from top posts, while VoiceStudio gives you local voice cloning with zero API costs.",
    },
    {
        "id": "factory-code-video",
        "start": 17.0,
        "max_dur": 8.0,
        "text": "HyperFrames turns HTML and GSAP code into finished vertical videos, while FLUX two generates sharp developer thumbnails on demand.",
    },
    {
        "id": "factory-production",
        "start": 25.5,
        "max_dur": 8.0,
        "text": "OpenMontage stitches b-roll and subtitles in seconds, while Social Media Agent queues posts to your channels.",
    },
    {
        "id": "factory-cta",
        "start": 34.0,
        "max_dur": 7.0,
        "text": "All twelve repositories run locally on your laptop. Comment FACTORY and I will send you the clickable link sheet.",
    },
]

OUT_DIR = Path(r"d:\Autogram\video_studio\output\ai-content-factory\audio")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def synthesize_all():
    print(f"Connecting to Voice Cloning Engine with HF_TOKEN (length: {len(HF_TOKEN) if HF_TOKEN else 0})...")
    client = Client("mrfakename/E2-F5-TTS", token=HF_TOKEN)
    
    generated_files = []
    
    for idx, scene in enumerate(SCENES):
        scene_id = scene["id"]
        text = scene["text"]
        dest = OUT_DIR / f"{scene_id}_cloned.wav"
        
        # Check if already generated and valid
        if dest.exists() and dest.stat().st_size > 50000:
            data, sr = sf.read(str(dest))
            dur = len(data) / sr
            print(f"[{idx+1}/{len(SCENES)}] '{scene_id}' already generated ({dur:.2f}s). Skipping.")
            generated_files.append((scene, dest, dur, sr))
            continue
            
        print(f"\n[{idx+1}/{len(SCENES)}] Synthesizing '{scene_id}':\n  \"{text}\"")
        
        t0 = time.time()
        result_path = client.predict(
            ref_audio=handle_file(REF_AUDIO),
            ref_text=REF_TEXT,
            gen_text=text,
            remove_silence=True,
            api_name="/predict"
        )
        t_gen = time.time() - t0
        
        # Read and check duration
        data, sr = sf.read(result_path)
        dur = len(data) / sr
        print(f"  -> Generated in {t_gen:.1f}s. Duration: {dur:.2f}s (max allowed: {scene['max_dur']}s)")
        
        # Save to destination
        shutil.copy2(result_path, dest)
        generated_files.append((scene, dest, dur, sr))
        time.sleep(2)  # courteous gap between calls
        
    print("\nAll scenes successfully cloned!")
    return generated_files

if __name__ == "__main__":
    synthesize_all()
