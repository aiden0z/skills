# Tier 1 Surface Lenses

Tier 1 lenses focus on single files or single functions. They are useful early because they find local defensive-code gaps and seed higher-tier paths.

### L1 Resource Lifecycle

- **Hypothesis**: paired operations such as open/close, acquire/release, allocate/free, attach/detach are paired on every control-flow branch.
- **Where to look**: `open(`, `acquire(`, connection-pool checkout, coroutine/thread spawn, file descriptors, missing `finally`.
- **Evidence pattern**: acquire/open occurs in a `try` branch but close/release is missing in an exception, return, cancellation, or retry path.
- **False-positive guard**: `with`, RAII, contextmanager, Go `defer`, Java try-with-resources, Rust `Drop`, or equivalent wrapper.
- **Stop / Tiebreak**: cover all branches in the function. If overlap with L9, leaked resource is L1; wrong ordering under concurrency is L9.
- Example: retry branch leaves an HTTP client open and leaks file descriptors.
- Counterexample: `async with httpx.AsyncClient() as c:` already scopes cleanup.

### L2 Boundary Input Validation

- **Hypothesis**: external input is validated for type, range, format, and authorization before use.
- **Where to look**: request bodies, URL params, headers, env vars, parsed files, external SDK responses, direct path/shell/SQL/eval use.
- **Evidence pattern**: unvalidated external value reaches SQL, shell, eval, file path, redirect, permission decision, or tenant boundary.
- **False-positive guard**: framework validation, typed schemas, gateway enforcement, ORM parameterization, strong params.
- **Stop / Tiebreak**: cover entry body plus one call layer. Injection/path traversal is L2; logical cross-service authorization drift is L17.
- Example: `X-Tenant` header is concatenated into a SQL `WHERE tenant=...`.
- Counterexample: apparent string building is SQLAlchemy parameterization.

### L3 Silent Failure

- **Hypothesis**: caught exceptions are logged, retried, converted, re-raised, or intentionally degraded; they are not silently swallowed.
- **Where to look**: broad catches, empty catch blocks, `pass`, ignored Go errors, `recover()`, `// ignore`.
- **Evidence pattern**: catch has no log, metric, rethrow, user-visible fallback, or durable state update.
- **False-positive guard**: explicit fallback path, cache-miss tolerance, central error middleware, monitored degradation.
- **Stop / Tiebreak**: cover catch blocks in the function. Swallowing itself is L3; swallowed exception causing state drift is L8/L10.
- Example: data write failure is caught with `except: pass`, so users see success.
- Counterexample: cache failure logs a warning and falls back to DB.

### L4 Numeric Precision and Overflow

- **Hypothesis**: money, quotas, timestamps, counters, and measurements do not lose precision or overflow.
- **Where to look**: float money, 32-bit counters, division, accumulation loops, bit shifts, signed/unsigned conversions.
- **Evidence pattern**: monetary calculation uses float; accumulator can overflow; divide-by-zero guard is absent; NaN can propagate.
- **False-positive guard**: Decimal/BigDecimal/int64, earlier denominator validation, bounded counters.
- **Stop / Tiebreak**: cover arithmetic in the function. Local numeric issue is L4; cross-service representation drift is L15.
- Example: monthly invoice total uses `float` and accumulates small currency drift.
- Counterexample: backend serializes large IDs as strings.

### L5 Time and Clock

- **Hypothesis**: time logic handles timezone, DST, leap dates, wall-vs-monotonic clocks, and historical/future dates.
- **Where to look**: `datetime.now()`, `time.time()`, `Date()`, timeout checks, cron, expiry math, timezone conversion.
- **Evidence pattern**: wall clock used for timeout; naive datetimes compared across timezones; "tomorrow" math fails across DST; month rollover is invalid.
- **False-positive guard**: monotonic clock for intervals, UTC storage, timezone-aware datetimes, robust time libraries.
- **Stop / Tiebreak**: cover time-related functions. Single-point time bug is L5; multi-service time drift is L15/L17.
- Example: cleanup job compares local `datetime.now()` with UTC records and deletes new rows.
- Counterexample: framework injects timezone-aware datetimes.

### L6 Representation and Serialization Semantics

- **Hypothesis**: data meaning survives serialization across process, language, and version boundaries.
- **Where to look**: JSON null vs missing, protobuf optional/default, unknown enums, base64 padding, int64 through JS Number, date units.
- **Evidence pattern**: producer sends `null` to mean delete while consumer treats it as absent; new enum has no default; large ID loses precision.
- **False-positive guard**: schema compatibility tests, protobuf/avro lint, explicit string encoding for large IDs.
- **Stop / Tiebreak**: cover serialization boundaries. Encoding/representation is L6; contract meaning drift is L15.
- Example: backend emits 18-digit IDs as JSON numbers and frontend rounds them.
- Counterexample: ID is already serialized as a string.

### L7 Resource Amplification Entry Point

- **Hypothesis**: one request/event cannot amplify into unbounded downstream calls, queries, allocations, or recursion.
- **Where to look**: IO inside loops, N+1 queries, recursion, user-provided regex, unsafe deserialization, unpaged list APIs, fan-out calls.
- **Evidence pattern**: user-controlled loop bound encloses IO; regex pattern comes from request; list endpoint loads unbounded rows.
- **False-positive guard**: batch query, hard bound, authorization-based cap, size limit before deserialization.
- **Stop / Tiebreak**: cover entry plus one call layer. Single-repo amplification is L7; cross-repo retry storm is L18.
- Example: `/api/users` dumps every user row without pagination.
- Counterexample: apparent N+1 path uses `joinedload` or batched `WHERE id IN (...)`.
