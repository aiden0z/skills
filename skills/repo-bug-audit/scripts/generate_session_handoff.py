#!/usr/bin/env python3
"""Generate a session-1 to session-2 handoff plan from candidate index and shard evidence.

Reads the candidate index and per-shard summaries, identifies high-priority repos
for deepening, and writes a structured plan to work/session-end-state.md.
"""

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a session-1 to session-2 handoff plan"
    )
    parser.add_argument("submit_root", help="Path to submit/ directory")
    parser.add_argument(
        "--max-deepen-repos",
        type=int,
        default=8,
        help="Maximum repos to recommend for session 2 deepening",
    )
    parser.add_argument(
        "--top-n-candidates",
        type=int,
        default=20,
        help="Top N candidates to highlight for immediate attention",
    )
    args = parser.parse_args()
    submit_root = Path(args.submit_root).expanduser().resolve()
    if not submit_root.is_dir():
        print(f"Error: {submit_root} is not a directory")
        return 1

    workspace_root = submit_root.parent
    if (workspace_root / "work").is_dir():
        pass
    elif (submit_root.parent / "work").is_dir():
        workspace_root = submit_root.parent
    else:
        workspace_root = submit_root.parent

    # Load candidate index
    index_path = submit_root / "indexes" / "candidates.generated.json"
    if not index_path.is_file():
        print(f"Error: {index_path} not found. Run generate_candidate_index.py first.")
        return 1

    with open(index_path) as f:
        index = json.load(f)

    # Load per-shard summaries to get candidate counts and priorities
    shards_root = workspace_root / "work" / "shards"
    repo_data: list[dict] = []
    for shard_dir in sorted(shards_root.iterdir()):
        if not shard_dir.is_dir():
            continue
        summary_path = shard_dir / "shard-summary.json"
        if not summary_path.is_file():
            continue
        with open(summary_path) as f:
            summary = json.load(f)
        candidates_path = shard_dir / "candidates.md"
        candidates_text = ""
        if candidates_path.is_file():
            candidates_text = candidates_path.read_text(encoding="utf-8", errors="replace")

        # Count P1/P2 candidates
        p1_count = candidates_text.count("P1-cand-")
        p2_count = candidates_text.count("P2-cand-")
        total = summary.get("candidate_count", 0)

        repo_data.append({
            "name": summary.get("repo", shard_dir.name),
            "candidate_count": total,
            "p1_count": p1_count,
            "p2_count": p2_count,
            "coverage": summary.get("coverage_classification", "unknown"),
        })

    # Sort by priority: P1 count desc, then P2 count desc
    repo_data.sort(key=lambda r: (-r["p1_count"], -r["p2_count"], -r["candidate_count"]))

    # Select repos for deepening
    deepen_repos = [r for r in repo_data if r["p1_count"] > 0 or r["p2_count"] > 2]
    deepen_repos = deepen_repos[:args.max_deepen_repos]

    # Cross-repo signals from validator output
    cross_repo_notes = []
    cross_file = workspace_root / "work" / "scanner-output" / "cross-repo-patterns.txt"
    if cross_file.is_file():
        cross_repo_notes = cross_file.read_text(encoding="utf-8", errors="replace").strip().splitlines()

    # Build handoff plan
    handoff = []
    handoff.append("# Session 1 → Session 2 Handoff Plan")
    handoff.append("")
    handoff.append(f"Generated from: {index_path}")
    handoff.append(f"Candidates found: {index.get('total_candidates', sum(r['candidate_count'] for r in repo_data))}")
    handoff.append("")
    handoff.append("## Repos to Deepen (by priority)")
    handoff.append("")
    handoff.append("| # | Repo | Candidates | P1 | P2 | Coverage |")
    handoff.append("|---|---|---|---|---|---|")
    for i, r in enumerate(deepen_repos, 1):
        handoff.append(f"| {i} | {r['name']} | {r['candidate_count']} | {r['p1_count']} | {r['p2_count']} | {r['coverage']} |")
    handoff.append("")

    # Skipped repos
    skipped = [r for r in repo_data if r not in deepen_repos]
    if skipped:
        handoff.append("## Skipped (low priority or zero findings)")
        handoff.append("")
        for r in skipped:
            handoff.append(f"- {r['name']}: {r['p1_count']} P1, {r['p2_count']} P2, {r['candidate_count']} total")
        handoff.append("")

    handoff.append("## Session 2 Checklist")
    handoff.append("")
    handoff.append("1. Resume from this output root")
    handoff.append("2. For each deepen repo: full call-chain tracing, complete seed triage, upgrade to `deep-complete`")
    handoff.append("3. Run cross-repo boundary and META checks across deepened repos")
    handoff.append("4. Deduplicate, promote, write Bug records")
    handoff.append("5. Full validation and final package")
    handoff.append("")

    if cross_repo_notes:
        handoff.append("## Cross-Repo Patterns to Investigate")
        handoff.append("")
        for note in cross_repo_notes[:10]:
            handoff.append(f"- {note}")
        handoff.append("")

    # Write
    output_path = workspace_root / "work" / "session-end-state.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(handoff))
    print(f"Handoff plan written to: {output_path}")
    print(f"Repos to deepen: {len(deepen_repos)}")
    print(f"Top priority repo: {deepen_repos[0]['name'] if deepen_repos else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
