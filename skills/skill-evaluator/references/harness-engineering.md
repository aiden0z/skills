# Harness Engineering

## Contents

- Purpose
- Research Synthesis
- Harness Layers
- Evidence Capture Discovery
- Evaluation Modes
- Gates and Thresholds
- CI and Regression Loop
- Minimal Harness Plan

## Purpose

Use this guide when a skill needs repeatable evaluation across versions, models, agents, or runtime environments. A harness turns isolated eval cases into a comparable system.

## Research Synthesis

Useful patterns from current eval practice:

- OpenAI skill evals frame an eval as prompt -> captured run (trace + artifacts) -> checks -> score. They recommend small targeted prompt sets, trigger tests, deterministic graders, and rubric grading for qualitative checks.
- OpenAI agent evals and trace grading emphasize workflow traces: model calls, tool calls, guardrails, handoffs, and structured criteria for finding regressions.
- Claude evaluation tooling emphasizes test cases, prompt versions, side-by-side comparison, and rerunning the suite after prompt changes.
- Inspect separates evaluation into datasets/tasks, solvers/agents, scorers, tools, sandboxes, and eval logs. This is a strong mental model for agent skill eval harnesses.
- LangSmith separates examples/datasets from experiments and captures traces, outputs, evaluator scores, metadata, and side-by-side comparisons.
- promptfoo emphasizes assertions: deterministic checks, model-assisted assertions, weighted scoring, direct assertions over stored outputs, and CI fail gates.
- DeepEval's test-case model highlights interaction scope: end-to-end agent run, component-level step, retrieved context, expected tools, token cost, and completion time.
- Agent runtimes expose different evidence surfaces. Treat Codex JSONL, Claude Code transcripts, GitHub Copilot agent logs, CI logs, OpenTelemetry traces, and hosted eval traces as different capture channels for the same evidence goal.

## Harness Layers

Design harnesses as layers:

1. **Dataset**
   - Eval cases with ids, tags, trigger expectation, prompt, hidden assertions, and required artifacts.
   - Include explicit invocation, implicit invocation, contextual invocation, and negative controls.

2. **Runner**
   - Executes each case in a clean workspace or isolated output root.
   - Uses least required permissions.
   - Records runtime configuration: skill version, model, agent runtime, date, environment, and command.

3. **Trace and Artifact Capture**
   - Capture transcript, JSONL events when available, commands, tool calls, generated files, stdout/stderr, screenshots, and validator output.
   - Keep traces separate from final artifacts so graders can inspect process, not just output.

4. **Scorers**
   - Deterministic first: file existence, command contains, forbidden file absent, validator exits 0, required section exists, id sequence contiguous.
   - Model-assisted second: rubric checks for quality, completeness, design judgment, or semantic correctness.
   - Human calibration: spot-check model graders, especially after rubric changes.

5. **Aggregation**
   - Aggregate by case, tag, failure category, required gate, model/runtime, and skill version.
   - Track both binary gates and scores.
   - Compare against a baseline run, not just a single pass/fail result.

6. **Gate**
   - Decide what blocks publishing.
   - Good blockers: trigger misses on core cases, skipped blocking gate, missing required artifacts, validation failure, unsafe action, or known regression.
   - Good warnings: efficiency drift, non-critical style drift, legacy eval schema, missing optional artifacts.

## Evidence Capture Discovery

Before a real-agent eval, discover what the current runtime can capture. Do not assume one agent's trace format applies everywhere.

Ask and record:

- Can the runtime emit structured events, JSONL, OpenTelemetry spans, or a tool-call timeline?
- Can the conversation/session transcript be exported or saved?
- Can shell commands, tool calls, or action logs be captured?
- Can file diffs be captured before and after the run?
- Can generated artifacts be written to an isolated output root?
- Can validator output, CI logs, PR comments, or workflow logs serve as evidence?
- What evidence is unavailable or manual-only?

Use this evidence ladder:

| Level | Evidence | Claims Allowed |
|---|---|---|
| 3 | Structured trace + artifacts + validator output | Workflow adherence and artifact validation |
| 2 | Transcript or command/tool log + artifacts | Partial workflow adherence and artifact validation |
| 1 | Artifacts + validator output only | Artifact validation only |
| 0 | Final answer only | Not acceptable for real-run eval |

Runtime examples:

- **Codex CLI**: prefer `codex exec --json` when available; parse JSONL events for commands, tool calls, usage, and final output.
- **Claude Code / IDE agents**: capture transcript/session export, terminal output, file diffs, generated artifacts, and validator logs.
- **GitHub Copilot coding agent**: capture PR/commit diff, issue or PR comments, workflow logs, generated artifacts, and CI validation.
- **LangSmith / Phoenix / Braintrust / OpenTelemetry**: export or inspect trace spans, tool calls, evaluator scores, and artifacts.
- **Unknown/custom runtime**: write down the discovered capture method and blind spots before grading.

Codex JSONL is a reference implementation, not a requirement. If no process trace is available, do not claim that the skill followed required workflow steps; claim only what artifacts and validators prove.

## Evaluation Modes

- **Static review**: inspect files and run mechanical checks. Fast but insufficient.
- **Dry-run harness**: validate eval cases and planned assertions without running agents.
- **Forward-test harness**: run fresh agents on a small representative suite.
- **Trace replay / artifact review**: grade stored transcripts and outputs without rerunning expensive tasks.
- **CI gate**: run a stable subset on every skill change.
- **Nightly/deep suite**: larger set with model-assisted or human-reviewed grading.

## Gates and Thresholds

Prefer explicit gates:

| Gate | Block? | Example |
|---|---|---|
| Trigger miss on explicit or implicit core case | Yes | Skill not invoked for target prompt |
| Negative trigger false positive | Yes for destructive/generative skills | Scaffolds new project for edit-existing request |
| Required artifact missing | Yes | No validation report, no evidence ledger |
| Forbidden shortcut observed | Yes | Package generated from memory |
| Validator failure | Yes | Skill's own validator exits non-zero |
| Rubric score below threshold | Usually | Architecture docs incomplete |
| Efficiency drift | Warning unless severe | Excessive retries or commands |

## CI and Regression Loop

Keep suites small and useful:

- Start with 10-20 cases for one skill.
- Add real failures as regression cases.
- Tag cases by feature and failure category.
- Keep a core blocking suite fast enough to run often.
- Run larger suites periodically.
- Compare results to the previous accepted baseline.
- When a case is flaky, quarantine it with a reason instead of deleting it.
- Review model-assisted grader drift with human spot checks.

## Minimal Harness Plan

For a new or recently changed skill:

```markdown
## Harness Plan

- Skill under eval:
- Version or commit:
- Runtime/model:
- Eval suite:
- Cases:
  - Explicit trigger:
  - Implicit trigger:
  - Negative trigger:
  - Regression:
  - Edge case:
- Runner:
- Evidence capture:
  - Runtime:
  - Structured trace:
  - Transcript/session log:
  - Command/tool log:
  - Artifact root:
  - Validator logs:
  - Known blind spots:
- Deterministic gates:
- Model/human rubric:
- Publish blockers:
- Baseline to compare:
```
