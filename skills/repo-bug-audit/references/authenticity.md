# Authenticity First

This is the **rule that overrides every other rule in this skill**. Read it before writing any deliverable: Bug records, README, knowledge docs, repo profiles, architecture review, audit-overview image, submission scope.

## Core Principle

> **薄但真 ≫ 厚但假 (thin-but-true ≫ thick-but-false).**
>
> If meeting any quality / thickness / completeness requirement requires inventing content, **do not meet the requirement**. Lower the priority, move the lead to candidates, shorten the section, or mark it explicitly unconfirmed. Fabrication is the only failure mode that this skill never accepts — every other failure (missing section, low confidence, fewer findings, smaller scope) is recoverable.

This rule applies to **all output under `submit/`** — text, numbers, file references, bash commands, status claims, and image content.

## Scope

Anything written to `submit/` falls under this rule:

- Bug records (`findings/P*/...md`)
- `README.md`, `indexes/`, `knowledge/*`, `knowledge/repo-profiles/*`, `knowledge/architecture-design-review.md`
- `quality/submission-scope.md`, `quality/repository-versions.md`
- `audit-overview.png` (every number, label, and category name)
- Any future deliverable (per-repo profile, interactive HTML viewer, etc.)

`work/` artifacts are exempt — they are scratch space.

## Four Categories of Fabrication (Hard Reject)

If any of these appear in `submit/`, the deliverable fails. No softening, no warning.

1. **Non-existent code references** — a Bug, knowledge file, or image cites `path/to/file.py:120` but that file or that line does not exist; or names a function / class / field / endpoint / config key that the repo does not contain.
2. **Non-existent commands or test targets** — a Bug recommends `npm run test:storage` but `package.json` has no such script; or `make integration` when no such Makefile target exists; or a test file path that is not in the repo.
3. **Invented metrics or status** — README / overview image / scope claims `已复核 P1/P2 共 12 项`, `coverage 78%`, `已确认无误` when no verification step actually ran; or version evidence that contradicts the actual git state.
4. **Cross-document literal repetition** — the same ≥60-character paragraph appears in `复现路径`, `修复建议`, or `代码证据` of two or more Bugs (template padding); or the same `修复边界` clause is reused across unrelated Bugs.

A Bug record is a unit. If even one of its substantive claims is fabricated, the entire record is rejected, not just edited.

## Honest-Uncertainty Markers (Always Acceptable)

These are explicit signals that the writer chose truth over thickness. They are **never penalized** by validator or evaluator, and a Bug containing them is allowed to pass the substance bar:

- `静态分析无法判断` — the conclusion needs runtime / ownership / production data to verify
- `证据不足：<具体不足之处>` — e.g. `证据不足：未在仓库中找到 retry 配置文件`
- `未确认：<待补的具体项>` — e.g. `未确认：候选修改点 A 与 B 二选一，需 owner 评估`
- `静态分析未覆盖此路径` — for areas explicitly skipped, with reason

Empty strings, `TBD`, `TODO`, `xxx`, `to be filled` are **not** honest-uncertainty markers — they are unfinished work and must be removed before submission.

## Per-Output Rules

### Bug Records

- Every step of `静态复现路径` must reference a real `path:line` or named symbol. Cannot reach 3 steps with real evidence → write 2 steps + `证据不足：<...>`, do not invent a third.
- `代码证据` invariant statements must be derivable from the quoted code block. Cannot derive → quote less code, not more, and write a smaller invariant.
- `修复边界` out-of-scope items must reference real adjacent code (`UserDAO.delete 不需要改：独立事务边界 [src/dao/user.py:88]`). Cannot identify out-of-scope → write `out-of-scope 暂未确认` rather than enumerating speculative "safe" files.
- `修复建议 / 最小修复` must name a real target (function / field / contract). Cannot name a target → mark `未确认：修复对象需 owner 评估`.
- `建议验证命令` follows the existing rule: each command must trace to `package.json` / `Makefile` / CI config / `pyproject.toml` etc., or be replaced by `未确认：仓库中未找到可直接对应该模块的测试命令。`

### README and Knowledge Docs

- All counts must equal `indexes/findings.generated.json`. No rounding, no estimates.
- Do not write fix-status verbs (`已修复 / 已确认 / 已验证 / 已复核`). The audit produces findings, not fix evidence.
- `knowledge/system-overview.md` claims about service relationships need ≥1 supporting code reference (entry point, RPC call site, message handler).
- `knowledge/repo-profiles/<repo>.md` tech stack / framework / build tool must be read from real `package.json` / `pyproject.toml` / `pom.xml` / `Cargo.toml` / `go.mod`. Do not infer from filenames.
- `knowledge/architecture-design-review.md` each architecture risk needs ≥1 Bug ID or ≥1 code reference as anchor. Pure abstract claims without anchor → drop the claim.

### audit-overview.png

- Every number must trace to `indexes/findings.generated.json`, README, or `quality/repository-versions.md`. No "看起来差不多 5 个" estimates.
- Module names, repo names, category labels must match exactly the values used in indexes — same case, same wording.
- Version evidence summary in the image must equal what is in `quality/repository-versions.md`. If the latter is incomplete, the image must say so, not paper over it.
- Quality Gate Q5 (see `audit-overview-image.md`): every concrete noun in the image must be findable in the repo or the package. One miss → regenerate.

### quality/submission-scope.md

- Every "downgraded / removed / merged" entry must cite the originating Bug ID and the concrete reason (which gate it failed).
- "P1/P2 confirmed" statements are not allowed. The audit confirms findings, not severity correctness in production.

## Evaluator Rubric — 30-Minute-Fix + Authenticity Veto

Used in `evaluation.md` Bug-Level Gate. Reviewer reads only the Bug Markdown (not the repo) and answers 5 questions:

1. **What to change** — can you name the file / function / call-site?
2. **How to change** — can you state the minimum fix direction (not full patch)?
3. **What can break** — can you state at least one compatibility / performance / cross-service risk?
4. **How to verify** — is there at least one regression path (command / test file / code location)?
5. **Authenticity veto** — does every concrete noun (function / file / line / call chain / command / metric) actually exist in the repo or package?

**Pass = 3-of-4 on Q1-Q4, AND Q5 fully clean.** Q5 is a single-veto question: any one fabricated noun → entire Bug fails, regardless of Q1-Q4 score.

Failure → apply one of the four documented actions (`lower confidence` / `move to candidates` / `merge` / `record uncertainty`), log in `submission-scope.md`. Never invent fixes mid-evaluation.

## Validator Enforcement

Levels:

- **ERROR (blocks delivery)** — verifiable fabrication signals:
  - `frontmatter.files[].path` references a path that does not exist in the repo (when `--repo-root` is provided)
  - bash command references an `npm` script, `make` target, `pyproject` script, or test file path that does not exist
  - identical ≥60-character paragraph appears in `静态复现路径` / `修复建议` / `代码证据` of two or more Bugs

- **WARN (visible signal, does not block)** — heuristic anti-fabrication signals:
  - extended banned phrases hit (e.g. `推测此处会`, `理论上可能`, `代码中应有 X 校验`)
  - `修复建议 / 最小修复` paragraph missing the three components (modify-target keyword + concrete noun + risk statement)
  - sections fall under the per-section thickness minimum but no honest-uncertainty marker is present

Evaluator (human or AI sub-agent) is responsible for everything the validator cannot mechanically check — primarily Q5 veto on body-text path:line references and invariant claims.

## Anti-Patterns Explicitly Banned by This Rule

- Reaching the "≥3 reproduction steps" bar by adding a vague step ("最终触发异常路径")
- Adding "long-term hardening" content that recommends generic patterns the codebase doesn't actually use
- Writing `已对 P1/P2 全量复核` in `submission-scope.md` without a real review pass
- Putting a fake commit hash in `quality/repository-versions.md` to satisfy version-evidence requirements
- Referencing `humanizer-zh` / `acquire-codebase-knowledge` outputs that were never generated
- "Repo profile" written from filenames instead of build metadata
- Architecture-review bullet points that read as principles ("应保证 X / 推荐使用 Y") rather than discoveries

## When in Doubt

Ask: *"If a reviewer opened this exact file in the repo right now, would they confirm the claim?"*

- Yes → keep.
- No, but I have evidence → strengthen the citation.
- No, and I do not have evidence → write the honest-uncertainty marker, or remove the claim.
- I am not sure → treat as "no evidence". Do not let "probably correct" leak into `submit/`.
