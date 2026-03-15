"""
Template Manager — Save and Reuse Custom Templates
===================================================
Saves user-confirmed templates for future reuse.
Templates stored as JSON metadata + HTML file pairs in saved-templates/.

Usage by Agent:
    - After user confirms a template, save it for future sessions
    - At Step 1, check saved-templates/ and offer reuse

Dependencies: Python stdlib only
"""

import json
from datetime import datetime
from pathlib import Path

# Save templates in user's working directory, NOT the skill installation directory
TEMPLATES_DIR = Path.cwd() / "saved-templates"


def save_template(name: str, html_path: str, metadata: dict) -> str:
    """
    Save a confirmed template for future reuse.

    Args:
        name: Template name (user-provided or auto-generated)
        html_path: Path to the HTML template file
        metadata: Dict with keys: width, colors, layout_type, description

    Returns:
        Path to saved template directory
    """
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = name.lower().replace(" ", "-")
    template_dir = TEMPLATES_DIR / safe_name
    template_dir.mkdir(parents=True, exist_ok=True)

    # Copy HTML
    html_content = Path(html_path).read_text(encoding="utf-8")
    (template_dir / "template.html").write_text(html_content, encoding="utf-8")

    # Save metadata
    metadata["name"] = name
    metadata["created"] = datetime.now().isoformat()
    (template_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Template saved: {template_dir}")
    return str(template_dir)


def list_templates() -> list:
    """List all saved templates with metadata."""
    if not TEMPLATES_DIR.exists():
        return []
    templates = []
    for d in sorted(TEMPLATES_DIR.iterdir()):
        meta_file = d / "metadata.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            meta["path"] = str(d)
            templates.append(meta)
    return templates


def load_template(name: str) -> tuple:
    """Load a saved template. Returns (html_content, metadata)."""
    safe_name = name.lower().replace(" ", "-")
    template_dir = TEMPLATES_DIR / safe_name
    html = (template_dir / "template.html").read_text(encoding="utf-8")
    meta = json.loads((template_dir / "metadata.json").read_text(encoding="utf-8"))
    return html, meta


def delete_template(name: str) -> bool:
    """Delete a saved template. Returns True if deleted."""
    import shutil
    safe_name = name.lower().replace(" ", "-")
    template_dir = TEMPLATES_DIR / safe_name
    if template_dir.exists():
        shutil.rmtree(template_dir)
        print(f"Template deleted: {safe_name}")
        return True
    return False
