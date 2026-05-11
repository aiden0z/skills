#!/usr/bin/env python3
"""Read-only discovery of local agent runtimes and likely evidence channels."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


CAPTURE_RE = re.compile(
    r"json|jsonl|trace|tracing|transcript|session|log|export|output|headless|non-interactive|print|ci|pull request|pr",
    re.IGNORECASE,
)
STRUCTURED_TRACE_RE = re.compile(
    r"--json\b|\bjsonl\b|structured event|trace export|opentelemetry|\botel\b",
    re.IGNORECASE,
)
PARTIAL_CAPTURE_RE = re.compile(
    r"transcript|session|log|export|debug|verbose|non-interactive|headless|print|pull request|\bpr\b|workflow|ci",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RuntimeProbe:
    name: str
    executables: tuple[str, ...]
    help_commands: tuple[tuple[str, ...], ...]
    version_commands: tuple[tuple[str, ...], ...]
    recommended_when_structured: str
    recommended_fallback: str


PROBES = [
    RuntimeProbe(
        name="codex",
        executables=("codex",),
        help_commands=(("codex", "exec", "--help"), ("codex", "--help")),
        version_commands=(("codex", "--version"), ("codex", "version")),
        recommended_when_structured='codex exec --json "<prompt>" > evals/artifacts/<case>.jsonl',
        recommended_fallback="terminal transcript + artifact root + validator logs",
    ),
    RuntimeProbe(
        name="claude-code",
        executables=("claude",),
        help_commands=(("claude", "--help"), ("claude", "help")),
        version_commands=(("claude", "--version"), ("claude", "version")),
        recommended_when_structured="capture structured/session output plus artifact root and validators",
        recommended_fallback="terminal transcript + git diff + artifact root + validator logs",
    ),
    RuntimeProbe(
        name="github-copilot",
        executables=("gh", "copilot"),
        help_commands=(("gh", "copilot", "--help"), ("copilot", "--help")),
        version_commands=(("gh", "--version"), ("copilot", "--version")),
        recommended_when_structured="capture PR/issue conversation, workflow logs, commit diff, artifacts, and CI output",
        recommended_fallback="capture before/after diff, PR comments when available, artifacts, and CI/validator logs",
    ),
    RuntimeProbe(
        name="kimi",
        executables=("kimi", "k2",),
        help_commands=(("kimi", "--help"), ("kimi", "help"), ("k2", "--help"), ("k2", "help")),
        version_commands=(("kimi", "--version"), ("k2", "--version")),
        recommended_when_structured="capture JSON/trace/session output plus artifacts and validators",
        recommended_fallback="terminal transcript + artifact root + validator logs",
    ),
]


def command_exists(command: str) -> str | None:
    return shutil.which(command)


def run_safe(command: tuple[str, ...], timeout: float) -> tuple[int | None, str]:
    if not command or not command_exists(command[0]):
        return None, ""
    try:
        result = subprocess.run(
            list(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    return result.returncode, result.stdout.strip()


def first_available_version(probe: RuntimeProbe, timeout: float) -> str:
    for command in probe.version_commands:
        _, output = run_safe(command, timeout)
        if output:
            return output.splitlines()[0][:200]
    return ""


def collect_help(probe: RuntimeProbe, timeout: float) -> tuple[str, list[str]]:
    outputs: list[str] = []
    commands: list[str] = []
    for command in probe.help_commands:
        _, output = run_safe(command, timeout)
        if output:
            commands.append(" ".join(command))
            outputs.append(output)
    return "\n\n".join(outputs), commands


def matching_lines(text: str, limit: int = 12) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        compact = " ".join(line.strip().split())
        if compact and CAPTURE_RE.search(compact):
            lines.append(compact[:240])
        if len(lines) >= limit:
            break
    return lines


def structured_trace_status(probe: RuntimeProbe, help_text: str) -> str:
    if STRUCTURED_TRACE_RE.search(help_text):
        return "likely"
    if PARTIAL_CAPTURE_RE.search(help_text):
        return "possible"
    return "unknown"


def evidence_level(status: str, name: str) -> int:
    if status == "likely":
        return 3
    if status == "possible":
        return 2
    if name == "github-copilot":
        return 1
    return 1


def probe_runtime(probe: RuntimeProbe, timeout: float) -> dict:
    found_paths = {
        exe: command_exists(exe)
        for exe in probe.executables
        if command_exists(exe)
    }
    if not found_paths:
        return {
            "name": probe.name,
            "available": False,
            "notes": ["No known executable found on PATH."],
        }
    help_text, help_commands = collect_help(probe, timeout)
    status = structured_trace_status(probe, help_text)
    recommendation = probe.recommended_when_structured if status == "likely" else probe.recommended_fallback
    return {
        "name": probe.name,
        "available": True,
        "executables": found_paths,
        "version": first_available_version(probe, timeout),
        "help_commands_checked": help_commands,
        "capture_hints": matching_lines(help_text),
        "structured_trace": status,
        "recommended_capture": recommendation,
        "evidence_level_estimate": evidence_level(status, probe.name),
        "notes": [
            "Discovery is read-only and only inspects local CLI help/version output.",
            "Confirm hosted logs, IDE transcripts, PR comments, and workspace-specific capture manually.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover local agent runtimes and likely evidence capture methods."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output.",
    )
    parser.add_argument(
        "--include-unavailable",
        action="store_true",
        help="Include runtimes not found on PATH.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Timeout in seconds for safe help/version commands.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write JSON discovery output.",
    )
    args = parser.parse_args()

    results = [probe_runtime(probe, args.timeout) for probe in PROBES]
    if not args.include_unavailable:
        results = [item for item in results if item.get("available")]
    payload = {
        "detected": results,
        "summary": {
            "available_count": sum(1 for item in results if item.get("available")),
            "best_evidence_level": max(
                [int(item.get("evidence_level_estimate", 0)) for item in results if item.get("available")]
                or [0]
            ),
        },
        "guidance": [
            "Use this as a starting point, not proof that a capture method works.",
            "Do not run a real-agent eval without explicit user approval.",
            "If evidence level is 0 or only final answers are available, do static/artifact review instead.",
        ],
    }
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json or args.output:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Agent runtime discovery")
        print(f"Available runtimes: {payload['summary']['available_count']}")
        print(f"Best evidence level estimate: {payload['summary']['best_evidence_level']}")
        for item in results:
            if not item.get("available"):
                continue
            print(f"\n- {item['name']}")
            print(f"  structured_trace: {item['structured_trace']}")
            print(f"  evidence_level_estimate: {item['evidence_level_estimate']}")
            print(f"  recommended_capture: {item['recommended_capture']}")
            if item.get("version"):
                print(f"  version: {item['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
