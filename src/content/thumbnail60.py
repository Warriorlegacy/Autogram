"""Deterministic 9:16 + 1:1 thumbnail generation for 60s reels (Signhify.studio).

Pure Playwright chromium screenshot of a self-contained HTML page: no network,
no external fonts (system font fallback via @font-face file:// on Windows, or
generic sans-serif), deterministic given (hook, topic, theme). Fail-soft: any
exception -> None, caller records status. NEVER burns captions or overlays
video frames — this is a standalone social cover image.
"""
from __future__ import annotations

import html
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

TARGET_W, TARGET_H = 1080, 1920
SQUARE_W, SQUARE_H = 1080, 1080
BG = "#020617"            # slate-950
ACCENT = "#10b981"        # emerald-500
ACCENT_DIM = "#059669"

# Fonts installed on the runner (Windows): fallback list; Plus Jakarta Sans is
# preferred but we never hard-fail on it.
FONT_FAMILIES = [
    ("Plus Jakarta Sans", Path(r"C:\Windows\Fonts\PlusJakartaSans-VariableFont_wght.ttf")),
    ("Plus Jakarta Sans", Path(r"C:\Windows\Fonts\PlusJakartaSans-Regular.ttf")),
    ("Bahnschrift", Path(r"C:\Windows\Fonts\bahnschrift.ttf")),
    ("Arial", Path(r"C:\Windows\Fonts\arial.ttf")),
]

FONT_STACK = "Plus Jakarta Sans, Bahnschrift, Arial, 'Segoe UI', sans-serif"


def _font_src() -> str:
    """Inline @font-face for the first existing system font file (deterministic)."""
    for name, path in FONT_FAMILIES:
        if path.exists():
            return (f"@font-face {{ font-family:'{name}'; src:url('file:///{path.as_posix()}') "
                    "format('truetype'); font-weight:100 900; }}\n"
                    f":root {{ --font: '{name}, {FONT_STACK}'; }}")
    return f":root {{ --font: '{FONT_STACK}'; }}"


def _split_words(hook: str, topic: str, max_words: int = 5, max_len: int = 14) -> list[str]:
    """2-5 high-contrast words from the hook (or topic), deduped, length-capped."""
    text = re.sub(r"[^A-Za-z0-9'’\- ]+", " ", f"{hook} {topic}").strip()
    words = [w for w in re.split(r"\s+", text) if w]
    # stopwords that read as filler on a thumbnail
    stop = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
            "is", "are", "it's", "you", "your", "this", "that", "what", "here's"}
    seen, out = set(), []
    for w in words:
        clean = w.strip("'’").strip()
        if not clean or clean.lower() in stop:
            continue
        if clean.lower() in seen:
            continue
        seen.add(clean.lower())
        out.append(clean[:max_len])
        if len(out) >= max_words:
            break
    if not out:
        out = [w for w in (topic or "Signhify").split()][:2]
    return out or ["Signhify"]


def _thumbnail_html(hook: str, topic: str, theme: str, words: list[str],
                    show_brand: bool = True, square: bool = False) -> str:
    """Self-contained HTML; dark bg #020617, emerald accent, 1 dominant visual."""
    w, h = (SQUARE_W, SQUARE_H) if square else (TARGET_W, TARGET_H)
    # one dominant visual: abstract gradient orb + grid + emerald glow (deterministic, no images)
    orb_radius = 430 if not square else 340
    orb_y = 470 if not square else 300
    tag = html.escape((theme or "B").upper())
    brand = "<div class='brand'>signhify<span>.studio</span></div>" if show_brand else ""
    word_html = "".join(
        f"<span class='w' style='--i:{i}'>{html.escape(w)}</span>"
        for i, w in enumerate(words))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><style>
{_font_src()}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{w}px; height:{h}px; overflow:hidden; background:{BG};
            font-family:var(--font); }}
.page {{ position:relative; width:{w}px; height:{h}px; background:
  radial-gradient(120% 90% at 50% 0%, #0b1526 0%, {BG} 55%),
  radial-gradient(60% 45% at 50% 108%, rgba(16,185,129,.16) 0%, transparent 70%);
  display:flex; flex-direction:column; }}
.grid {{ position:absolute; inset:0; background-image:
  linear-gradient(rgba(148,163,184,.07) 1px, transparent 1px),
  linear-gradient(90deg, rgba(148,163,184,.07) 1px, transparent 1px);
  background-size:64px 64px; }}
.orb {{ position:absolute; left:50%; top:{orb_y}px; width:{orb_radius}px; height:{orb_radius}px;
  transform:translateX(-50%);
  background:radial-gradient(circle at 35% 30%, rgba(52,211,153,.55) 0%, rgba(16,185,129,.28) 42%, rgba(2,6,23,0) 72%);
  border-radius:50%; filter:blur(6px); }}
.orb::after {{ content:""; position:absolute; inset:14%; border-radius:50%;
  border:2px solid rgba(16,185,129,.45);
  box-shadow:0 0 60px rgba(16,185,129,.35), inset 0 0 40px rgba(16,185,129,.18); }}
.tag {{ position:absolute; top:64px; left:64px; font-weight:800; letter-spacing:.28em;
  font-size:34px; color:{ACCENT}; }}
.brand {{ position:absolute; bottom:{56 if not square else 44}px; left:64px; right:64px;
  font-size:{44 if not square else 38}px; font-weight:800; color:#e2e8f0; letter-spacing:.04em; }}
.brand span {{ color:{ACCENT}; }}
.words {{ position:absolute; left:64px; right:64px; {("top:1180px;" if not square else "top:560px;")}
  display:flex; flex-direction:column; gap:{34 if not square else 26}px; }}
.w {{ font-size:{150 if not square else 118}px; font-weight:900; line-height:1.02;
  color:#f8fafc; text-shadow:0 6px 30px rgba(2,6,23,.9); letter-spacing:-.02em; }}
.w:nth-child(2n) {{ color:{ACCENT}; }}
.sq {{ position:absolute; right:64px; {("top:1120px;" if not square else "top:470px;")}
  width:{96 if not square else 84}px; height:{96 if not square else 84}px;
  border-radius:18px; background:linear-gradient(135deg, {ACCENT}, #0ea5e9);
  display:flex; align-items:center; justify-content:center;
  font-size:{44 if not square else 36}px; font-weight:900; color:{BG}; }}
</style></head>
<body><div class="page">
  <div class="grid"></div>
  <div class="orb"></div>
  <div class="tag">{tag}</div>
  <div class="words">{word_html}</div>
  <div class="sq">▶</div>
  {brand}
</div></body></html>"""


def _screenshot(html_text: str, out_path: str, width: int, height: int) -> str:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height},
                                device_scale_factor=1.0)
        page.set_content(html_text, wait_until="load", timeout=20000)
        page.screenshot(path=out_path, clip={"x": 0, "y": 0, "width": width, "height": height})
        browser.close()
    return out_path


def generate_thumbnail(hook: str, topic: str, out_dir: str | Path,
                       theme: str = "", square: bool = False,
                       show_brand: bool = True) -> str | None:
    """Render thumbnail.png (1080x1920) or thumbnail_1x1.png (1080x1080).

    Deterministic given (hook, topic, theme). Returns output path or None on
    failure (never raises).
    """
    try:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        name = "thumbnail_1x1.png" if square else "thumbnail.png"
        out = out_dir / name
        words = _split_words(hook, topic)
        w, h = (SQUARE_W, SQUARE_H) if square else (TARGET_W, TARGET_H)
        html_text = _thumbnail_html(hook, topic, theme, words, show_brand, square)
        _screenshot(html_text, str(out), w, h)
        if not out.exists() or out.stat().st_size < 500:
            logger.warning(f"thumbnail {name} suspiciously small or missing")
            return None
        return str(out)
    except Exception as e:
        logger.warning(f"thumbnail generation failed: {e}")
        return None
