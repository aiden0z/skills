#!/usr/bin/env python3
"""Grade repo-bug-audit eval traces and artifacts.

This is a lightweight replay grader. It does not run an agent. Feed it a stored
fresh-agent transcript plus the produced audit workspace, and it checks the
portable eval-case assertions under evals/.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def as_list(value) -> list:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def load_cases(paths: list[Path], selected_ids: set[str] | None = None) -> list[dict]:
    cases: list[dict] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for case in payload.get("evals", []):
            if not isinstance(case, dict):
                continue
            case_id = str(case.get("id", "")).strip()
            if selected_ids and case_id not in selected_ids:
                continue
            cases.append(case)
    return cases


def match_text(text: str, value: str, *, regex: bool = False, case_sensitive: bool = False) -> bool:
    if regex:
        flags = 0 if case_sensitive else re.IGNORECASE
        return re.search(value, text, flags=flags) is not None
    if case_sensitive:
        return value in text
    return value.lower() in text.lower()


def count_text(text: str, value: str, *, regex: bool = False, case_sensitive: bool = False) -> int:
    if regex:
        flags = 0 if case_sensitive else re.IGNORECASE
        return len(re.findall(value, text, flags=flags))
    haystack = text if case_sensitive else text.lower()
    needle = value if case_sensitive else value.lower()
    return haystack.count(needle)


def index_of(text: str, value: str, *, case_sensitive: bool = False) -> int:
    haystack = text if case_sensitive else text.lower()
    needle = value if case_sensitive else value.lower()
    return haystack.find(needle)


def extract_trace_channels(trace_text: str) -> dict[str, list[str] | str]:
    commands: list[str] = []
    command_outputs: list[str] = []
    messages: list[str] = []
    tools: list[str] = []
    pending_bash: dict[str, int] = {}
    for line in trace_text.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Codex exec JSONL shape.
        item = payload.get("item", {})
        if isinstance(item, dict):
            if item.get("type") == "command_execution":
                tools.append("command_execution")
                commands.append(str(item.get("command", "")))
                command_outputs.append(str(item.get("aggregated_output", "")))
                continue
            if item.get("type") == "agent_message":
                messages.append(str(item.get("text", "")))
                continue

        # Claude Code stream-json shape.
        message = payload.get("message")
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content", [])
        if isinstance(content, str):
            if role == "assistant":
                messages.append(content)
            continue
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text" and role == "assistant":
                messages.append(str(block.get("text", "")))
                continue
            if block_type == "tool_use":
                tool_name = str(block.get("name", ""))
                tools.append(tool_name)
                tool_input = block.get("input", {})
                if not isinstance(tool_input, dict):
                    tool_input = {}
                if tool_name == "Bash":
                    commands.append(str(tool_input.get("command", "")))
                    command_outputs.append("")
                    tool_id = str(block.get("id", ""))
                    if tool_id:
                        pending_bash[tool_id] = len(command_outputs) - 1
                elif tool_name in {"Read", "Write", "Edit", "MultiEdit"}:
                    path = tool_input.get("file_path") or tool_input.get("path") or ""
                    commands.append(f"{tool_name} {path}")
                    command_outputs.append("")
                else:
                    commands.append(tool_name)
                    command_outputs.append("")
                continue
            if block_type == "tool_result":
                tool_use_id = str(block.get("tool_use_id", ""))
                output = str(block.get("content", ""))
                if tool_use_id in pending_bash:
                    command_outputs[pending_bash[tool_use_id]] = output
    return {
        "trace": trace_text,
        "commands": commands,
        "command_text": "\n".join(commands),
        "command_outputs": command_outputs,
        "command_output_text": "\n".join(command_outputs),
        "messages": messages,
        "message_text": "\n".join(messages),
        "tools": tools,
        "tool_text": "\n".join(tools),
    }


def suspicious_bulk_writer_commands(commands: list[str]) -> list[str]:
    suspicious: list[str] = []
    final_artifact_markers = [
        "findings/P",
        "knowledge/repo-profiles",
        "quality/lens-coverage",
        "quality/depth-coverage",
        "README.md",
        "architecture-design-review.md",
        "work/shards",
        "candidates.md",
        "shard-summary.json",
    ]
    loop_markers = [
        "for r in repos",
        "for repo in repos",
        "for repo_item in",
        "for shard in",
        "for profile in",
        "for profile,",
        "for prof in",
        "for cand in",
        "for item in",
    ]
    for command in commands:
        lowered = command.lower()
        if (
            re.search(r"(python3?|node|bash|zsh|sh)\s+-?\s*<<", command)
            and re.search(r"write_text\s*\(|writeFileSync\s*\(|cat\s*>|tee\s+", command)
            and re.search(r"work/shards|candidates\.md|shard-summary\.json", command, flags=re.IGNORECASE)
            and (re.search(r"\bfor\s+\w+\s+in\b", command) or "glob(" in command or "rglob(" in command)
        ):
            suspicious.append(command)
            continue
        if (
            re.search(r"(python3?|node|bash|zsh|sh)\s+-?\s*<<", command)
            and re.search(r"TARGET_PER_REPO|retained in the broad funnel and parked because static review did not prove", command)
            and re.search(r"high-recall-scan\.json|work/shards|candidates\.md", command)
        ):
            suspicious.append(command)
            continue
        if re.search(
            r"\bpython3?\b[^;\n]*work/(tmp|scripts)/[^ \n\t\"']*"
            r"(fill|write|build|generate|make|render|sync|create|compose|package|artifact|evidence|coverage|profile|candidate|finding|knowledge|depth|lens|submit|final|handoff)"
            r"[^ \n\t\"']*\.py",
            lowered,
        ):
            suspicious.append(command)
            continue
        if re.search(r"work/(tmp|scripts)/[^ \n\t\"']*(write|build|generate|make|render)[^ \n\t\"']*(package|evidence|docs|final|handoff|deliverable)[^ \n\t\"']*\.py", lowered):
            suspicious.append(command)
            continue
        if "write_package.py" in lowered or "build_evidence_docs.py" in lowered:
            suspicious.append(command)
            continue
        if not re.search(r"(python3?|node|bash|zsh|sh)\s+-?\s*<<", command):
            continue
        if not re.search(r"write_text\s*\(|writeFileSync\s*\(|cat\s*>|tee\s+", command):
            continue
        marker_count = sum(marker in command for marker in final_artifact_markers)
        has_loop = any(marker in command for marker in loop_markers)
        if marker_count >= 3 or (marker_count >= 2 and has_loop):
            suspicious.append(command)
    return suspicious


def script_final_markdown_categories(text: str) -> set[str]:
    categories: set[str] = set()
    if not re.search(r"\bwrite_text\s*\(|\bopen\s*\([^)]*[\"']w", text):
        return categories
    markers = {
        "findings": [r"findings/P[1-4]", r"SUBMIT\s*/\s*[\"']findings[\"']", r"submit/.*/?findings"],
        "repo_profiles": [r"knowledge/repo-profiles", r"SUBMIT\s*/\s*[\"']knowledge[\"']\s*/\s*[\"']repo-profiles[\"']"],
        "quality": [r"quality/(lens-coverage|depth-coverage|submission-scope|repository-versions)", r"SUBMIT\s*/\s*[\"']quality[\"']"],
        "knowledge": [r"knowledge/(system-overview|repo-relationship-map|risk-paths|architecture-design-review)", r"SUBMIT\s*/\s*[\"']knowledge[\"']"],
        "readme": [r"README\.md", r"SUBMIT\s*/\s*[\"']README\.md[\"']"],
    }
    for category, patterns in markers.items():
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
            categories.add(category)
    return categories


def artifact_bulk_writer_hits(artifact_root: Path) -> list[str]:
    hits: list[str] = []
    work_root = artifact_root / "work"
    if not work_root.is_dir():
        return hits
    for script_path in sorted(work_root.rglob("*.py")):
        if any(part in {"__pycache__", "node_modules"} for part in script_path.parts):
            continue
        text = script_path.read_text(encoding="utf-8", errors="replace")
        categories = script_final_markdown_categories(text)
        suspicious_name = re.search(
            r"(fill|write|generate|build|make|render|compose|sync).*(package|artifact|evidence|docs|coverage|profile|candidate|finding|knowledge|final|handoff|deliverable)|"
            r"(package|artifact|evidence|docs|coverage|profile|candidate|finding|knowledge|final|handoff|deliverable).*(fill|write|generate|build|make|render|compose|sync)",
            script_path.name,
            re.IGNORECASE,
        )
        if len(categories) >= 2 or (categories and suspicious_name):
            hits.append(f"{script_path.relative_to(artifact_root)} ({', '.join(sorted(categories))})")
    return hits


def artifact_high_recall_funnel_failure(artifact_root: Path) -> str | None:
    high_path = artifact_root / "work/scanner-output/high-recall-scan.json"
    candidate_path = artifact_root / "submit/indexes/candidates.generated.json"
    depth_path = artifact_root / "submit/quality/depth-coverage.md"
    if not high_path.is_file() or not candidate_path.is_file() or not depth_path.is_file():
        return None
    try:
        high = json.loads(high_path.read_text(encoding="utf-8"))
        candidates = json.loads(candidate_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return f"invalid JSON while checking high-recall funnel: {exc}"
    total_hits = high.get("total_hits")
    total_candidates = candidates.get("total_candidates")
    if not isinstance(total_hits, int) or not isinstance(total_candidates, int):
        return None
    # Do not fail on candidate-count quotas. The validator and human review
    # should inspect seed_triage / issue-family coverage / depth coverage for
    # honest refutation rather than forcing a fixed number of leads.
    return None


def artifact_candidate_index_integrity_failure(artifact_root: Path) -> str | None:
    candidate_path = artifact_root / "submit/indexes/candidates.generated.json"
    shards_root = artifact_root / "work/shards"
    if not candidate_path.is_file() or not shards_root.is_dir():
        return None
    try:
        payload = json.loads(candidate_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return f"invalid candidate index JSON: {exc}"
    if payload.get("generated_by") != "generate_candidate_index.py":
        return "candidate index missing generated_by=generate_candidate_index.py"
    if payload.get("schema_version") != 3:
        return "candidate index missing schema_version=3"
    for field in ("candidates_by_priority", "candidate_outcomes", "candidate_outcomes_by_priority"):
        if not isinstance(payload.get(field), dict):
            return f"candidate index missing {field}"
    gate_complete_unsubmitted = payload.get("gate_complete_unsubmitted_candidates")
    if not isinstance(gate_complete_unsubmitted, list):
        return "candidate index missing gate_complete_unsubmitted_candidates"
    if gate_complete_unsubmitted:
        sample = []
        for item in gate_complete_unsubmitted[:5]:
            if isinstance(item, dict):
                sample.append(
                    f"{item.get('repo', 'unknown')}:{item.get('id', 'unlabeled')}:{item.get('priority', 'unknown')}"
                )
            else:
                sample.append(str(item))
        return "gate-complete candidates remain unsubmitted: " + ", ".join(sample)
    failures: list[str] = []
    for item in payload.get("repos", []):
        if not isinstance(item, dict):
            continue
        profile = str(item.get("profile_name", "unknown"))
        candidate_count = item.get("candidate_count")
        explicit_count = item.get("explicit_candidate_entries")
        submitted = item.get("submitted_bug_ids")
        submitted_count = len(submitted) if isinstance(submitted, list) else 0
        if not isinstance(explicit_count, int):
            failures.append(f"{profile} missing explicit_candidate_entries")
            continue
        if isinstance(candidate_count, int) and candidate_count > explicit_count + submitted_count:
            failures.append(
                f"{profile} candidate_count {candidate_count} exceeds explicit entries plus submitted Bugs "
                f"({explicit_count + submitted_count})"
            )
    if failures:
        return "; ".join(failures[:8])
    return None


REQUIRED_ISSUE_FAMILIES = {
    "auth-authorization": ["auth-authorization", "authorization", "authentication", "authn", "authz", "鉴权", "授权", "认证"],
    "secrets-config": ["secrets-config", "secret", "credential", "token", "key", "凭据", "密钥", "配置泄露"],
    "execution-sandbox": ["execution-sandbox", "execution", "sandbox", "rce", "command", "eval", "exec", "执行", "沙箱", "命令"],
    "deserialization-ipc": ["deserialization-ipc", "deserialization", "serialization", "ipc", "uds", "pickle", "反序列化", "进程间"],
    "file-path-storage": ["file-path-storage", "path traversal", "file path", "upload", "download", "storage", "路径", "文件", "上传", "下载", "存储"],
    "network-ssrf": ["network-ssrf", "ssrf", "network", "http client", "url", "callback", "网络", "回调"],
    "tls-transport": ["tls-transport", "tls", "ssl", "certificate", "transport", "证书", "传输"],
    "frontend-rendering": ["frontend-rendering", "frontend", "xss", "html", "markdown", "dom", "前端", "渲染"],
    "state-data-integrity": ["state-data-integrity", "state", "transaction", "data integrity", "database", "一致性", "事务", "数据"],
    "async-lifecycle-recovery": ["async-lifecycle-recovery", "async", "lifecycle", "recovery", "worker", "queue", "异步", "生命周期", "恢复"],
    "resource-concurrency": ["resource-concurrency", "resource", "concurrency", "thread", "pool", "leak", "并发", "资源", "泄漏"],
    "deployment-supply-chain": ["deployment-supply-chain", "deployment", "docker", "container", "dependency", "supply", "部署", "容器", "依赖", "供应链"],
}


def artifact_issue_family_coverage_failure(artifact_root: Path) -> str | None:
    path = artifact_root / "submit/quality/issue-family-coverage.md"
    if not path.is_file():
        return "missing submit/quality/issue-family-coverage.md"
    text = path.read_text(encoding="utf-8", errors="replace")
    lower = text.lower()
    missing: list[str] = []
    for family, aliases in REQUIRED_ISSUE_FAMILIES.items():
        if not any(alias.lower() in lower for alias in aliases):
            missing.append(family)
    if missing:
        return "issue-family coverage missing: " + ", ".join(missing[:8])
    if not re.search(r"fresh[- ]run|first[- ]run|independent scan|首次|独立扫描|新扫描", text, re.IGNORECASE):
        return "issue-family coverage does not state fresh/current-source scan provenance"
    return None


GENERIC_CANDIDATE_PHRASES = [
    "retained in the broad funnel and parked because static review did not prove a complete trigger, missing guard, and impact chain",
    "fresh current-source seed from",
]


def artifact_generic_candidate_inflation_failure(artifact_root: Path) -> str | None:
    """Catch candidate backlogs filled from scanner seeds without repo-local triage.

    A few parked scanner-seed lines are fine. Dozens of nearly identical lines are
    a different artifact: a synthetic recall number that looks like exploration.
    """
    shards_root = artifact_root / "work/shards"
    if not shards_root.is_dir():
        return None
    phrase_counts = {phrase: 0 for phrase in GENERIC_CANDIDATE_PHRASES}
    affected_files: set[str] = set()
    for candidates_path in sorted(shards_root.glob("*/candidates.md")):
        text = candidates_path.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in GENERIC_CANDIDATE_PHRASES:
            count = text.count(phrase)
            if count:
                phrase_counts[phrase] += count
                affected_files.add(str(candidates_path.relative_to(artifact_root)))
    broad_funnel_count = phrase_counts[GENERIC_CANDIDATE_PHRASES[0]]
    fresh_seed_count = phrase_counts[GENERIC_CANDIDATE_PHRASES[1]]
    if broad_funnel_count >= 12 or (fresh_seed_count >= 30 and len(affected_files) >= 6):
        sample = ", ".join(sorted(affected_files)[:5])
        return (
            "candidate backlog appears bulk-inflated from scanner seeds: "
            f"{broad_funnel_count} boilerplate parked lines, {fresh_seed_count} fresh-seed lines "
            f"across {len(affected_files)} shard files; sample {sample}"
        )
    return None


def final_artifact_touch_commands(commands: list[str]) -> list[str]:
    hits: list[str] = []
    for command in commands:
        if re.search(r"\btouch\b|find\s+[^;\n]*-exec\s+touch\b", command) and re.search(
            r"/submit/(README\.md|findings(?:/|\b)|knowledge(?:/|\b)|quality(?:/|\b)|indexes(?:/|\b)|bug-audit-report\.html)",
            command,
        ):
            hits.append(command)
            continue
        if "generate_bug_report_html.py" in command or "generate_candidate_index.py" in command:
            continue
        if not re.search(r"\bwrite_text\s*\(|\bopen\s*\([^)]*[\"']w|writeFileSync\s*\(", command):
            continue
        if not re.search(r"submit\s*[)/]|/submit/|submit/'|submit/\"", command):
            continue
        marker_count = len(
            re.findall(
                r"README\.md|findings|knowledge|quality|indexes|repo-profiles|bug-audit-report\.html",
                command,
                flags=re.IGNORECASE,
            )
        )
        has_bulk_path_loop = re.search(r"\bfor\s+\w+\s+in\s+(paths|files|artifacts)|glob\s*\(|rglob\s*\(", command)
        if marker_count >= 2 or has_bulk_path_loop:
            hits.append(command)
    return hits


def artifact_high_priority_promotion_review_failure(artifact_root: Path) -> str | None:
    shards_root = artifact_root / "work/shards"
    if not shards_root.is_dir():
        return None
    failures: list[str] = []
    for candidates_path in sorted(shards_root.glob("*/candidates.md")):
        text = candidates_path.read_text(encoding="utf-8", errors="replace")
        candidate_match = re.search(
            r"^##\s*(?:Candidate Leads|候选线索)\s*$([\s\S]*?)(?=^##\s|\Z)",
            text,
            flags=re.MULTILINE,
        )
        if not candidate_match:
            continue
        candidate_body = candidate_match.group(1)
        high_ids: list[str] = []
        for line in candidate_body.splitlines():
            if not re.search(r"\bparked\s+P[12]\b|\bP[12]\s*[:,-]?\s*parked\b", line, flags=re.IGNORECASE):
                continue
            match = re.search(r"\b(C\d+)\b", line, flags=re.IGNORECASE)
            high_ids.append(match.group(1).upper() if match else "<unlabeled>")
        if not high_ids:
            continue
        review_match = re.search(
            r"^##\s*(?:Promotion Review|提升复核|升级复核)\s*$([\s\S]*?)(?=^##\s|\Z)",
            text,
            flags=re.MULTILINE,
        )
        if not review_match:
            failures.append(f"{candidates_path.relative_to(artifact_root)} missing Promotion Review for {', '.join(high_ids[:6])}")
            continue
        review = review_match.group(1)
        review_upper = review.upper()
        missing = [candidate_id for candidate_id in high_ids if candidate_id != "<unlabeled>" and candidate_id not in review_upper]
        if missing:
            failures.append(f"{candidates_path.relative_to(artifact_root)} Promotion Review misses {', '.join(missing[:6])}")
            continue
        if not re.search(r"`[^`]+:\d+`|\bBUG-\d{4,}\b", review):
            failures.append(f"{candidates_path.relative_to(artifact_root)} Promotion Review lacks code anchor or merge target")
            continue
        if not re.search(
            r"\b(missing|insufficient|runtime|deployment|duplicate|merged|merge target|false-positive|"
            r"guard|scope|needs?|unconfirmed|blocked)\b|缺|未确认|运行时|部署|合并|误报|缺少|范围",
            review,
            flags=re.IGNORECASE,
        ):
            failures.append(f"{candidates_path.relative_to(artifact_root)} Promotion Review lacks a concrete non-promotion reason")
    if failures:
        return "; ".join(failures[:6])
    return None


def historical_audit_source_scan_hits(commands: list[str], outputs: list[str]) -> list[str]:
    hits: list[str] = []
    generated_output_re = re.compile(
        r"(/work/(shards|scanner-output|drafts|tmp)/|"
        r"/submit/(findings|quality|knowledge|indexes)/|"
        r"/submit/(bug-audit-report\.html|audit-overview\.png)|"
        r"/ab-test-[^/\s]+/|"
        r"/[^/\s]*(bug-audit|audit-output|audit-package)[^/\s]*/(work|submit)/)",
        re.IGNORECASE,
    )
    for command, output in zip(commands, outputs):
        if not re.search(r"\b(rg|grep)\b", command):
            continue
        if "validate_bug_package.py" in command or "generate_bug_index.py" in command:
            continue
        if "/submit/" in command:
            continue
        # Ignore command-output bookkeeping such as `wc -l <output-root>/work/scanner-output/foo.txt`.
        # This is not a source scan result; it is the path of the scan artifact itself.
        non_empty_output_lines = [line.strip() for line in str(output).splitlines() if line.strip()]
        if non_empty_output_lines and all(
            re.fullmatch(r"\d+\s+\S+/work/scanner-output/\S+", line) for line in non_empty_output_lines
        ):
            continue
        if not generated_output_re.search(output):
            continue
        hits.append(command)
    return hits


def check_trace_assertion(assertion: dict, trace_channels: dict[str, list[str] | str]) -> str | None:
    assertion_type = str(assertion.get("type", "")).strip()
    case_sensitive = bool(assertion.get("case_sensitive", False))
    regex = bool(assertion.get("regex", False))
    trace_text = str(trace_channels.get("trace", ""))
    command_text = str(trace_channels.get("command_text", ""))
    message_text = str(trace_channels.get("message_text", ""))
    tool_text = str(trace_channels.get("tool_text", ""))
    commands = trace_channels.get("commands", [])
    outputs = trace_channels.get("command_outputs", [])
    if not isinstance(commands, list):
        commands = []
    if not isinstance(outputs, list):
        outputs = []

    if assertion_type in {"skill_invoked", "command_contains", "tool_called", "trace_contains"}:
        value = str(assertion.get("value", "")).strip()
        if not value:
            return f"{assertion_type}: missing value"
        if assertion_type == "command_contains":
            haystack = command_text
        elif assertion_type == "tool_called":
            haystack = tool_text
        else:
            haystack = trace_text
        if not match_text(haystack, value, regex=regex, case_sensitive=case_sensitive):
            return f"{assertion_type}: missing {value!r}"
        return None

    if assertion_type == "command_not_contains":
        value = str(assertion.get("value", "")).strip()
        if not value:
            return "command_not_contains: missing value"
        if match_text(command_text, value, regex=regex, case_sensitive=case_sensitive):
            return f"command_not_contains: found forbidden {value!r}"
        return None

    if assertion_type in {"command_count_at_most", "command_count_at_least"}:
        pattern = str(assertion.get("pattern", assertion.get("value", ""))).strip()
        if not pattern:
            return f"{assertion_type}: missing pattern"
        found = count_text(command_text, pattern, regex=regex, case_sensitive=case_sensitive)
        if assertion_type == "command_count_at_most":
            maximum = assertion.get("max", 0)
            if not isinstance(maximum, int):
                return "command_count_at_most: max must be an integer"
            if found > maximum:
                return f"command_count_at_most: found {found} matches for {pattern!r}, max {maximum}"
        else:
            minimum = assertion.get("min", 0)
            if not isinstance(minimum, int):
                return "command_count_at_least: min must be an integer"
            if found < minimum:
                return f"command_count_at_least: found {found} matches for {pattern!r}, min {minimum}"
        return None

    if assertion_type == "trace_not_contains":
        value = str(assertion.get("value", "")).strip()
        if not value:
            return "trace_not_contains: missing value"
        if match_text(trace_text, value, regex=regex, case_sensitive=case_sensitive):
            return f"trace_not_contains: found forbidden {value!r}"
        return None

    if assertion_type == "trace_order":
        before = str(assertion.get("before", "")).strip()
        after = str(assertion.get("after", "")).strip()
        if not before or not after:
            return "trace_order: missing before or after"
        before_index = index_of(trace_text, before, case_sensitive=case_sensitive)
        after_index = index_of(trace_text, after, case_sensitive=case_sensitive)
        if before_index < 0:
            return f"trace_order: missing before marker {before!r}"
        if after_index < 0:
            return f"trace_order: missing after marker {after!r}"
        if before_index >= after_index:
            return f"trace_order: {before!r} must appear before {after!r}"
        return None

    if assertion_type == "ask_count_at_most":
        pattern = str(assertion.get("pattern", assertion.get("value", ""))).strip()
        maximum = assertion.get("max", 0)
        if not isinstance(maximum, int):
            return "ask_count_at_most: max must be an integer"
        if not pattern:
            return "ask_count_at_most: missing pattern"
        found = count_text(message_text, pattern, regex=regex, case_sensitive=case_sensitive)
        if found > maximum:
            return f"ask_count_at_most: found {found} matches for {pattern!r}, max {maximum}"
        return None

    if assertion_type == "shard_gate_failure_blocks_report":
        last_shard_gate_failed = False
        for command, output in zip(commands, outputs):
            command = str(command)
            output = str(output)
            if "--validate-shards-only" in command:
                error_match = re.search(r"Errors:\s*([1-9]\d*)", output)
                last_shard_gate_failed = bool(error_match or re.search(r"^ERROR:", output, flags=re.MULTILINE))
                continue
            if last_shard_gate_failed and ("generate_bug_report_html.py" in command or "audit-overview" in command):
                return (
                    "shard_gate_failure_blocks_report: report asset command ran after "
                    "a failing --validate-shards-only gate without a later passing shard gate"
                )
        return None

    if assertion_type == "final_validation_requires_handoff_flags":
        has_final_validation = False
        for command in commands:
            command = str(command)
            if "validate_bug_package.py" not in command:
                continue
            if "--validate-shards-only" in command:
                continue
            if "--require-knowledge" in command and "--require-html-report" in command and "--repo-root" in command:
                has_final_validation = True
                break
        if not has_final_validation:
            return (
                "final_validation_requires_handoff_flags: missing final validation command "
                "with --require-knowledge --require-html-report --repo-root"
            )
        return None

    if assertion_type == "bulk_package_writer_absent":
        suspicious = suspicious_bulk_writer_commands([str(command) for command in commands])
        if suspicious:
            preview = suspicious[0].replace("\n", " ")[:240]
            return f"bulk_package_writer_absent: suspicious mass-generation command found: {preview}"
        return None

    if assertion_type == "final_artifact_touch_absent":
        suspicious = final_artifact_touch_commands([str(command) for command in commands])
        if suspicious:
            preview = suspicious[0].replace("\n", " ")[:240]
            return f"final_artifact_touch_absent: final/shard artifact touch or bulk rewrite found: {preview}"
        return None

    if assertion_type == "source_scan_excludes_historical_packages":
        hits = historical_audit_source_scan_hits(
            [str(command) for command in commands],
            [str(output) for output in outputs],
        )
        if hits:
            preview = hits[0].replace("\n", " ")[:240]
            return f"source_scan_excludes_historical_packages: rg/grep scan reached historical audit package output: {preview}"
        return None

    if assertion_type == "generic_candidate_inflation_absent":
        command_text = "\n".join(str(command) for command in commands)
        if re.search(
            r"TARGET_PER_REPO|retained in the broad funnel and parked because static review did not prove",
            command_text,
            flags=re.IGNORECASE,
        ):
            return "generic_candidate_inflation_absent: trace contains scanner-seed candidate inflation pattern"
        return None

    return f"unsupported trace assertion type: {assertion_type}"


def artifact_path(root: Path, assertion: dict) -> Path:
    return root / str(assertion.get("path", "")).strip()


def check_artifact_assertion(assertion: dict, artifact_root: Path) -> str | None:
    assertion_type = str(assertion.get("type", "")).strip()
    case_sensitive = bool(assertion.get("case_sensitive", False))
    regex = bool(assertion.get("regex", False))

    if assertion_type == "exists":
        path = artifact_path(artifact_root, assertion)
        if not path.exists():
            return f"exists: missing {path}"
        return None

    if assertion_type == "not_exists":
        path = artifact_path(artifact_root, assertion)
        if path.exists():
            return f"not_exists: forbidden path exists {path}"
        return None

    if assertion_type in {"file_contains", "file_not_contains"}:
        path = artifact_path(artifact_root, assertion)
        value = str(assertion.get("value", "")).strip()
        if not path.is_file():
            return f"{assertion_type}: missing file {path}"
        if not value:
            return f"{assertion_type}: missing value"
        text = path.read_text(encoding="utf-8", errors="replace")
        matched = match_text(text, value, regex=regex, case_sensitive=case_sensitive)
        if assertion_type == "file_contains" and not matched:
            return f"file_contains: {path} missing {value!r}"
        if assertion_type == "file_not_contains" and matched:
            return f"file_not_contains: {path} contains forbidden {value!r}"
        return None

    if assertion_type == "no_bulk_writer_scripts":
        hits = artifact_bulk_writer_hits(artifact_root)
        if hits:
            return "no_bulk_writer_scripts: " + "; ".join(hits[:5])
        return None

    if assertion_type == "high_recall_funnel_not_too_thin":
        return artifact_high_recall_funnel_failure(artifact_root)

    if assertion_type == "candidate_index_integrity":
        return artifact_candidate_index_integrity_failure(artifact_root)

    if assertion_type == "issue_family_coverage_complete":
        return artifact_issue_family_coverage_failure(artifact_root)

    if assertion_type == "generic_candidate_inflation_absent":
        return artifact_generic_candidate_inflation_failure(artifact_root)

    if assertion_type == "high_priority_parked_candidates_reviewed":
        return artifact_high_priority_promotion_review_failure(artifact_root)

    if assertion_type in {"glob_count_at_least", "glob_count_equals"}:
        pattern = str(assertion.get("pattern", assertion.get("path", ""))).strip()
        if not pattern:
            return f"{assertion_type}: missing pattern"
        count = len(list(artifact_root.glob(pattern)))
        if assertion_type == "glob_count_at_least":
            minimum = assertion.get("min", 0)
            if not isinstance(minimum, int):
                return "glob_count_at_least: min must be an integer"
            if count < minimum:
                return f"glob_count_at_least: {pattern!r} matched {count}, min {minimum}"
        else:
            expected = assertion.get("count", 0)
            if not isinstance(expected, int):
                return "glob_count_equals: count must be an integer"
            if count != expected:
                return f"glob_count_equals: {pattern!r} matched {count}, expected {expected}"
        return None

    return f"unsupported artifact assertion type: {assertion_type}"


def grade_case(case: dict, trace_text: str, artifact_root: Path | None) -> dict:
    failures: list[str] = []
    trace_channels = extract_trace_channels(trace_text)
    for assertion in as_list(case.get("trace_assertions")):
        if not isinstance(assertion, dict):
            failures.append("trace assertion must be an object")
            continue
        failure = check_trace_assertion(assertion, trace_channels)
        if failure:
            failures.append(f"trace: {failure}")

    artifact_assertions = as_list(case.get("artifact_assertions"))
    if artifact_assertions and artifact_root is None:
        failures.append("artifact_root is required for artifact assertions")
    elif artifact_root is not None:
        for assertion in artifact_assertions:
            if not isinstance(assertion, dict):
                failures.append("artifact assertion must be an object")
                continue
            failure = check_artifact_assertion(assertion, artifact_root)
            if failure:
                failures.append(f"artifact: {failure}")

    total_assertions = len(as_list(case.get("trace_assertions"))) + len(artifact_assertions)
    passed_assertions = max(total_assertions - len(failures), 0)
    score = 1.0 if total_assertions == 0 else passed_assertions / total_assertions
    return {
        "id": case.get("id", ""),
        "status": "pass" if not failures else "fail",
        "score": score,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade repo-bug-audit eval trace/artifact assertions")
    parser.add_argument("cases", nargs="+", help="Eval case JSON file(s)")
    parser.add_argument("--trace", help="Stored transcript or tool trace text")
    parser.add_argument("--artifact-root", help="Audit workspace root containing submit/ and work/")
    parser.add_argument("--case", action="append", default=[], help="Run only the selected case id; may be repeated")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    trace_text = ""
    if args.trace:
        trace_text = Path(args.trace).expanduser().read_text(encoding="utf-8", errors="replace")
    artifact_root = Path(args.artifact_root).expanduser().resolve() if args.artifact_root else None
    cases = load_cases([Path(path).expanduser().resolve() for path in args.cases], set(args.case) or None)
    results = [grade_case(case, trace_text, artifact_root) for case in cases]
    failed = [result for result in results if result["status"] != "pass"]

    payload = {
        "status": "fail" if failed else "pass",
        "case_count": len(results),
        "failed": len(failed),
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Eval trace grade")
        print(f"Status: {payload['status']}")
        print(f"Cases: {payload['case_count']}")
        print(f"Failed: {payload['failed']}")
        for result in results:
            print(f"- {result['id']}: {result['status']} ({result['score']:.2f})")
            for failure in result["failures"]:
                print(f"  ERROR: {failure}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
