# Knowledge Base

Use this when mapping repositories, updating `submit/knowledge/`, or checking the final package.

## Contents

- Operating Model
- Exploration Knowledge Capture
- Minimal Knowledge Map
- Final Submitted Knowledge
- Completeness Check

## Operating Model

Knowledge and Bug discovery are iterative:

1. Build a minimal knowledge map.
2. Use it to choose risky paths.
3. Capture reusable exploration facts as knowledge atoms.
4. Promote evidence-backed candidates to Bugs.
5. Promote evidence-backed atoms into repo knowledge.
6. Repeat until the requested depth or package target is reached.

Do not wait for a complete knowledge base before hunting Bugs. Do not submit a package with only shallow inventory notes.

## Exploration Knowledge Capture

Read `knowledge-capture.md` during Phase 2. Use `work/drafts/knowledge-capture.md` as the scratch ledger for facts learned during search, refutation, and verification.

Capture facts such as:

- Entry points discovered while tracing candidates.
- Boundary calls, event schemas, shared storage, shared config, and cross-repo contracts.
- State owners, lifecycle transitions, locks, caches, queues, terminal states, and reconciliation paths.
- Sibling implementations that explain false positives.
- Verification command sources and command gaps.
- Uncovered areas that constrain confidence.

Before packaging, promote evidence-backed atoms into `submit/knowledge/` and leave speculative atoms in `work/`.

## Minimal Knowledge Map

Before writing many Bugs, collect enough facts to guide the first search:

- Repository list, branch context, language, framework, and build system.
- Language ecosystem evidence from `language-ecosystems.md`: package/build files, test command sources, framework conventions, and module boundaries.
- Main entry points: API, task, worker, CLI, scheduler, UI route, SDK public API.
- External systems: database, cache, queue, cloud API, storage backend, network controller, shell, device, auth, billing, monitoring.
- Primary domain profile from `domain-profiles.md`.
- Resource lifecycles and state owners.
- Async or long-running workflows.
- Security boundary and tenant/user boundary.
- First-pass cross-repo relationships.
- Initial high-risk paths and unknowns.

This map can live in `work/drafts/` while incomplete. Move stable knowledge into `submit/knowledge/`.

## Final Submitted Knowledge

The final `submit/knowledge/` should let another Agent continue analysis or start fixes without rescanning basics.

For repo-group targets, completeness starts from the frozen roster in `work/scanner-output/repo-inventory.json`: every discovered repo should have a profile, even when it produced zero submitted Bugs.

Required when relevant:

- `knowledge/system-overview.md`
- `knowledge/repo-relationship-map.md`
- `knowledge/risk-paths.md`
- `knowledge/architecture-design-review.md`
- `knowledge/repo-profiles/*.md`

### `system-overview.md`

Include:

- Analysis scope and repository responsibilities.
- Branch/commit evidence summary or pointer to `quality/repository-versions.md`.
- Runtime shape: API, workers, schedulers, UI, SDK, services.
- Language/framework ecosystems and where verification commands come from.
- Core workflows and resource lifecycles.
- Data stores, external systems, and state owners.
- Auth, tenant boundary, async jobs, and recovery surfaces.
- Known unknowns that affect confidence.

### `repo-relationship-map.md`

Include:

- Repo-to-repo dependencies.
- API, event, task, package, UI-to-backend, or SDK relationships.
- External system relationships.
- Source-of-truth ownership for key resources.
- Cross-repo call chains tied to Bug families.
- Contracts a fix should preserve when visible in code: API fields, state enums, resource lifecycle owner, async job terminal states, external IDs, and compatibility expectations.

### `risk-paths.md`

Include:

- High-risk lifecycle paths and failure propagation.
- Stability, data integrity, cross-system consistency, recovery, security, storage/network performance, observability, deployment/runtime, and resource-leak paths.
- P1/P2 issue families and the paths that produce them.
- Candidate areas that remain outside submitted findings.

### `architecture-design-review.md`

Include:

- Repeated architecture risk signals.
- Evidence from code shape, file/module ownership, cross-system writes, and repeated Bug families.
- Mapping from architecture signals to concrete Bug IDs.
- Discovery wording, not command-style design principles.

### `repo-profiles/*.md`

One file per audited repo. Include:

- Repo responsibility and primary domain profile.
- Key modules, entry points, background jobs, and external dependencies.
- Language ecosystem, build metadata, and confirmed or missing test command sources.
- Main resource lifecycles or user workflows.
- Boundary inventories: outbound calls, inbound endpoints, shared events, shared storage, shared config, execution boundaries, serialization/contracts, and deployment/runtime assumptions.
- Intent inputs for META-1 and verification sources for META-2.
- Risk surfaces: state owners, consistency boundaries, lifecycle transitions, execution/serialization boundaries, recovery surfaces, and resource boundaries that future lens passes should revisit.
- Submitted Bug families affecting the repo.
- Important candidates, uncovered areas, and unknowns that should guide later passes.

## Completeness Check

Before packaging:

- Knowledge reflects submitted Bugs, not only initial inventory.
- Exploration knowledge atoms have been promoted, parked, or removed.
- Every audited repo has a profile with boundary inventories, verification sources, risk surfaces, Bug links, and uncovered areas.
- Repeated Bug families are summarized once and linked to concrete Bug IDs.
- Cross-repo relationships explain the risk paths used in the findings.
- Empty or repetitive optional files are removed.
- Unknowns and assumptions are explicit in `quality/submission-scope.md` or the relevant knowledge file.
- The wording follows `writing-style.md`.
