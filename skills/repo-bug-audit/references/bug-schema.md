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

> **Read `authenticity.md` first.** The thickness rules below are **conditional on real evidence** — never invent steps, code refs, or fix targets to satisfy them. Use the honest-uncertainty markers (`证据不足：…`, `静态分析无法判断`, `未确认：…`) when evidence runs out.

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

## Section Substance Bar

For the four sections below, the agent must hit a minimum substance level OR write an honest-uncertainty marker (see `authenticity.md`). Never invent content to clear the bar.

### 静态复现路径

- ≥3 ordered steps; each step has `path:line` or a named symbol; steps are connected with prose ("接着 / 然后 / 此时"), not a bare list.
- If real evidence does not support 3 steps: write the steps you have + `证据不足：<具体未覆盖的下游路径>`. A 2-step path with an honest marker is acceptable; a 3-step path with a fabricated step is not.

### 代码证据

- ≥1 code reference block (`path:line` quote, reasonably scoped, do not paste whole files) + ≥1 invariant statement directly tied to the quote ("应保证 / 期望" sentence).
- The invariant must be derivable from the quoted code. If you cannot derive it, quote less code, write a smaller invariant, or move the Bug to candidates.

### 修复边界

- ≥1 primary modification target (file / function / contract) and ≥1 explicit out-of-scope item (`X 不需要改：<具体理由>`).
- The out-of-scope item is the key signal: it forces the writer to think about blast radius. If you cannot justify any out-of-scope item from real adjacent code, write `out-of-scope 暂未确认：<具体不足之处>` rather than enumerating speculative "safe" files.

### 修复建议

- Two paragraphs:
  - **最小修复** — must contain (a) a modification verb (修改 / 调整 / 替换 / 引入 / 移除), (b) a concrete noun (function / field / module name, not "这个方法"), and (c) a risk note (兼容性 / 性能 / 跨服务影响).
  - **长期加固** — one structural recommendation, or write `无` if nothing structural is warranted. Do not invent generic patterns the codebase does not use.
- If you cannot name a real modification target, write `未确认：修复对象需 owner 评估` and stop. Do not pad with generic advice ("建议添加 try/catch / 加强校验").

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

- **Authenticity First** (`authenticity.md`) overrides every rule below. If a rule cannot be met with real evidence, use an honest-uncertainty marker rather than fabricating.
- Use concrete repo/module names and exact entry points.
- Explain static reproduction as a code path, not a runtime claim.
- Keep fix suggestions actionable but not overly prescriptive.
- Make fix boundaries explicit enough for another Agent to avoid unrelated edits.
- Suggested verification commands must be evidence-backed; otherwise mark them unconfirmed.
- Avoid duplicate generic paragraphs across many Bugs; each record must explain its own module and failure path.
- Avoid “AI 分析”, “显然”, “可能存在大量问题” and other vague language.
- If a Bug is only pattern-level, reduce confidence or move it out of submitted findings.
