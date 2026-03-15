"""
Output Manager — Organized Output Directories
==============================================
Creates timestamped, project-named output directories instead of
dumping all files into a flat output/ folder.

Usage by Agent:
    1. At the start of generation, call create_project() to get a clean directory
    2. Save all files (HTML, EML, images) into that directory
    3. At the end, call list_projects() to show the user their history

Directory structure:
    output/
      2026-03-15_product-monthly-report/
        newsletter-preview.html
        newsletter.eml
        images/
      2026-03-15_weekly-digest/
        newsletter-preview.html
        newsletter.eml

Dependencies: Python stdlib only
"""

import json
from datetime import datetime
from pathlib import Path

# Output to the user's current working directory, NOT the skill installation directory
OUTPUT_ROOT = Path.cwd() / "output"


def create_project(name: str) -> str:
    """
    Create a new output project directory.

    Args:
        name: descriptive name (e.g., "product-monthly-report")
              will be sanitized for filesystem safety

    Returns:
        Absolute path to the created directory
    """
    safe_name = name.lower().strip()
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in safe_name)
    safe_name = safe_name.replace(" ", "-")

    date_prefix = datetime.now().strftime("%Y-%m-%d")
    dir_name = f"{date_prefix}_{safe_name}"

    project_dir = OUTPUT_ROOT / dir_name
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "images").mkdir(exist_ok=True)

    # Save project metadata
    meta = {
        "name": name,
        "created": datetime.now().isoformat(),
        "date": date_prefix,
    }
    (project_dir / "project.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Project created: {project_dir}")
    return str(project_dir)


def list_projects() -> list:
    """
    List all output projects, newest first.
    Returns list of dicts with name, path, created date, files.
    """
    if not OUTPUT_ROOT.exists():
        return []

    projects = []
    for d in sorted(OUTPUT_ROOT.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        meta_file = d / "project.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            meta["path"] = str(d)
            meta["files"] = [f.name for f in d.iterdir() if f.is_file() and f.name != "project.json"]
            projects.append(meta)
        else:
            # Legacy directory without metadata
            projects.append({
                "name": d.name,
                "path": str(d),
                "created": None,
                "files": [f.name for f in d.iterdir() if f.is_file()]
            })

    return projects


def get_project_path(name: str) -> str:
    """Get the most recent project directory matching a name."""
    projects = list_projects()
    for p in projects:
        if name.lower() in p["name"].lower():
            return p["path"]
    return None


def cleanup_old(keep_last: int = 10) -> int:
    """Remove old project directories, keeping the N most recent."""
    import shutil
    projects = list_projects()
    if len(projects) <= keep_last:
        return 0

    removed = 0
    for p in projects[keep_last:]:
        shutil.rmtree(p["path"])
        removed += 1
        print(f"Removed: {p['path']}")

    return removed
