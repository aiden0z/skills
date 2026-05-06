# Evaluation

Use this after findings are written and before final packaging. Evaluation checks whether records are real, useful, prioritized correctly, and consistent as a package.

Evaluation does not replace `validate_bug_package.py`. The script checks structure; this file checks judgment.

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

If any item is weak:

- Lower confidence, or
- Move the lead to `work/candidates/`, or
- Merge it into a stronger Bug, or
- Record the uncertainty in the Bug and `quality/submission-scope.md`.

## Package-Level Gate

Check the package as a single artifact:

- README counts match `indexes/findings.generated.json`.
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

- Compare submitted issue families against the domain profile in `domain-profiles.md`.
- If one easy pattern dominates, sample the top records and confirm they affect distinct entry points, resources, or lifecycle phases.
- For infra repositories, check that data integrity, recovery, availability, resource leak, storage/network performance, and security boundaries were all considered.
- For non-infra repositories, check that the product's core workflow, data safety, security boundary, recovery cost, and customer impact were considered.
- If a high-risk area has no findings, note whether it was reviewed, excluded, or left as unknown.

## Priority Calibration

Before packaging, re-read all P1/P2 records:

- P1 requires core interruption, major data/security/fund risk, tenant isolation risk, destructive state drift, or high recovery cost.
- P2 requires degraded core operation, serious stability risk, common operational failure, or cross-system state drift with recoverable blast radius.
- Do not raise priority based only on words like security, timeout, async, or OpenStack.
- Downgrade when the effect is narrow, display-only, guarded by existing framework behavior, or requires unlikely configuration.

## Skill Regression Gate

Use when editing this skill itself:

- Weak pattern lead should stay in `work/candidates/`.
- Duplicate same-entry/same-failure/same-impact records should merge.
- Resume run should keep existing IDs stable and record downgrade/removal reasons.
- P1/P2 inflation should be caught by priority calibration.
- Package handoff should include aligned README, indexes, knowledge, quality notes, and optional image.

Keep regression notes outside submitted audit outputs unless the user asks for them.
