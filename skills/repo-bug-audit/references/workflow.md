# Workflow

## Contents

- Phase 0: Setup
- Phase 1: Minimal Knowledge Map
- Phase 2: Candidate Search
- Phase 3: Deep Verification
- Phase 4: Write Findings
- Phase 5: Architecture and Knowledge
- Phase 6: Review and Package

## Phase 0: Setup

- Confirm workspace root, audit output root, repos, reference repos, provided analyst when available, date, and language.
- Record repository branch, commit hash, and dirty status when available; use `metadata.md`.
- If the workspace already exists, read `resume-audit.md` before editing findings.
- If the task triggers Deep Discussion Mode, read `deep-discussion.md` and write a short analysis charter before inventory.
- If the user asks for automatic execution, proceed without repeated confirmation, but keep edits inside the output root.
- For automatic execution, skip discussion and record key assumptions in `quality/submission-scope.md` or the README.
- Infer safe defaults for date, language, package name, and optional package parts; do not infer analyst identity.
- If analyst is missing, use a placeholder in automatic runs. Ask once only when final handoff requirements explicitly need a named analyst.
- Create a lowercase, descriptive workspace name with separate `submit/` and `work/` directories.

## Phase 1: Minimal Knowledge Map

Collect enough facts before hunting Bugs; do not wait for complete documentation. **For every repo in scope, write one `submit/knowledge/repo-profiles/<repo>.md` per `references/repo-profile.md`** — this includes a Mermaid call graph (per `references/call-graph-conventions.md`) and the 5 boundary types (Outbound / Inbound / Shared Events / Shared Storage / Shared Config) plus Intent Inputs (README/ADR/design docs index). The profile is the input substrate for Tier 3 lens and META-1; without it, cross-repo exploration cannot run.

- Repositories, branches, languages, frameworks, build systems.
- Entry points: API views/controllers, service/provider layers, tasks, workers, CLIs, scripts.
- External systems: databases, cloud APIs, storage backends, network controllers, virtualization platforms, HTTP APIs, queues, shells, devices, billing, auth.
- Largest files/functions and generic directories: `utils`, `common`, `helpers`, `shared`.
- Cross-repo dependencies and call chains.
- Primary domain profile from `domain-profiles.md`.
- Language ecosystem facts from `language-ecosystems.md`: build metadata, framework entry points, package/test command sources, and language-specific false-positive guards.
- Initial resource lifecycles, state owners, async workflows, security boundaries, and high-risk paths.
- Use `knowledge-base.md` to decide what belongs in the minimal map.

Suggested commands. Use `rg` when available; use `cross-platform.md` when running on Windows or when a command fails.

```bash
rg --files
rg -n "timeout|retry|transaction|subprocess|shell|eval\\(|deserialize|pickle|yaml\\.load|while True|sleep\\(|TODO|FIXME" .
```

Unix, Linux, and macOS example for large source files:

```bash
git ls-files | grep -E '\\.(py|js|ts|tsx|java|kt|go|rs|cs|php|rb|c|cc|cpp|h|hpp)$' | xargs wc -l | sort -n | tail
```

Windows PowerShell equivalent:

```powershell
Get-ChildItem -Recurse -File -Include *.py,*.js,*.ts,*.tsx,*.java,*.kt,*.go,*.rs,*.cs,*.php,*.rb,*.c,*.cpp,*.h |
  Sort-Object Length -Descending |
  Select-Object -First 20 FullName,Length
```

## Phase 2: Candidate Search

**This phase is the lens system.** See `references/exploration-lenses.md` for the methodology.

Core loop per lens (4 steps):
1. **Hypothesize** — write down the failure mode you are looking for, before grepping
2. **Hunt** — apply the lens's "Where to look" patterns
3. **Refute** — for each candidate, find a sibling site that handles the same scenario correctly; the diff is the bug or the false-positive guard
4. **Promote or Park** — surviving candidates become Bugs; reputed-but-weak go to `work/candidates/`; refuted go into the lens application record's "排除原因"

**Coverage requirement**: Tier 2 (L8-L14) and Tier 3 (L15-L19, when audit covers ≥2 repos) lens must each have a 5-section application record in `submit/quality/lens-coverage.md`. Tier 1 (L1-L7) records optional. "已应用 lens 但未发现" is a legitimate, encouraged output. **Never invent findings to fill coverage** — see `authenticity.md`.

**Pluggable strategy**: if the user specified a non-default strategy (in `submit/quality/submission-scope.md`), follow that strategy; coverage requirement applies to the declared lens subset.

**Domain profile shapes lens priority** (`references/domain-profiles.md`); it does not exclude lens.

**Knowledge feedback**: update the per-repo profile and call graph when a candidate reveals a new boundary, lifecycle, state owner, or cross-repo relationship.

## Phase 3: Deep Verification

Before a candidate becomes a Bug, answer:

- What exact entry point triggers the path?
- What resource or user operation is affected?
- What code evidence proves the risky ordering or missing guard?
- What failure mode is realistic in production?
- What would the user/operator see?
- What existing wrapper, config, transaction, retry, or cleanup might make this a false positive?
- Does the finding duplicate another Bug, or is it a distinct module/path?

If any answer is weak, lower confidence or move it to `work/candidates/`.
Use `candidate-triage.md` for candidate notes and `deduplication.md` before deciding whether to merge or split findings.

## Phase 4: Write Findings

- Use `bug-schema.md`.
- Put findings in `findings/P1`, `findings/P2`, `findings/P3`, `findings/P4`.
- Filename must include priority, Bug id, and short description.
- On continuation runs, use the next ID after the largest existing `BUG-xxxx`; do not renumber old records.
- The final submitted package must contain a single contiguous `BUG-0001..BUG-N` sequence. Gaps and per-agent reserved ranges are rejected by `scripts/validate_bug_package.py`. For parallel multi-agent merges, see `resume-audit.md` → "Parallel Multi-Agent Consolidation".
- Keep static-analysis status clear: do not say “已验证” unless runtime proof exists.
- Add fix boundary, minimum safe fix, and suggested verification commands. Commands must be traceable to repository files; write `未确认` when no trustworthy command is visible.

## Phase 5: Architecture and Knowledge

Consolidate final knowledge files that help developers understand and continue the audit:

- `knowledge/system-overview.md`
- `knowledge/repo-relationship-map.md`
- `knowledge/risk-paths.md`
- `knowledge/architecture-design-review.md`
- `knowledge/repo-profiles/*.md` (already written in Phase 1; revise after lens findings expose new boundaries)
- `work/candidates/` for low-confidence leads that should not enter submitted findings.

**META-1 sweep (intent vs implementation drift)**: using each repo profile's `Intent Inputs` section, scan README / ADR / design docs / key commit messages and compare to actual code behavior. Findings are not new categories — they map back to L1-L19 (record the lens in `bug-schema.md` frontmatter `lens:`). META-1 may also surface as additional context in existing Bugs.

**META-2 sweep (failure-path test coverage)**: spot-check `tests/` against modules touched by Tier 2/3 Bugs. If a Bug's affected code path has no failure-path tests, note "风险增强：缺测试" in the relevant lens application record (this may justify priority bump).

Use `knowledge-base.md` for the final completeness check.
Architecture review should describe risk signals, not dictate principles.
Skip or collapse optional knowledge files when they would be empty or repetitive.

## Phase 6: Review and Package

- Generate indexes.
- For large or multi-repo packages, validate with `--require-knowledge`; add `--require-image` when `audit-overview.png` is expected.
- Run `evaluation.md` after structural validation.
- Evaluate all P1/P2 Bugs; for large packages, sample each issue family and risk domain.
- Re-read high-severity Bugs for false positives.
- Record downgrade, removal, merge, or candidate-promotion decisions in `quality/submission-scope.md`.
- Record priority-calibration changes and weak/unreviewed high-risk areas in `quality/submission-scope.md`.
- Check duplicate wording across modules.
- Check all Markdown is Chinese and developer-facing.
- Remove empty optional knowledge files from `submit/`.
- Check final repo knowledge is reusable and reflects submitted Bug families.
- Compress images; keep zip packages reasonably small.
- Zip only `submit/`; do not include `work/`.
- Rebuild zip after every final change.
