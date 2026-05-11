# Forward Testing

## Contents

- Purpose
- When To Forward-Test
- No-Leak Protocol
- Prompt Shapes
- Evidence To Collect
- Evaluation Review
- When To Stop

## Purpose

Forward-testing asks a fresh agent to use the skill on a realistic task. It tests whether the skill generalizes when the agent does not see your diagnosis, planned fix, or expected answer.

Use it to answer: would another agent naturally trigger the skill, read the right resources, follow the gates, and produce the required evidence?

## When To Forward-Test

Forward-test when any of these are true:

- The skill is complex, multi-step, or high-impact.
- The skill was changed because of a real failure.
- The skill has blocking gates, validators, or output schemas.
- The skill is about analysis, code changes, safety, reporting, or orchestration.
- The user asks whether the skill "really works".

Skip or postpone only when the run would be costly, long-running, require external approvals, or modify live systems. In those cases, ask the user before dispatching.

## No-Leak Protocol

Follow these rules from skill-creator validation integrity:

- Use a fresh thread, agent, or clean context where practical.
- Pass the skill path and a realistic user request.
- Pass raw artifacts, not your conclusions.
- Do not reveal the suspected failure, intended fix, hidden rubric, or expected output.
- Do not reuse artifacts from prior failed runs unless the eval is explicitly about resume behavior.
- Clean up or isolate generated artifacts between iterations.

The goal is to test transferable behavior, not whether an agent can follow hints.

## Prompt Shapes

Good:

```text
Use $repo-bug-audit at /path/to/repo-bug-audit to analyze /path/to/a/repo-group and produce a final handoff package.
```

Good:

```text
Use $email-designer at /path/to/email-designer to create an Outlook-compatible launch email from this brief: ...
```

Bad:

```text
Test whether the skill now creates shard summaries and avoids write_package.py.
```

Bad:

```text
Review the skill and pretend a user asked for a multi-repo audit.
```

## Evidence To Collect

Save or summarize:

- User-like prompt.
- Agent transcript or key progress messages.
- Files created or modified.
- Validator output.
- Screenshots or rendered artifacts when relevant.
- Deviations from required process.
- Whether the agent asked unnecessary questions or skipped required questions.

## Evaluation Review

Evaluate the run with `evaluation-rubric.md`.

Ask:

- Did the skill trigger from the user-like prompt?
- Did the agent read the needed references?
- Did it follow blocking gates before irreversible or quality-critical steps?
- Did it produce required artifacts and process evidence?
- Did it run validation before claiming completion?
- Did it avoid forbidden shortcuts?
- Did the final answer honestly state coverage and remaining gaps?

## Evaluator Context: Diagnosis IS the Output

When forward-testing `skill-evaluator` itself, the no-leak rule still applies but the framing differs. The evaluator's job is to diagnose skill issues, so the prompt should ask for an evaluation of a concrete skill without hinting at which specific failure to find.

Good (evaluator self-test):

```text
Use $skill-evaluator at /path/to/skill-evaluator to review /path/to/a-skill-with-known-gaps and return a verdict.
```

Bad (evaluator self-test):

```text
Check whether skill-evaluator correctly flags the missing blocking gate in /path/to/a-skill.
```

The difference: the good prompt asks for evaluation; the bad prompt tells the evaluator what to find. The test is whether the evaluator discovers the gaps on its own — exactly the same principle as any other skill forward-test.

## When To Stop

Stop iterating when:

- The original failure case no longer reproduces.
- The fix does not depend on leaked context.
- Mechanical checks pass.
- The updated skill still stays concise and progressively loaded.
- New risks are documented as follow-up eval cases rather than hidden assumptions.

