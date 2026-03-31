"""
EML to HTML Extractor — Extract HTML and Images from EML Files
===============================================================
Extracts HTML content and CID-embedded images from .eml files,
enabling users to import existing emails for modification or
crystallization into production mode projects.

Usage by Agent:
    1. User provides an .eml file path
    2. Execute extract_from_eml(eml_path) to get HTML + images
    3. Execute save_extracted(result, output_dir) to save files
    4. The saved HTML has CID references converted to relative paths

Dependencies: Python stdlib only (email module)
"""

import email
import os
import re
from email import policy
from pathlib import Path
from typing import Dict, Optional


def extract_from_eml(eml_path: str) -> dict:
    """
    Extract HTML content and embedded images from an EML file.

    Args:
        eml_path: Path to the .eml file

    Returns:
        dict with keys:
            - subject: str — email subject
            - from: str — sender address
            - to: str — recipient(s)
            - html: str or None — HTML content (None if no HTML part)
            - plain_text: str or None — plain text content
            - images: dict — {content_id: bytes} for CID-embedded images
    """
    with open(eml_path, "r", encoding="utf-8", errors="replace") as f:
        msg = email.message_from_file(f, policy=policy.default)

    result = {
        "subject": str(msg.get("Subject", "")),
        "from": str(msg.get("From", "")),
        "to": str(msg.get("To", "")),
        "html": None,
        "plain_text": None,
        "images": {},
    }

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if content_type == "text/html" and "attachment" not in content_disposition:
                result["html"] = part.get_content()
            elif content_type == "text/plain" and "attachment" not in content_disposition:
                result["plain_text"] = part.get_content()
            elif content_type.startswith("image/"):
                content_id = part.get("Content-ID", "")
                if content_id:
                    # Strip angle brackets: <logo> → logo
                    cid = content_id.strip("<>")
                    result["images"][cid] = part.get_payload(decode=True)
                else:
                    # Use filename as key
                    filename = part.get_filename()
                    if filename:
                        name = Path(filename).stem
                        result["images"][name] = part.get_payload(decode=True)
    else:
        content_type = msg.get_content_type()
        if content_type == "text/html":
            result["html"] = msg.get_content()
        elif content_type == "text/plain":
            result["plain_text"] = msg.get_content()

    return result


def save_extracted(result: dict, output_dir: str) -> dict:
    """
    Save extracted HTML and images to a directory.
    Converts CID references in HTML to relative image paths.

    Args:
        result: dict from extract_from_eml()
        output_dir: directory to save files into

    Returns:
        dict with keys:
            - html_path: str — path to saved HTML file
            - image_paths: list[str] — paths to saved image files
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    images_dir = output / "images"
    images_dir.mkdir(exist_ok=True)

    saved = {"html_path": None, "image_paths": []}

    # Save images
    image_cid_to_filename = {}
    for cid, img_bytes in result["images"].items():
        # Determine extension from magic bytes
        ext = _detect_image_ext(img_bytes)
        safe_name = re.sub(r'[^\w\-.]', '_', cid)
        filename = f"{safe_name}{ext}"
        img_path = images_dir / filename
        img_path.write_bytes(img_bytes)
        saved["image_paths"].append(str(img_path))
        image_cid_to_filename[cid] = f"images/{filename}"

    # Save HTML with CID → relative path conversion
    if result["html"]:
        html = result["html"]
        for cid, rel_path in image_cid_to_filename.items():
            html = html.replace(f"cid:{cid}", rel_path)
        html_path = output / "imported-email.html"
        html_path.write_text(html, encoding="utf-8")
        saved["html_path"] = str(html_path)

    return saved


def _detect_image_ext(data: bytes) -> str:
    """Detect image format from magic bytes."""
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return ".png"
    elif data[:2] == b'\xff\xd8':
        return ".jpg"
    elif data[:4] == b'GIF8':
        return ".gif"
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return ".webp"
    return ".png"  # default
