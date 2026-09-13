"""Autonomous Instagram Reels pipeline (spec: AUTONOMOUS_INSTAGRAM_REELS_AGENT_SPEC).

Thin spec-compatible facade over the existing Autogram engine — no duplicated
provider logic:
- script  -> src.content.generator (OpenRouter :free chain + template fallback)
- visual  -> src.content.image_generator (Pollinations FLUX 9:16)
- TTS     -> edge-tts (no key, uncapped)
- subs    -> faster-whisper (optional) -> kinetic .ass karaoke
- render  -> FFmpeg + libass zoompan

Spec API preserved: generate_reel_content / synthesize_speech / download_visual /
to_ass_time / compile_word_level_ass / render_ffmpeg / execute_reels_pipeline.
"""

import asyncio
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent / "workspace"
BASE_DIR.mkdir(parents=True, exist_ok=True)

VOICE_NAME = os.getenv("REELS_VOICE", "en-US-ChristopherNeural")

AUDIO_FILE = str(BASE_DIR / "audio.mp3")
BACKGROUND_IMG = str(BASE_DIR / "background.jpg")
SUBTITLES_ASS = str(BASE_DIR / "subtitles.ass")
OUTPUT_REEL = str(BASE_DIR / "final_reel.mp4")

FREE_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nex-agi/nex-n2.5-pro:free",
    "google/gemma-4-31b-it:free",
]


def generate_reel_content(topic: str) -> dict:
    """Viral script + visual prompt + caption via OpenRouter :free (falls back to engine)."""
    import json

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    system_prompt = (
        "You are an elite Instagram viral content director. Create an engaging 20-second Reel script. "
        "Return STRICT JSON with keys: "
        "'script' (concise spoken text under 45 words, high-tension hook, no emojis), "
        "'visual_prompt' (photorealistic 9:16 portrait scene description, dramatic volumetric lighting), "
        "'caption' (punchy caption with 5 niche hashtags)."
    )
    if api_key:
        from openai import OpenAI

        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        last_err = None
        for model in FREE_MODELS:
            try:
                res = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Topic: {topic}"},
                    ],
                    response_format={"type": "json_object"},
                )
                data = json.loads(res.choices[0].message.content)
                if "script" in data and "visual_prompt" in data:
                    data.setdefault("caption", f"{topic} #reels #viral #psychology #facts #shorts")
                    return data
            except Exception as e:  # ponytail: try next free model, engine fallback below
                last_err = e
                logger.warning(f"OpenRouter {model} failed: {e}")
        logger.warning(f"All OpenRouter :free models failed ({last_err}); using engine fallback.")

    # $0 fallback: existing engine chain (groq/gemini/ollama/template — never fails)
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.content.generator import generator

    script = generator.generate_reel_script({"topic": topic, "pillar": "Tech Explainer"})
    return {
        "script": script["narration"],
        "visual_prompt": f"Cinematic 9:16 portrait of {script['subject']}, dramatic volumetric lighting, photorealistic",
        "caption": f"{script['caption']}\n\n{' '.join(script['hashtags'])}",
    }


async def synthesize_speech(text: str, output_path: str = AUDIO_FILE):
    import edge_tts

    comm = edge_tts.Communicate(text, voice=VOICE_NAME, rate="+5%", pitch="+0Hz")
    await comm.save(output_path)


def download_visual(prompt: str, output_path: str = BACKGROUND_IMG):
    """9:16 visual via existing Pollinations dispatcher (Cloudflare fallback built in)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.content.image_generator import image_generator

    clean = re.sub(r"[^a-zA-Z0-9\s]", "", prompt)[:180]
    image_generator.generate_image(clean, width=1080, height=1920, output_path=output_path)


def to_ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


_ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kinetic,Arial Black,76,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,2,5,60,60,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _events_for_words(words: list[tuple[str, float, float]], chunk_size: int = 3) -> list[str]:
    """Pure helper (testable without whisper): karaoke events for (word, start, end)."""
    events = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i : i + chunk_size]
        for active_idx, (_, w_start, w_end) in enumerate(chunk):
            parts = []
            for idx, (w, _, _) in enumerate(chunk):
                clean = w.strip().upper()
                if idx == active_idx:
                    parts.append(f"{{\\c&H0000FFFF\\fscx115\\fscy115}}{clean}{{\\fscx100\\fscy100\\c&H00FFFFFF}}")
                else:
                    parts.append(f"{{\\c&H00FFFFFF}}{clean}")
            events.append(
                f"Dialogue: 0,{to_ass_time(w_start)},{to_ass_time(w_end)},Kinetic,,0,0,0,,{' '.join(parts)}"
            )
    return events


def compile_word_level_ass(audio_path: str = AUDIO_FILE, ass_path: str = SUBTITLES_ASS):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        WhisperModel = None
    events: list[str] = []
    if WhisperModel is not None:
        whisper = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = whisper.transcribe(audio_path, word_timestamps=True)
        for segment in segments:
            chunk_words = [(w.word, w.start, w.end) for w in (segment.words or [])]
            events.extend(_events_for_words(chunk_words))
    else:
        # ponytail: no naive fallback — fake timestamps would desync karaoke.
        # Upgrade path: pip install faster-whisper for true word alignment.
        raise RuntimeError("faster-whisper not installed; run pip install -r requirements.txt")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(_ASS_HEADER + "\n".join(events))


def render_ffmpeg(
    image_path: str = BACKGROUND_IMG,
    audio_path: str = AUDIO_FILE,
    ass_path: str = SUBTITLES_ASS,
    output_path: str = OUTPUT_REEL,
):
    clean_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "zoompan=z='min(zoom+0.0012,1.15)':d=750:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
        f"subtitles='{clean_ass}'[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path,
    ]
    subprocess.run(cmd, check=True)


def execute_reels_pipeline(topic: str) -> dict:
    import json as _json

    data = generate_reel_content(topic)
    asyncio.run(synthesize_speech(data["script"], AUDIO_FILE))
    download_visual(data["visual_prompt"], BACKGROUND_IMG)
    compile_word_level_ass(AUDIO_FILE, SUBTITLES_ASS)
    render_ffmpeg(BACKGROUND_IMG, AUDIO_FILE, SUBTITLES_ASS, OUTPUT_REEL)
    result = {
        "video_path": OUTPUT_REEL,
        "caption": data["caption"],
        "script": data["script"],
        "visual_prompt": data["visual_prompt"],
        "topic": topic,
    }
    with open(str(BASE_DIR / "metadata.json"), "w", encoding="utf-8") as f:
        _json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    result = execute_reels_pipeline(sys.argv[1] if len(sys.argv) > 1 else "The Neuroscience of the Flow State")
    print(f"Generated Reel at: {result['video_path']}")
