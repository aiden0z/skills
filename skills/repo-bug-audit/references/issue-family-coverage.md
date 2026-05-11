# Issue Family Coverage

Use this reference for deep, full, repo-group, security/auth, or high-recall audits. It exists so first-run audits keep a visible recall funnel without depending on historical packages.

## Purpose

`submit/quality/issue-family-coverage.md` is a fresh current-source coverage matrix. It shows which broad Bug families were actively explored before final promotion, even when no older audit package exists.

Historical packages may add comparison rows later, but they must not be the source of this matrix. Search hits are also not the only source: fill the matrix from AI-led code understanding, agent reports, gap analysis, manual call-chain tracing, and supplemental scan results.

## Family Selection

Do not use a fixed built-in family list. Choose families from the current audit:

- risk surfaces found while reading the code;
- gaps named by repo agents;
- recurring candidate themes across repos;
- user-requested focus areas;
- supplemental scan categories generated after initial exploration.

The family set is a recall ledger, not a checklist. A small repo may need only a few rows. A deep multi-repo audit should normally have enough rows to explain the important promoted, parked, refuted, no-hit, not-applicable, and out-of-scope paths.

## Row Format

Use one row per LLM-declared family. Keep rows short but evidence-bearing.

| Family | Fresh Sources | Outcome | Evidence |
|---|---|---|---|
| `<family-id>` | agent report + call-chain trace + supplemental scan category | promoted + parked | `repo/path/file.ext:42` promoted as `BUG-0005`; `repo/other.ext:88` parked, missing reachable trigger proof |

Allowed outcomes:

- `promoted`: one or more submitted Bugs.
- `merged`: family represented by a broader submitted Bug.
- `parked`: credible leads exist but missed one Bug schema gate.
- `refuted`: reviewed fresh hits and found concrete false-positive guards.
- `no-hit`: fresh scan or fresh surface review found no credible current-source hits.
- `not-applicable` / `out-of-scope`: explain why the family does not apply to the requested scope.

## Quality Bar

- Cite at least one code path anchor for `promoted`, `merged`, `parked`, or `refuted`.
- For `no-hit`, name the search, source surface, or call-chain family that produced no credible hit.
- Do not write "covered by general scan" without a family-specific outcome.
- Do not write only scanner commands. For large/high-risk repos, each family should also mention at least one behavioral surface when present: route, worker, CLI, service, state owner, side-effect boundary, deployment template, or frontend render path.
- Do not wait for historical baseline review to fill this file. Create it from the fresh scan first, then append a historical comparison note when applicable.
