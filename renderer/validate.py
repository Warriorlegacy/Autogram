"""
Validation utilities for Instagram Carousel Slides.
Checks aspect ratio, dimensions, file size, and text limits.
"""

import os
from pathlib import Path
from PIL import Image

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1350
TARGET_ASPECT_RATIO = TARGET_WIDTH / TARGET_HEIGHT  # 0.8 (4:5)

STORY_TARGET_WIDTH = 1080
STORY_TARGET_HEIGHT = 1920
STORY_TARGET_ASPECT_RATIO = STORY_TARGET_WIDTH / STORY_TARGET_HEIGHT  # 0.5625 (9:16)

MAX_HEADLINE_CHARS = 80
MAX_BODY_CHARS = 240
MAX_FILE_SIZE_BYTES = 8 * 1024 * 1024  # 8MB Meta limit

class ValidationError(Exception):
    pass

def validate_slide_content(slide: dict) -> list[str]:
    """Check text length limits before rendering."""
    warnings = []
    headline = slide.get("headline", "")
    body = slide.get("body", "")
    
    if len(headline) > MAX_HEADLINE_CHARS:
        warnings.append(
            f"Slide {slide.get('slide_number')}: Headline length ({len(headline)}) exceeds {MAX_HEADLINE_CHARS} chars."
        )
    if len(body) > MAX_BODY_CHARS:
        warnings.append(
            f"Slide {slide.get('slide_number')}: Body length ({len(body)}) exceeds {MAX_BODY_CHARS} chars."
        )
    return warnings

import time

def validate_image_file(image_path: str | Path, expected_width: int = TARGET_WIDTH, expected_height: int = TARGET_HEIGHT) -> dict:
    """Validate rendered image dimensions, format, and aspect ratio."""
    path = Path(image_path)
    if not path.exists():
        raise ValidationError(f"Rendered image file not found: {path}")

    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(f"File {path.name} size ({file_size} bytes) exceeds 8MB limit.")

    width = height = 0
    format_name = ""
    for attempt in range(5):
        try:
            with Image.open(path) as img:
                img.load()
                width, height = img.size
                format_name = (img.format or "").upper()
                break
        except Exception as e:
            if attempt == 4:
                raise ValidationError(f"Image {path.name} could not be identified: {e}")
            time.sleep(0.1)

    expected_ratio = expected_width / expected_height if expected_height else 1.0
    aspect = width / height if height else 0

    if width != expected_width or height != expected_height:
        raise ValidationError(
            f"Image {path.name} resolution is {width}x{height}, expected {expected_width}x{expected_height}."
        )

    if abs(aspect - expected_ratio) > 0.01:
        raise ValidationError(
            f"Image {path.name} aspect ratio {aspect:.3f} does not match expected {expected_ratio:.3f}."
        )

    if format_name not in ["JPEG", "JPG", "PNG"]:
        raise ValidationError(f"Image {path.name} format is {format_name}, expected JPEG or PNG.")

    return {
        "valid": True,
        "path": str(path),
        "width": width,
        "height": height,
        "size_bytes": file_size,
        "format": format_name
    }
