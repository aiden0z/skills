# Authenticity First

This rule overrides every other rule in this skill. Read it before writing any deliverable: Bug records, README, knowledge docs, repo profiles, architecture review, audit-overview image, or submission scope.

## Contents

- Core Principle
- Scope
- Hard-Reject Fabrication
- Honest-Uncertainty Markers
- Per-Output Rules
- Evaluator Rubric
- Validator Enforcement
- Anti-Patterns
- When in Doubt

## Core Principle

> Thin-but-true beats thick-but-false.
>
> If a quality, depth, or completeness requirement would require invented content, do not satisfy that requirement. Lower confidence, move the lead to candidates, shorten the section, or mark the missing evidence explicitly. Fabrication is the only unrecoverable failure mode in this skill.

This rule applies to every output under `submit/`: text, numbers, file references, commands, status claims, and image content.

## Scope

Anything written to `submit/` falls under this rule:

- Bug records (`findings/P*/...md`)
- `README.md`, `indexes/`, `knowledge/*`, `knowledge/repo-profiles/*`, `knowledge/architecture-design-review.md`
- `quality/submission-scope.md`, `quality/repository-versions.md`, `quality/lens-coverage.md`
- `audit-overview.png` and any HTML used to generate it
- Any future final deliverable

`work/` artifacts are scratch space. They may be incomplete, but they must not be copied into `submit/` without evidence review.

## Hard-Reject Fabrication

If any of these appear in `submit/`, the package fails:

1. **Non-existent code references**: a path, line, function, class, endpoint, field, config key, or command target is cited but does not exist.
2. **Non-existent verification commands**: a Bug recommends an npm script, Make target, test file, CI job, or package command not present in the repo.
3. **Invented metrics or status**: README, image, or scope text claims review counts, coverage percentages, "confirmed", "verified", or version evidence that did not happen.
4. **Template padding**: the same long paragraph is reused across unrelated Bugs, especially in reproduction path, code evidence, fix boundary, or fix suggestion.

A Bug record is a unit. If one substantive claim is fabricated, reject or rewrite the whole record instead of trimming only the bad sentence.

## Honest-Uncertainty Markers

Use explicit uncertainty markers when evidence runs out. These are allowed to pass the substance bar because they protect truthfulness.

English deliverables:

- `static analysis cannot confirm`
- `insufficient evidence: <specific missing evidence>`
- `unconfirmed: <specific unknown>`
- `static analysis did not cover this path`

Chinese deliverables:

- `静态分析无法判断`
- `证据不足：<具体不足之处>`
- `未确认：<待补的具体项>`
- `静态分析未覆盖此路径`

Empty strings, `TBD`, `TODO`, `xxx`, and `to be filled` are not honest-uncertainty markers. They are unfinished work.

## Per-Output Rules

### Bug Records

- Every static reproduction step must reference a real `path:line` or named symbol. If real evidence supports only two steps, write two steps plus an honest-uncertainty marker.
- Code-evidence invariants must be derivable from the quoted code. If not, quote less code, narrow the invariant, or move the lead to candidates.
- Fix-boundary out-of-scope claims must reference real adjacent code or a real contract. If no boundary can be proven, mark it unconfirmed.
- Fix suggestions must name a real target: function, field, module, schema, config, or contract. If the target is unclear, mark it unconfirmed and stop.
- Suggested verification commands must trace to repository files such as `package.json`, `Makefile`, CI config, `pyproject.toml`, test files, or existing scripts.

### README and Knowledge Docs

- Counts must match `indexes/findings.generated.json`. Do not estimate.
- Do not use fix-status verbs such as "fixed", "confirmed", "verified", or localized equivalents unless runtime proof exists.
- `knowledge/system-overview.md` service-relationship claims need at least one supporting code reference.
- `knowledge/repo-profiles/<repo>.md` tech stack and build facts must come from real build metadata, not filename guesses.
- `knowledge/architecture-design-review.md` architecture risks need at least one Bug ID or code reference as an anchor.

### Lens Coverage

- `quality/lens-coverage.md` may record zero candidates. It still needs real scanned entry points, patterns, and uncovered areas.
- A lens record must not imply that the whole repo was covered unless the scan actually touched the whole repo.
- Combined cross-repo boundary / META records for large multi-repo audits must state which repos were covered and which were not.

### audit-overview.png

- Every number must trace to generated indexes, README, or repository-version evidence.
- Module names, repo names, and category labels must match package values exactly.
- Version evidence in the image must match `quality/repository-versions.md`.
- Every concrete noun in the image must be findable in the repo or final package.

### quality/submission-scope.md

- Every downgrade, removal, merge, or candidate-promotion entry must cite the Bug ID or candidate and the concrete gate that changed it.
- Do not write "P1/P2 confirmed" unless an actual review pass occurred. Static audit confirms evidence, not production severity.

## Evaluator Rubric

The Bug-level review uses a 30-minute-fix test plus an authenticity veto. A reviewer should be able to answer from the Bug Markdown:

1. What file, function, call site, schema, or contract should change?
2. What is the minimum fix direction?
3. What compatibility, performance, data, or cross-service risk could break?
4. What command, test path, or code path can verify the fix?
5. Does every concrete noun actually exist in the repo or package?

Pass = at least three of Q1-Q4 plus a clean Q5. Q5 is a veto: one fabricated noun fails the Bug regardless of the other answers.

Failure actions: lower confidence, move to candidates, merge with another Bug, or record a precise uncertainty marker. Never invent fixes during evaluation.

## Validator Enforcement

The validator can block only mechanically verifiable signals:

- `frontmatter.files[].path` references a missing repo path when `--repo-root` is provided
- suggested commands reference missing scripts, Make targets, package scripts, or test paths
- long duplicate paragraphs appear across submitted Bug records
- required package files or lens-coverage records are missing

The evaluator is responsible for body-text authenticity, invariant quality, false-positive review, and severity calibration.

## Anti-Patterns

- Adding a vague reproduction step only to reach a section-length bar
- Recommending generic hardening patterns that the codebase does not use
- Claiming full P1/P2 review without a real review pass
- Inventing commit hashes, branch names, coverage numbers, or package metrics
- Citing companion-skill outputs that were never generated
- Writing repo profiles from filenames instead of build metadata
- Writing architecture review as abstract principles rather than discovered risk signals

## When in Doubt

Ask: if a reviewer opened the exact repo file now, would they confirm this claim?

- Yes: keep it.
- No, but evidence exists: strengthen the citation.
- No evidence: mark uncertainty or remove the claim.
- Unsure: treat it as no evidence.
