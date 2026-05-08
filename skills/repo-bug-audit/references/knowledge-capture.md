# Knowledge Capture

Use this during exploration, not only at the end. The goal is to reuse cognition produced while reading code, running lenses, refuting candidates, and comparing sibling implementations.

## Capture Loop

1. **Notice** a reusable fact while scanning or verifying.
2. **Record** it as a short knowledge atom in `work/drafts/knowledge-capture.md`.
3. **Attach evidence**: real path, symbol, command source, endpoint, config, schema, or Bug/candidate ID.
4. **Promote** evidence-backed atoms into `submit/knowledge/`.
5. **Discard or keep in work/** atoms that remain speculative.

Do not copy raw exploration diaries into `submit/`. Submit concise facts with evidence.

## Knowledge Atom Format

```markdown
### <repo> / <topic>

- Type: entry-point | boundary | state-owner | lifecycle | invariant | false-positive-guard | verification-source | cross-repo-contract | risk-path | uncovered-area
- Evidence: `path/to/file.ext:line` or `command source`
- Learned: <one reusable fact>
- Reuse Target: repo-profile | system-overview | repo-relationship-map | risk-paths | architecture-design-review | lens-coverage | candidate
- Status: promote | parked | refuted
```

Keep atoms small. One atom should capture one reusable fact.

## What To Capture

- Entry points found while tracing a candidate.
- Shared wrappers, adapters, validators, transactions, retry helpers, or cleanup hooks that explain false positives.
- State owners, lifecycle transitions, terminal states, idempotency keys, locks, caches, queues, and reconciliation paths.
- Cross-repo calls, event schemas, shared storage, shared config, API fields, state enums, and compatibility assumptions.
- Verification command sources and command gaps.
- Sibling implementations that handle the same scenario correctly.
- Uncovered paths that constrain confidence.
- Repeated issue-family patterns that should become architecture risk signals.

## Promotion Map

| Atom type | Promote to |
|---|---|
| entry-point | `repo-profiles/<repo>.md` Entry Points and Call Graph |
| boundary / cross-repo-contract | repo profile boundary sections and `repo-relationship-map.md` |
| state-owner / lifecycle | repo profile Risk Surfaces and `risk-paths.md` |
| invariant / false-positive-guard | lens exclusion reasons, Bug false-positive review, or architecture review |
| verification-source | repo profile Verification Sources and Bug suggested verification commands |
| uncovered-area | repo profile Known Uncovered Areas and `submission-scope.md` |
| repeated pattern | `architecture-design-review.md` with Bug IDs or code anchors |

## Promotion Rules

- Promote only facts with evidence. Use `unconfirmed` for missing ownership, callers, schema sources, or command coverage.
- If an atom explains why a candidate is not a Bug, keep the false-positive guard; it is reusable knowledge.
- If an atom comes from a Bug, link the Bug ID from the promoted knowledge.
- If an atom comes from a parked lead, link the candidate file instead of implying a confirmed Bug.
- Remove duplicate atoms after promotion; keep `work/drafts/knowledge-capture.md` as a working ledger, not a second knowledge base.
