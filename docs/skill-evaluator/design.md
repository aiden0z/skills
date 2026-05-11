# Skill Evaluator Design Notes

`skill-evaluator` is a review and hardening skill for Agent Skills. It helps maintainers decide whether a skill is discoverable, executable, verifiable, and robust under realistic agent behavior.

This design note is for human maintainers. Agent runtimes should still treat `skills/skill-evaluator/SKILL.md` as the entry point.

[中文文档](design_CN.md)

## What It Is For

Use this skill when you need to:

- Review whether a skill is ready to publish or install.
- Investigate why a skill triggers inconsistently.
- Turn an observed agent failure into a regression eval case.
- Check whether a skill's workflow can be followed by a fresh agent.
- Add deterministic validation around skill outputs.
- Design a lightweight eval harness for complex or high-risk skills.
- Compare skill behavior across versions, agents, or models.
- Discover how a specific agent runtime can expose traces, transcripts, diffs, or validation evidence for real-run evaluation.
- Inspect local agent CLIs such as Codex, Claude Code, GitHub Copilot, Kimi, or custom wrappers before choosing a capture strategy.

It is especially useful for skills that produce structured artifacts, coordinate multi-step workflows, rely on references/scripts, or have previously failed in realistic runs.

## What Problem It Solves

Many skills look good when read as instructions but fail in actual use. Common failure modes include:

- The skill description is too vague, so the agent does not trigger it.
- The workflow is described but not enforced by gates or validators.
- The agent produces polished final output while skipping required exploration.
- References exist but are not discoverable from `SKILL.md`.
- Validation only checks final files, not the process used to create them.
- Historical failures are discussed once but never converted into repeatable evals.
- A skill passes a mechanical structure check while still being semantically weak.

`skill-evaluator` addresses these problems by combining static review, rubric-based judgment, eval case design, failure regression, optional harness planning, and evidence-capture discovery for real agent runs.

## Core Design Philosophy

The skill follows a few principles:

1. **Evaluate behavior, not prose quality**

   A skill should be judged by what a fresh agent actually does with it. Clear writing matters, but it is not enough.

2. **Prefer evidence over confidence**

   Good evaluations use transcripts, tool calls, diffs, generated artifacts, validators, and trace logs. The final answer alone is too easy to over-trust.

3. **Keep the default path lightweight**

   Not every skill needs a full harness. Basic review should remain fast: read the skill, run mechanical checks, score design fit, and recommend targeted changes.

4. **Make complex evaluation opt-in**

   Harness engineering is available for high-impact or failure-prone skills, but it is not mandatory for every small skill.

5. **Convert failures into assets**

   A real failure should become a regression case, a validator check, a reference improvement, or a workflow gate.

6. **Use deterministic checks first**

   Scripts and assertions should catch objective failures before relying on model-assisted grading.

7. **Discover evidence channels instead of hardcoding one agent**

   Codex JSONL is a useful reference implementation, but it is not the protocol. Other runtimes may expose transcripts, IDE logs, PR comments, CI logs, trace spans, diffs, or generated artifacts. The evaluator should first discover what the current runtime can capture, then state which claims the available evidence can support.

## How It Works

The main workflow lives in `SKILL.md`:

1. **Scope the evaluation**
   - Identify the target skill, runtime, intended user, and realistic prompts.
   - Collect evidence such as prior transcripts, generated artifacts, and validation logs.

2. **Run mechanical checks**
   - Use `scripts/check_skill_quality.py` to catch packaging and hygiene issues.
   - Run the evaluated skill's own validators when available.

3. **Evaluate design fit**
   - Use `references/evaluation-rubric.md` to score trigger quality, workflow control, progressive disclosure, deterministic resources, validation integrity, and output evidence.

4. **Design or review eval cases**
   - Use `references/eval-case-design.md`.
   - Convert known failures using `references/failure-regression.md`.
   - Validate eval case files with `scripts/check_eval_cases.py`.

5. **Forward-test when useful**
   - Use `references/forward-testing.md` to run fresh-agent checks without leaking the expected diagnosis.
   - Use `references/harness-engineering.md` to discover the runtime's evidence capture channels before grading workflow adherence.
   - Optionally run `scripts/discover_agent_runtime.py` to inspect local agent CLIs before choosing a capture strategy.

6. **Recommend or apply changes**
   - Convert each weakness into a concrete change: metadata, workflow gate, script, reference split, validator, eval case, or output schema.

## Lightweight Harness Model

For complex skills, `references/harness-engineering.md` defines a minimal repeatable harness model:

- **Dataset**: realistic prompts, trigger cases, negative controls, and regressions.
- **Runner**: the runtime command or environment used to execute each case.
- **Evidence capture discovery**: find the best available runtime evidence channel before running or grading the eval.
- **Trace and artifact capture**: structured traces, transcripts, commands, diffs, generated files, CI logs, and validation logs.
- **Scorers**: deterministic checks first, model-assisted or human review second.
- **Aggregation**: results grouped by case, tag, failure category, model, runtime, and skill version.
- **Gate**: rules that decide whether a skill can be published.

This is intentionally a design pattern, not a required framework. The goal is to make evaluation repeatable without turning every skill into a large testing platform.

## Evidence Capture Discovery

Real-run evaluation needs process evidence. Different agent tools expose that evidence differently, so the evaluator should discover the available capture channel rather than assume a fixed format.

For local CLI discovery, run:

```bash
python3 scripts/discover_agent_runtime.py --json
```

The script is read-only. It checks local `PATH`, safe help/version commands, and capture-related help text. It does not start an agent run.

Use this ladder:

| Level | Evidence | Claims Allowed |
|---|---|---|
| 3 | Structured trace + artifacts + validator output | Workflow adherence and artifact validation |
| 2 | Transcript or command/tool log + artifacts | Partial workflow adherence and artifact validation |
| 1 | Artifacts + validator output only | Artifact validation only |
| 0 | Final answer only | Not acceptable for real-run eval |

Examples:

- Codex CLI: `codex exec --json` can produce JSONL structured events.
- Claude Code or IDE agents: capture transcript/session export, terminal logs, diffs, artifacts, and validator output.
- GitHub Copilot coding agent: capture PR/commit diff, issue or PR comments, workflow logs, generated artifacts, and CI validation.
- LangSmith, Phoenix, Braintrust, or OpenTelemetry-backed systems: capture trace spans, tool calls, evaluator scores, and artifacts.
- Custom or unknown CLI agents: inspect help output for `json`, `trace`, `log`, `session`, `export`, `output`, or non-interactive/headless modes.

If only final artifacts are available, the evaluator should say `artifact validation passed` rather than `workflow adhered`. This distinction matters for skills where the final report can look complete while the exploration process was skipped.

## File Structure

```text
docs/
  skill-evaluator/
    design.md
    design_CN.md

skills/
  skill-evaluator/
    SKILL.md
    agents/
      openai.yaml
    evals/
      core-regressions.json
    references/
      agent-runtime-discovery.md
      best-practices.md
      eval-case-design.md
      evaluation-rubric.md
      failure-regression.md
      forward-testing.md
      harness-engineering.md
      skill-prompt-quality.md
    scripts/
      check_eval_cases.py
      check_skill_quality.py
      discover_agent_runtime.py
    templates/
      eval-case.json
      harness-plan.md
```

## Key References

- `references/best-practices.md`
  - Distilled guidance from skill creation and eval best practices.

- `references/agent-runtime-discovery.md`
  - Safe discovery flow for local agent CLIs and runtime-specific capture channels.

- `references/evaluation-rubric.md`
  - Scoring framework for skill readiness.

- `references/eval-case-design.md`
  - Portable schema and patterns for skill eval cases.

- `references/failure-regression.md`
  - How to turn observed failures into no-leak regression cases.

- `references/forward-testing.md`
  - Fresh-agent testing protocol.

- `references/harness-engineering.md`
  - Lightweight harness design for repeatable skill evaluation, including evidence capture discovery.

- `references/skill-prompt-quality.md`
  - Static review gate for whether `SKILL.md` can reliably steer agent behavior.

## Scripts

### `check_skill_quality.py`

Runs deterministic checks over a skill directory:

```bash
python3 scripts/check_skill_quality.py /path/to/skill
```

It checks core packaging and hygiene, including frontmatter, line count, references, scripts, and common anti-patterns.

### `check_eval_cases.py`

Validates portable skill eval case JSON files:

```bash
python3 scripts/check_eval_cases.py /path/to/evals.json
```

Use strict mode when a suite is ready to enforce the portable schema:

```bash
python3 scripts/check_eval_cases.py --strict-portable /path/to/evals.json
```

Strict mode requires fields such as `scope`, `trigger_expectation`, `tags`, `grader`, and `failure_categories`.

### `discover_agent_runtime.py`

Performs read-only local discovery of common agent runtimes:

```bash
python3 scripts/discover_agent_runtime.py --json
```

It looks for CLI hints for Codex, Claude Code, GitHub Copilot, Kimi, and similar local wrappers. Its output is a starting point for the harness plan, not a guarantee that a real run will expose every event.

## Eval Case Shape

The starter template is in `templates/eval-case.json`.

Important fields include:

- `id`: stable case id.
- `type`: happy path, edge case, negative, regression, trigger, or ambiguous scope.
- `scope`: agent-level, component-level, reference-retrieval, or artifact-review.
- `trigger_expectation`: explicit, implicit, contextual, negative, or not-applicable.
- `prompt`: realistic user request without leaking the hidden rubric.
- `must_do`: required actions.
- `must_not_do`: forbidden shortcuts.
- `required_artifacts`: files or outputs expected after the run.
- `success_evidence`: transcript, trace, artifact, or validator evidence.
- `trace_assertions`: deterministic checks over captured events or transcripts.
- `artifact_assertions`: deterministic checks over generated files.
- `grader`: deterministic, model-assisted, human, or hybrid.
- `failure_categories`: labels used for aggregation.

## When Not To Use It

Do not use this skill as heavy process for every small edit. A tiny skill with a clear trigger and one simple script may only need:

```bash
python3 scripts/check_skill_quality.py /path/to/skill
python3 /path/to/skill-creator/scripts/quick_validate.py /path/to/skill
```

Use the fuller rubric, eval cases, or harness planning when the skill is complex, user-facing, failure-prone, or about to be published broadly.

## Relationship To Other Skill Tools

`skill-evaluator` complements skill creation tools:

- Use `skill-creator` to create or reshape a skill.
- Use `skill-evaluator` to test whether the resulting skill works under realistic conditions.
- Use a target skill's own validators to check its domain-specific artifacts.

The evaluator should not replace domain-specific validation. It asks whether the skill itself is well designed and whether agents can reliably follow it.

## Maintenance Notes

- Keep `SKILL.md` concise and under 500 lines.
- Put detailed methodology in `references/`.
- Keep scripts dependency-light and deterministic.
- Add real failures to eval cases instead of only documenting them in prose.
- Prefer warnings in normal mode and hard blockers in strict mode.
- Re-run validation after edits:

```bash
python3 scripts/check_skill_quality.py .
python3 scripts/check_eval_cases.py --strict-portable templates/eval-case.json
python3 -m py_compile scripts/check_eval_cases.py scripts/check_skill_quality.py scripts/discover_agent_runtime.py
```
