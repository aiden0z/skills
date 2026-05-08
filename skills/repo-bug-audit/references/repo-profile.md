# Per-Repo Profile

Each audited repository gets one profile at `submit/knowledge/repo-profiles/<repo-name>.md`. The profile feeds Tier 3 lenses (L15-L19) and META-1. Without it, cross-repo exploration has no reliable boundary inventory.

File naming: use the repository short name. If the scope is written as `org/repo`, use `org__repo.md`. Only lowercase letters, numbers, dots, underscores, and hyphens are allowed; convert other characters to `-`.

> First constraint: see `authenticity.md`. Every path, line number, endpoint, function, and commit hash in the profile must be real. Prefer an empty set plus an explicit uncertainty marker over fabricated completeness.

## Contents

- When to Write
- Required Sections
- Section Guidance
- Writing Rules
- Lens Mapping

## When to Write

Write one profile for each repo after Phase 1 minimal knowledge collection. Even single-repo audits need a profile because lens records use it as the entry-point substrate.

If a repo has no cross-repo communication (for example, a small internal library or CLI tool), still write a profile. Boundary sections may be empty, but mark them explicitly as "No boundary of this type found in this repo."

## Required Sections

Use these canonical sections in English for skill-facing consistency. If the final package language is not English, translate section titles consistently while preserving the same order and meaning.

```markdown
# <repo-name> Profile

## Tech Stack
## Entry Points
## Outbound Calls
## Inbound Endpoints
## Shared Events
## Shared Storage
## Shared Config
## Intent Inputs
## Verification Sources
## Risk Surfaces
## Call Graph
## Findings and Candidates
## Known Uncovered Areas
```

## Section Guidance

### 1. Tech Stack

List language, framework, build tool, middleware, and test framework. Cite evidence from files such as `package.json`, `pom.xml`, `go.mod`, `requirements.txt`, `pyproject.toml`, or `Dockerfile`. Do not infer stack from filenames alone.

```markdown
- Language: Python 3.11 (`pyproject.toml`)
- Web framework: FastAPI 0.104 (`requirements.txt:15`)
- ORM: SQLAlchemy 2.x (`requirements.txt:22`)
- Queue: Celery + Redis (`requirements.txt:30`, `docker-compose.yml:42`)
- Tests: pytest (`pytest.ini`)
```

### 2. Entry Points

List all external ways to execute repo code:

- HTTP/gRPC routes: path → handler + `path:line`
- Message consumers: topic/queue → handler
- Scheduled jobs: cron expression → handler
- CLI commands: command → entry function
- WebSocket or long-lived connections

```markdown
### HTTP
- POST /api/v1/snapshots -> `src/api/snapshots.py:42` `create_snapshot`
- DELETE /api/v1/snapshots/{id} -> `src/api/snapshots.py:101` `delete_snapshot`

### Worker
- queue=cleanup -> `src/workers/cleanup.py:18` `process_cleanup`
```

### 3. Outbound Calls

Calls this repo makes to another service or repo. This feeds L15.

```markdown
| Target | Method | Call Site | Schema Source |
|---|---|---|---|
| user-service | HTTP GET /users/{id} | `src/clients/user.py:23` | No schema; fields inferred from `src/clients/user.py:30` |
| billing-service | gRPC ChargeOrder | `src/clients/billing.py:55` | `../shared-protos/billing.proto:12` |
```

`No schema` is a high-risk signal for L15, not a finding by itself.

### 4. Inbound Endpoints

Endpoints in this repo that are known or likely to be called by another repo. If the caller cannot be confirmed, write `caller unconfirmed`.

```markdown
| Endpoint | Known Callers | Contract Location |
|---|---|---|
| POST /api/v1/snapshots | release-cli, web-frontend | `docs/openapi.yaml` |
| internal: validate_token | auth-gateway (caller unconfirmed) | No contract document found |
```

### 5. Shared Events

Events or messages produced or consumed across service boundaries.

```markdown
### Produced
- snapshot.created -> Kafka topic `release.snapshot` (`src/events/publisher.py:40`)
  - schema: `src/events/schemas/snapshot_created.py:5`
  - fields: id, version, files[], created_at

### Consumed
- billing.charged <- Kafka topic `billing.events` (`src/workers/billing_listener.py:12`)
  - schema source: unconfirmed; consumer parses fields by name
```

### 6. Shared Storage

Storage directly read or written by this repo where at least one other repo also has access. This feeds L17.

```markdown
| Storage | Table / Key / Prefix | This Repo Access | Known Shared Parties |
|---|---|---|---|
| MySQL | release.snapshots | read + write | release-worker (write), analytics (read-only) |
| Redis | snapshot:lock:* | read + write + TTL | release-worker (write) |
| S3 | s3://release-bucket/snapshots/ | write | analytics (read), release-cli (read) |
```

If shared parties cannot be confirmed, write `known shared parties: unconfirmed`.

### 7. Shared Config

Config, feature flags, and secret names that are shared across repos or should carry the same meaning.

```markdown
- `RELEASE_LOCK_TIMEOUT`: this repo defaults to 30s (`config/settings.py:18`); release-worker default is unconfirmed.
- feature flag `enable_dual_write`: checked in `src/release/snapshot.py:200`; release-worker usage unconfirmed.
```

### 8. Intent Inputs

Inputs for META-1 intent-vs-implementation drift. List only sources that actually exist:

```markdown
- `README.md`: repo purpose and core behavior
- `docs/architecture/snapshot-design.md`: snapshot design from early 2024
- `docs/adrs/0003-use-redis-for-locking.md`: lock design ADR
- Important commit messages:
  - abc1234 "fix: prevent snapshot drift" (2024-03)
  - def5678 "refactor: extract release service" (2024-06)
- Key PR: #445 snapshot lock redesign
```

If README/docs/issues/commit messages are all absent, write `Intent Inputs: inferred`, cite the inference source (for example package metadata, entry names, CLI help, or test names), and mark confidence low. Never invent document names for completeness.

### 9. Verification Sources

List confirmed commands and the files that make them credible. This section feeds Bug records' `Suggested Verification Commands` and META-2.

```markdown
| Command / Source | Evidence | Coverage |
|---|---|---|
| `npm test` | `package.json:scripts.test` | broad unit suite |
| `make test-storage` | `Makefile:test-storage` | storage module regression |
| unconfirmed | no module-specific test command found for `src/snapshot/` | command gap for snapshot Bugs |
```

Do not invent commands. If only a generic command is visible, say it is generic.

### 10. Risk Surfaces

Summarize state owners, lifecycle transitions, and resource boundaries that lens passes should revisit.

```markdown
| Resource / State | Owner Module | Lifecycle / Failure Surface | Evidence |
|---|---|---|---|
| snapshot record | `src/snapshot/service.py` | create -> upload -> publish -> cleanup | `src/snapshot/service.py:42` |
| distributed lock | `src/locks/redis_lock.py` | acquire / renew / release / expire | `src/locks/redis_lock.py:18` |
```

Keep this compact. It should help the next agent choose paths, not become a full design document.

### 11. Call Graph

Follow `call-graph-conventions.md`. Default expectation: at least one Mermaid graph. Complex repos may split graphs by use case or subsystem.

Small-repo exemption: if the repo has no more than 10 source/config files and a text description is clearer than a diagram, omit Mermaid and write `Call Graph Exemption: <=10-file small repo; text summary is clearer.` Then provide 3-8 lines covering entry points, core functions, and uncovered areas. The validator warns when a profile has neither Mermaid nor the exemption marker.

### 12. Findings and Candidates

After Bug records are written, link the repo profile back to submitted Bugs and important candidate leads.

```markdown
### Submitted Bugs
- `BUG-0003`: snapshot cleanup loses retry state after partial upload failure.

### Candidate Leads
- `work/candidates/snapshot-cache-drift.md`: parked because caller ownership is unconfirmed.
```

Use Bug IDs, candidate filenames, and one-line failure modes. Do not duplicate full Bug records here.

### 13. Known Uncovered Areas

List areas the agent knows exist but did not inspect deeply:

```markdown
- `src/legacy/`: 500+ lines with separate entry points, not included in call graph.
- `tests/conftest.py`: fixture monkeypatching may hide additional call paths.
- `src/native/_fast.so`: compiled extension without source.
```

This is an honesty marker, not an apology.

## Writing Rules

- Verify every `path:line` before writing it.
- Use `unconfirmed` for unknown schema sources, callers, ownership, or intent inputs.
- Keep sections compact; 5 real tech-stack lines beat 30 decorative lines.
- Keep each profile under 800 lines. Split by subsystem only when needed.
- Do not force a meaningless Mermaid diagram for a <=10-file utility repo; use the exemption marker and a concise text summary.
- Update `Verification Sources`, `Risk Surfaces`, and `Findings and Candidates` after Bug records are written; Phase 1 profiles are allowed to start thin, final profiles are not.

## Lens Mapping

| Profile Section | Feeds |
|---|---|
| Outbound Calls | L15 contract drift |
| Shared Events | L15, L18 retry/idempotency |
| Shared Storage | L17 shared-state ownership |
| Shared Config | L12 config drift, L17 |
| Inbound + Outbound | L16 saga completeness, L19 release safety |
| Intent Inputs | META-1 intent drift |
| Verification Sources | META-2 and Bug verification commands |
| Risk Surfaces | L8-L14 path selection and fix handoff |
| Call Graph | Tier 2 entry-point substrate |
| Findings and Candidates | final handoff and resume audits |
| Known Uncovered Areas | META-2 and future audit handoff |
