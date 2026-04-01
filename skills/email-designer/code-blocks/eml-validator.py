"""
EML Validator — Check Generated EML File Integrity
====================================================
Scans a generated .eml file for structural and CID embedding issues.
Agent should run this AFTER generating EML and BEFORE proceeding to Step 6.

Usage by Agent:
    1. Generate EML (using eml-builder.py or html-to-eml.py)
    2. Run validate_eml(eml_path) to check for issues
    3. Fix any errors found
    4. Then proceed to Step 6

Dependencies: Python stdlib only (email, re, pathlib)
"""

import re
from email import policy
from email.parser import BytesParser
from pathlib import Path


def validate_eml(eml_path: str) -> dict:
    """
    Validate an EML file for structural integrity and CID embedding correctness.

    Checks adapt to the email content: image-related checks only fire when
    the HTML actually references CID images or contains unresolved image paths.
    Pure-text emails (no images) will pass without false positives.

    Returns dict with 'passed' (bool), 'errors' (list), 'warnings' (list).
    """
    errors = []
    warnings = []

    path = Path(eml_path)
    if not path.exists():
        return {"passed": False, "errors": [f"EML file not found: {eml_path}"], "warnings": []}

    # Parse the EML file
    with open(path, "rb") as fp:
        msg = BytesParser(policy=policy.default).parse(fp)

    # ── 1. MIME root structure ───────────────────────────────────────────
    root_type = msg.get_content_type()
    if root_type != "multipart/alternative":
        errors.append(
            f"MIME_ROOT: Root content type is '{root_type}' — expected "
            f"'multipart/alternative'. Outlook needs alternative with "
            f"text/plain + HTML."
        )

    # ── 2. text/plain exists ─────────────────────────────────────────────
    plain_parts = _find_parts(msg, "text/plain")
    if not plain_parts:
        errors.append(
            "NO_PLAIN_TEXT: Missing text/plain part — email clients that "
            "cannot render HTML will show nothing."
        )

    # ── 3. text/html exists ──────────────────────────────────────────────
    html_parts = _find_parts(msg, "text/html")
    if not html_parts:
        errors.append(
            "NO_HTML: Missing text/html part — the email has no HTML body."
        )

    # ── 12. X-Unsent header ─────────────────────────────────────────────
    if msg.get("X-Unsent") != "1":
        errors.append(
            "NO_X_UNSENT: Missing or incorrect 'X-Unsent: 1' header — "
            "Outlook will not open this as a draft/compose window."
        )

    # ── 13. Subject not empty ────────────────────────────────────────────
    subject = msg.get("Subject", "")
    if not subject or not subject.strip():
        errors.append(
            "EMPTY_SUBJECT: Email subject is empty — most email clients "
            "will show '(no subject)'."
        )

    # If no HTML part, skip all image-related checks
    if not html_parts:
        passed = len(errors) == 0
        return {"passed": passed, "errors": errors, "warnings": warnings}

    # Extract HTML content for analysis
    html_content = html_parts[0].get_content()

    # Detect CID references in HTML: src="cid:xxx"
    cid_refs_in_html = set(re.findall(r'src=["\']cid:([^"\']+)["\']', html_content, re.IGNORECASE))

    # Detect unresolved local image paths — any src that is NOT cid:, http(s)://, or data:
    # These are local relative paths that won't render in an email client.
    residual_paths = re.findall(
        r'src=["\'](?!cid:|https?://|data:)([^"\']+\.(png|jpe?g|gif|svg|webp|bmp))["\']',
        html_content, re.IGNORECASE
    )
    residual_paths = [match[0] for match in residual_paths]  # extract full path from groups

    # Collect all embedded image parts and their CIDs
    image_parts = _find_image_parts(msg)
    embedded_cids = set()
    for part_info in image_parts:
        embedded_cids.add(part_info["cid"])

    # Determine if this email is supposed to have images
    has_image_intent = bool(cid_refs_in_html) or bool(residual_paths)

    # ── 8. Residual path check ───────────────────────────────────────────
    if residual_paths:
        errors.append(
            f"RESIDUAL_IMAGE_PATH: Found {len(residual_paths)} unresolved "
            f"local image path(s) in HTML: "
            f"{', '.join(residual_paths[:5])}. "
            f"All image src must use 'cid:' references in EML — local "
            f"relative paths will NOT display in email clients."
        )

    # ── 4. multipart/related structure (only when images expected) ───────
    if has_image_intent:
        related_parts = _find_parts(msg, "multipart/related")
        if not related_parts:
            errors.append(
                "NO_RELATED: HTML references CID images but no "
                "'multipart/related' container found — images are not "
                "properly embedded in the MIME structure."
            )
        else:
            # ── 5. HTML position in related (RFC 2387) ───────────────────
            related = related_parts[0]
            children = list(related.iter_parts())
            if children:
                first_child = children[0]
                if first_child.get_content_type() != "text/html":
                    errors.append(
                        f"HTML_NOT_FIRST: In multipart/related, the first "
                        f"child is '{first_child.get_content_type()}' — "
                        f"RFC 2387 requires text/html to be the first part "
                        f"so clients know it is the root document."
                    )

    # ── 6. CID forward completeness ──────────────────────────────────────
    missing_cids = cid_refs_in_html - embedded_cids
    if missing_cids:
        errors.append(
            f"CID_MISSING: HTML references {len(missing_cids)} CID(s) not "
            f"found as embedded MIME parts: {', '.join(sorted(missing_cids))}. "
            f"These images will show as broken in the email client."
        )

    # ── 7. CID reverse completeness ──────────────────────────────────────
    unused_cids = embedded_cids - cid_refs_in_html
    if unused_cids:
        warnings.append(
            f"CID_UNUSED: {len(unused_cids)} embedded image(s) not "
            f"referenced in HTML: {', '.join(sorted(unused_cids))}. "
            f"These waste email size and may show as attachments."
        )

    # ── 9-11. Per-image-part checks ──────────────────────────────────────
    for part_info in image_parts:
        cid = part_info["cid"]
        raw_content_id = part_info["raw_content_id"]
        disposition = part_info["disposition"]
        x_attachment_id = part_info["x_attachment_id"]

        # ── 9. Content-ID format (RFC 2392: must have angle brackets) ────
        if raw_content_id and not (raw_content_id.startswith("<") and raw_content_id.endswith(">")):
            errors.append(
                f"CID_FORMAT: Image '{cid}' has Content-ID '{raw_content_id}' "
                f"— RFC 2392 requires angle brackets: '<{cid}>'. Some "
                f"clients will fail to match the CID reference."
            )

        # ── 10. X-Attachment-Id ──────────────────────────────────────────
        if not x_attachment_id:
            warnings.append(
                f"NO_X_ATTACHMENT_ID: Image '{cid}' is missing "
                f"'X-Attachment-Id' header — Outlook and Gmail use this "
                f"to correlate CID references."
            )

        # ── 11. Content-Disposition ──────────────────────────────────────
        if disposition and not disposition.lower().startswith("inline"):
            warnings.append(
                f"NOT_INLINE: Image '{cid}' has Content-Disposition "
                f"'{disposition}' — should be 'inline' to display within "
                f"the email body instead of as a downloadable attachment."
            )

    # ── 14. File size check ──────────────────────────────────────────────
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > 10:
        warnings.append(
            f"LARGE_EML: EML file is {file_size_mb:.1f}MB — some email "
            f"clients or servers reject messages over 10MB. Consider "
            f"compressing images."
        )

    passed = len(errors) == 0
    return {"passed": passed, "errors": errors, "warnings": warnings}


# ── Helpers ──────────────────────────────────────────────────────────────


def _find_parts(msg, content_type: str) -> list:
    """Find all MIME parts matching the given content type."""
    parts = []
    if msg.get_content_type() == content_type:
        parts.append(msg)
    if msg.is_multipart():
        for part in msg.iter_parts():
            parts.extend(_find_parts(part, content_type))
    return parts


def _find_image_parts(msg) -> list:
    """Find all image MIME parts and extract their CID metadata."""
    parts = []
    for part in msg.walk():
        if part.get_content_maintype() == "image":
            raw_cid = part.get("Content-ID", "")
            cid = raw_cid.strip("<>") if raw_cid else ""
            parts.append({
                "cid": cid,
                "raw_content_id": raw_cid,
                "disposition": part.get("Content-Disposition", ""),
                "x_attachment_id": part.get("X-Attachment-Id", ""),
                "content_type": part.get_content_type(),
            })
    return parts


# ── CLI entry point ──────────────────────────────────────────────────────


def validate_file(eml_path: str) -> dict:
    """Validate an EML file. Prints results and returns dict."""
    result = validate_eml(eml_path)

    if result["passed"] and not result["warnings"]:
        print(f"✓ PASSED — No EML integrity issues found.")
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
        print("Usage: python eml-validator.py <path-to-eml>")
