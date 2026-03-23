#!/usr/bin/env python3
"""
html-to-eml.py — Convert an HTML newsletter into a draft .eml file.

Produces a standards-compliant MIME message with embedded images that
opens as an editable draft in Outlook (Classic) and Thunderbird.

Image handling:
    HTML uses relative paths: src="images/logo.png"
    This script automatically converts them to CID references and embeds
    the image files as MIME parts during EML generation.

MIME structure:
    multipart/alternative
    +-- text/plain              (fallback for text-only clients)
    +-- multipart/related
        +-- text/html           (the newsletter, with cid: references)
        +-- image/...           (embedded images)

Python stdlib only — no third-party dependencies.
"""

import hashlib
import mimetypes
import os
import re
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG — edit these values before running
# ---------------------------------------------------------------------------
HTML_FILE = "output/newsletter.html"   # Path to the source HTML file
OUTPUT_EML = "output/newsletter.eml"   # Where to write the resulting .eml
SUBJECT = "Newsletter Title"           # Email subject line
SENDER = ""                            # From address (optional, can be empty)
TO_ADDRS = []                          # List of recipient addresses (optional)
IMAGE_DIR = "output/images"            # Directory containing CID images


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def html_to_text(html: str) -> str:
    """Strip HTML tags and decode common entities to produce a plain-text
    fallback.  This is intentionally simple — no external dependency needed."""
    # Remove all HTML tags
    text = re.sub(r"<[^>]+>", "", html)
    # Decode the most common HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")  # &amp; last so we don't double-decode
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    # Collapse runs of whitespace into a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def attach_image(msg: MIMEMultipart, cid: str, path: str) -> None:
    """Attach an image to *msg* with the given Content-ID.

    Headers are set for maximum compatibility across mail clients:

    * Content-ID: <cid>
        Standard RFC 2392 identifier.  The angle brackets are required by the
        spec; HTML references the image as ``src="cid:name"``.

    * X-Attachment-Id: cid
        Non-standard header used by Outlook and Gmail to correlate CID
        references when Content-ID alone is not honoured.

    * Content-Disposition: inline; filename="..."
        Tells the client to render the image inline rather than offering it
        as a downloadable attachment.  The filename is forced to ASCII to
        avoid encoding issues in older Outlook builds.
    """
    filepath = Path(path)
    mime_type = mimetypes.guess_type(str(filepath))[0] or "application/octet-stream"

    with open(filepath, "rb") as fp:
        image_data = fp.read()

    if mime_type.startswith("image/"):
        subtype = mime_type.split("/", 1)[1]
        img = MIMEImage(image_data, _subtype=subtype)
    else:
        maintype, subtype = mime_type.split("/", 1)
        img = MIMEBase(maintype, subtype)
        img.set_payload(image_data)
        encoders.encode_base64(img)

    # Content-ID — angle brackets are mandatory per RFC 2392
    img.add_header("Content-ID", f"<{cid}>")

    # X-Attachment-Id — Outlook / Gmail use this to match CID references
    img.add_header("X-Attachment-Id", cid)

    # Content-Disposition: inline — display in body, not as a download
    # Force an ASCII-safe filename to avoid mojibake in older Outlook
    safe_filename = (
        filepath.name.encode("ascii", "ignore").decode("ascii")
        or f"{cid}.png"
    )
    img.add_header("Content-Disposition", "inline", filename=safe_filename)

    msg.attach(img)



def replace_images_with_cid(html: str, image_dir: str) -> tuple:
    """Parse HTML for <img src="images/..."> references, replace with CID,
    and return (converted_html, {cid: filepath}).

    CID generation:
    - ASCII filenames: stem is the CID (e.g., images/logo.png -> cid:logo)
    - Non-ASCII filenames: img_{md5[:16]} (e.g., images/产品.png -> cid:img_abc123)

    Raises FileNotFoundError if any referenced image is missing.
    """
    img_dir = Path(image_dir)
    cid_map = {}
    missing = []

    pattern = re.compile(r"""(<img[^>]*\bsrc=["'])images/([^"']+)(["'])""", re.IGNORECASE)

    def _replace(match):
        prefix, filename, suffix = match.group(1), match.group(2), match.group(3)
        filepath = img_dir / filename

        if not filepath.exists():
            missing.append((f"images/{filename}", str(filepath)))
            return match.group(0)

        stem = Path(filename).stem
        try:
            stem.encode("ascii")
            cid = stem
        except UnicodeEncodeError:
            cid = f"img_{hashlib.md5(filename.encode('utf-8')).hexdigest()[:16]}"

        cid_map[cid] = str(filepath.resolve())
        return f'{prefix}cid:{cid}{suffix}'

    converted = pattern.sub(_replace, html)

    if missing:
        msg_lines = ["Referenced images not found:"]
        for src, path in missing:
            msg_lines.append(f"  - {src} (expected at {path})")
        raise FileNotFoundError("\n".join(msg_lines))

    return converted, cid_map


def convert() -> None:
    """Read the HTML file, build a multipart MIME message with embedded
    images, and write the result as an ``.eml`` file.

    MIME structure produced::

        multipart/alternative
        +-- text/plain
        +-- multipart/related
            +-- text/html
            +-- image/… (one per CID image)
    """
    html_path = Path(HTML_FILE)
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {HTML_FILE}")

    html_content = html_path.read_text(encoding="utf-8")

    # -- Root container: multipart/alternative ---------------------------------
    # RFC 2046 §5.1.4 — the client picks the *last* alternative it can render,
    # so text/plain comes first (lowest fidelity) and the related block last.
    msg = MIMEMultipart("alternative")

    msg["Subject"] = SUBJECT

    if SENDER:
        msg["From"] = SENDER

    if TO_ADDRS:
        # Semicolon separator is the Outlook convention for multiple recipients
        msg["To"] = "; ".join(TO_ADDRS)

    # X-Unsent: 1 — tells Outlook (Classic) and Thunderbird to open the
    # message in compose/draft mode so the user can review and send manually.
    # Note: *not* supported by Outlook for Mac or "New Outlook".
    msg["X-Unsent"] = "1"

    # -- text/plain alternative ------------------------------------------------
    plain_text = html_to_text(html_content)
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))

    # -- multipart/related (HTML + images) -------------------------------------
    converted_html, cid_map = replace_images_with_cid(html_content, IMAGE_DIR)

    if cid_map:
        msg_related = MIMEMultipart("related")
        msg_related.attach(MIMEText(converted_html, "html", "utf-8"))

        for cid, img_path in cid_map.items():
            attach_image(msg_related, cid, img_path)
            print(f"  Embedded image: cid:{cid} <- {Path(img_path).name}")

        msg.attach(msg_related)
    else:
        msg.attach(MIMEText(html_content, "html", "utf-8"))

    # -- Write .eml ------------------------------------------------------------
    output_path = Path(OUTPUT_EML)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(msg.as_string(), encoding="utf-8")

    print(f"  EML saved to: {OUTPUT_EML}")
    print(f"  Images embedded: {len(cid_map)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    convert()
