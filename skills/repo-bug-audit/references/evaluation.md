# Evaluation

Use this after findings are written and before final packaging. Evaluation checks whether records are real, useful, prioritized correctly, and consistent as a package.

Evaluation does not replace `validate_bug_package.py`. The script checks structure; this file checks judgment.

> **Authenticity First** (`references/authenticity.md`) is the rule that overrides every gate below. A Bug that fabricates content fails immediately, regardless of which other checks it would have passed.

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

## Package-Level Gate

Check the package as a single artifact:

- README counts match `indexes/findings.generated.json` exactly. No rounding, no estimates.
- Knowledge claims in `system-overview.md`, `repo-relationship-map.md`, `risk-paths.md` each have ≥1 supporting code reference or Bug ID anchor (Q5 veto applies to knowledge files too).
- `repo-profiles/<repo>.md` tech stack is read from real `package.json` / `pyproject.toml` / `pom.xml` / `Cargo.toml` / `go.mod`, not inferred from filenames.
- `architecture-design-review.md` each risk bullet has ≥1 Bug ID or ≥1 code reference; pure abstract claims are removed.
- `submission-scope.md` "downgraded / removed / merged" entries cite originating Bug ID and concrete failed gate; no `已确认无误 / 已复核全部` claims.
- P1/P2 summaries align with actual Bug metadata and issue families.
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
