#!/usr/bin/env python3
"""Validate a repository Bug audit package."""
from __future__ import annotations

import argparse
import json
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
    "indexes/findings.generated.md",
    "indexes/findings.generated.json",
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
    "fix_risk",
]
# Allowed values for optional `lens` frontmatter field (see references/exploration-lenses.md).
VALID_LENS = {f"L{i}" for i in range(1, 20)} | {"META-1", "META-2"}
# Lens coverage record sections (5-section hard format from exploration-lenses.md).
LENS_COVERAGE_SECTIONS = {
    "zh": ["已扫描入口", "关注模式", "候选数", "排除原因", "未覆盖"],
    "en": ["Scanned Entry Points", "Patterns", "Candidates", "Exclusion Reasons", "Uncovered"],
}
REQUIRED_SECTIONS = {
    "zh": [
        "结论",
        "影响范围",
        "前置条件",
        "静态复现路径",
        "实际表现",
        "期望表现",
        "代码证据",
        "误报排查",
        "修复边界",
        "修复建议",
        "建议验证命令",
        "验证标准",
    ],
    "en": [
        "Conclusion",
        "Impact Scope",
        "Preconditions",
        "Static Reproduction Path",
        "Actual Behavior",
        "Expected Behavior",
        "Code Evidence",
        "False-positive Review",
        "Fix Boundary",
        "Fix Suggestion",
        "Suggested Verification Commands",
        "Validation Standard",
    ],
}
SECTION_MIN_CHARS = {
    "zh": {
        "代码证据": 20,
        "误报排查": 20,
        "修复边界": 20,
        "修复建议": 20,
        "建议验证命令": 8,
        "验证标准": 20,
    },
    "en": {
        "Code Evidence": 20,
        "False-positive Review": 20,
        "Fix Boundary": 20,
        "Fix Suggestion": 20,
        "Suggested Verification Commands": 8,
        "Validation Standard": 20,
    },
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
    # Inflated significance / "标志着" framing
    "标志着",
    "扮演关键角色",
    "扮演了关键",
    "扮演重要角色",
    "扮演了重要",
    "凸显了",
    "凸显出",
    "奠定了基础",
    "奠定基础",
    "代表着一次",
    "反映了更广泛",
    # Vacuous closers
    "总而言之",
    "综上所述",
    "总的来说",
    "在某种意义上",
    # Future-looking filler in audit context
    "展望未来",
    "未来可期",
    # Vague attribution
    "业内普遍认为",
    "相关研究表明",
    "观察者指出",
    # Promo-style adjectives applied to internal systems
    "充满活力",
    "全方位的",
    "系统性地",
    # Hollow fix-suggestion clichés (anti-fabrication padding)
    "建议添加 try/catch",
    "建议加强校验",
    "建议增加日志",
    "考虑使用",
    "可能需要重构",
    "建议关注",
    "建议进行压测",
    # Pseudo-precise speculation (anti-fabrication, see authenticity.md)
    "推测此处会",
    "理论上可能",
    "代码中应有",
]
# Sections subject to cross-Bug literal-duplicate detection (authenticity.md → category 4).
# Identical paragraphs across these sections are the strongest fabrication signal.
DEDUPE_SECTIONS = {
    "zh": ["静态复现路径", "修复建议", "代码证据"],
    "en": ["Static Reproduction Path", "Fix Suggestion", "Code Evidence"],
}
DEDUPE_MIN_CHARS = 60
PRIORITIES = {"P1", "P2", "P3", "P4"}
CONFIDENCE = {"high", "medium", "low"}
FIX_RISK = {"low", "medium", "high", "unknown"}
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


def section_body(text: str, section: str) -> str | None:
    marker = f"## {section}"
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == marker:
            start = index + 1
            break
    if start is None:
        return None
    body = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip()


def has_verification_command_or_marker(body: str) -> bool:
    normalized = body.lower()
    return bool(
        re.search(r"`[^`]+`", body)
        or "未确认" in body
        or "not confirmed" in normalized
        or "unconfirmed" in normalized
    )


def check_lens_coverage(text: str, language: str) -> tuple[list[str], list[str]]:
    """Parse lens-coverage.md content. Return (errors, warnings).

    Format: each lens is an H3 like '### Lens L9 ...' followed by 5 bullet sections.
    """
    errors: list[str] = []
    warnings: list[str] = []
    sections = LENS_COVERAGE_SECTIONS[language]
    blocks = re.split(r"^###\s+", text, flags=re.MULTILINE)
    declared_lens: list[str] = []
    for block in blocks[1:]:
        header = block.split("\n", 1)[0]
        m = re.search(r"\b(L\d{1,2}|META-[12])\b", header)
        if not m:
            continue
        lens_id = m.group(1)
        if lens_id not in VALID_LENS:
            errors.append(f"lens-coverage.md: unknown lens identifier in heading: {header}")
            continue
        declared_lens.append(lens_id)
        for sec in sections:
            if sec not in block:
                errors.append(f"lens-coverage.md: lens {lens_id} record missing section '{sec}'")
        if "无未覆盖" in block or "no uncovered" in block.lower():
            warnings.append(f"lens-coverage.md: lens {lens_id} claims no uncovered area; honest-uncertainty markers preferred")
    if not declared_lens:
        errors.append("lens-coverage.md present but contains no lens record (expected '### Lens L? ...' blocks)")
    return errors, warnings


def check_mermaid_guards(text: str, rel_path: str) -> list[str]:
    """Light WARN-level checks on mermaid blocks (per call-graph-conventions.md)."""
    warnings: list[str] = []
    blocks = re.findall(r"```mermaid\n(.*?)```", text, re.DOTALL)
    for idx, block in enumerate(blocks, 1):
        node_ids = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*[\[(\{]", block))
        if len(node_ids) > 30:
            warnings.append(f"{rel_path} mermaid block #{idx}: {len(node_ids)} nodes exceeds guardrail of 30; consider splitting")
        block_end = text.find("```", text.find(block) + len(block) - 10)
        tail = text[block_end : block_end + 600] if block_end >= 0 else ""
        if not re.search(r"未覆盖|Uncovered", tail):
            warnings.append(f"{rel_path} mermaid block #{idx}: missing '未覆盖' / 'Uncovered' paragraph within ~600 chars after the diagram (per call-graph-conventions.md)")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Bug audit package")
    parser.add_argument("root", help="Bug audit output root")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="Expected Bug section language")
    parser.add_argument("--max-image-kb", type=int, default=500, help="Warn if PNG exceeds this size")
    parser.add_argument("--require-knowledge", action="store_true", help="Require reusable knowledge docs for final handoff packages")
    parser.add_argument("--require-image", action="store_true", help="Require audit-overview.png for final handoff packages")
    parser.add_argument("--banned", action="append", default=[], help="Additional banned text")
    parser.add_argument(
        "--repo-root",
        action="append",
        default=[],
        help=(
            "Path to a target repository checkout. Enables existence checks for "
            "frontmatter `files[].path` references. May be repeated for multi-repo audits."
        ),
    )
    parser.add_argument(
        "--require-lens-coverage",
        action="store_true",
        help="Require submit/quality/lens-coverage.md to exist and contain valid 5-section records per enabled lens",
    )
    parser.add_argument(
        "--allow-id-gaps",
        action="store_true",
        help="Allow non-contiguous BUG-xxxx IDs. Reserved for in-progress / resume runs only; final delivery must be contiguous BUG-0001..BUG-N",
    )
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
            errors.append(f"Temporary directory must not be in audit output: {temporary_dir}")

    seen_ids = {}
    finding_count = 0
    repos = set()
    # Authenticity: collect long paragraphs from high-risk sections for cross-Bug duplicate detection.
    dedupe_index: dict[str, list[str]] = {}
    repo_roots = [Path(p).expanduser().resolve() for p in args.repo_root] if args.repo_root else []
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
        fix_risk = meta.get("fix_risk")
        if fix_risk not in FIX_RISK:
            errors.append(f"{rel} fix_risk must be low/medium/high/unknown")
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
        # Lens enum check (optional `lens:` frontmatter, single value or list)
        lens_meta = meta.get("lens")
        if lens_meta is not None:
            lens_values = lens_meta if isinstance(lens_meta, list) else [lens_meta]
            for lv in lens_values:
                if str(lv).strip() not in VALID_LENS:
                    errors.append(f"{rel} invalid lens value: {lv} (allowed: L1-L19, META-1, META-2)")
        domains = as_list(meta.get("infra_domains"))
        if not domains:
            errors.append(f"{rel} infra_domains must contain at least one value")
        for section in REQUIRED_SECTIONS[args.language]:
            if f"## {section}" not in text:
                errors.append(f"{rel} missing section: {section}")
                continue
            min_len = SECTION_MIN_CHARS[args.language].get(section)
            if min_len is not None:
                body = section_body(text, section) or ""
                if len(body) < min_len:
                    errors.append(f"{rel} section is too thin: {section}")
                if section in ("建议验证命令", "Suggested Verification Commands") and not has_verification_command_or_marker(body):
                    errors.append(f"{rel} suggested verification commands must include a confirmed command or an explicit unconfirmed marker")
        # Authenticity: cross-Bug duplicate detection on high-risk sections.
        for section in DEDUPE_SECTIONS[args.language]:
            body = section_body(text, section) or ""
            for paragraph in body.split("\n\n"):
                normalized = re.sub(r"\s+", " ", paragraph).strip()
                if len(normalized) >= DEDUPE_MIN_CHARS:
                    dedupe_index.setdefault(normalized, []).append(f"{rel}::{section}")
        # Authenticity: frontmatter file paths must exist in at least one provided repo root.
        if repo_roots:
            files_meta = meta.get("files")
            file_entries = files_meta if isinstance(files_meta, list) else []
            for entry in file_entries:
                rel_path = None
                if isinstance(entry, dict):
                    rel_path = entry.get("path")
                elif isinstance(entry, str):
                    rel_path = entry
                if not rel_path:
                    continue
                rel_path = str(rel_path).strip().lstrip("/")
                if not rel_path:
                    continue
                if not any((rr / rel_path).exists() for rr in repo_roots):
                    errors.append(
                        f"{rel} references non-existent path in frontmatter files: {rel_path}"
                    )

    # Bug ID continuity: final delivery must be a single contiguous BUG-0001..BUG-N range.
    # Gaps and segmented per-agent ranges (e.g. parallel sub-agent merges) must be
    # consolidated before submission. See references/resume-audit.md
    # → "Parallel Multi-Agent Consolidation".
    if seen_ids:
        numeric_ids = []
        for raw_id in seen_ids:
            m = re.fullmatch(r"BUG-(\d{4})", str(raw_id))
            if m:
                numeric_ids.append(int(m.group(1)))
        numeric_ids.sort()
        if numeric_ids:
            n = len(numeric_ids)
            expected = list(range(1, n + 1))
            min_id = numeric_ids[0]
            max_id = numeric_ids[-1]
            duplicates = sorted({x for x in numeric_ids if numeric_ids.count(x) > 1})
            unique_sorted = sorted(set(numeric_ids))
            missing = sorted(set(range(1, max_id + 1)) - set(unique_sorted))
            is_contiguous_from_one = numeric_ids == expected and not duplicates
            if not is_contiguous_from_one:
                detail_parts = []
                if min_id != 1:
                    detail_parts.append(f"sequence does not start at BUG-0001 (min=BUG-{min_id:04d})")
                if missing:
                    preview = ", ".join(f"BUG-{x:04d}" for x in missing[:8])
                    if len(missing) > 8:
                        preview += f", … (+{len(missing) - 8} more)"
                    detail_parts.append(f"missing IDs: {preview}")
                if max_id != n or (min_id == 1 and missing):
                    detail_parts.append(f"have {n} Bugs, max=BUG-{max_id:04d} (expected BUG-{n:04d})")
                detail = "; ".join(detail_parts) or "non-contiguous sequence"
                msg = (
                    "Bug IDs must form a single contiguous range BUG-0001..BUG-"
                    f"{n:04d} for final delivery. {detail}. "
                    "If multiple agents ran in parallel, consolidate and renumber per "
                    "references/resume-audit.md → \"Parallel Multi-Agent Consolidation\". "
                    "Use --allow-id-gaps for in-progress / resume runs only."
                )
                if args.allow_id_gaps:
                    warnings.append(msg)
                else:
                    errors.append(msg)

    # Authenticity: report cross-Bug literal-duplicate paragraphs in high-risk sections.
    for normalized, locations in dedupe_index.items():
        unique_bugs = {loc.split("::")[0] for loc in locations}
        if len(unique_bugs) >= 2:
            preview = (normalized[:60] + "…") if len(normalized) > 60 else normalized
            errors.append(
                "Duplicate paragraph (template-padding signal) appears in: "
                + ", ".join(sorted(locations))
                + f" — content starts with: {preview!r}"
            )

    # Lens coverage check (D2 lens system)
    lens_coverage_path = root / "quality/lens-coverage.md"
    if lens_coverage_path.is_file():
        lc_text = lens_coverage_path.read_text(encoding="utf-8", errors="replace")
        lc_errors, lc_warnings = check_lens_coverage(lc_text, args.language)
        errors.extend(lc_errors)
        warnings.extend(lc_warnings)
    elif args.require_lens_coverage:
        errors.append("Missing quality/lens-coverage.md (required by --require-lens-coverage; see references/exploration-lenses.md)")

    # Mermaid call-graph guardrail check on repo profiles (D3)
    profiles_dir = root / "knowledge/repo-profiles"
    if profiles_dir.is_dir():
        for profile_path in sorted(profiles_dir.glob("*.md")):
            if profile_path.name in ("README.md",):
                continue
            profile_rel = profile_path.relative_to(root).as_posix()
            profile_text = profile_path.read_text(encoding="utf-8", errors="replace")
            warnings.extend(check_mermaid_guards(profile_text, profile_rel))

    index_json = root / "indexes/findings.generated.json"
    if index_json.is_file():
        try:
            index_payload = json.loads(index_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"indexes/findings.generated.json is not valid JSON: {exc}")
        else:
            if index_payload.get("total") != finding_count:
                errors.append(
                    "indexes/findings.generated.json total is stale: "
                    f"index={index_payload.get('total')}, findings={finding_count}"
                )
            indexed_findings = index_payload.get("findings")
            if not isinstance(indexed_findings, list):
                errors.append("indexes/findings.generated.json must contain a findings list")
            else:
                indexed_ids = {str(item.get("id", "")) for item in indexed_findings if isinstance(item, dict)}
                actual_ids = {str(bug_id) for bug_id in seen_ids}
                if indexed_ids != actual_ids:
                    missing = sorted(actual_ids - indexed_ids)
                    extra = sorted(indexed_ids - actual_ids)
                    errors.append(
                        "indexes/findings.generated.json ids are stale: "
                        f"missing={missing or []}, extra={extra or []}"
                    )
                for item in indexed_findings:
                    if not isinstance(item, dict):
                        errors.append("indexes/findings.generated.json findings entries must be objects")
                        continue
                    for key in ("entry_points", "files", "related_repos"):
                        if key not in item:
                            errors.append(f"indexes/findings.generated.json finding {item.get('id', '<unknown>')} missing {key}")

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
