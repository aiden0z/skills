# Skill Evaluation Rubric

## Contents

- Verdicts
- Scoring
- Blocking Failures
- Review Checklist
- Report Template

## Verdicts

- `ready`: no blocking failures; minor improvements only.
- `usable-with-gaps`: works for normal cases but has risks that should be fixed before broad reuse.
- `not-ready`: likely to fail, mis-trigger, skip important process, or produce unverifiable output.

## Scoring

Score each dimension from 0 to 2.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Trigger metadata | Vague or workflow-heavy | Some triggers but incomplete | Concrete when-to-use signals, no workflow shortcut |
| Prompt quality gate | Instructions are prose-only or easy to bypass | Some constraints but weak evidence mapping | `SKILL.md` has clear hierarchy, gates, evidence contracts, and anti-shortcut rules |
| Scope and boundaries | Unclear or overbroad | Mostly clear | Clear target tasks, non-goals, and safe defaults |
| Workflow control | Freeform advice | Steps exist but weak gates | Required workflow with blocking gates |
| Progressive disclosure | Everything in one file or hidden references | Some split but hard to navigate | Lean `SKILL.md`, direct references, TOCs for long files |
| Deterministic resources | No scripts for repeatable fragile checks | Scripts exist but weak output | Scripts are robust, actionable, and documented |
| Validation integrity | Final output can mask weak process | Some validation | Evidence ledgers, validators, and pre/final checks |
| Eval coverage | No eval cases | Happy paths only | Happy, ambiguous, edge, and failure-regression cases |
| Maintainability | Project-specific residue or placeholders | Some cleanup needed | Neutral, concise, no placeholders, no private residue |

## Blocking Failures

Any of these normally makes the verdict `not-ready`:

- Missing or invalid `SKILL.md` frontmatter.
- Description does not provide usable trigger conditions.
- Unfinished marker text remains in submittable skill files.
- Skill requires important outputs but defines no success evidence.
- A known real-world failure mode can still pass the skill workflow.
- Scripts required by the workflow do not run.
- The skill hardcodes private project names, users, or paths without a clear reason.
- Forward-testing only succeeds when the tester sees the intended answer or diagnosis.

## Review Checklist

### Metadata

- Does `description` say when to use the skill?
- Does it avoid summarizing the workflow?
- Does it include artifact types, symptoms, and user intents?

### Main Body

- Is `SKILL.md` under 500 lines?
- Does it start with the most important constraint or iron law?
- Are steps imperative and specific?
- Are risky transitions guarded by blocking gates?
- Are anti-patterns explicit enough to close loopholes?
- Did you run `references/skill-prompt-quality.md` as a static front gate?
- Can each critical instruction be mapped to evidence or an eval assertion?

### References

- Are all reference files directly linked from `SKILL.md`?
- Do files over 100 lines have a contents section?
- Is information split by domain or task rather than by accidental history?

### Scripts

- Do scripts cover fragile, repeatable checks?
- Do scripts fail with actionable messages?
- Are parameters meaningful and documented?
- Were scripts actually run after edits?

### Evals

- Are eval cases based on realistic user prompts?
- Do they include required and forbidden behaviors?
- Do they test process evidence, not just final output?
- Is at least one case derived from a real failure?

## Report Template

```markdown
## Verdict

ready | usable-with-gaps | not-ready

## Top Risks

1. Risk title — evidence and impact.

## Evidence

- Files inspected:
- Scripts run:
- Artifacts/transcripts reviewed:

## Recommended Changes

| Priority | Target | Change | Why |
|---|---|---|---|

## Suggested Eval Cases

| Case | Prompt | Must Pass | Must Not Do |
|---|---|---|---|
```
