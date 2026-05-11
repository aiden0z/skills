# Depth Coverage

Use this ledger for multi-repo, deep, or continue runs. Its job is to prevent shallow packages from looking complete just because they have profiles, indexes, or an HTML report.

## Contents

- When Required
- Repository Roster Gate
- Historical Baselines
- Repo Shard Plan
- Parallelization Gate
- Repo Understanding Gate
- Required File
- Required Sections
- Per-repo Coverage Rules
- Zero-finding Repo Rules
- Final Claim Rule

## When Required

Create and maintain `submit/quality/depth-coverage.md` when any of these are true:

- The target has more than one audited repo.
- The user asks for "deep", "full", "complete", "continue", "deepen", or a package review.
- A previous audit package exists under or near the target root.
- The final package is a handoff/report package with reusable knowledge.

Lightweight single-repo scans may omit it only when `submission-scope.md` clearly declares a narrow strategy.

## Repository Roster Gate

For repo-group audits, the target root may be a plain directory that contains multiple repo checkouts. The parent directory does not need to be a Git repository.

Before candidate hunting, freeze the repo roster:

```bash
python3 scripts/discover_repositories.py <target-root> \
  --output-json <output-root>/work/scanner-output/repo-inventory.json \
  --output-md <output-root>/work/scanner-output/repo-inventory.md \
  --output-shards-md <output-root>/work/scanner-output/repo-shards.md \
  --output-scan-roots <output-root>/work/scanner-output/repo-scan-roots.txt \
  --output-shard-dir <output-root>/work/shards
```

Use the discovered roster as the source of truth for coverage:

- Broad source scans must use `work/scanner-output/repo-scan-roots.txt`, not the parent directory.
- Every discovered repo must appear in `quality/repository-versions.md`.
- Every discovered repo must have one `knowledge/repo-profiles/<repo>.md`.
- Every discovered repo must have a filled `work/shards/<repo>/shard-summary.json`.
- Every discovered repo must have a filled `work/shards/<repo>/candidates.md`.
- Every discovered repo must appear in `quality/depth-coverage.md`.
- Every discovered repo needs one of: submitted Bugs, parked candidates, or a concrete zero-finding rationale.

For large groups, create shards by domain, stack, or risk surface, but do not drop repos from the roster. If time or evidence is insufficient to inspect every repo deeply, the package must be labeled `first-pass`, `focused`, or `in-progress`; do not call it a complete/deep audit.

## Repo Shard Plan

For repo groups, default decomposition is one repo per task. This makes missing repos visible and lets agents parallelize without sharing mutable state.

Create `work/scanner-output/repo-shards.md` from the discovery script after the roster is frozen:

```markdown
| Shard | Repo | Mode | Execution | Primary Surfaces | Output Scope | Status |
|---|---|---|---|---|---|---|
| shard-001 | service-api | parallel-ok | parallel | HTTP -> service -> DB; scheduler -> client | `work/shards/service-api/` + `knowledge/repo-profiles/service-api.md` | running |
```

Rules:

- One repo per shard by default.
- Batch only tiny, tightly-coupled repos when separate profiles would add noise.
- Keep large or high-risk repos standalone.
- Parallel workers may write `submit/knowledge/repo-profiles/<repo>.md` and `work/shards/<repo>/...`.
- Parallel workers should not write global `submit/findings/`, `quality/lens-coverage.md`, `quality/depth-coverage.md`, `indexes/`, README, HTML, or overview image directly.
- The coordinator merges shard outputs serially after deduplication, priority calibration, and final ID renumbering.

## Parallelization Gate

For repo groups, parallel execution is not just an optimization; it is the default way to keep each repo from being reduced to a shallow shared sweep.

After Phase 1 profiles exist:

- Mark each shard `parallel`, `serial`, or `batched` in `work/scanner-output/repo-shards.md`.
- If the runtime has subagents, background agents, or parallel tool calls and there is more than one parallel-eligible shard, dispatch independent repo shards in parallel.
- If a parallel-eligible shard is run serially, record a concrete reason in both `repo-shards.md` and `work/shards/<repo>/shard-summary.json`.
- Acceptable serial reasons: runtime has no subagent/parallel facility, shard depends on another repo's local output, repo is tiny and batched with a named neighbor, user requested one-agent execution, or resource limits make parallel work unsafe.
- Unacceptable serial reasons: "faster", "simpler", "not needed", or no reason.

This gate does not force submitted Bug count upward. It forces the exploration process to be explicit enough that a small Bug count can be trusted or challenged.

## Repo Understanding Gate

Before candidate hunting, every repo shard must use `repo-understanding.md` to build a risk surface map from real code paths. The map is the bridge between inventory and Bug discovery: it explains which behaviors the agent understood before deciding where Bugs may exist.

The shard summary must include:

- `surface_map`: populated categories from `repo-understanding.md`, such as `entry_points`, `auth_boundaries`, `state_owners`, `consistency_boundaries`, `external_integrations`, `execution_boundaries`, `serialization_contracts`, `async_jobs`, `config_and_secrets`, `user_input_paths`, `file_paths`, `resource_lifecycle`, `observability_recovery`, and `deployment_runtime`.
- `hypothesis_loops`: one or more evidence-bearing loops for non-trivial repos. Each loop states a concrete failure hypothesis, entry point, traced boundary, guard/refutation, and result.
- `strongest_refuted_leads`: required for non-trivial repos with no submitted Bugs and no parked candidates.

Pattern scans are inputs, not understanding. A shard that only says "searched auth/config/http patterns" has not passed this gate.

Each shard must fill `work/shards/<repo>/shard-summary.json` and `work/shards/<repo>/candidates.md` before final package validation:

```json
{
  "repo": "service-api",
  "profile_name": "service-api",
  "parallel_eligible": true,
  "execution_mode": "parallel",
  "agent_or_worker": "repo-shard-001",
  "serial_reason": "",
  "coverage_classification": "first-pass",
  "focus_scope": "",
  "surface_map": {
    "entry_points": ["src/api/orders.py"],
    "auth_boundaries": ["src/auth/policies.py"],
    "state_owners": ["src/db/order_repo.py"],
    "consistency_boundaries": ["src/service/orders.py coordinates order row and payment intent"],
    "external_integrations": ["src/clients/payments.py"],
    "execution_boundaries": ["src/jobs/export.py launches report subprocess"],
    "serialization_contracts": ["src/schemas/order_event.py"],
    "async_jobs": ["src/jobs/reconcile.py"],
    "config_and_secrets": ["src/settings.py"],
    "user_input_paths": ["src/api/uploads.py"],
    "file_paths": ["src/storage/tmp.py"],
    "resource_lifecycle": ["src/storage/tmp.py create -> upload -> cleanup"],
    "observability_recovery": ["src/jobs/reconcile.py logs retry exhaustion without repair task"],
    "deployment_runtime": ["Dockerfile"]
  },
  "risk_surfaces_scanned": ["HTTP controllers", "service -> DB writes"],
  "evidence_paths": ["src/api/orders.py", "src/service/orders.py", "src/db/order_repo.py"],
  "commands_or_searches": ["rg -n \"timeout|retry|subprocess\" src", "rg -n \"@router|@app\" src"],
  "call_chains_traced": ["POST /orders -> create_order -> order_repo.insert"],
  "hypothesis_loops": [
    {
      "surface": "HTTP order creation",
      "hypothesis": "Duplicate client retry may create duplicate orders when idempotency is absent.",
      "entry_point": "POST /orders in src/api/orders.py",
      "chain_or_boundary": "create_order -> order_repo.insert",
      "guard_or_refutation": "src/api/orders.py checks Idempotency-Key before insert",
      "result": "refuted"
    }
  ],
  "strongest_refuted_leads": ["Duplicate order creation refuted by Idempotency-Key guard in src/api/orders.py"],
  "candidate_count": 2,
  "submitted_bug_ids": ["BUG-0003"],
  "zero_finding_rationale": "",
  "remaining_gaps": ["runtime retry config not executed"],
  "knowledge_atoms": ["order state owner: src/db/order_repo.py"],
  "profile_updated_from_shard": true,
  "profile_evidence_sections": ["Risk Surfaces", "Findings and Candidates", "Known Uncovered Areas"]
}
```

Rules:

- `evidence_paths` must be real paths in that repo.
- `commands_or_searches` must be concrete repo-local commands or patterns, not summaries like "rg auth/config/http patterns".
- `execution_mode` must be `parallel`, `serial`, or `batched`.
- `parallel_eligible` must be a boolean. Parallel-eligible shards run serially need a concrete `serial_reason`.
- Repos with 50+ source-like files need at least 3 evidence paths.
- `risk_surfaces_scanned` and `commands_or_searches` cannot be empty.
- Non-trivial repos (>10 source-like files) need a populated `surface_map` with at least 3 categories and at least one `hypothesis_loops` entry.
- Large repos (50+ source-like files) need at least 4 populated `surface_map` categories, including at least one executable/user-facing entry surface and at least one state, consistency, integration, execution, serialization, resource, file, config, or runtime boundary.
- Each hypothesis loop must include a concrete hypothesis, entry point, chain or boundary, guard/refutation, and result (`promoted`, `parked`, or `refuted`).
- If a repo has no candidates and no submitted Bugs, `zero_finding_rationale` must explain what was scanned and why nothing was promoted.
- If a non-trivial repo has no candidates and no submitted Bugs, it must also record a strongest refuted lead or a refuted hypothesis loop.
- `candidates.md` must not remain in its pending template state. It should list candidate leads, refuted leads, or a concrete zero-candidate rationale.
- Zero-candidate rationale and refuted leads must name concrete scanned paths, patterns, or guard evidence; generic "representative entry files" wording is not enough.
- `profile_updated_from_shard` must be true after local exploration, and `profile_evidence_sections` must include `Risk Surfaces`, `Findings and Candidates`, and `Known Uncovered Areas`.
- `focused` coverage requires a concrete `focus_scope`; `first-pass` and `focused` coverage require `remaining_gaps`.
- `deep-complete` for a 50+ file repo requires at least one `call_chains_traced` entry.
- `deep-complete` must not list blocking gaps such as unknown, uncovered, pending, or not-reviewed areas.
- Do not replace these summaries with a late script or inline heredoc that writes shard summaries, candidates, profiles, depth coverage, lens coverage, or final Markdown in one pass.

## Historical Baselines

Before scanning code, search the target root and sibling output locations for previous audit work:

- `*/submit/findings/*.md`
- `*bug-audit*`
- `*/indexes/findings.generated.json`
- `*/quality/submission-scope.md`

Treat these as comparison baselines, not as audited code targets and not as package scaffolding.

Fresh deep audits must build a new package from the current source tree:

- Do not copy prior finding files.
- Do not preserve prior Bug IDs.
- Do not reuse prior repo profiles, indexes, HTML reports, or report structure.
- Do not make the prior package the source of truth for counts.

For each baseline, record one of:

- **Reviewed for contrast**: after the independent scan, compare issue families and risk domains against the baseline, then record material omissions or why they were not promoted.
- **Excluded**: record why, such as stale branch, different scope, malformed package, or user-requested narrow scope.
- **None found**: record that no prior audit package was found in the searched locations.

Never ignore a historical package silently. A target with an existing 100+ finding package and a new 7-finding package is a depth failure unless the new package is explicitly scoped as a fresh narrow pass or the old package was reviewed for contrast and differences are explained.

## Required File

`submit/quality/depth-coverage.md` should be concise but complete. Use the final deliverable language.

Suggested Chinese skeleton:

```markdown
# Depth Coverage

## Repository Roster Gate

- Roster source: `work/scanner-output/repo-inventory.json`
- Discovered repos: 0
- Profiles completed: 0
- Coverage classification: first-pass | focused | deep-complete
- Missing roster entries: none | <list>

## Repo Shard Plan

| Shard | Repo | Mode | Execution | Primary Surfaces | Output Scope | Status |
|---|---|---|---|---|---|---|

## Repository Inventory

| Repo | Branch | Commit | Profile | Source-like Files |
|---|---|---|---|---:|

## Historical Baselines

| Path | Finding Count | Decision | Reason |
|---|---:|---|---|

## Per-repo Coverage

| Repo | Submitted Bugs | Parked Candidates | Primary Surfaces Scanned | Remaining Gaps |
|---|---:|---:|---|---|

## Zero-finding Repos

| Repo | Scanned Surfaces | Rationale | Remaining Gaps |
|---|---|---|---|

## Depth Conclusion

- Scope claim:
- Historical baseline review summary:
- Known weak areas:
```

English section aliases are also valid: `Repository Roster Gate`, `Repository Inventory`, `Historical Baselines`, `Per-repo Coverage`, `Zero-finding Repos`, and `Depth Conclusion`.

## Required Sections

These sections are always required when `depth-coverage.md` is used:

- `Repository Inventory` / `仓库清单`
- `Historical Baselines` / `历史审计基线`
- `Per-repo Coverage` / `分仓覆盖`
- `Zero-finding Repos` / `零 Bug 仓`
- `Depth Conclusion` / `深度结论`

For repo-group roots or multi-repo final handoff, `Repository Roster Gate` / `仓库名册门禁` is also required.

The validator checks these aliases and also checks that every repo profile name appears somewhere in the file.

For repo-group roots, final validation with `--repo-root <target-root>` also checks every discovered repo against `repository-versions.md`, `repo-profiles/`, and this file. A non-Git parent directory is valid; the validator expands it to child repo checkouts.

## Per-repo Coverage Rules

Every audited repo needs one row or paragraph with:

- Profile path or profile status.
- Submitted Bug count.
- Parked candidate count when available.
- Primary surfaces scanned: relevant `repo-understanding.md` surface-map categories, such as entry points, auth boundaries, state/consistency owners, integrations, execution boundaries, serialization/contracts, async jobs, config/secrets, user/file paths, lifecycle, observability/recovery, deployment/runtime, or dependencies as applicable.
- Remaining gaps: runtime-only behavior, deployment-only configuration, generated code, vendored code, missing tests, or intentionally skipped areas.

For a repo to be called deeply explored, include a concise signal that at least one real call chain was traced from entry point to state owner, integration, execution boundary, or lifecycle transition. For example:

```markdown
| service-api | 2 | 3 | HTTP controllers -> service layer -> DB writes; scheduler -> outbound client | Deployment-only retries unverified |
```

If only pattern scans and sample reads were performed, classify the row or package as first-pass/focused instead of deep-complete.

If a repo has many Bugs, summarize by issue family and link to `indexes/findings.generated.md` rather than duplicating every Bug.

## Zero-finding Repo Rules

Zero findings can be valid. They are only valid when the package says why.

For each zero-finding repo, include:

- What was scanned.
- Why no submitted Bug was promoted.
- Whether weak leads were parked.
- What remains unknown.

Do not use empty praise such as "no issues found". Prefer concrete language:

```markdown
| template-repo | README and file inventory | Only one template file; no executable entry point or config surface in current checkout | Runtime behavior not applicable until template expands |
```

## Final Claim Rule

Do not write or say:

- "deep analysis complete"
- "all repos fully analyzed"
- "complete multi-repo audit"

unless all are true:

- `depth-coverage.md` is current.
- The frozen roster count equals version rows, repo profiles, and depth coverage rows.
- Every repo has a filled shard summary with real evidence paths.
- Every repo has a filled candidates file with candidate leads, refuted leads, or zero-candidate rationale.
- Every repo profile was revised from shard evidence and the shard summary records the required profile evidence sections.
- Any `focused` row names the focus scope; any `first-pass`/`focused` row names remaining gaps.
- Every shard records execution mode; serial execution for parallel-eligible repos has a concrete reason.
- `lens-coverage.md` is current.
- Every audited repo has a profile.
- Historical baselines are reviewed for contrast, explicitly excluded, or recorded as none found.
- Zero-finding repos have a rationale.
- `validate_bug_package.py` exits 0 with the final handoff flags.

If one of these is missing, use narrower wording such as "first pass", "focused pass", "candidate package", or "coverage still open".
