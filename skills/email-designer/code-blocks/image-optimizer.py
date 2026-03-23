"""
Image Optimizer — Compress Images for Email Embedding
======================================================
Converts and compresses images to reduce EML file size.
Handles PNG→JPEG conversion, resizing, and transparency.

Usage by Agent:
    1. After user provides images to images/ directory
    2. Run optimize_directory('images/') to compress large files
    3. Report savings to user

Dependencies: pillow (auto-installed by deps-checker.py)
"""

import os
from pathlib import Path
from PIL import Image


def optimize_image(
    input_path: str,
    output_path: str = None,
    max_width: int = 1200,
    quality: int = 85,
) -> tuple:
    """Compress an image for email embedding.

    Converts PNG/GIF/BMP to JPEG, resizes if wider than max_width,
    and handles transparency (RGBA→RGB with white background).

    Args:
        input_path: Path to input image (any PIL-supported format)
        output_path: Path to save compressed JPEG. If None, overwrites
                     input with .jpg extension.
        max_width: Maximum width in pixels (maintains aspect ratio)
        quality: JPEG quality (1-100, default 85)

    Returns:
        Tuple of (output_path_str, original_size_kb, compressed_size_kb)
    """
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".jpg")
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    original_size_kb = os.path.getsize(input_path) / 1024

    img = Image.open(input_path)
    width, height = img.size

    # Handle transparency: paste on white background
    if img.mode in ("RGBA", "LA", "P"):
        if img.mode == "P":
            img = img.convert("RGBA")
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode in ("RGBA", "LA"):
            background.paste(img, mask=img.split()[-1])
        else:
            background.paste(img)
        img = background
    else:
        img = img.convert("RGB")

    # Resize if needed
    if width > max_width:
        scale = max_width / width
        new_height = round(height * scale)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Save as JPEG
    img.save(str(output_path), "JPEG", quality=quality, optimize=True)

    compressed_size_kb = os.path.getsize(output_path) / 1024

    return (str(output_path.resolve()), original_size_kb, compressed_size_kb)


def optimize_directory(
    image_dir: str,
    max_width: int = 1200,
    quality: int = 85,
    threshold_kb: int = 200,
) -> list:
    """Scan directory and optimize images exceeding size threshold.

    Only processes files larger than threshold_kb. Already-small files
    are skipped. JPEG files are only re-compressed if oversized.

    Args:
        image_dir: Directory containing images
        max_width: Maximum width in pixels
        quality: JPEG quality
        threshold_kb: Only optimize files larger than this (in KB)

    Returns:
        List of (filename, original_kb, compressed_kb) for optimized files.
        Empty list if no files needed optimization.
    """
    img_dir = Path(image_dir)
    if not img_dir.is_dir():
        return []

    img_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
    results = []

    for p in sorted(img_dir.iterdir()):
        if not p.is_file() or p.suffix.lower() not in img_extensions:
            continue

        size_kb = os.path.getsize(p) / 1024
        if size_kb <= threshold_kb:
            continue

        output_path = p.with_suffix(".jpg")
        _, original_kb, compressed_kb = optimize_image(
            str(p), str(output_path), max_width, quality
        )

        # Remove original if output is a different file
        if output_path != p and output_path.exists():
            p.unlink()

        results.append((output_path.name, original_kb, compressed_kb))

    return results
