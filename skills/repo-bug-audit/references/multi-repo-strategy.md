# Multi-Repository Strategy

## When to Split into Multiple Sessions

A single audit session can deeply cover **up to 10 repositories**. For 11+ repos, recommend splitting.

| Repos | Sessions | Strategy |
|---|---|---|
| 1-5 | 1 | Full deep: per-repo call-chain tracing, exhaustive seed triage, complete hypothesis loops |
| 6-10 | 1 | Deep, parallel Agent exploration per repo |
| **11-25** | **2** | **Session 1**: first-pass all repos, identify top risks. **Session 2**: deepen high-risk repos + cross-repo lenses + package |
| 26+ | 3+ | Session 1: first-pass all. Session 2: deepen selected. Session 3+: incremental deepen + package |

## When to Recommend Splitting

In **interactive mode**, recommend splitting when the roster has **11 or more repos with source code** (not counting stub repos). In **automatic mode**, default to 2-session plan and record in `submission-scope.md`.

### Recommendation format

One yes/no question, no enumeration:

> "This group has 20 repos — beyond what a single deep scan can cover. Split into 2 sessions?
> - Session 1: first-pass all 20, find the highest-risk repos
> - Session 2: deepen the top repos, cross-repo analysis, final package
>
> Start session 1?"

## Session 1: First-Pass All Repos

1. Set audit charter with `batch-first-pass` coverage mode
2. Initialize workspace, freeze roster, run high-recall scan
3. Dispatch parallel exploration agents for all repos
4. Convert Agent output to shard evidence (see below)
5. Run `validate_bug_package.py --validate-shards-only --coverage-mode batch-first-pass`
6. Generate candidate index, draft HTML report
7. **Record end state**: per-repo candidate counts, P1/P2 candidates, recommended repos for Session 2 deepening

Session 1 delivers: **candidate inventory across all repos with prioritized hit list for Session 2**.

## Session 2: Deepen + Package

1. Resume from session 1's output root
2. Select repos for deepening by: P1 count, infrastructure criticality (BFF, auth, data stores), cross-repo connectivity
3. For selected repos: full call-chain tracing, complete seed triage, upgrade to `deep-complete`
4. Run cross-repo boundary + META checks
5. Deduplicate, promote, write Bug records
6. Full validation and final package

## Agent Output Conversion

In `batch-first-pass` mode, converting parallel Agent exploration reports to shard JSON/MD is allowed when:

- Content is sourced from **named Agent outputs** (not embedded prose from memory)
- The conversion is **deterministic** (same input → same output)

Safe pattern: a Python script that parses one Agent's report and writes that repo's shard files. Unsafe pattern: a script that loops over repos with hardcoded prose strings.
