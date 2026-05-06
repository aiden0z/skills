# Knowledge Base

Use this when mapping repositories, updating `submit/knowledge/`, or checking the final package.

## Contents

- Operating Model
- Minimal Knowledge Map
- Final Submitted Knowledge
- Completeness Check

## Operating Model

Knowledge and Bug discovery are iterative:

1. Build a minimal knowledge map.
2. Use it to choose risky paths.
3. Promote evidence-backed candidates to Bugs.
4. Feed Bug evidence back into repo knowledge.
5. Repeat until the requested depth or package target is reached.

Do not wait for a complete knowledge base before hunting Bugs. Do not submit a package with only shallow inventory notes.

## Minimal Knowledge Map

Before writing many Bugs, collect enough facts to guide the first search:

- Repository list, branch context, language, framework, and build system.
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

### `risk-paths.md`

Include:

- High-risk lifecycle paths and failure propagation.
- Stability, data integrity, recovery, security, storage/network performance, and resource-leak paths.
- P1/P2 issue families and the paths that produce them.
- Candidate areas that remain outside submitted findings.

### `architecture-design-review.md`

Include:

- Repeated architecture risk signals.
- Evidence from code shape, file/module ownership, cross-system writes, and repeated Bug families.
- Mapping from architecture signals to concrete Bug IDs.
- Discovery wording, not command-style design principles.

### `repo-profiles/*.md`

One file per important repo. Include:

- Repo responsibility and primary domain profile.
- Key modules, entry points, background jobs, and external dependencies.
- Main resource lifecycles or user workflows.
- Submitted Bug families affecting the repo.
- Important candidates or unknowns that should guide later passes.

## Completeness Check

Before packaging:

- Knowledge reflects submitted Bugs, not only initial inventory.
- Repeated Bug families are summarized once and linked to concrete Bug IDs.
- Cross-repo relationships explain the risk paths used in the findings.
- Empty or repetitive optional files are removed.
- Unknowns and assumptions are explicit in `quality/submission-scope.md` or the relevant knowledge file.
- The wording follows `writing-style.md`.
