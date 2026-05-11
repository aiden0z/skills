# Skill Prompt Quality Gate

## Contents

- Purpose
- When To Use
- Gate Dimensions
- Scoring
- Blocking Signals
- Review Procedure
- Output Notes

## Purpose

Review `SKILL.md` as executable agent instructions, not as polished prose. The question is whether a fresh agent can reliably trigger the skill, follow the intended process, leave evidence, and avoid known shortcuts.

This is a static front gate. It can identify instruction risks before a real run, but it cannot prove runtime compliance. Use transcripts, traces, artifacts, and validators for that claim.

## When To Use

Use this gate during design-fit evaluation when:

- The skill has a multi-step workflow.
- The skill previously failed in a real agent run.
- The skill can produce polished final artifacts while skipping required process.
- The skill relies on references, scripts, validators, or runtime-specific behavior.
- The user asks whether the prompt or `SKILL.md` quality is good enough.

## Gate Dimensions

Score each dimension from 0 to 2.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Trigger clarity | Vague, generic, or missing negative cases | Usable but incomplete | Clear explicit, implicit, and negative triggers |
| Instruction hierarchy | Required, optional, fallback, and forbidden actions blur together | Some hierarchy exists | Required gates, optional paths, fallbacks, and prohibitions are distinct |
| Workflow enforceability | Advice only | Steps exist but are easy to skip | Critical transitions have blocking gates or evidence requirements |
| Evidence contract | Completion claims need no proof | Some evidence named | Each important claim maps to artifacts, logs, traces, validators, or explicit uncertainty |
| Progressive disclosure | Too much in `SKILL.md` or hidden references | References exist but weak loading guidance | Lean `SKILL.md` with direct, conditional reference-loading cues |
| Anti-shortcut coverage | Known shortcuts remain possible | Some warnings but vague | Concrete anti-patterns close observed or likely loopholes |
| Evalability | Requirements cannot become assertions | Some checks possible | Key rules map cleanly to eval prompts, trace assertions, or artifact assertions |

## Scoring

- `12-14`: prompt quality is strong enough for normal use; verify with real runs when risk is high.
- `8-11`: usable with gaps; improve weak dimensions before broad reuse.
- `0-7`: not ready for reliable use; rewrite the instruction structure before forward-testing.

Do not average this score into a false sense of certainty. A single blocking signal below can override a high score.

## Blocking Signals

Any of these normally blocks a `ready` verdict:

- The description does not make the skill discoverable for its primary use.
- The description contains a mini-workflow that lets agents skip reading `SKILL.md`.
- A required output has no evidence contract.
- A known real failure can still pass by producing final artifacts only.
- The skill uses "should", "ensure", or "be thorough" where a fragile step needs a gate.
- References are necessary but not directly linked from `SKILL.md`.
- A high-scale task has no shard, phase, or coverage evidence model.
- The skill invites project-specific residue, private paths, or domain names without an explicit reason.

## Review Procedure

1. Read the frontmatter first. Decide whether a fresh agent would trigger the skill from realistic user prompts.
2. Read only the `SKILL.md` body next. Mark each major instruction as required, optional, fallback, forbidden, or explanatory.
3. For each required step, ask what evidence would prove it happened.
4. For each known failure, ask whether the current text still allows the failure to look successful.
5. For each referenced file, check whether `SKILL.md` tells the agent when to load it.
6. Convert weak prompt areas into concrete changes: stronger trigger metadata, a blocking gate, an anti-shortcut rule, a reference-loading cue, a validator check, or an eval case.

## Output Notes

When reporting this gate, separate:

- Static prompt risks: what the instructions make likely.
- Evidence gaps: what cannot be proven without a run.
- Runtime claims: only what traces, transcripts, artifacts, or validators support.

Useful phrasing:

- `Prompt quality risk`: the skill allows a shortcut.
- `Evidence gap`: the final artifact cannot prove the workflow happened.
- `Runtime failure`: a captured run shows the agent skipped or violated the rule.
