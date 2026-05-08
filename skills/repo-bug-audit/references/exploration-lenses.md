# Exploration Lenses

This is the entry point for the lens system. **A lens is a risk perspective for repository audit work**: state a concrete failure hypothesis, hunt for code evidence, refute candidates against sibling implementations, then promote or park the result. Phase 2 reads this page first; load the tier-specific files only when that tier is enabled.

> First constraint: see `authenticity.md`. Lens coverage is never a reason to fabricate. "Applied and found no Bug" is a valid and encouraged outcome.

## Contents

- Borrowed mental models
- Hypothesis-first static audit
- Default lens scope
- Split reference files
- Lens application records
- Pluggable strategies

## Borrowed Mental Models

This lens system borrows from:

- **systematic-debugging skill**: dynamic debugging discipline (Root Cause → Pattern → Hypothesis → Implementation), adapted to static audit work. Borrowed on 2026-05-07.
- **error-debugging-error-analysis skill**: multi-component boundary evidence collection, adapted into Outbound / Inbound / Shared Events / Shared Storage / Shared Config profile sections. Borrowed on 2026-05-07.

Revisit this page when those upstream skills materially change.

## Hypothesis-First Static Audit

The equivalent of "NO FIXES WITHOUT ROOT CAUSE" is:

```text
NO CANDIDATE WITHOUT HYPOTHESIS FIRST
```

Before grepping or reading code, write the specific failure mode being hunted. Without that, the audit turns into pattern matching and produces shallow false positives.

Run this loop for every enabled lens:

1. **Hypothesize** — write: "I am looking for failure mode X because Y would cause impact Z."
2. **Hunt** — use grep, LSP, call graphs, and profile tables according to the lens.
3. **Refute with sibling diff** — compare each candidate with 1-2 nearby implementations that handle the same scenario correctly. The diff is either the Bug or the false-positive guard.
4. **Promote or park** — promoted candidates become Bugs; weak but plausible leads go to `work/candidates/`; refuted candidates go into the lens record's exclusion reasons.
5. **Capture knowledge** — write reusable facts to `work/drafts/knowledge-capture.md` per `knowledge-capture.md`.

## Default Lens Scope

**Single-repo default: Tier 1 + Tier 2 + META.** Tier 3 is skipped by default because it needs cross-repo profiles, boundary inventories, and counterpart evidence.

**Multi-repo default: Tier 1 + Tier 2 + Tier 3 + META.** Enable Tier 3 only when the audit scope covers at least two repositories. In 5+ repo audits, Tier 3 and META may use combined records per lens instead of repeated per-repo boilerplate.

**Lightweight strategy:** when the user explicitly asks for a quick scan, candidate pre-study, or a specific checklist, declare the enabled lens subset in `submit/quality/submission-scope.md`. `lens-coverage.md` is still required for final delivery; validate with `--lens-scope custom` for declared narrowed strategies. Use `--skip-lens-coverage` only for in-progress or resume runs.

## Split Reference Files

| File | Load when | Content |
|---|---|---|
| `lenses-tier1.md` | First pass for single-repo or multi-repo audits; useful for small repos | L1-L7, single-file / single-function surface lenses |
| `lenses-tier2.md` | Required by default | L8-L14, cross-file / cross-module lenses |
| `lenses-tier3.md` | Audit scope covers at least two repos | L15-L19, cross-repo / architecture-boundary lenses |
| `lenses-meta.md` | Phase 5 | META-1 / META-2 global contrast scans |

## Depth Tiers

| Tier | Scope | Lens IDs | Character |
|---|---|---|---|
| Tier 1 surface | single file / single function | L1-L7 | grep plus local code reading; defensive-code and technical-debt signals |
| Tier 2 cross-cut | cross-file / cross-module within one repo | L8-L14 | state, ordering, configuration, and lifecycle paths across modules |
| Tier 3 cross-repo | cross-repository / cross-service | L15-L19 | distributed contracts, ownership, release, migration, and consistency issues |

META lenses are not independent L20/L21 categories. They are contrast scans applied after other lenses: META-1 for intent drift, META-2 for failure-path test coverage.

## Lens Shape

Each lens file uses this compact structure:

```markdown
### L? <Name>

- **Hypothesis** — failure mode being hunted
- **Where to look** — grep patterns, LSP queries, profile tables, or call-graph nodes
- **Evidence pattern** — what evidence is strong enough for the Bug record
- **False-positive guard** — what would make the candidate not a Bug
- **Stop / Tiebreak** — when to stop; where to classify overlaps
- Example: one anonymous positive example
- Counterexample: one anonymous false-positive example
```

## Lens Application Records

Every audit writes `submit/quality/lens-coverage.md`. It stays under `quality/` because it is a coverage gate and honest-uncovered-area record; reusable repository knowledge stays under `knowledge/`.

Record every enabled lens:

- Single-repo default: L1-L14 + META.
- Multi-repo default: L1-L19 + META.
- User-declared lightweight strategy: the declared subset.

Each record has five required fields. Use section labels that match the final deliverable language (`--language zh` or `--language en` in the validator).

English template:

```markdown
### L13 Cache Consistency — Application Record

- Scanned Entry Points: src/cache/, src/api/users.py, src/api/orders.py
- Patterns: rg "cache\.(set|get|delete|invalidate)|@cached|redis\." src/
- Candidates: 4
- Exclusion Reasons:
  - src/cache/user_cache.py:23 invalidates user cache after write
  - src/api/orders.py:45 TTL is 30s and README declares that drift window
  - src/cache/lru.py:12 in-process only; no cross-process consistency issue
  - src/cache/session.py:8 read-only cache; writer is auth-service and recorded in repo profile
- Uncovered: CDN cache configuration is outside audit scope
```

Zero-candidate records are valid. Keep all five fields, for example `Candidates: 0` and `Exclusion Reasons: N/A (no candidates)`.

After each lens, capture reusable cognition separately from the 5-section coverage record: wrappers that explain false positives, sibling implementations that show safe patterns, uncovered areas, command sources, state owners, and cross-repo boundaries. Promote evidence-backed facts into `submit/knowledge/` before packaging.

## Relationship to Other References

| Reference | Relationship |
|---|---|
| `authenticity.md` | first constraint; coverage never justifies fabrication |
| `knowledge-capture.md` | scratch-to-submitted knowledge loop for exploration facts |
| `repo-profile.md` | required input for Tier 3 |
| `call-graph-conventions.md` | profile call-graph guardrails |
| `bug-schema.md` | Bug frontmatter `lens` enum comes from this system |
| `risk-taxonomy.md` | maps categories to primary lenses |
| `domain-profiles.md` | changes lens priority, not authenticity requirements |
| `language-ecosystems.md` | language-specific high-risk APIs for L4/L5/L6 |
| `evaluation.md` | Q6 checks lens coverage completeness |
| `architecture-review.md` | consumes Tier 3 application records |

## Pluggable Strategies

When the user specifies another strategy, such as OWASP ASVS, an internal checklist, or a lens subset:

- Record it as a free-form paragraph in `submit/quality/submission-scope.md`.
- Execute the declared strategy.
- Apply lens coverage requirements to the declared built-in subset.
- Validate final packages with `--lens-scope custom`; do not use `--skip-lens-coverage` for final delivery.
