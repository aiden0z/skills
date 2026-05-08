# Tier 3 Cross-Repo / Architecture Lenses

Tier 3 lenses require the five boundary sections in `repo-profile.md`: Outbound Calls, Inbound Endpoints, Shared Events, Shared Storage, and Shared Config. Do not run Tier 3 without profiles.

### L15 Contract Drift

- **Hypothesis**: caller and callee agree on field names, types, optionality, enum values, semantics, and version compatibility.
- **Where to look**: Outbound Calls in one profile plus Inbound Endpoints in the counterpart profile; event producer schema vs consumer parser; OpenAPI/proto vs code-derived fields.
- **Evidence pattern**: producer and consumer use different field names; producer adds a non-optional field before consumers update; consumer has no default for new enum values.
- **False-positive guard**: protobuf compatibility lint, contract tests, gateway field rewrite, version field plus dual-version compatibility window.
- **Stop / Tiebreak**: cover profile-listed cross-repo boundaries. Representation/encoding issue is L6; semantic contract drift is L15.
- Example: order-service renames `paid_at` to `paid_time`; billing-service still reads `paid_at`.
- Counterexample: gateway maps old and new field names during rollout.

### L16 Distributed Transaction / Saga Completeness

- **Hypothesis**: cross-repo multi-step operations can recover from any step failing; side effects either complete, compensate, or reach a visible terminal state.
- **Where to look**: entry points that call multiple external services; event-driven chains; saga orchestrators; outbox/inbox tables.
- **Evidence pattern**: A calls B successfully, C fails, and B's side effect is never compensated; idempotency key missing between steps; orchestrator crash has no resume.
- **False-positive guard**: Temporal/Cadence/Camunda, outbox plus reconciler, durable step state, manual handoff path.
- **Stop / Tiebreak**: cover each cross-service multi-step chain. Single-repo multi-step recovery is L10; cross-repo chain is L16.
- Example: inventory is reserved, payment fails, and inventory is never released.
- Counterexample: reconciler scans incomplete steps every five minutes and compensates.

### L17 Shared-State Ownership

- **Hypothesis**: shared storage or config has one owner for invariants; other repos do not bypass that owner and break invariants.
- **Where to look**: Shared Storage and Shared Config profile sections; cross-repo grep for table names, Redis key prefixes, S3 prefixes, feature flags.
- **Evidence pattern**: repo A validates positive balance but repo B writes negative values directly; same Redis key is hash in one repo and string in another; same flag name has different semantics.
- **False-positive guard**: DB constraints/triggers, shared library wrapper, explicit owner ADR, access only through owner API.
- **Stop / Tiebreak**: cover all shared storage/config access points. Single-repo concurrency is L9; cross-repo invariant violation is L17.
- Example: billing validates `balance >= 0`, while admin-tool writes directly to the table without the invariant.
- Counterexample: admin-tool calls billing API instead of direct DB writes.

### L18 Cross-Repo Retry and Idempotency

- **Hypothesis**: when caller A retries, callee B is idempotent; idempotency keys survive the boundary; retries cannot amplify into a storm.
- **Where to look**: Outbound Calls with retry settings; inbound handlers that create resources; idempotency-key propagation; retry budget and backoff.
- **Evidence pattern**: caller retries without idempotency key; callee creates a fresh record on every request; retry has no upper bound or no backoff.
- **False-positive guard**: framework injects idempotency key; callee deduplicates by business key; circuit breaker or bounded exponential backoff exists.
- **Stop / Tiebreak**: cover cross-repo retry pairs. Single-repo retry behavior is L10; cross-repo retry is L18.
- Example: payment callback is retried three times and creates three payment rows.
- Counterexample: callee deduplicates by `(caller_id, request_id)`.

### L19 Migration and Release Safety

- **Hypothesis**: schema, API, and config changes are compatible while N and N-1 versions are live; failed canaries can roll back safely.
- **Where to look**: migration scripts, version fields, feature flag rollout, recent shared storage changes, compatibility shims.
- **Evidence pattern**: N+1 drops a column still read by N; NOT NULL is added before backfill; migration is one-way and breaks rollback.
- **False-positive guard**: expand-and-contract migration, dual write/read window, rollback script, blue-green deployment, deprecation window completed.
- **Stop / Tiebreak**: cover recent and in-flight migrations. Single-repo schema lifecycle is L11; cross-version/cross-repo compatibility is L19.
- Example: v2 deletes `legacy_id`; rollback to v1 crashes because v1 still reads it.
- Counterexample: field had a completed deprecation window and all live versions stopped reading it.
