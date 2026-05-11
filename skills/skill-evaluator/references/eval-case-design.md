# Eval Case Design

## Contents

- Eval Case Principles
- Case Types
- JSON Shape
- Portable Case Fields
- Forward-Testing Protocol
- Example Assertions

## Eval Case Principles

Use eval cases to catch failures that matter in real use. An eval case should be a realistic user request plus specific assertions about process and output.

Prefer assertions over vague expected-output prose. A useful eval says what the agent must do, what it must not do, and what artifact or transcript evidence proves it.

## Case Types

- Happy path: normal intended use.
- Ambiguous scope: user omits important details; skill should infer safe defaults or ask one necessary question.
- Edge case: small input, large input, existing workspace, missing dependency, or partial prior output.
- Negative case: skill should decline, defer, or avoid destructive action.
- Regression case: derived from a real observed failure.
- Trigger case: prompt should or should not activate the skill.

## JSON Shape

Use this shape for portable eval cases:

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": "case-001",
      "type": "regression",
      "scope": "agent-level",
      "trigger_expectation": "explicit",
      "tags": ["workflow", "validator"],
      "prompt": "Use the skill on a realistic user request.",
      "must_do": [
        "Run the required validator",
        "Create a per-unit evidence ledger"
      ],
      "must_not_do": [
        "Generate final deliverables from memory",
        "Claim completion before validation"
      ],
      "required_artifacts": [
        "submit/quality/depth-coverage.md"
      ],
      "success_evidence": [
        "Validator exits 0",
        "Transcript shows the blocking gate before packaging"
      ],
      "trace_assertions": [
        {"type": "skill_invoked", "value": "skill-name"},
        {"type": "command_contains", "value": "validate"}
      ],
      "artifact_assertions": [
        {"type": "exists", "path": "submit/quality/depth-coverage.md"}
      ],
      "grader": {
        "mode": "deterministic",
        "threshold": 1.0
      },
      "failure_categories": [
        "trigger-miss",
        "workflow-skip",
        "missing-artifact"
      ]
    }
  ]
}
```

## Portable Case Fields

Recommended fields:

- `id`: stable lowercase case id.
- `type`: `happy-path`, `ambiguous-scope`, `edge-case`, `negative`, `regression`, or `trigger`.
- `scope`: `agent-level`, `component-level`, `reference-retrieval`, or `artifact-review`.
- `trigger_expectation`: `explicit`, `implicit`, `contextual`, `negative`, or `not-applicable`.
- `tags`: domains for filtering and comparison.
- `prompt`: user-like prompt. Do not include the hidden rubric or expected fix.
- `must_do`: required actions or artifacts.
- `must_not_do`: forbidden shortcuts.
- `required_artifacts`: files or outputs expected after the run.
- `success_evidence`: transcript, trace, artifact, or validator evidence proving success.
- `trace_assertions`: deterministic checks over a captured event stream or transcript.
- `artifact_assertions`: deterministic checks over files.
- `grader`: deterministic, model-assisted, human, or hybrid grading mode.
- `failure_categories`: labels used to aggregate failures across runs.

Existing eval files may use older `expected_output` or `expectations` fields. Treat those as migration inputs, not as the target schema. Run:

```bash
python3 scripts/check_eval_cases.py <evals.json>
```

Use `--strict-portable` when a skill is ready to enforce the portable schema.

## Forward-Testing Protocol

Use fresh agents or clean threads when practical.

Good prompt:

```text
Use $skill-name at /path/to/skill-name to handle: <realistic user request>
```

Bad prompt:

```text
Review this skill and check whether it fixes the bug where agents skip Phase 2.
```

Do not leak the intended diagnosis, expected answer, or planned fix unless the eval explicitly tests reference retrieval.

After the run, evaluate:

- Did the skill trigger?
- Did the agent read the needed references?
- Did it follow blocking gates?
- Did it produce required artifacts?
- Did validation happen before success claims?
- Did it avoid forbidden shortcuts?

## Example Assertions

For a workflow skill:

- Must create a scope summary before implementation.
- Must run validation before final handoff.
- Must not ask repeated confirmation questions unless checkpointed mode is requested.

For an analysis skill:

- Must cite raw evidence paths or transcript lines.
- Must record uncertainty instead of inventing missing data.
- Must include at least one negative or zero-result rationale when no findings are produced.

For a generation skill:

- Must use provided templates/assets.
- Must verify output with a renderer or validator.
- Must not leave unfinished marker text in final artifacts.
