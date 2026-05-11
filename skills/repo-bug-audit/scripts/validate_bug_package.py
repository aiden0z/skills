#!/usr/bin/env python3
"""Validate a repository Bug audit package."""
from __future__ import annotations

import argparse
import html
import json
import re
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import audit_scope_contract

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
    "indexes/audit-scope.generated.json",
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
HTML_REPORT_FILE = "bug-audit-report.html"
DEPTH_COVERAGE_FILE = "quality/depth-coverage.md"
CANDIDATE_INDEX_FILE = "indexes/candidates.generated.json"
CANDIDATE_COVERAGE_FILE = "quality/candidate-coverage.md"
ISSUE_FAMILY_COVERAGE_FILE = "quality/issue-family-coverage.md"
SHARD_SUMMARY_FILE = "shard-summary.json"
SHARD_GATE_RECEIPT_FILE = "work/scanner-output/shard-gate.passed.json"
PREPACKAGE_RECEIPT_FILE = "work/scanner-output/prepackage-validation.passed.json"
SCAN_ROOTS_FILE = "work/scanner-output/repo-scan-roots.txt"
HIGH_RECALL_SCAN_JSON = "work/scanner-output/high-recall-scan.json"
HIGH_RECALL_SCAN_MD = "work/scanner-output/high-recall-scan.md"
VALIDATOR_VERSION = "repo-bug-audit-validator-2026-05-11-scope-scan-family"
CANDIDATE_INDEX_GENERATOR = "generate_candidate_index.py"
CANDIDATE_INDEX_SCHEMA_VERSION = 3
HTML_TOP_NAV_GRADIENT = (
    "linear-gradient(90deg,rgba(16,68,59,.96) 0%,"
    "rgba(15,118,110,.94) 58%,rgba(18,130,113,.92) 100%)"
)
HTML_TOTAL_METRIC_BACKGROUND = "linear-gradient(145deg,#FFFFFF 0%,#F8FAFC 62%,#EEF2F7 100%)"
HTML_MAX_SHELL_BOTTOM_PADDING_PX = 40
HTML_MAX_FOOTER_MARGIN_TOP_PX = 28
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
    r"(depth downgrade accepted by user|user accepted (?:a )?downgrade|user accepted first[- ]pass|"
    r"用户.*(接受|确认|同意).*(降级|首轮|第一阶段|first[- ]pass)|"
    r"(降级|首轮|第一阶段|first[- ]pass).*(用户.*(接受|确认|同意)))",
    re.IGNORECASE,
)
OVERVIEW_DECISION_VALUES = {
    "included",
    "omitted-by-user",
    "omitted-as-lightweight-scan",
    "omitted-after-failure",
    "deferred-post-handoff",
}
CRITICAL_ONLY_SCOPE_RE = re.compile(
    r"\b(P1[- ]only|critical[- ]only|critical findings only)\b|只提交\s*P1|仅\s*P1|只看高危|仅高危",
    re.IGNORECASE,
)
REQUIRED_HTML_SECTIONS = [
    "hero",
    "metrics",
    "analysis-scope",
    "quality",
    "architecture",
    "repositories",
    "findings",
    "knowledge",
    "package-guide",
    "provenance",
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
VALID_BOUNDARIES = {
    "api-contract", "cache", "message", "rollback", "third-party",
    "lifecycle", "concurrency", "config", "failure-mode", "clock",
    "permission-propagation", "pagination", "idempotency",
}
VALID_META_LENS = {"META-1", "META-2"}
LEGACY_LENS = {f"L{i}" for i in range(1, 20)}
VALID_LENS = VALID_BOUNDARIES | VALID_META_LENS
BOUNDARY_ORDER = [
    "api-contract", "cache", "message", "rollback", "third-party",
    "lifecycle", "concurrency", "config", "failure-mode", "clock",
    "permission-propagation", "pagination", "idempotency",
]
VALID_EXECUTION_MODES = {"parallel", "serial", "batched"}
VALID_COVERAGE_CLASSIFICATIONS = {"first-pass", "focused", "deep-complete"}
PROFILE_EVIDENCE_REQUIRED_SECTIONS = {
    "Risk Surfaces",
    "Findings and Candidates",
    "Known Uncovered Areas",
}
MERMAID_ID_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
MERMAID_DECL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*[\[(\{]")
MERMAID_KEYWORDS = {
    "flowchart",
    "graph",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "gitGraph",
    "mindmap",
    "timeline",
    "subgraph",
    "end",
    "direction",
    "TB",
    "TD",
    "BT",
    "LR",
    "RL",
}
# Lens coverage record sections. New 13-boundary records use concise fields;
# legacy package records are accepted for compatibility.
LENS_COVERAGE_SECTION_ALIASES = {
    "zh": {
        "scanned": ["已扫描", "已扫描入口"],
        "candidates": ["候选", "候选数"],
        "refuted": ["已排除", "排除原因"],
        "uncovered": ["未覆盖"],
    },
    "en": {
        "scanned": ["Scanned", "Scanned Entry Points"],
        "candidates": ["Candidates"],
        "refuted": ["Refuted", "Exclusion Reasons"],
        "uncovered": ["Uncovered"],
    },
}
DEPTH_COVERAGE_SECTION_ALIASES = [
    ("Repository Roster Gate", ["Repository Roster Gate", "仓库名册门禁"]),
    ("Repository Inventory", ["Repository Inventory", "仓库清单"]),
    ("Historical Baselines", ["Historical Baselines", "历史审计基线"]),
    ("Per-repo Coverage", ["Per-repo Coverage", "分仓覆盖"]),
    ("Zero-finding Repos", ["Zero-finding Repos", "零 Bug 仓"]),
    ("Depth Conclusion", ["Depth Conclusion", "深度结论"]),
]
ISSUE_FAMILY_OUTCOME_RE = re.compile(
    r"\b(promoted|parked|refuted|merged|none|no[- ]hit|not[- ]applicable|out[- ]of[- ]scope)\b|"
    r"提交|候选|排除|合并|无命中|未发现|不适用|范围外|保留",
    re.IGNORECASE,
)
ISSUE_FAMILY_REQUIRED_COLUMNS = {"family", "sources", "outcome", "evidence"}
ISSUE_FAMILY_PLACEHOLDER_VALUES = {
    "",
    "-",
    "—",
    "pending",
    "todo",
    "tbd",
    "unknown",
    "n/a",
    "na",
    "待填",
    "待补充",
    "待确认",
    "未知",
    "<family-id>",
}
SINGLE_REPO_DEFAULT_LENS = VALID_BOUNDARIES | VALID_META_LENS
MULTI_REPO_DEFAULT_LENS = VALID_BOUNDARIES | VALID_META_LENS
PROFILE_REQUIRED_SECTION_ALIASES = [
    ("Tech Stack", ["Tech Stack", "技术栈"]),
    ("Entry Points", ["Entry Points", "入口点"]),
    ("Outbound Calls", ["Outbound Calls", "出站调用"]),
    ("Inbound Endpoints", ["Inbound Endpoints", "入站端点"]),
    ("Shared Events", ["Shared Events", "共享事件"]),
    ("Shared Storage", ["Shared Storage", "共享存储"]),
    ("Shared Config", ["Shared Config", "共享配置"]),
    ("Intent Inputs", ["Intent Inputs", "意图输入"]),
    ("Verification Sources", ["Verification Sources", "验证来源", "验证命令来源"]),
    ("Risk Surfaces", ["Risk Surfaces", "风险面", "风险面与状态"]),
    ("Call Graph", ["Call Graph", "调用图"]),
    ("Findings and Candidates", ["Findings and Candidates", "发现与候选", "Bug 与候选"]),
    ("Known Uncovered Areas", ["Known Uncovered Areas", "已知未覆盖区域", "未覆盖区域"]),
]
GENERIC_SHARD_PHRASES = [
    "representative entry files",
    "auth/config/http/shell/path patterns",
    "no lead had enough code evidence",
    "pattern-only hits in generated clients",
    "no executable trigger path and impact were proven",
    "manual nl -ba review of promoted code paths",
    "external route/controller -> service/helper -> storage/network/shell boundary",
    "profile updated from shard evidence",
    "entry points; auth; config; outbound",
    "entry points, auth, config, outbound",
    "risk surface map",
    "surface map completed",
    "not promoted due to insufficient evidence",
    "retained in the broad funnel and parked because static review did not prove",
    "fresh current-source seed from",
]
GENERIC_PROFILE_PATTERNS = [
    "A[External entry points] --> B[Service/controller module]",
    "B --> C[Storage, shell, network, or runtime boundary]",
    "Confirmed boundaries are listed in findings when promoted",
    "Shared storage was inferred only when code referenced S3, NFS, Redis, PostgreSQL, or Kubernetes resources",
]
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
REPO_SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
    ".yaml",
    ".yml",
}


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


def sanitize_profile_name(name: str) -> str:
    safe = name.replace("/", "__").lower()
    return re.sub(r"[^a-z0-9._-]+", "-", safe).strip("-") or "repo"


def text_mentions_alias(text: str, aliases: list[str]) -> bool:
    for alias in aliases:
        if not alias:
            continue
        pattern = rf"(^|[^A-Za-z0-9_.-]){re.escape(alias)}($|[^A-Za-z0-9_.-])"
        if re.search(pattern, text):
            return True
    return False


def repo_item_matches_name(repo_item: dict, repo_name: str) -> bool:
    return text_mentions_alias(str(repo_name), repo_aliases(repo_item))


def strip_table_cell(value: str) -> str:
    value = html.unescape(str(value))
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"```.*?```", " ", value, flags=re.DOTALL)
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_>#]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def normalize_scope_header(value: str) -> str:
    raw = strip_table_cell(value)
    lowered = raw.lower().replace(" ", "_").replace("-", "_")
    if "repository" in lowered or lowered == "repo" or "仓库" in raw:
        return "repository"
    if ("audit" in lowered and "branch" in lowered) or lowered == "branch" or "审计分支" in raw or raw == "分支":
        return "audit_branch"
    if "commit" in lowered:
        return "commit"
    if "dirty" in lowered or "worktree" in lowered or "工作区" in raw:
        return "dirty"
    if ("submitted" in lowered and "bug" in lowered) or ("bug" in lowered and "提交" in raw) or "提交 Bug" in raw:
        return "submitted_bugs"
    return lowered


def parse_markdown_scope_tables(text: str) -> list[list[dict[str, str]]]:
    tables: list[list[dict[str, str]]] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if not current:
            return
        headers: list[str] = []
        rows: list[dict[str, str]] = []
        for line in current:
            cells = [strip_table_cell(cell.strip()) for cell in line.strip().strip("|").split("|")]
            is_separator = cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells if cell)
            if is_separator:
                continue
            if not headers:
                headers = [normalize_scope_header(cell) for cell in cells]
                continue
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            rows.append(dict(zip(headers, cells)))
        if rows:
            tables.append(rows)
        current = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("|"):
            current.append(line)
        else:
            flush()
    flush()
    return tables


def parse_html_scope_tables(text: str) -> list[list[dict[str, str]]]:
    section_match = re.search(
        r"<section\b[^>]*\bid=[\"']analysis-scope[\"'][^>]*>(.*?)</section>",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not section_match:
        return []
    section = section_match.group(1)
    tables: list[list[dict[str, str]]] = []
    for table_match in re.finditer(r"<table\b[^>]*>(.*?)</table>", section, flags=re.IGNORECASE | re.DOTALL):
        headers: list[str] = []
        rows: list[dict[str, str]] = []
        for row_match in re.finditer(r"<tr\b[^>]*>(.*?)</tr>", table_match.group(1), flags=re.IGNORECASE | re.DOTALL):
            row_html = row_match.group(1)
            header_cells = re.findall(r"<th\b[^>]*>(.*?)</th>", row_html, flags=re.IGNORECASE | re.DOTALL)
            data_cells = re.findall(r"<td\b[^>]*>(.*?)</td>", row_html, flags=re.IGNORECASE | re.DOTALL)
            if header_cells:
                headers = [normalize_scope_header(cell) for cell in header_cells]
                continue
            if data_cells and headers:
                cells = [strip_table_cell(cell) for cell in data_cells]
                if len(cells) < len(headers):
                    cells.extend([""] * (len(headers) - len(cells)))
                rows.append(dict(zip(headers, cells)))
        if rows:
            tables.append(rows)
    return tables


def scope_table_rows(tables: list[list[dict[str, str]]]) -> list[dict[str, str]]:
    required = {"repository", "audit_branch", "commit", "dirty", "submitted_bugs"}
    for rows in tables:
        if rows and required.issubset(set(rows[0])):
            return rows
    return []


def normalize_issue_family_header(value: str) -> str:
    raw = strip_table_cell(value)
    lowered = raw.lower().replace(" ", "_").replace("-", "_")
    if "family" in lowered or "家族" in raw or "风险" in raw:
        return "family"
    if "source" in lowered or "fresh" in lowered or "scan" in lowered or "来源" in raw or "扫描" in raw:
        return "sources"
    if "outcome" in lowered or "result" in lowered or "结果" in raw or "结论" in raw:
        return "outcome"
    if "evidence" in lowered or "anchor" in lowered or "证据" in raw or "锚点" in raw:
        return "evidence"
    return lowered


def parse_markdown_issue_family_rows(text: str) -> list[dict[str, str]]:
    tables: list[list[dict[str, str]]] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if not current:
            return
        headers: list[str] = []
        rows: list[dict[str, str]] = []
        for line in current:
            cells = [strip_table_cell(cell.strip()) for cell in line.strip().strip("|").split("|")]
            is_separator = cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells if cell)
            if is_separator:
                continue
            if not headers:
                headers = [normalize_issue_family_header(cell) for cell in cells]
                continue
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            rows.append(dict(zip(headers, cells)))
        if rows:
            tables.append(rows)
        current = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("|"):
            current.append(line)
        else:
            flush()
    flush()

    for rows in tables:
        if rows and ISSUE_FAMILY_REQUIRED_COLUMNS.issubset(set(rows[0])):
            return rows
    return []


def issue_family_cell_missing(value: str) -> bool:
    return strip_table_cell(value).lower() in ISSUE_FAMILY_PLACEHOLDER_VALUES


REQUIRED_SCOPE_COLUMNS = {"repository", "audit_branch", "commit", "dirty", "submitted_bugs"}
ALLOWED_SCOPE_COLUMNS = set(REQUIRED_SCOPE_COLUMNS)
PLACEHOLDER_SCOPE_VALUES = {
    "",
    "-",
    "—",
    "unknown",
    "pending",
    "待采集",
    "待补充",
    "not specified",
    "n/a",
    "na",
    "tbd",
    "todo",
    "unconfirmed",
    "未知",
}


def scope_value_missing(value: str) -> bool:
    return strip_table_cell(value).lower() in PLACEHOLDER_SCOPE_VALUES


def repo_alias_counts(expected_repo_items: list[dict]) -> Counter:
    counts: Counter[str] = Counter()
    for item in expected_repo_items:
        for alias in {strip_table_cell(alias).lower() for alias in repo_aliases(item) if strip_table_cell(alias)}:
            counts[alias] += 1
    return counts


def unique_repo_aliases(repo_item: dict, expected_repo_items: list[dict]) -> list[str]:
    counts = repo_alias_counts(expected_repo_items)
    aliases = []
    for alias in repo_aliases(repo_item):
        normalized = strip_table_cell(alias).lower()
        if normalized and counts[normalized] == 1:
            aliases.append(alias)
    return aliases


def match_scope_rows_to_repos(
    rows: list[dict[str, str]], expected_repo_items: list[dict], source_name: str
) -> tuple[dict[str, dict[str, str]], list[str]]:
    errors: list[str] = []
    matched_rows: dict[str, dict[str, str]] = {}
    for row in rows:
        repo_cell = row.get("repository", "")
        matches = [
            item
            for item in expected_repo_items
            if text_mentions_alias(repo_cell, unique_repo_aliases(item, expected_repo_items))
        ]
        if len(matches) > 1:
            errors.append(
                f"{source_name} scope baseline row is ambiguous and matches multiple discovered repos: "
                f"{strip_table_cell(repo_cell)}"
            )
            continue
        if not matches:
            continue
        display_name = matches[0]["display_name"]
        if display_name in matched_rows:
            errors.append(f"{source_name} scope baseline has duplicate row for discovered repo: {display_name}")
            continue
        matched_rows[display_name] = row
    return matched_rows, errors


def submitted_bug_counts_for_repos(
    submitted_repo_counts: dict[str, object] | None,
    expected_repo_items: list[dict],
    source_name: str,
) -> tuple[dict[str, int], list[str]]:
    if submitted_repo_counts is None:
        return {}, []
    errors: list[str] = []
    counts_by_repo = {item["display_name"]: 0 for item in expected_repo_items}
    for item in expected_repo_items:
        aliases = unique_repo_aliases(item, expected_repo_items)
        matches = [
            (repo_name, count)
            for repo_name, count in submitted_repo_counts.items()
            if text_mentions_alias(str(repo_name), aliases)
        ]
        if len(matches) > 1:
            errors.append(
                f"{source_name} cannot verify submitted Bug count for {item['display_name']}: "
                "indexes/findings.generated.json repo key is ambiguous"
            )
            continue
        if len(matches) == 1:
            try:
                counts_by_repo[item["display_name"]] = int(matches[0][1] or 0)
            except (TypeError, ValueError):
                errors.append(
                    f"{source_name} cannot verify submitted Bug count for {item['display_name']}: "
                    f"non-numeric index count {matches[0][1]!r}"
                )
    return counts_by_repo, errors


def check_scope_baseline_rows(
    rows: list[dict[str, str]],
    expected_repo_items: list[dict],
    source_name: str,
    submitted_repo_counts: dict[str, object] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not rows:
        errors.append(
            f"{source_name} scope baseline table must include columns: "
            "Repository, Audit Branch, Commit, Dirty/Worktree, Submitted Bugs"
        )
        return errors

    columns = set(rows[0])
    extra_columns = sorted(column for column in columns - ALLOWED_SCOPE_COLUMNS if column)
    if extra_columns:
        errors.append(
            f"{source_name} scope baseline table must stay simplified; remove column(s): "
            + ", ".join(extra_columns)
        )

    matched_rows, match_errors = match_scope_rows_to_repos(rows, expected_repo_items, source_name)
    errors.extend(match_errors)
    expected_bug_counts, count_errors = submitted_bug_counts_for_repos(
        submitted_repo_counts,
        expected_repo_items,
        source_name,
    )
    errors.extend(count_errors)

    missing_repos = [item["display_name"] for item in expected_repo_items if item["display_name"] not in matched_rows]
    if missing_repos:
        errors.append(f"{source_name} scope baseline missing discovered repo row(s): " + ", ".join(missing_repos))

    for repo_name, row in matched_rows.items():
        for key, label in (
            ("audit_branch", "audit branch"),
            ("commit", "commit"),
            ("dirty", "dirty/worktree status"),
        ):
            if scope_value_missing(row.get(key, "")):
                errors.append(f"{source_name} scope baseline row for {repo_name} is missing {label}")
        bug_count = strip_table_cell(row.get("submitted_bugs", ""))
        if not re.fullmatch(r"\d+", bug_count):
            errors.append(f"{source_name} scope baseline row for {repo_name} must have numeric submitted Bug count")
        elif submitted_repo_counts is not None and int(bug_count) != expected_bug_counts.get(repo_name, 0):
            errors.append(
                f"{source_name} scope baseline row for {repo_name} has submitted Bug count {bug_count}, "
                f"expected {expected_bug_counts.get(repo_name, 0)} from indexes/findings.generated.json"
            )
    return errors


def check_readme_scope_baseline(
    readme_text: str,
    expected_repo_items: list[dict],
    submitted_repo_counts: dict[str, object] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not expected_repo_items:
        return errors
    if not re.search(r"分析范围与版本基线|Analysis Scope and Version Baseline", readme_text, re.IGNORECASE):
        errors.append(
            "README.md missing simplified analysis scope/version baseline section "
            "(`分析范围与版本基线` / `Analysis Scope and Version Baseline`)"
        )
    rows = scope_table_rows(parse_markdown_scope_tables(readme_text))
    errors.extend(check_scope_baseline_rows(rows, expected_repo_items, "README.md", submitted_repo_counts))
    return errors


def check_html_scope_baseline(
    html_text: str,
    expected_repo_items: list[dict],
    submitted_repo_counts: dict[str, object] | None = None,
) -> list[str]:
    rows = scope_table_rows(parse_html_scope_tables(html_text))
    return check_scope_baseline_rows(rows, expected_repo_items, HTML_REPORT_FILE, submitted_repo_counts)


def scope_expected_items_from_payload(payload: dict) -> list[dict]:
    items = []
    for row in audit_scope_contract.scope_records_from_payload(payload):
        repo = str(row.get("repository", "")).strip()
        if not repo:
            continue
        items.append(
            {
                "display_name": repo,
                "profile_name": sanitize_profile_name(repo),
                "path_name": repo.split("/")[-1],
                "path": "",
                "source_like_files": 0,
            }
        )
    return items


def scope_repo_counts_from_payload(payload: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in audit_scope_contract.scope_records_from_payload(payload):
        repo = str(row.get("repository", "")).strip()
        submitted = row.get("submitted_bugs", 0)
        if not repo or not isinstance(submitted, int) or submitted < 0:
            continue
        counts[repo] = submitted
    return counts


def read_audit_scope_payload(root: Path) -> tuple[dict | None, list[str]]:
    path = root / audit_scope_contract.AUDIT_SCOPE_INDEX
    if not path.is_file():
        return None, [f"Missing generated audit scope contract: {audit_scope_contract.AUDIT_SCOPE_INDEX}"]
    payload, err = load_json_file(path)
    if err:
        if err == "expected JSON object":
            return None, [f"{audit_scope_contract.AUDIT_SCOPE_INDEX} must be a JSON object"]
        return None, [f"{audit_scope_contract.AUDIT_SCOPE_INDEX} is not valid JSON: {err}"]
    return payload, []


def check_audit_scope_manifest(
    root: Path,
    payload: dict,
    expected_repo_items: list[dict],
    index_repo_counts: dict[str, object] | None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return [f"{audit_scope_contract.AUDIT_SCOPE_INDEX} must be a JSON object"]
    if payload.get("schema_version") != audit_scope_contract.SCHEMA_VERSION:
        errors.append(
            f"{audit_scope_contract.AUDIT_SCOPE_INDEX} schema_version must be {audit_scope_contract.SCHEMA_VERSION}"
        )
    rows = audit_scope_contract.scope_records_from_payload(payload)
    if not rows:
        errors.append(f"{audit_scope_contract.AUDIT_SCOPE_INDEX} must contain non-empty repositories list")
        return errors
    if payload.get("total_analyzed_repos") != len(rows):
        errors.append(
            f"{audit_scope_contract.AUDIT_SCOPE_INDEX} total_analyzed_repos is stale: "
            f"index={payload.get('total_analyzed_repos')}, rows={len(rows)}"
        )
    version_evidence = payload.get("version_evidence")
    if isinstance(version_evidence, dict):
        complete = sum(
            1
            for row in rows
            if not any(audit_scope_contract.version_value_missing(str(row.get(key, ""))) for key in ("audit_branch", "commit", "dirty"))
        )
        if version_evidence.get("total") != len(rows) or version_evidence.get("complete") != complete:
            errors.append(
                f"{audit_scope_contract.AUDIT_SCOPE_INDEX} version_evidence is stale: "
                f"index={version_evidence}, expected={{'complete': {complete}, 'total': {len(rows)}}}"
            )
    else:
        errors.append(f"{audit_scope_contract.AUDIT_SCOPE_INDEX} missing version_evidence object")

    seen_repos: set[str] = set()
    count_checked_rows: list[dict] = []
    for row in rows:
        repo = str(row.get("repository", "")).strip()
        if repo in seen_repos:
            errors.append(f"{audit_scope_contract.AUDIT_SCOPE_INDEX} has duplicate repository row: {repo}")
        seen_repos.add(repo)
        for key, label in (("audit_branch", "audit branch"), ("commit", "commit"), ("dirty", "dirty/worktree status")):
            if audit_scope_contract.version_value_missing(str(row.get(key, ""))):
                errors.append(f"{audit_scope_contract.AUDIT_SCOPE_INDEX} row for {repo} is missing {label}")
        submitted = row.get("submitted_bugs")
        if not isinstance(submitted, int) or submitted < 0:
            errors.append(f"{audit_scope_contract.AUDIT_SCOPE_INDEX} row for {repo} must have non-negative integer submitted_bugs")
        else:
            count_checked_rows.append(row)

    if expected_repo_items:
        missing = [
            item["display_name"]
            for item in expected_repo_items
            if not any(text_mentions_alias(row["repository"], unique_repo_aliases(item, expected_repo_items)) for row in rows)
        ]
        if missing:
            errors.append(
                f"{audit_scope_contract.AUDIT_SCOPE_INDEX} missing discovered repo(s) from --repo-root roster: "
                + ", ".join(missing)
            )
        ambiguous = [
            item["display_name"]
            for item in expected_repo_items
            if not unique_repo_aliases(item, expected_repo_items)
        ]
        if ambiguous:
            errors.append(
                f"{audit_scope_contract.AUDIT_SCOPE_INDEX} cannot uniquely match discovered repo(s); use full relative repo names: "
                + ", ".join(ambiguous)
            )

    if index_repo_counts is not None:
        expected_counts, count_errors = submitted_bug_counts_for_repos(
            index_repo_counts,
            scope_expected_items_from_payload(payload),
            audit_scope_contract.AUDIT_SCOPE_INDEX,
        )
        errors.extend(count_errors)
        for row in count_checked_rows:
            repo = str(row.get("repository", ""))
            if row.get("submitted_bugs") != expected_counts.get(repo, 0):
                errors.append(
                    f"{audit_scope_contract.AUDIT_SCOPE_INDEX} row for {repo} has submitted_bugs "
                    f"{row.get('submitted_bugs')}, expected {expected_counts.get(repo, 0)} from indexes/findings.generated.json"
                )

    version_text = audit_scope_contract.read_text(root / "quality/repository-versions.md")
    if version_text:
        version_rows = audit_scope_contract.parse_repository_versions(version_text)
        version_by_repo = {row["repository"]: row for row in version_rows}
        for row in rows:
            repo = row["repository"]
            source_row = version_by_repo.get(repo)
            if source_row is None:
                errors.append(f"{audit_scope_contract.AUDIT_SCOPE_INDEX} row for {repo} is not present in quality/repository-versions.md")
                continue
            for key in ("audit_branch", "commit", "dirty"):
                if str(row.get(key, "")) != str(source_row.get(key, "")):
                    errors.append(
                        f"{audit_scope_contract.AUDIT_SCOPE_INDEX} row for {repo} has stale {key}: "
                        f"manifest={row.get(key)!r}, repository-versions.md={source_row.get(key)!r}"
                    )
    return errors


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def should_skip_repo_discovery_dir(path: Path) -> bool:
    name = path.name
    skip_names = {
        ".git",
        ".hg",
        ".svn",
        ".idea",
        ".vscode",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "dist",
        "build",
        "target",
        "coverage",
    }
    return name in skip_names or "bug-audit" in name


def count_source_like_files(repo: Path) -> int:
    count = 0
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(repo).parts
        if any(should_skip_repo_discovery_dir(Path(part)) for part in rel_parts[:-1]):
            continue
        if path.suffix.lower() in REPO_SOURCE_EXTENSIONS or path.name in {"Dockerfile", "Makefile"}:
            count += 1
    return count


def discover_expected_repos(repo_roots: list[Path], max_depth: int = 2) -> list[dict]:
    """Discover repo roster from --repo-root for coverage checks.

    A Git root is one expected repo. A non-Git group root contributes every nested
    Git repo up to max_depth, stopping at each discovered repo. This mirrors
    scripts/discover_repositories.py closely enough for final package validation.
    """
    discovered: dict[Path, dict] = {}
    for root in repo_roots:
        if not root.exists():
            continue
        root = root.resolve()
        if is_git_repo(root):
            display_name = root.name
            discovered[root] = {
                "display_name": display_name,
                "profile_name": sanitize_profile_name(display_name),
                "path_name": root.name,
                "path": str(root),
                "source_like_files": count_source_like_files(root),
            }
            continue
        stack: list[tuple[Path, int]] = [(root, 0)]
        while stack:
            current, depth = stack.pop()
            if depth > max_depth:
                continue
            if current != root and is_git_repo(current):
                try:
                    rel = current.relative_to(root).as_posix()
                except ValueError:
                    rel = current.name
                discovered[current] = {
                    "display_name": rel,
                    "profile_name": sanitize_profile_name(rel),
                    "path_name": current.name,
                    "path": str(current),
                    "source_like_files": count_source_like_files(current),
                }
                continue
            if depth == max_depth:
                continue
            try:
                children = sorted(
                    child
                    for child in current.iterdir()
                    if child.is_dir() and not should_skip_repo_discovery_dir(child)
                )
            except OSError:
                continue
            for child in reversed(children):
                stack.append((child, depth + 1))
    return [discovered[path] for path in sorted(discovered, key=lambda p: discovered[p]["profile_name"])]


def repo_aliases(repo_item: dict) -> list[str]:
    aliases = [
        str(repo_item.get("display_name", "")),
        str(repo_item.get("profile_name", "")),
        str(repo_item.get("path_name", "")),
    ]
    return list(dict.fromkeys(alias for alias in aliases if alias))


def expected_repo_for_name(repo_name: str, expected_repo_items: list[dict]) -> dict | None:
    for repo_item in expected_repo_items:
        if repo_item_matches_name(repo_item, repo_name):
            return repo_item
    return None


def path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def file_path_exists_for_repo(rel_path: str, repo_item: dict, repo_roots: list[Path]) -> bool:
    repo_path = Path(str(repo_item.get("path", ""))).expanduser().resolve()
    direct = repo_path / rel_path
    if direct.exists():
        return True
    for root in repo_roots:
        candidate = root / rel_path
        if candidate.exists() and path_is_under(candidate, repo_path):
            return True
    return False


def audit_workspace_root(root: Path) -> Path:
    return root.parent if root.name == "submit" else root


def as_string_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if value in (None, ""):
        return []
    return [str(value)]


def load_json_file(path: Path) -> tuple[dict | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, str(exc)
    except json.JSONDecodeError as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "expected JSON object"
    return payload, None


def section_body_for_aliases(text: str, aliases: list[str]) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        for alias in aliases:
            if re.match(rf"^#{{2,4}}\s+{re.escape(alias)}\s*$", line.strip(), flags=re.IGNORECASE):
                body: list[str] = []
                for body_line in lines[index + 1:]:
                    if re.match(r"^#{2,4}\s+", body_line):
                        return "\n".join(body).strip()
                    body.append(body_line)
                return "\n".join(body).strip()
    return ""


def section_is_emptyish(text: str) -> bool:
    normalized = re.sub(r"[\s`*_>-]+", " ", text).strip().lower()
    return normalized in {
        "",
        "none",
        "none.",
        "n/a",
        "na",
        "no candidate",
        "no candidates",
        "no candidate promoted",
        "none recorded yet",
        "暂无",
        "无",
        "无候选",
    }


def contains_generic_shard_phrase(text: str) -> bool:
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in GENERIC_SHARD_PHRASES)


def generic_candidate_boilerplate_count(text: str) -> int:
    lowered = text.lower()
    return sum(
        lowered.count(phrase)
        for phrase in [
            "retained in the broad funnel and parked because static review did not prove",
            "fresh current-source seed from",
        ]
    )


def has_code_anchor(text: str) -> bool:
    return bool(
        re.search(
            r"(`?[\w./-]+\.(c|cc|cpp|cs|css|go|h|hpp|html|java|js|jsx|kt|m|mm|php|py|rb|rs|scala|sh|sql|swift|ts|tsx|vue|yaml|yml|xml|gradle|toml|json|properties)`?|/[\w./-]+|[A-Za-z_][\w$]*\.[A-Za-z_][\w$]*)",
            text,
        )
        or re.search(r"\b(Dockerfile|Makefile|go\.mod|package\.json|pyproject\.toml|pom\.xml|build\.gradle(?:\.kts)?)\b", text)
        or re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\s+/", text)
    )


def surface_entry_is_specific(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 4 or contains_generic_shard_phrase(stripped):
        return False
    if stripped.lower() in {"none", "n/a", "na", "unknown", "todo", "pending", "无", "暂无"}:
        return False
    return has_code_anchor(stripped)


def normalized_surface_map(value) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, list[str]] = {}
    for category, entries in value.items():
        key = str(category).strip()
        if not key:
            continue
        normalized[key] = as_string_list(entries)
    return normalized


def specific_surface_entries(surface_map: dict[str, list[str]]) -> dict[str, list[str]]:
    specific: dict[str, list[str]] = {}
    for category, entries in surface_map.items():
        filtered = [entry for entry in entries if surface_entry_is_specific(entry)]
        if filtered:
            specific[category] = filtered
    return specific


def hypothesis_loop_has_evidence(loop) -> bool:
    if isinstance(loop, str):
        return bool(loop.strip()) and has_code_anchor(loop) and not contains_generic_shard_phrase(loop)
    if not isinstance(loop, dict):
        return False
    hypothesis = str(loop.get("hypothesis", "")).strip()
    result = str(loop.get("result", "")).strip().lower()
    evidence_text = " ".join(str(value) for value in loop.values())
    return (
        len(hypothesis) >= 10
        and result in {"promoted", "parked", "refuted", "merged"}
        and has_code_anchor(evidence_text)
        and not contains_generic_shard_phrase(evidence_text)
    )


def seed_triage_has_evidence(item) -> bool:
    if isinstance(item, str):
        return (
            has_code_anchor(item)
            and bool(re.search(r"\b(promoted|parked|refuted|merged)\b|提交|候选|排除|合并|保留", item, re.IGNORECASE))
            and not contains_generic_shard_phrase(item)
        )
    if not isinstance(item, dict):
        return False
    outcome = str(item.get("outcome", "")).strip().lower()
    location = str(item.get("location", "")).strip()
    follow_up = str(item.get("follow_up", "")).strip()
    candidate_or_reason = str(item.get("candidate_or_reason", "")).strip()
    return (
        outcome in VALID_SEED_TRIAGE_OUTCOMES
        and bool(location)
        and (has_code_anchor(location) or ":" in location)
        and len(follow_up) >= 12
        and len(candidate_or_reason) >= 8
    )


def profile_sections_are_present(payload: dict) -> tuple[set[str], set[str]]:
    raw_sections = payload.get("profile_evidence_sections")
    if isinstance(raw_sections, dict):
        present = {str(key).strip() for key, value in raw_sections.items() if str(value).strip()}
    else:
        present = {str(item).strip() for item in as_string_list(raw_sections)}
    return present, PROFILE_EVIDENCE_REQUIRED_SECTIONS - present


def explicit_candidate_entry_count(candidate_body: str) -> int:
    count = 0
    for raw in candidate_body.splitlines():
        line = raw.strip()
        if not line.startswith(("- ", "* ", "### ", "#### ")):
            continue
        if re.search(r"\bnone recorded yet\b|pending shard exploration|暂无|待补充", line, re.IGNORECASE):
            continue
        if re.search(r"\b(C\d+|BUG-\d{4,})\b", line, flags=re.IGNORECASE):
            count += 1
            continue
        if re.search(r"`[^`]+:\d+`|[A-Za-z0-9_./-]+\.(py|ts|tsx|js|java|go|rs|yaml|yml|sh|md):\d+", line):
            count += 1
    return count


def check_candidates_evidence(
    path: Path,
    rel_path: str,
    candidate_count: int,
    submitted_bug_ids: list[str],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if "Pending shard exploration" in text:
        errors.append(f"{rel_path}: still contains pending shard exploration template")
    candidate_body = section_body_for_aliases(text, ["Candidate Leads", "候选线索"])
    promotion_body = section_body_for_aliases(text, ["Promotion Review", "提升复核", "升级复核"])
    refuted_body = section_body_for_aliases(text, ["Refuted Leads", "已排除线索", "误报排查"])
    zero_body = section_body_for_aliases(text, ["Zero-candidate Rationale", "零候选理由", "零候选说明"])
    # Format warnings
    if candidate_body == "":
        warnings.append(f"{rel_path}: missing Candidate Leads section")
    if refuted_body == "":
        warnings.append(f"{rel_path}: missing Refuted Leads section")
    if zero_body == "":
        warnings.append(f"{rel_path}: missing Zero-candidate Rationale section")
    # Evidence errors
    if candidate_count > 0 and section_is_emptyish(candidate_body):
        errors.append(f"{rel_path}: candidate_count > 0 but Candidate Leads is empty")
    if candidate_count > 0 and not has_code_anchor(candidate_body) and "BUG-" not in candidate_body:
        errors.append(f"{rel_path}: candidate leads need a Bug ID, candidate file, or code path anchor")
    boilerplate_count = generic_candidate_boilerplate_count(candidate_body)
    if boilerplate_count >= 3:
        warnings.append(
            f"{rel_path}: Candidate Leads contains {boilerplate_count} generic scanner-seed parked lines"
        )
    explicit_count = explicit_candidate_entry_count(candidate_body)
    allowed_count = explicit_count + len(submitted_bug_ids)
    if candidate_count > allowed_count:
        errors.append(
            f"{rel_path}: candidate_count ({candidate_count}) exceeds explicit Candidate Leads entries "
            f"plus submitted Bugs ({allowed_count})"
        )
    if candidate_count == 0 and len(zero_body) < 40:
        warnings.append(f"{rel_path}: zero-candidate rationale is short, consider naming concrete paths")
    if candidate_count == 0 and contains_generic_shard_phrase(zero_body) and not has_code_anchor(zero_body):
        errors.append(f"{rel_path}: zero-candidate rationale is too generic; name concrete paths or scanned surfaces")
    if contains_generic_shard_phrase(refuted_body) and not has_code_anchor(refuted_body):
        warnings.append(f"{rel_path}: refuted leads — name the specific guard, sibling implementation, or false-positive reason with file:line")
    high_priority_parked_ids: list[str] = []
    for line in candidate_body.splitlines():
        if not re.search(r"\bparked\s+P[12]\b|\bP[12]\s*[:,-]?\s*parked\b", line, flags=re.IGNORECASE):
            continue
        match = re.search(r"\b(C\d+)\b", line, flags=re.IGNORECASE)
        high_priority_parked_ids.append(match.group(1).upper() if match else "<unlabeled>")
    if high_priority_parked_ids:
        if section_is_emptyish(promotion_body):
            errors.append(
                f"{rel_path}: parked P1/P2 candidates require a Promotion Review section "
                f"({', '.join(high_priority_parked_ids[:8])})"
            )
        else:
            review_upper = promotion_body.upper()
            missing_ids = [
                candidate_id
                for candidate_id in high_priority_parked_ids
                if candidate_id != "<unlabeled>" and candidate_id not in review_upper
            ]
            if missing_ids:
                warnings.append(
                    f"{rel_path}: Promotion Review — add an entry for each parked P1/P2 candidate id "
                    f"(missing {', '.join(missing_ids[:8])})"
                )
            if not has_code_anchor(promotion_body) and "BUG-" not in promotion_body:
                warnings.append(f"{rel_path}: Promotion Review could use a code anchor or merge target")
            if not re.search(
                r"\b(missing|insufficient|runtime|deployment|duplicate|merged|merge target|false-positive|"
                r"guard|scope|needs?|unconfirmed|blocked)\b|缺|未确认|运行时|部署|合并|误报|缺少|范围",
                promotion_body,
                flags=re.IGNORECASE,
            ):
                warnings.append(f"{rel_path}: Promotion Review should name the missing gate or guard")
    return errors, warnings


def write_shard_gate_receipt(workspace_root: Path, root: Path, expected_repo_items: list[dict]) -> None:
    receipt_path = workspace_root / SHARD_GATE_RECEIPT_FILE
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    payload = {
        "validator_version": VALIDATOR_VERSION,
        "passed_at": now.isoformat(),
        "passed_at_epoch": now.timestamp(),
        "submit_root": str(root),
        "repo_count": len(expected_repo_items),
        "profiles": [item["profile_name"] for item in expected_repo_items],
    }
    receipt_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_prepackage_receipt(workspace_root: Path, root: Path, expected_repo_items: list[dict], finding_count: int) -> None:
    receipt_path = workspace_root / PREPACKAGE_RECEIPT_FILE
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    payload = {
        "validator_version": VALIDATOR_VERSION,
        "passed_at": now.isoformat(),
        "passed_at_epoch": now.timestamp(),
        "submit_root": str(root),
        "repo_count": len(expected_repo_items),
        "finding_count": finding_count,
        "profiles": [item["profile_name"] for item in expected_repo_items],
    }
    receipt_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check_prepackage_receipt(
    workspace_root: Path,
    root: Path,
    require_asset_order: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not require_asset_order:
        return errors, warnings
    receipt_path = workspace_root / PREPACKAGE_RECEIPT_FILE
    if not receipt_path.is_file():
        errors.append(
            f"Missing pre-package validation receipt: {PREPACKAGE_RECEIPT_FILE}. "
            "Run validate_bug_package.py <submit-root> --repo-root <path> before generating HTML or overview assets."
        )
        return errors, warnings
    payload, error = load_json_file(receipt_path)
    if error or payload is None:
        errors.append(f"{PREPACKAGE_RECEIPT_FILE} is not valid JSON: {error}")
        return errors, warnings
    if payload.get("validator_version") != VALIDATOR_VERSION:
        warnings.append(
            f"{PREPACKAGE_RECEIPT_FILE}: validator_version differs from current {VALIDATOR_VERSION}; rerun pre-package validation if in doubt"
        )
    passed_epoch = payload.get("passed_at_epoch")
    if isinstance(passed_epoch, (int, float)):
        for asset in (root / HTML_REPORT_FILE, root / "audit-overview.png"):
            if asset.exists() and asset.stat().st_mtime + 0.000001 < float(passed_epoch):
                rel = asset.relative_to(root).as_posix()
                errors.append(f"{rel} is older than pre-package validation; regenerate report assets after validation")
    return errors, warnings


def check_shard_gate_receipt(
    workspace_root: Path,
    root: Path,
    expected_repo_items: list[dict],
    require_asset_order: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if len(expected_repo_items) <= 1:
        return errors, warnings
    receipt_path = workspace_root / SHARD_GATE_RECEIPT_FILE
    if not receipt_path.is_file():
        errors.append(
            f"Missing shard evidence gate receipt: {SHARD_GATE_RECEIPT_FILE}. "
            "Run validate_bug_package.py <submit-root> --validate-shards-only --repo-root <path> before packaging."
        )
        return errors, warnings
    payload, error = load_json_file(receipt_path)
    if error or payload is None:
        errors.append(f"{SHARD_GATE_RECEIPT_FILE} is not valid JSON: {error}")
        return errors, warnings
    if payload.get("validator_version") != VALIDATOR_VERSION:
        warnings.append(
            f"{SHARD_GATE_RECEIPT_FILE}: validator_version differs from current {VALIDATOR_VERSION}; rerun shard gate if in doubt"
        )
    if payload.get("repo_count") != len(expected_repo_items):
        errors.append(
            f"{SHARD_GATE_RECEIPT_FILE}: repo_count={payload.get('repo_count')} does not match discovered roster {len(expected_repo_items)}"
        )
    profiles = set(as_string_list(payload.get("profiles")))
    expected_profiles = {str(item["profile_name"]) for item in expected_repo_items}
    if profiles != expected_profiles:
        errors.append(f"{SHARD_GATE_RECEIPT_FILE}: profiles do not match current discovered roster")
    if require_asset_order:
        passed_epoch = payload.get("passed_at_epoch")
        if isinstance(passed_epoch, (int, float)):
            final_assets = [root / rel for rel in ("README.md", HTML_REPORT_FILE, "audit-overview.png")]
            final_assets.extend(sorted((root / "findings").glob("P[1-4]/*.md")))
            for asset in final_assets:
                if asset.exists() and asset.stat().st_mtime + 0.000001 < float(passed_epoch):
                    rel = asset.relative_to(root).as_posix()
                    errors.append(
                        f"{rel} is older than the shard gate receipt; generate or rewrite final findings "
                        "from shard evidence after shard validation. Do not use touch or timestamp-only updates."
                    )
    return errors, warnings


def check_scan_roots_file(workspace_root: Path, expected_repo_items: list[dict]) -> list[str]:
    errors: list[str] = []
    if len(expected_repo_items) <= 1:
        return errors
    path = workspace_root / SCAN_ROOTS_FILE
    if not path.is_file():
        errors.append(f"Missing repo source scan roots: {SCAN_ROOTS_FILE}")
        return errors
    raw_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    roots = [line.strip() for line in raw_lines if line.strip() and not line.lstrip().startswith("#")]
    expected_paths = {str(Path(str(item["path"])).expanduser().resolve()) for item in expected_repo_items}
    actual_paths = {str(Path(line).expanduser().resolve()) for line in roots}
    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        if missing:
            errors.append(f"{SCAN_ROOTS_FILE}: missing repo source roots: " + ", ".join(missing[:8]))
        if extra:
            errors.append(f"{SCAN_ROOTS_FILE}: contains non-roster roots: " + ", ".join(extra[:8]))
    for line in roots:
        resolved = Path(line).expanduser().resolve()
        if "bug-audit" in resolved.name or any("bug-audit" in part for part in resolved.parts):
            errors.append(f"{SCAN_ROOTS_FILE}: audit package path is not a source root: {line}")
        if not (resolved / ".git").exists():
            errors.append(f"{SCAN_ROOTS_FILE}: source root is not a Git repo: {line}")
    return errors


def load_high_recall_repo_index(workspace_root: Path) -> dict[str, dict]:
    json_path = workspace_root / HIGH_RECALL_SCAN_JSON
    payload, error = load_json_file(json_path)
    if error or not isinstance(payload, dict):
        return {}
    repos = payload.get("repos")
    if not isinstance(repos, list):
        return {}
    index: dict[str, dict] = {}
    for item in repos:
        if not isinstance(item, dict):
            continue
        profile_name = str(item.get("profile_name", "")).strip()
        if not profile_name:
            continue
        categories = {
            str(hit.get("category", "")).strip()
            for hit in item.get("hits", [])
            if isinstance(hit, dict) and str(hit.get("category", "")).strip()
        }
        index[profile_name] = {
            "hit_count": item.get("hit_count") if isinstance(item.get("hit_count"), int) else 0,
            "categories": categories,
        }
    return index


VALID_SEED_TRIAGE_OUTCOMES = {"promoted", "parked", "refuted", "merged"}




def check_shard_summaries(
    workspace_root: Path,
    expected_repo_items: list[dict],
    repo_roots: list[Path],
    coverage_mode: str = "deep",
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    relaxed = coverage_mode == "batch-first-pass"
    if len(expected_repo_items) <= 1:
        return errors, warnings
    shards_root = workspace_root / "work/shards"
    high_recall_by_profile = load_high_recall_repo_index(workspace_root)
    for repo_item in expected_repo_items:
        profile_name = str(repo_item["profile_name"])
        summary_path = shards_root / profile_name / SHARD_SUMMARY_FILE
        rel_summary = f"work/shards/{profile_name}/{SHARD_SUMMARY_FILE}"
        candidates_path = shards_root / profile_name / "candidates.md"
        rel_candidates = f"work/shards/{profile_name}/candidates.md"
        has_candidates_file = candidates_path.is_file()
        if not has_candidates_file:
            errors.append(f"Missing repo shard candidates file: {rel_candidates}")
        if not summary_path.is_file():
            errors.append(f"Missing repo shard summary: {rel_summary}")
            continue
        payload, error = load_json_file(summary_path)
        if error or payload is None:
            errors.append(f"{rel_summary} is not valid JSON: {error}")
            continue
        if str(payload.get("profile_name", "")) != profile_name:
            errors.append(f"{rel_summary}: profile_name must be {profile_name}")
        if not repo_item_matches_name(repo_item, str(payload.get("repo", ""))):
            errors.append(f"{rel_summary}: repo must match discovered repo {repo_item['display_name']}")
        source_count = int(repo_item.get("source_like_files", 0) or 0)

        # === EVIDENCE ERRORS (blocking) ===
        # These check for fabricated, missing, or inconsistent evidence. They
        # intentionally do not prescribe which Bug patterns the agent must hunt.
        execution_mode = str(payload.get("execution_mode", "")).strip()
        if execution_mode not in VALID_EXECUTION_MODES:
            errors.append(
                f"{rel_summary}: execution_mode must be one of "
                f"{', '.join(sorted(VALID_EXECUTION_MODES))}"
            )
        parallel_eligible = payload.get("parallel_eligible")
        if not isinstance(parallel_eligible, bool):
            errors.append(f"{rel_summary}: parallel_eligible must be a boolean")
        elif source_count > 10 and not parallel_eligible:
            warnings.append(f"{rel_summary}: repo has >10 source-like files but parallel_eligible is false")
        serial_reason = str(payload.get("serial_reason", "")).strip()
        if parallel_eligible is True and execution_mode == "serial" and len(serial_reason) < 20:
            errors.append(f"{rel_summary}: serial execution for a parallel-eligible shard needs a concrete serial_reason")

        classification = str(payload.get("coverage_classification", "")).strip()
        if classification not in VALID_COVERAGE_CLASSIFICATIONS:
            errors.append(
                f"{rel_summary}: coverage_classification must be first-pass, focused, or deep-complete"
            )
        focus_scope = str(payload.get("focus_scope", "")).strip()
        if classification == "focused" and len(focus_scope) < 10:
            errors.append(f"{rel_summary}: focused coverage requires a concrete focus_scope")

        risk_surfaces = as_string_list(payload.get("risk_surfaces_scanned"))
        evidence_paths = as_string_list(payload.get("evidence_paths"))
        searches = as_string_list(payload.get("commands_or_searches"))
        submitted_bug_ids = as_string_list(payload.get("submitted_bug_ids"))
        candidate_count = payload.get("candidate_count")
        if not isinstance(candidate_count, int) or candidate_count < 0:
            errors.append(f"{rel_summary}: candidate_count must be a non-negative integer")
            candidate_count = 0
        if source_count > 0 and not evidence_paths:
            errors.append(f"{rel_summary}: evidence_paths must include at least one real path")
        if not risk_surfaces:
            errors.append(f"{rel_summary}: risk_surfaces_scanned must not be empty")
        if not searches:
            errors.append(f"{rel_summary}: commands_or_searches must not be empty")
        # Check that cited file paths actually exist in the repo
        for rel_path in evidence_paths:
            if not file_path_exists_for_repo(rel_path.strip().lstrip("/"), repo_item, repo_roots):
                errors.append(f"{rel_summary}: evidence path does not exist in repo {repo_item['display_name']}: {rel_path}")

        surface_map = normalized_surface_map(payload.get("surface_map"))
        specific_surfaces = specific_surface_entries(surface_map)
        if source_count > 10 and not specific_surfaces:
            errors.append(
                f"{rel_summary}: non-trivial repo needs at least one evidence-bearing surface_map entry"
            )
        elif not relaxed and source_count > 50 and len(specific_surfaces) < 2:
            warnings.append(
                f"{rel_summary}: large repo has a thin surface_map; keep coverage_classification honest"
            )

        raw_loops = payload.get("hypothesis_loops")
        if isinstance(raw_loops, list):
            hypothesis_loops = raw_loops
        elif raw_loops in (None, ""):
            hypothesis_loops = []
        else:
            hypothesis_loops = [raw_loops]
        evidence_loops = [loop for loop in hypothesis_loops if hypothesis_loop_has_evidence(loop)]
        if source_count > 10 and not evidence_loops:
            errors.append(
                f"{rel_summary}: non-trivial repo needs at least one evidence-bearing hypothesis_loops entry"
            )

        profile_updated = payload.get("profile_updated_from_shard")
        if source_count > 0 and profile_updated is not True:
            errors.append(f"{rel_summary}: profile_updated_from_shard must be true after shard exploration")
        _, missing_profile_sections = profile_sections_are_present(payload)
        if source_count > 0 and missing_profile_sections:
            errors.append(
                f"{rel_summary}: profile_evidence_sections missing "
                + ", ".join(sorted(missing_profile_sections))
            )

        high_recall_info = high_recall_by_profile.get(profile_name, {})
        high_recall_hits = high_recall_info.get("hit_count") if isinstance(high_recall_info, dict) else 0
        if isinstance(high_recall_hits, int) and high_recall_hits > 0:
            raw_seed_triage = payload.get("seed_triage")
            seed_triage = raw_seed_triage if isinstance(raw_seed_triage, list) else []
            if not any(seed_triage_has_evidence(item) for item in seed_triage):
                errors.append(
                    f"{rel_summary}: high-recall seeds exist; seed_triage needs at least one evidence-bearing reviewed seed"
                )

        # Candidate count consistency
        if submitted_bug_ids and candidate_count < len(submitted_bug_ids):
            errors.append(
                f"{rel_summary}: candidate_count must include promoted submitted_bug_ids; "
                f"found {candidate_count} candidates for {len(submitted_bug_ids)} submitted Bugs"
            )
        # Zero-finding repos must explain why
        zero_rationale = str(payload.get("zero_finding_rationale", "")).strip()
        if not submitted_bug_ids and candidate_count == 0 and len(zero_rationale) < 20:
            errors.append(f"{rel_summary}: zero_finding_rationale is required when no candidates or Bugs were found")
        call_chains = as_string_list(payload.get("call_chains_traced"))
        remaining_gaps = as_string_list(payload.get("remaining_gaps"))
        if not relaxed and classification in {"first-pass", "focused"} and not remaining_gaps:
            warnings.append(f"{rel_summary}: partial coverage should name remaining_gaps")
        if classification == "deep-complete":
            if source_count >= 50 and not call_chains:
                warnings.append(f"{rel_summary}: large deep-complete shard should list call_chains_traced")
            blocking_gap_terms = [
                "unknown", "uncovered", "not reviewed", "pending",
                "未知", "未覆盖", "未审阅", "待确认",
            ]
            for gap in remaining_gaps:
                lowered = gap.lower()
                if any(term in lowered for term in blocking_gap_terms):
                    errors.append(f"{rel_summary}: deep-complete cannot list blocking remaining gap: {gap}")
        strongest_refuted = as_string_list(payload.get("strongest_refuted_leads"))
        refuted_loop = any(
            isinstance(loop, dict) and str(loop.get("result", "")).strip().lower() == "refuted"
            for loop in evidence_loops
        )
        if source_count > 10 and not submitted_bug_ids and candidate_count == 0 and not strongest_refuted and not refuted_loop:
            errors.append(
                f"{rel_summary}: zero-candidate non-trivial repo needs a strongest_refuted_leads entry or refuted hypothesis loop"
            )

        # Candidate evidence checks compare declared counts against concrete notes.
        if has_candidates_file:
            cand_errors, _ = check_candidates_evidence(candidates_path, rel_candidates, candidate_count, submitted_bug_ids)
            errors.extend(cand_errors)

    # Cross-repo pattern detection: same candidate description in 3+ repos → worth deep-diving
    cross_repo_warnings = detect_cross_repo_patterns(expected_repo_items, shards_root)
    warnings.extend(cross_repo_warnings)

    return errors, warnings


def detect_cross_repo_patterns(
    expected_repo_items: list[dict],
    shards_root: Path,
) -> list[str]:
    """Detect candidate patterns via bigram matching across 3+ repos."""
    warnings: list[str] = []
    repo_candidates: dict[str, list[str]] = {}
    for repo_item in expected_repo_items:
        profile_name = str(repo_item["profile_name"])
        candidates_path = shards_root / profile_name / "candidates.md"
        if not candidates_path.is_file():
            continue
        text = candidates_path.read_text(encoding="utf-8", errors="replace")
        entries = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- ") and ("cand-" in stripped.lower() or "`" in stripped):
                desc = re.sub(r'^-\s*\*?P\d-cand-\w+-\d+\*?\s*:?\s*', '', stripped)
                desc = desc.strip()
                if len(desc) > 20:
                    entries.append(desc)
        if entries:
            repo_candidates[profile_name] = entries

    from collections import Counter
    bigram_repos: dict[str, Counter] = {}
    for repo_name, entries in repo_candidates.items():
        for entry in entries:
            words = [w.lower() for w in re.findall(r'[a-z_]{3,}', entry.lower())]
            for i in range(len(words) - 1):
                w1, w2 = words[i], words[i+1]
                if w1 in COMMON_WORDS or w2 in COMMON_WORDS:
                    continue
                bigram = f"{w1} {w2}"
                if bigram not in bigram_repos:
                    bigram_repos[bigram] = Counter()
                bigram_repos[bigram][repo_name] += 1

    reported: set[frozenset] = set()
    for bigram, counter in sorted(bigram_repos.items(), key=lambda x: -len(x[1])):
        if len(counter) < 3:
            continue
        repos_key = frozenset(counter.keys())
        if repos_key in reported:
            continue
        reported.add(repos_key)
        repos_str = ", ".join(sorted(counter.keys()))
        warnings.append(
            f"cross-repo pattern: '{bigram}' in {len(counter)} repos "
            f"({repos_str}) — consider cross-repo lens deep-dive"
        )

    return warnings


# Common words to exclude from cross-repo pattern detection
COMMON_WORDS = {
    "this", "that", "with", "from", "when", "code", "file", "user", "data",
    "path", "line", "using", "used", "into", "does", "such", "they", "have",
    "been", "would", "could", "which", "their", "them", "also", "than",
    "then", "only", "over", "very", "just", "like", "make", "made", "need",
    "well", "even", "much", "must", "part", "same", "some", "take", "work",
    "what", "where", "while", "after", "before", "being", "other",
}


def check_candidate_index(
    root: Path,
    workspace_root: Path,
    expected_repo_items: list[dict],
    finding_count: int,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if len(expected_repo_items) <= 1:
        return errors, warnings

    index_path = root / CANDIDATE_INDEX_FILE
    coverage_path = root / CANDIDATE_COVERAGE_FILE
    markdown_path = root / "indexes/candidates.generated.md"
    if not index_path.is_file():
        errors.append(
            f"Missing candidate pool index: {CANDIDATE_INDEX_FILE}; "
            "run generate_candidate_index.py before pre-package validation"
        )
        return errors, warnings
    if not markdown_path.is_file():
        errors.append("Missing candidate pool Markdown index: indexes/candidates.generated.md")
    if not coverage_path.is_file():
        errors.append(f"Missing candidate discovery coverage: {CANDIDATE_COVERAGE_FILE}")

    payload, error = load_json_file(index_path)
    if error or not isinstance(payload, dict):
        errors.append(f"{CANDIDATE_INDEX_FILE} is not valid JSON: {error}")
        return errors, warnings
    if payload.get("generated_by") != CANDIDATE_INDEX_GENERATOR:
        errors.append(
            f"{CANDIDATE_INDEX_FILE}: generated_by must be {CANDIDATE_INDEX_GENERATOR}; "
            "run the deterministic candidate index generator instead of hand-writing this file"
        )
    if payload.get("schema_version") != CANDIDATE_INDEX_SCHEMA_VERSION:
        errors.append(
            f"{CANDIDATE_INDEX_FILE}: schema_version must be {CANDIDATE_INDEX_SCHEMA_VERSION}; "
            "regenerate with generate_candidate_index.py"
        )
    for field in ("candidates_by_priority", "candidate_outcomes", "candidate_outcomes_by_priority"):
        if not isinstance(payload.get(field), dict):
            errors.append(f"{CANDIDATE_INDEX_FILE}: missing {field}; regenerate with generate_candidate_index.py")
    gate_complete_unsubmitted = payload.get("gate_complete_unsubmitted_candidates")
    if not isinstance(gate_complete_unsubmitted, list):
        errors.append(
            f"{CANDIDATE_INDEX_FILE}: missing gate_complete_unsubmitted_candidates; "
            "regenerate with generate_candidate_index.py"
        )
        gate_complete_unsubmitted = []

    shard_total = 0
    submitted_links = 0
    shard_repos: set[str] = set()
    for repo_item in expected_repo_items:
        profile_name = str(repo_item["profile_name"])
        summary_path = workspace_root / "work/shards" / profile_name / SHARD_SUMMARY_FILE
        if not summary_path.is_file():
            continue
        shard_payload, shard_error = load_json_file(summary_path)
        if shard_error or not isinstance(shard_payload, dict):
            continue
        shard_repos.add(profile_name)
        count = shard_payload.get("candidate_count")
        if isinstance(count, int) and count >= 0:
            shard_total += count
        submitted = shard_payload.get("submitted_bug_ids")
        if isinstance(submitted, list):
            submitted_links += len(submitted)

    index_total = payload.get("total_candidates")
    if not isinstance(index_total, int) or index_total < 0:
        errors.append(f"{CANDIDATE_INDEX_FILE}: total_candidates must be a non-negative integer")
    elif index_total != shard_total:
        errors.append(
            f"{CANDIDATE_INDEX_FILE}: total_candidates ({index_total}) does not match shard candidate_count total ({shard_total})"
        )
    submitted_total = payload.get("total_submitted_findings")
    if not isinstance(submitted_total, int) or submitted_total != finding_count:
        errors.append(
            f"{CANDIDATE_INDEX_FILE}: total_submitted_findings must match findings index count ({finding_count})"
        )
    promoted_links = payload.get("total_promoted_candidate_links")
    if isinstance(promoted_links, int) and promoted_links != submitted_links:
        errors.append(
            f"{CANDIDATE_INDEX_FILE}: promoted candidate links ({promoted_links}) do not match shard submitted_bug_ids ({submitted_links})"
        )
    if finding_count > shard_total:
        errors.append(
            f"{CANDIDATE_INDEX_FILE}: submitted findings ({finding_count}) exceed candidate leads ({shard_total}); "
            "every final Bug must come from a candidate or shard lead"
        )

    high_recall_payload, high_recall_error = load_json_file(workspace_root / HIGH_RECALL_SCAN_JSON)
    total_seed_hits = 0
    if not high_recall_error and isinstance(high_recall_payload, dict):
        raw_hits = high_recall_payload.get("total_hits")
        if isinstance(raw_hits, int) and raw_hits > 0:
            total_seed_hits = raw_hits
    depth_text = ""
    depth_path = root / DEPTH_COVERAGE_FILE
    if depth_path.is_file():
        depth_text = depth_path.read_text(encoding="utf-8", errors="replace")
    scope_text = ""
    scope_path = root / "quality/submission-scope.md"
    if scope_path.is_file():
        scope_text = scope_path.read_text(encoding="utf-8", errors="replace")
    intent = extract_depth_intent(scope_text)
    requested_deep = bool(DEEP_INTENT_RE.search(intent) or scope_records_requested_deep(scope_text))
    critical_only_scope = bool(CRITICAL_ONLY_SCOPE_RE.search(scope_text))
    if gate_complete_unsubmitted:
        sample = []
        for item in gate_complete_unsubmitted[:6]:
            if isinstance(item, dict):
                label = str(item.get("id") or "unlabeled")
                repo = str(item.get("repo") or item.get("profile_name") or "unknown")
                priority = str(item.get("priority") or "unknown")
                sample.append(f"{repo}:{label}:{priority}")
            else:
                sample.append(str(item))
        message = (
            f"{CANDIDATE_INDEX_FILE}: gate-complete candidates remain unsubmitted "
            f"({', '.join(sample)}). Promote them to findings/P1-P4 or change their candidate note "
            "to name the missing gate."
        )
        if critical_only_scope:
            warnings.append(message + " Critical-only scope is recorded, so this is not blocking.")
        else:
            errors.append(message)
    claims_deep_complete = bool(DEEP_COMPLETE_RE.search(depth_text)) and not depth_coverage_is_partial(depth_text)
    if claims_deep_complete and total_seed_hits >= 100 and isinstance(index_total, int):
        minimum_expected = min(160, max(40, len(expected_repo_items) * 4, total_seed_hits // 12))
        if index_total < minimum_expected:
            warnings.append(
                f"{CANDIDATE_INDEX_FILE}: deep-complete high-recall funnel is too thin "
                f"({index_total} retained candidates from {total_seed_hits} search seeds; heuristic comparison threshold "
                f"{minimum_expected}). This is a review signal, not a fixed Bug quota; make sure seed_triage, "
                "issue-family coverage, and depth-coverage explain why leads were refuted, parked, or not applicable."
            )
    if requested_deep and total_seed_hits >= 500 and isinstance(index_total, int):
        minimum_expected = min(160, max(30, len(expected_repo_items) * 3, total_seed_hits // 50))
        if index_total < minimum_expected:
            message = (
                f"{CANDIDATE_INDEX_FILE}: requested deep/high-recall funnel is too thin "
                f"({index_total} retained candidates from {total_seed_hits} search seeds; heuristic comparison threshold "
                f"{minimum_expected}). "
                "Candidate admission is broader than final Bug submission; continue repo-local triage "
                "or record that the user accepted a narrower recall target."
            )
            warnings.append(message)
        parked_total = payload.get("total_parked_or_unpromoted_candidates")
        if finding_count > 0 and index_total <= finding_count:
            message = (
                f"{CANDIDATE_INDEX_FILE}: candidate funnel collapsed into final findings "
                f"({index_total} candidates for {finding_count} submitted Bugs). "
                "A high-recall deep audit should preserve parked, merged, refuted, or follow-up-needed leads "
                "instead of submitting every retained candidate."
            )
            warnings.append(message)
        if isinstance(parked_total, int) and finding_count > 0 and parked_total == 0:
            message = (
                f"{CANDIDATE_INDEX_FILE}: no parked or unpromoted candidates are visible despite "
                f"{total_seed_hits} high-recall seeds. Retain credible lower-confidence/P3/P4/follow-up leads "
                "or explain the user-accepted recall downgrade."
            )
            warnings.append(message)
        findings_by_priority = payload.get("findings_by_priority") if isinstance(payload.get("findings_by_priority"), dict) else {}
        candidates_by_priority = payload.get("candidates_by_priority") if isinstance(payload.get("candidates_by_priority"), dict) else {}
        non_p1_findings = sum(int(findings_by_priority.get(priority, 0) or 0) for priority in ("P2", "P3", "P4"))
        non_p1_candidates = sum(int(candidates_by_priority.get(priority, 0) or 0) for priority in ("P2", "P3", "P4"))
        if finding_count > 0 and non_p1_findings == 0 and non_p1_candidates > 0 and not critical_only_scope:
            warnings.append(
                f"{CANDIDATE_INDEX_FILE}: submitted findings are P1-only while lower-priority candidates exist. "
                "This can be valid, but candidate-coverage.md must make their parked/refuted/missing-gate outcomes clear."
            )
        unknown_priority = payload.get("unknown_priority_candidate_count")
        unknown_outcome = payload.get("unknown_outcome_candidate_count")
        if isinstance(unknown_priority, int) and unknown_priority > 0:
            warnings.append(
                f"{CANDIDATE_INDEX_FILE}: {unknown_priority} candidate entries lack a priority estimate; "
                "P1-saturation checks are weaker without P1-P4 candidate tags."
            )
        if isinstance(unknown_outcome, int) and unknown_outcome > 0:
            warnings.append(
                f"{CANDIDATE_INDEX_FILE}: {unknown_outcome} candidate entries lack an outcome; "
                "mark promoted, parked, refuted, or merged during the promotion sweep."
            )

    repos = payload.get("repos")
    if not isinstance(repos, list):
        errors.append(f"{CANDIDATE_INDEX_FILE}: repos must be a list")
    else:
        index_profiles = {str(item.get("profile_name", "")) for item in repos if isinstance(item, dict)}
        missing = sorted(shard_repos - index_profiles)
        if missing:
            errors.append(f"{CANDIDATE_INDEX_FILE}: missing repo candidate rows: " + ", ".join(missing[:12]))
        for item in repos:
            if not isinstance(item, dict):
                continue
            profile = str(item.get("profile_name", "unknown"))
            candidate_count = item.get("candidate_count")
            explicit_count = item.get("explicit_candidate_entries")
            submitted = item.get("submitted_bug_ids")
            submitted_count = len(submitted) if isinstance(submitted, list) else 0
            if not isinstance(explicit_count, int) or explicit_count < 0:
                errors.append(
                    f"{CANDIDATE_INDEX_FILE}: repo {profile} missing explicit_candidate_entries; "
                    "regenerate with generate_candidate_index.py"
                )
                continue
            if isinstance(candidate_count, int) and candidate_count > explicit_count + submitted_count:
                errors.append(
                    f"{CANDIDATE_INDEX_FILE}: repo {profile} candidate_count ({candidate_count}) "
                    f"exceeds explicit candidate entries plus submitted Bugs ({explicit_count + submitted_count})"
                )
            gate_complete = item.get("gate_complete_unsubmitted_candidates")
            if gate_complete is not None and not isinstance(gate_complete, list):
                errors.append(f"{CANDIDATE_INDEX_FILE}: repo {profile} gate_complete_unsubmitted_candidates must be a list")

    if coverage_path.is_file():
        text = coverage_path.read_text(encoding="utf-8", errors="replace")
        for required in ("Candidate Funnel", "Priority Promotion Sweep", "Repository Candidate Coverage"):
            if required not in text:
                errors.append(f"{CANDIDATE_COVERAGE_FILE}: missing section {required!r}")
        if str(index_total) not in text:
            warnings.append(f"{CANDIDATE_COVERAGE_FILE}: candidate total is not visibly recorded")
    return errors, warnings


def check_issue_family_coverage(
    root: Path,
    workspace_root: Path,
    expected_repo_items: list[dict],
) -> tuple[list[str], list[str]]:
    """Validate the fresh-run issue-family matrix without prescribing families."""
    errors: list[str] = []
    warnings: list[str] = []
    path = root / ISSUE_FAMILY_COVERAGE_FILE
    if not path.is_file():
        errors.append(
            f"Missing fresh-run issue-family coverage matrix: {ISSUE_FAMILY_COVERAGE_FILE}; "
            "deep or multi-repository audits must show which risk families were promoted, parked, refuted, or had no credible hits"
        )
        return errors, warnings

    text = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"Issue Family Coverage|问题家族覆盖|风险家族覆盖", text, flags=re.IGNORECASE):
        errors.append(f"{ISSUE_FAMILY_COVERAGE_FILE}: missing Issue Family Coverage heading")
    if not re.search(r"fresh[- ]run|first[- ]run|independent scan|首次|独立扫描|新扫描", text, flags=re.IGNORECASE):
        errors.append(
            f"{ISSUE_FAMILY_COVERAGE_FILE}: must state that the matrix comes from the fresh current-source scan, "
            "not from historical package reuse"
        )

    rows = parse_markdown_issue_family_rows(text)
    if not rows:
        errors.append(
            f"{ISSUE_FAMILY_COVERAGE_FILE}: missing issue-family table with columns "
            "Family, Fresh Sources, Outcome, Evidence"
        )
        return errors, warnings
    for index, row in enumerate(rows, 1):
        family = strip_table_cell(row.get("family", ""))
        sources = strip_table_cell(row.get("sources", ""))
        outcome = strip_table_cell(row.get("outcome", ""))
        evidence = strip_table_cell(row.get("evidence", ""))
        label = family or f"row {index}"
        if issue_family_cell_missing(family):
            errors.append(f"{ISSUE_FAMILY_COVERAGE_FILE}: issue-family row {index} has no family name")
        if issue_family_cell_missing(sources):
            errors.append(f"{ISSUE_FAMILY_COVERAGE_FILE}: issue-family {label} needs fresh source/surface evidence")
        if not ISSUE_FAMILY_OUTCOME_RE.search(outcome):
            errors.append(
                f"{ISSUE_FAMILY_COVERAGE_FILE}: issue-family {label} needs an outcome "
                "(promoted, parked, refuted, merged, no-hit, not-applicable, or out-of-scope)"
            )
        if issue_family_cell_missing(evidence):
            errors.append(f"{ISSUE_FAMILY_COVERAGE_FILE}: issue-family {label} needs evidence or a no-hit explanation")
            continue
        if re.search(r"\b(promoted|parked|refuted|merged)\b|提交|候选|排除|合并|保留", outcome, re.IGNORECASE):
            if not (has_code_anchor(evidence) or "BUG-" in evidence):
                warnings.append(
                    f"{ISSUE_FAMILY_COVERAGE_FILE}: issue-family {label} should cite a code anchor or submitted Bug id"
                )
    return errors, warnings


def check_high_recall_scan(workspace_root: Path, expected_repo_items: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if len(expected_repo_items) <= 1:
        return errors, warnings

    json_path = workspace_root / HIGH_RECALL_SCAN_JSON
    md_path = workspace_root / HIGH_RECALL_SCAN_MD
    if not json_path.is_file():
        errors.append(
            f"Missing high-recall search seed index: {HIGH_RECALL_SCAN_JSON}; "
            "generate LLM patterns after initial exploration, then run run_high_recall_scan.py against repo-scan-roots.txt"
        )
        return errors, warnings
    if not md_path.is_file():
        errors.append(f"Missing high-recall search seed summary: {HIGH_RECALL_SCAN_MD}")

    payload, error = load_json_file(json_path)
    if error or not isinstance(payload, dict):
        errors.append(f"{HIGH_RECALL_SCAN_JSON} is not valid JSON: {error}")
        return errors, warnings

    repo_count = payload.get("repo_count")
    if repo_count != len(expected_repo_items):
        errors.append(
            f"{HIGH_RECALL_SCAN_JSON}: repo_count ({repo_count}) does not match frozen roster ({len(expected_repo_items)})"
        )
    total_hits = payload.get("total_hits")
    if not isinstance(total_hits, int) or total_hits < 0:
        errors.append(f"{HIGH_RECALL_SCAN_JSON}: total_hits must be a non-negative integer")
    patterns = payload.get("patterns")
    if not isinstance(patterns, list) or not patterns:
        errors.append(f"{HIGH_RECALL_SCAN_JSON}: patterns must contain at least one LLM-generated pattern")

    repos = payload.get("repos")
    if not isinstance(repos, list):
        errors.append(f"{HIGH_RECALL_SCAN_JSON}: repos must be a list")
        return errors, warnings
    index_profiles = {str(item.get("profile_name", "")) for item in repos if isinstance(item, dict)}
    expected_profiles = {str(item["profile_name"]) for item in expected_repo_items}
    missing = sorted(expected_profiles - index_profiles)
    if missing:
        errors.append(f"{HIGH_RECALL_SCAN_JSON}: missing repository scan rows: " + ", ".join(missing[:12]))

    scan_error_rows: list[str] = []
    for item in repos:
        if not isinstance(item, dict):
            continue
        raw_errors = item.get("errors")
        if isinstance(raw_errors, list):
            repo_errors = [str(value).strip() for value in raw_errors if str(value).strip()]
        elif raw_errors:
            repo_errors = [str(raw_errors).strip()]
        else:
            repo_errors = []
        if repo_errors:
            label = str(item.get("profile_name") or item.get("repo") or "<unknown>")
            scan_error_rows.append(f"{label}: {repo_errors[0]}")
    if scan_error_rows:
        preview = "; ".join(scan_error_rows[:5])
        if len(scan_error_rows) > 5:
            preview += f"; ... (+{len(scan_error_rows) - 5} more)"
        if isinstance(total_hits, int) and total_hits == 0:
            errors.append(
                f"{HIGH_RECALL_SCAN_JSON}: scan recorded errors and produced zero hits; "
                f"fix the LLM-generated patterns or scanner setup, then rerun. Sample: {preview}"
            )
        else:
            warnings.append(
                f"{HIGH_RECALL_SCAN_JSON}: scan recorded errors for {len(scan_error_rows)} repo row(s); "
                f"verify failed patterns were intentionally skipped. Sample: {preview}"
            )

    for profile_name in sorted(expected_profiles):
        seed_path = workspace_root / "work/shards" / profile_name / "search-seeds.md"
        if not seed_path.is_file():
            errors.append(f"Missing per-shard high-recall seed file: work/shards/{profile_name}/search-seeds.md")
            continue
        seed_text = seed_path.read_text(encoding="utf-8", errors="replace")
        if "high-recall exploration seeds" not in seed_text and "Search Seeds" not in seed_text:
            warnings.append(f"work/shards/{profile_name}/search-seeds.md does not look like a high-recall seed file")

    if md_path.is_file():
        md_text = md_path.read_text(encoding="utf-8", errors="replace")
        for required in ("High-recall Search Seeds", "Repository Seeds"):
            if required not in md_text:
                errors.append(f"{HIGH_RECALL_SCAN_MD}: missing section {required!r}")
    return errors, warnings


FINAL_MARKDOWN_SCRIPT_MARKERS = {
    "findings": [
        r"findings/P[1-4]",
        r"SUBMIT\s*/\s*[\"']findings[\"']",
        r"submit/.*/?findings",
    ],
    "repo_profiles": [
        r"knowledge/repo-profiles",
        r"SUBMIT\s*/\s*[\"']knowledge[\"']\s*/\s*[\"']repo-profiles[\"']",
    ],
    "quality": [
        r"quality/(lens-coverage|depth-coverage|submission-scope|repository-versions)",
        r"SUBMIT\s*/\s*[\"']quality[\"']",
    ],
    "knowledge": [
        r"knowledge/(system-overview|repo-relationship-map|risk-paths|architecture-design-review)",
        r"SUBMIT\s*/\s*[\"']knowledge[\"']",
    ],
    "readme": [
        r"README\.md",
        r"SUBMIT\s*/\s*[\"']README\.md[\"']",
    ],
}


def script_final_markdown_categories(text: str) -> set[str]:
    categories: set[str] = set()
    if not re.search(r"\b(write_text|open\s*\(|Path\s*\().*", text, re.DOTALL):
        return categories
    if not re.search(r"\bwrite_text\s*\(|\bopen\s*\([^)]*[\"']w", text):
        return categories
    for category, patterns in FINAL_MARKDOWN_SCRIPT_MARKERS.items():
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
            categories.add(category)
    return categories


def check_package_writer_scripts(workspace_root: Path) -> list[str]:
    errors: list[str] = []
    work_root = workspace_root / "work"
    if not work_root.is_dir():
        return errors
    for script_path in sorted(work_root.rglob("*.py")):
        if any(part in {"__pycache__", "node_modules"} for part in script_path.parts):
            continue
        text = script_path.read_text(encoding="utf-8", errors="replace")
        categories = script_final_markdown_categories(text)
        suspicious_name = re.search(
            r"(write|generate|build|make|render).*(package|evidence|docs|final|handoff|deliverable)|"
            r"(package|evidence|docs|final|handoff|deliverable).*(write|generate|build|make|render)",
            script_path.name,
            re.IGNORECASE,
        )
        if len(categories) >= 2 or (categories and suspicious_name):
            errors.append(
                f"{script_path.relative_to(workspace_root)} appears to mass-generate final Markdown deliverables "
                f"({', '.join(sorted(categories))}); write findings/profiles/depth/lens coverage "
                "incrementally from shard evidence instead"
            )
    return errors


def lens_sort_key(lens_id: str) -> tuple[int, int]:
    if lens_id.startswith("L") and lens_id[1:].isdigit():
        return (3, int(lens_id[1:]))
    if lens_id in BOUNDARY_ORDER:
        return (0, BOUNDARY_ORDER.index(lens_id))
    if lens_id.startswith("META-") and lens_id[-1:].isdigit():
        return (1, int(lens_id[-1]))
    return (2, 999)


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


def has_heading_alias(text: str, aliases: list[str]) -> bool:
    for alias in aliases:
        if re.search(rf"^#{{2,4}}\s+{re.escape(alias)}\s*$", text, flags=re.MULTILINE | re.IGNORECASE):
            return True
    return False


def missing_profile_sections(text: str) -> list[str]:
    missing = []
    for canonical, aliases in PROFILE_REQUIRED_SECTION_ALIASES:
        if not has_heading_alias(text, aliases):
            missing.append(canonical)
    return missing


def missing_depth_sections(text: str, require_roster_gate: bool) -> list[str]:
    missing = []
    for canonical, aliases in DEPTH_COVERAGE_SECTION_ALIASES:
        if canonical == "Repository Roster Gate" and not require_roster_gate:
            continue
        if not has_heading_alias(text, aliases):
            missing.append(canonical)
    return missing


def check_depth_coverage(
    text: str,
    profile_paths: list[Path],
    index_payload: dict | None,
    expected_repo_items: list[dict] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate the deep/multi-repo coverage ledger."""
    errors: list[str] = []
    warnings: list[str] = []
    expected_count = len(expected_repo_items or [])
    require_roster_gate = expected_count > 1 or len(profile_paths) > 1
    missing_sections = missing_depth_sections(text, require_roster_gate)
    if missing_sections:
        errors.append(
            f"{DEPTH_COVERAGE_FILE}: missing required sections: "
            + ", ".join(missing_sections)
        )

    profile_repos = [p.stem for p in profile_paths]
    for repo in profile_repos:
        if repo not in text:
            errors.append(f"{DEPTH_COVERAGE_FILE}: missing repo coverage row/text for profile: {repo}")
    for repo_item in expected_repo_items or []:
        if not text_mentions_alias(text, repo_aliases(repo_item)):
            errors.append(
                f"{DEPTH_COVERAGE_FILE}: missing discovered repo coverage row/text: "
                f"{repo_item['display_name']} (expected profile {repo_item['profile_name']})"
            )

    if not re.search(r"Historical Baselines|历史审计基线", text, flags=re.IGNORECASE):
        errors.append(f"{DEPTH_COVERAGE_FILE}: missing historical baseline section")
    if not re.search(
        r"reviewed for contrast|excluded|none found|reviewed|未发现|对照|已审阅|排除",
        text,
        flags=re.IGNORECASE,
    ):
        errors.append(
            f"{DEPTH_COVERAGE_FILE}: historical baselines must state reviewed-for-contrast/excluded/none-found status"
        )
    if re.search(r"\b(imported|copied|reused)\b|导入|复制|复用", text, flags=re.IGNORECASE):
        errors.append(
            f"{DEPTH_COVERAGE_FILE}: fresh deep audits must not import/copy/reuse previous audit structure; "
            "historical baselines are contrast-only unless the user explicitly requested repackaging"
        )

    if index_payload and isinstance(index_payload.get("repo"), dict):
        finding_repos = set(index_payload.get("repo", {}).keys())
        zero_finding_repos = [repo for repo in profile_repos if repo not in finding_repos]
        if zero_finding_repos and not re.search(r"Zero-finding Repos|零 Bug 仓", text, flags=re.IGNORECASE):
            errors.append(f"{DEPTH_COVERAGE_FILE}: zero-finding repos exist but no zero-finding section found")
        for repo in zero_finding_repos:
            if repo not in text:
                errors.append(f"{DEPTH_COVERAGE_FILE}: zero-finding repo missing rationale: {repo}")
        if len(finding_repos - set(profile_repos) - {"cross-repo"}) > 0:
            warnings.append(
                f"{DEPTH_COVERAGE_FILE}: index has finding repos without matching profiles: "
                + ", ".join(sorted(finding_repos - set(profile_repos) - {"cross-repo"}))
            )

    if expected_count > 1 and not re.search(
        r"Coverage Classification|覆盖分类|first[- ]pass|focused|deep[- ]complete|首轮|聚焦|深度完成",
        text,
        flags=re.IGNORECASE,
    ):
        errors.append(
            f"{DEPTH_COVERAGE_FILE}: repo-group coverage must state coverage classification "
            "(first-pass/focused/deep-complete)"
        )
    if expected_count >= 10 and not re.search(
        r"Repo Shard Plan|Shard|shard|parallel|serial|分片|并行|串行|任务拆分",
        text,
        flags=re.IGNORECASE,
    ):
        errors.append(
            f"{DEPTH_COVERAGE_FILE}: large repo-group coverage must document a repo shard/parallelization plan"
        )
    if expected_count >= 10 and not re.search(
        r"first[- ]pass|focused|deep|complete|首轮|第一阶段|聚焦|深度|完整|完成",
        text,
        flags=re.IGNORECASE,
    ):
        warnings.append(
            f"{DEPTH_COVERAGE_FILE}: large repo group should state coverage classification "
            "(first-pass/focused/deep-complete) in the depth conclusion"
        )

    if re.search(r"\b(TODO|TBD|xxx)\b", text, flags=re.IGNORECASE):
        errors.append(f"{DEPTH_COVERAGE_FILE}: unresolved placeholder marker found")
    return errors, warnings


def extract_depth_intent(scope_text: str) -> str:
    match = DEPTH_INTENT_RE.search(scope_text)
    if match:
        return match.group(2).strip()
    return ""


def scope_records_requested_deep(scope_text: str) -> bool:
    return bool(REQUESTED_DEEP_RE.search(scope_text))


def check_depth_intent_gate(scope_text: str, depth_text: str, final_assets_expected: bool) -> list[str]:
    errors: list[str] = []
    if not final_assets_expected:
        return errors
    intent = extract_depth_intent(scope_text)
    if not intent:
        errors.append(
            "quality/submission-scope.md must record audit depth intent before final report assets "
            "(for example: Audit depth intent: deep | first-pass | focused | lightweight | custom)"
        )
        return errors
    if intent.lower() in {"pending", "unknown", "todo", "tbd", "待确认", "未知"}:
        errors.append(f"quality/submission-scope.md audit depth intent is unresolved: {intent}")
        return errors
    requested_deep = bool(DEEP_INTENT_RE.search(intent) or scope_records_requested_deep(scope_text))
    if scope_records_requested_deep(scope_text) and not DEEP_INTENT_RE.search(intent):
        errors.append(
            "Depth intent mismatch: submission-scope.md says the user requested deep/full/per-repo analysis, "
            "but audit depth intent was rewritten to a non-deep value. Keep requested depth intent separate "
            "from delivered coverage classification; record user-accepted downgrade before final report assets."
        )
    if requested_deep and not depth_text.strip():
        errors.append(
            f"Depth intent mismatch: requested depth is deep/full/per-repo, but {DEPTH_COVERAGE_FILE} is missing or empty."
        )
        return errors
    if requested_deep and depth_coverage_is_partial(depth_text):
        if not (DOWNGRADE_ACCEPTED_RE.search(scope_text) or DOWNGRADE_ACCEPTED_RE.search(depth_text)):
            errors.append(
                "Depth intent mismatch: requested depth is deep/full/per-repo, but depth coverage is "
                "first-pass/focused/in-progress. Continue exploration or record that the user accepted "
                "a depth downgrade before final HTML/overview handoff."
            )
    return errors


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


def has_verification_command_or_marker(body: str) -> bool:
    normalized = body.lower()
    return bool(
        re.search(r"`[^`]+`", body)
        or "未确认" in body
        or "not confirmed" in normalized
        or "unconfirmed" in normalized
    )


def normalize_lens_heading(header: str) -> tuple[str | None, bool]:
    legacy = re.search(r"\b(L\d{1,2})\b", header)
    if legacy:
        return legacy.group(1), True
    meta = re.search(r"\b(META-[12])\b", header, flags=re.IGNORECASE)
    if meta:
        return meta.group(1).upper(), False
    boundary = re.match(r"Boundary:\s*(.+)|(.+)", header.strip(), flags=re.IGNORECASE)
    if not boundary:
        return None, False
    name = (boundary.group(1) or boundary.group(2)).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    return name or None, False


def block_has_section_alias(block: str, aliases: list[str]) -> bool:
    lowered = block.lower()
    return any(alias.lower() in lowered for alias in aliases)


def check_lens_coverage(
    text: str,
    language: str,
    expected_lens: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Parse lens-coverage.md content. Return (errors, warnings).

    Accepts the current boundary format ('### Boundary: API Contract') and
    legacy L1-L19 records for old packages.
    """
    errors: list[str] = []
    warnings: list[str] = []
    section_aliases = LENS_COVERAGE_SECTION_ALIASES[language]
    blocks = re.split(r"^###\s+", text, flags=re.MULTILINE)
    declared_lens: list[str] = []
    for block in blocks[1:]:
        header = block.split("\n", 1)[0]
        lens_id, legacy = normalize_lens_heading(header)
        if not lens_id:
            continue
        if legacy:
            warnings.append(
                f"lens-coverage.md: legacy lens heading {lens_id} is accepted for compatibility; prefer architecture boundaries"
            )
        elif lens_id not in VALID_LENS:
            warnings.append(f"lens-coverage.md: custom boundary '{lens_id}' is outside the default 13-boundary set")
        declared_lens.append(lens_id)
        for section_name, aliases in section_aliases.items():
            if not block_has_section_alias(block, aliases):
                errors.append(f"lens-coverage.md: lens {lens_id} record missing section '{section_name}'")
        if "无未覆盖" in block or "no uncovered" in block.lower():
            warnings.append(f"lens-coverage.md: lens {lens_id} claims no uncovered area; honest-uncertainty markers preferred")
    if not declared_lens:
        errors.append("lens-coverage.md present but contains no lens record (expected '### Boundary: API Contract' or META heading)")
    if expected_lens:
        declared = set(declared_lens)
        missing = sorted(expected_lens - declared, key=lens_sort_key)
        if missing:
            errors.append(
                "lens-coverage.md missing enabled lens records: "
                + ", ".join(missing)
                + " (use --lens-scope custom only when submission-scope.md declares a narrowed strategy)"
            )
    return errors, warnings


def mermaid_node_ids(block: str) -> set[str]:
    """Best-effort Mermaid node extraction for guardrail warnings.

    Counts both shaped declarations (`A[Label]`) and edge-only nodes (`A --> B`).
    This is intentionally lightweight; it warns on obvious oversize diagrams without
    trying to be a full Mermaid parser.
    """
    node_ids: set[str] = set()
    for raw_line in block.splitlines():
        line = raw_line.split("%%", 1)[0].strip()
        if not line:
            continue
        node_ids.update(MERMAID_DECL_RE.findall(line))
        if "--" not in line and "-." not in line and "==" not in line:
            continue
        without_edge_labels = re.sub(r"\|[^|]*\|", " ", line)
        without_shape_labels = re.sub(r"\[[^\]]*\]|\([^)]*\)|\{[^}]*\}", " ", without_edge_labels)
        for token in MERMAID_ID_RE.findall(without_shape_labels):
            if token not in MERMAID_KEYWORDS:
                node_ids.add(token)
    return node_ids


def check_mermaid_guards(text: str, rel_path: str) -> list[str]:
    """Light WARN-level checks on mermaid blocks (per call-graph-conventions.md)."""
    warnings: list[str] = []
    blocks = re.findall(r"```mermaid\n(.*?)```", text, re.DOTALL)
    for idx, block in enumerate(blocks, 1):
        node_ids = mermaid_node_ids(block)
        if len(node_ids) > 30:
            warnings.append(f"{rel_path} mermaid block #{idx}: {len(node_ids)} nodes exceeds guardrail of 30; consider splitting")
        block_end = text.find("```", text.find(block) + len(block) - 10)
        tail = text[block_end : block_end + 600] if block_end >= 0 else ""
        if not re.search(r"Uncovered|未覆盖", tail):
            warnings.append(f"{rel_path} mermaid block #{idx}: missing 'Uncovered' / '未覆盖' paragraph within ~600 chars after the diagram (per call-graph-conventions.md)")
    return warnings


def check_repo_profile_guards(text: str, rel_path: str) -> list[str]:
    warnings = check_mermaid_guards(text, rel_path)
    if "```mermaid" in text:
        return warnings
    if re.search(r"调用图豁免|Call Graph Exemption", text, re.IGNORECASE):
        return warnings
    warnings.append(
        f"{rel_path}: missing mermaid call graph; use a documented small-repo call graph exemption when the repo has <=10 files"
    )
    return warnings


def profile_generic_errors(text: str, rel_path: str) -> list[str]:
    errors: list[str] = []
    for pattern in GENERIC_PROFILE_PATTERNS:
        if pattern in text:
            errors.append(f"{rel_path}: contains generic profile placeholder text: {pattern[:80]}")
    return errors


def compact_css(text: str) -> str:
    return re.sub(r"\s+", "", text)


def css_block(text: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", text, flags=re.DOTALL)
    return match.group(1) if match else ""


def css_property(block: str, property_name: str) -> str:
    match = re.search(rf"{re.escape(property_name)}\s*:\s*([^;]+)", block)
    return match.group(1).strip() if match else ""


def css_px_number(value: str) -> float | None:
    match = re.match(r"(-?\d+(?:\.\d+)?)px$", value.strip())
    return float(match.group(1)) if match else None


def css_padding_bottom_px(value: str) -> float | None:
    parts = value.split()
    if not parts:
        return None
    bottom_index = 0 if len(parts) <= 2 else 2
    return css_px_number(parts[bottom_index])


def check_html_design_contract(text: str) -> list[str]:
    errors: list[str] = []
    compact = compact_css(text)
    if compact_css(HTML_TOP_NAV_GRADIENT) not in compact:
        errors.append(
            f"{HTML_REPORT_FILE}: top navigation must keep the approved theme gradient: {HTML_TOP_NAV_GRADIENT}"
        )
    if compact_css(HTML_TOTAL_METRIC_BACKGROUND) not in compact:
        errors.append(
            f"{HTML_REPORT_FILE}: total Bug metric card must keep the approved neutral-light background: "
            f"{HTML_TOTAL_METRIC_BACKGROUND}"
        )

    shell_padding = css_property(css_block(text, ".shell"), "padding")
    shell_bottom = css_padding_bottom_px(shell_padding)
    if shell_bottom is None:
        errors.append(f"{HTML_REPORT_FILE}: cannot verify .shell bottom padding")
    elif shell_bottom > HTML_MAX_SHELL_BOTTOM_PADDING_PX:
        errors.append(
            f"{HTML_REPORT_FILE}: .shell bottom padding too large: {shell_bottom:g}px "
            f"(max {HTML_MAX_SHELL_BOTTOM_PADDING_PX}px)"
        )

    footer_margin = css_property(css_block(text, ".report-footer"), "margin-top")
    footer_margin_top = css_px_number(footer_margin)
    if footer_margin_top is None:
        errors.append(f"{HTML_REPORT_FILE}: cannot verify footer top margin")
    elif footer_margin_top > HTML_MAX_FOOTER_MARGIN_TOP_PX:
        errors.append(
            f"{HTML_REPORT_FILE}: footer top margin too large: {footer_margin_top:g}px "
            f"(max {HTML_MAX_FOOTER_MARGIN_TOP_PX}px)"
        )
    return errors


def check_html_report(text: str, index_payload: dict | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for section_id in REQUIRED_HTML_SECTIONS:
        if f'id="{section_id}"' not in text and f"id='{section_id}'" not in text:
            errors.append(f"{HTML_REPORT_FILE}: missing required section anchor: {section_id}")
    required_terms = ["repo-bug-audit", "github.com/aiden0z/skills", "source=static-analysis"]
    for term in required_terms:
        if term not in text:
            errors.append(f"{HTML_REPORT_FILE}: missing provenance term: {term}")
    if re.search(r"\b(TODO|TBD|xxx)\b", text, flags=re.IGNORECASE):
        errors.append(f"{HTML_REPORT_FILE}: unresolved placeholder marker found")
    external_asset = re.search(
        r"<(?:script|link|img|source|iframe)\b[^>]*(?:src|href)=['\"]https?://",
        text,
        flags=re.IGNORECASE,
    )
    if external_asset or re.search(r"url\(['\"]?https?://", text, flags=re.IGNORECASE):
        errors.append(f"{HTML_REPORT_FILE}: external asset reference found; report must be self-contained")
    errors.extend(check_html_design_contract(text))
    if index_payload:
        total = int(index_payload.get("total", 0) or 0)
        m = re.search(r'data-total-bugs=["\'](\d+)["\']', text)
        if not m:
            errors.append(f"{HTML_REPORT_FILE}: missing data-total-bugs attribute")
        elif int(m.group(1)) != total:
            errors.append(f"{HTML_REPORT_FILE}: total Bug count mismatch: html={m.group(1)}, index={total}")
        priority = index_payload.get("priority", {}) if isinstance(index_payload.get("priority"), dict) else {}
        for prio in ("p1", "p2", "p3", "p4"):
            expected = int(priority.get(prio.upper(), 0) or 0)
            m = re.search(rf'data-priority-{prio}=["\'](\d+)["\']', text)
            if not m:
                errors.append(f"{HTML_REPORT_FILE}: missing data-priority-{prio} attribute")
            elif int(m.group(1)) != expected:
                errors.append(
                    f"{HTML_REPORT_FILE}: {prio.upper()} count mismatch: html={m.group(1)}, index={expected}"
                )
    if len(text.encode("utf-8")) > 2_000_000:
        warnings.append(f"{HTML_REPORT_FILE}: file exceeds 2MB; consider reducing embedded detail")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Bug audit package")
    parser.add_argument("root", help="Bug audit output root")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="Expected Bug section language")
    parser.add_argument("--max-image-kb", type=int, default=500, help="Warn if PNG exceeds this size")
    parser.add_argument("--require-knowledge", action="store_true", help="Require reusable knowledge docs for final handoff packages")
    parser.add_argument(
        "--require-depth-coverage",
        action="store_true",
        help="Require quality/depth-coverage.md. Multi-repo final handoffs with --require-knowledge require it by default.",
    )
    parser.add_argument(
        "--validate-shards-only",
        action="store_true",
        help=(
            "Run the early repo-shard evidence gate only. Use before writing final Bug records, "
            "README, HTML, or overview assets."
        ),
    )
    parser.add_argument("--require-image", action="store_true", help="Require audit-overview.png for final handoff packages")
    parser.add_argument("--require-html-report", action="store_true", help="Require bug-audit-report.html for final handoff packages")
    parser.add_argument("--banned", action="append", default=[], help="Additional banned text")
    parser.add_argument(
        "--repo-root",
        action="append",
        default=[],
        help=(
            "Path to a target repository checkout or a parent directory containing multiple repo checkouts. "
            "Enables roster coverage and frontmatter `files[].path` existence checks. "
            "May be repeated for multi-repo audits."
        ),
    )
    parser.add_argument(
        "--repo-discovery-depth",
        type=int,
        default=2,
        help="Depth to search below non-Git --repo-root directories when discovering repo-group rosters.",
    )
    parser.add_argument(
        "--allow-missing-repo-root",
        action="store_true",
        help=(
            "Allow final validation without --repo-root. Reserved for non-local source snapshots; "
            "record the reason in quality/submission-scope.md."
        ),
    )
    parser.add_argument(
        "--require-lens-coverage",
        action="store_true",
        help=(
            "Deprecated compatibility flag. Lens coverage is required by default; "
            "use --skip-lens-coverage for in-progress / resume runs only."
        ),
    )
    parser.add_argument(
        "--skip-lens-coverage",
        action="store_true",
        help="Skip required submit/quality/lens-coverage.md check. Reserved for in-progress / resume runs only.",
    )
    parser.add_argument(
        "--lens-scope",
        choices=["auto", "single", "multi", "custom"],
        default="auto",
        help=(
            "Expected lens set for lens-coverage.md. auto uses repo-profile count. "
            "Accepts 13-boundary identifiers and META-1/2; legacy L1-L19 records are compatibility-only. "
            "Use custom only when submission-scope.md declares a narrowed strategy."
        ),
    )
    parser.add_argument(
        "--allow-id-gaps",
        action="store_true",
        help="Allow non-contiguous BUG-xxxx IDs. Reserved for in-progress / resume runs only; final delivery must be contiguous BUG-0001..BUG-N",
    )
    parser.add_argument(
        "--coverage-mode",
        choices=["deep", "batch-first-pass"],
        default="deep",
        help=(
            "Coverage strictness for shard validation. deep (default): minimum evidence contract plus depth warnings. "
            "batch-first-pass: same authenticity checks with relaxed depth warnings "
            "for multi-repo first-pass scans. See references/shard-schema.md."
        ),
    )
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if (root / "submit").is_dir() and not (root / "findings").is_dir():
        root = root / "submit"
    errors = []
    warnings = []
    index_payload_for_html = None
    index_repo_counts: dict[str, object] | None = None
    audit_scope_payload: dict | None = None
    workspace_root = audit_workspace_root(root)
    if args.require_lens_coverage and args.skip_lens_coverage:
        errors.append("Cannot combine --require-lens-coverage with --skip-lens-coverage")
    if args.require_knowledge and not args.repo_root and not args.allow_missing_repo_root:
        errors.append(
            "Final handoff validation with --require-knowledge must include --repo-root so roster and path checks can run "
            "(use --allow-missing-repo-root only for non-local source snapshots and record the reason in submission-scope.md)"
        )
    repo_roots = [Path(p).expanduser().resolve() for p in args.repo_root] if args.repo_root else []
    missing_repo_roots = [str(path) for path in repo_roots if not path.exists()]
    for path in missing_repo_roots:
        warnings.append(f"--repo-root path does not exist and cannot be used for roster/path validation: {path}")
    expected_repo_items = discover_expected_repos(repo_roots, args.repo_discovery_depth)
    path_check_roots = repo_roots + [
        Path(item["path"]).expanduser().resolve()
        for item in expected_repo_items
        if item.get("path")
    ]
    html_report_exists = (root / HTML_REPORT_FILE).is_file()
    overview_image_exists = (root / "audit-overview.png").is_file()
    submitted_findings_exist = any((root / "findings").glob("P[1-4]/*.md"))
    final_asset_validation = args.require_html_report or args.require_image or html_report_exists or overview_image_exists
    repo_group_strong_validation = (
        len(expected_repo_items) > 1
        and (args.require_knowledge or final_asset_validation or submitted_findings_exist)
    )
    scope_baseline_validation = bool(expected_repo_items) and (
        repo_group_strong_validation or final_asset_validation or args.require_depth_coverage
    )

    if args.validate_shards_only:
        if not repo_roots and not args.allow_missing_repo_root:
            errors.append("--validate-shards-only requires --repo-root unless --allow-missing-repo-root is recorded")
        if not expected_repo_items:
            errors.append("--validate-shards-only could not discover any repos from --repo-root")
        inventory_path = workspace_root / "work/scanner-output/repo-inventory.json"
        shards_plan_path = workspace_root / "work/scanner-output/repo-shards.md"
        if not inventory_path.is_file():
            errors.append("Missing frozen repo roster: work/scanner-output/repo-inventory.json")
        if not shards_plan_path.is_file():
            errors.append("Missing repo shard plan: work/scanner-output/repo-shards.md")
        errors.extend(check_scan_roots_file(workspace_root, expected_repo_items))
        high_recall_errors, high_recall_warnings = check_high_recall_scan(workspace_root, expected_repo_items)
        errors.extend(high_recall_errors)
        warnings.extend(high_recall_warnings)
        shard_errors, shard_warnings = check_shard_summaries(workspace_root, expected_repo_items, repo_roots, args.coverage_mode)
        errors.extend(shard_errors)
        warnings.extend(shard_warnings)
        errors.extend(check_package_writer_scripts(workspace_root))
        receipt_path = workspace_root / SHARD_GATE_RECEIPT_FILE
        if not errors:
            write_shard_gate_receipt(workspace_root, root, expected_repo_items)
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
        if not errors:
            print(f"Shard gate receipt: {receipt_path}")
        return 1 if errors else 0

    for d in REQUIRED_DIRS:
        if not (root / d).is_dir():
            errors.append(f"Missing directory: {d}")
    for f in REQUIRED_FILES:
        if not (root / f).is_file():
            errors.append(f"Missing file: {f}")
    submission_scope_text = ""
    submission_scope_path = root / "quality/submission-scope.md"
    if submission_scope_path.is_file():
        submission_scope_text = submission_scope_path.read_text(encoding="utf-8", errors="replace")
    readme_text = ""
    readme_path = root / "README.md"
    if readme_path.is_file():
        readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
    early_finding_count = len(list((root / "findings").glob("P*/*.md")))
    if final_asset_validation:
        has_overview_label = re.search(
            r"audit-overview|overview image|概览图|概览图片|总览图",
            submission_scope_text,
            flags=re.IGNORECASE,
        )
        has_overview_decision = any(value in submission_scope_text for value in OVERVIEW_DECISION_VALUES)
        if args.require_image or overview_image_exists:
            if not has_overview_label or not has_overview_decision:
                errors.append(
                    "quality/submission-scope.md must record audit-overview.png decision "
                    f"({', '.join(sorted(OVERVIEW_DECISION_VALUES))}) before requiring or submitting the image"
                )
        elif not has_overview_label or not has_overview_decision:
            warnings.append(
                "quality/submission-scope.md should record audit-overview.png as deferred-post-handoff "
                "or omitted; final validation no longer blocks on the optional overview image decision"
            )
    if repo_group_strong_validation:
        inventory_path = workspace_root / "work/scanner-output/repo-inventory.json"
        shards_plan_path = workspace_root / "work/scanner-output/repo-shards.md"
        if not inventory_path.is_file():
            errors.append("Missing frozen repo roster: work/scanner-output/repo-inventory.json")
        if not shards_plan_path.is_file():
            errors.append("Missing repo shard plan: work/scanner-output/repo-shards.md")
        errors.extend(check_scan_roots_file(workspace_root, expected_repo_items))
        high_recall_errors, high_recall_warnings = check_high_recall_scan(workspace_root, expected_repo_items)
        errors.extend(high_recall_errors)
        warnings.extend(high_recall_warnings)
        shard_errors, shard_warnings = check_shard_summaries(workspace_root, expected_repo_items, repo_roots, args.coverage_mode)
        errors.extend(shard_errors)
        warnings.extend(shard_warnings)
        if not args.validate_shards_only:
            candidate_errors, candidate_warnings = check_candidate_index(
                root,
                workspace_root,
                expected_repo_items,
                early_finding_count,
            )
            errors.extend(candidate_errors)
            warnings.extend(candidate_warnings)
        receipt_errors, receipt_warnings = check_shard_gate_receipt(
            workspace_root,
            root,
            expected_repo_items,
            require_asset_order=final_asset_validation,
        )
        errors.extend(receipt_errors)
        warnings.extend(receipt_warnings)
    prepackage_errors, prepackage_warnings = check_prepackage_receipt(
        workspace_root,
        root,
        require_asset_order=final_asset_validation,
    )
    errors.extend(prepackage_errors)
    warnings.extend(prepackage_warnings)
    if args.require_knowledge or repo_group_strong_validation:
        errors.extend(check_package_writer_scripts(workspace_root))
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
        if expected_repo_items:
            missing_versions = [
                item["display_name"]
                for item in expected_repo_items
                if not text_mentions_alias(version_text, unique_repo_aliases(item, expected_repo_items))
            ]
            if missing_versions:
                errors.append(
                    "quality/repository-versions.md missing discovered repo(s) from --repo-root roster: "
                    + ", ".join(missing_versions)
                )
    for f in OPTIONAL_KNOWLEDGE_FILES:
        path = root / f
        if path.exists():
            if body_len(path) < 40:
                warnings.append(f"{f} appears empty; fill it or remove it before packaging")
    for temporary_dir in ("candidates", "eval", "infographic", "scanner-output", "drafts", "tmp"):
        if (root / temporary_dir).exists():
            errors.append(f"Temporary directory must not be in audit output: {temporary_dir}")
    profiles_dir = root / "knowledge/repo-profiles"
    profile_paths = []
    if profiles_dir.is_dir():
        profile_paths = [p for p in sorted(profiles_dir.glob("*.md")) if p.name != "README.md"]
    if not profile_paths and not args.skip_lens_coverage:
        errors.append(
            "Missing repo profiles: knowledge/repo-profiles/*.md is required for final lens-based delivery"
        )
    if expected_repo_items and not args.skip_lens_coverage:
        profile_stems = {path.stem for path in profile_paths}
        missing_profiles = [
            item["profile_name"]
            for item in expected_repo_items
            if item["profile_name"] not in profile_stems
        ]
        if missing_profiles:
            errors.append(
                "Missing repo profile(s) for discovered --repo-root roster: "
                + ", ".join(missing_profiles)
                + ". Generate one submit/knowledge/repo-profiles/<repo>.md per discovered repo, "
                "even when no Bug is submitted for that repo."
            )

    seen_ids = {}
    finding_count = 0
    repos = set()
    # Authenticity: collect long paragraphs from high-risk sections for cross-Bug duplicate detection.
    dedupe_index: dict[str, list[str]] = {}
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
                lens_value = str(lv).strip()
                if lens_value in LEGACY_LENS:
                    warnings.append(f"{rel} uses legacy lens value {lv}; prefer a 13-boundary lens id")
                elif lens_value not in VALID_LENS:
                    warnings.append(f"{rel} unrecognized lens value: {lv} (expected 13-boundary id or META-1/2)")
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
        if path_check_roots:
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
                target_repo_item = expected_repo_for_name(str(meta.get("repo", "")), expected_repo_items)
                if target_repo_item:
                    exists = file_path_exists_for_repo(rel_path, target_repo_item, repo_roots)
                else:
                    exists = any((rr / rel_path).exists() for rr in path_check_roots)
                if not exists:
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
    if args.skip_lens_coverage:
        pass
    elif lens_coverage_path.is_file():
        lc_text = lens_coverage_path.read_text(encoding="utf-8", errors="replace")
        expected_lens = None
        if args.lens_scope != "custom":
            if args.lens_scope == "single":
                expected_lens = SINGLE_REPO_DEFAULT_LENS
            elif args.lens_scope == "multi":
                expected_lens = MULTI_REPO_DEFAULT_LENS
            elif len(profile_paths) > 1 or len(expected_repo_items) > 1:
                expected_lens = MULTI_REPO_DEFAULT_LENS
            else:
                expected_lens = SINGLE_REPO_DEFAULT_LENS
        lc_errors, lc_warnings = check_lens_coverage(lc_text, args.language, expected_lens)
        errors.extend(lc_errors)
        warnings.extend(lc_warnings)
    else:
        errors.append(
            "Missing quality/lens-coverage.md (required by default; use --skip-lens-coverage only for in-progress / resume runs; see references/exploration-lenses.md)"
        )

    # Mermaid call-graph guardrail check on repo profiles (D3)
    if profile_paths:
        for profile_path in profile_paths:
            profile_rel = profile_path.relative_to(root).as_posix()
            profile_text = profile_path.read_text(encoding="utf-8", errors="replace")
            warnings.extend(check_repo_profile_guards(profile_text, profile_rel))
            generic_profile_errors = profile_generic_errors(profile_text, profile_rel)
            if args.require_knowledge or len(expected_repo_items) > 1:
                errors.extend(generic_profile_errors)
            else:
                warnings.extend(generic_profile_errors)
            missing_sections = missing_profile_sections(profile_text)
            if missing_sections:
                message = (
                    f"{profile_rel}: missing required profile sections: "
                    + ", ".join(missing_sections)
                )
                if args.require_knowledge:
                    errors.append(message)
                else:
                    warnings.append(message)

    index_json = root / "indexes/findings.generated.json"
    if index_json.is_file():
        try:
            index_payload = json.loads(index_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"indexes/findings.generated.json is not valid JSON: {exc}")
        else:
            if not isinstance(index_payload, dict):
                errors.append("indexes/findings.generated.json must be a JSON object")
                index_payload = {}
            else:
                index_payload_for_html = index_payload
                repo_counts = index_payload.get("repo")
                if isinstance(repo_counts, dict):
                    index_repo_counts = repo_counts
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

    if scope_baseline_validation:
        audit_scope_payload, audit_scope_errors = read_audit_scope_payload(root)
        errors.extend(audit_scope_errors)
        if audit_scope_payload is not None:
            errors.extend(check_audit_scope_manifest(root, audit_scope_payload, expected_repo_items, index_repo_counts))

    if scope_baseline_validation:
        scope_expected_items = scope_expected_items_from_payload(audit_scope_payload) if audit_scope_payload else expected_repo_items
        scope_repo_counts = scope_repo_counts_from_payload(audit_scope_payload) if audit_scope_payload else index_repo_counts
        errors.extend(check_readme_scope_baseline(readme_text, scope_expected_items, scope_repo_counts))

    depth_intent = extract_depth_intent(submission_scope_text)
    deep_intent_requires_depth = (
        final_asset_validation
        and bool(depth_intent)
        and depth_intent.lower() not in {"pending", "unknown", "todo", "tbd", "待确认", "未知"}
        and bool(DEEP_INTENT_RE.search(depth_intent))
    )
    depth_required = args.require_depth_coverage or deep_intent_requires_depth or (
        args.require_knowledge and (len(profile_paths) > 1 or len(expected_repo_items) > 1)
    )
    if repo_group_strong_validation or depth_required:
        family_errors, family_warnings = check_issue_family_coverage(
            root,
            workspace_root,
            expected_repo_items,
        )
        errors.extend(family_errors)
        warnings.extend(family_warnings)
    depth_coverage_path = root / DEPTH_COVERAGE_FILE
    depth_text = ""
    if depth_required and not depth_coverage_path.is_file():
        errors.append(
            f"Missing {DEPTH_COVERAGE_FILE} (required for multi-repo/deep final handoff; see references/depth-coverage.md)"
        )
    if depth_coverage_path.is_file():
        depth_text = depth_coverage_path.read_text(encoding="utf-8", errors="replace")
        depth_errors, depth_warnings = check_depth_coverage(
            depth_text,
            profile_paths,
            index_payload_for_html,
            expected_repo_items,
        )
        errors.extend(depth_errors)
        warnings.extend(depth_warnings)
    if final_asset_validation:
        errors.extend(check_depth_intent_gate(submission_scope_text, depth_text, final_asset_validation))

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

    html_report = root / HTML_REPORT_FILE
    if args.require_html_report and not html_report.is_file():
        errors.append(f"Missing required interactive HTML report: {HTML_REPORT_FILE}")
    if html_report.is_file():
        html_text = html_report.read_text(encoding="utf-8", errors="replace")
        html_errors, html_warnings = check_html_report(html_text, index_payload_for_html)
        errors.extend(html_errors)
        warnings.extend(html_warnings)
        if scope_baseline_validation:
            scope_expected_items = scope_expected_items_from_payload(audit_scope_payload) if audit_scope_payload else expected_repo_items
            scope_repo_counts = scope_repo_counts_from_payload(audit_scope_payload) if audit_scope_payload else index_repo_counts
            errors.extend(check_html_scope_baseline(html_text, scope_expected_items, scope_repo_counts))

    if not errors and not final_asset_validation:
        write_prepackage_receipt(workspace_root, root, expected_repo_items, finding_count)

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
