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
entry_points:
  - ResourceService.delete_resource
files:
  - path: service/path/to/file.py
    lines: "120-168"
related_repos:
  - dependent-service
---
```

Do not include `sla`, `owner`, or `due_date` unless the user asks for workflow tracking.

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
10. `## 修复建议`
11. `## 验证标准`

For English deliverables, use equivalent headings: `Conclusion`, `Impact Scope`, `Preconditions`, `Static Reproduction Path`, `Actual Behavior`, `Expected Behavior`, `Code Evidence`, `False-positive Review`, `Fix Suggestion`, and `Validation Standard`.

## Writing Rules

- Use concrete repo/module names and exact entry points.
- Explain static reproduction as a code path, not a runtime claim.
- Keep fix suggestions actionable but not overly prescriptive.
- Avoid duplicate generic paragraphs across many Bugs; each record must explain its own module and failure path.
- Avoid “AI 分析”, “显然”, “可能存在大量问题” and other vague language.
- If a Bug is only pattern-level, reduce confidence or move it out of submitted findings.
