# Shard Evidence Schema

## Contents

- shard-summary.json
- Required Top-Level Fields
- Required for specific modes
- Surface Map
- Hypothesis Loops
- Seed Triage
- candidates.md
- batch-first-pass Relaxations

This is the canonical schema for `work/shards/<repo>/shard-summary.json` and `work/shards/<repo>/candidates.md`. The validator enforces the minimum evidence contract: real paths, honest execution/coverage status, at least one evidence-bearing surface and hypothesis loop for non-trivial repos, seed triage when supplemental seeds exist, and candidate-count consistency. The richer guidance below helps reviewers judge depth without turning discovery into a checklist.

## shard-summary.json

### Required Top-Level Fields

| Field | Type | Description |
|---|---|---|
| `repo` | string | Repository name matching the frozen roster |
| `profile_name` | string | Must match `repo` |
| `execution_mode` | enum | `parallel`, `serial`, or `batched` |
| `parallel_eligible` | boolean | Must be `true` for repos with >10 source files |
| `coverage_classification` | enum | `deep-complete`, `first-pass`, or `focused` |
| `candidate_count` | integer | Number of retained candidates (includes promoted Bugs) |
| `submitted_bug_ids` | string[] | Bug IDs promoted from this shard (e.g. `["BUG-0001"]`) |
| `profile_updated_from_shard` | boolean | Must be `true` after exploration |
| `evidence_paths` | string[] | Real file paths relative to repo root (validator checks existence). ≥1 for any repo, ≥3 for ≥50 files |
| `risk_surfaces_scanned` | string[] | Non-empty list of surface names actually scanned |
| `commands_or_searches` | string[] | Concrete repo-local search commands or patterns |
| `surface_map` | object | See Surface Map below |
| `hypothesis_loops` | object[] | See Hypothesis Loops below |
| `seed_triage` | object[] | See Seed Triage below |
| `profile_evidence_sections` | object | Must include keys: `Findings and Candidates`, `Known Uncovered Areas`, `Risk Surfaces` |

### Required for specific modes

| Field | Required when | Type |
|---|---|---|
| `agent_or_worker` | execution_mode is `parallel` or `batched` | string |
| `serial_reason` | parallel_eligible=true but execution_mode=serial | string (≥20 chars) |
| `focus_scope` | coverage_classification=`focused` | string (≥10 chars) |
| `remaining_gaps` | coverage_classification=`first-pass` or `focused` | string[] |
| `call_chains_traced` | coverage_classification=`deep-complete` AND ≥50 files | string[] |
| `zero_finding_rationale` | candidate_count=0 AND no submitted Bugs | string (≥20 chars) |

### Surface Map

An object mapping surface category names to arrays of description strings. Common categories: `entry_points`, `auth`, `state`, `external_integrations`, `execution`, `config_secrets`, `network`, `file_io`, `serialization`, `async_jobs`.

- For non-trivial repos: ≥3 populated categories
- For repos with ≥50 files: ≥4 populated categories
- Each populated entry must contain specific file references

### Hypothesis Loops

Array of objects, each representing one exploration hypothesis:

```json
{
  "hypothesis": "Short description of the failure hypothesis",
  "result": "promoted|parked|refuted",
  "route": "How this hypothesis is reachable (endpoint, entry point)",
  "entry_point": "Specific file path or function",
  "chain_or_boundary": "The call chain or boundary being tested",
  "guard_or_refutation": "What guards exist or what refuted the hypothesis",
  "evidence": "Code evidence for the conclusion"
}
```

In `batch-first-pass` mode, `hypothesis` and `result` are required; other fields are recommended but not enforced.

### Seed Triage

Array of objects, one per reviewed high-recall seed category:

```json
{
  "category": "auth_and_authorization|config_and_secrets|deployment_and_supply_chain|execution_boundaries|file_and_path_boundaries|frontend_trust_boundaries|network_and_ssrf|resource_lifecycle|serialization_contracts|state_and_data_integrity|transport_security",
  "location": "File:line reference",
  "seed": "The search seed text",
  "follow_up": "What tracing/refutation was performed",
  "outcome": "promoted|parked|refuted|merged",
  "candidate_or_reason": "Linked candidate ID or refutation reason"
}
```

Coverage guidance:
- **deep mode**: review enough seed categories to explain promoted, parked, refuted, or merged outcomes.
- **batch-first-pass mode**: record representative seeds rather than inflating counts.

## candidates.md

### Required Sections

1. `## Candidate Leads` — One evidence-bearing bullet per retained candidate. Each bullet must include a candidate ID or `path:line` anchor. The number of bullets in this section must equal `candidate_count` in shard-summary.json.
2. `## Refuted Leads` — What was reviewed and dismissed.
3. `## Zero-candidate Rationale` — If no candidates, explain why with concrete scanned surfaces.

### Candidate Lead Format

```
- P<priority>-cand-<repo>-<NN>: <title> — <file:line> <evidence summary>
```

Example: `- P1-cand-agent-01: RCE via eval() — chat/agent.py:1252 eval() on LLM tool arguments`

## batch-first-pass Relaxations

When `--coverage-mode batch-first-pass` is passed to the validator, these rules are relaxed:

| Rule | deep | batch-first-pass |
|---|---|---|
| seed_triage | Evidence-bearing reviewed seed required when supplemental seeds exist | Representative reviewed seed required when supplemental seeds exist |
| surface_map | At least one evidence-bearing surface for non-trivial repos; more surfaces expected for credible deep claims | Same minimum; narrower coverage must be labeled honestly |
| hypothesis_loops | At least one evidence-bearing promoted, parked, refuted, or merged loop for non-trivial repos | Same minimum; concise loop accepted |
| commands_or_searches specificity | Code anchors required | Path references accepted |
| evidence_paths format | Line numbers stripped, existence checked | Existence checked, line numbers tolerated |
