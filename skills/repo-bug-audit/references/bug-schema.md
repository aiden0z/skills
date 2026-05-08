# Bug Record Schema

Use one Markdown file per Bug. Store structured metadata in the Markdown file itself.

## Contents

- Filename
- Metadata Block
- Required Sections
- Section Substance Bar
- Fix-Ready Sections
- Writing Rules

## Filename

`P<priority>-BUG-<id>-<short-kebab-description>.md`

Examples:

- `P1-BUG-0001-volume-delete-removes-local-record-before-backend-confirm.md`
- `P2-BUG-0042-http-client-has-no-timeout.md`

## Metadata Block

Use a YAML-compatible frontmatter block at the top. Do not create separate YAML files.

```markdown
---
id: BUG-0001
priority: P1
confidence: high
status: open
source: static-analysis
repo: target-service
module: storage
category: data-integrity
issue_family: cross-system-state-mutation
infra_domains: [control-plane, data-integrity, recovery]
fix_risk: medium
entry_points:
  - ResourceService.delete_resource
files:
  - path: service/path/to/file.ext
    lines: "120-168"
related_repos:
  - dependent-service
lens:
  - L8
  - L17
---
```

`lens` is an optional list tagging which exploration lens surfaced the Bug. Allowed values are `L1`-`L19`, `META-1`, and `META-2`. Use the lens that best matches the primary phenomenon; if multiple apply, list them in priority order.

Do not include `sla`, `owner`, or `due_date` unless the user asks for workflow tracking.

`fix_risk` describes the expected risk of changing the affected code path, not Bug impact:

- `low`: localized change, clear owner, limited blast radius
- `medium`: shared code, async state, compatibility, or multiple call paths
- `high`: cross-repo contracts, data migration, storage/network/control-plane lifecycle, or security boundaries
- `unknown`: evidence is enough to submit the Bug, but fix impact needs runtime or ownership context

## Required Sections

Read `authenticity.md` first. Substance requirements are conditional on real evidence; never invent steps, code refs, or fix targets to satisfy them.

Chinese is the default final-deliverable language for Chinese users. Use these headings unless the user requests English:

1. `# <priority> <short title>`
2. `## 结论`
3. `## 影响范围`
4. `## 前置条件`
5. `## 静态复现路径`
6. `## 实际表现`
7. `## 期望表现`
8. `## 代码证据`
9. `## 误报排查`
10. `## 修复边界`
11. `## 修复建议`
12. `## 建议验证命令`
13. `## 验证标准`

For English deliverables, use:

1. `# <priority> <short title>`
2. `## Conclusion`
3. `## Impact Scope`
4. `## Preconditions`
5. `## Static Reproduction Path`
6. `## Actual Behavior`
7. `## Expected Behavior`
8. `## Code Evidence`
9. `## False-positive Review`
10. `## Fix Boundary`
11. `## Fix Suggestion`
12. `## Suggested Verification Commands`
13. `## Validation Standard`

## Section Substance Bar

For the four sections below, hit the minimum substance level or write an honest-uncertainty marker from `authenticity.md`.

### Static Reproduction Path

- At least three ordered steps when evidence supports them.
- Each step has a real `path:line`, named symbol, route, job, command, or call site.
- If evidence supports fewer steps, write the real steps and add a specific uncertainty marker. A thin true path is better than a padded false path.

### Code Evidence

- Include at least one scoped code reference block or quoted excerpt.
- Add at least one invariant statement directly tied to the quote: what the code should preserve, release, validate, retry, order, or reject.
- The invariant must be derivable from the quoted code. If not, narrow the claim or move the lead to candidates.

### Fix Boundary

- Name the primary modification target: file, function, module, schema, config, or contract.
- Name at least one out-of-scope item when evidence supports it.
- If no out-of-scope boundary can be proven, write a precise unconfirmed marker instead of inventing safe files.

### Fix Suggestion

Use two short paragraphs or bullets:

- **Minimum safe fix**: modification verb + concrete target + risk note.
- **Longer-term hardening**: optional structural improvement, or `none` / `无` if no structural hardening is warranted.

If no real modification target can be named, write an unconfirmed marker and stop. Do not pad with generic advice.

## Fix-Ready Sections

Use these sections to help a later agent or developer repair the Bug without expanding scope.

### Fix Boundary

State the safest change boundary:

- Primary files, functions, services, or contracts likely involved
- Files or modules that should not change unless new evidence requires it
- Cross-repo or external contract impact, if visible
- Data migration, compatibility, rollout, or recovery concerns, if visible

Do not invent ownership, runtime behavior, or deployment constraints. If the boundary is unclear, say what is known and what remains unknown.

### Fix Suggestion

Separate:

- Minimum safe fix: the smallest change that should remove the failure mode
- Longer-term hardening: adapter isolation, reconciliation, idempotency, retry budget, contract clarification, or similar codebase-aligned follow-up

Keep suggestions actionable but not overly prescriptive. Do not write the full patch unless the user asks for fixes.

### Suggested Verification Commands

List only commands traceable to repository files such as `package.json`, `pyproject.toml`, `tox.ini`, `pom.xml`, `build.gradle`, `go.mod`, `Cargo.toml`, `.csproj`, `Makefile`, CI config, test files, or existing scripts. Use `language-ecosystems.md` to identify credible command sources.

If no trustworthy command is found, write one of:

- `unconfirmed: no repository command was found that directly covers this module`
- `未确认：仓库中未找到可直接对应该模块的测试命令。`

When a command is suggested, explain why it is relevant:

```markdown
- `npm run test -- --run resource-delete.spec.ts`: `package.json` defines `test`; the named spec covers state display after resource-delete failure.
- `make test-storage`: `Makefile` defines this target; it is the closest storage-module regression command.
```

Never fabricate test file names, package scripts, or CI jobs.

## Writing Rules

- Authenticity First overrides every rule below.
- Use concrete repo/module names and exact entry points.
- Explain static reproduction as a code path, not a runtime claim.
- Keep fix suggestions actionable but not overly prescriptive.
- Make fix boundaries explicit enough for another agent to avoid unrelated edits.
- Suggested verification commands must be evidence-backed; otherwise mark them unconfirmed.
- Avoid duplicate generic paragraphs across Bugs; each record must explain its own module and failure path.
- Avoid "AI analysis", "obvious", "many possible issues", and localized equivalents.
- If a Bug is only pattern-level, reduce confidence or move it out of submitted findings.
