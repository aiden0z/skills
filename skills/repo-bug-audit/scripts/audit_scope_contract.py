"""Build and parse the audit-scope machine contract.

The contract is a reproducibility layer for final reports. It describes what
was analyzed and how many submitted Bugs each analyzed repo produced; it does
not decide which Bugs should be discovered or promoted.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
AUDIT_SCOPE_INDEX = "indexes/audit-scope.generated.json"
MISSING_VERSION_VALUES = {
    "",
    "-",
    "—",
    "unknown",
    "pending",
    "not specified",
    "n/a",
    "na",
    "tbd",
    "todo",
    "unconfirmed",
    "待采集",
    "待补充",
    "未知",
}
ROLE_EXCLUDE_RE = re.compile(
    r"\b(reference|ref|excluded|out[- ]?of[- ]?scope|comparison|baseline|sample)\b|"
    r"参考|仅参考|排除|范围外|对照|基线",
    re.IGNORECASE,
)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def strip_table_cell(value: str, limit: int = 240) -> str:
    value = html.unescape(str(value))
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"```.*?```", " ", value, flags=re.DOTALL)
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_>#]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit].strip()


def normalize_table_header(value: str) -> str:
    raw = strip_table_cell(value)
    lowered = raw.lower().replace(" ", "_").replace("-", "_")
    if "repository" in lowered or lowered == "repo" or "仓库" in raw:
        return "repository"
    if lowered == "role" or "角色" in raw:
        return "role"
    if ("audit" in lowered and "branch" in lowered) or lowered == "branch" or "审计分支" in raw or raw == "分支":
        return "audit_branch"
    if "commit" in lowered or ("提交" in raw and "bug" not in lowered):
        return "commit"
    if "dirty" in lowered or "worktree" in lowered or "工作区" in raw:
        return "dirty"
    return lowered


def parse_markdown_tables(text: str) -> list[list[dict[str, str]]]:
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
            if cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells if cell):
                continue
            if not headers:
                headers = [normalize_table_header(cell) for cell in cells]
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


def table_is_repository_versions(rows: list[dict[str, str]]) -> bool:
    return bool(rows) and {"repository", "audit_branch", "commit", "dirty"}.issubset(set(rows[0]))


def role_is_excluded(role: str) -> bool:
    role = role.strip()
    if not role:
        return False
    if re.search(r"\b(target|analyzed|audit)\b|目标|审计|分析", role, re.IGNORECASE):
        return False
    return bool(ROLE_EXCLUDE_RE.search(role))


def parse_repository_versions(text: str) -> list[dict[str, str]]:
    for rows in parse_markdown_tables(text):
        if not table_is_repository_versions(rows):
            continue
        records: list[dict[str, str]] = []
        for row in rows:
            repo = row.get("repository", "").strip()
            if not repo or repo.lower() in {"repository", "repo"}:
                continue
            if role_is_excluded(row.get("role", "")):
                continue
            if not any(row.get(key, "").strip() for key in ("audit_branch", "commit", "dirty")):
                continue
            records.append(
                {
                    "repository": repo,
                    "audit_branch": row.get("audit_branch", "").strip(),
                    "commit": row.get("commit", "").strip(),
                    "dirty": row.get("dirty", "").strip(),
                }
            )
        if records:
            return records
    return []


def version_value_missing(value: str) -> bool:
    return strip_table_cell(str(value), 80).lower() in MISSING_VERSION_VALUES


def bug_count_for_repo(repo: str, repo_counter: Counter | dict[str, Any]) -> int:
    if repo in repo_counter:
        return safe_int(repo_counter[repo])
    normalized = repo.lower()
    if "/" in normalized:
        return 0
    matches: list[int] = []
    for candidate, count in repo_counter.items():
        candidate_text = str(candidate).lower()
        if candidate_text.endswith("/" + normalized):
            matches.append(safe_int(count))
    return matches[0] if len(matches) == 1 else 0


def build_audit_scope_payload(
    repository_versions_text: str,
    findings_index_payload: dict[str, Any] | None,
    *,
    generated_by: str,
) -> dict[str, Any]:
    repo_counter = Counter()
    if findings_index_payload and isinstance(findings_index_payload.get("repo"), dict):
        repo_counter = Counter(findings_index_payload.get("repo", {}))
    records = parse_repository_versions(repository_versions_text)
    repositories = []
    complete = 0
    for record in records:
        repo = record["repository"]
        row = {
            "repository": repo,
            "audit_branch": record.get("audit_branch", ""),
            "commit": record.get("commit", ""),
            "dirty": record.get("dirty", ""),
            "submitted_bugs": bug_count_for_repo(repo, repo_counter),
        }
        if not any(version_value_missing(str(row.get(key, ""))) for key in ("audit_branch", "commit", "dirty")):
            complete += 1
        repositories.append(row)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": generated_by,
        "sources": {
            "repository_versions": "quality/repository-versions.md",
            "findings_index": "indexes/findings.generated.json",
        },
        "total_analyzed_repos": len(repositories),
        "version_evidence": {"complete": complete, "total": len(repositories)},
        "repositories": repositories,
    }


def scope_records_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("repositories")
    if not isinstance(rows, list):
        return []
    records = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        repo = strip_table_cell(row.get("repository", ""))
        if not repo:
            continue
        raw_submitted = row.get("submitted_bugs", 0)
        submitted_bugs: int | str
        try:
            submitted_bugs = int(raw_submitted or 0)
        except (TypeError, ValueError):
            submitted_bugs = strip_table_cell(raw_submitted)
        records.append(
            {
                "repository": repo,
                "audit_branch": strip_table_cell(row.get("audit_branch", "")),
                "commit": strip_table_cell(row.get("commit", "")),
                "dirty": strip_table_cell(row.get("dirty", "")),
                "submitted_bugs": submitted_bugs,
            }
        )
    return records


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate audit-scope.generated.json from final package indexes")
    parser.add_argument("root", help="Bug audit submit root")
    parser.add_argument("--output", default=AUDIT_SCOPE_INDEX, help="Output path under submit root")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if (root / "submit").is_dir() and not (root / "quality").is_dir():
        root = root / "submit"
    versions_text = read_text(root / "quality/repository-versions.md")
    if not versions_text:
        raise SystemExit("Missing quality/repository-versions.md")
    findings_index = read_json_object(root / "indexes/findings.generated.json")
    payload = build_audit_scope_payload(
        versions_text,
        findings_index,
        generated_by="audit_scope_contract.py",
    )
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated audit scope contract: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
