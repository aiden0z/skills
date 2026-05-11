# Skill Evaluation Best Practices

## Contents

- Core Thesis
- Source Principles
- What Good Skills Optimize For
- Common Failure Modes
- How to Apply This to Existing Skills

## Core Thesis

A skill is not a longer prompt. It is a reusable capability module that tells an agent when to act, how to proceed, what evidence to produce, and how to verify that the work is done.

Evaluate a skill by asking: would another agent, with only this skill and a realistic user request, reliably do the right thing?

## Source Principles

These principles synthesize:

- OpenAI eval-skills guidance: start from real tasks, define success criteria, compare behavior across iterations, and treat failures as eval cases.
- OpenAI agent eval and trace grading guidance: inspect traces when debugging workflow behavior, grade traces against structured criteria, and use datasets/eval runs to compare changes over time.
- Claude skill best practices: keep the main skill concise, use progressive disclosure, place detailed context in resources, and include scripts for deterministic work.
- Trae skill best practices: skills should be clear, rigorous, executable instruction documents; design from failure; use workflow/checklists; harden scripts with predictable outputs.
- Harness-oriented frameworks such as Inspect, LangSmith, promptfoo, and DeepEval: separate dataset/case definition from runner, trace capture, deterministic assertions, model/human grading, and aggregate comparison.
- Local skill-forge / skill-creator practice: every line must justify its token cost; descriptions control triggering; forward-test with raw artifacts, not leaked conclusions.

## What Good Skills Optimize For

### Trigger Accuracy

The `description` should describe when to use the skill, not summarize the workflow. If the description contains a mini-workflow, agents may follow it as a shortcut and skip `SKILL.md`.

Good trigger metadata names concrete situations, artifacts, symptoms, and user intents.

### Process Control

For fragile tasks, vague instructions are not enough. Use:

- Required workflow steps.
- Blocking gates before risky or quality-critical transitions.
- Anti-patterns that close common loopholes.
- Output schemas or ledgers when process evidence matters.

### Progressive Disclosure

Keep `SKILL.md` as the map. Put detailed standards, schemas, examples, and domain references in directly linked files.

Large reference files should have a table of contents. Avoid deep reference chains.

### Deterministic Resources

Scripts should handle repeatable, fragile, or easy-to-forget checks. Script output should be understandable, actionable, and stable across platforms where possible.

Use scripts for structure validation, artifact inspection, schema checks, and evidence completeness checks. Do not rely on the agent to remember mechanical details.

### Evidence Over Polish

A beautiful final artifact can hide a weak process. Evaluate whether the skill forces the agent to leave evidence: commands run, paths inspected, decisions recorded, validation output, or explicit uncertainty.

### Failure-Driven Iteration

Start from observed failures:

- What shortcut did the agent take?
- What missing gate allowed the shortcut?
- What artifact would have made the failure visible?
- Can a script check it?
- Can a small eval case reproduce it?

### Harness Engineering

A mature skill eval is a small harness, not just a checklist. Keep these layers separate:

- Dataset: prompts, tags, trigger expectations, required artifacts, and success criteria.
- Runner: how fresh agents are invoked, with least required permissions.
- Trace capture: transcript, commands, tool calls, artifacts, stdout/stderr, and timing.
- Graders: deterministic assertions first, model-assisted rubric second, human review for calibration.
- Aggregation: pass/fail, score, failure category, baseline comparison, and known flaky cases.
- Gate: what blocks publishing and what becomes a warning.

## Common Failure Modes

- Description summarizes the workflow and becomes a shortcut.
- `SKILL.md` is a broad essay instead of executable instructions.
- The skill says "ensure quality" without defining checkable evidence.
- The agent can create final deliverables without doing the required exploration.
- No negative cases or ambiguity cases exist.
- Optional resources are not clearly linked from `SKILL.md`.
- Scripts fail with stack traces instead of actionable messages.
- The skill has no regression path after real-world failures.
- The skill overfits one project by hardcoding names, paths, or private context.
- Forward tests leak the intended diagnosis and therefore do not test generalization.

## How to Apply This to Existing Skills

When reviewing a skill, map each issue to a concrete intervention:

| Failure | Preferred Intervention |
|---|---|
| Skill does not trigger | Rewrite `description` with user intents and artifact types |
| Agent skips a phase | Add a blocking gate and checklist item |
| Agent produces shallow output | Require per-unit evidence ledger or output schema |
| Agent fabricates completeness | Add validator checks and honest uncertainty language |
| Final report hides poor process | Require source evidence and pre-package validation |
| Skill is too long | Move details into references with direct links |
| Repeated manual checks | Add a script |
| Real failure recurs | Add eval case and regression expectation |
