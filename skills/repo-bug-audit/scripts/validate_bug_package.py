#!/usr/bin/env python3
"""Validate a repository Bug audit package."""
from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path

REQUIRED_DIRS = [
    "findings/P1",
    "findings/P2",
    "findings/P3",
    "findings/P4",
    "indexes",
    "knowledge",
    "knowledge/repo-profiles",
    "quality",
    "standards",
]
REQUIRED_FILES = [
    "README.md",
    "quality/submission-scope.md",
    "quality/repository-versions.md",
    "standards/bug-report-standard.md",
    "knowledge/README.md",
]
OPTIONAL_KNOWLEDGE_FILES = [
    "knowledge/system-overview.md",
    "knowledge/repo-relationship-map.md",
    "knowledge/risk-paths.md",
    "knowledge/architecture-design-review.md",
]
REQUIRED_KNOWLEDGE_FOR_HANDOFF = [
    "knowledge/system-overview.md",
    "knowledge/repo-relationship-map.md",
    "knowledge/risk-paths.md",
]
REQUIRED_META = [
    "id",
    "priority",
    "confidence",
    "status",
    "source",
    "repo",
    "module",
    "category",
    "issue_family",
    "infra_domains",
]
REQUIRED_SECTIONS = {
    "zh": ["结论", "影响范围", "前置条件", "静态复现路径", "实际表现", "期望表现", "代码证据", "误报排查", "修复建议", "验证标准"],
    "en": [
        "Conclusion",
        "Impact Scope",
        "Preconditions",
        "Static Reproduction Path",
        "Actual Behavior",
        "Expected Behavior",
        "Code Evidence",
        "False-positive Review",
        "Fix Suggestion",
        "Validation Standard",
    ],
}
DEFAULT_BANNED = [
    "AI 分析",
    "AI 生成",
    "AI 味道",
    "AI Agent",
    "由 AI",
    "作为 AI",
    "我是 AI",
    "大模型",
    "智能分析",
    "自动分析",
    "高置信缺陷",
    "已完成验证",
    "已完成复核",
    "确认无误",
    "全部真实",
    "面向开发团队",
    "供开发者参考",
    "方便后续使用",
    "可直接修复",
    "下面是分析结果",
    "经过分析",
    "我将从",
    "我们发现",
    "值得关注",
]
PRIORITIES = {"P1", "P2", "P3", "P4"}
CONFIDENCE = {"high", "medium", "low"}
BUG_FILE_RE = re.compile(r"^P[1-4]-BUG-\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


def parse_value(raw: str):
    raw = raw.strip().strip('"').strip("'")
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip('"').strip("'") for x in inner.split(",")]
    return raw


def append_block_value(data: dict, key: str, raw: str):
    if ":" in raw:
        item_key, item_val = raw.split(":", 1)
        item = {item_key.strip(): parse_value(item_val)}
        data.setdefault(key, []).append(item)
        return item
    data.setdefault(key, []).append(parse_value(raw))
    return None


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data = {}
    current_key = None
    current_item = None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if not line.startswith(" ") and ":" in line:
            key, val = line.split(":", 1)
            current_key = key.strip()
            current_item = None
            data[current_key] = parse_value(val) if val.strip() else []
            continue
        if current_key and line.startswith("  - "):
            current_item = append_block_value(data, current_key, line[4:].strip())
            continue
        if current_item is not None and line.startswith("    ") and ":" in line:
            key, val = line.strip().split(":", 1)
            current_item[key.strip()] = parse_value(val)
    return data


def read_png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError:
        return None
    if len(header) < 24 or not header.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    if header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def as_list(value) -> list:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def body_len(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    body = "\n".join(line for line in text.splitlines() if not line.startswith("#")).strip()
    return len(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Bug audit package")
    parser.add_argument("root", help="Bug package root")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="Expected Bug section language")
    parser.add_argument("--max-image-kb", type=int, default=500, help="Warn if PNG exceeds this size")
    parser.add_argument("--require-knowledge", action="store_true", help="Require reusable knowledge docs for final handoff packages")
    parser.add_argument("--require-image", action="store_true", help="Require audit-overview.png for final handoff packages")
    parser.add_argument("--banned", action="append", default=[], help="Additional banned text")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if (root / "submit").is_dir() and not (root / "findings").is_dir():
        root = root / "submit"
    errors = []
    warnings = []

    for d in REQUIRED_DIRS:
        if not (root / d).is_dir():
            errors.append(f"Missing directory: {d}")
    for f in REQUIRED_FILES:
        if not (root / f).is_file():
            errors.append(f"Missing file: {f}")
    versions_path = root / "quality/repository-versions.md"
    if versions_path.is_file():
        version_text = versions_path.read_text(encoding="utf-8", errors="replace")
        for heading in ("Branch", "分支"):
            if heading in version_text:
                break
        else:
            warnings.append("quality/repository-versions.md should include branch information when available")
        if not any(term in version_text for term in ("Commit", "commit")):
            warnings.append("quality/repository-versions.md should include commit hash information when available")
        if not any(term in version_text for term in ("Dirty", "工作区状态")):
            warnings.append("quality/repository-versions.md should include dirty worktree status when available")
    for f in OPTIONAL_KNOWLEDGE_FILES:
        path = root / f
        if path.exists():
            if body_len(path) < 40:
                warnings.append(f"{f} appears empty; fill it or remove it before packaging")
    for temporary_dir in ("candidates", "eval", "infographic", "scanner-output", "drafts", "tmp"):
        if (root / temporary_dir).exists():
            errors.append(f"Temporary directory must not be in submission package: {temporary_dir}")

    seen_ids = {}
    finding_count = 0
    repos = set()
    for path in sorted((root / "findings").glob("P*/*.md")):
        finding_count += 1
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if not BUG_FILE_RE.match(path.name):
            errors.append(f"{rel} filename must match P1-BUG-0001-short-description.md")
        for key in REQUIRED_META:
            if key not in meta or meta.get(key) in ("", []):
                errors.append(f"{rel} missing metadata: {key}")
        bug_id = meta.get("id")
        if bug_id:
            if not re.fullmatch(r"BUG-\d{4}", str(bug_id)):
                errors.append(f"{rel} id must match BUG-0001")
            if bug_id in seen_ids:
                errors.append(f"{rel} duplicate id also used by {seen_ids[bug_id]}")
            seen_ids[bug_id] = rel
        priority = meta.get("priority")
        if priority not in PRIORITIES:
            errors.append(f"{rel} priority must be one of P1/P2/P3/P4")
        elif path.parent.name != priority:
            errors.append(f"{rel} priority mismatch: metadata={priority}, folder={path.parent.name}")
        confidence = meta.get("confidence")
        if confidence not in CONFIDENCE:
            errors.append(f"{rel} confidence must be high/medium/low")
        if meta.get("status") != "open":
            errors.append(f"{rel} status must be open")
        if meta.get("source") != "static-analysis":
            errors.append(f"{rel} source must be static-analysis")
        if meta.get("repo"):
            repos.add(str(meta.get("repo")))
        if "sla" in meta:
            errors.append(f"{rel} must not include SLA metadata")
        if "owner" in meta or "due_date" in meta:
            warnings.append(f"{rel} contains workflow-tracking metadata; include only if requested")
        domains = as_list(meta.get("infra_domains"))
        if not domains:
            errors.append(f"{rel} infra_domains must contain at least one value")
        for section in REQUIRED_SECTIONS[args.language]:
            if f"## {section}" not in text:
                errors.append(f"{rel} missing section: {section}")

    if args.require_knowledge and finding_count:
        for f in REQUIRED_KNOWLEDGE_FOR_HANDOFF:
            path = root / f
            if not path.is_file():
                errors.append(f"Missing reusable knowledge file for handoff: {f}")
            elif body_len(path) < 120:
                errors.append(f"{f} is too thin for handoff knowledge; expand it or omit --require-knowledge")
        repo_profiles = list((root / "knowledge/repo-profiles").glob("*.md"))
        if not repo_profiles:
            errors.append("Missing repo profiles for handoff knowledge: knowledge/repo-profiles/*.md")
        for path in repo_profiles:
            if body_len(path) < 80:
                errors.append(f"{path.relative_to(root)} is too thin for handoff knowledge")
        if len(repos) > 1:
            arch = root / "knowledge/architecture-design-review.md"
            if not arch.is_file():
                errors.append("Missing architecture review for multi-repo handoff: knowledge/architecture-design-review.md")
            elif body_len(arch) < 120:
                errors.append("knowledge/architecture-design-review.md is too thin for multi-repo handoff")

    banned = DEFAULT_BANNED + args.banned
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for term in banned:
            if term and term in text:
                warnings.append(f"{path.relative_to(root)} contains discouraged term: {term}")

    for path in sorted(root.rglob("*.png")):
        size_kb = path.stat().st_size / 1024
        if size_kb > args.max_image_kb:
            warnings.append(f"{path.relative_to(root)} is {size_kb:.0f}KB; consider compressing")
    overview_image = root / "audit-overview.png"
    if args.require_image and not overview_image.is_file():
        errors.append("Missing required audit overview image: audit-overview.png")
    if overview_image.is_file() and overview_image.stat().st_size == 0:
        errors.append("audit-overview.png is empty")
    if overview_image.is_file() and overview_image.stat().st_size > 0:
        dimensions = read_png_dimensions(overview_image)
        if dimensions is None:
            message = "audit-overview.png dimensions could not be read; verify it is a valid PNG"
            if args.require_image:
                errors.append(message)
            else:
                warnings.append(message)
        else:
            width, height = dimensions
            aspect = width / height if height else 0
            if width < 1400 or height < 900:
                message = (
                    f"audit-overview.png is {width}x{height}; overview images may be hard to read below 1400x900"
                )
                if args.require_image:
                    errors.append(message)
                else:
                    warnings.append(message)
            if aspect < 1.2:
                message = (
                    f"audit-overview.png aspect ratio is {aspect:.2f}; avoid long vertical or square overview images"
                )
                if args.require_image:
                    errors.append(message)
                else:
                    warnings.append(message)
            if aspect > 2.0:
                message = (
                    f"audit-overview.png aspect ratio is {aspect:.2f}; very wide images can shrink text in previews"
                )
                if args.require_image:
                    errors.append(message)
                else:
                    warnings.append(message)

    print(f"Validated package: {root}")
    print(f"Errors: {len(errors)}")
    for e in errors[:100]:
        print(f"ERROR: {e}")
    if len(errors) > 100:
        print(f"ERROR: ... {len(errors)-100} more")
    print(f"Warnings: {len(warnings)}")
    for w in warnings[:100]:
        print(f"WARN: {w}")
    if len(warnings) > 100:
        print(f"WARN: ... {len(warnings)-100} more")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
