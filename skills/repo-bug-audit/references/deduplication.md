# Deduplication

Use this before creating, splitting, merging, or removing findings.

## Merge

Merge findings when all three are the same:

- Same entry point or user/operator action.
- Same failure mode.
- Same impact scope.

Keep the strongest evidence, list representative affected files, and record any merged Bug id in `submit/quality/submission-scope.md`.

## Split

Split findings when any of these differ materially:

- Different resource lifecycle, such as create/delete/recover/migrate.
- Different affected resource, such as volume, snapshot, host, tenant, token, cache, route, or device.
- Different failure mode, such as data loss, permission bypass, resource leak, request hang, or stale display.
- Different owner module where fixing one path would not fix the other.

## Keep in Knowledge

- Repeated architecture patterns belong in `submit/knowledge/`, but they do not replace concrete Bug records.
- One architecture risk can explain many Bugs; it should not become a vague umbrella Bug unless it has its own concrete failure path.

## Candidate Handling

- Put duplicate or weak variants in `work/candidates/`, not `submit/findings/`.
- If two Bugs are merged during review, keep the surviving Bug id stable and record the merge reason.
- Do not inflate counts by cloning the same wording across modules.
