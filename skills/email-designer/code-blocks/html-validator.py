"""
HTML Validator — Check Outlook Compatibility Rules
===================================================
Scans generated HTML for common Outlook-breaking patterns.
Agent should run this AFTER generating HTML and BEFORE generating EML.

Usage by Agent:
    1. Generate HTML
    2. Run validate(html) to check for violations
    3. Fix any issues found
    4. Then proceed to EML generation

Dependencies: Python stdlib only (re)
"""

import re
from pathlib import Path


def validate(html: str) -> dict:
    """
    Validate HTML against Outlook compatibility rules.
    Returns dict with 'passed' (bool), 'errors' (list), 'warnings' (list).
    """
    errors = []
    warnings = []

    # ERRORS — will break in Outlook

    # 1. Flexbox usage
    if re.search(r'display\s*:\s*flex', html, re.IGNORECASE):
        errors.append("FLEX_LAYOUT: Found 'display:flex' — Outlook ignores flexbox. Use table layout.")

    # 2. Grid usage
    if re.search(r'display\s*:\s*grid', html, re.IGNORECASE):
        errors.append("GRID_LAYOUT: Found 'display:grid' — Outlook ignores CSS grid. Use table layout.")

    # 3. border-radius — only flag if used outside <!--[if !mso]> blocks
    # Inside non-mso blocks, Outlook never sees it, so it's safe (e.g., rounded buttons)
    br_matches = list(re.finditer(r'border-radius\s*:', html, re.IGNORECASE))
    if br_matches:
        # Check if ALL occurrences are inside <!--[if !mso]>...<!--<![endif]--> blocks
        non_mso_blocks = list(re.finditer(
            r'<!--\[if !mso\]><!-->(.*?)<!--<!\[endif\]-->',
            html, re.DOTALL | re.IGNORECASE
        ))
        non_mso_ranges = [(m.start(), m.end()) for m in non_mso_blocks]
        unsafe_br = [
            m for m in br_matches
            if not any(start <= m.start() <= end for start, end in non_mso_ranges)
        ]
        if unsafe_br:
            errors.append(
                f"BORDER_RADIUS: Found {len(unsafe_br)} 'border-radius' outside "
                f"<!--[if !mso]> blocks — Outlook ignores this. Move to non-mso "
                f"block or remove."
            )

    # 4. CSS border used for dividers (renders as black in Outlook)
    # Only flag border on td/tr elements that look like dividers (height=1)
    if re.search(r'border\s*:\s*\d+px\s+solid\s+#(?!000)', html, re.IGNORECASE):
        warnings.append("CSS_BORDER_COLOR: Found colored CSS border — Outlook renders ALL CSS borders as black. Use VML + bgcolor for colored dividers.")

    # 5. margin for spacing
    if re.search(r'margin-top\s*:\s*[1-9]', html, re.IGNORECASE) or \
       re.search(r'margin-bottom\s*:\s*[1-9]', html, re.IGNORECASE):
        warnings.append("MARGIN_SPACING: Found margin-top/bottom — Outlook ignores these. Use spacer rows (<tr><td height='N'>).")

    # 6. float usage
    if re.search(r'float\s*:\s*(left|right)', html, re.IGNORECASE):
        errors.append("FLOAT_LAYOUT: Found 'float' — unreliable in Outlook. Use table cells for side-by-side.")

    # 7. background-image (partial support only)
    if re.search(r'background-image\s*:', html, re.IGNORECASE):
        warnings.append("BG_IMAGE: Found 'background-image' — only partially supported in Outlook. Use VML for background images or solid bgcolor.")

    # 8. div used for layout (check for div with width/display styling)
    div_layout = re.findall(r'<div[^>]*style="[^"]*(?:width|display|float|flex)[^"]*"', html, re.IGNORECASE)
    if div_layout:
        errors.append(f"DIV_LAYOUT: Found {len(div_layout)} <div> elements with layout styles — use <table> for layout in email.")

    # 9. Missing VML namespaces
    if 'xmlns:v=' not in html:
        errors.append("MISSING_VML_NS: Missing VML namespace (xmlns:v=) on <html> tag.")

    # 10. Missing OfficeDocumentSettings
    if 'OfficeDocumentSettings' not in html:
        errors.append("MISSING_OFFICE_SETTINGS: Missing OfficeDocumentSettings XML block.")

    # 11. Missing MSO conditional comments
    if '<!--[if mso]>' not in html:
        warnings.append("MISSING_MSO_CONDITIONAL: No MSO conditional comments found — Outlook-specific fixes may be missing.")

    # 12. Missing color-scheme meta (dark mode prevention)
    if 'color-scheme' not in html:
        warnings.append("MISSING_COLOR_SCHEME: Missing color-scheme meta tag — email may invert colors in dark mode.")

    # 13. External CSS reference
    if re.search(r'<link[^>]*rel="stylesheet"', html, re.IGNORECASE):
        errors.append("EXTERNAL_CSS: Found <link rel='stylesheet'> — Outlook ignores external CSS. Use inline styles.")

    # 14. Images missing width/height attributes
    imgs_missing = re.findall(r'<img(?![^>]*width=)[^>]*>', html, re.IGNORECASE)
    if imgs_missing:
        warnings.append(f"IMG_NO_DIMENSIONS: Found {len(imgs_missing)} <img> without width attribute — Outlook may render images at wrong size.")

    # 15. Missing display:block on images
    imgs_no_block = re.findall(r'<img(?![^>]*display\s*:\s*block)[^>]*>', html, re.IGNORECASE)
    if imgs_no_block:
        warnings.append(f"IMG_NO_BLOCK: Found {len(imgs_no_block)} <img> without display:block — may have bottom gap in Outlook.")

    # 16. Table missing table-layout:fixed
    tables_no_fixed = re.findall(r'<table(?![^>]*table-layout)[^>]*width=(?:"[^%"]+")', html, re.IGNORECASE)
    if tables_no_fixed:
        warnings.append(f"TABLE_NO_FIXED: Found {len(tables_no_fixed)} <table> with pixel width but no table-layout:fixed.")

    # 17. Column pixel widths that may overflow parent table
    # Find tables with pixel width, then check if child td pixel widths + padding exceed it
    for table_match in re.finditer(
        r'<table[^>]*width="(\d+)"[^>]*>(.+?)</table>', html, re.DOTALL | re.IGNORECASE
    ):
        table_width = int(table_match.group(1))
        table_body = table_match.group(2)
        # Find the first row's td widths
        first_row = re.search(r'<tr[^>]*>(.*?)</tr>', table_body, re.DOTALL | re.IGNORECASE)
        if first_row:
            td_widths = re.findall(r'<td[^>]*width="(\d+)"', first_row.group(1), re.IGNORECASE)
            if td_widths:
                total = sum(int(w) for w in td_widths)
                if total > table_width:
                    errors.append(
                        f"COLUMN_OVERFLOW: Table width={table_width}px but columns sum to {total}px "
                        f"({'+'.join(td_widths)}). Use percentage widths or reduce column widths."
                    )
                elif total == table_width:
                    # Exact match means padding WILL cause overflow
                    has_padding = re.search(r'padding\s*:\s*\d+px\s+\d+px', first_row.group(1))
                    if has_padding:
                        warnings.append(
                            f"COLUMN_OVERFLOW_RISK: Table width={table_width}px and columns "
                            f"sum to exactly {total}px — padding will cause overflow. "
                            f"Use percentage widths instead."
                        )

    # 18. Inner tables/elements with pixel widths exceeding container
    # Find the main container width
    container_match = re.search(r'<table[^>]*width="(\d+)"[^>]*align="center"', html, re.IGNORECASE)
    if container_match:
        container_w = int(container_match.group(1))
        # Find any child element with a pixel width larger than container
        oversized = re.findall(
            rf'(?:width="(\d+)"[^>]*style="[^"]*width:\s*(\d+)px)',
            html, re.IGNORECASE
        )
        for attr_w, style_w in oversized:
            w = int(attr_w or style_w)
            if w > container_w:
                errors.append(
                    f"ELEMENT_OVERFLOW: Found element with width={w}px inside "
                    f"{container_w}px container. Reduce width or use percentage."
                )
                break  # Report once

    # 19. Text elements missing word-wrap protection (16px+ font sizes)
    text_no_wrap = re.findall(
        r'<(?:h[1-6]|p|td)[^>]*style="(?![^"]*(?:word-wrap|overflow-wrap))[^"]*font-size:\s*(?:1[6-9]|[2-9]\d)\s*px[^"]*"[^>]*>[^<]{10,}',
        html, re.IGNORECASE
    )
    if text_no_wrap:
        warnings.append(
            f"TEXT_NO_WRAP: Found {len(text_no_wrap)} large-font text elements without "
            f"word-wrap:break-word — long text may overflow container."
        )

    # 20. HTML size exceeding Gmail clip threshold (102KB)
    html_size_kb = len(html.encode('utf-8')) / 1024
    if html_size_kb > 102:
        errors.append(
            f"HTML_TOO_LARGE: HTML is {html_size_kb:.0f}KB — Gmail clips emails larger than "
            f"102KB. Reduce content or split into multiple emails."
        )
    elif html_size_kb > 80:
        warnings.append(
            f"HTML_NEAR_LIMIT: HTML is {html_size_kb:.0f}KB — approaching Gmail's 102KB clip "
            f"threshold. Consider reducing content."
        )

    # 21. Images missing alt attribute (accessibility + image-off fallback)
    imgs_no_alt = re.findall(r'<img(?![^>]*alt=)[^>]*>', html, re.IGNORECASE)
    if imgs_no_alt:
        warnings.append(
            f"IMG_NO_ALT: Found {len(imgs_no_alt)} <img> without alt attribute — "
            f"hurts accessibility and shows nothing when images are blocked."
        )

    # 22. Non-HTTPS links (Outlook warns about http:// links)
    http_links = re.findall(r'href="http://(?!localhost)', html, re.IGNORECASE)
    if http_links:
        warnings.append(
            f"HTTP_LINKS: Found {len(http_links)} http:// link(s) — use https:// instead. "
            f"Outlook and Gmail may show security warnings for non-HTTPS links."
        )

    # 23. Missing preheader text (inbox preview line)
    has_preheader = bool(re.search(
        r'(?:preheader|preview[-_]?text|display\s*:\s*none[^>]*>[^<]{10,})',
        html, re.IGNORECASE
    ))
    if not has_preheader:
        warnings.append(
            "NO_PREHEADER: No preheader/preview text found. Add a hidden preheader after "
            "<body> for better inbox preview: <div style='display:none;'>Preview text</div>"
        )

    # 24. HTML lists (<ul>/<ol>) — Outlook renders with unpredictable spacing
    html_lists = re.findall(r'<(?:ul|ol)[^>]*>', html, re.IGNORECASE)
    if html_lists:
        warnings.append(
            f"HTML_LISTS: Found {len(html_lists)} <ul>/<ol> list(s) — Outlook renders list "
            f"indent and spacing inconsistently. Use table rows with manual bullet characters "
            f"instead (e.g., a <td> with '•' or numbered text)."
        )

    # 25. @font-face / web fonts (completely ignored in Outlook)
    if re.search(r'@font-face', html, re.IGNORECASE):
        warnings.append(
            "WEB_FONTS: Found @font-face — Outlook ignores custom/web fonts entirely. "
            "Only system fonts work. Ensure the font-family stack has adequate fallbacks."
        )

    # 26. Animated GIF (Outlook shows only the first frame)
    gif_refs = re.findall(r'\.gif["\']', html, re.IGNORECASE)
    if gif_refs:
        warnings.append(
            f"ANIMATED_GIF: Found {len(gif_refs)} .gif reference(s) — Outlook displays only "
            f"the first frame. Ensure the first frame conveys the message on its own."
        )

    # 27. Table nesting depth (>8 levels can crash Outlook)
    max_depth = 0
    depth = 0
    for match in re.finditer(r'<(/?)table[\s>]', html, re.IGNORECASE):
        if match.group(1) == '':
            depth += 1
            max_depth = max(max_depth, depth)
        else:
            depth = max(0, depth - 1)
    if max_depth > 8:
        errors.append(
            f"TABLE_NESTING: Tables nested {max_depth} levels deep — Outlook may crash or "
            f"fail to render beyond ~8 levels. Simplify the layout."
        )
    elif max_depth > 6:
        warnings.append(
            f"TABLE_NESTING: Tables nested {max_depth} levels deep — keep under 8 for "
            f"Outlook safety."
        )

    # 28. CSS position (absolute/relative/fixed — all ignored in Outlook)
    if re.search(r'position\s*:\s*(?:absolute|relative|fixed)', html, re.IGNORECASE):
        errors.append(
            "CSS_POSITION: Found position:absolute/relative/fixed — Outlook ignores CSS "
            "positioning entirely. Use table cell alignment instead."
        )

    # 29. <video>/<audio> tags (not supported in any email client except Apple Mail)
    media_tags = re.findall(r'<(?:video|audio)[^>]*>', html, re.IGNORECASE)
    if media_tags:
        errors.append(
            f"MEDIA_TAGS: Found {len(media_tags)} <video>/<audio> tag(s) — not supported in "
            f"Outlook, Gmail, or most email clients. Use a static image with a play button "
            f"linking to the video URL instead."
        )

    # 30. Layout tables missing role="presentation"
    layout_tables = re.findall(
        r'<table(?![^>]*role=)[^>]*(?:cellpadding|cellspacing)[^>]*>',
        html, re.IGNORECASE
    )
    if layout_tables:
        warnings.append(
            f"TABLE_NO_ROLE: Found {len(layout_tables)} layout <table> without "
            f"role=\"presentation\" — screen readers will announce table structure. "
            f"Add role=\"presentation\" to layout tables."
        )

    # 31. Missing lang attribute on <html>
    if not re.search(r'<html[^>]*\slang="[a-z]{2}', html, re.IGNORECASE):
        warnings.append(
            "MISSING_LANG: <html> tag is missing lang attribute — screen readers "
            "need this to use correct pronunciation. Add lang=\"en\" or lang=\"zh\"."
        )

    passed = len(errors) == 0
    return {"passed": passed, "errors": errors, "warnings": warnings}


def validate_file(html_path: str) -> dict:
    """Validate an HTML file. Prints results and returns dict."""
    html = Path(html_path).read_text(encoding="utf-8")
    result = validate(html)

    if result["passed"] and not result["warnings"]:
        print(f"✓ PASSED — No Outlook compatibility issues found.")
    else:
        if result["errors"]:
            print(f"✗ FAILED — {len(result['errors'])} error(s):")
            for e in result["errors"]:
                print(f"  ERROR: {e}")
        if result["warnings"]:
            print(f"  {len(result['warnings'])} warning(s):")
            for w in result["warnings"]:
                print(f"  WARN:  {w}")
        if not result["errors"]:
            print(f"✓ PASSED (with warnings)")

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        validate_file(sys.argv[1])
    else:
        print("Usage: python html-validator.py <path-to-html>")
