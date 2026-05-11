# Evaluation

Use this after findings are written and before final packaging. Evaluation checks whether records are real, useful, prioritized correctly, and consistent as a package.

Evaluation does not replace `validate_bug_package.py`. The script checks structure; this file checks judgment.

> **Authenticity First** (`references/authenticity.md`) is the rule that overrides every gate below. A Bug that fabricates content fails immediately, regardless of which other checks it would have passed.

## Contents

- 30-Minute-Fix Rubric (Bug-Level)
- Bug-Level Gate
- Q6 — Lens Coverage Gate (Package-Level)
- Package-Level Gate
- Depth Gate
- Priority Calibration
- Skill Regression Gate
- Portable Eval Suite

## 30-Minute-Fix Rubric (Bug-Level)

Read **only the Bug Markdown** (do not open the repo). Answer 5 questions:

1. **What to change** — can you name the file / function / call-site to modify?
2. **How to change** — can you state the minimum-fix direction (not full patch)?
3. **What can break** — at least one compatibility / performance / cross-service / data risk?
4. **How to verify** — at least one regression path (command / test file / reviewable code location)?
5. **Authenticity veto** — does every concrete noun (function / file / line / call chain / command / metric / framework) actually exist in the repo or package?

**Pass = 3-of-4 on Q1-Q4, AND Q5 is fully clean.** Q5 is a single-veto question: any one fabricated noun → entire Bug fails, regardless of how well Q1-Q4 score.

If a Bug fails:

- Q5 fail (fabrication) → **remove the fabricated claim** before deciding next action; do not just downgrade.
- Q1-Q4 fail (substance) → take one of the actions below.

## Bug-Level Gate

Run on every submitted Bug for small packages. For large packages, run on all P1/P2 Bugs and at least one representative Bug from each issue family.

A Bug passes only when these are explicit:

- Entry point: API, task, command, callback, lifecycle hook, or user operation.
- Trigger condition: concrete condition, not only pattern wording.
- Code evidence: file/function/ordering/guard/cleanup evidence.
- Failure mode: realistic exception, timeout, partial success, race, retry exhaustion, config edge, or operator action.
- Impact: affected resource, tenant, user, data, control-plane path, or recovery path.
- False-positive review: existing wrapper, transaction, retry, policy, cleanup, or config has been checked.
- Priority: P1/P2 is justified by blast radius, data/security risk, recovery cost, or core workflow impact.
- Confidence: high/medium/low matches evidence strength.
- Fix boundary: safest affected files/functions/contracts are named, and unrelated modules are not implied.
- Fix suggestion: actionable but not overly prescriptive.
- Suggested verification commands: commands are traceable to repository files, or the record clearly says they are not confirmed.
- Validation standard: clear checks for the developer or fixing Agent.

If any item is weak, take exactly one of the following actions and log the change in `quality/submission-scope.md`:

- Lower confidence, or
- Move the lead to `work/candidates/`, or
- Merge it into a stronger Bug, or
- Record the uncertainty in the Bug and `quality/submission-scope.md`.

For Q5 (authenticity) failures specifically: first **strip the fabricated claim** (delete the invented file ref / fake command / non-existent symbol), then re-evaluate on the remaining real content. If what remains is too thin to support the priority, apply one of the four actions above. Never "fix" a fabricated claim by inventing a different one.

Gate failure never pauses the workflow. The four actions above are the full action space; do not invent ad-hoc fixes and do not ask the user mid-scan. If a P1/P2 Bug fails because it depends on unverified assumptions, prefer "move to candidates" over "lower confidence" — submitted findings should not carry low-confidence priority claims that look authoritative in README counts.

## Q6 — Lens Coverage Gate (Package-Level)

Apply after Q1-Q5 pass on individual Bugs. Read `submit/quality/lens-coverage.md` and check:

- For each lens enabled by the audit (see `exploration-lenses.md` for the current boundary set; user-specified strategy in `submission-scope.md` overrides), is there an entry?
- Does each entry have all 5 sections for the package language? English labels: `Scanned Entry Points` / `Patterns` / `Candidates` / `Exclusion Reasons` / `Uncovered`. Chinese labels: `已扫描入口` / `关注模式` / `候选数` / `排除原因` / `未覆盖`.
- Do scanned entry points list real paths? Do exclusion reasons cite `path:line` anchors when candidates were excluded? Does uncovered area name a concrete gap rather than claiming perfect coverage?
- Q5 (authenticity) applies to lens-coverage.md content too — fabricated coverage claims, non-existent wrappers, fake paths, or made-up exclusion reasons fail the same way fabricated Bugs fail.

**Pass = every enabled lens has a complete, authentic 5-section record.** Missing lens or missing section → ERROR (also caught by validator). Sections present but content fabricated → Q5 veto applied to that lens's section; agent must strip fabrication and re-evaluate (same rule as Bug Q5 failure).

"Applied and found no Bug" with concrete scanned entry points, search patterns, `Candidates: 0`, `Exclusion Reasons: N/A (no candidates)`, and a real uncovered area is a **passing** record, not a failure. Encourage this output over invented findings.

## Package-Level Gate

Check the package as a single artifact:

- README counts match `indexes/findings.generated.json` exactly. No rounding, no estimates.
- Knowledge claims in `system-overview.md`, `repo-relationship-map.md`, `risk-paths.md` each have ≥1 supporting code reference or Bug ID anchor (Q5 veto applies to knowledge files too).
- `repo-profiles/<repo>.md` tech stack is read from real `package.json` / `pyproject.toml` / `pom.xml` / `Cargo.toml` / `go.mod`, not inferred from filenames.
- `repo-profiles/<repo>.md` includes verification sources, risk surfaces, submitted Bug links, candidate links when present, and known uncovered areas. Missing profile sections are warnings by default and become validation errors under `--require-knowledge`.
- `architecture-design-review.md` each risk bullet has ≥1 Bug ID or ≥1 code reference; pure abstract claims are removed.
- `submission-scope.md` "downgraded / removed / merged" entries cite originating Bug ID and concrete failed gate; no blanket "fully verified / fully reviewed" claims.
- P1/P2 summaries align with actual Bug metadata and issue families.
- Repeated issue families are grouped in indexes or README without hiding concrete Bugs.
- Stability risks are ordered ahead of cosmetic or narrow issues when priorities tie.
- Knowledge files explain the relationships used by submitted findings.
- Knowledge files identify language ecosystems, build/test metadata, and cross-repo contracts when they affect later fixes.
- Architecture review describes discovered risk signals, not solution principles.
- `audit-overview.png`, README, indexes, and knowledge use the same counts and risk names.
- No temporary files, candidates, scanner dumps, old images, or drafts are inside `submit/`.
- Text avoids process narration, self-reference, audience explanation, and AI-flavored phrases.

## Depth Gate

Use this to avoid shallow-but-large submissions:

- For multi-repo/deep runs, read `quality/depth-coverage.md` before accepting the package-level conclusion.
- For repo-group roots, compare the frozen roster in `work/scanner-output/repo-inventory.json` against `quality/repository-versions.md`, `knowledge/repo-profiles/`, and `quality/depth-coverage.md`. Missing roster entries are a depth failure even when the package validates other structure.
- For repo-group roots, inspect `work/shards/<repo>/shard-summary.json` and `work/shards/<repo>/candidates.md` for each repo before accepting final packaging. The summary must contain execution mode, serial reason when applicable, real evidence paths, scan commands/searches, candidate count, profile update evidence, and either submitted Bug IDs or a concrete zero-finding rationale. The candidates file must not still be the pending template.
- Confirm repo understanding evidence exists before accepting shard exploration: `surface_map` names concrete repo-local risk surfaces, `hypothesis_loops` trace at least one concrete failure hypothesis for non-trivial repos, and zero-finding non-trivial repos include a strongest refuted lead or refuted loop.
- Reject packages whose final Markdown, profiles, shard summaries, candidates, depth coverage, or lens coverage were created by a late package-writer script, loop, or inline heredoc batch. This remains a failure even when the script embeds real-looking evidence, because the workflow no longer proves repo-by-repo cognition. A single-file shell fallback for one named artifact is acceptable; a multi-artifact batch is not. Scripts may render indexes, HTML, images, or tables from already-filled shard summaries; they should not contain the final prose claims themselves.
- Confirm broad source scans used `work/scanner-output/repo-scan-roots.txt`. If `rg`/`grep` output includes previous `*bug-audit*/work` or `*bug-audit*/submit` content during source scanning, the fresh-rescan gate fails.
- Reject packages that generate final Bug records, README, HTML, overview image, or final knowledge before the shard evidence gate has passed. `work/scanner-output/shard-gate.passed.json` is the receipt; report assets are render layers over final evidence, not proof of exploration.
- Confirm every audited repo profile is represented in `depth-coverage.md`, not only repos with submitted Bugs.
- Confirm the package states its coverage classification: `first-pass`, `focused`, or `deep-complete`. A package based on pattern scans and sample reads across many repos is first-pass/focused unless each high-risk repo has real call-chain tracing from entry point to state owner, integration, execution boundary, or lifecycle transition.
- Confirm historical audit packages discovered under the target root were reviewed for contrast or explicitly excluded. A previous large package plus a new tiny package is a depth failure unless the scope says it is intentionally narrow and the baseline comparison explains the difference.
- Confirm fresh audits did not reuse prior package structure: new findings, IDs, profiles, indexes, and reports must come from the current source scan, not copied historical artifacts.
- Confirm zero-finding repos have a concrete rationale: scanned surfaces, parked candidates if any, and remaining gaps.
- Compare submitted issue families against the domain profile in `domain-profiles.md`.
- If one easy pattern dominates, sample the top records and confirm they affect distinct entry points, resources, or lifecycle phases.
- For infra repositories, check that data integrity, cross-system consistency, recovery, availability, resource leak, storage/network performance, deployment/runtime assumptions, observability, and security boundaries were all considered.
- For non-infra repositories, check that the product's core workflow, data safety, security boundary, recovery cost, and customer impact were considered.
- If a high-risk area has no findings, note whether it was reviewed, excluded, or left as unknown.
- Do not accept "deep analysis complete" wording unless `validate_bug_package.py` exits 0 with `--require-knowledge --require-html-report` and, for single-repo deep runs, `--require-depth-coverage`.

## Priority Calibration

Before packaging, re-read all P1/P2 records:

- P1 requires core interruption, major data/security/fund risk, tenant isolation risk, destructive state drift, or high recovery cost.
- P2 requires degraded core operation, serious stability risk, common operational failure, or cross-system state drift with recoverable blast radius.
- Do not raise priority based only on words like security, timeout, async, or OpenStack.
- Downgrade when the effect is narrow, display-only, guarded by existing framework behavior, or requires unlikely configuration.

## Skill Regression Gate

Use when editing this skill itself:

- Validate the portable eval suite:

```bash
python3 /Users/aiden/.agents/skills/skill-evaluator/scripts/check_eval_cases.py evals/core-regressions.json --strict-portable
```

- When a fresh-agent run is available, grade its transcript and audit workspace:

```bash
python3 scripts/grade_eval_trace.py evals/core-regressions.json --trace <fresh-agent-transcript.txt> --artifact-root <audit-workspace>
```

- Weak pattern lead should stay in `work/candidates/`.
- Duplicate same-entry/same-failure/same-impact records should merge.
- Resume run should keep existing IDs stable and record downgrade/removal reasons.
- P1/P2 inflation should be caught by priority calibration.
- Package handoff should include aligned README, indexes, knowledge, quality notes, and optional image.

Keep regression notes outside submitted audit outputs unless the user asks for them.

## Portable Eval Suite

The minimal suite lives at `evals/core-regressions.json`.

- `multi-repo-parent-20-roster-shards`: catches shallow parent-directory audits that skip repo roster/shard/depth gates.
- `late-package-writer-forbidden`: catches one-shot scripts that synthesize final Markdown instead of exploration evidence.
- `multi-repo-parent-20-roster-shards` also catches inline bulk writers and source scans that accidentally include historical audit output.
- `multi-repo-parent-20-roster-shards` fails when a fresh-agent trace shows `generate_bug_report_html.py` or overview generation after a failing `--validate-shards-only` run.
- `multi-repo-parent-20-roster-shards` also requires final handoff validation to use `--require-knowledge --require-html-report --repo-root`; a weaker validator invocation is not final-validation evidence.
- If the deterministic package validator passes but `grade_eval_trace.py` fails on `bulk_package_writer_absent`, the Skill eval fails. A polished package is not enough evidence that the workflow was followed.
- `html-default-image-optional`: catches missing default HTML, repeated image questions, or missing provenance.
- `single-repo-lightweight-scan`: catches over-scoping single-repo work into repo-group machinery and silent lens omission.
- `historical-package-fresh-rescan`: catches reuse of old audit packages when the user asked for a fresh scan.

These cases are not a replacement for `validate_bug_package.py`; they are forward-test and trace-replay checks for fresh-agent behavior. Add new cases only when they represent a real failure mode or a high-risk workflow branch.
