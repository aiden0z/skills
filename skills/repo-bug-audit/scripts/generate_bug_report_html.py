#!/usr/bin/env python3
"""Generate a self-contained interactive HTML Bug audit report."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import audit_scope_contract

SKILL_NAME = "repo-bug-audit"
SKILL_SOURCE = "github.com/aiden0z/skills"
SKILL_SOURCE_URL = "https://github.com/aiden0z/skills"

PRIORITY_ORDER = ["P1", "P2", "P3", "P4"]
SHARD_GATE_RECEIPT = "work/scanner-output/shard-gate.passed.json"
PREPACKAGE_RECEIPT = "work/scanner-output/prepackage-validation.passed.json"
REPO_INVENTORY = "work/scanner-output/repo-inventory.json"
DEPTH_COVERAGE = "quality/depth-coverage.md"
SUBMISSION_SCOPE = "quality/submission-scope.md"
CANDIDATE_COVERAGE = "quality/candidate-coverage.md"
DEPTH_INTENT_RE = re.compile(
    r"(audit depth intent|analysis depth|requested depth|审计深度意图|分析深度|请求深度)\s*[:：]\s*`?([^\n`]+)",
    re.IGNORECASE,
)
DEEP_INTENT_RE = re.compile(
    r"\b(deep|full|complete|exhaustive|max(?:imum)?|per[- ]repo)\b|"
    r"深度|完整|全面|尽可能|每个\s*repo|每仓|逐仓|全部仓库",
    re.IGNORECASE,
)
REQUESTED_DEEP_RE = re.compile(
    r"((user|original|initial)\s+(request|requested|asked|intent)|用户.*(要求|请求|希望)|原始.*(要求|请求))"
    r".{0,100}"
    r"(\b(deep|full|complete|exhaustive|max(?:imum)?|per[- ]repo)\b|深度|完整|全面|尽可能|每个\s*repo|每仓|逐仓|全部仓库)",
    re.IGNORECASE,
)
PARTIAL_COVERAGE_RE = re.compile(
    r"\b(first[- ]pass|focused|in[- ]progress)\b|首轮|第一阶段|聚焦|进行中",
    re.IGNORECASE,
)
DEEP_COMPLETE_RE = re.compile(r"\bdeep[- ]complete\b|深度完成", re.IGNORECASE)
DOWNGRADE_ACCEPTED_RE = re.compile(
    r"(depth downgrade accepted|user accepted downgrade|accepted first[- ]pass|"
    r"用户.*(接受|确认|同意).*(降级|首轮|第一阶段|first[- ]pass)|"
    r"(降级|首轮|第一阶段|first[- ]pass).*(用户.*(接受|确认|同意)))",
    re.IGNORECASE,
)

LENS_NAMES = {
    "en": {
        "api-contract": "API contract",
        "cache": "Cache",
        "message": "Message",
        "rollback": "Rollback",
        "third-party": "Third-party",
        "lifecycle": "Lifecycle",
        "concurrency": "Concurrency",
        "config": "Config",
        "failure-mode": "Failure mode",
        "clock": "Clock",
        "permission-propagation": "Permission propagation",
        "pagination": "Pagination",
        "idempotency": "Idempotency",
        "META-1": "Intent vs implementation",
        "META-2": "Failure-path test coverage",
    },
    "zh": {
        "api-contract": "API 契约",
        "cache": "缓存",
        "message": "消息",
        "rollback": "回滚",
        "third-party": "第三方依赖",
        "lifecycle": "生命周期",
        "concurrency": "并发",
        "config": "配置",
        "failure-mode": "失败模式",
        "clock": "时钟",
        "permission-propagation": "权限传递",
        "pagination": "分页",
        "idempotency": "幂等性",
        "META-1": "意图与实现漂移",
        "META-2": "失败路径测试覆盖",
    },
}

TIER_GROUPS = [
    ("local", "Service-Local", ["config", "concurrency", "lifecycle", "clock", "cache", "failure-mode"]),
    ("cross-service", "Cross-Service", ["api-contract", "message", "third-party", "rollback", "pagination", "idempotency"]),
    ("cross-repo", "Cross-Repo", ["permission-propagation"]),
]

TIER_NAMES = {
    "en": {
        "local": "service-local boundaries",
        "cross-service": "cross-service boundaries",
        "cross-repo": "cross-repo amplification",
        "meta": "candidate amplification checks",
    },
    "zh": {
        "local": "服务内边界",
        "cross-service": "跨服务边界",
        "cross-repo": "跨仓库放大",
        "meta": "META 透镜",
    },
}

LABELS = {
    "en": {
        "title_suffix": "Bug Static Analysis Report",
        "open_audit": "BUG AUDIT",
        "report_console": "Audit Delivery Report",
        "source": "source=static-analysis",
        "generated_with": "Generated with",
        "skill_source": "Skill source",
        "data_from": "Data from final package files",
        "total": "Total Bugs",
        "p1p2": "P1/P2 Focus",
        "repos": "Analyzed Repos",
        "quality": "Quality Core",
        "quality_gate": "Evidence Gate",
        "coverage_strategy": "Exploration Coverage",
        "coverage_boundary": "Known Boundaries",
        "metrics_eyebrow": "Metrics",
        "priority_breakdown": "Priority Breakdown",
        "quality_eyebrow": "Quality gates",
        "quality_title": "Quality Core Insights",
        "architecture_eyebrow": "Architecture",
        "architecture_title": "Architecture Insights",
        "repo_eyebrow": "Repository distribution",
        "findings_eyebrow": "Submitted findings",
        "findings_title": "Findings Preview",
        "knowledge_eyebrow": "Reusable knowledge",
        "guide_eyebrow": "Handoff guide",
        "risk": "Risk Composition",
        "analysis_scope": "Analysis Scope",
        "analysis_scope_eyebrow": "Scope baseline",
        "analysis_scope_title": "Analysis Scope and Version Baseline",
        "audit_branch": "Audit Branch",
        "commit": "Commit",
        "dirty": "Worktree",
        "submitted_bugs": "Submitted Bugs",
        "architecture": "Architecture Insights",
        "repo_situation": "Repository Situation",
        "coverage_classification": "Coverage Classification",
        "findings": "Findings Preview",
        "knowledge": "Reusable Knowledge",
        "guide": "Delivery Package Guide",
        "provenance": "Provenance",
        "search": "Search Bug ID, title, repo, module, category...",
        "all": "All",
        "priority": "Priority",
        "repo": "Repo",
        "category": "Category",
        "confidence": "Confidence",
        "fix_risk": "Fix Risk",
        "risk_types": "Risk Types",
        "classified_categories": "classified categories",
        "lens": "Coverage tag",
        "bug_details": "Details",
        "conclusion": "Conclusion",
        "impact": "Impact",
        "evidence": "Evidence",
        "false_positive": "False-positive Review",
        "fix_boundary": "Fix Boundary",
        "verification": "Verification",
        "package_files": "Package Files",
        "reading_order": "Suggested reading order",
        "no_findings": "No submitted Bugs found.",
        "not_specified": "not specified",
        "version_evidence": "Version evidence",
        "method": "Method",
        "status": "Status",
        "analyst": "Analyst",
        "date": "Date",
        "scope": "Scope",
        "static_note": "No runtime verification is claimed unless it appears explicitly in the submitted package.",
        "source_files": "Source files",
        "open_markdown": "Markdown file",
        "show_p1p2": "Show P1/P2",
        "reset": "Reset",
        "current_results": "Visible",
        "page_size": "Per page",
        "prev": "Prev",
        "next": "Next",
        "submission_scope": "Submission scope",
        "lens_coverage": "Coverage record",
        "architecture_signals": "Architecture signals",
        "risk_paths": "Risk paths",
        "architecture_invariants": "Architecture invariants",
        "issue_families": "Issue families",
        "impact_domains": "Impact domains",
        "handoff_focus": "Fix priorities",
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "low": "low",
        "repo_profiles": "repo profiles",
        "interactive_report": "interactive report",
        "summary": "summary",
        "bug_records": "Bug records",
        "machine_data": "machine data",
        "repo_cognition": "repo cognition",
        "scope_gates": "scope/gates",
        "schema": "schema",
        "static_cover": "static cover",
        "hero_metrics": "01 Hero metrics",
        "p1p2_findings": "02 P1/P2 findings",
        "architecture_reading": "03 Architecture insights",
        "knowledge_gates": "04 Knowledge and handoff",
        "lens_fallback": "Coverage details are available in quality/lens-coverage.md.",
        "depth_fallback": "Depth coverage details are available in quality/depth-coverage.md.",
        "architecture_fallback": "No architecture-design-review.md content was found.",
        "risk_fallback": "No risk-path or repo-relationship summary was found.",
    },
    "zh": {
        "title_suffix": "Bug 静态分析报告",
        "open_audit": "BUG 审计",
        "report_console": "审计交付报告",
        "source": "source=static-analysis",
        "generated_with": "生成工具",
        "skill_source": "Skill 来源",
        "data_from": "数据来自最终交付包",
        "total": "Bug 总数",
        "p1p2": "P1/P2 重点",
        "repos": "分析仓库",
        "quality": "质量核心",
        "quality_gate": "收录与证据门槛",
        "coverage_strategy": "覆盖策略",
        "coverage_boundary": "已知边界",
        "metrics_eyebrow": "核心指标",
        "priority_breakdown": "优先级分布",
        "quality_eyebrow": "审计门禁",
        "quality_title": "质量核心洞察",
        "architecture_eyebrow": "架构阅读",
        "architecture_title": "架构洞察",
        "repo_eyebrow": "仓库分布",
        "findings_eyebrow": "已提交问题",
        "findings_title": "Bug 预览",
        "knowledge_eyebrow": "可复用认知",
        "guide_eyebrow": "交付指引",
        "risk": "风险组成",
        "analysis_scope": "分析范围",
        "analysis_scope_eyebrow": "范围基线",
        "analysis_scope_title": "分析范围与版本基线",
        "audit_branch": "审计分支",
        "commit": "Commit",
        "dirty": "工作区状态",
        "submitted_bugs": "提交 Bug",
        "architecture": "架构洞察",
        "repo_situation": "仓库情况",
        "coverage_classification": "覆盖分类",
        "findings": "Bug 预览",
        "knowledge": "可复用知识",
        "guide": "交付物指引",
        "provenance": "来源与方法",
        "search": "搜索 Bug ID、标题、仓库、模块、类型...",
        "all": "全部",
        "priority": "优先级",
        "repo": "仓库",
        "category": "类型",
        "confidence": "置信度",
        "fix_risk": "修复风险",
        "risk_types": "风险类型",
        "classified_categories": "已归类问题",
        "lens": "覆盖标签",
        "bug_details": "详情",
        "conclusion": "结论",
        "impact": "影响",
        "evidence": "证据",
        "false_positive": "误报排查",
        "fix_boundary": "修复边界",
        "verification": "验证命令",
        "package_files": "交付文件",
        "reading_order": "建议阅读顺序",
        "no_findings": "未发现已提交 Bug。",
        "not_specified": "待补充",
        "version_evidence": "版本凭证",
        "method": "方法",
        "status": "状态",
        "analyst": "分析人",
        "date": "时间",
        "scope": "范围",
        "static_note": "除非交付包中明确提供运行时证据，否则本报告不声称已完成运行时验证。",
        "source_files": "数据来源",
        "open_markdown": "Markdown 文件",
        "show_p1p2": "只看 P1/P2",
        "reset": "重置",
        "current_results": "当前结果",
        "page_size": "每页",
        "prev": "上一页",
        "next": "下一页",
        "submission_scope": "提交口径",
        "lens_coverage": "覆盖记录",
        "architecture_signals": "架构风险信号",
        "risk_paths": "风险路径",
        "architecture_invariants": "架构不变量",
        "issue_families": "问题族",
        "impact_domains": "影响域",
        "handoff_focus": "后续修复重点",
        "critical": "严重",
        "high": "高",
        "medium": "中",
        "low": "低",
        "repo_profiles": "仓库画像",
        "interactive_report": "交互报告",
        "summary": "摘要",
        "bug_records": "Bug 明细",
        "machine_data": "机器可读数据",
        "repo_cognition": "仓库认知",
        "scope_gates": "口径/门禁",
        "schema": "规范",
        "static_cover": "静态封面",
        "hero_metrics": "01 总览指标",
        "p1p2_findings": "02 P1/P2 重点",
        "architecture_reading": "03 架构洞察",
        "knowledge_gates": "04 知识与交付",
        "lens_fallback": "覆盖细节见 quality/lens-coverage.md。",
        "depth_fallback": "深度覆盖细节见 quality/depth-coverage.md。",
        "architecture_fallback": "未找到 architecture-design-review.md 内容。",
        "risk_fallback": "未找到 risk-path 或 repo-relationship 摘要。",
    },
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def audit_workspace_root(root: Path) -> Path:
    return root.parent if root.name == "submit" else root


def is_repo_group_workspace(root: Path) -> bool:
    workspace_root = audit_workspace_root(root)
    inventory_path = workspace_root / REPO_INVENTORY
    if inventory_path.is_file():
        try:
            payload = json.loads(inventory_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return True
        repos = payload.get("repos")
        if isinstance(repos, list):
            return len(repos) > 1
        return True
    shards_root = workspace_root / "work/shards"
    if shards_root.is_dir():
        return sum(1 for path in shards_root.iterdir() if path.is_dir()) > 1
    return False


def ensure_report_gate(root: Path, allow_ungated_draft: bool) -> None:
    if allow_ungated_draft:
        return
    workspace_root = audit_workspace_root(root)
    prepackage_receipt = workspace_root / PREPACKAGE_RECEIPT
    if not prepackage_receipt.is_file():
        raise SystemExit(
            "Refusing to generate final HTML report before pre-package validation passes.\n"
            f"Missing: {prepackage_receipt}\n"
            "Run: python3 scripts/validate_bug_package.py <submit-root> --repo-root <target-root>\n"
            "Use --allow-ungated-draft only for an explicitly labeled non-final draft."
        )
    enforce_depth_intent_report_gate(root)
    if not is_repo_group_workspace(root):
        return
    receipt_path = workspace_root / SHARD_GATE_RECEIPT
    if not receipt_path.is_file():
        raise SystemExit(
            "Refusing to generate final HTML report for a repo-group audit before the shard evidence gate passes.\n"
            f"Missing: {receipt_path}\n"
            "Run: python3 scripts/validate_bug_package.py <submit-root> --validate-shards-only --repo-root <target-root>\n"
            "Use --allow-ungated-draft only for an explicitly labeled non-final draft."
        )


def extract_depth_intent(scope_text: str) -> str:
    match = DEPTH_INTENT_RE.search(scope_text)
    if match:
        return match.group(2).strip()
    return ""


def scope_records_requested_deep(scope_text: str) -> bool:
    return bool(REQUESTED_DEEP_RE.search(scope_text))


def enforce_depth_intent_report_gate(root: Path) -> None:
    scope_path = root / SUBMISSION_SCOPE
    depth_path = root / DEPTH_COVERAGE
    scope_text = scope_path.read_text(encoding="utf-8", errors="replace") if scope_path.is_file() else ""
    depth_text = depth_path.read_text(encoding="utf-8", errors="replace") if depth_path.is_file() else ""
    intent = extract_depth_intent(scope_text)
    if not intent:
        raise SystemExit(
            "Refusing to generate final HTML report before audit depth intent is recorded.\n"
            f"Add a line to {SUBMISSION_SCOPE}: 'Audit depth intent: deep | first-pass | focused | lightweight | custom'."
        )
    if intent.lower() in {"pending", "unknown", "todo", "tbd", "待确认", "未知"}:
        raise SystemExit(f"Refusing to generate final HTML report while audit depth intent is unresolved: {intent}")
    scope_requested_deep = scope_records_requested_deep(scope_text)
    deep_requested = bool(DEEP_INTENT_RE.search(intent) or scope_requested_deep)
    partial_coverage = depth_coverage_is_partial(depth_text)
    downgrade_accepted = bool(DOWNGRADE_ACCEPTED_RE.search(scope_text) or DOWNGRADE_ACCEPTED_RE.search(depth_text))
    if scope_requested_deep and not DEEP_INTENT_RE.search(intent):
        raise SystemExit(
            "Refusing to generate final HTML report: submission-scope.md says the user requested deep/full analysis, "
            "but audit depth intent was rewritten to a non-deep value. Keep requested depth intent separate from "
            "delivered coverage classification, or record user-accepted downgrade before creating final report assets."
        )
    if deep_requested and not depth_text.strip():
        raise SystemExit(
            "Refusing to generate final HTML report: requested depth is deep/full, "
            f"but {DEPTH_COVERAGE} is missing or empty."
        )
    if deep_requested and partial_coverage and not downgrade_accepted:
        raise SystemExit(
            "Refusing to generate final HTML report: requested depth is deep/full, "
            "but depth coverage is first-pass/focused/in-progress.\n"
            "Continue repo-local exploration, or record that the user accepted a depth downgrade before creating final report assets."
        )


def depth_coverage_is_partial(depth_text: str) -> bool:
    classification_lines = [
        line
        for line in depth_text.splitlines()
        if re.search(r"coverage classification|覆盖分类|scope claim|范围结论|深度结论", line, re.IGNORECASE)
    ]
    for line in classification_lines:
        if DEEP_COMPLETE_RE.search(line) and not PARTIAL_COVERAGE_RE.search(line):
            return False
        if PARTIAL_COVERAGE_RE.search(line):
            return True
    if DEEP_COMPLETE_RE.search(depth_text) and not PARTIAL_COVERAGE_RE.search(depth_text):
        return False
    return bool(PARTIAL_COVERAGE_RE.search(depth_text))


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


def as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value if not isinstance(x, dict)]
    if value in (None, ""):
        return []
    return [str(value)]


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def section_body(text: str, names: list[str]) -> str:
    lines = text.splitlines()
    for name in names:
        marker = f"## {name}"
        start = None
        for index, line in enumerate(lines):
            if line.strip() == marker:
                start = index + 1
                break
        if start is None:
            continue
        body = []
        for line in lines[start:]:
            if line.startswith("## "):
                break
            body.append(line)
        return "\n".join(body).strip()
    return ""


def compact_absolute_paths(value: str) -> str:
    pattern = re.compile(r"(?<![\w:])(?:~|/(?:Users|home|tmp|var|private|opt))[^\s，,。；;：:)]+")

    def replace(match: re.Match) -> str:
        raw = match.group(0)
        normalized = raw.replace("~", str(Path.home()), 1)
        return Path(normalized).name or raw

    return pattern.sub(replace, value)


def strip_markdown(value: str, limit: int = 280) -> str:
    value = re.sub(r"```.*?```", " ", value, flags=re.DOTALL)
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"^#+\s*", "", value, flags=re.MULTILINE)
    value = re.sub(r"[*_>#]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = compact_absolute_paths(value)
    if len(value) > limit:
        return value[: limit - 1].rstrip() + "…"
    return value


def extract_bullets(text: str, limit: int = 6) -> list[str]:
    bullets = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            item = strip_markdown(stripped[2:], 180)
            if item and item not in bullets:
                bullets.append(item)
        if len(bullets) >= limit:
            break
    return bullets


def unique_items(items: list[str], limit: int = 6) -> list[str]:
    seen = set()
    result = []
    for item in items:
        normalized = re.sub(r"\s+", " ", item).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def heading_sections(text: str, limit: int = 4) -> list[dict[str, str]]:
    sections = []
    current_title = ""
    current_body: list[str] = []

    def flush():
        if not current_title:
            return
        body = "\n".join(current_body).strip()
        summary = summarize_section_body(body)
        if summary:
            title = re.sub(r"^\d+[.、]\s*", "", current_title).strip()
            sections.append({"title": strip_markdown(title, 96), "summary": summary})

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            current_body = []
            if len(sections) >= limit:
                break
            continue
        if current_title:
            current_body.append(line)
    if len(sections) < limit:
        flush()
    return sections[:limit]


def summarize_section_body(body: str, limit: int = 320) -> str:
    if not body:
        return ""
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    priority_lines = []
    for prefix in ("风险：", "Risk:", "风险信号：", "Risk signal:", "已提交：", "Submitted:"):
        priority_lines.extend(line for line in lines if line.startswith(prefix))
    if priority_lines:
        return strip_markdown(" ".join(priority_lines[:2]), limit)
    paragraphs = []
    current = []
    for line in lines:
        if line.startswith(("- ", "* ", "### ")):
            continue
        current.append(line)
        if len(" ".join(current)) > 180:
            break
    if current:
        paragraphs.append(" ".join(current))
    if not paragraphs:
        bullets = extract_bullets(body, 2)
        return strip_markdown(" ".join(bullets), limit)
    return strip_markdown(" ".join(paragraphs), limit)


def parse_lens_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for match in re.finditer(r"\bL([1-9]|1[0-9])\s*-\s*L?([1-9]|1[0-9])\b", text):
        start = int(match.group(1))
        end = int(match.group(2))
        if start <= end:
            ids.update(f"L{i}" for i in range(start, end + 1))
    ids.update(re.findall(r"\bL(?:[1-9]|1[0-9])\b", text))
    ids.update(item.upper() for item in re.findall(r"\bMETA-[12]\b", text, flags=re.IGNORECASE))
    for boundary_id in LENS_NAMES["en"]:
        if boundary_id.startswith("META-"):
            continue
        if re.search(rf"\b{re.escape(boundary_id)}\b", text, flags=re.IGNORECASE):
            ids.add(boundary_id)
    if re.search(r"\bMETA\b", text) and not any(item.startswith("META-") for item in ids):
        ids.update(["META-1", "META-2"])
    return ids


def parse_lens_record_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for line in text.splitlines():
        meta = re.match(r"###\s+(META-[12])\b", line, flags=re.IGNORECASE)
        if meta:
            ids.add(meta.group(1).upper())
            continue
        boundary = re.match(r"###\s+(?:Boundary:\s*)?(.+)", line, flags=re.IGNORECASE)
        if not boundary:
            continue
        name = re.sub(r"[^a-z0-9]+", "-", boundary.group(1).strip().lower()).strip("-")
        if name in LENS_NAMES["en"] or name in LENS_NAMES["zh"]:
            ids.add(name)
    return ids


def lens_list(ids: list[str], language: str) -> str:
    names = LENS_NAMES[language]
    separator = "、" if language == "zh" else ", "
    return separator.join(f"{lens_id} {names.get(lens_id, lens_id)}" for lens_id in ids)


def lens_group_label(ids: list[str], full_group: list[str]) -> str:
    if ids == full_group:
        return f"{ids[0]}-{ids[-1]}"
    return "/".join(ids)


def coverage_strategy_bullets(scope_doc: str, lens_coverage: str, language: str, limit: int = 6) -> list[str]:
    scope_section = section_body(scope_doc, ["Lens 覆盖", "Lens Coverage"])
    scope_bullets = extract_bullets(scope_section, 5)
    enabled = parse_lens_record_ids(lens_coverage) or parse_lens_ids(scope_section)
    if not enabled:
        return unique_items(scope_bullets + lens_summary_bullets(lens_coverage, language, 4), limit)

    bullets = []
    for key, tier_label, group_ids in TIER_GROUPS:
        present = [lens_id for lens_id in group_ids if lens_id in enabled]
        if not present:
            continue
        group_label = lens_group_label(present, group_ids)
        if language == "zh":
            bullets.append(
                f"已启用 {tier_label} {TIER_NAMES[language][key]}（{group_label}）：{lens_list(present, language)}。"
            )
        else:
            bullets.append(
                f"Enabled {tier_label} {TIER_NAMES[language][key]} ({group_label}): {lens_list(present, language)}."
            )

    meta_ids = [lens_id for lens_id in ["META-1", "META-2"] if lens_id in enabled]
    if meta_ids:
        if language == "zh":
            bullets.append(f"已启用 META {TIER_NAMES[language]['meta']}：{lens_list(meta_ids, language)}。")
        else:
            bullets.append(f"Enabled META {TIER_NAMES[language]['meta']}: {lens_list(meta_ids, language)}.")

    if language == "zh":
        bullets.append("覆盖明细：quality/lens-coverage.md。")
    else:
        bullets.append("Coverage details: quality/lens-coverage.md.")
    return unique_items(bullets, limit)


def depth_coverage_bullets(depth_coverage: str, language: str, limit: int = 5) -> list[str]:
    if not depth_coverage:
        return []
    roster_gate = section_body(depth_coverage, ["Repository Roster Gate", "仓库名册门禁"])
    conclusion = section_body(depth_coverage, ["Depth Conclusion", "深度结论"])
    raw_bullets = extract_bullets(roster_gate, limit) + extract_bullets(conclusion, 2)
    focused = []
    for item in raw_bullets:
        if re.search(
            r"coverage classification|覆盖分类|discovered repos|profiles completed|missing roster|scope claim|known weak|已发现仓库|画像|缺失|范围|弱区",
            item,
            flags=re.IGNORECASE,
        ):
            focused.append(item)
    if not focused:
        match = re.search(
            r"(first[- ]pass|focused|deep[- ]complete|首轮|聚焦|深度完成)",
            depth_coverage,
            flags=re.IGNORECASE,
        )
        if match:
            prefix = "覆盖分类" if language == "zh" else "Coverage classification"
            focused.append(f"{prefix}: {match.group(1)}")
    if focused:
        focused.append(
            "深度覆盖明细：quality/depth-coverage.md。"
            if language == "zh"
            else "Depth coverage details: quality/depth-coverage.md."
        )
    return unique_items(focused, limit)


def candidate_funnel_bullets(candidate_coverage: str, language: str, limit: int = 3) -> list[str]:
    if not candidate_coverage:
        return []
    funnel = section_body(candidate_coverage, ["Candidate Funnel", "候选发现漏斗"])
    bullets = extract_bullets(funnel, limit + 2)
    focused = []
    for item in bullets:
        if re.search(r"candidate leads|submitted findings|parked|unpromoted|候选|提交|搁置|未升级", item, re.IGNORECASE):
            focused.append(item)
    if focused:
        focused.append(
            "候选漏斗明细：quality/candidate-coverage.md。"
            if language == "zh"
            else "Candidate funnel details: quality/candidate-coverage.md."
        )
    return unique_items(focused, limit)


def lens_summary_bullets(text: str, language: str, limit: int = 4) -> list[str]:
    records = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        if line.startswith("### "):
            if current:
                records.append(current)
            current = {"title": line[4:].strip(), "candidates": 0, "uncovered": ""}
            continue
        if not current:
            continue
        candidate = re.search(r"候选数[：:]\s*(\d+)", line)
        if candidate:
            current["candidates"] = int(candidate.group(1))
        if "未覆盖" in line and ("：" in line or ":" in line):
            current["uncovered"] = strip_markdown(re.split(r"[：:]", line, maxsplit=1)[1], 120)
    if current:
        records.append(current)
    if not records:
        return extract_bullets(text, limit)

    uncovered = unique_items([str(r.get("uncovered", "")) for r in records if r.get("uncovered")], 2)
    if language == "zh":
        bullets = ["覆盖记录已单独保存在 quality/lens-coverage.md。"]
        if uncovered:
            bullets.append("主要未覆盖：" + "；".join(uncovered))
        return bullets[:limit]
    bullets = ["Coverage records are available in quality/lens-coverage.md."]
    if uncovered:
        bullets.append("Main uncovered areas: " + "; ".join(uncovered))
    return bullets[:limit]


def split_count(counter: dict, key: str) -> int:
    return int(counter.get(key, 0) or 0)


def load_findings(root: Path, index_payload: dict) -> list[dict]:
    findings = []
    for item in index_payload.get("findings", []):
        if not isinstance(item, dict):
            continue
        path = root / str(item.get("path", ""))
        text = read_text(path)
        meta = parse_frontmatter(text)
        merged = dict(item)
        merged["lens"] = as_list(meta.get("lens", item.get("lens", [])))
        merged["title"] = item.get("title") or first_heading(text) or item.get("id", "")
        merged["conclusion"] = strip_markdown(section_body(text, ["结论", "Conclusion"]), 320)
        merged["impact"] = strip_markdown(section_body(text, ["影响范围", "Impact Scope"]), 260)
        merged["evidence"] = strip_markdown(section_body(text, ["代码证据", "Code Evidence"]), 260)
        merged["false_positive"] = strip_markdown(section_body(text, ["误报排查", "False-positive Review"]), 220)
        merged["fix_boundary"] = strip_markdown(section_body(text, ["修复边界", "Fix Boundary"]), 220)
        merged["verification"] = strip_markdown(section_body(text, ["建议验证命令", "Suggested Verification Commands"]), 220)
        findings.append(merged)
    return findings


def parse_metadata(readme: str, versions: str, scope_doc: str, language: str) -> dict:
    label = LABELS[language]
    data = {
        "date": label["not_specified"],
        "analyst": label["not_specified"],
        "method": "static-analysis",
        "scope": label["not_specified"],
        "status": label["not_specified"],
        "version": label["not_specified"],
    }
    patterns = {
        "date": [r"(?:分析时间|Analysis date)[：:]\s*`?([^`\n]+)`?"],
        "analyst": [r"(?:分析人|Analyst)[：:]\s*`?([^`\n]+)`?"],
        "method": [r"(?:分析方法|Method)[：:]\s*`?([^`\n]+)`?"],
        "scope": [r"(?:分析范围|Scope)[：:]\s*`?([^`\n]+)`?"],
        "status": [r"(?:当前状态|Status)[：:]\s*`?([^`\n]+)`?"],
    }
    combined = "\n".join([readme, scope_doc])
    for key, pats in patterns.items():
        for pattern in pats:
            m = re.search(pattern, combined, flags=re.IGNORECASE)
            if m:
                data[key] = strip_markdown(m.group(1), 120)
                break
    if versions:
        version_records = audit_scope_contract.parse_repository_versions(versions)
        complete = 0
        total = len(version_records)
        for record in version_records:
            if not any(audit_scope_contract.version_value_missing(record.get(key, "")) for key in ("audit_branch", "commit", "dirty")):
                complete += 1
        if total:
            data["version"] = f"{complete}/{total}"
    if data["date"] == label["not_specified"]:
        data["date"] = date.today().isoformat()
    return data


def load_audit_scope_records(root: Path, versions: str, repo_counter: Counter) -> tuple[list[dict[str, str]], dict[str, int]]:
    manifest_path = root / audit_scope_contract.AUDIT_SCOPE_INDEX
    if manifest_path.is_file():
        try:
            payload = json.loads(read_text(manifest_path) or "{}")
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict):
            manifest_records = audit_scope_contract.scope_records_from_payload(payload)
            if manifest_records:
                records = [
                    {
                        "repository": str(row.get("repository", "")),
                        "audit_branch": str(row.get("audit_branch", "")),
                        "commit": str(row.get("commit", "")),
                        "dirty": str(row.get("dirty", "")),
                    }
                    for row in manifest_records
                ]
                bug_counts = {
                    str(row["repository"]): audit_scope_contract.safe_int(row.get("submitted_bugs", 0))
                    for row in manifest_records
                    if row.get("repository")
                }
                return records, bug_counts
    records = audit_scope_contract.parse_repository_versions(versions)
    bug_counts = {
        record["repository"]: audit_scope_contract.bug_count_for_repo(record["repository"], repo_counter)
        for record in records
        if record.get("repository")
    }
    return records, bug_counts


def top_items(counter: Counter, limit: int = 6) -> list[tuple[str, int]]:
    return [(str(k), int(v)) for k, v in counter.most_common(limit) if k]


def pill(text: str, kind: str = "neutral") -> str:
    return f'<span class="pill {kind}">{esc(text)}</span>'


def display_scope(scope: str, repo_counter: Counter, fallback: str) -> str:
    repo_names = [name for name, _ in repo_counter.most_common() if name]
    if repo_names:
        if scope == fallback or "/" in scope or "\\" in scope:
            return ", ".join(repo_names[:4]) + (f" +{len(repo_names) - 4}" if len(repo_names) > 4 else "")
    if "/" not in scope and "\\" not in scope:
        return scope
    parts = [part for part in re.split(r"[,，\s]+", scope) if part]
    shortened = []
    for part in parts:
        if "/" in part or "\\" in part:
            shortened.append(Path(part).name or part.rstrip("/\\").split("/")[-1])
        else:
            shortened.append(part)
    result = " ".join(x for x in shortened if x)
    return result or fallback


def report_subject(root: Path, scope: str, repo_counter: Counter, fallback: str, language: str) -> str:
    repo_names = [name for name, _ in repo_counter.most_common() if name]
    if len(repo_names) == 1:
        return repo_names[0]
    if 1 < len(repo_names) <= 3:
        return " + ".join(repo_names)
    if len(repo_names) > 3:
        if language == "zh":
            return f"{repo_names[0]} 等 {len(repo_names)} 仓"
        return f"{repo_names[0]} + {len(repo_names) - 1} repos"

    scope_label = display_scope(scope, repo_counter, fallback)
    if scope_label and scope_label != fallback:
        return scope_label

    package_name = root.parent.name if root.name == "submit" else root.name
    package_name = re.sub(r"-bug-audit(?:-.+)?$", "", package_name)
    return package_name or fallback


def meta_token(name: str, value: Any) -> str:
    return f'<span class="meta-token"><span>{esc(name)}</span><strong>{esc(value)}</strong></span>'


def metric_tile(label: str, value: Any, sub: str = "", kind: str = "") -> str:
    return f"""
    <div class="metric-tile {kind}">
      <div class="metric-label">{esc(label)}</div>
      <div class="metric-value">{esc(value)}</div>
      <div class="metric-sub">{esc(sub)}</div>
    </div>
    """


def priority_cells(priority: dict, label: dict) -> str:
    names = {
        "P1": label["critical"],
        "P2": label["high"],
        "P3": label["medium"],
        "P4": label["low"],
    }
    cells = []
    for item in PRIORITY_ORDER:
        cells.append(
            f"""
            <div class="priority-cell {item.lower()}">
              <span>{esc(item)}</span>
              <strong>{split_count(priority, item)}</strong>
              <em>{esc(names[item])}</em>
            </div>
            """
        )
    return "".join(cells)


def bar_list(title: str, rows: list[tuple[str, int]], total: int, empty_label: str) -> str:
    if not rows:
        rows = [(empty_label, 0)]
    items = []
    max_value = max([value for _, value in rows] + [1])
    for name, value in rows:
        width = 6 if max_value == 0 else max(6, round((value / max_value) * 100))
        items.append(
            f"""
            <div class="bar-row">
              <div class="bar-head"><span>{esc(name)}</span><strong>{value}</strong></div>
              <div class="bar-track"><span style="width:{width}%"></span></div>
            </div>
            """
        )
    return f"""
    <section class="panel">
      <div class="panel-title">{esc(title)}</div>
      <div class="bar-list">{''.join(items)}</div>
    </section>
    """


def bullet_panel(title: str, bullets: list[str], fallback: str) -> str:
    if not bullets:
        bullets = [fallback]
    body = "".join(f"<li>{esc(item)}</li>" for item in bullets[:6])
    return f"""
    <section class="panel">
      <div class="panel-title">{esc(title)}</div>
      <ul class="insight-list">{body}</ul>
    </section>
    """


def insight_panel(title: str, rows: list[dict[str, str]], fallback: str) -> str:
    if not rows:
        rows = [{"title": fallback, "summary": ""}]
    items = []
    for row in rows[:4]:
        summary = f"<p>{esc(row.get('summary', ''))}</p>" if row.get("summary") else ""
        items.append(
            f"""
            <article class="insight-item">
              <h3>{esc(row.get("title", ""))}</h3>
              {summary}
            </article>
            """
        )
    return f"""
    <section class="panel insight-stack">
      <div class="panel-title">{esc(title)}</div>
      <div class="insight-items">{''.join(items)}</div>
    </section>
    """


def render_findings(findings: list[dict], label: dict) -> str:
    if not findings:
        return f'<div class="empty-state">{esc(label["no_findings"])}</div>'
    cards = []
    for item in findings:
        priority = str(item.get("priority", ""))
        repo = str(item.get("repo", ""))
        category = str(item.get("category", ""))
        confidence = str(item.get("confidence", ""))
        fix_risk = str(item.get("fix_risk", ""))
        lens = " ".join(as_list(item.get("lens", [])))
        search_text = " ".join(
            [
                str(item.get("id", "")),
                str(item.get("title", "")),
                repo,
                str(item.get("module", "")),
                category,
                confidence,
                fix_risk,
                lens,
            ]
        ).lower()
        cards.append(
            f"""
            <article class="finding-card"
              data-priority="{esc(priority)}"
              data-repo="{esc(repo)}"
              data-category="{esc(category)}"
              data-confidence="{esc(confidence)}"
              data-fix-risk="{esc(fix_risk)}"
              data-lens="{esc(lens)}"
              data-search="{esc(search_text)}">
              <details>
                <summary>
                  <span class="finding-main">
                    {pill(priority, priority.lower())}
                    <span class="bug-id">{esc(item.get("id", ""))}</span>
                    <span class="finding-title">{esc(item.get("title", ""))}</span>
                  </span>
                  <span class="finding-meta">{esc(repo)} · {esc(category)} · {esc(confidence)}</span>
                </summary>
                <div class="finding-detail">
                  <div><h4>{esc(label["conclusion"])}</h4><p>{esc(item.get("conclusion") or "unconfirmed")}</p></div>
                  <div><h4>{esc(label["impact"])}</h4><p>{esc(item.get("impact") or "unconfirmed")}</p></div>
                  <div><h4>{esc(label["evidence"])}</h4><p>{esc(item.get("evidence") or "unconfirmed")}</p></div>
                  <div><h4>{esc(label["false_positive"])}</h4><p>{esc(item.get("false_positive") or "unconfirmed")}</p></div>
                  <div><h4>{esc(label["fix_boundary"])}</h4><p>{esc(item.get("fix_boundary") or "unconfirmed")}</p></div>
                  <div><h4>{esc(label["verification"])}</h4><p>{esc(item.get("verification") or "unconfirmed")}</p></div>
                  <div class="source-path">{esc(label["open_markdown"])}: <code>{esc(item.get("path", ""))}</code></div>
                </div>
              </details>
            </article>
            """
        )
    return "".join(cards)


def render_filter_group(name: str, key: str, values: list[str], label_all: str) -> str:
    buttons = [f'<button class="filter-chip active" data-filter="{esc(key)}" data-value="">{esc(label_all)}</button>']
    for value in values[:12]:
        buttons.append(
            f'<button class="filter-chip" data-filter="{esc(key)}" data-value="{esc(value)}">{esc(value)}</button>'
        )
    return f"""
    <div class="filter-group">
      <span>{esc(name)}</span>
      <div>{''.join(buttons)}</div>
    </div>
    """


def render_repo_cards(findings: list[dict], repo_counter: Counter, label: dict) -> str:
    if not repo_counter:
        return f'<article class="repo-card"><h3>{esc(label["not_specified"])}</h3><div class="mini">0 Bugs</div></article>'
    cards = []
    for repo, count in top_items(repo_counter, 12):
        scoped = [item for item in findings if str(item.get("repo", "")) == repo]
        prio = Counter(str(item.get("priority", "")) for item in scoped if item.get("priority"))
        cats = Counter(str(item.get("category", "")) for item in scoped if item.get("category"))
        top_category = cats.most_common(1)[0][0] if cats else label["not_specified"]
        p_summary = " · ".join(f"{name}:{prio.get(name, 0)}" for name in PRIORITY_ORDER if prio.get(name, 0))
        if not p_summary:
            p_summary = "P1-P4:0"
        cards.append(
            f"""
            <article class="repo-card">
              <h3>{esc(repo)}</h3>
              <div class="mini">{esc(count)} Bugs · {esc(p_summary)}</div>
              <div class="mini">{esc(label["category"])}: {esc(top_category)}</div>
            </article>
            """
        )
    return "".join(cards)


def render_analysis_scope_table(
    version_records: list[dict[str, str]],
    repo_counter: Counter,
    label: dict,
    repo_bug_counts: dict[str, int] | None = None,
) -> str:
    records = version_records
    if not records:
        records = [
            {"repository": repo, "audit_branch": "", "commit": "", "dirty": ""}
            for repo, _ in top_items(repo_counter, 999)
        ]
    if not records:
        records = [{"repository": label["not_specified"], "audit_branch": "", "commit": "", "dirty": ""}]

    body_rows = []
    repo_bug_counts = repo_bug_counts or {}
    for record in records:
        repo = record.get("repository", "").strip() or label["not_specified"]
        bug_count = repo_bug_counts.get(repo, audit_scope_contract.bug_count_for_repo(repo, repo_counter))
        branch = record.get("audit_branch", "").strip() or label["not_specified"]
        commit = record.get("commit", "").strip() or label["not_specified"]
        dirty = record.get("dirty", "").strip() or label["not_specified"]
        body_rows.append(
            f"""
            <tr>
              <td><strong>{esc(repo)}</strong></td>
              <td><code>{esc(branch)}</code></td>
              <td><code>{esc(commit)}</code></td>
              <td>{esc(dirty)}</td>
              <td class="number-cell">{esc(bug_count)}</td>
            </tr>
            """
        )
    return f"""
    <div class="scope-table-wrap">
      <table class="scope-table">
        <thead>
          <tr>
            <th>{esc(label["repo"])}</th>
            <th>{esc(label["audit_branch"])}</th>
            <th>{esc(label["commit"])}</th>
            <th>{esc(label["dirty"])}</th>
            <th>{esc(label["submitted_bugs"])}</th>
          </tr>
        </thead>
        <tbody>{''.join(body_rows)}</tbody>
      </table>
    </div>
    """


def package_entry_exists(root: Path, name: str) -> bool:
    target = root / name.rstrip("/")
    return target.is_dir() if name.endswith("/") else target.is_file()


def render_package_guide(root: Path, label: dict, output_name: str) -> str:
    files = [
        (output_name, label["interactive_report"], True, "primary"),
        ("README.md", label["summary"], package_entry_exists(root, "README.md"), ""),
        ("findings/", label["bug_records"], package_entry_exists(root, "findings/"), ""),
        ("indexes/", label["machine_data"], package_entry_exists(root, "indexes/"), ""),
        ("knowledge/", label["repo_cognition"], package_entry_exists(root, "knowledge/"), ""),
        ("quality/", label["scope_gates"], package_entry_exists(root, "quality/"), ""),
        ("standards/", label["schema"], package_entry_exists(root, "standards/"), ""),
        ("audit-overview.png", label["static_cover"], package_entry_exists(root, "audit-overview.png"), ""),
    ]
    cards = "".join(
        f"<div class=\"{'file-card ' + esc(kind) if kind else 'file-card'}\"><strong>{esc(name)}</strong><span>{esc(desc)}</span></div>"
        for name, desc, exists, kind in files
        if exists
    )
    return f"""
    <section id="package-guide" class="section-card">
      <div class="section-heading">
        <div><p>{esc(label["guide_eyebrow"])}</p><h2>{esc(label["package_files"])}</h2></div>
      </div>
      <div class="file-grid">{cards}</div>
      <div class="reading-order">
        <strong>{esc(label["reading_order"])}</strong>
        <span>{esc(label["hero_metrics"])}</span><span>{esc(label["p1p2_findings"])}</span><span>{esc(label["architecture_reading"])}</span><span>{esc(label["knowledge_gates"])}</span>
      </div>
    </section>
    """


def render_html(root: Path, language: str, output_name: str) -> str:
    label = LABELS[language]
    index_path = root / "indexes/findings.generated.json"
    index_payload = json.loads(read_text(index_path) or "{}")
    findings = load_findings(root, index_payload)
    readme = read_text(root / "README.md")
    versions = read_text(root / "quality/repository-versions.md")
    scope_doc = read_text(root / "quality/submission-scope.md")
    lens_coverage = read_text(root / "quality/lens-coverage.md")
    depth_coverage = read_text(root / "quality/depth-coverage.md")
    candidate_coverage = read_text(root / CANDIDATE_COVERAGE)
    arch = read_text(root / "knowledge/architecture-design-review.md")
    risk_paths = read_text(root / "knowledge/risk-paths.md")
    relationship = read_text(root / "knowledge/repo-relationship-map.md")
    metadata = parse_metadata(readme, versions, scope_doc, language)

    total = int(index_payload.get("total", len(findings)) or 0)
    priority = index_payload.get("priority", {})
    p1p2 = split_count(priority, "P1") + split_count(priority, "P2")
    repos = index_payload.get("repo", {})
    confidence = index_payload.get("confidence", {})
    categories = Counter(index_payload.get("category", {}))
    risk_type_count = len([key for key, value in categories.items() if key and value])
    infra = Counter(index_payload.get("infra_domains", {}))
    fix_risk = Counter(index_payload.get("fix_risk", {}))
    repo_counter = Counter(repos)
    version_records, repo_bug_counts = load_audit_scope_records(root, versions, repo_counter)
    analysis_repo_counter = Counter(
        {record["repository"]: repo_bug_counts.get(record["repository"], 0) for record in version_records}
    ) or repo_counter
    repo_count = len(version_records) if version_records else len([key for key, value in repos.items() if key and value])
    family = Counter(index_payload.get("issue_family", {}))
    project_title = f"{report_subject(root, metadata['scope'], analysis_repo_counter, label['not_specified'], language)} {label['title_suffix']}"
    scope_label = display_scope(metadata["scope"], analysis_repo_counter, label["not_specified"])

    quality_gate_bullets = unique_items(
        extract_bullets(section_body(scope_doc, ["收录", "Included"]), 4)
        + extract_bullets(section_body(scope_doc, ["质量评估", "Quality Evaluation"]), 4)
        + candidate_funnel_bullets(candidate_coverage, language, 3),
        5,
    )
    coverage_bullets = coverage_strategy_bullets(scope_doc, lens_coverage, language, 6)
    depth_bullets = depth_coverage_bullets(depth_coverage, language, 5)
    boundary_bullets = unique_items(
        extract_bullets(section_body(scope_doc, ["排除", "Exclusions"]), 4)
        + extract_bullets(section_body(scope_doc, ["当前状态", "Current Status"]), 2),
        5,
    )
    arch_sections = heading_sections(arch, 4)
    risk_sections = heading_sections(risk_paths, 4)
    relationship_bullets = extract_bullets(relationship, 5)
    knowledge_focus_sections = risk_sections[:3] or arch_sections[:3]

    all_repos = [name for name, _ in top_items(repo_counter, 12)]
    all_categories = [name for name, _ in top_items(categories, 12)]
    all_confidence = [name for name, _ in top_items(Counter(confidence), 12)]
    all_fix_risk = [name for name, _ in top_items(fix_risk, 12)]
    priority_attrs = " ".join(
        f'data-priority-{p.lower()}="{split_count(priority, p)}"' for p in PRIORITY_ORDER
    )

    return f"""<!doctype html>
<html lang="{esc(language)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(project_title)}</title>
  <style>
    :root {{
      --bg:#F4F6F4; --paper:#FFFFFF; --ink:#111514; --muted:#59635F; --soft:#93A09A;
      --line:#DDE4DF; --accent:#0F766E; --accent-2:#22C1A7; --surface:#F8FAF8; --slate:#475569; --slate-soft:#E7ECF2;
      --p1-bg:#FEE2E2; --p1-fg:#DC2626; --p2-bg:#FEF3C7; --p2-fg:#D97706;
      --p3-bg:#DBEAFE; --p3-fg:#2563EB; --p4-bg:#F1F5F9; --p4-fg:#64748B;
      --mono:"JetBrains Mono","IBM Plex Mono","SFMono-Regular",Consolas,monospace;
      --sans:Geist,Satoshi,"Avenir Next","PingFang SC","Noto Sans CJK SC",sans-serif;
    }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-padding-top:82px; }}
    body {{
      margin:0; color:var(--ink); font-family:var(--sans);
      background:
        linear-gradient(90deg,rgba(15,23,42,.03) 1px,transparent 1px) 0 0/44px 44px,
        linear-gradient(180deg,rgba(15,23,42,.026) 1px,transparent 1px) 0 0/44px 44px,
        linear-gradient(180deg,#F8F8F5 0%,#EEF3EF 100%);
    }}
    a {{ color:inherit; }}
    .shell {{ max-width:1220px; margin:0 auto; padding:34px 28px 34px; }}
    .top-nav {{ position:sticky; top:0; z-index:20; backdrop-filter:blur(18px); background:linear-gradient(90deg,rgba(16,68,59,.96) 0%,rgba(15,118,110,.94) 58%,rgba(18,130,113,.92) 100%); border-bottom:1px solid rgba(34,193,167,.38); color:white; box-shadow:0 14px 40px -34px rgba(15,23,42,.72); }}
    .top-nav-inner {{ max-width:1220px; margin:0 auto; padding:10px 28px; display:grid; grid-template-columns:minmax(260px,1fr) auto; gap:24px; align-items:center; }}
    .brand-mini {{ display:flex; align-items:center; color:white; min-width:0; }}
    .brand-text {{ display:grid; gap:1px; min-width:0; }}
    .brand-text strong {{ color:white; font-size:12px; line-height:1; font-weight:900; letter-spacing:.04em; }}
    .brand-text span {{ color:rgba(232,246,241,.68); font-size:11px; line-height:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
    .nav-links {{ display:flex; gap:7px; flex-wrap:nowrap; }}
    .nav-links a, .filter-chip, .quick-toggle, .pager-button {{ border:1px solid rgba(17,21,20,.12); background:rgba(255,255,255,.78); color:var(--muted); border-radius:999px; padding:7px 10px; font-size:12px; font-weight:700; text-decoration:none; cursor:pointer; box-shadow:0 1px 0 rgba(255,255,255,.8) inset; white-space:nowrap; }}
    .nav-links a {{ color:rgba(241,250,247,.74); background:rgba(255,255,255,.08); border-color:rgba(255,255,255,.14); box-shadow:none; }}
    .nav-links a:hover {{ border-color:rgba(34,193,167,.46); color:white; background:rgba(230,245,240,.14); }}
    .filter-chip:hover, .filter-chip.active, .quick-toggle.active {{ border-color:rgba(15,118,110,.34); color:var(--accent); background:#ECFDF5; }}
    .pager-button:hover:not(:disabled) {{ border-color:rgba(15,118,110,.34); color:var(--accent); background:#ECFDF5; }}
    .hero {{ position:relative; overflow:hidden; border:1px solid rgba(15,118,110,.22); border-radius:8px; background:rgba(255,255,255,.96); box-shadow:0 28px 80px -34px rgba(15,118,110,.35),0 18px 42px -28px rgba(17,21,20,.26),inset 0 1px 0 rgba(255,255,255,.72); }}
    .hero::before {{ content:""; position:absolute; left:0; top:0; right:0; height:4px; background:linear-gradient(90deg,#0B4F49 0%,var(--accent) 42%,var(--accent-2) 100%); }}
    .hero-inner {{ position:relative; z-index:1; padding:32px 36px 30px; }}
    .hero-layout {{ display:grid; gap:20px; }}
    .hero-title-row {{ display:grid; gap:14px; align-content:start; max-width:980px; }}
    .eyebrow {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
    .badge-dark {{ display:inline-flex; background:#213531; color:white; border-radius:999px; padding:6px 11px; font-size:12px; line-height:1; font-weight:800; letter-spacing:.04em; }}
    .source-badge {{ color:var(--accent); font-size:12px; font-weight:800; }}
    h1 {{ margin:0; font-size:44px; line-height:1.04; letter-spacing:0; max-width:980px; }}
    .hero-note {{ margin:0; color:var(--muted); font-size:13px; line-height:1.55; max-width:820px; }}
    .meta-strip {{ display:flex; flex-wrap:wrap; gap:8px 14px; margin-top:auto; padding-top:18px; border-top:1px solid var(--line); color:var(--muted); font-size:12px; line-height:1.45; }}
    .meta-token {{ display:inline-flex; align-items:baseline; gap:5px; max-width:100%; }}
    .meta-token + .meta-token::before {{ content:""; width:3px; height:3px; border-radius:999px; background:#CBD5E1; margin-right:6px; transform:translateY(-1px); flex:0 0 auto; }}
    .meta-token span {{ color:var(--soft); font-weight:800; letter-spacing:.03em; text-transform:uppercase; white-space:nowrap; }}
    .meta-token strong {{ color:var(--ink); font-weight:700; overflow-wrap:anywhere; }}
    .hero-dashboard {{ border:1px solid var(--line); border-radius:8px; background:linear-gradient(180deg,#FFFFFF 0%,#F7FAF8 100%); padding:10px; display:grid; grid-template-columns:minmax(150px,176px) minmax(0,1fr); gap:10px; align-items:stretch; box-shadow:inset 0 0 0 1px rgba(255,255,255,.8); }}
    .dashboard-side {{ display:grid; grid-template-rows:auto auto; gap:8px; min-width:0; }}
    .metric-total {{ position:relative; min-height:124px; border:1px solid rgba(15,118,110,.28); border-radius:8px; padding:14px 16px; background:linear-gradient(145deg,#FFFFFF 0%,#F8FAFC 62%,#EEF2F7 100%); color:var(--ink); overflow:hidden; display:flex; flex-direction:column; justify-content:space-between; gap:12px; box-shadow:inset 0 1px 0 rgba(255,255,255,.86); }}
    .metric-total::before {{ content:""; position:absolute; left:0; top:0; bottom:0; z-index:1; width:3px; background:linear-gradient(180deg,var(--accent),var(--accent-2)); }}
    .metric-total::after {{ content:""; position:absolute; right:-38px; bottom:-48px; z-index:0; width:116px; height:116px; border:1px solid rgba(15,118,110,.14); transform:rotate(28deg); }}
    .metric-tile-row {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:7px; }}
    .metric-tile {{ min-height:56px; border:1px solid #E9F0EB; border-radius:8px; padding:9px 11px 9px 13px; background:#FAFCFA; display:grid; grid-template-columns:minmax(0,1fr) auto; grid-template-rows:auto auto; align-items:center; gap:1px 10px; position:relative; overflow:hidden; }}
    .metric-tile::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:2px; background:#DDE4DF; }}
    .metric-tile.metric-focus {{ border-color:rgba(15,118,110,.32); background:#F3FBF8; box-shadow:inset 0 0 0 1px rgba(34,193,167,.08); }}
    .metric-tile.metric-focus::before {{ background:var(--accent); }}
    .metric-label {{ font-size:11px; color:inherit; opacity:.74; font-weight:850; }}
    .metric-value {{ grid-column:2; grid-row:1 / 3; font-family:var(--mono); font-size:25px; line-height:1; font-weight:900; font-variant-numeric:tabular-nums; }}
    .metric-total .metric-label, .metric-total .metric-sub {{ position:relative; z-index:2; }}
    .metric-total .metric-value {{ position:absolute; inset:0; z-index:1; width:100%; display:flex; align-items:center; justify-content:center; grid-column:auto; grid-row:auto; font-size:58px; text-align:center; }}
    .metric-sub {{ font-size:11px; color:inherit; opacity:.62; margin-top:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .metric-tile.p1 .metric-value {{ color:var(--p1-fg); }} .metric-tile.p2 .metric-value {{ color:var(--p2-fg); }}
    .metric-tile.p3 .metric-value {{ color:var(--p3-fg); }} .metric-tile.p4 .metric-value {{ color:var(--p4-fg); }}
    .priority-cells {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:7px; }}
    .priority-cell {{ min-height:56px; border-radius:8px; background:#F7FAF8; border:1px solid #E9F0EB; padding:9px 10px 9px 11px; display:grid; grid-template-columns:minmax(24px,.7fr) minmax(28px,1fr) minmax(24px,.7fr); gap:5px; align-items:center; position:relative; overflow:hidden; }}
    .priority-cell::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:2px; background:#CBD5E1; }}
    .priority-cell.p1::before {{ background:var(--p1-fg); }} .priority-cell.p2::before {{ background:var(--p2-fg); }}
    .priority-cell.p3::before {{ background:var(--p3-fg); }} .priority-cell.p4::before {{ background:var(--p4-fg); }}
    .priority-cell span {{ font-family:var(--mono); font-size:11px; font-weight:800; color:var(--muted); }}
    .priority-cell strong {{ justify-self:center; min-width:28px; text-align:center; font-family:var(--mono); font-size:25px; line-height:1; font-weight:900; font-variant-numeric:tabular-nums; }}
    .priority-cell em {{ justify-self:end; font-style:normal; color:var(--muted); font-size:11px; white-space:nowrap; }}
    .priority-cell.p1 strong {{ color:var(--p1-fg); }} .priority-cell.p2 strong {{ color:var(--p2-fg); }}
    .priority-cell.p3 strong {{ color:var(--p3-fg); }} .priority-cell.p4 strong {{ color:var(--p4-fg); }}
    .section-card {{ margin-top:34px; background:transparent; border:0; border-radius:0; padding:0; scroll-margin-top:82px; }}
    .section-heading {{ display:flex; justify-content:space-between; gap:20px; align-items:end; margin-bottom:16px; }}
    .section-heading p {{ margin:0; font-size:12px; font-weight:800; letter-spacing:.04em; text-transform:uppercase; color:var(--accent); }}
    .section-card.tone-architecture .section-heading p {{ color:var(--slate); }}
    .section-heading h2 {{ margin:4px 0 0; font-size:24px; letter-spacing:0; }}
    .panel-grid-3 {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }}
    .panel-grid-2 {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
    .panel {{ background:#FFF; border:1px solid var(--line); border-radius:8px; padding:16px; box-shadow:0 10px 28px -22px rgba(10,10,10,.2); }}
    .tone-architecture .panel {{ border-color:#D8E0E8; }}
    .panel-title {{ font-weight:800; margin-bottom:12px; }}
    .bar-row {{ margin-top:11px; }}
    .bar-head {{ display:flex; justify-content:space-between; gap:12px; font-size:13px; color:var(--muted); }}
    .bar-head strong {{ font-family:var(--mono); color:var(--ink); }}
    .bar-track {{ height:8px; background:#F1F5F9; border-radius:999px; overflow:hidden; margin-top:6px; }}
    .bar-track span {{ display:block; height:100%; background:linear-gradient(90deg,var(--accent),var(--accent-2)); border-radius:inherit; }}
    .insight-list {{ margin:0; padding-left:18px; color:var(--muted); line-height:1.55; font-size:13px; }}
    .insight-list li + li {{ margin-top:8px; }}
    .insight-stack {{ padding:0; overflow:hidden; }}
    .insight-stack .panel-title {{ margin:0; padding:16px 16px 0; }}
    .insight-items {{ display:grid; }}
    .insight-item {{ padding:14px 16px 15px; border-top:1px solid var(--line); }}
    .insight-stack .panel-title + .insight-items .insight-item:first-child {{ border-top:0; }}
    .insight-item h3 {{ margin:0 0 6px; font-size:15px; line-height:1.35; display:flex; gap:9px; align-items:baseline; }}
    .insight-item h3::before {{ content:""; width:7px; height:7px; border-radius:999px; background:var(--accent); flex:0 0 auto; transform:translateY(-1px); }}
    .tone-architecture .insight-item h3::before {{ background:var(--slate); }}
    .insight-item p {{ margin:0; color:var(--muted); font-size:13px; line-height:1.55; }}
    .scope-table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:8px; background:#FFF; box-shadow:0 10px 28px -22px rgba(10,10,10,.18); }}
    .scope-table {{ width:100%; border-collapse:collapse; min-width:760px; }}
    .scope-table th, .scope-table td {{ padding:11px 13px; border-bottom:1px solid var(--line); text-align:left; font-size:13px; vertical-align:top; }}
    .scope-table th {{ color:var(--soft); font-size:11px; text-transform:uppercase; letter-spacing:.04em; background:#F8FAFC; }}
    .scope-table tr:last-child td {{ border-bottom:0; }}
    .scope-table code {{ overflow-wrap:anywhere; }}
    .scope-table .number-cell {{ font-family:var(--mono); font-weight:900; font-variant-numeric:tabular-nums; text-align:right; }}
    .repo-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }}
    .repo-depth-panel {{ margin-bottom:12px; }}
    .repo-card {{ border:1px solid var(--line); border-radius:8px; padding:14px; background:#FFF; box-shadow:0 10px 28px -22px rgba(10,10,10,.18); }}
    .repo-card h3 {{ margin:0 0 8px; font-size:16px; }}
    .repo-card .mini {{ color:var(--muted); font-size:12px; line-height:1.45; }}
    .filters {{ display:grid; gap:10px; margin-bottom:14px; }}
    .search-row {{ display:flex; gap:10px; }}
    .search-row input {{ flex:1; border:1px solid var(--line); border-radius:8px; padding:12px 14px; font:inherit; background:#FFF; }}
    .filter-group {{ display:grid; grid-template-columns:110px minmax(0,1fr); gap:10px; align-items:start; }}
    .filter-group > span {{ font-size:12px; font-weight:800; color:var(--soft); padding-top:8px; }}
    .filter-group div {{ display:flex; gap:8px; flex-wrap:wrap; }}
    .results-toolbar {{ display:flex; justify-content:space-between; align-items:center; gap:14px; margin:2px 0 14px; padding:10px 12px; border:1px solid var(--line); border-radius:8px; background:rgba(255,255,255,.86); box-shadow:0 10px 28px -24px rgba(10,10,10,.18); }}
    .result-status {{ color:var(--muted); font-size:12px; font-weight:800; font-variant-numeric:tabular-nums; }}
    .pager {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; color:var(--soft); font-size:12px; font-weight:800; }}
    .pager select {{ border:1px solid var(--line); border-radius:999px; padding:7px 28px 7px 10px; background:#FFF; color:var(--muted); font:inherit; font-size:12px; font-weight:800; }}
    .pager-button {{ padding-inline:12px; }}
    .pager-button:disabled {{ opacity:.42; cursor:not-allowed; }}
    .page-status {{ min-width:48px; text-align:center; color:var(--muted); font-family:var(--mono); font-size:12px; font-weight:800; }}
    .finding-list-window {{ display:grid; gap:10px; }}
    .finding-card {{ border:1px solid var(--line); border-radius:8px; background:#FFF; margin-top:0; overflow:hidden; box-shadow:0 10px 28px -22px rgba(10,10,10,.18); }}
    .finding-card[hidden] {{ display:none; }}
    .finding-card summary {{ cursor:pointer; list-style:none; padding:14px 16px; display:grid; grid-template-columns:minmax(0,1fr) auto; gap:16px; align-items:center; }}
    .finding-card summary::-webkit-details-marker {{ display:none; }}
    .finding-main {{ display:flex; gap:10px; align-items:center; min-width:0; }}
    .bug-id {{ font-family:var(--mono); font-weight:800; font-size:13px; white-space:nowrap; }}
    .finding-title {{ font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .finding-meta {{ color:var(--muted); font-size:12px; white-space:nowrap; justify-self:end; text-align:right; }}
    .finding-detail {{ border-top:1px solid var(--line); padding:16px; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; color:var(--muted); font-size:13px; line-height:1.5; }}
    .finding-detail h4 {{ margin:0 0 4px; color:var(--ink); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
    .finding-detail p {{ margin:0; }}
    .source-path {{ grid-column:1/-1; font-size:12px; background:#F8FAFC; border-radius:8px; padding:10px; }}
    code, .mono {{ font-family:var(--mono); }}
    .pill {{ display:inline-flex; border-radius:999px; padding:4px 8px; font-family:var(--mono); font-size:11px; font-weight:800; line-height:1; }}
    .pill.p1 {{ background:var(--p1-bg); color:var(--p1-fg); }} .pill.p2 {{ background:var(--p2-bg); color:var(--p2-fg); }}
    .pill.p3 {{ background:var(--p3-bg); color:var(--p3-fg); }} .pill.p4 {{ background:var(--p4-bg); color:var(--p4-fg); }}
    .pill.neutral {{ background:#F1F5F9; color:#64748B; }}
    .file-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; align-items:stretch; }}
    .file-card {{ min-height:96px; border:1px solid var(--line); border-radius:8px; padding:14px; background:#FFF; display:grid; align-content:start; gap:5px; }}
    .file-card.primary {{ border-color:rgba(15,118,110,.34); background:#F3FBF8; }}
    .file-card span {{ color:var(--muted); font-size:12px; }}
    .reading-order {{ margin-top:14px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; color:var(--muted); font-size:13px; }}
    .reading-order span {{ border:1px dashed var(--line); border-radius:999px; padding:6px 10px; background:#FFF; }}
    .report-footer {{ margin-top:24px; border-top:1px solid var(--line); padding:16px 0 0; color:var(--muted); display:grid; grid-template-columns:minmax(0,1fr) auto minmax(0,1fr); gap:12px; align-items:start; font-size:12px; line-height:1.45; }}
    .report-footer span:nth-child(2) {{ justify-self:center; }}
    .report-footer span:nth-child(3) {{ justify-self:end; text-align:right; }}
    .report-footer strong {{ color:var(--ink); }}
    .report-footer a {{ color:var(--accent); font-weight:800; text-decoration:none; }}
    .report-footer a:hover {{ text-decoration:underline; text-underline-offset:3px; }}
    .empty-state {{ border:1px dashed var(--line); border-radius:8px; padding:22px; color:var(--muted); text-align:center; }}
    .hidden-count {{ font-size:12px; color:var(--soft); }}
    @media (max-width: 900px) {{
      .panel-grid-3, .panel-grid-2, .finding-detail {{ grid-template-columns:1fr; }}
      .hero-layout {{ grid-template-columns:1fr; }}
      h1 {{ font-size:32px; }}
      .top-nav-inner {{ grid-template-columns:1fr; align-items:flex-start; }}
      .filter-group {{ grid-template-columns:1fr; }}
      .search-row {{ flex-direction:column; }}
      .results-toolbar {{ align-items:flex-start; flex-direction:column; }}
      .finding-card summary {{ grid-template-columns:1fr; align-items:flex-start; }}
      .finding-main {{ flex-wrap:wrap; width:100%; }}
      .finding-title {{ flex-basis:100%; white-space:normal; overflow:visible; text-overflow:clip; line-height:1.35; }}
      .finding-meta {{ justify-self:start; text-align:left; white-space:normal; }}
      .report-footer {{ grid-template-columns:1fr; }}
      .report-footer span:nth-child(2), .report-footer span:nth-child(3) {{ justify-self:start; text-align:left; }}
    }}
    @media (max-width: 560px) {{
      .shell {{ padding:40px 28px 34px; }}
      .hero-inner {{ padding:30px; }}
      .metric-tile-row {{ grid-template-columns:1fr; }}
      .priority-cells {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
    }}
  </style>
</head>
<body>
  <nav class="top-nav">
    <div class="top-nav-inner">
      <div class="brand-mini">
        <span class="brand-text"><strong>{esc(label["report_console"])}</strong><span>{esc(scope_label)}</span></span>
      </div>
      <div class="nav-links">
        <a href="#metrics">{esc(label["metrics_eyebrow"])}</a>
        <a href="#analysis-scope">{esc(label["analysis_scope"])}</a>
        <a href="#quality">{esc(label["quality"])}</a>
        <a href="#architecture">{esc(label["architecture"])}</a>
        <a href="#repositories">{esc(label["repo_situation"])}</a>
        <a href="#findings">{esc(label["findings"])}</a>
        <a href="#package-guide">{esc(label["guide"])}</a>
      </div>
    </div>
  </nav>
  <main class="shell" id="report-root" data-total-bugs="{total}" {priority_attrs}>
    <section class="hero" id="hero">
      <div class="hero-inner">
        <div class="hero-layout">
          <div class="hero-title-row">
            <div class="eyebrow"><span class="badge-dark">{esc(label["open_audit"])}</span><span class="source-badge">{esc(label["source"])}</span></div>
            <h1>{esc(project_title)}</h1>
            <p class="hero-note">{esc(label["static_note"])}</p>
            <div class="meta-strip" aria-label="{esc(label["provenance"])}">
              {meta_token(label["date"], metadata["date"])}
              {meta_token(label["scope"], scope_label)}
              {meta_token(label["analyst"], metadata["analyst"])}
              {meta_token(label["status"], metadata["status"])}
              {meta_token(label["method"], label["source"])}
            </div>
          </div>
          <aside class="hero-dashboard" aria-label="{esc(label["metrics_eyebrow"])}">
            <article class="metric-total">
              <div>
                <div class="metric-label">{esc(label["total"])}</div>
                <div class="metric-value">{esc(total)}</div>
              </div>
              <div class="metric-sub">{esc(label["source"])}</div>
            </article>
            <div class="dashboard-side">
              <div class="priority-cells" aria-label="{esc(label["priority_breakdown"])}">{priority_cells(priority, label)}</div>
              <div class="metric-tile-row">
                {metric_tile(label["p1p2"], p1p2, "P1 + P2", "metric-focus p1")}
                {metric_tile(label["repos"], repo_count, label["repo_profiles"])}
                {metric_tile(label["risk_types"], risk_type_count, label["classified_categories"])}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <section id="metrics" class="section-card">
      <div class="section-heading"><div><p>{esc(label["metrics_eyebrow"])}</p><h2>{esc(label["risk"])}</h2></div><span class="hidden-count" id="visible-count"></span></div>
      <div class="panel-grid-3">
        {bar_list(label["priority"], [(p, split_count(priority, p)) for p in PRIORITY_ORDER], total, label["not_specified"])}
        {bar_list(label["category"], top_items(categories, 6), total, label["not_specified"])}
        {bar_list(label["fix_risk"], top_items(fix_risk, 6), total, label["not_specified"])}
      </div>
    </section>

    <section id="analysis-scope" class="section-card">
      <div class="section-heading"><div><p>{esc(label["analysis_scope_eyebrow"])}</p><h2>{esc(label["analysis_scope_title"])}</h2></div></div>
      {render_analysis_scope_table(version_records, repo_counter, label, repo_bug_counts)}
    </section>

    <section id="quality" class="section-card tone-quality">
      <div class="section-heading"><div><p>{esc(label["quality_eyebrow"])}</p><h2>{esc(label["quality_title"])}</h2></div></div>
      <div class="panel-grid-2">
        {bullet_panel(label["quality_gate"], quality_gate_bullets, label["static_note"])}
        {bullet_panel(label["coverage_strategy"], coverage_bullets, label["lens_fallback"])}
        {bullet_panel(label["coverage_boundary"], boundary_bullets, label["static_note"])}
        {bar_list(label["confidence"], top_items(Counter(confidence), 5), total, label["not_specified"])}
      </div>
    </section>

    <section id="architecture" class="section-card tone-architecture">
      <div class="section-heading"><div><p>{esc(label["architecture_eyebrow"])}</p><h2>{esc(label["architecture_title"])}</h2></div></div>
      <div class="panel-grid-2">
        {insight_panel(label["architecture_invariants"], arch_sections, label["architecture_fallback"])}
        {insight_panel(label["risk_paths"], risk_sections, label["risk_fallback"]) if risk_sections else bullet_panel(label["risk_paths"], relationship_bullets, label["risk_fallback"])}
      </div>
    </section>

    <section id="repositories" class="section-card">
      <div class="section-heading"><div><p>{esc(label["repo_eyebrow"])}</p><h2>{esc(label["repo_situation"])}</h2></div></div>
      {f'<div class="repo-depth-panel">{bullet_panel(label["coverage_classification"], depth_bullets, label["depth_fallback"])}</div>' if depth_bullets else ''}
      <div class="repo-grid">
        {render_repo_cards(findings, repo_counter, label)}
      </div>
    </section>

    <section id="findings" class="section-card">
      <div class="section-heading"><div><p>{esc(label["findings_eyebrow"])}</p><h2>{esc(label["findings_title"])}</h2></div></div>
      <div class="filters">
        <div class="search-row">
          <input id="search" type="search" placeholder="{esc(label["search"])}" autocomplete="off">
          <button class="quick-toggle" id="p1p2-toggle">{esc(label["show_p1p2"])}</button>
          <button class="quick-toggle" id="reset-filters">{esc(label["reset"])}</button>
        </div>
        {render_filter_group(label["priority"], "priority", PRIORITY_ORDER, label["all"])}
        {render_filter_group(label["repo"], "repo", all_repos, label["all"])}
        {render_filter_group(label["category"], "category", all_categories, label["all"])}
        {render_filter_group(label["confidence"], "confidence", all_confidence, label["all"])}
        {render_filter_group(label["fix_risk"], "fixRisk", all_fix_risk, label["all"])}
      </div>
      <div class="results-toolbar" aria-live="polite">
        <div class="result-status" id="result-status"></div>
        <div class="pager">
          <label for="page-size">{esc(label["page_size"])}</label>
          <select id="page-size" aria-label="{esc(label["page_size"])}">
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
            <option value="all">{esc(label["all"])}</option>
          </select>
          <button class="pager-button" id="prev-page" type="button">{esc(label["prev"])}</button>
          <span class="page-status" id="page-status"></span>
          <button class="pager-button" id="next-page" type="button">{esc(label["next"])}</button>
        </div>
      </div>
      <div id="finding-list" class="finding-list-window">{render_findings(findings, label)}</div>
    </section>

    <section id="knowledge" class="section-card">
      <div class="section-heading"><div><p>{esc(label["knowledge_eyebrow"])}</p><h2>{esc(label["knowledge"])}</h2></div></div>
      <div class="panel-grid-3">
        {bar_list(label["issue_families"], top_items(family, 6), total, label["not_specified"])}
        {bar_list(label["impact_domains"], top_items(infra, 6), total, label["not_specified"])}
        {insight_panel(label["handoff_focus"], knowledge_focus_sections, label["risk_fallback"]) if knowledge_focus_sections else bullet_panel(label["handoff_focus"], relationship_bullets, label["risk_fallback"])}
      </div>
    </section>

    {render_package_guide(root, label, output_name)}

    <footer id="provenance" class="report-footer">
      <span><strong>{esc(label["generated_with"])}</strong> {esc(SKILL_NAME)} skill</span>
      <span><strong>{esc(label["skill_source"])}</strong> <a href="{esc(SKILL_SOURCE_URL)}" target="_blank" rel="noopener noreferrer">{esc(SKILL_SOURCE)}</a></span>
      <span>{esc(label["source"])} · {esc(label["data_from"])}</span>
    </footer>
  </main>
  <script>
    const state = {{ search: "", filters: {{}}, p1p2: false, page: 1, pageSize: "20" }};
    const cards = [...document.querySelectorAll(".finding-card")];
    const visibleCount = document.getElementById("visible-count");
    const resultStatus = document.getElementById("result-status");
    const pageStatus = document.getElementById("page-status");
    const pageSizeSelect = document.getElementById("page-size");
    const prevPage = document.getElementById("prev-page");
    const nextPage = document.getElementById("next-page");
    const resultLabel = {json.dumps(label["current_results"], ensure_ascii=False)};
    function normalize(value) {{ return (value || "").toLowerCase(); }}
    function matchFilter(card, key, value) {{
      if (!value) return true;
      const attr = key === "fixRisk" ? "fixRisk" : key;
      const data = normalize(card.dataset[attr]);
      return data.split(/\\s+/).includes(normalize(value)) || data === normalize(value);
    }}
    function cardMatches(card) {{
      const searchOK = !state.search || normalize(card.dataset.search).includes(state.search);
      const filtersOK = Object.entries(state.filters).every(([key, value]) => matchFilter(card, key, value));
      const pOK = !state.p1p2 || ["P1", "P2"].includes(card.dataset.priority);
      return searchOK && filtersOK && pOK;
    }}
    function applyFilters() {{
      const matched = cards.filter(cardMatches);
      const totalVisible = matched.length;
      const numericPageSize = state.pageSize === "all" ? Math.max(totalVisible, 1) : Number(state.pageSize);
      const pageCount = state.pageSize === "all" ? 1 : Math.max(1, Math.ceil(totalVisible / numericPageSize));
      state.page = Math.min(Math.max(state.page, 1), pageCount);
      const start = state.pageSize === "all" ? 0 : (state.page - 1) * numericPageSize;
      const end = state.pageSize === "all" ? totalVisible : Math.min(start + numericPageSize, totalVisible);
      const visibleSet = new Set(matched.slice(start, end));
      for (const card of cards) {{
        const show = visibleSet.has(card);
        card.hidden = !show;
        if (!show) card.querySelector("details")?.removeAttribute("open");
      }}
      if (visibleCount) visibleCount.textContent = `${{totalVisible}} / ${{cards.length}}`;
      if (resultStatus) {{
        const range = totalVisible === 0 ? "0" : `${{start + 1}}-${{end}}`;
        resultStatus.textContent = `${{resultLabel}} ${{range}} / ${{totalVisible}}`;
      }}
      if (pageStatus) pageStatus.textContent = `${{state.page}} / ${{pageCount}}`;
      if (prevPage) prevPage.disabled = state.page <= 1;
      if (nextPage) nextPage.disabled = state.page >= pageCount;
    }}
    document.getElementById("search")?.addEventListener("input", event => {{
      state.search = normalize(event.target.value);
      state.page = 1;
      applyFilters();
    }});
    document.querySelectorAll(".filter-chip").forEach(button => {{
      button.addEventListener("click", () => {{
        const key = button.dataset.filter;
        const value = button.dataset.value;
        document.querySelectorAll(`.filter-chip[data-filter="${{key}}"]`).forEach(el => el.classList.remove("active"));
        button.classList.add("active");
        if (value) state.filters[key] = value; else delete state.filters[key];
        state.page = 1;
        applyFilters();
      }});
    }});
    document.getElementById("p1p2-toggle")?.addEventListener("click", event => {{
      state.p1p2 = !state.p1p2;
      event.currentTarget.classList.toggle("active", state.p1p2);
      state.page = 1;
      applyFilters();
    }});
    pageSizeSelect?.addEventListener("change", event => {{
      state.pageSize = event.target.value;
      state.page = 1;
      applyFilters();
    }});
    prevPage?.addEventListener("click", () => {{
      state.page -= 1;
      applyFilters();
    }});
    nextPage?.addEventListener("click", () => {{
      state.page += 1;
      applyFilters();
    }});
    document.getElementById("reset-filters")?.addEventListener("click", () => {{
      state.search = ""; state.filters = {{}}; state.p1p2 = false; state.page = 1;
      const search = document.getElementById("search");
      if (search) search.value = "";
      document.querySelectorAll(".filter-chip").forEach(el => el.classList.toggle("active", el.dataset.value === ""));
      document.getElementById("p1p2-toggle")?.classList.remove("active");
      applyFilters();
    }});
    applyFilters();
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate interactive Bug audit HTML report")
    parser.add_argument("root", help="Bug audit output root")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="Report language")
    parser.add_argument("--output", default="bug-audit-report.html", help="Output filename under submit root")
    parser.add_argument(
        "--allow-ungated-draft",
        action="store_true",
        help="Allow HTML generation before shard-gate receipt. Reserved for explicitly labeled non-final drafts.",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if (root / "submit").is_dir() and not (root / "findings").is_dir():
        root = root / "submit"
    ensure_report_gate(root, args.allow_ungated_draft)
    index_path = root / "indexes/findings.generated.json"
    if not index_path.is_file():
        raise SystemExit(f"Missing generated index: {index_path}")

    output = root / args.output
    output.write_text(render_html(root, args.language, args.output), encoding="utf-8")
    print(f"Generated interactive Bug audit report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
