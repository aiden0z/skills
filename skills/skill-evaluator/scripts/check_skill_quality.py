#!/usr/bin/env python3
"""Mechanical and semantic quality checks for Agent Skill folders."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


BAD_AUXILIARY_FILES = {
    "CHANGELOG.md",
    "INSTALLATION.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "README.md",
    "README_CN.md",
    "README.zh-CN.md",
}
PLACEHOLDER_RE = re.compile(r"\[TODO:|^\s*(TODO|TBD|FIXME|xxx)\b|<\s*(TODO|TBD|FIXME|xxx)\s*>", re.IGNORECASE)
FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
WORKFLOW_WORDS = re.compile(
    r"\b(step|workflow|first|then|finally|run|create|write|validate|dispatch|generate)\b",
    re.IGNORECASE,
)
# Deep semantic checks — warn only, these are heuristics not blockers
BLOCKING_GATE_RE = re.compile(r"⛔\s*BLOCKING|BLOCKING\s*(GATE|STEP|CHECK)", re.IGNORECASE)
ANTI_SHORTCUT_RE = re.compile(r"(must\s*not|never|forbidden|do\s*not\s*use|anti.pattern|no\s+bulk)", re.IGNORECASE)
VALIDATOR_MENTION_RE = re.compile(r"(validate|validator|validation|check.*script|run.*\.py)", re.IGNORECASE)
EVIDENCE_CONTRACT_RE = re.compile(r"(evidence.*(ledger|path|artifact|trace)|must\s*produce|must\s*leave|must\s*create)", re.IGNORECASE)
VAGUE_GATE_RE = re.compile(r"^\s*(?:should\s+ensure\b|be\s+thorough\b|ensure\s+quality\b)", re.IGNORECASE | re.MULTILINE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_simple_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data: dict[str, str] = {}
    for raw_line in match.group("body").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def has_contents_section(text: str) -> bool:
    return bool(re.search(r"^##?\s+(Contents|Table of Contents|目录)\s*$", text, flags=re.MULTILINE | re.IGNORECASE))


def has_unfinished_marker(text: str) -> bool:
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if PLACEHOLDER_RE.search(line):
            return True
    return False


def run_py_compile(script: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return result.returncode == 0, result.stdout.strip()


def check_semantic_gates(text: str, script_names: set[str]) -> list[str]:
    """Check for blocking gates, anti-shortcut rules, evidence contracts, and vague-gate anti-patterns."""
    warnings: list[str] = []
    if not BLOCKING_GATE_RE.search(text):
        warnings.append("SKILL.md has no explicit blocking gate (⛔ BLOCKING or BLOCKING GATE); risky transitions may be unguarded")
    if not ANTI_SHORTCUT_RE.search(text):
        warnings.append("SKILL.md may lack explicit anti-shortcut rules; common loopholes may remain open")
    if not EVIDENCE_CONTRACT_RE.search(text):
        warnings.append("SKILL.md may lack explicit evidence contracts; completion claims may be unverifiable")
    if VAGUE_GATE_RE.search(text):
        warnings.append("SKILL.md uses vague 'ensure quality' language where a concrete gate or script call may be needed")
    # Check that scripts referenced in SKILL.md actually exist
    script_refs = set(re.findall(r"scripts/([\w_]+\.py)", text))
    missing = script_refs - script_names
    if missing:
        warnings.append(f"SKILL.md references scripts not found in scripts/: {', '.join(sorted(missing))}")
    return warnings


def check_script_actionability(script: Path) -> list[str]:
    """Check that a Python script has argparse or a clear usage pattern."""
    warnings: list[str] = []
    text = read_text(script)
    if "argparse" not in text and "ArgumentParser" not in text and "sys.argv" not in text:
        warnings.append(f"{script.name} may lack CLI argument handling; consider adding argparse for usability")
    if "print(" not in text and "sys.stdout" not in text and "json.dump" not in text and "json.dumps" not in text:
        warnings.append(f"{script.name} may produce no output; scripts should provide actionable feedback")
    return warnings


def check_skill(root: Path) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict = {}

    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        errors.append("Missing SKILL.md")
        return errors, warnings, metrics

    text = read_text(skill_md)
    lines = text.splitlines()
    metrics["skill_md_lines"] = len(lines)
    if len(lines) > 500:
        errors.append(f"SKILL.md has {len(lines)} lines; keep it under 500")

    frontmatter = parse_simple_frontmatter(text)
    metrics["frontmatter_keys"] = sorted(frontmatter)
    if not frontmatter.get("name"):
        errors.append("Frontmatter missing name")
    if not frontmatter.get("description"):
        errors.append("Frontmatter missing description")
    description = frontmatter.get("description", "")
    if description and not re.search(r"\b(use when|when|trigger|evaluate|review|create|edit|work with)\b", description, re.IGNORECASE):
        warnings.append("Description may not contain clear trigger conditions")
    if description and len(WORKFLOW_WORDS.findall(description)) >= 4:
        warnings.append("Description may summarize workflow; keep process details in SKILL.md body")

    if has_unfinished_marker(text):
        errors.append("SKILL.md contains placeholder/TODO text")

    if not re.search(r"IRON LAW|Core Constraint|Operating Rules|Workflow", text, flags=re.IGNORECASE):
        warnings.append("SKILL.md may lack an explicit core constraint or workflow")

    agents_yaml = root / "agents/openai.yaml"
    if not agents_yaml.is_file():
        warnings.append("Missing agents/openai.yaml")

    for bad_name in BAD_AUXILIARY_FILES:
        bad_path = root / bad_name
        if bad_path.exists():
            warnings.append(f"Auxiliary file usually does not belong in a skill: {bad_name}")

    references = sorted((root / "references").glob("*.md")) if (root / "references").is_dir() else []
    metrics["reference_count"] = len(references)
    for ref in references:
        ref_text = read_text(ref)
        if has_unfinished_marker(ref_text):
            errors.append(f"{ref.relative_to(root)} contains placeholder/TODO text")
        if len(ref_text.splitlines()) > 100 and not has_contents_section(ref_text):
            warnings.append(f"{ref.relative_to(root)} is over 100 lines and should have a Contents section")

    scripts = sorted((root / "scripts").glob("*.py")) if (root / "scripts").is_dir() else []
    metrics["python_script_count"] = len(scripts)
    for script in scripts:
        ok, output = run_py_compile(script)
        if not ok:
            errors.append(f"{script.relative_to(root)} failed py_compile: {output}")

    # Semantic checks (warnings only — these are heuristics, not blockers)
    if not errors:
        script_names = {s.name for s in scripts}
        semantic_warnings = check_semantic_gates(text, script_names)
        warnings.extend(semantic_warnings)
        for script in scripts:
            script_warnings = check_script_actionability(script)
            for w in script_warnings:
                warnings.append(f"{script.relative_to(root)}: {w}")

    return errors, warnings, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Check an Agent Skill folder for mechanical quality issues")
    parser.add_argument("skill_path", help="Path to the skill folder")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument("--receipt", help="Write a JSON receipt file after a passing check")
    args = parser.parse_args()

    root = Path(args.skill_path).expanduser().resolve()
    errors, warnings, metrics = check_skill(root)
    payload = {
        "skill_path": str(root),
        "status": "fail" if errors else "pass",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Skill quality check: {root}")
        print(f"Status: {payload['status']}")
        print(f"Errors: {len(errors)}")
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"WARN: {warning}")
        if metrics:
            print("Metrics:")
            for key, value in metrics.items():
                print(f"- {key}: {value}")
    if args.receipt and not errors:
        from datetime import datetime, timezone
        receipt = {
            "skill_path": str(root),
            "status": "pass",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "errors": len(errors),
            "warnings": len(warnings),
            "metrics": metrics,
        }
        receipt_path = Path(args.receipt).expanduser().resolve()
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
