# Failure Regression

## Contents

- Purpose
- Failure Intake
- Convert Failure To Eval Case
- Map Failure To Skill Changes
- Regression Acceptance
- Example

## Purpose

Real failures are the best eval cases. A failure regression turns an observed bad agent run into a reusable case that can be rerun after skill edits.

The aim is not to punish low-quality output. The aim is to identify the missing gate or evidence requirement that allowed the output.

## Failure Intake

Collect raw evidence:

- Original user prompt.
- Agent transcript or key action log.
- Skill version/path used.
- Output artifacts.
- Validator output, if any.
- What the user expected.
- What happened instead.

Write the failure in neutral form:

```text
Observed: Agent produced a final multi-repo package after a short global scan.
Impact: Final artifacts looked complete but per-repo exploration evidence was thin.
Missing gate: No per-repo shard summary or validator check prevented packaging.
```

## Convert Failure To Eval Case

Remove diagnosis from the prompt. The eval prompt should look like a real user request.

Bad regression prompt:

```text
Check that the agent does not use a late package writer.
```

Good regression prompt:

```text
Use $repo-bug-audit at /path/to/skill to perform a deep static audit of /path/to/repo-group and produce the final package.
```

Move the diagnosis into assertions:

- `must_do`: freeze repo roster, produce per-repo shard summaries, run final validator.
- `must_not_do`: mass-generate final Markdown from a late package writer.
- `success_evidence`: shard JSON exists for every repo; validator output is clean.

## Map Failure To Skill Changes

Use this mapping:

| Failure Pattern | Skill Change |
|---|---|
| Skill did not trigger | Improve `description` trigger conditions |
| Agent skipped a phase | Add blocking workflow gate |
| Agent used a shortcut | Add anti-pattern rule and validator check |
| Final output hid weak process | Add evidence ledger or output schema |
| Agent fabricated completeness | Add honest-uncertainty rule and validation |
| Repeated manual check | Add script |
| Reference not read | Link it directly from `SKILL.md` and name when to read it |
| Evaluation leaked answer | Rewrite forward-test prompt with no diagnosis |

## Regression Acceptance

Accept the fix only when:

- The regression eval prompt no longer reproduces the failure.
- The agent passes because of the skill, not because the prompt exposed the expected behavior.
- Mechanical checks pass.
- The new rule is not overfit to one private repo, user, company, or path.
- The change adds the minimum necessary constraint.

## Example

Failure:

```text
A multi-repo audit completed with polished HTML and image output, but the agent scanned only a few high-risk patterns and then generated final package files from a scratch script.
```

Regression case:

```json
{
  "id": "repo-audit-regression-001",
  "type": "regression",
  "prompt": "Use $repo-bug-audit at /path/to/repo-bug-audit to run a deep static audit of /path/to/repo-group and produce a final handoff package.",
  "must_do": [
    "Freeze the repository roster before candidate hunting",
    "Create a shard summary for every repository",
    "Run final validation with the repo root"
  ],
  "must_not_do": [
    "Mass-generate final Markdown deliverables from a late package-writer script",
    "Claim deep completion without per-repo evidence"
  ],
  "success_evidence": [
    "work/shards/<repo>/shard-summary.json exists for every discovered repo",
    "Final validator output reports zero errors"
  ]
}
```

