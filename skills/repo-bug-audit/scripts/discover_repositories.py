#!/usr/bin/env python3
"""Discover repository rosters for multi-repo Bug audits."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIR_NAMES = {
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
SKIP_DIR_SUBSTRINGS = ("bug-audit",)
SOURCE_EXTENSIONS = {
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
    ".m",
    ".mm",
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
MANIFEST_NAMES = {
    "Cargo.toml",
    "Dockerfile",
    "Gemfile",
    "Makefile",
    "build.gradle",
    "build.gradle.kts",
    "compose.yaml",
    "docker-compose.yml",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
}


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    value = result.stdout.strip()
    return value or "unknown"


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def should_skip_dir(path: Path) -> bool:
    name = path.name
    return name in SKIP_DIR_NAMES or any(part in name for part in SKIP_DIR_SUBSTRINGS)


def sanitize_profile_name(name: str) -> str:
    safe = name.replace("/", "__").lower()
    return re.sub(r"[^a-z0-9._-]+", "-", safe).strip("-") or "repo"


def discover_repos(root: Path, max_depth: int) -> list[Path]:
    root = root.resolve()
    if is_git_repo(root):
        return [root]
    repos: list[Path] = []
    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        if depth > max_depth:
            continue
        if current != root and is_git_repo(current):
            repos.append(current)
            continue
        if depth == max_depth:
            continue
        try:
            children = sorted(p for p in current.iterdir() if p.is_dir() and not should_skip_dir(p))
        except OSError:
            continue
        for child in reversed(children):
            stack.append((child, depth + 1))
    return sorted(set(repos))


def source_inventory(repo: Path) -> tuple[int, list[str], list[str]]:
    extensions: Counter[str] = Counter()
    source_count = 0
    manifests: list[str] = []
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(repo).parts
        if any(part in SKIP_DIR_NAMES for part in rel_parts[:-1]):
            continue
        if any(any(token in part for token in SKIP_DIR_SUBSTRINGS) for part in rel_parts[:-1]):
            continue
        if path.name in MANIFEST_NAMES:
            manifests.append(path.relative_to(repo).as_posix())
        suffix = path.suffix.lower()
        if suffix in SOURCE_EXTENSIONS or path.name in {"Dockerfile", "Makefile"}:
            source_count += 1
            extensions[suffix or path.name] += 1
    top_extensions = [f"{ext}:{count}" for ext, count in extensions.most_common(8)]
    return source_count, top_extensions, sorted(manifests)[:20]


def repo_display_name(repo: Path, root: Path) -> str:
    root = root.resolve()
    try:
        rel = repo.resolve().relative_to(root)
    except ValueError:
        return repo.name
    if rel == Path("."):
        return repo.name
    return rel.as_posix()


def inspect_repo(repo: Path, root: Path) -> dict:
    display_name = repo_display_name(repo, root)
    branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    commit = run_git(repo, "rev-parse", "HEAD")
    dirty_raw = run_git(repo, "status", "--short")
    dirty = "unknown" if dirty_raw == "unknown" else ("yes" if dirty_raw else "no")
    default_branch_raw = run_git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    default_branch = default_branch_raw.replace("origin/", "", 1) if default_branch_raw != "unknown" else "unknown"
    source_count, top_extensions, manifests = source_inventory(repo)
    return {
        "name": display_name,
        "profile_name": sanitize_profile_name(display_name),
        "path": str(repo),
        "branch": branch,
        "commit": commit,
        "dirty": dirty,
        "default_branch": default_branch,
        "source_like_files": source_count,
        "top_extensions": top_extensions,
        "manifest_files": manifests,
    }


def render_markdown(repos: list[dict]) -> str:
    lines = [
        "# Repository Inventory",
        "",
        "| Repo | Profile | Branch | Commit | Dirty | Source-like Files | Manifests |",
        "|---|---|---|---|---|---:|---|",
    ]
    for repo in repos:
        commit = repo["commit"][:12] if repo["commit"] != "unknown" else "unknown"
        manifests = ", ".join(repo["manifest_files"][:5]) or "none found"
        lines.append(
            "| {name} | `{profile}` | `{branch}` | `{commit}` | `{dirty}` | {source_count} | {manifests} |".format(
                name=repo["name"],
                profile=repo["profile_name"],
                branch=repo["branch"],
                commit=commit,
                dirty=repo["dirty"],
                source_count=repo["source_like_files"],
                manifests=manifests,
            )
        )
    return "\n".join(lines) + "\n"


def render_shards_markdown(repos: list[dict]) -> str:
    lines = [
        "# Repo Shard Plan",
        "",
        "| Shard | Repo | Mode | Execution | Primary Surfaces | Output Scope | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for index, repo in enumerate(repos, 1):
        mode = "standalone"
        if repo["source_like_files"] <= 10:
            mode = "batch-ok"
        elif repo["source_like_files"] <= 300:
            mode = "parallel-ok"
        lines.append(
            "| shard-{index:03d} | {name} | {mode} | planned: parallel if runtime supports it, otherwise record serial reason | surface map from repo-understanding.md: entry/state/integration/execution/lifecycle/runtime as applicable | `work/shards/{profile}/` + `submit/knowledge/repo-profiles/{profile}.md` | planned |".format(
                index=index,
                name=repo["name"],
                mode=mode,
                profile=repo["profile_name"],
            )
        )
    return "\n".join(lines) + "\n"


def render_scan_roots(repos: list[dict]) -> str:
    lines = [
        "# Repo Source Scan Roots",
        "# Use these paths for broad source searches. Do not run broad rg/grep over",
        "# the parent directory, because historical audit packages and generated",
        "# deliverables under *bug-audit* are comparison baselines, not source code.",
    ]
    lines.extend(repo["path"] for repo in repos)
    return "\n".join(lines) + "\n"


def empty_shard_summary(repo: dict) -> dict:
    return {
        "repo": repo["name"],
        "profile_name": repo["profile_name"],
        "parallel_eligible": repo["source_like_files"] > 10,
        "execution_mode": "",
        "agent_or_worker": "",
        "serial_reason": "",
        "coverage_classification": "",
        "focus_scope": "",
        "surface_map": {
            "entry_points": [],
            "auth_boundaries": [],
            "state_owners": [],
            "consistency_boundaries": [],
            "external_integrations": [],
            "execution_boundaries": [],
            "serialization_contracts": [],
            "async_jobs": [],
            "config_and_secrets": [],
            "user_input_paths": [],
            "file_paths": [],
            "resource_lifecycle": [],
            "observability_recovery": [],
            "deployment_runtime": [],
        },
        "risk_surfaces_scanned": [],
        "evidence_paths": [],
        "commands_or_searches": [],
        "seed_triage": [],
        "call_chains_traced": [],
        "hypothesis_loops": [],
        "strongest_refuted_leads": [],
        "candidate_count": 0,
        "submitted_bug_ids": [],
        "zero_finding_rationale": "",
        "remaining_gaps": [],
        "knowledge_atoms": [],
        "profile_updated_from_shard": False,
        "profile_evidence_sections": [],
    }


def write_shard_summary_templates(repos: list[dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for repo in repos:
        repo_dir = output_dir / repo["profile_name"]
        repo_dir.mkdir(parents=True, exist_ok=True)
        summary_path = repo_dir / "shard-summary.json"
        if not summary_path.exists():
            summary_path.write_text(
                json.dumps(empty_shard_summary(repo), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        candidates_path = repo_dir / "candidates.md"
        if not candidates_path.exists():
            candidates_path.write_text(
                "\n".join(
                    [
                        f"# Candidates: {repo['name']}",
                        "",
                        "Use this shard-local file for weak leads, refuted leads, and zero-candidate rationale.",
                        "Do not write final Bug records here; the coordinator promotes verified candidates later.",
                        "",
                        "## Candidate Leads",
                        "",
                        "- None recorded yet.",
                        "",
                        "When adding leads, prefer this parseable shape:",
                        "",
                        "- C1 | P2 | outcome=parked | bug_gate=missing | missing_gate=trigger-path | `repo/path/file.ext:line` | short suspicion",
                        "- C2 | P3 | outcome=promoted | bug_gate=complete | BUG-0017 | `repo/path/file.ext:line` | short title",
                        "",
                        "Allowed outcomes: promoted, parked, refuted, merged.",
                        "If bug_gate=complete is left unpromoted, final validation will fail unless a critical-only scope is recorded.",
                        "",
                        "## Promotion Review",
                        "",
                        "- None recorded yet.",
                        "",
                        "## Refuted Leads",
                        "",
                        "- None recorded yet.",
                        "",
                        "## Zero-candidate Rationale",
                        "",
                        "- Pending shard exploration.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover Git repositories for a repo-bug-audit run")
    parser.add_argument("roots", nargs="+", help="Repository or repository-group root paths")
    parser.add_argument("--max-depth", type=int, default=2, help="Depth to search below non-Git group roots")
    parser.add_argument("--output-json", help="Write machine-readable roster JSON")
    parser.add_argument("--output-md", help="Write Markdown inventory table")
    parser.add_argument("--output-shards-md", help="Write Markdown repo shard plan")
    parser.add_argument("--output-scan-roots", help="Write newline-delimited repo source roots for broad scans")
    parser.add_argument("--output-shard-dir", help="Create one work/shards/<repo>/shard-summary.json template per repo")
    args = parser.parse_args()

    all_repos: dict[Path, dict] = {}
    for raw_root in args.roots:
        root = Path(raw_root).expanduser().resolve()
        for repo in discover_repos(root, args.max_depth):
            all_repos[repo] = inspect_repo(repo, root)

    repos = sorted(all_repos.values(), key=lambda item: item["profile_name"])
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_count": len(repos),
        "repos": repos,
    }

    if args.output_json:
        output_json = Path(args.output_json).expanduser().resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = render_markdown(repos)
    if args.output_md:
        output_md = Path(args.output_md).expanduser().resolve()
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(markdown, encoding="utf-8")
    if args.output_shards_md:
        output_shards = Path(args.output_shards_md).expanduser().resolve()
        output_shards.parent.mkdir(parents=True, exist_ok=True)
        output_shards.write_text(render_shards_markdown(repos), encoding="utf-8")
    scan_roots_targets: list[Path] = []
    if args.output_scan_roots:
        scan_roots_targets.append(Path(args.output_scan_roots).expanduser().resolve())
    elif args.output_json:
        scan_roots_targets.append(Path(args.output_json).expanduser().resolve().with_name("repo-scan-roots.txt"))
    for output_scan_roots in scan_roots_targets:
        output_scan_roots.parent.mkdir(parents=True, exist_ok=True)
        output_scan_roots.write_text(render_scan_roots(repos), encoding="utf-8")
    if args.output_shard_dir:
        write_shard_summary_templates(repos, Path(args.output_shard_dir).expanduser().resolve())
    if not args.output_json and not args.output_md and not args.output_shards_md and not args.output_shard_dir:
        print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
