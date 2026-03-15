"""
Content Filler — Replace Placeholders with Real Content
========================================================
Replaces {{placeholder}} markers in generated HTML with user-provided content.

Usage by Agent:
    1. Read the generated HTML template
    2. Collect content from user in conversation
    3. Use this script to fill placeholders
    4. Save filled HTML, then convert to EML

Dependencies: Python stdlib only
"""

import re
from pathlib import Path


def list_placeholders(html: str) -> list:
    """Extract all {{placeholder}} markers from HTML. Returns unique sorted list."""
    return sorted(set(re.findall(r"\{\{(\w+)\}\}", html)))


def fill_placeholders(html: str, content: dict) -> str:
    """
    Replace {{key}} markers with content values.
    Values can be plain text or HTML snippets.
    """
    for key, value in content.items():
        html = html.replace(f"{{{{{key}}}}}", value)
    return html


def fill_from_file(html_path: str, content: dict, output_path: str) -> str:
    """Read HTML file, fill placeholders, save to output."""
    html = Path(html_path).read_text(encoding="utf-8")
    filled = fill_placeholders(html, content)
    Path(output_path).write_text(filled, encoding="utf-8")
    print(f"Filled template saved: {output_path}")
    return filled


def unfilled_placeholders(html: str) -> list:
    """List any remaining unfilled {{placeholder}} markers."""
    return sorted(set(re.findall(r"\{\{(\w+)\}\}", html)))


def fill_batch(html: str, content: dict, image_dir: str = None) -> str:
    """
    Fill multiple placeholders at once.

    Args:
        html: HTML with {{placeholder}} markers
        content: dict mapping placeholder names to values
        image_dir: optional directory path; if provided, auto-maps
                   image filenames to CID placeholders

    Returns:
        HTML with placeholders replaced
    """
    # Auto-map images if directory provided
    if image_dir:
        from pathlib import Path
        img_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
        img_dir = Path(image_dir)
        if img_dir.exists():
            for p in img_dir.iterdir():
                if p.suffix.lower() in img_exts and p.stem not in content:
                    content[p.stem] = f"cid:{p.stem}"

    return fill_placeholders(html, content)


def generate_fill_template(html: str) -> str:
    """
    Generate a YAML-like template showing all placeholders for the user to fill.
    Agent can show this to the user for batch input.

    Example output:
        title: 在此输入标题
        subtitle: 在此输入副标题
        section_1_title: 章节标题
        section_1_content: 在此输入正文内容
    """
    placeholders = list_placeholders(html)
    lines = ["# Fill in values for each placeholder below:"]
    for p in placeholders:
        lines.append(f"{p}: ")
    return "\n".join(lines)
