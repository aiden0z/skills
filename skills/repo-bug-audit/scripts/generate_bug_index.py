#!/usr/bin/env python3
"""Generate Markdown and JSON indexes from Bug audit records."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

PRIO_ORDER = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
CONF_ORDER = {"high": 1, "medium": 2, "low": 3}
STABILITY_ORDER = {
    "data-integrity": 1,
    "recovery": 2,
    "availability": 3,
    "resource-leak": 4,
    "storage-performance": 5,
    "network-performance": 6,
    "consistency": 7,
    "security": 8,
}
BLAST_DOMAINS = {"cross-repo", "control-plane", "data-integrity", "security", "availability", "recovery"}


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


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value if not isinstance(x, dict)]
    if value in (None, ""):
        return []
    return [str(value)]


def stability_rank(item: dict) -> int:
    keys = [item.get("category", "")] + as_list(item.get("infra_domains"))
    ranks = [STABILITY_ORDER[x] for x in keys if x in STABILITY_ORDER]
    return min(ranks) if ranks else 99


def blast_rank(item: dict) -> int:
    domains = set(as_list(item.get("infra_domains")))
    return 0 if domains & BLAST_DOMAINS else 1


def collect(root: Path) -> list[dict]:
    findings = []
    for path in sorted((root / "findings").glob("P*/*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        item = {
            "id": meta.get("id", ""),
            "priority": meta.get("priority", path.parent.name),
            "confidence": meta.get("confidence", ""),
            "status": meta.get("status", ""),
            "repo": meta.get("repo", ""),
            "module": meta.get("module", ""),
            "category": meta.get("category", ""),
            "issue_family": meta.get("issue_family", ""),
            "infra_domains": as_list(meta.get("infra_domains", [])),
            "title": first_heading(text),
            "path": str(path.relative_to(root)),
        }
        findings.append(item)
    findings.sort(
        key=lambda x: (
            PRIO_ORDER.get(x["priority"], 99),
            CONF_ORDER.get(x["confidence"], 99),
            stability_rank(x),
            blast_rank(x),
            x["id"],
            x["path"],
        )
    )
    return findings


def md_table(title: str, counter: Counter, language: str = "zh") -> str:
    if language == "zh":
        lines = [f"## {title}", "", "| 项 | 数量 |", "|---|---:|"]
    else:
        lines = [f"## {title}", "", "| Item | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or '未填写'} | {count} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Bug audit indexes")
    parser.add_argument("root", help="Bug package root")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="Output language")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    findings = collect(root)
    (root / "indexes").mkdir(parents=True, exist_ok=True)

    priority = Counter(x["priority"] for x in findings)
    confidence = Counter(x["confidence"] for x in findings)
    category = Counter(x["category"] for x in findings)
    repo = Counter(x["repo"] for x in findings)
    family = Counter(x["issue_family"] for x in findings)
    infra = Counter(domain for x in findings for domain in x["infra_domains"])

    if args.language == "zh":
        md = [
            "# 仓库 Bug 审计索引",
            "",
            f"Bug 总数：`{len(findings)}`",
            "",
            md_table("优先级分布", priority, args.language),
            md_table("置信度分布", confidence, args.language),
            md_table("类型分布", category, args.language),
            md_table("影响域分布", infra, args.language),
            md_table("仓库分布", repo, args.language),
            md_table("问题族分布", family, args.language),
            "## 明细",
            "",
            "| ID | 优先级 | 置信度 | 仓库 | 模块 | 类型 | 问题族 | 标题 | 文件 |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    else:
        md = [
            "# Bug Audit Index",
            "",
            f"Total Bugs: `{len(findings)}`",
            "",
            md_table("Priority Distribution", priority, args.language),
            md_table("Confidence Distribution", confidence, args.language),
            md_table("Category Distribution", category, args.language),
            md_table("Impact Domain Distribution", infra, args.language),
            md_table("Repository Distribution", repo, args.language),
            md_table("Issue Family Distribution", family, args.language),
            "## Details",
            "",
            "| ID | Priority | Confidence | Repo | Module | Category | Issue Family | Title | File |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    for x in findings:
        title = x["title"].replace("|", "\\|")
        md.append(
            f"| {x['id']} | {x['priority']} | {x['confidence']} | {x['repo']} | {x['module']} | "
            f"{x['category']} | {x['issue_family']} | {title} | `{x['path']}` |"
        )
    md.append("")

    (root / "indexes/findings.generated.md").write_text("\n".join(md), encoding="utf-8")
    payload = {
        "total": len(findings),
        "priority": dict(priority),
        "confidence": dict(confidence),
        "category": dict(category),
        "infra_domains": dict(infra),
        "repo": dict(repo),
        "issue_family": dict(family),
        "findings": findings,
    }
    (root / "indexes/findings.generated.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated indexes for {len(findings)} findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
