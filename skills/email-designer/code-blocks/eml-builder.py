"""
EML Builder -- generate RFC 822 .eml drafts with CID-embedded images.

Usage (AI Agent):
    1. Instantiate EMLBuilder with sender / subject.
    2. Chain .set_html(), .add_to(), .add_image() etc.
    3. Call .build("out.eml") to write the file, or .build() for a string.

Example:
    eml = (
        EMLBuilder("team@example.com", "Weekly Report")
        .set_html(html_string)
        .add_to("alice@example.com", "bob@example.com")
        .add_image("logo", "assets/logo.png")
        .build("report.eml")
    )

Only stdlib is used: email.mime.*, mimetypes, pathlib, re.
"""

import mimetypes
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional


class EMLBuilder:
    """Fluent builder that produces Outlook-compatible .eml draft files."""

    def __init__(self, sender: str = "", subject: str = "") -> None:
        self._sender = sender
        self._subject = subject
        self._to: List[str] = []
        self._cc: List[str] = []
        self._bcc: List[str] = []
        self._html = ""
        self._images: dict = {}  # {cid: (path, mime_type)}

    # -- fluent setters ------------------------------------------------

    def set_sender(self, sender: str) -> "EMLBuilder":
        self._sender = sender
        return self

    def set_subject(self, subject: str) -> "EMLBuilder":
        self._subject = subject
        return self

    def set_html(self, html: str) -> "EMLBuilder":
        self._html = html
        return self

    def add_to(self, *addrs: str) -> "EMLBuilder":
        self._to.extend(addrs)
        return self

    def add_cc(self, *addrs: str) -> "EMLBuilder":
        self._cc.extend(addrs)
        return self

    def add_bcc(self, *addrs: str) -> "EMLBuilder":
        self._bcc.extend(addrs)
        return self

    def add_image(self, cid: str, path: str) -> "EMLBuilder":
        """Register an inline image. Reference it in HTML as src="cid:<cid>"."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        self._images[cid] = (path, mime)
        return self

    # -- build ---------------------------------------------------------

    def build(self, output_file: Optional[str] = None) -> str:
        """Assemble the MIME tree and optionally write to *output_file*."""
        # Root is multipart/alternative so clients can pick plain or HTML.
        msg = MIMEMultipart("alternative")
        msg["Subject"] = self._subject
        msg["From"] = self._sender
        # X-Unsent: 1 tells Outlook/Thunderbird to open in compose mode
        # (draft). Not supported by Outlook for Mac or New Outlook.
        msg["X-Unsent"] = "1"
        if self._to:
            msg["To"] = "; ".join(self._to)
        if self._cc:
            msg["Cc"] = "; ".join(self._cc)
        if self._bcc:
            msg["Bcc"] = "; ".join(self._bcc)

        # Plain-text fallback for clients that cannot render HTML.
        msg.attach(MIMEText(_html_to_text(self._html), "plain", "utf-8"))

        if self._images:
            # multipart/related groups the HTML root document with its
            # inline resources (images).  RFC 2387 requires the HTML part
            # to be the *first* child so clients know it is the root.
            related = MIMEMultipart("related")
            related.attach(MIMEText(self._html, "html", "utf-8"))
            for cid, (path, mime) in self._images.items():
                related.attach(_make_inline_image(cid, path, mime))
            msg.attach(related)
        else:
            msg.attach(MIMEText(self._html, "html", "utf-8"))

        eml = msg.as_string()
        if output_file:
            out = Path(output_file)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(eml, encoding="utf-8")
        return eml


# -- helpers (module-private) ------------------------------------------

def _make_inline_image(cid: str, path: str, mime: str) -> MIMEBase:
    """Create a MIME part for a CID-embedded inline image."""
    data = Path(path).read_bytes()
    maintype, subtype = mime.split("/", 1)
    if maintype == "image":
        part = MIMEImage(data, _subtype=subtype)
    else:
        part = MIMEBase(maintype, subtype)
        part.set_payload(data)
        encoders.encode_base64(part)
    # Content-ID in angle brackets per RFC 2392; HTML references as
    # src="cid:name" (without brackets).
    part.add_header("Content-ID", f"<{cid}>")
    # X-Attachment-Id lets Outlook and Gmail associate the CID reference
    # with this attachment -- without it images may show as broken.
    part.add_header("X-Attachment-Id", cid)
    # Content-Disposition: inline tells the client to render the image
    # within the message body rather than as a downloadable attachment.
    # Use an ASCII-safe filename to avoid encoding issues in headers.
    name = Path(path).name
    safe = name.encode("ascii", "ignore").decode("ascii") or f"{cid}.png"
    part.add_header("Content-Disposition", "inline", filename=safe)
    return part


def _html_to_text(html: str) -> str:
    """Naive HTML-to-plain-text for the text/plain fallback."""
    text = re.sub(r"<[^>]+>", "", html)
    for entity, ch in (("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")):
        text = text.replace(entity, ch)
    return re.sub(r"\s+", " ", text).strip()
