# Resume Audit

Use this when continuing, deepening, reviewing, downgrading, or repackaging an existing audit workspace.

## Start State

- Read `submit/indexes/findings.generated.json` first.
- If the index is missing or stale, run `scripts/generate_bug_index.py` before assigning new IDs.
- Find the largest existing `BUG-xxxx`; new Bugs continue from the next number.
- Do not renumber existing Bugs just to improve ordering.
- Read `submit/quality/submission-scope.md` for previous assumptions, exclusions, downgrade notes, and candidate handling.

## Updating Findings

- After adding, editing, moving, downgrading, or removing any Bug file, regenerate indexes.
- After regenerating indexes, run package validation.
- If a Bug is downgraded, moved to candidates, merged, or removed, record the reason in `submit/quality/submission-scope.md`.
- Record enough detail for the next Agent to understand the decision: date, Bug id, old state, new state, reason, and evidence checked.

Suggested note format:

```markdown
## 续跑记录

- `2026-05-06`：`BUG-0012` 从 `P1/high` 调整为 `P2/medium`。原因：入口存在统一重试包装，仍保留为部分失败后的状态漂移风险。
- `2026-05-06`：`BUG-0041` 合并入 `BUG-0037`。原因：同一入口、同一失败模式、同一影响范围。
- `2026-05-06`：`BUG-0056` 移至 `work/candidates/`。原因：缺少可确认的触发路径，需要运行时配置证明。
```

## Candidate Promotion

- Only promote `work/candidates/` leads after code evidence, trigger path, realistic failure mode, and impact are explicit.
- When promoted, create a formal Bug under `submit/findings/P*`.
- Keep the candidate note in `work/candidates/` with `升级结果：BUG-xxxx`, or move it under `work/candidates/upgraded/`.
- If promotion fails, update `未提交原因` and `升级所需证据` so the next pass does not restart from zero.

## Finish State

- `submit/indexes/findings.generated.md` and `submit/indexes/findings.generated.json` are current.
- README counts match the generated index.
- `submit/quality/submission-scope.md` records material changes.
- `work/` remains excluded from the final package.
