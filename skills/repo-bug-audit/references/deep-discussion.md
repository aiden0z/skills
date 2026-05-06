# Deep Discussion Mode

Use this mode when a Bug analysis task still needs design before execution. The goal is not to chat broadly; the goal is to produce a short analysis charter that lets the later scan run consistently.

## When to Enter

- The user explicitly mentions `$brainstorming`, “先讨论”, “先设计”, “深度思考”, or asks to refine the analysis method.
- The target spans many repositories and the output scope, confidence threshold, risk focus, or package format is unclear in a way that cannot be safely inferred.
- The user wants to change P1-P4 definitions, confidence rules, architecture-review style, security scope, image wording, README structure, or developer handoff format.
- The task is to design, improve, or review this `repo-bug-audit` skill itself.

## When to Skip

- The user asks for “全自动执行”, “不要频繁确认”, or clearly wants execution over discussion.
- The repositories, output root, report format, priority rules, and package audience are already clear.
- Missing details have safe defaults and do not change safety, target scope, or final package semantics.
- The task is a narrow continuation, such as regenerating indexes, compressing images, or validating an existing package.

## Output: Analysis Charter

Write a concise charter before scanning:

- **目标**: exploratory audit, audit output, architecture review, security pass, or fix-planning input.
- **范围**: target repos, reference repos, excluded paths, branches if known.
- **输出目录**: workspace root and final package location.
- **语言和口吻**: usually Chinese, developer-facing, no meta wording.
- **优先级规则**: P1-P4 definitions and whether infra-stability findings move earlier.
- **置信度规则**: submit only high/medium confidence, or keep low confidence in `work/candidates/`.
- **风险视角**: data integrity, recovery, availability, resource leak, storage/network performance, security, cross-system consistency, architecture risk.
- **证据要求**: entry point, code path, failure mode, impact, static reproduction path, expected/actual behavior, fix suggestion, validation checks.
- **交付物**: Bug Markdown files, indexes, knowledge docs, relationship maps, architecture review, README, audit overview image, zip package.
- **交互策略**: automatic execution or checkpointed review.

## Discussion Questions

Ask at most one substantial question at a time. Prefer a question only when the answer affects output quality or risk classification.

Do not ask about naming, cosmetic packaging, image style, or optional skill installation during automatic runs. Record assumptions in `submit/quality/submission-scope.md`.

Useful questions:

- “这次结果更偏提交给开发修复，还是先做内部风险摸底？”
- “低置信线索要放进候选区，还是这次只保留能提交的 Bug？”
- “是否把存储、网络、恢复能力这类私有云稳定性风险排在普通功能问题前面？”
- “最终需要 README、图片、关系图谱和 zip 包，还是只需要 Bug 列表？”

## When Updating This Skill

For skill design work, use this lighter process:

1. Define the behavior gap.
2. Compare two or three implementation options.
3. Choose the smallest change that keeps the skill reusable.
4. Update `SKILL.md` only for routing and core rules.
5. Put detailed procedures in `references/`.
6. Validate the skill folder after editing.

Do not add process history, meeting notes, or user-specific project details to the skill.

## Relation to `brainstorming`

If the `brainstorming` skill is available and the user explicitly mentions it, use it to shape the charter and tradeoffs. Keep the output lighter than a full product spec unless the user is designing a new tool or workflow from scratch.

If `brainstorming` would force unnecessary confirmation during an explicitly automatic run, do not stop execution; record reasonable assumptions in the package quality notes instead.
