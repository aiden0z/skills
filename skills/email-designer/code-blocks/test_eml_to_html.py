"""Tests for EML to HTML extractor."""

import os
import sys
import tempfile
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

sys.path.insert(0, os.path.dirname(__file__))


def _import():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "eml_to_html",
        os.path.join(os.path.dirname(__file__), "eml-to-html.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _create_test_eml(tmpdir, html_content, subject="Test Email", images=None):
    """Create a test EML file with optional embedded images."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "sender@example.com"
    msg["To"] = "receiver@example.com"

    # Plain text part
    msg.attach(MIMEText("Plain text fallback", "plain", "utf-8"))

    if images:
        # multipart/related for HTML + images
        related = MIMEMultipart("related")
        related.attach(MIMEText(html_content, "html", "utf-8"))
        for cid, img_bytes in images.items():
            img_part = MIMEImage(img_bytes, "png")
            img_part.add_header("Content-ID", f"<{cid}>")
            img_part.add_header("Content-Disposition", "inline", filename=f"{cid}.png")
            related.attach(img_part)
        msg.attach(related)
    else:
        msg.attach(MIMEText(html_content, "html", "utf-8"))

    eml_path = os.path.join(tmpdir, "test.eml")
    with open(eml_path, "w") as f:
        f.write(msg.as_string())
    return eml_path


def test_extract_html_basic():
    """Test extracting HTML from a simple EML file."""
    mod = _import()
    html = "<html><body><h1>Hello</h1></body></html>"

    with tempfile.TemporaryDirectory() as tmpdir:
        eml_path = _create_test_eml(tmpdir, html, "Test Subject")
        result = mod.extract_from_eml(eml_path)

        assert result["subject"] == "Test Subject"
        assert result["from"] == "sender@example.com"
        assert "<h1>Hello</h1>" in result["html"]
        assert result["images"] == {}


def test_extract_html_with_images():
    """Test extracting HTML + embedded CID images."""
    mod = _import()
    html = '<html><body><img src="cid:logo"></body></html>'
    # 1x1 red PNG
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
        b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
        b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        eml_path = _create_test_eml(tmpdir, html, images={"logo": png_bytes})
        result = mod.extract_from_eml(eml_path)

        assert "<img" in result["html"]
        assert "logo" in result["images"]
        assert isinstance(result["images"]["logo"], bytes)


def test_save_extracted():
    """Test saving extracted HTML and images to a directory."""
    mod = _import()
    html = '<html><body><img src="cid:banner"><p>Content</p></body></html>'
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
        b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
        b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        eml_path = _create_test_eml(tmpdir, html, images={"banner": png_bytes})
        output_dir = os.path.join(tmpdir, "output")

        result = mod.extract_from_eml(eml_path)
        saved = mod.save_extracted(result, output_dir)

        assert os.path.exists(saved["html_path"])
        assert os.path.exists(os.path.join(output_dir, "images", "banner.png"))

        # Check CID references were converted to relative paths
        saved_html = Path(saved["html_path"]).read_text(encoding="utf-8")
        assert 'src="images/banner.png"' in saved_html
        assert "cid:" not in saved_html


def test_extract_plain_text_only():
    """Test handling EML with no HTML part."""
    mod = _import()

    msg = MIMEText("Just plain text", "plain", "utf-8")
    msg["Subject"] = "Plain Only"
    msg["From"] = "a@b.com"

    with tempfile.TemporaryDirectory() as tmpdir:
        eml_path = os.path.join(tmpdir, "plain.eml")
        with open(eml_path, "w") as f:
            f.write(msg.as_string())

        result = mod.extract_from_eml(eml_path)
        assert result["html"] is None
        assert result["plain_text"] == "Just plain text"


if __name__ == "__main__":
    test_extract_html_basic()
    print("PASS: test_extract_html_basic")
    test_extract_html_with_images()
    print("PASS: test_extract_html_with_images")
    test_save_extracted()
    print("PASS: test_save_extracted")
    test_extract_plain_text_only()
    print("PASS: test_extract_plain_text_only")
    print("\nAll tests passed!")
