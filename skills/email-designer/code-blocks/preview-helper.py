"""
Preview Helper — Auto-open HTML in Browser + ASCII Layout Summary
=================================================================
Opens generated HTML in default browser and prints an ASCII layout
summary so user can get a quick overview without leaving the terminal.

Dependencies: Python stdlib only
"""

import subprocess
import sys
import re
from pathlib import Path


def open_in_browser(html_path: str) -> bool:
    """Open HTML file in default browser. Returns True if successful."""
    path = Path(html_path).resolve()
    if not path.exists():
        print(f"File not found: {html_path}")
        return False

    if sys.platform == "darwin":
        subprocess.run(["open", str(path)])
    elif sys.platform == "win32":
        subprocess.run(["start", str(path)], shell=True)
    else:
        subprocess.run(["xdg-open", str(path)])

    print(f"Opened in browser: {path}")
    return True


def ascii_layout_summary(html: str) -> str:
    """
    Generate a simple ASCII representation of the email layout.
    Extracts section structure from HTML comments and headings.
    """
    lines = []
    width = 50

    lines.append("\u250c" + "\u2500" * width + "\u2510")

    # Extract sections from HTML headings and comments
    sections = []

    # Look for component comments
    for match in re.finditer(r"<!--\s*(.+?(?:Component|Section|Header|Footer).*?)\s*-->", html, re.IGNORECASE):
        sections.append(match.group(1).strip())

    # Fallback: detect by headings
    if not sections:
        for match in re.finditer(r"<h[1-3][^>]*>([^<]+)</h[1-3]>", html, re.IGNORECASE):
            sections.append(match.group(1).strip())
        if not sections:
            if "<img" in html.lower():
                sections.append("Image Content")
            if "<table" in html.lower():
                sections.append("Table Content")
            sections.append("Email Body")

    for i, section in enumerate(sections):
        name = section[:width - 4] if len(section) > width - 4 else section
        padding = (width - len(name)) // 2
        lines.append("\u2502" + " " * padding + name + " " * (width - padding - len(name)) + "\u2502")
        if i < len(sections) - 1:
            lines.append("\u251c" + "\u2500" * width + "\u2524")

    lines.append("\u2514" + "\u2500" * width + "\u2518")
    return "\n".join(lines)
