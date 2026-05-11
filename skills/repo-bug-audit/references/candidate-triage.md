# Candidate Triage

Use candidates for plausible leads that are not ready for submitted findings. A candidate is useful scratch evidence, not a weaker Bug record.

For repo-group, deep/full, or high-recall audits, candidates are also the discovery-funnel evidence. Do not treat final submitted Bugs as the only output of exploration. `candidate_count` in `work/shards/<repo>/shard-summary.json` counts all retained repo-local leads after first triage, including leads later promoted to submitted Bugs. Each retained lead must also appear as an evidence-bearing bullet in `work/shards/<repo>/candidates.md` with a candidate id (`C1`, `C2`, ...), priority estimate, outcome (`promoted`, `parked`, `refuted`, or `merged`), Bug-gate state (`bug_gate=complete` or `bug_gate=missing`), and a concrete `path:line` or submitted `BUG-0000` link. This makes the final package distinguish "46 candidates, 8 confirmed" from "only 8 things were explored" without letting JSON counts drift away from real notes.

High-recall search seeds are one step earlier than candidates. A seed becomes a candidate only after repo-local tracing finds a plausible failure mode that is not already refuted. Record that transition in shard `seed_triage`; do not silently drop seed categories just because they are not final Bugs.

For "deep", "full", "as many Bugs as possible", or security/auth runs, bias toward a larger retained candidate backlog before promotion. The goal is not to inflate submitted Bugs; it is to keep P3/P4, medium-confidence, duplicate-family, and follow-up-needed leads visible so a low confirmed count is credible. A high-recall scan with hundreds of seeds and only a tiny retained candidate pool is usually a process smell unless the package is honestly labeled `first-pass`/`focused` with concrete remaining gaps.

## Candidate Admission Threshold

Candidate admission is intentionally broader than final Bug submission.

Promote to a submitted Bug only when the full Bug gate is satisfied: code evidence, trigger path, realistic failure mode, affected resource, and impact.

Retain a candidate when repo-local tracing shows a plausible risk that is not refuted yet. A retained candidate needs a concrete code anchor and at least two of these signals:

- An exposed entry point, worker, CLI, plugin/tool path, upload/download path, callback, or scheduled path can reach the code.
- External input, tenant/user/resource identity, config, file path, URL, serialized payload, or model/tool metadata can influence the boundary.
- The expected guard is missing, unclear, client-side only, deployment-dependent, or inconsistent with a sibling implementation.
- The boundary has a side effect: state mutation, file/object storage, subprocess/code execution, network call, credential handling, serialization, lifecycle transition, or recovery behavior.
- The candidate matches a required issue family that has not yet been represented by a promoted, parked, merged, or refuted lead.

Do not require complete exploitability, a full fix design, or runtime reproduction to retain a candidate. Those are promotion inputs, not candidate-admission inputs.

For high-recall multi-repo runs, the candidate pool should normally be wider than the submitted findings. If every retained candidate becomes a submitted Bug, the funnel has probably collapsed too early: revisit lower-priority, medium-confidence, duplicate-family, and follow-up-needed leads before finalizing.

Do not stop at P1/P2. If a lower-priority lead has code evidence, a trigger path, a realistic failure mode, affected resource, and impact, submit it as P3/P4. Use candidates for leads that are plausible but still missing a key gate. A candidate marked `bug_gate=complete` must either be `outcome=promoted` / `outcome=merged` or it will fail final validation; change the gate to `bug_gate=missing missing_gate=<gate>` when evidence is incomplete.

High-priority parked leads need extra care. If `work/shards/<repo>/candidates.md` contains any `parked P1` or `parked P2` lead, add a `Promotion Review` section before final validation. Review each parked high-priority lead by candidate id (`C1`, `C2`, ...), and state the missing gate: trigger path, affected resource, realistic impact, duplicate/merged Bug, deployment-only condition, runtime-only confirmation, or false-positive guard. A final package should not hide likely P1/P2 Bugs in the candidate backlog just because stronger Bugs already exist.

## Candidate Format

Keep each candidate short. One Markdown file under `work/candidates/` is enough.

English template:

```markdown
- C1 | P2 | outcome=parked | bug_gate=missing | missing_gate=trigger-path | `repo/path/file.ext:line` | <short suspicion>
- C2 | P3 | outcome=promoted | bug_gate=complete | BUG-0017 | `repo/path/file.ext:line` | <short title>
```

Chinese deliverables may use:

```markdown
- C1 | P2 | outcome=parked | bug_gate=missing | missing_gate=trigger-path | `repo/path/file.ext:line` | <短疑点>
- C2 | P3 | outcome=promoted | bug_gate=complete | BUG-0017 | `repo/path/file.ext:line` | <短标题>
```

Optional after a later pass:

```markdown
- C1: kept parked because missing trigger path from public entry point; evidence checked at `repo/path/file.ext:line`.
- C2: promoted as `BUG-0017`.
```

## Candidate Index

After candidate promotion/refutation and after `scripts/generate_bug_index.py`, run:

```bash
python3 scripts/generate_candidate_index.py <submit-root>
```

Outputs:

- `submit/indexes/candidates.generated.json`
- `submit/indexes/candidates.generated.md`
- `submit/quality/candidate-coverage.md`

For repo-group final packages, `validate_bug_package.py --repo-root <path>` rejects a missing candidate index, mismatched shard totals, or submitted findings that do not trace back to shard candidates.

## Promotion Rules

- Promote only when code evidence, trigger path, failure mode, and impact are all explicit.
- Do not submit raw scanner output as a Bug.
- Do not submit pattern-only claims such as "HTTP call has no timeout" unless the affected call path and production impact are clear.
- For high-recall/deep audits, review the retained candidates across P1-P4 before finalizing. A final package containing only P1/P2 Bugs should be justified by the candidate funnel, not by omission of lower-priority credible issues.
- For final packages, `generate_candidate_index.py` creates a Priority Promotion Sweep. If it reports gate-complete unsubmitted candidates, either promote them into `findings/P*/` or edit the candidate note to name the missing gate.
- For any parked P1/P2 lead, add a `Promotion Review` entry. If the lead satisfies the Bug schema, promote it; if not, name the missing gate rather than saying it was deprioritized.
- If evidence remains weak, keep the lead in `work/candidates/` and improve the "Evidence Needed To Promote" field.
- If the same lead repeats across files without distinct impact, keep one candidate and list representative locations.
- If a candidate becomes a Bug, copy only evidence-backed claims into `submit/`; leave speculation in `work/`.
