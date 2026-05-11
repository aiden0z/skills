# Workflow

## Contents

- Phase 0: Audit Charter
- Phase 1: Workspace and Roster
- Phase 2: High-recall Pattern Plan
- Phase 3: Shard Plan
- Phase 4: Repo Briefs
- Phase 5: Repo-local Exploration
- Phase 6: Shard Evidence Gate
- Phase 7: Cross-repo and META Lenses
- Phase 8: Candidate Promotion
- Phase 9: Findings
- Phase 10: Knowledge
- Phase 11: Validation, Report Assets, and Handoff

## Phase 0: Audit Charter

- Confirm workspace root, audit output root, repos, reference repos, provided analyst when available, date, language, and package audience.
- Record explicit audit depth intent in `quality/submission-scope.md`: `deep`, `full`, `per-repo-deep`, `first-pass`, `focused`, `lightweight`, or `custom`. User wording such as "deep", "full", "complete", "尽可能", "每个 repo", "逐仓", or "完整" is a deep/full intent unless the user later accepts a downgrade.
- Record repository branch, commit hash, and dirty status when available; use `metadata.md`.
- If the workspace already exists, read `resume-audit.md` before editing findings.
- If the task triggers Deep Discussion Mode, read `deep-discussion.md` and write a short analysis charter before inventory.
- If the user asks for automatic execution, proceed without repeated confirmation, but keep edits inside the output root and record assumptions in `quality/submission-scope.md`.
- Infer safe defaults for date, language, package name, and optional package parts; do not infer analyst identity.
- Create a lowercase, descriptive workspace name with separate `submit/` and `work/` directories.
- For fresh deep/full audits, search for historical audit packages before scanning code. Treat them as comparison baselines, not scaffolding.

## Phase 1: Workspace and Roster

Run `scripts/init_bug_workspace.py` first.

For a parent directory containing multiple repo checkouts, run `scripts/discover_repositories.py` immediately after workspace creation:

```bash
python3 scripts/discover_repositories.py <target-root> \
  --output-json <output-root>/work/scanner-output/repo-inventory.json \
  --output-md <output-root>/work/scanner-output/repo-inventory.md \
  --output-shards-md <output-root>/work/scanner-output/repo-shards.md \
  --output-scan-roots <output-root>/work/scanner-output/repo-scan-roots.txt \
  --output-shard-dir <output-root>/work/shards
```

The parent directory itself does not need to be a Git repo. The frozen roster is the source of truth for version evidence, repo profiles, shard summaries, depth coverage, and final validation.

Before this roster exists, do not run `rg --files`, broad `find`, `grep`, or source inventory over the parent target root; that can load generated audit/eval artifacts into the agent's working context before the boundary is established. Use `discover_repositories.py` as the inventory mechanism.

Use `work/scanner-output/repo-scan-roots.txt` as the input list for broad source searches. Do not run broad `rg`/`grep` over the parent directory; ad hoc exclude globs are not reliable because prior audit/eval workspaces may use arbitrary names. Use a roots-file loop for ad hoc scans:

```bash
while IFS= read -r repo; do
  rg -n "<pattern>" "$repo" -S
done < <output-root>/work/scanner-output/repo-scan-roots.txt
```

Parent-root scans can pull in old `*bug-audit*` packages, `ab-test-*` outputs, generated reports, dependency folders, and build outputs. If a broad scan returns `/work/shards/`, `/work/scanner-output/`, `/submit/findings/`, `/submit/quality/`, `/submit/knowledge/`, or `/submit/indexes/` paths, discard it and rerun against the frozen repo roots. Historical packages are reviewed for contrast after the independent source scan.

Do not write final README, final Bug records, final knowledge docs, HTML, or overview image in this phase.

## Phase 2: High-recall Pattern Plan

Do not run broad high-recall seeds before repo-local exploration. First let agents read code, build surface maps, and return candidate/gap reports. For repo-group, deep/full, security/auth, or "find as many Bugs as possible" requests, plan to generate `work/scanner-output/llm-patterns.json` after Phase 5 from:

- risk surfaces agents did not cover,
- patterns found in one repo but not checked in siblings,
- issue families missing from the fresh candidate pool,
- language/framework-specific risky constructs observed in the actual repos.

The later scan is supplemental evidence. It should expand coverage, not replace model-led code reading.

## Phase 3: Shard Plan

For repo groups, default decomposition is one repo per shard. Batch only tiny, tightly-coupled repos when separate profiles add noise; keep large or high-risk repos standalone.

Before candidate hunting:

- Mark each shard `parallel`, `serial`, or `batched` in `work/scanner-output/repo-shards.md`.
- Fill the execution fields in every `work/shards/<repo>/shard-summary.json`.
- If subagents, background agents, or parallel tool calls are available and more than one shard is parallel-eligible, dispatch independent repo shards in parallel.
- If a parallel-eligible shard runs serially, record a concrete `serial_reason`.
- Parallel workers may write only `submit/knowledge/repo-profiles/<repo>.md` and `work/shards/<repo>/...`.
- The coordinator owns global findings, lens coverage, depth coverage, indexes, README, HTML, overview image, and final validation.

## Phase 4: Repo Briefs

Build just enough knowledge to guide exploration; do not turn this into final documentation.

For every roster repo, capture:

- Languages, frameworks, build systems, manifests, and verification command sources.
- Entry points: API views/controllers, service/provider layers, tasks, workers, CLIs, scripts, UI routes.
- External systems: databases, cloud APIs, storage, network controllers, HTTP APIs, queues, shells, devices, auth.
- Largest files/functions and generic directories: `utils`, `common`, `helpers`, `shared`.
- Initial architect-level surfaces from `repo-understanding.md`: state owners, consistency boundaries, external integrations, execution boundaries, serialization/contracts, async workflows, config/secrets, user/file paths, resource lifecycle, observability/recovery, and deployment/runtime assumptions.

Start one `submit/knowledge/repo-profiles/<repo>.md` per roster repo using `repo-profile.md`, but treat it as a living profile. Final profiles must be revised from shard evidence, not left as inventory-only templates.

Start `quality/depth-coverage.md` for multi-repo/deep runs with roster count, profile count, historical baselines, and planned shard rows.

## Phase 5: Repo-local Exploration

Repo-local exploration must happen before cross-repo conclusions.

Load `repo-understanding.md` first. Before candidate promotion, every non-trivial repo needs a surface map that names concrete source paths for relevant architect-level surfaces: entry points, auth boundaries, state owners, consistency boundaries, external integrations, execution boundaries, serialization/contracts, async jobs, config/secrets, user input paths, file paths, resource lifecycle, observability/recovery, deployment/runtime, or dependency surfaces as applicable.

Then load `exploration-lenses.md`. META checks are in `exploration-lenses.md`; read cross-repo amplification in `exploration-lenses.md` only after repo-local summaries exist. For each shard:

1. State concrete failure hypotheses.
2. Hunt through repo-local entry points and risk surfaces.
3. Refute candidates with sibling implementations or guards.
4. Promote verified candidates or park weak leads.
5. Update the repo profile and `work/drafts/knowledge-capture.md` when new boundaries, state owners, invariants, or verification sources are learned.

Every repo needs at least one explicit sweep over its relevant surface map. Do not reduce this to a fixed grep checklist: backend repos often need state/consistency/integration tracing; tool repos often need execution/file/resource lifecycle tracing; frontend repos often need route/auth/API/state/error-display tracing; infra repos often need deployment/runtime/recovery tracing. Non-trivial repos need at least one hypothesis loop that starts from a concrete failure mode and ends in `promoted`, `parked`, or `refuted`. Large/high-risk repos need call-chain tracing from entry point to state owner, integration, execution boundary, or lifecycle transition before they can be called deeply explored.

For deep, full, repo-group, or "find as many Bugs as possible" requests, this phase is recall-oriented. Keep medium/low-confidence leads as candidates instead of silently dropping them. A candidate can later be promoted, parked, refuted, or merged, but it must stay visible in shard notes until the promotion pass explains the outcome.

After initial repo-local agent reports exist, generate LLM-targeted patterns and run the supplemental high-recall scan:

```bash
python3 scripts/run_high_recall_scan.py <output-root>/work/scanner-output/repo-scan-roots.txt \
  --inventory <output-root>/work/scanner-output/repo-inventory.json \
  --patterns-file <output-root>/work/scanner-output/llm-patterns.json \
  --output-json <output-root>/work/scanner-output/high-recall-scan.json \
  --output-md <output-root>/work/scanner-output/high-recall-scan.md \
  --output-shard-dir <output-root>/work/shards
```

This helper prevents shell quoting errors with newline-delimited repo roots and keeps historical audit packages out of source scans. It writes `work/scanner-output/high-recall-scan.*` and `work/shards/<repo>/search-seeds.md`.

Use each shard's `search-seeds.md` for supplemental triage. The search seeds are a coverage backstop; repo-local surface maps and call-chain tracing remain the evidence layer.

For every shard with high-recall seeds, fill `seed_triage` in `shard-summary.json` before final candidate promotion. Record representative reviewed seeds across categories with:

- `category`: category from `search-seeds.md`
- `location`: concrete `path:line`
- `seed`: the risky line or symbol reviewed
- `follow_up`: what entry point, guard, sibling implementation, or boundary was traced
- `outcome`: `promoted`, `parked`, `refuted`, or `merged`
- `candidate_or_reason`: Bug ID, candidate title, merge target, or false-positive reason

This is the bridge from 600+ search seeds to a credible candidate pool. A low Bug count is credible only when seed triage explains why reviewed seeds were refuted or parked.

Each shard must update:

- `work/shards/<repo>/shard-summary.json`
- `work/shards/<repo>/candidates.md`
- `submit/knowledge/repo-profiles/<repo>.md`

Filled shard summaries must include:

- `coverage_classification`: `first-pass`, `focused`, or `deep-complete`
- `focus_scope`: required when classification is `focused`
- `surface_map`: evidence paths grouped by repo risk surface
- `hypothesis_loops`: concrete hypothesis, entry point, chain/boundary, guard/refutation, and result
- `seed_triage`: representative high-recall seeds reviewed and classified
- `strongest_refuted_leads`: the best refuted leads when no Bug is submitted
- `candidate_count`: all retained repo-local leads after first triage, including leads later promoted to submitted Bugs; this must match the evidence-bearing bullets in `candidates.md` plus submitted Bug links
- `submitted_bug_ids`: final Bug IDs promoted from this shard after consolidation
- `profile_updated_from_shard: true`
- `profile_evidence_sections`: at least `Risk Surfaces`, `Findings and Candidates`, and `Known Uncovered Areas`

Zero-candidate shards are valid only when the summary and candidates file say what was scanned, which suspicious leads were refuted or parked, why no candidate was promoted, and what remains unknown.

For non-zero candidate shards, write one bullet per retained lead in `candidates.md`. Each bullet should include a candidate id, rough priority, outcome, concrete `path:line` or `BUG-0000`, and the missing gate or promotion result. Do not compress eight leads into one generic line and then set `candidate_count: 8`.

Do not manufacture candidate recall by filling each shard to a target count from scanner seeds. `high-recall-scan.json` provides prompts for repo-local triage, not ready-made candidates. Repeated parked lines with the same generic explanation are a workflow failure; each retained lead must name the inspected boundary, trigger hypothesis, observed or missing guard, and promote/park/refute/merge reason.

## Phase 6: Shard Evidence Gate

Before writing final Bug records, README, HTML, or overview assets, run:

```bash
python3 scripts/validate_bug_package.py <submit-root> \
  --validate-shards-only \
  --repo-root <target-root>
```

Fix all shard-gate errors before continuing. This gate checks roster coverage, high-recall scan outputs, shard plans, execution mode, serial reasons, candidates files, real evidence paths, scan commands, candidate counts, zero-finding rationale, profile updates, and coverage classification.
It also checks repo-understanding evidence: non-generic surface maps, hypothesis loops, refuted leads for zero-finding non-trivial repos, and profile updates sourced from exploration.

If the shard gate exits non-zero or prints any `ERROR:`, stop the final-handoff path. Do not run the normal validator as a substitute, do not generate `README.md`, `bug-audit-report.html`, or `audit-overview.png`, and do not tell the user the audit is complete. Report the workspace as `in-progress`, include the shard-gate error count, and keep fixing repo-local shard evidence.

A passing shard gate writes `work/scanner-output/shard-gate.passed.json`. Final Bug records, README, HTML, and overview image generation must happen after that receipt; final validation rejects stale findings or report assets.

The shard gate is not a license to bulk-fill evidence. Do not repair shard files with one large inline script that loops over every repo and writes generic candidates, profiles, depth coverage, or lens records. Do not use an inline `TARGET_PER_REPO` loop or a high-recall seed replay to pad `candidates.md`. Fix the underlying repo-local summaries with concrete paths, searches, and candidate/refutation evidence.

## Phase 7: Cross-repo and META Lenses

Only after repo-local shard summaries exist, read cross-repo amplification in `exploration-lenses.md` for multi-repo audits.

- Boundary records use repo profiles and shard evidence to inspect cross-repo contracts, shared state, shared config, version skew, and ownership gaps.
- META-1 uses profile Intent Inputs to compare README/ADR/design intent against actual implementation.
- META-2 spot-checks failure-path tests for modules touched by boundary-driven candidates.
- Every applicable boundary needs a concise record in `quality/lens-coverage.md`, including zero-candidate and not-applicable records.

Do not let a cross-repo grep replace repo-local exploration.

## Phase 8: Candidate Promotion

Before a candidate becomes a Bug, answer:

- What exact entry point triggers the path?
- What resource or user operation is affected?
- What code evidence proves the risky ordering or missing guard?
- What failure mode is realistic in production?
- What would the user/operator see?
- What existing wrapper, config, transaction, retry, cleanup, or permission check might make this a false positive?
- Does the finding duplicate another Bug, or is it a distinct module/path?

If any answer is weak, lower confidence or move it to `work/candidates/`. Use `candidate-triage.md` and `deduplication.md`.

Before freezing final counts, run a Priority Promotion Sweep:

- Review retained candidates across P1, P2, P3, and P4; P1 saturation is not a stopping condition.
- Mark candidate notes with `priority_estimate`, `outcome`, `bug_gate`, and `missing_gate` when known.
- Promote every `bug_gate=complete` candidate to `findings/P*/` or merge it into a submitted Bug.
- Leave a candidate parked only when the missing gate is explicit: code evidence, trigger path, failure mode, affected resource, impact, duplicate/merge target, deployment assumption, runtime-only confirmation, or false-positive guard.
- A P1-only final package is valid only when lower-priority candidates are parked/refuted/merged with named missing gates, or the user explicitly requested critical-only scope.

After promotion/refutation, run:

```bash
python3 scripts/generate_candidate_index.py <submit-root>
```

This creates `indexes/candidates.generated.json`, `indexes/candidates.generated.md`, and `quality/candidate-coverage.md`. The candidate funnel must explain how many leads were discovered, how many became submitted findings, how many remain parked or unpromoted, and the P1-P4 promotion sweep outcomes. For repo-group final packages, pre-package validation rejects a missing or inconsistent candidate index and any `gate-complete` candidate that remains unsubmitted without a recorded critical-only scope.

## Phase 9: Findings

- Use `bug-schema.md`.
- Put findings in `findings/P1`, `findings/P2`, `findings/P3`, `findings/P4`.
- Write submitted Bug records directly from promoted candidate evidence. Use one edit/command per Bug record when the content is prose-heavy. A single-file heredoc is acceptable only as a shell fallback for exactly one named Bug file; it must not contain loops, arrays of Bug files, or multiple final artifact paths.
- Do not embed multiple full Bug records in one Python/JS/shell heredoc or package-generation script. If you need to renumber or rename files, do it mechanically after the content exists; do not regenerate the package prose in a batch script.
- Keep static-analysis status clear: do not claim runtime verification unless runtime proof exists.
- Add fix boundary, minimum safe fix, and suggested verification commands. Commands must be traceable to repository files; write `unconfirmed` when no trustworthy command is visible.
- The final submitted package must contain a single contiguous `BUG-0001..BUG-N` sequence. For parallel multi-agent merges, see `resume-audit.md` → "Parallel Multi-Agent Consolidation".

## Phase 10: Knowledge

Promote evidence-backed atoms from `work/drafts/knowledge-capture.md` into `submit/knowledge/`; leave speculative or refuted atoms in `work/`.

Do not generate repo profiles, depth coverage, lens coverage, and final knowledge from one inline script. Write or revise one evidence-bearing knowledge/quality artifact at a time. If a helper is needed, it may format tables from already-filled shard JSON; it must not contain the final prose claims itself.

Final knowledge should help developers or later agents continue without rescanning basics:

- `knowledge/system-overview.md`
- `knowledge/repo-relationship-map.md`
- `knowledge/risk-paths.md`
- `knowledge/architecture-design-review.md`
- `knowledge/repo-profiles/*.md`

Before packaging, revise each repo profile's `Verification Sources`, `Risk Surfaces`, `Findings and Candidates`, and `Known Uncovered Areas` sections so the profile reflects exploration evidence and submitted Bug families.

Architecture review should describe discovered risk signals, not dictate abstract principles.

## Phase 11: Validation, Report Assets, and Handoff

Run this order:

1. Generate indexes with `scripts/generate_bug_index.py`.
2. Generate the candidate funnel with `scripts/generate_candidate_index.py <submit-root>` for repo-group, deep/full, or high-recall runs. Do not hand-write or patch `indexes/candidates.generated.json`; it must contain the generator metadata expected by validation.
3. Run pre-package validation with `scripts/validate_bug_package.py --repo-root <target-root>`. A passing run before report assets writes `work/scanner-output/prepackage-validation.passed.json`.
4. Run `evaluation.md` after structural validation.
5. Evaluate all P1/P2 Bugs; for large packages, sample each issue family and risk domain.
6. Record downgrades, removals, merges, priority changes, and weak areas in `quality/submission-scope.md`.
7. Generate report assets only after shard validation and pre-package validation pass.
8. Before generating final HTML or overview assets, compare audit depth intent against `quality/depth-coverage.md`; if deep/full/per-repo-deep was requested but coverage is first-pass/focused/in-progress, continue exploration or record user-accepted downgrade first.
9. Generate `bug-audit-report.html` by default for final handoff/report packages.
10. Generate `audit-overview.png` only when requested/expected and after the overview decision is recorded. In interactive mode, do not block kickoff or final validation on an undecided optional image; record `deferred-post-handoff` and ask after the validated handoff summary.
11. Run final validation with `--require-knowledge --require-html-report --repo-root <target-root>` and add `--require-image` when the overview image is included.
12. Deliver the final summary only after final validation exits 0.

Report assets are render layers over final evidence. They must not be created early to make a thin exploration look finished.

Before Step 1, self-check the artifact writing trace: no command should have created or rewritten multiple final Markdown/shard artifacts in one process. If you used an inline script or heredoc batch for `submit/findings`, `submit/knowledge`, `submit/quality`, `work/shards/*/candidates.md`, or `work/shards/*/shard-summary.json`, the workflow failed even if package validation passes. Replace the batch output with one-artifact-at-a-time evidence writes before continuing.

`generate_bug_report_html.py` refuses final HTML generation when audit depth intent is missing or unresolved, or when `work/scanner-output/prepackage-validation.passed.json` is missing. For repo-group audits, it also enforces the shard gate by default and refuses final HTML generation when `work/scanner-output/shard-gate.passed.json` is missing. Its ungated draft flag is only for a clearly labeled non-final preview and must not be used for final handoff.

The HTML generator and final validator also enforce depth-intent mismatch: a deep/full/per-repo-deep request cannot produce final report assets from first-pass/focused/in-progress coverage unless `submission-scope.md` or `depth-coverage.md` records that the user accepted the downgrade.
