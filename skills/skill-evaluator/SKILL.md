---
name: skill-evaluator
description: Use when asked to review a skill's quality, test whether a skill works correctly, find why a skill behaves inconsistently or fails to trigger, check if a skill is ready to publish, harden a skill against known failure modes, or turn an observed failure into a repeatable test case.
---

# Skill Evaluator

IRON LAW: Evaluate a skill against real-use failure modes, not against how convincing its instructions sound.

## Purpose

Assess whether a skill is discoverable, concise, executable, verifiable, and robust under realistic agent behavior. Turn observed failures into concrete workflow gates, scripts, references, or eval cases.

## Operating Rules

- Treat a skill as a reusable capability module, not a long prompt.
- Prefer raw evidence: user prompts, agent transcripts, diffs, output artifacts, validation logs, and failed runs.
- Do not pass your diagnosis or intended fix into forward-testing prompts; pass the skill and realistic user request.
- Do not grade success by output polish alone. Check whether the agent followed the required process and left verifiable evidence.
- Do not require artificial success counts. Require process evidence that makes low-output results trustworthy.
- Keep recommendations specific: name the file, rule, script, eval case, or validator check that should change.
- If the user asks you to modify the evaluated skill, apply the smallest change that blocks the observed failure mode.

## Workflow

1. **Scope the Evaluation ⚠️ REQUIRED**
   - Identify the skill path, target runtime, intended users, and concrete usage examples.
   - If no examples are provided, derive 3 realistic prompts from the skill description and user context.
   - Collect evidence: current `SKILL.md`, relevant references/scripts, prior agent transcript, output artifacts, or failing behavior.

2. **Run Mechanical Checks ⛔ BLOCKING**
   - Run `scripts/check_skill_quality.py <skill-path>` and capture the full output (status, error count, warning count, metrics).
   - If the skill has its own validator, run that too.
   - A verdict is not valid without mechanical check evidence in the output. If the check script cannot be run (missing Python, broken script), record that as the first risk and set the verdict to `not-ready`.
   - Treat script results as a starting point; they do not replace semantic evaluation.

3. **Evaluate Design Fit ⚠️ REQUIRED**
   - Read `references/best-practices.md`.
   - Read `references/skill-prompt-quality.md` to review `SKILL.md` as executable agent instructions; treat it as a front gate, not proof of runtime compliance.
   - Use `references/evaluation-rubric.md` to score trigger quality, workflow control, progressive disclosure, deterministic resources, validation integrity, and output evidence.
   - Identify anti-patterns: workflow hidden in description, vague "ensure quality" instructions, no negative cases, no close-loop validation, or final artifacts that can mask weak process.

4. **Design or Review Eval Cases ⚠️ REQUIRED**
   - Read `references/eval-case-design.md`.
   - For repeatable suites or CI-style checks, read `references/harness-engineering.md`.
   - If the evaluation starts from a known failure, read `references/failure-regression.md` first and convert the failure into a no-leak regression case.
   - Create or review eval cases that include happy paths, ambiguity, edge cases, and known failure modes.
   - Prefer assertions over broad expected-output prose: required actions, forbidden shortcuts, required artifacts, and validation commands.
   - Validate eval files with `scripts/check_eval_cases.py <evals.json>` when eval cases exist.

5. **Forward-Test When Useful**
   - Read `references/forward-testing.md`.
   - For complex, high-impact, or recently changed skills, forward-test with fresh agents when the runtime allows it and the user approves any costly or risky runs.
   - Before running a real-agent eval, use `references/agent-runtime-discovery.md` and optionally `scripts/discover_agent_runtime.py` to discover available agent runtimes and capture channels.
   - Then use `references/harness-engineering.md` → "Evidence Capture Discovery" to record the chosen evidence level. Codex JSONL is a reference implementation, not a hard dependency.
   - Prompt shape: `Use $<skill-name> at <path> to handle: <realistic user request>`.
   - Review available traces, transcripts, command logs, diffs, validator output, and artifacts against the rubric. Do not leak the expected answer unless testing retrieval of a known reference.
   - If only final artifacts are available, report artifact-level validation only; do not claim workflow adherence.

6. **Recommend or Apply Changes**
   - Convert each failure into one of: trigger metadata change, workflow gate, anti-pattern rule, deterministic script, validator check, reference split, eval case, or output schema.
   - Keep `SKILL.md` under 500 lines; move detailed standards into directly linked reference files.
   - After edits, rerun mechanical checks and any representative eval/smoke checks.

## Output Shape

For a review-only task, return these five sections in order. Omit any section only when the evaluation did not reach that phase:

1. **Mechanical Check Results** — output from `scripts/check_skill_quality.py` (status, error count, warning count, key metrics). If this section is absent, the evaluation is incomplete and the verdict must be `not-ready`.
2. **Verdict** — `ready`, `usable-with-gaps`, or `not-ready`.
3. **Top Risks** — ordered by impact, each with evidence from files, scripts, transcripts, or artifacts.
4. **Recommended Changes** — each names a target file, rule, script, or eval case, and explains why the change matters.
5. **Suggested Eval Cases** — at least one concrete prompt with must-do and must-not-do assertions.

For an edit task, also include changed files and verification commands.

## Resources

- `scripts/check_skill_quality.py` — deterministic skill structure and hygiene checks. Pass `--receipt <path>` to write a timestamped JSON receipt after a passing run; use this as evidence that mechanical checks completed before a verdict.
- `scripts/check_eval_cases.py` — validate portable eval case JSON files.
- `scripts/discover_agent_runtime.py` — read-only discovery of local agent CLIs and likely evidence capture methods.
- `references/best-practices.md` — distilled guidance from OpenAI, Claude, Trae, and local skill-forge/skill-creator principles.
- `references/skill-prompt-quality.md` — static gate for whether `SKILL.md` can reliably steer agent behavior.
- `references/evaluation-rubric.md` — scoring rubric and pass/fail gates.
- `references/eval-case-design.md` — how to create regression and forward-test cases.
- `references/agent-runtime-discovery.md` — how to discover capture channels for Codex, Claude Code, GitHub Copilot, Kimi, and custom agents.
- `references/harness-engineering.md` — design repeatable eval harnesses: datasets, traces, graders, aggregation, and gates.
- `references/forward-testing.md` — skill-creator style fresh-agent testing protocol.
- `references/failure-regression.md` — convert observed failures into no-leak regression cases and skill changes.
- `templates/eval-case.json` — starter schema for skill eval cases.
- `templates/harness-plan.md` — lightweight plan for repeatable skill eval suites.
