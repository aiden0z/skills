#!/usr/bin/env python3
"""Generate candidate-pool indexes from repo shard evidence."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SHARD_SUMMARY = "shard-summary.json"
CANDIDATE_INDEX_SCHEMA_VERSION = 3
GENERATED_BY = "generate_candidate_index.py"
PRIORITIES = ("P1", "P2", "P3", "P4")
OUTCOMES = ("promoted", "parked", "refuted", "merged", "unknown")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def candidate_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = []
    in_section = False
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"^##\s+(Candidate Leads|候选线索)\b", line, flags=re.IGNORECASE):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if not line or re.search(r"\bnone recorded yet\b|pending shard exploration|暂无|待补充", line, re.IGNORECASE):
            continue
        if line.startswith(("- ", "* ", "### ", "#### ")):
            lines.append(re.sub(r"^[-*#\s]+", "", line).strip())
    return lines


def explicit_candidate_count(path: Path) -> int:
    """Count evidence-bearing candidate entries in candidates.md."""
    count = 0
    for line in candidate_lines(path):
        if re.search(r"\b(C\d+|BUG-\d{4,})\b", line, flags=re.IGNORECASE):
            count += 1
            continue
        if re.search(r"`[^`]+:\d+`|[A-Za-z0-9_./-]+\.(py|ts|tsx|js|java|go|rs|yaml|yml|sh|md):\d+", line):
            count += 1
    return count


def normalize_outcome(line: str) -> str:
    lower = line.lower()
    explicit = re.search(r"\boutcome\s*[:=]\s*(promoted|submitted|parked|unpromoted|refuted|merged|duplicate)\b", lower)
    if explicit:
        value = explicit.group(1)
        if value == "submitted":
            return "promoted"
        if value == "unpromoted":
            return "parked"
        if value == "duplicate":
            return "merged"
        return value
    if re.search(r"\b(promoted|submitted)\b|已提交|已升级|提交为", lower):
        return "promoted"
    if re.search(r"\b(merged|duplicate)\b|合并|重复", lower):
        return "merged"
    if re.search(r"\b(refuted|false[- ]positive|not[- ]applicable)\b|已排除|误报|不适用", lower):
        return "refuted"
    if re.search(r"\b(parked|unpromoted|follow[- ]up|kept)\b|搁置|未提交|待补", lower):
        return "parked"
    return "unknown"


def normalize_gate(line: str) -> str:
    lower = line.lower()
    if re.search(r"\b(?:bug[_ -]?gate|gate)\s*[:=]\s*(?:complete|pass(?:ed)?)\b|bug gate complete|满足.*bug gate", lower):
        return "complete"
    if re.search(r"\b(?:bug[_ -]?gate|gate)\s*[:=]\s*(?:missing|incomplete|blocked|unknown|partial)\b", lower):
        return "incomplete"
    if re.search(r"\bmissing[_ -]?gate\s*[:=]\s*[\w./-]+|缺少.*(证据|触发|影响|路径|失败模式)", lower):
        return "incomplete"
    return "unknown"


def extract_missing_gate(line: str) -> str:
    match = re.search(r"\bmissing[_ -]?gate\s*[:=]\s*([A-Za-z0-9_./:-]+)", line, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"\bnot submitted because\s*[:：]\s*([^;|]+)", line, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"未提交原因\s*[:：]\s*([^;|]+)", line)
    if match:
        return match.group(1).strip()
    return ""


def parse_candidate_lead(line: str, repo: str, profile_name: str) -> dict[str, Any]:
    candidate_id = ""
    match = re.search(r"\b(C\d+)\b", line, flags=re.IGNORECASE)
    if match:
        candidate_id = match.group(1).upper()
    priority_match = re.search(r"\bP([1-4])\b", line, flags=re.IGNORECASE)
    priority = f"P{priority_match.group(1)}" if priority_match else "unknown"
    bug_match = re.search(r"\bBUG-\d{4,}\b", line, flags=re.IGNORECASE)
    submitted_bug_id = bug_match.group(0).upper() if bug_match else ""
    outcome = normalize_outcome(line)
    if submitted_bug_id and outcome == "unknown":
        outcome = "promoted"
    gate = normalize_gate(line)
    missing_gate = extract_missing_gate(line)
    return {
        "repo": repo,
        "profile_name": profile_name,
        "id": candidate_id,
        "priority": priority,
        "outcome": outcome,
        "bug_gate": gate,
        "missing_gate": missing_gate,
        "submitted_bug_id": submitted_bug_id,
        "line": line,
    }


def load_findings(root: Path) -> list[dict[str, Any]]:
    index = root / "indexes/findings.generated.json"
    if not index.is_file():
        return []
    payload = load_json(index)
    findings = payload.get("findings", payload)
    return findings if isinstance(findings, list) else []


def collect(root: Path) -> dict[str, Any]:
    workspace = root.parent
    shards_root = workspace / "work/shards"
    findings = load_findings(root)
    findings_by_repo = Counter(str(f.get("repo", "unknown")) for f in findings if isinstance(f, dict))
    findings_by_priority = Counter(str(f.get("priority", "unknown")) for f in findings if isinstance(f, dict))
    candidates_by_priority: Counter[str] = Counter()
    candidates_by_outcome: Counter[str] = Counter()
    outcomes_by_priority: dict[str, Counter[str]] = {priority: Counter() for priority in PRIORITIES}
    outcomes_by_priority["unknown"] = Counter()
    gate_complete_unsubmitted: list[dict[str, Any]] = []
    unknown_priority_count = 0
    unknown_outcome_count = 0
    repos = []
    total_candidates = 0
    total_promoted_links = 0

    for summary_path in sorted(shards_root.glob(f"*/{SHARD_SUMMARY}")):
        payload = load_json(summary_path)
        if not payload:
            continue
        profile_name = str(payload.get("profile_name") or summary_path.parent.name)
        repo = str(payload.get("repo") or profile_name)
        candidates_path = summary_path.parent / "candidates.md"
        leads = candidate_lines(candidates_path)
        parsed_leads = [parse_candidate_lead(line, repo, profile_name) for line in leads]
        explicit_count = explicit_candidate_count(candidates_path)
        candidate_count = payload.get("candidate_count")
        if not isinstance(candidate_count, int) or candidate_count < 0:
            candidate_count = explicit_count
        submitted_bug_ids = payload.get("submitted_bug_ids")
        if not isinstance(submitted_bug_ids, list):
            submitted_bug_ids = []
        total_candidates += candidate_count
        total_promoted_links += len(submitted_bug_ids)
        repo_priority = Counter(str(item["priority"]) for item in parsed_leads)
        repo_outcome = Counter(str(item["outcome"]) for item in parsed_leads)
        repo_outcomes_by_priority: dict[str, Counter[str]] = {priority: Counter() for priority in PRIORITIES}
        repo_outcomes_by_priority["unknown"] = Counter()
        repo_gate_complete_unsubmitted: list[dict[str, Any]] = []
        for item in parsed_leads:
            priority = str(item["priority"])
            outcome = str(item["outcome"])
            candidates_by_priority[priority] += 1
            candidates_by_outcome[outcome] += 1
            outcomes_by_priority.setdefault(priority, Counter())[outcome] += 1
            repo_outcomes_by_priority.setdefault(priority, Counter())[outcome] += 1
            if priority == "unknown":
                unknown_priority_count += 1
            if outcome == "unknown":
                unknown_outcome_count += 1
            if item["bug_gate"] == "complete" and outcome not in {"promoted", "merged"} and not item["submitted_bug_id"]:
                compact = {key: item[key] for key in ("repo", "profile_name", "id", "priority", "outcome", "missing_gate", "line")}
                gate_complete_unsubmitted.append(compact)
                repo_gate_complete_unsubmitted.append(compact)
        repos.append(
            {
                "repo": repo,
                "profile_name": profile_name,
                "candidate_count": candidate_count,
                "explicit_candidate_entries": explicit_count,
                "candidate_leads_sample": leads[:20],
                "submitted_bug_ids": [str(item) for item in submitted_bug_ids],
                "submitted_finding_count": findings_by_repo.get(repo, 0),
                "candidates_by_priority": dict(sorted(repo_priority.items())),
                "candidate_outcomes": dict(sorted(repo_outcome.items())),
                "candidate_outcomes_by_priority": {
                    priority: dict(sorted(counter.items()))
                    for priority, counter in sorted(repo_outcomes_by_priority.items())
                    if counter
                },
                "gate_complete_unsubmitted_candidates": repo_gate_complete_unsubmitted,
                "coverage_classification": str(payload.get("coverage_classification", "")),
                "remaining_gaps": payload.get("remaining_gaps") if isinstance(payload.get("remaining_gaps"), list) else [],
            }
        )

    parked_or_unpromoted = max(total_candidates - total_promoted_links, 0)
    return {
        "schema_version": CANDIDATE_INDEX_SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_candidates": total_candidates,
        "total_submitted_findings": len(findings),
        "total_promoted_candidate_links": total_promoted_links,
        "total_parked_or_unpromoted_candidates": parked_or_unpromoted,
        "findings_by_priority": dict(sorted(findings_by_priority.items())),
        "candidates_by_priority": dict(sorted(candidates_by_priority.items())),
        "candidate_outcomes": dict(sorted(candidates_by_outcome.items())),
        "candidate_outcomes_by_priority": {
            priority: dict(sorted(counter.items()))
            for priority, counter in sorted(outcomes_by_priority.items())
            if counter
        },
        "gate_complete_unsubmitted_candidates": gate_complete_unsubmitted,
        "unknown_priority_candidate_count": unknown_priority_count,
        "unknown_outcome_candidate_count": unknown_outcome_count,
        "repos_with_candidates": sum(1 for repo in repos if repo["candidate_count"] > 0),
        "repos": repos,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Candidate Pool Index",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Candidate leads | {payload['total_candidates']} |",
        f"| Submitted findings | {payload['total_submitted_findings']} |",
        f"| Promoted candidate links | {payload['total_promoted_candidate_links']} |",
        f"| Parked or unpromoted candidates | {payload['total_parked_or_unpromoted_candidates']} |",
        f"| Gate-complete unsubmitted candidates | {len(payload['gate_complete_unsubmitted_candidates'])} |",
        f"| Repos with candidates | {payload['repos_with_candidates']} |",
        "",
        "## By Priority",
        "",
        "| Priority | Candidates | Submitted Findings |",
        "|---|---:|---:|",
    ]
    for priority in PRIORITIES:
        lines.append(
            f"| {priority} | {payload['candidates_by_priority'].get(priority, 0)} | {payload['findings_by_priority'].get(priority, 0)} |"
        )
    lines.extend(
        [
            "",
            "## By Outcome",
            "",
            "| Outcome | Candidates |",
            "|---|---:|",
        ]
    )
    for outcome in OUTCOMES:
        lines.append(f"| {outcome} | {payload['candidate_outcomes'].get(outcome, 0)} |")
    lines.extend(
        [
            "",
            "## By Repository",
            "",
            "| Repo | Candidates | Submitted Findings | Coverage | Sample Leads |",
            "|---|---:|---:|---|---|",
        ]
    )
    for repo in payload["repos"]:
        sample = "; ".join(repo["candidate_leads_sample"][:3]) or "none"
        lines.append(
            "| {repo} | {candidates} | {findings} | `{coverage}` | {sample} |".format(
                repo=repo["repo"],
                candidates=repo["candidate_count"],
                findings=repo["submitted_finding_count"],
                coverage=repo["coverage_classification"] or "unknown",
                sample=sample.replace("|", "\\|"),
            )
        )
    return "\n".join(lines) + "\n"


def render_candidate_coverage(payload: dict[str, Any]) -> str:
    lines = [
        "# Candidate Discovery Coverage",
        "",
        "This file keeps the high-recall discovery layer visible after final Bug promotion.",
        "",
        "## Candidate Funnel",
        "",
        f"- Candidate leads: `{payload['total_candidates']}`",
        f"- Submitted findings: `{payload['total_submitted_findings']}`",
        f"- Promoted candidate links: `{payload['total_promoted_candidate_links']}`",
        f"- Parked or unpromoted candidates: `{payload['total_parked_or_unpromoted_candidates']}`",
        f"- Gate-complete unsubmitted candidates: `{len(payload['gate_complete_unsubmitted_candidates'])}`",
        f"- Repositories with candidates: `{payload['repos_with_candidates']}`",
        "",
        "## Priority Promotion Sweep",
        "",
        "| Priority | Candidates | Submitted Findings | Promoted | Parked | Refuted | Merged | Unknown Outcome |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for priority in PRIORITIES:
        outcomes = payload["candidate_outcomes_by_priority"].get(priority, {})
        lines.append(
            "| {priority} | {candidates} | {findings} | {promoted} | {parked} | {refuted} | {merged} | {unknown} |".format(
                priority=priority,
                candidates=payload["candidates_by_priority"].get(priority, 0),
                findings=payload["findings_by_priority"].get(priority, 0),
                promoted=outcomes.get("promoted", 0),
                parked=outcomes.get("parked", 0),
                refuted=outcomes.get("refuted", 0),
                merged=outcomes.get("merged", 0),
                unknown=outcomes.get("unknown", 0),
            )
        )
    if payload["gate_complete_unsubmitted_candidates"]:
        lines.extend(["", "### Gate-Complete Candidates Still Unsubmitted", ""])
        for item in payload["gate_complete_unsubmitted_candidates"][:30]:
            label = item["id"] or "unlabeled"
            lines.append(
                f"- `{item['repo']}` {label} {item['priority']} outcome=`{item['outcome']}`: {item['line']}"
            )
    else:
        lines.extend(["", "No gate-complete unsubmitted candidates were detected in structured candidate notes."])
    lines.extend(
        [
            "",
            "## Repository Candidate Coverage",
            "",
            "| Repo | Candidates | Submitted Findings | Coverage |",
            "|---|---:|---:|---|",
        ]
    )
    for repo in payload["repos"]:
        lines.append(
            f"| {repo['repo']} | {repo['candidate_count']} | {repo['submitted_finding_count']} | `{repo['coverage_classification'] or 'unknown'}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Candidate count measures recall-oriented static leads retained after repo-local exploration.",
            "- Submitted findings are the promoted, higher-confidence subset.",
            "- A small submitted Bug count is acceptable only when this funnel and shard evidence explain where the remaining leads were parked, refuted, or left for follow-up.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate candidate-pool indexes for repo-bug-audit")
    parser.add_argument("submit_root", help="Path to the submit/ directory")
    args = parser.parse_args()

    root = Path(args.submit_root).expanduser().resolve()
    payload = collect(root)
    (root / "indexes").mkdir(parents=True, exist_ok=True)
    (root / "quality").mkdir(parents=True, exist_ok=True)
    (root / "indexes/candidates.generated.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (root / "indexes/candidates.generated.md").write_text(render_markdown(payload), encoding="utf-8")
    (root / "quality/candidate-coverage.md").write_text(render_candidate_coverage(payload), encoding="utf-8")
    print(f"Generated candidate index: {root / 'indexes/candidates.generated.json'}")
    print(f"Candidate leads: {payload['total_candidates']}")
    print(f"Submitted findings: {payload['total_submitted_findings']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
