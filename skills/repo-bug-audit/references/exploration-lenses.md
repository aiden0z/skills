# Exploration Lenses

## Contents

- How to Use
- The 13 Architecture Boundaries
- Natural Boundaries
- Meta Lenses
- Lens Coverage Records
- Session-Specific Scope

A lens is a risk perspective: pick an architecture boundary, form a concrete failure hypothesis, trace the code across that boundary, then promote or park the result.

This file replaces the previous L1-L19 pattern catalog. LLMs already know what `eval()`, `pickle.loads()`, and `dangerouslySetInnerHTML` do. They don't need a checklist of function names. What they need is to be pointed at the right **architecture boundaries** — the places where bugs concentrate because assumptions break across system layers.

## How to Use

For each repo during exploration, scan the 13 boundaries below. Not every boundary applies to every repo — a CLI tool has no message boundary, a pure frontend has no database. Skip what doesn't apply, record that you skipped it.

For each boundary that applies:

1. **Hypothesize** — "I am looking at X boundary because Y assumption could break and cause Z impact."
2. **Trace** — follow data from one side of the boundary to the other. Read every function in between.
3. **Find the sibling** — another code path crossing the same boundary. If the sibling has a guard this path lacks, that's a finding.
4. **Promote or park** — clear evidence + trigger path = candidate. Weak signal = parked lead.

## The 13 Architecture Boundaries

### 1. API Contract

Data leaving one component and entering another carries assumptions about format, meaning, and lifecycle. The producer and consumer evolve independently — each side can change without the other knowing.

**How to examine**: Find the border where data crosses from one component to another — an HTTP response body, a message payload, a shared database row. Read the producer's serialization code: what values can it emit? Then read every consumer of that data: do they all handle the full range? A field that means "deleted" to the producer and "absent" to the consumer is a Bug. A field the producer removed but a consumer still reads is a Bug. Look for version fields, enum values, and nullable markers — these signal contract assumptions. Compare error response formats: does the consumer's error handling match what the producer actually returns?

### 2. Cache

Data exists in two places with a time window where they disagree. Every cache hit is a decision to tolerate staleness — but the code that reads from cache rarely acknowledges this tradeoff explicitly.

**How to examine**: Find every cache write. Find every cache read. For each pair, ask: what happens between the write and the next read? What happens if the cached data is evicted before the next write? Trace the invalidation path: does every code path that mutates the source data also invalidate or update the cache? If invalidation fails silently, does the system serve stale data indefinitely? Look at the TTL: is it chosen based on how fast the underlying data actually changes, or is it an arbitrary number? Find cache-aside patterns (check cache, miss, load, store) — the window between load and store is where concurrent requests can stampede the origin.

### 3. Message

Data moves between services asynchronously. Delivery is not guaranteed. Order is not guaranteed. Messages can arrive more than once. The producer and consumer make independent assumptions about these guarantees.

**How to examine**: Find the produce side — what triggers a message? Find the consume side — what happens on receipt? Trace what the consumer does when it fails: is the message retried, dead-lettered, or silently dropped? If the consumer processes a message but crashes before acknowledging, the message redelivers — is the handler safe against this? Look for ordering dependencies: does the consumer assume message A arrives before message B? Check the retry configuration: is there a max retry count and a backoff, or can messages retry forever? Check schema evolution: if the producer adds a field, does the old consumer still running in production handle it or crash?

### 4. Rollback

Code moves forward; state must move both directions. Migrations, feature flags, and deployments create windows where old and new versions coexist in production.

**How to examine**: Find every database migration. For each, ask: if we run the down migration, is any data lost that the up migration created? Destructive changes (dropping columns, deleting tables) are rollback-hostile. Find every feature flag check. For each: when this flag is turned off, what happens to data that was written while it was on? Does the off-path clean up, ignore, or break on the new data shape? Check deployment order: during a rolling update, can a new instance write data in a format the old instance can't read?

### 5. Third-Party

A dependency outside your control can fail, hang, return garbage, or change behavior without notice. The callsite's assumptions about the dependency's reliability are rarely explicit in the code.

**How to examine**: Find every outbound call to an external system. Look at what surrounds it: is there a timeout? If not, the call can hang the caller forever. If there is a timeout, what happens when it fires — does the caller retry, fail, or return stale data? If there's a retry, does it use exponential backoff, or does it hammer the dependency harder? Trace the response handling: if the dependency returns a 500, a malformed body, or a success code with unexpected structure, does the caller handle it or crash? Check if the dependency is called on every request or only on some — a dependency called only in an edge case is the one whose failure won't be noticed until production.

### 6. Lifecycle

Every process, connection, pool, and temp file has a start, a steady state, and an end. The code that handles the start is run once per deploy; the code that handles the end may never have been run in production.

**How to examine**: Find startup code — initialization, config loading, connection establishment, cache warming. What happens if any of these fail? Does the process crash, hang, or start in a degraded state? Find shutdown code — signal handlers, cleanup hooks, drain logic. Are connections drained before closing? Are in-flight requests given time to complete? Are temp files cleaned up? Find process manager configuration (systemd, supervisord, Docker restart policy): if the process crashes, who restarts it? Is there a health check, and does it test actual functionality or just return 200? Find background job or worker initialization: if the process restarts, do in-progress jobs resume or get orphaned?

### 7. Concurrency

Two execution contexts touch the same state without coordination. The Bug only manifests under specific timing — it won't appear in single-request testing.

**How to examine**: Find shared mutable state — module-level variables, class-level fields in singleton services, shared caches without locking. Trace a read-modify-write sequence: if two requests interleave between the read and the write, does the second write corrupt the first? Find lock acquisition: is every lock released in a finally block? Are there nested locks, and if so, is the lock ordering consistent everywhere? Look for "check then create" patterns: does the code check if a resource exists and then create it, with a gap where another request can create it first? In async code: does an await release control, and does the code after the await still hold the invariants it assumed before?

### 8. Config

Behavior is parameterized by values that change independently of code. The same code path behaves differently across environments, and the differences are rarely reviewed together.

**How to examine**: Pick one config key. Find its value in every environment file (dev, tst, pre, prod). Are they different? If they are, is the difference intentional and documented? Look for default values in code: if the config key is absent, what behavior does the default produce? Is the default safe for production, or is it a development convenience (debug=true, auth=disabled, log_level=debug)? Check if secrets are stored alongside non-secret config: an encryption key in the same file as the encrypted value is not protection. Check config precedence: env vars override files override defaults — a value set in one layer may be silently overridden by another.

### 9. Failure Mode

Every system degrades. The question is whether it degrades safely — maintaining its core guarantees even when parts of it are broken.

**How to examine**: Pick an external dependency. Trace what happens when it's unreachable: does the calling code catch the exception, and what does it do next? Does the system continue serving requests without the dependency (fail-open, potentially without the protection the dependency provided) or reject requests (fail-closed, potentially causing an outage for a dependency failure)? Find partial failure scenarios: if one of three backends is down, does the system make consistent decisions, or does it depend on which backend handled the request? Look for cascading failure paths: a timeout in service A causes thread exhaustion, which causes health checks to fail in service B, which causes the load balancer to drain service B.

### 10. Clock

Time is not uniform. Clocks drift between machines. Timezones shift. The same instant can have different representations in different parts of the system, and code that compares them can make wrong decisions.

**How to examine**: Find every place a timestamp is generated. Is it wall-clock time or monotonic time? Wall-clock for a timeout means an NTP adjustment can make the timeout fire early or never. Trace where timestamps are compared: are they from the same clock source? A timestamp from service A compared to a timestamp from service B is a comparison of two clocks that may disagree. Find timezone conversions: is the conversion happening at the right layer, or is a UTC timestamp being treated as local? Check expiration logic: if TTL is computed as "now + duration", and "now" comes from a different clock than the one checking expiration, items may expire early or live forever. Check DST boundaries: code that adds "24 hours" crosses a DST transition may get 23 or 25 hours.

### 11. Permission Propagation

A user's request passes through multiple services. At each hop, a decision is made about whose authority to use for the downstream call. One wrong decision in the chain can grant or deny access incorrectly.

**How to examine**: Trace a request from the outermost entry point through every internal service call. At each outbound call, what credentials are attached? Does the service forward the original user's token, or does it use its own service account? If it uses a service account, can the downstream service distinguish which user initiated the request? Look for scope changes: does the token get narrower at each hop (removing unnecessary permissions), or does the full token propagate? If a downstream service is compromised, what can it do with the tokens it receives? Check if audit logs at each hop record the original caller identity or only the immediate caller.

### 12. Pagination

Data sets larger than memory must be split across multiple responses. The split strategy makes assumptions about the underlying data — assumptions that break when the data changes between pages.

**How to examine**: Find every list endpoint. Is it offset-based or cursor-based? If offset-based: the underlying data can change between page 1 and page 2, causing items to shift between pages — some items are skipped, others appear twice. If cursor-based: is the cursor stable? A cursor based on a mutable field (like "last updated") will break when the field changes. Find the default page size: is it small enough for performance but large enough to avoid excessive round-trips? Is there a maximum page size enforced, or can a caller request page_size=999999? Check if the pagination method is consistent across all list endpoints in the system, or if each endpoint reinvented it differently.

### 13. Idempotency

Some operations are safe to repeat; others are not. The distinction is a property of the operation's semantics, not the transport protocol — but the transport protocol (HTTP retries, message redelivery) will repeat them anyway.

**How to examine**: Find every state-changing operation (POST, PUT, PATCH, DELETE, message handler). For each: if this operation is executed twice with the same inputs, is the result the same as executing it once? If the caller sends a request, doesn't receive the response due to a network error, and retries — does the server create two resources, charge twice, or send two emails? Look for idempotency key mechanisms: does the server accept a client-generated key and deduplicate by it? What's the key's scope — per-request, per-customer, global? When do idempotency keys expire, and what happens when they do — can a retry after expiry create a duplicate? Check GET endpoints: are they truly side-effect-free, or do they increment counters, write audit logs, or trigger background work?

## Natural Boundaries

These boundaries don't need explicit guidance. LLMs will find bugs at them without being told:

- **Trust boundary** — user input entering the system. LLMs recognize unvalidated input, SQL injection, command injection, path traversal.
- **Execution boundary** — data executed as code. LLMs recognize `eval()`, `exec()`, `ProcessBuilder`, `new Function()`.
- **Serialization boundary** — data changing representation. LLMs recognize `pickle`, `ObjectInputStream`, `yaml.load()`.
- **Rendering boundary** — user content becoming UI. LLMs recognize `dangerouslySetInnerHTML`, `innerHTML`, `v-html`.

You can still record findings at these boundaries in lens coverage. Just don't spend exploration time explicitly hunting them — the LLM will flag them naturally while examining the 13 guided boundaries.

## Meta Lenses

Meta lenses are applied after boundary exploration. They don't find new bugs directly; they amplify or refute existing candidates.

### META-1: Intent vs Implementation

Compare what the system says it does (README, ADRs, comments, commit messages) with what the code actually does. A README claiming retries where code has none. An ADR requiring auth where an endpoint is open. Record findings as boundary-specific candidates, tagged `META-1`.

### META-2: Failure-Path Coverage

For each candidate Bug in a critical path, check whether tests cover the failure mode. No failure-path test makes the Bug higher priority. Don't submit "missing test" as a Bug — record it as risk amplification on the existing candidate.

## Lens Coverage Records

Every audit writes `submit/quality/lens-coverage.md`. For each boundary examined, record:

```markdown
### Boundary: API Contract

- Scanned: services A ↔ B interface, message schema v2
- Candidates: 2 (null-handling mismatch, deprecated field consumer)
- Refuted: 1 (pagination contract confirmed consistent via shared library)
- Uncovered: service C ↔ D interface (out of audit scope)
```

Zero-candidate records are valid: "Applied and found no Bug."

## Session-Specific Scope

- **Single-repo / deep**: Examine all 13 boundaries. If a boundary doesn't apply (e.g. no message queue), record "not applicable" with the reason.
- **Multi-repo / batch-first-pass Session 1**: Focus on boundaries most likely to yield cross-repo patterns: Config, API Contract, Third-Party, Permission Propagation. Sample the rest.
- **Session 2+**: Full boundary coverage on deepened repos.
