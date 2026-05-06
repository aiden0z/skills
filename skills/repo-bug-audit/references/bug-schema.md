# Bug Record Schema

Use one Markdown file per Bug. Store structured metadata in the Markdown file itself.

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
---
```

Do not include `sla`, `owner`, or `due_date` unless the user asks for workflow tracking.

`fix_risk` describes the expected risk of changing the affected code path, not the Bug impact:

- `low`: localized change, clear owner, limited blast radius.
- `medium`: affects shared code, async state, compatibility, or multiple call paths.
- `high`: affects cross-repo contracts, data migration, storage/network/control-plane lifecycle, or security boundaries.
- `unknown`: evidence is enough to submit the Bug, but fix impact cannot be assessed without runtime or ownership context.

## Required Sections

Use Chinese headings by default:

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

For English deliverables, use equivalent headings: `Conclusion`, `Impact Scope`, `Preconditions`, `Static Reproduction Path`, `Actual Behavior`, `Expected Behavior`, `Code Evidence`, `False-positive Review`, `Fix Boundary`, `Fix Suggestion`, `Suggested Verification Commands`, and `Validation Standard`.

## Fix-Ready Sections

Use these sections to help a later Agent or developer repair the Bug without expanding scope.

### 修复边界

State the safest change boundary:

- Primary files, functions, services, or contracts likely involved.
- Files or modules that should not be changed unless new evidence requires it.
- Cross-repo or external contract impact, if any.
- Data migration, compatibility, rollout, or recovery concerns, if visible from code.

Do not invent ownership, runtime behavior, or deployment constraints. If the boundary is not clear, say what is known and what remains unknown.

### 修复建议

Separate:

- Minimum safe fix: the smallest change that should remove the failure mode.
- Longer-term hardening: optional structural cleanup, adapter isolation, reconciliation, idempotency, retry budget, or contract clarification.

Keep suggestions actionable but not overly prescriptive. Do not rewrite the full patch unless the user asks for fixes.

### 建议验证命令

List only commands that are traceable to repository files such as `package.json`, `pyproject.toml`, `tox.ini`, `pom.xml`, `build.gradle`, `go.mod`, `Cargo.toml`, `.csproj`, `Makefile`, CI config, test files, or existing scripts. Use `language-ecosystems.md` to identify credible command sources.

If no trustworthy command is found, write:

- `未确认：仓库中未找到可直接对应该模块的测试命令。`

When a command is suggested, include why it is relevant:

```markdown
- `npm run test -- --run resource-delete.spec.ts`：`package.json` 中存在 `test` 脚本，覆盖资源删除失败后的状态展示。
- `make test-storage`：`Makefile` 中存在该目标，可作为存储模块回归检查。
```

Never fabricate test file names, package scripts, or CI jobs.

## Writing Rules

- Use concrete repo/module names and exact entry points.
- Explain static reproduction as a code path, not a runtime claim.
- Keep fix suggestions actionable but not overly prescriptive.
- Make fix boundaries explicit enough for another Agent to avoid unrelated edits.
- Suggested verification commands must be evidence-backed; otherwise mark them unconfirmed.
- Avoid duplicate generic paragraphs across many Bugs; each record must explain its own module and failure path.
- Avoid “AI 分析”, “显然”, “可能存在大量问题” and other vague language.
- If a Bug is only pattern-level, reduce confidence or move it out of submitted findings.
