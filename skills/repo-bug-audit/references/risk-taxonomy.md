# Risk Taxonomy

## Priority

Use P1-P4 as Bug impact priority. Do not add SLA fields to Bug records.
For non-infra repositories, map the same priorities to the product's core workflow, data safety, security boundary, recovery cost, and customer impact.
Use `domain-profiles.md` to tune search focus for infra, backend, frontend, SDK, mobile, or generic repositories.

| Priority | Definition | Infra examples |
|---|---|---|
| P1 | Core business interruption, major data/security/fund risk, or high recovery cost if not fixed quickly. | Data cannot recover after outage; tenant/account isolation bypass; destructive backend state drift; high-privilege command injection. |
| P2 | Core operation degraded or large non-core impact; serious stability or business-risk potential. | Core workflow fails under common conditions; external resource cleanup leaks; backend state drifts; task hangs without recovery. |
| P3 | Limited user or non-core scenario impact; function mostly usable with workaround. | Intermittent notification delay; observability mismatch; narrow edge case with bounded blast radius. |
| P4 | Cosmetic, wording, low-impact edge case, or no clear business loss. | Label typo, minor copy issue, display-only inconsistency. |

## Confidence

| Confidence | Meaning | Submission rule |
|---|---|---|
| high | Code evidence, trigger path, failure mode, and impact are clear. | Eligible for submitted findings. |
| medium | Strong suspicion but depends on runtime/config assumptions. | Keep if important, mark clearly, or move to `work/candidates/`. |
| low | Pattern-only lead without enough proof. | Do not submit as confirmed Bug; keep in `work/candidates/`. |

## Fix Risk

`fix_risk` describes the expected change risk for a later fix, not the Bug impact priority.

| Fix risk | Meaning |
|---|---|
| low | Localized change, clear module boundary, limited blast radius. |
| medium | Shared code, async state, compatibility behavior, or multiple call paths may be affected. |
| high | Cross-repo contract, data migration, storage/network/control-plane lifecycle, or security boundary may be affected. |
| unknown | Bug evidence is enough to submit, but fix impact cannot be assessed from static evidence. |

## Categories

Use one primary category and optional secondary tags.

- `data-integrity`: local/remote state split, premature deletion, lost update, inconsistent source of truth.
- `availability`: request hang, worker starvation, unavailable core operation, missing timeout.
- `recovery`: no retry, no compensation, no manual handoff, unrecoverable partial success.
- `resource-leak`: leaked volume connection, orphaned resource, file/socket/thread/process leak.
- `security`: authz/authn, tenant boundary, injection, path traversal, unsafe deserialization, secrets, TLS disabled.
- `consistency`: cross-service drift, stale cache/index, async status mismatch.
- `storage-performance`: unbounded storage calls, sync hot path, inefficient volume/snapshot/backup operations.
- `network-performance`: unbounded network calls, control-plane blocking network dependency, slow route/device sync.
- `observability`: wrong status/log/action label, masked failure, missing audit trail.
- `concurrency`: race, lock omission, check-then-act, duplicate job execution.
- `config-safety`: insecure defaults, fail-open config, hardcoded environment assumptions.

## Infra Domains

Tag infra impact with one or more: `control-plane`, `storage-performance`, `network-performance`, `compute-lifecycle`, `security`, `recovery`, `availability`, `data-integrity`, `resource-leak`, `cross-repo`.

## Sorting

Sort submitted Bugs by:

1. Priority: P1 -> P2 -> P3 -> P4.
2. Confidence: high -> medium -> low.
3. Infra stability: data integrity, recovery, availability, resource leak, storage/network performance first.
4. Blast radius: cross-repo/control-plane before isolated module.
5. Evidence strength and fixability.
