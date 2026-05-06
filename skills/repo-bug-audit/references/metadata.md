# Metadata

Use this when setting scope, writing README, recording repository versions, or building `audit-overview.png`.

## Required Audit Metadata

Record in README and `quality/submission-scope.md`:

- Analysis date.
- Analyst only when provided; otherwise mark it missing and do not guess.
- Scope.
- Method: `static-analysis`.
- Status: `open` findings, pending runtime/developer review.
- Language.
- Domain profile.
- Reference repositories when used.

## Analyst Field

Use the analyst field as package metadata, not as inferred identity.

- Valid sources: explicit user input, existing audit package metadata, or the `--analyst` argument in `scripts/init_bug_workspace.py`.
- Do not infer it from OS username, Git user/email, directory owner, hostname, model name, or tool account.
- In skill instructions, templates, and examples, use neutral placeholders such as `<analyst>` instead of real personal identifiers.
- In automatic runs, do not pause only for a missing analyst. Write `待补充` in Chinese packages or `not specified` in English packages.
- In checkpointed final handoff, ask once only if the organization or user expects a named analyst on README or image.
- Keep README, `quality/submission-scope.md`, and `audit-overview.png` consistent. If the value is missing, either show the placeholder or omit `分析人` from the image when space is tight.

## Repository Version Evidence

Record repository version evidence in `quality/repository-versions.md` when available.

Suggested columns:

```markdown
| Repository | Role | Branch | Commit | Dirty | Notes |
|---|---|---|---|---|---|
| target-service | target | `main` | `abc1234` | `no` |  |
| platform-ref | reference | `stable/zed` | `unknown` | `unknown` | not a Git checkout |
```

Rules:

- Use `git rev-parse --abbrev-ref HEAD` for branch when available.
- Use `git rev-parse HEAD` for commit hash when available.
- Use `git status --short` to mark dirty state when available.
- If a repo is not a Git checkout, record `unknown` and explain in Notes.
- Do not guess missing branch or commit information.
- Dirty worktree does not block analysis; it changes how reproducible the package is.
- For shallow clones, detached HEAD, or exported source trees, record the available evidence.

## Where Metadata Appears

- `submit/README.md`: concise analysis info and scope.
- `submit/quality/submission-scope.md`: assumptions, exclusions, confidence threshold, continuation notes.
- `submit/quality/repository-versions.md`: branch, commit, dirty status, and notes.
- `submit/knowledge/system-overview.md`: scope and reference repositories when relevant.
- `submit/audit-overview.png`: compact footer or side rail with date, analyst when provided, source, scope, and version-evidence summary.

## Audit Overview Image Metadata

Use compact labels:

- `时间`
- `分析人` when provided; otherwise use `待补充` or omit from the image if space is limited
- `范围`
- `方法`
- `版本凭证`

For version evidence, show a summary rather than a long table:

- `版本凭证：6/6 仓库已记录 branch/hash`
- `版本凭证：4/6 已记录，2 个仓库缺少 Git 信息`
- `版本凭证：未采集`

Keep full details in `quality/repository-versions.md`.
