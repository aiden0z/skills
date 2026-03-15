"""
HTML Patcher — Targeted Modifications Without Full Regeneration
===============================================================
Applies specific changes to generated HTML (color, text, spacing)
without regenerating the entire template.

Usage by Agent:
    When user says "change the header color to red" or "make the title bigger",
    use these functions instead of regenerating everything.

Dependencies: Python stdlib only (re)
"""

import re
from pathlib import Path


def replace_color(html: str, old_color: str, new_color: str) -> str:
    """Replace a color value everywhere in the HTML (case-insensitive)."""
    # Replace in both bgcolor attributes and CSS color/background-color values
    result = re.sub(re.escape(old_color), new_color, html, flags=re.IGNORECASE)
    return result


def replace_text(html: str, old_text: str, new_text: str) -> str:
    """Replace specific visible text content (not HTML tags/attributes)."""
    return html.replace(old_text, new_text)


def change_width(html: str, old_width: int, new_width: int) -> str:
    """Change the email container width."""
    result = html
    # Replace width="N" attributes
    result = result.replace(f'width="{old_width}"', f'width="{new_width}"')
    # Replace width: Npx in styles
    result = result.replace(f'width: {old_width}px', f'width: {new_width}px')
    result = result.replace(f'width:{old_width}px', f'width:{new_width}px')
    # Replace max-width
    result = result.replace(f'max-width: {old_width}px', f'max-width: {new_width}px')
    return result


def change_font_size(html: str, selector_text: str, new_size: int) -> str:
    """
    Change font-size for elements containing specific text.
    Finds the nearest style attribute and updates font-size.
    """
    # Find elements containing the selector text and change their font-size
    pattern = rf'(font-size:\s*)\d+px([^>]*>{re.escape(selector_text)})'
    result = re.sub(pattern, rf'\g<1>{new_size}px\2', html)
    return result


def add_section(html: str, section_html: str, before_footer: bool = True) -> str:
    """
    Insert a new section into the email.
    By default inserts before the footer.
    """
    if before_footer:
        # Find the footer (last major table or comment indicating footer)
        footer_markers = ['<!-- FOOTER', '<!-- Footer', 'footer']
        for marker in footer_markers:
            idx = html.lower().rfind(marker.lower())
            if idx > 0:
                # Find the start of the table containing the footer
                table_start = html.rfind('<table', 0, idx)
                if table_start > 0:
                    return html[:table_start] + section_html + "\n" + html[table_start:]

    # Fallback: insert before </body>
    body_end = html.rfind('</body>')
    if body_end > 0:
        return html[:body_end] + section_html + "\n" + html[body_end:]

    return html + section_html


def remove_section(html: str, section_title: str) -> str:
    """
    Remove a section by its title text.
    Removes from the section title table to the next section title or footer.
    """
    # Find the section title
    idx = html.find(section_title)
    if idx < 0:
        return html

    # Find the containing table start (go back to find <table)
    # Look for the section wrapper - typically a <tr> containing the title
    section_start = html.rfind('<tr>', 0, idx)
    # Find the next section title or footer
    remaining = html[idx + len(section_title):]
    # Look for next section pattern (section title h2)
    next_section = re.search(r'<td[^>]*style="padding:\s*24px', remaining)
    if next_section:
        section_end = idx + len(section_title) + next_section.start()
    else:
        section_end = len(html)

    if section_start > 0:
        return html[:section_start] + html[section_end:]
    return html


def patch_file(html_path: str, output_path: str = None, **operations) -> str:
    """
    Apply multiple patches to an HTML file.

    Args:
        html_path: path to HTML file
        output_path: where to save (default: overwrite input)
        **operations: keyword arguments specifying patches
            colors: dict of {old: new} color replacements
            texts: dict of {old: new} text replacements
            width: tuple of (old_width, new_width)

    Returns:
        Patched HTML string
    """
    html = Path(html_path).read_text(encoding="utf-8")

    if "colors" in operations:
        for old, new in operations["colors"].items():
            html = replace_color(html, old, new)

    if "texts" in operations:
        for old, new in operations["texts"].items():
            html = replace_text(html, old, new)

    if "width" in operations:
        old_w, new_w = operations["width"]
        html = change_width(html, old_w, new_w)

    out = output_path or html_path
    Path(out).write_text(html, encoding="utf-8")
    print(f"Patched: {out}")
    return html
