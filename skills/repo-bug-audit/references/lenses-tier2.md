# Tier 2 Cross-Cut Lenses

Tier 2 lenses trace state, ordering, lifecycle, configuration, and observability across files or modules within one repository.

### L8 State Machine Consistency

- **Hypothesis**: every write to a shared state/status field is a legal transition; no skipped, regressed, or conflicting transition exists.
- **Where to look**: enum fields named `status`, `state`, `phase`; all writes via `set_status`, `update(status=...)`, assignments, migrations.
- **Evidence pattern**: direct `pending -> done` jump skips required `processing`; terminal state returns to non-terminal state; two writers race a transition.
- **False-positive guard**: state-machine library, DB constraint, trigger, or single transition wrapper.
- **Stop / Tiebreak**: cover all writes to the field. Legal transition problem is L8; concurrent state write is L9.
- Example: refund rollback path moves order `refunded -> paid` without audit state.
- Counterexample: admin-only transition is explicitly documented and guarded.

### L9 Concurrency and Ordering

- **Hypothesis**: shared resources are accessed under correct locks, transactions, or atomic operations; check-then-act is atomic.
- **Where to look**: globals, singletons, caches, DB rows, `SELECT FOR UPDATE`, Redis `GET` then `SET`, cron reentry, async cancellation.
- **Evidence pattern**: `if not exists: create` outside transaction/lock; multi-worker consumer lacks idempotency or distributed lock.
- **False-positive guard**: unique constraint, atomic SQL update, Redis SETNX, distributed lock wrapper, queue visibility timeout.
- **Stop / Tiebreak**: cover reads and writes for the shared resource. Single-process race is L9; cross-repo invariant break is L17.
- Example: balance check and decrement run as separate operations and can overspend.
- Counterexample: SQL `UPDATE balance = balance - X WHERE balance >= X` is atomic.

### L10 Failure Recovery and Compensation

- **Hypothesis**: every multi-step operation has rollback, compensation, durable retry, or manual handoff for partial success.
- **Where to look**: `step1(); step2(); step3()`, external side effects outside DB transactions, retry exhaustion, async task terminal states.
- **Evidence pattern**: step2 failure leaves step1 side effect; retry exhaustion leaves `processing` forever; no DLQ or reconciliation path.
- **False-positive guard**: saga/outbox/TCC, idempotent reconciler, workflow engine, durable terminal states.
- **Stop / Tiebreak**: cover the operation chain. Single-repo compensation is L10; cross-repo saga is L16.
- Example: payment succeeds but fulfillment API fails, leaving order permanently paid and unfulfilled.
- Counterexample: outbox table plus reconciler retries and marks terminal failure.

### L11 Data Lifecycle

- **Hypothesis**: create -> active -> archive -> delete lifecycle is explicit; historical, soft-deleted, and migrating data is read correctly.
- **Where to look**: DELETE, `deleted_at`, TTL, archive jobs, migrations, read filters, dual-write/dual-read windows.
- **Evidence pattern**: list API returns soft-deleted rows; GC deletes referenced records; migration dual-writes but reads from only one side.
- **False-positive guard**: base query filters deleted rows; migration includes dual-read; admin audit endpoint intentionally includes deleted data.
- **Stop / Tiebreak**: cover CRUD for the data class. Single-repo lifecycle is L11; shared data ownership is L17.
- Example: user deletion sets `deleted_at`, but normal list endpoint still returns the user.
- Counterexample: endpoint is admin audit and intentionally returns all records.

### L12 Configuration and Environment Drift

- **Hypothesis**: dev/staging/prod config has compatible semantics; defaults are safe; missing secrets fail closed.
- **Where to look**: `os.environ.get(KEY, default)`, env branches, feature flags, config schema, missing-key behavior.
- **Evidence pattern**: default disables auth; missing secret skips encryption; prod-only validation cannot be exercised in dev/test.
- **False-positive guard**: startup schema validation, fail-fast settings loader, reviewed feature-flag defaults.
- **Stop / Tiebreak**: cover config reads. Single-repo config is L12; same-name cross-repo config drift is L17.
- Example: `AUTH_ENABLED` defaults to false when env var is absent.
- Counterexample: production startup requires the value and exits if absent.

### L13 Cache Consistency

- **Hypothesis**: after writes, every cache layer is invalidated or updated with correct dimensions such as tenant and user.
- **Where to look**: `cache.set`, `cache.get`, `cache.delete`, decorators, Redis keys, CDN rules, ORM caches.
- **Evidence pattern**: write path does not invalidate related key; key omits tenant/user; only one of multiple cache layers is updated.
- **False-positive guard**: write-through cache, centralized invalidator, short documented TTL drift, request-scoped cache only.
- **Stop / Tiebreak**: cover write and read paths for the data class. Single-repo cache is L13; shared cache ownership is L17.
- Example: user rename writes DB but `GET /users/me` returns stale CDN response.
- Counterexample: 30s drift is documented and acceptable for that endpoint.

### L14 Critical-Path Observability

- **Hypothesis**: destructive, financial, privilege, and recovery operations have audit trails; metrics and alerts match real success/failure states.
- **Where to look**: delete/refund/privilege paths, metric increments relative to try/except, alert queries, PromQL/SQL filters.
- **Evidence pattern**: delete has no audit log; success metric increments before operation succeeds; alert filters a state value that code never writes.
- **False-positive guard**: middleware audit log, metric after success, alert tests, centralized event pipeline.
- **Stop / Tiebreak**: cover critical path plus monitoring config. Observability gaps discovered during other lenses can be recorded under L14.
- Example: admin deletes user with no audit event and no actor recorded.
- Counterexample: framework middleware records actor/action/resource for every admin route.
