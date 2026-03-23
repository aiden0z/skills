"""
CID Image Embedder — Utility for Email Image Embedding
=======================================================
Handles image discovery, MIME type detection, and CID reference generation.

Usage by Agent:
    - Use to scan a directory for images and generate CID mappings
    - Use to create placeholder images (1x1 transparent PNG)
    - Use to validate image paths before EML generation

Dependencies: Python stdlib only
"""

import base64
import hashlib
import mimetypes
from pathlib import Path


def scan_images(directory: str) -> dict:
    """Scan directory for images, return {filename_stem: path} mapping."""
    img_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
    images = {}
    for p in Path(directory).iterdir():
        if p.suffix.lower() in img_extensions:
            images[p.stem] = str(p)
    return images


def create_placeholder_png(output_path: str, width: int = 1, height: int = 1) -> str:
    """Create a minimal 1x1 transparent PNG placeholder (no Pillow needed)."""
    # Minimal valid PNG: 1x1 transparent pixel
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
        "nGNgYPgPAAEDAQAIicLsAAAABJRU5ErkJggg=="
    )
    Path(output_path).write_bytes(png_data)
    return output_path


def get_mime_type(path: str) -> str:
    """Detect MIME type for an image file."""
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


def sanitize_image_name(filename: str) -> str:
    """Generate an ASCII-safe CID from an image filename.

    ASCII filenames: use the stem directly (e.g., 'logo.png' -> 'logo').
    Non-ASCII filenames: use 'img_' + md5 hash prefix (e.g., '产品.png' -> 'img_a1b2c3d4e5f6g7h8').
    """
    stem = Path(filename).stem
    try:
        stem.encode("ascii")
        return stem
    except UnicodeEncodeError:
        path_hash = hashlib.md5(filename.encode("utf-8")).hexdigest()[:16]
        return f"img_{path_hash}"


def validate_images(image_map: dict) -> list:
    """Validate all image paths exist. Returns list of missing paths."""
    return [path for path in image_map.values() if not Path(path).exists()]
