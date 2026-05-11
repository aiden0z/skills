# Issue Family Coverage

Use this reference for deep, full, repo-group, security/auth, or high-recall audits. It exists so first-run audits do not depend on historical packages for recall.

## Purpose

`submit/quality/issue-family-coverage.md` is a fresh current-source coverage matrix. It shows which broad Bug families were actively explored before final promotion, even when no older audit package exists.

Historical packages may add comparison rows later, but they must not be the source of this matrix. Search hits are also not the only source: fill the matrix from both AI-led code understanding and search-led seed triage.

## Required Families

Cover every family below for repo-group/deep/high-recall final handoffs:

| Family | Scope |
|---|---|
| `auth-authorization` | Authentication checks, authorization enforcement, tenant/project isolation |
| `secrets-config` | Credential storage, config precedence, encryption key management |
| `execution-sandbox` | Code execution boundaries, dynamic code loading, plugin systems |
| `deserialization-ipc` | Data deserialization, inter-process communication, parser safety |
| `file-path-storage` | File operations, path construction, upload/download handling, object storage |
| `network-ssrf` | Outbound network calls, URL construction from input, internal service reachability |
| `tls-transport` | Certificate validation, transport encryption, proxy configuration |
| `frontend-rendering` | User content rendered as UI, browser storage, iframe embedding |
| `state-data-integrity` | Transaction boundaries, data consistency, concurrent mutation handling |
| `async-lifecycle-recovery` | Async job lifecycle, worker recovery, startup/shutdown sequence |
| `resource-concurrency` | Resource pooling, cleanup guarantees, concurrency primitives |
| `deployment-supply-chain` | Container security, dependency management, build pipeline integrity |

## Row Format

Use one row per family. Keep rows short but evidence-bearing.

| Family | Fresh Sources | Outcome | Evidence |
|---|---|---|---|
| `execution-sandbox` | model-led route/worker walk + `rg "exec\\(|eval\\(|subprocess|ProcessBuilder" <repo roots>` | promoted + parked | `agent/...:42` promoted as `BUG-0005`; `tools/...:88` parked, missing reachable route proof |

Allowed outcomes:

- `promoted`: one or more submitted Bugs.
- `merged`: family represented by a broader submitted Bug.
- `parked`: credible leads exist but missed one Bug schema gate.
- `refuted`: reviewed fresh hits and found concrete false-positive guards.
- `no-hit`: fresh scan found no credible current-source hits.
- `not-applicable` / `out-of-scope`: explain why the family does not apply to the requested scope.

## Quality Bar

- Cite at least one code path anchor for `promoted`, `merged`, `parked`, or `refuted`.
- For `no-hit`, name the search or surface that produced no credible hit.
- Do not write "covered by general scan" without a family-specific outcome.
- Do not write only scanner commands. For large/high-risk repos, each family should also mention at least one behavioral surface when present: route, worker, CLI, service, state owner, side-effect boundary, deployment template, or frontend render path.
- Do not wait for historical baseline review to fill this file. Create it from the fresh scan first, then append a historical comparison note when applicable.
