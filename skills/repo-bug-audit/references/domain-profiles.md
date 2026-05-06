# Domain Profiles

Choose one primary profile per audit and optional secondary profiles for mixed repositories. The profile changes search focus and sorting emphasis, not the evidence standard.

## Contents

- `infra`
- `backend`
- `frontend`
- `sdk`
- `mobile`
- `generic`

## `infra`

Focus:

- Data integrity across local database, cloud control plane, storage backend, network backend, and virtualization platform.
- Recovery after partial failure, outage, retry exhaustion, operator interruption, or node/service restart.
- Resource leaks: attachments, sessions, volumes, ports, routes, devices, locks, tasks, threads, and temporary files.
- Storage/network performance on control-plane hot paths.
- Control-plane safety, tenant boundary, destructive operation ordering, and state reconciliation.

Architecture lens:

- Use cases should expose clear resource lifecycle steps: create, attach, detach, migrate, snapshot, backup, restore, delete, reconcile.
- Cross-system workflows should have durable state, idempotency, retry budget, terminal state, compensation path, or manual handoff.
- External systems should be behind adapters with consistent timeout, retry, TLS, auth, audit, and error translation.
- State reconciliation should compare local DB, cache, OpenStack/cloud API, storage backend, network backend, and billing/monitoring state.
- Failure domains should stay isolated; one backend slowness or drift should not block unrelated control-plane operations.

High-priority signals:

- Backend success followed by local failure without compensation.
- Local deletion before remote confirmation.
- Long task without durable state, retry budget, or terminal status.
- Cross-system state drift that affects compute, storage, network, identity, billing, or deployment recovery.

## `backend`

Focus:

- Transaction boundaries, idempotency, async jobs, retries, compensation, and external dependency failure.
- Authorization, authentication, tenant/user boundaries, and sensitive data handling.
- Cache/index consistency, event ordering, and database write ordering.
- Error mapping and operational observability.

Architecture lens:

- Controllers should stay thin; use cases/application services should own business orchestration.
- Domain rules should not depend directly on ORM, HTTP client, SDK, queue, cache, or framework globals.
- Local DB changes and async events should avoid divergence through Outbox-style or equivalent durable handoff.
- Consumers should handle duplicate messages through Inbox-style or equivalent idempotency records.
- Bounded contexts should not mutate each other's tables or internal models without an explicit API or anti-corruption layer.

High-priority signals:

- DB write and remote call mixed without clear rollback or recovery.
- Duplicate job execution or check-then-act race.
- Request path can hang because external dependency has no timeout or bounded retry.

## `frontend`

Focus:

- Permission display and action gating mismatch.
- State confusion between UI cache, URL state, store state, and backend truth.
- Sensitive information exposure in DOM, logs, URLs, local storage, or exported files.
- Irreversible actions without confirmation, rollback feedback, or refreshed state.
- Error recovery, stale data after mutation, and unavailable core interactions.

Architecture lens:

- UI state should have a clear owner: server state, route state, form state, local component state, or persistent client state.
- Permission display should not be treated as authorization; backend authorization remains the source of truth.
- Mutation flows should define loading, disabled, optimistic update, rollback, and refetch behavior.
- Shared API clients should standardize error mapping, auth refresh, timeout, cancellation, and sensitive-field filtering.
- Error boundaries and fallback states should keep core workflows recoverable after partial UI failure.

High-priority signals:

- UI shows an operation as successful while backend failure remains hidden.
- Unauthorized action is visible or executable because frontend and backend assumptions diverge.
- User can repeat a destructive action because loading/disabled state is not enforced.

## `sdk`

Focus:

- API compatibility, version behavior, error type stability, and backward-compatible defaults.
- Retry semantics, timeout propagation, cancellation, and idempotency keys.
- Resource release for clients, streams, sockets, files, subprocesses, and background tasks.
- Thread safety, async safety, and shared mutable state.

Architecture lens:

- Public API contracts should remain stable across minor releases, especially error types and default behavior.
- Retry/circuit-breaker behavior should not change the meaning of non-idempotent operations.
- Transport adapters should isolate HTTP/gRPC/file/process details from higher-level client behavior.
- Cancellation and timeout should propagate through all layers instead of stopping at the public API boundary.
- Shared clients should document and enforce thread-safety or async-safety assumptions.

High-priority signals:

- Retry changes operation meaning or duplicates a non-idempotent call.
- Error type changes break callers' recovery logic.
- Client lifecycle leaks resources under common failure paths.

## `mobile`

Focus:

- Weak network, offline recovery, retry-after-resume, and duplicate submission.
- Permission prompts, privacy boundaries, secure local storage, and token lifecycle.
- Crash risks in lifecycle transitions, background tasks, notifications, and media/file handling.
- State reconciliation after app restart, background kill, or account switch.

Architecture lens:

- Local state should distinguish draft, queued, synced, failed, and conflict states.
- Background jobs should be idempotent and safe across app restart, OS kill, and network changes.
- Permission-dependent features should handle denial, revocation, and partial grant without corrupting flow state.
- Local storage should separate sensitive credentials, user data, cache, and recoverable drafts.
- Sync code should define conflict resolution and avoid silent overwrite.

High-priority signals:

- Offline or resume path can lose user data.
- Permission denial leaves the app in a broken or misleading state.
- Background task repeats destructive or payment-like operations.

## `generic`

Focus:

- Core workflow correctness, data safety, security boundary, recovery cost, performance degradation, and maintainability risk.
- Use this when the repo type is unclear, then switch profiles once the architecture is understood.

Architecture lens:

- Start with use cases, state owners, external dependencies, async work, security boundary, and failure recovery.
- Escalate to a specific profile when the dominant risk domain becomes clear.
