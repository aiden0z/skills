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
- **Never block any run on a missing analyst**: in interactive mode, ask only once at Phase 1 if the run already implies final handoff; in automatic mode, write `待补充` (Chinese) or `not specified` (English) and continue; in checkpointed/resume mode, reuse the value from `submit/quality/submission-scope.md` without re-asking.
- Keep README, `quality/submission-scope.md`, and `audit-overview.png` consistent. If the value is missing, either show the placeholder or omit `分析人` from the image when space is tight.

## Repository Version Evidence

Record repository version evidence in `quality/repository-versions.md` when available.

Suggested columns:

```markdown
| Repository | Role | Audit Branch | Commit | Dirty | Default Branch | Stable Candidate | Candidate Confidence | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| target-service | target | `main` | `abc1234` | `no` | `main` | `release/2.4.0` | `medium` | release branch naming + version sort | user confirmed `main` for audit |
| platform-ref | reference | `stable/zed` | `unknown` | `unknown` | `unknown` | `stable/zed` | `high` | user-provided branch | not a Git checkout |
```

Rules:

- Use `git rev-parse --abbrev-ref HEAD` for branch when available.
- Use `git rev-parse HEAD` for commit hash when available.
- Use `git status --short` to mark dirty state when available.
- Use existing local evidence first for default branch and stable candidates; do not fetch remote refs just for branch discovery unless the user approves or the task already requires fresh remote data.
- Use `git symbolic-ref refs/remotes/origin/HEAD` or equivalent local refs for default branch when available.
- Inspect local remote branches, tags, release notes, CI/CD config, deployment docs, and user-provided branch lists for stable candidates.
- Treat `stable/*`, `release/*`, `lts/*`, `support/*`, SemVer-like branches, protected release branches, and documented deployment branches as stronger stable-candidate evidence than raw commit recency.
- If a repo is not a Git checkout, record `unknown` and explain in Notes.
- Do not guess missing branch or commit information.
- Do not assume the highest-looking version is stable unless the naming, documentation, release metadata, or user input supports that meaning.
- Dirty worktree does not block analysis; it changes how reproducible the package is.
- For shallow clones, detached HEAD, or exported source trees, record the available evidence.

## Audit Branch Confirmation

Branch baseline changes the audit scope.

- If the user provided explicit branches, use them and record `Candidate Confidence` as `high` with `user-provided branch` in Evidence.
- If the user asks for the latest stable, release, production, or final handoff audit without naming branches, identify candidates and ask which baseline to use before scanning **(interactive/checkpointed only)**.
- If current checkout differs from the strongest stable candidate, ask before switching or before treating the candidate as the audit baseline **(interactive/checkpointed only)**.
- If the user asks for the current code, do not ask again; record current checkout as the audit baseline and stable candidate as reference evidence when available.
- **Automatic mode** never switches branches and never asks. When the user requested "latest stable" without naming a branch, audit the current checkout, treat the highest-confidence stable candidate as reference-only evidence, and record both the assumption and the unresolved baseline mismatch in `quality/submission-scope.md` under `分支基线偏离` so a human can re-run if needed.

Use a compact question:

```text
当前检出分支是 `<current>`，稳定候选是 `<candidate>`（置信度：<level>）。这次审计以当前分支为准，还是切到稳定候选分支后再审计？
```

If there are multiple repositories, ask with a short table and offer one decision for the whole group when possible.

## Stable Candidate Confidence

| Confidence | Evidence |
|---|---|
| `high` | User-provided branch; release/deployment docs name the branch; hosting metadata identifies a protected release branch; CI/CD deploy config maps to the branch. |
| `medium` | Branch name follows `stable/*`, `release/*`, `lts/*`, `support/*`, or SemVer-like naming and can be version-sorted from local refs. |
| `low` | Candidate is inferred from default branch, latest tag, or recent activity without release/deployment confirmation. |
| `unknown` | No reliable local or documented evidence. |

## Where Metadata Appears

- `submit/README.md`: concise analysis info and scope.
- `submit/quality/submission-scope.md`: assumptions, exclusions, confidence threshold, continuation notes.
- `submit/quality/repository-versions.md`: audit branch, commit, dirty status, default branch, stable candidate, confidence, evidence, and notes.
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
