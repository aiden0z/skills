# Resume Audit

Use this when continuing, deepening, reviewing, downgrading, or repackaging an existing audit workspace.

## Contents

- Bug ID Strategy — When Each Rule Applies
- Start State
- Updating Findings
- Candidate Promotion
- Parallel Multi-Agent Consolidation
- Finish State

## Bug ID Strategy — When Each Rule Applies

Two rules look like they conflict. They don't — they apply to different scenarios. Use this decision tree before assigning or renumbering any ID:

```
Are you producing the FINAL submitted package right now?
├── No (still scanning, still writing Bugs, mid-resume)
│   └── Rule: KEEP existing IDs stable. Continue from max(BUG-xxxx) + 1.
│       Gaps from removed/merged Bugs are OK during this phase.
│       Run validator with --allow-id-gaps if needed.
│
└── Yes (about to zip, deliver, or hand off)
    │
    ├── Single-agent or sequential resume → IDs already stable & dense from
    │   incremental work. Verify contiguous; no renumber needed.
    │
    └── Parallel multi-agent merge (two+ agents wrote BUG-* independently)
        └── Rule: RENUMBER all Bugs to a single contiguous BUG-0001..N
            sequence per "Parallel Multi-Agent Consolidation" below.
            Update filenames, frontmatter IDs, indexes, and any
            cross-Bug references. Validator must pass WITHOUT --allow-id-gaps.
```

Short version: **stable during work, contiguous on delivery**. The "do not renumber" rule prevents churn during incremental work; the "must be contiguous" rule prevents segmented IDs in the final artifact.

## Start State

- Read `submit/indexes/findings.generated.json` first.
- If the index is missing or stale, run `scripts/generate_bug_index.py` before assigning new IDs.
- Find the largest existing `BUG-xxxx`; new Bugs continue from the next number.
- Do not renumber existing Bugs just to improve ordering. (Final-delivery renumber is a separate step — see decision tree above.)
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

## Parallel Multi-Agent Consolidation

Use this when multiple agents (sub-agents, parallel workers, separate sessions on the same repo group) produced Bug records independently and you are merging them into one final package.

### Hard Rule

The final submitted package MUST contain a single contiguous `BUG-0001..BUG-N` sequence — no gaps, no segmented per-agent ranges, no reserved blocks. `scripts/validate_bug_package.py` rejects gaps unless `--allow-id-gaps` is set, and that flag is reserved for active resume runs only, never for final delivery.

Anti-patterns to reject:

- ❌ Agent A submits `BUG-0001..0008`, agent B submits `BUG-0100..0107` — gap of 92.
- ❌ Each agent reserves a 100-ID block (`0001-0099`, `0100-0199`, …) "for safety" and leaves most slots empty.
- ❌ Renumbering only the final indexes/README while leaving filenames and frontmatter on the segmented IDs.
- ❌ Hiding gaps by adding placeholder Bug files.

### Sub-Agent Coordination (during analysis)

To avoid ID conflicts during parallel work, do one of:

1. **Sharded ranges + final renumber (recommended for true parallelism)** — give each agent a temporary range (e.g. agent A `BUG-1001..`, agent B `BUG-2001..`, agent C `BUG-3001..`). These are temporary IDs only. At consolidation, renumber the entire merged set to `BUG-0001..BUG-N`.
2. **Serial ID allocator** — each agent calls `scripts/generate_bug_index.py` to learn the current max and claims the next slot atomically. Works only when agents share the same workspace and run sequentially enough for the allocator to be authoritative.
3. **Per-priority reservation** — not allowed; merges still must produce a single contiguous range across all priorities.

### Consolidation Procedure

1. Collect all Bug files from every agent into one `findings/P*/` tree.
2. Resolve duplicates per `deduplication.md` first — do not renumber before dedup, or you will renumber Bugs you later remove.
3. Sort surviving Bugs deterministically: by `priority` (P1→P4), then by original `id` ascending, then by filename. Document any deviation in `submission-scope.md`.
4. Renumber sequentially `BUG-0001..BUG-N`. For each Bug:
   - Update the filename's `BUG-xxxx` segment.
   - Update the frontmatter `id:` field.
   - Update every cross-reference (`merged into BUG-xxxx`, `升级结果：BUG-xxxx`, `relates-to:`, knowledge docs, image text).
5. Regenerate indexes via `scripts/generate_bug_index.py`.
6. Run `scripts/validate_bug_package.py` — it will fail if the final IDs are not contiguous starting at `BUG-0001`.
7. Record the renumber operation in `submit/quality/submission-scope.md` with an old-id → new-id mapping table so reviewers can trace any external references that pointed at temporary IDs.

Suggested mapping note:

```markdown
## 并行合并重编号 (2026-05-07)

| 原始 ID (sub-agent) | 合并后 ID | 来源 |
| --- | --- | --- |
| BUG-1001 | BUG-0001 | agent-A: backend |
| BUG-1002 | BUG-0002 | agent-A: backend |
| BUG-2001 | BUG-0003 | agent-B: frontend |
| BUG-2002 | BUG-0004 | agent-B: frontend |
| BUG-3001 | BUG-0005 | agent-C: cli |
```

### When This Rule Does NOT Apply

- A single agent doing an incremental resume on the same workspace — preserve existing IDs and continue from `max+1`. This naturally produces a contiguous range.
- Active in-progress workspaces in `work/`. Continuity is enforced only at submission. During analysis, gaps from removed/merged candidates are acceptable until the next consolidation pass.

## Finish State

- `submit/indexes/findings.generated.md` and `submit/indexes/findings.generated.json` are current.
- README counts match the generated index.
- `submit/quality/submission-scope.md` records material changes.
- `work/` remains excluded from the final package.
