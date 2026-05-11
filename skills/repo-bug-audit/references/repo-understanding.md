# Repo Understanding Contract

Use this contract before candidate Bug hunting. Its goal is to make each repo's behavior legible enough that low Bug counts can be trusted.

## Contents

- When Required
- Risk Surface Map
- Hypothesis Loops
- Zero-finding Standard
- Shard Summary Fields
- Common Failures

## When Required

Use this contract for:

- Every repo in a repo-group audit.
- Any single-repo audit described as deep, full, complete, handoff, or final.
- Any repo with more than 10 source-like files unless the run is explicitly recorded as a lightweight/custom scan.

For tiny utility repos, keep the contract short. It is enough to identify the executable entry point or explain that none exists.

## Companion Knowledge Skills

If `acquire-codebase-knowledge` is available, use it as an accelerator for large or unfamiliar repos, not as a substitute for this contract.

- Its stack/structure/integration docs can seed `surface_map`.
- Its architecture and concerns notes can seed hypothesis loops.
- Its testing docs can seed verification sources and META-2 checks.
- Do not let it write `docs/codebase/` into source repositories unless the user approved that output. For audit-only runs, copy only verified facts into `work/drafts/knowledge-capture.md`, `work/shards/<repo>/shard-summary.json`, and `submit/knowledge/repo-profiles/<repo>.md`.

## Risk Surface Map

Before searching for Bugs, build a repo-local surface map from source evidence. Do not infer surfaces from directory names alone.

For repo-group or high-recall runs, the first surface map comes from model-led code reading. After the supplemental `run_high_recall_scan.py --patterns-file` pass creates `work/shards/<repo>/search-seeds.md`, revisit the map and hypothesis loops for gaps. Do not treat a seed hit as a candidate until you trace the entry point, boundary, guard/refutation, and realistic failure mode.

## Hybrid Discovery Loop

Bug discovery must combine model-led code understanding with search-led coverage.

Model-led discovery is the first track. Read manifests, routes, CLIs, workers, services, adapters, state owners, and side-effect boundaries. Ask what the system is trying to do, then form failure hypotheses from behavior:

- Which user or system action enters here?
- What resource, tenant, file, model, job, socket, queue, or external service can be affected?
- What guard should exist: permission, validation, transaction, timeout, retry, cleanup, idempotency, schema, sandbox, or lifecycle handling?
- What sibling implementation or caller pattern confirms or refutes the expectation?

Search-led discovery is the second track. Use high-recall hits to find surfaces the model-led walk may miss: rare execution paths, dynamic calls, config defaults, edge-case parsers, old routes, deployment templates, test-only code copied into production, and issue families not represented in the first pass.

Retain candidates from either track. A candidate does not need to originate from a scanner hit. It can come from reading a call chain and noticing a missing guard, impossible state transition, unsafe lifecycle edge, or inconsistent sibling implementation. Conversely, a scanner hit is only a seed until the code walk gives it boundary, trigger hypothesis, guard status, and outcome.

Every non-trivial shard should show both tracks:

- `surface_map` and `hypothesis_loops` record model-led understanding.
- `seed_triage` records search-led coverage checks.
- `candidates.md` records promoted, parked, merged, and refuted leads from both tracks.

Required categories when present. This is the architect-level surface taxonomy for `repo-bug-audit`; it should guide scanning, not become a checklist of invented content.

- `entry_points`: API routes, controllers, CLIs, workers, scheduled tasks, UI routes, scripts.
- `auth_boundaries`: backend permission checks, tenancy/resource ownership, tokens, roles, policy adapters, front-end route guards that must not be the only protection.
- `state_owners`: database repositories, domain state machines, object storage, file stores, queues, workflow state, ownership of mutable resources.
- `consistency_boundaries`: transactions, idempotency keys, retries, compensation, cache/index synchronization, cross-step rollback, read/write split.
- `external_integrations`: HTTP/RPC clients, SDKs, browsers, model providers, cloud APIs, webhooks, callback consumers.
- `execution_boundaries`: shells, subprocesses, dynamic code execution, plugin execution, sandbox/worker isolation, command construction.
- `serialization_contracts`: pickle/YAML/XML/JSON parsing, DTO/event payloads, API schemas, DB migrations, protobuf/OpenAPI/GraphQL contracts.
- `async_jobs`: schedulers, background workers, queues, callbacks, retries, event consumers, terminal-state transitions.
- `config_and_secrets`: env loading, defaults, feature flags, credentials, TLS/proxy settings, deployment-specific toggles.
- `user_input_paths`: upload, download, URL/path/query/body/Markdown/rendered input paths, front-end XSS sinks and preview/render boundaries.
- `file_paths`: local temp files, NFS/shared paths, generated files, archive extraction, cleanup, object-store key construction.
- `resource_lifecycle`: file descriptors, connections, locks, threads/coroutines, GPU/model handles, temporary resources, cleanup/finalizers.
- `observability_recovery`: error handling, audit logs, metrics, retry visibility, dead-letter/manual recovery, alertable terminal failures.
- `deployment_runtime`: containers, startup scripts, health checks, process users, mounted volumes, runtime permissions, rollout/rollback assumptions.

Every non-trivial repo should populate at least three categories. Large repos should cover enough categories to explain why later Bugs or zero findings are plausible. Do not force absent surfaces; record them as uncovered or not applicable only when source evidence supports that boundary.

## Hypothesis Loops

For each important surface, run a concrete loop:

1. State a failure hypothesis.
2. Name the entry point.
3. Trace to the state owner, external integration, or side-effect boundary.
4. Look for the guard: validation, permission check, transaction, retry, timeout, cleanup, idempotency, or sibling implementation.
5. Record the result as `promoted`, `parked`, or `refuted`.

A hypothesis loop is not a search summary. It needs code anchors such as `src/api/orders.py`, a route like `POST /orders`, or a function/class boundary.

## High-recall Seed Triage

When `work/shards/<repo>/search-seeds.md` exists, the shard summary must include `seed_triage`. This prevents broad search from becoming decorative. Review representative seeds across categories and classify each as `promoted`, `parked`, `refuted`, or `merged`.

Use this shape:

```json
{
  "category": "execution_boundaries",
  "location": "src/jobs/export.py:42",
  "seed": "subprocess.run(command, shell=True)",
  "follow_up": "Traced export_job -> build_command -> subprocess.run and checked filename allowlist",
  "outcome": "parked",
  "candidate_or_reason": "Candidate: export command may accept untrusted report names; needs caller permission trace"
}
```

Do not triage only the easiest category. Large repos should review several categories so auth, execution, file/path, network, state, config, and lifecycle surfaces do not vanish behind one final Bug count.

Examples:

- `POST /orders -> create_order -> order_repo.insert`; hypothesis: duplicate submit creates double order; guard: unique idempotency key in `orders.py`; result: `refuted`.
- `worker sync_accounts -> crm_client.post`; hypothesis: retry without timeout blocks worker; guard: no timeout found in `clients/crm.py`; result: `parked`.

## Zero-finding Standard

Zero findings are valid only when the repo shows exploration work:

- The surface map names concrete scanned paths.
- At least one suspicious lead is refuted or parked for non-trivial repos.
- The zero-finding rationale names why no Bug was promoted.
- Remaining gaps are explicit.

Do not write "no issues found" without the above evidence.

## Shard Summary Fields

Add these fields to each `work/shards/<repo>/shard-summary.json`:

```json
{
  "surface_map": {
    "entry_points": ["src/api/orders.py"],
    "auth_boundaries": ["src/auth/policies.py"],
    "state_owners": ["src/db/order_repo.py"],
    "consistency_boundaries": ["src/api/orders.py uses Idempotency-Key before order_repo.insert"],
    "external_integrations": ["src/clients/payments.py"],
    "execution_boundaries": ["src/jobs/export.py invokes subprocess.run([...])"],
    "serialization_contracts": ["src/contracts/order_event.py"],
    "async_jobs": ["src/jobs/reconcile.py"],
    "config_and_secrets": ["src/settings.py"],
    "user_input_paths": ["src/api/uploads.py"],
    "file_paths": ["src/storage/tmp.py"],
    "resource_lifecycle": ["src/storage/tmp.py creates and deletes temporary files"],
    "observability_recovery": ["src/jobs/reconcile.py logs dead-letter failures"],
    "deployment_runtime": ["Dockerfile"]
  },
  "hypothesis_loops": [
    {
      "surface": "HTTP order creation",
      "hypothesis": "Duplicate client retry may create duplicate orders when idempotency is absent.",
      "entry_point": "POST /orders in src/api/orders.py",
      "chain_or_boundary": "create_order -> order_repo.insert",
      "guard_or_refutation": "src/api/orders.py checks Idempotency-Key before insert",
      "result": "refuted"
    }
  ],
  "seed_triage": [
    {
      "category": "execution_boundaries",
      "location": "src/jobs/export.py:42",
      "seed": "subprocess.run(command, shell=True)",
      "follow_up": "Traced export_job input from POST /exports to command construction",
      "outcome": "parked",
      "candidate_or_reason": "Needs permission and filename allowlist confirmation before promotion"
    }
  ],
  "strongest_refuted_leads": [
    "Duplicate order creation refuted by Idempotency-Key guard in src/api/orders.py"
  ]
}
```

`surface_map` and `hypothesis_loops` can be concise, but they must be evidence-bearing. Use relative paths inside the target repo when possible.

## Common Failures

- Pattern-only scanning without a surface map.
- Treating `high-recall-scan.json` as the source of truth instead of a coverage aid.
- Only retaining leads that came from regex hits; AI-led call-chain discoveries are valid candidates too.
- Final profiles that describe architecture but do not name evidence paths.
- Zero-candidate shards with no strongest refuted lead.
- Call chains that say "controller -> service -> storage" without route, function, or file anchors.
- Starting final report generation before repo understanding fields are filled and shard validation passes.
