---
name: repo-bug-audit
description: Use when asked to find Bugs, audit or review a repository, scan code for security/reliability/architecture risks, inspect a folder of many repos, produce evidence-backed Bug reports, continue a prior audit, or compare/triage candidate findings.
---

# Repo Bug Audit

IRON LAW: Do not submit a Bug unless code evidence, trigger path, realistic failure mode, and impact are all explicit.

IRON LAW: Do not write final deliverables from memory or embedded prose. Every shard summary, candidate note, Bug record, and knowledge doc must trace back to either (a) exploration evidence gathered repo-by-repo, or (b) a named Agent's exploration report converted deterministically. Scripts may render indexes, HTML, and images from existing evidence. See `references/shard-schema.md` for format and `references/multi-repo-strategy.md` for Agent output conversion rules.

## Purpose

Find evidence-backed Bugs and architecture risk signals across one or more repositories, then package the results so developers or later Agents can review, reproduce, triage, and fix them safely.

This skill is review-first. Do not patch code unless the user explicitly asks for fixes after the analysis.

## North Star

Use all available codebase knowledge to understand each audited repo first, then maximize credible Bug discovery through evidence-backed hypotheses, call-chain tracing, refutation, and triage.

The workflow exists to prove real repo understanding, not to fill forms. Prefer honest gaps and parked leads over template-complete shallow coverage.

## Quick Reference

When context is tight, keep these six rules active:

1. Evidence beats completeness: if a step cannot be honestly completed, mark coverage as `in-progress`, `focused`, or explicitly uncertain instead of filling forms.
2. Explore first, scan later: repo roster → AI-led surface mapping → Agent exploration → gap analysis → LLM-generated targeted scan → shard evidence, candidate promotion/refutation, and pre-package validation must precede README, HTML, and overview assets.
3. Scan only frozen source roots: for repo groups, use `repo-scan-roots.txt`; generated audit output and historical packages are never source roots.
4. Candidates require triage: scanner hits are prompts, not candidates. Candidate admission is broader than Bug submission; retain plausible unrefuted P1-P4 leads after repo-local boundary, trigger hypothesis, guard status, and outcome are named.
5. P1 saturation is not a stopping condition: before final handoff, sweep retained P1-P4 candidates and submit every gate-complete Bug; parked leads must name the missing gate.
6. Evidence must be traceable: every artifact traces back to repo exploration or a named Agent's report converted deterministically. HTML is default; overview PNG is optional and can be offered after handoff.

## Conflict Resolution

When rules appear to conflict, resolve them in this order:

1. Authenticity and real code evidence.
2. User-requested scope and depth intent.
3. Roster, shard, candidate, and lens validation gates.
4. Report asset generation and packaging polish.

If the requested depth cannot be met in the current run, do not skip gates or relabel the work silently. Keep the requested intent in `submission-scope.md`, classify delivered coverage honestly in `depth-coverage.md`, and ask for or record a user-accepted downgrade before final report assets.

## Operating Rules

### Bug Discovery (read these when exploring)

- **Read code, don't just grep.** Read `references/exploration-methodology.md` before dispatching agents. The exploration loop is: pick a surface → trace input to state → trace state to side effect → find a sibling implementation → compare. Grep is a starting point, not the hunt.
- **Candidate recall over candidate perfection.** Retain any lead with a concrete boundary and trigger hypothesis, even P3/P4 or medium-confidence. The candidate funnel exists to preserve leads; Bug promotion filters them later. Never silently discard a credible lead.
- **Sibling comparison is the strongest signal.** A Bug is most convincing when you can point at another code path that handles the same scenario correctly. The diff between the two is the Bug.
- **Cross-repo amplification.** When you find a pattern in one repo (same S3 key, same UDS pattern, same eval() usage), check sibling repos. The same team, the same patterns, the same bugs. After agents return, the validator automatically flags cross-repo keyword patterns — review these and dispatch targeted follow-up.
- **Supplemental scans after agents return.** After Phase 6, review agent findings for gaps: what risk surfaces did they not cover? What patterns did they mention in one repo but not check in sibling repos? Run targeted follow-up scans against `repo-scan-roots.txt`. You know what dangerous code looks like in each language — apply your own judgment about what patterns to scan for.
- **Hybrid discovery.** Every non-trivial shard runs two tracks: (1) AI-led code understanding from entry points, call chains, and state boundaries; (2) search-led seed triage from high-recall hits. Shards that only report grep results are weak.
- **Explore before concluding.** Do not announce final Bug totals or coverage classification until shard evidence is complete. Report provisional state: candidates found, areas still open, what's blocked.

### Evidence Integrity (read these when packaging)

- **Authenticity First (overrides every other rule).** Never fabricate code references, commands, or status claims. Read `references/authenticity.md`. "Insufficient evidence" is an acceptable answer; made-up evidence is not.
- **Every finding needs a code anchor.** Candidate bullets in `candidates.md` must include `file:line` references. The validator checks these paths exist.
- **Artifact provenance.** Shard summaries and candidate notes must trace back to exploration evidence. In batch-first-pass mode, converting Agent exploration reports to shard files via deterministic scripts is allowed. Never write from memory or embedded prose. See `references/multi-repo-strategy.md`.
- **Fresh scan, fresh structure.** New audit = new output root, new IDs, new profiles. Historical packages are comparison baselines only.
- **Depth coverage is honest.** `depth-coverage.md` must list every repo with real candidate counts and coverage classification. Never claim "deep complete" unless the validator confirms it.

### Process (apply throughout)

- **Repository roster gate.** For repo groups, freeze the roster with `discover_repositories.py` before any exploration. Scan only against `repo-scan-roots.txt`.
- **High-recall scan.** Scan is post-agent: generate patterns after repo-local exploration reports return, then run `run_high_recall_scan.py --patterns-file <llm-patterns.json>`.
- **Per-repo profile.** Every audited repo gets a `submit/knowledge/repo-profiles/<repo>.md`. Update from shard evidence after exploration.
- **Per-repo shard.** One `work/shards/<repo>/` per repo with `shard-summary.json` and `candidates.md`. Parallel agents write repo-local outputs; coordinator consolidates global outputs.
- **Issue-family coverage.** For deep/high-recall runs, build `quality/issue-family-coverage.md` from the fresh scan. See `references/issue-family-coverage.md`.
- **Language.** Skill and references in English. Final deliverables in the user's language.
- **Static-analysis scope.** All findings are static-analysis until runtime-verified. Prefer infra-stability risks: data integrity, recovery, availability, security boundaries, execution safety.
- **Meta.** Ask only when a decision changes safety or scope. Don't switch branches, infer analyst identity, or add SLA fields. Keep wording natural and developer-facing.

## Run Modes

Every interaction rule in this skill and its references is anchored to one of these three modes. When you read "interactive mode" / "automatic mode" / "checkpointed mode" anywhere in this skill, use the definitions below.

**Mode detection — automatic mode requires an EXPLICIT, UNAMBIGUOUS signal**, not a casual mention of "auto" or its localized equivalents:

- ✅ Triggers automatic mode: standalone directives such as "don't ask me anything", "run autonomously", "fully automatic", or localized equivalents meaning unattended execution; or the agent runtime explicitly declared a non-interactive run.
- ❌ Does NOT trigger automatic mode: casual usage like "auto-format the output" or "automatically generate a Bug list" — here "auto" describes the action, not the interaction style. Treat as **interactive**.
- ⚠️ When in doubt, treat as **interactive**. A false-positive automatic detection silently destroys user trust; a false-positive interactive detection only costs one extra question.

| Mode | Pause for clarification? | Pause for optional companion skills? | Pause for image / scope / analyst decisions? |
|---|---|---|---|
| **interactive** (default) | Yes — pause when the answer materially changes safety, scope, or final package semantics. | Yes — pause once per high-value skill at the phase named in `references/related-skills.md` → "When to Ask (Per-Phase Trigger Table)". | Scope / analyst: yes when user-affecting. Overview image: do not pause at kickoff; mention once and ask only after the validated handoff if it was not already requested. |
| **automatic** (explicit signal only) | No — never pause. Infer safe defaults and record every assumption in `submit/quality/submission-scope.md`. | No — never prompt for installation. Record skipped recommendations under a `skipped recommended skills` note in `submission-scope.md`. | No — apply safe defaults and record them in `submission-scope.md`. |
| **checkpointed** (user requested checkpoints, step-by-step confirmation, or this is a resume) | Yes at declared checkpoints only — phase boundaries by default; otherwise behave like interactive within each chunk. | On resume: do NOT re-prompt for skills already declined in `submission-scope.md`. Otherwise behave like interactive. | Read `submission-scope.md` first; do not re-ask decisions already recorded there. |

A decision is **user-affecting** (and therefore subject to the table above) when it changes any of: audit branch, knowledge file count, Bug priority on a P1/P2 finding, or analyst identity displayed in deliverables. Pure formatting, file-naming, optional overview image timing, or workspace-layout choices are NOT user-affecting — apply safe defaults silently.

## Coverage Depth Modes

These modes control how thoroughly each repo is explored. They are independent of the interaction mode (interactive/automatic/checkpointed).

| Mode | Repos per Session | Per-Repo Depth | Validator Flag |
|---|---|---|---|
| **deep** | 1-10 | Full call-chain tracing, exhaustive seed triage, complete hypothesis loops. Parallel Agents handle up to 10 repos in one session. | `--coverage-mode deep` (default) |
| **batch-first-pass** | 11-25 | AI-led surface mapping + representative seed triage + evidence-backed candidates. Session 1 finds the hot spots; Session 2 deepens them. | `--coverage-mode batch-first-pass` |
| **focused** | 1-5 specific repos within a larger group | Deep on selected repos, zero-finding rationale for rest | `--coverage-mode deep` |
| **lightweight** | 1-25 | Pattern scan only, no shard evidence required | No shard validation |

### When to Recommend Splitting

In **interactive mode**, when the roster has **11 or more repos with source code** and the user requests deep/full coverage, recommend splitting into 2 sessions. Read `references/multi-repo-strategy.md` for the full strategy.

Present a single yes/no question:

> "This group has N repos. A single deep scan would be shallow per repo. Split into M sessions? Session 1: first-pass all repos. Session 2: deepen high-risk ones."

In **automatic mode**, default to `batch-first-pass` for 10+ repo groups and record the choice in `submission-scope.md`.

### batch-first-pass Mode Specifics

- Read `references/multi-repo-strategy.md` and `references/shard-schema.md` before starting.
- Parallel Agent exploration produces narrative reports; converting these to shard JSON/MD is a **legitimate bulk operation** when each artifact's content comes from a named Agent's output. See `references/multi-repo-strategy.md` → "Agent Output Conversion" for safe vs. unsafe patterns.
- Run shard validation with `--coverage-mode batch-first-pass` for relaxed schema requirements.
- `candidates.md` must still have one evidence-bearing bullet per candidate with `path:line` anchors.
- Zero-candidate repos need a concrete rationale naming scanned surfaces.

## Deep Discussion Mode

Use this mode before scanning when analysis intent needs design, not just execution.

Do not enter this mode just because a repository group is large — for 11+ repos, simply recommend splitting per `references/multi-repo-strategy.md` and proceed. Enter this mode only when a decision cannot be safely inferred and materially changes scope, risk classification, package format, or user-facing commitments.

Trigger it for:

- User mentions `$brainstorming` or asks to think, discuss, or design the audit flow before scanning.
- Unclear ownership, unknown risk priorities, or ambiguous output format requirements (not just "many repos").
- The user wants to refine P1-P4 definitions, confidence rules, architecture review style, security scope, package format, image wording, or developer handoff style.
- The task is to improve this Skill or its references/scripts.

In this mode:

- Read `references/deep-discussion.md`.
- If the installed `brainstorming` skill is available, use it to discuss scope, tradeoffs, and deliverable design.
- Keep discussion concrete: produce an analysis charter, not an open-ended brainstorm.
- Ask at most one substantial question at a time unless the user asked for fully automatic execution.
- After the user approves the charter, return to the Workflow Checklist.

## Interaction Policy

For mode-dependent behavior (companion skills, image kickoff, branch confirmation, analyst, automatic-mode defaults), see **Run Modes** above and the per-domain references. The rules below cover only mode-independent interaction discipline:

- Start work with safe assumptions instead of asking formatting or naming questions.
- Ask at most one question per turn; never batch multiple questions.
- Phrase install/decision asks as a single yes/no with the public locator visible (e.g. `op7418/humanizer-zh@humanizer-zh`); do not enumerate every companion skill.
- Never ask whether to continue after each phase unless the user requested checkpoints.
- Keep progress updates to phase boundaries or major assumption changes; do not report every candidate Bug.
- Do not expose `work/` scratch content unless it affects a user decision or the user asks for candidates.

## Workflow Checklist

1. **Set audit charter ⚠️ REQUIRED**
   - Identify target repositories, reference repositories, branch context, output root, provided analyst, analysis date, and package audience.
   - For a directory containing multiple repos, treat the directory as a repo-group root even when the directory itself is not a Git checkout. The repos below it are the audit units.
   - Record explicit requested audit depth intent in `quality/submission-scope.md`: `deep`, `full`, `per-repo-deep`, `first-pass`, `focused`, `lightweight`, or `custom`. If the user asks for "deep", "full", "complete", "尽可能", "每个 repo", or similar wording, this remains the requested deep/full intent until the user accepts a downgrade. Do not rewrite requested intent to `first-pass` just to generate final assets; record delivered coverage separately in `quality/depth-coverage.md`.
   - Record audit metadata and repository version evidence when available; use `references/metadata.md`.
   - Identify current branch, default branch, and stable-branch candidate when evidence is available. For interactive runs, confirm the audit branch baseline before scanning if the user did not provide explicit branches.
   - Decide overview image intent using `references/package-output.md`: requested, recommended, omitted, or deferred-post-handoff. In interactive mode, mention once when `audit-overview.png` is recommended, but do not stop for a yes/no kickoff question. If the user does not explicitly request or decline it, record `deferred-post-handoff` and continue. In automatic mode, apply the default in `package-output.md` and record it in `submission-scope.md`.
   - Treat `bug-audit-report.html` differently from the overview image: it is generated by default for final handoff/report/dashboard packages and does not need a kickoff question. Skip it only for lightweight scans, candidate-only studies, narrow single-Bug reviews, or an explicit no-HTML request.
   - If the user gives no output root, create a descriptive lowercase workspace under the repo group, with `submit/` for final files and `work/` for temporary artifacts.
   - If the output root already exists or the user asks to continue/deepen/review, read `references/resume-audit.md` before changing findings.
   - For repo-group targets, scan the target root for historical audit packages (`*/submit/findings/*.md`, `*bug-audit*`, or previous output roots). Treat them as comparison baselines, not code targets and not scaffolding: do not copy their findings, IDs, profiles, indexes, or report structure into a fresh audit. After the independent scan, review them for omitted issue families and record `reviewed` or `excluded` status in `submission-scope.md` and `depth-coverage.md`.
   - **End of phase**: report a one-line scope summary to the user (interactive/checkpointed) or write the same summary into `submit/quality/submission-scope.md` (automatic), using the final deliverable language. Format in English: `Scope: <repos> · Branch: <branch> · Output: <path> · Image: <included|omitted|deferred-post-handoff>`. This is a report, not a confirmation prompt — do not ask "proceed?".

2. **Initialize workspace ⛔ BLOCKING**
   - Run `scripts/init_bug_workspace.py` through Python explicitly to create the output skeleton.
   - Read `references/package-output.md` for directory and packaging conventions.
   - **Schema smoke test**: after workspace initialization and shard template creation, spot-validate one empty shard template against the schema in `references/shard-schema.md`. Read that reference once now so field names and enum values are known before exploration begins. This prevents discovering 300+ schema errors at Phase 7.
   - Do not write README, final Bug records, final knowledge docs, HTML, or overview image in this phase.

3. **Freeze repo roster ⛔ BLOCKING**
   - For repo-group targets, run `scripts/discover_repositories.py` immediately after workspace creation and store `repo-inventory.json`, `repo-inventory.md`, `repo-shards.md`, `repo-scan-roots.txt`, and empty shard templates under `work/`.
   - Use the frozen roster for `quality/repository-versions.md`, repo briefs/profiles, depth coverage, shard validation, and final validation. Do not discover repos ad hoc later from memory.

4. **Plan repo shards ⛔ BLOCKING**
   - Read `references/depth-coverage.md`. Default decomposition is one repo per shard; batch only tiny, tightly-coupled repos.
   - Mark every shard as `parallel`, `serial`, or `batched` in `work/scanner-output/repo-shards.md` and `work/shards/<repo>/shard-summary.json`.
   - If subagents or parallel tools are available and more than one shard is parallel-eligible, dispatch independent repo shards in parallel. Parallel-eligible serial shards require a concrete `serial_reason`.
   - Global outputs (`submit/findings/`, `quality/lens-coverage.md`, `quality/depth-coverage.md`, indexes, README, HTML, overview image) stay coordinator-owned.

5. **Build repo briefs ⚠️ REQUIRED**
   - Inventory each roster repo just enough to guide exploration: languages, frameworks, entry points, manifests, largest files/functions, external dependencies, background jobs, data stores, execution boundaries, serialization/contracts, lifecycle/recovery surfaces, deployment/runtime assumptions, and verification command sources.
   - Use `references/language-ecosystems.md` to identify build metadata, framework entry points, and evidence-backed verification command sources.
   - Start one `submit/knowledge/repo-profiles/<repo>.md` per roster repo, but treat it as a living profile. Final profiles must be revised from shard evidence, not left as inventory-only templates.
   - Start `submit/quality/depth-coverage.md` for multi-repo/deep runs with roster count, profile count, historical baselines found/reviewed/excluded, and planned shard rows.
   - For detailed mapping, prefer `acquire-codebase-knowledge` if exposed by the runtime, but only run it in a way that does not modify source repos unless the user approves its `docs/codebase/` output. Otherwise use its mapping approach as an accelerator and write the audit-local understanding into `work/shards/`, `work/drafts/knowledge-capture.md`, and `submit/knowledge/repo-profiles/`. If it is not installed and this is a multi-repo or unfamiliar large codebase, follow `references/related-skills.md` → "Use Order" (interactive: ask once with the locator visible; automatic: continue and record in `submission-scope.md`).

6. **Run repo-local shard exploration ⛔ BLOCKING**
   - Read `references/repo-understanding.md` and `references/exploration-methodology.md` before dispatching agents.
   - **Agent dispatch prompts**: for each agent, include (a) repo path, (b) instruction to follow the exploration loop in `exploration-methodology.md`, (c) instruction to produce a structured report with Project Summary, Surface Map, Top Risk Candidates (with file:line evidence), and Repo Profile Data. Agents explore fresh — do NOT give them pre-generated seeds. Seeds are generated AFTER exploration from gap analysis. Do NOT ask agents to write shard files directly — agents explore and report; the coordinator converts reports to shard evidence.
   - Dispatch independent repo shards in parallel if tools allow. Batch small/tightly-coupled repos; large/high-risk repos stay standalone.
   - **After agents return, run supplemental scans.** Review the candidate list for gaps: what risk surfaces did agents not cover? What patterns did agents find in one repo but not check in sibling repos? Run targeted follow-up scans against `repo-scan-roots.txt` to fill the gaps you identify.

7. **Validate shard evidence ⛔ BLOCKING**
   - Run `scripts/validate_bug_package.py <submit-root> --validate-shards-only --repo-root <target-root>` before writing final Bug records or report assets.
   - Fix missing roster entries, missing shard summaries, missing candidate notes, missing scan commands, invalid execution modes, non-existent evidence paths, or weak zero-finding rationales before continuing.
   - If this command prints any `ERROR:` or exits non-zero, stop the final-handoff path. Do not run normal validation as a substitute, do not generate README/HTML/overview assets, and do not claim completion; report the package as `in-progress` with the shard-gate error count.
   - A passing shard gate writes `work/scanner-output/shard-gate.passed.json`; final validation rejects report assets generated before this receipt.

### Session 1 Endpoint (batch-first-pass and first-pass)

After Phase 7 passes with zero evidence errors (warnings are acceptable):
- Run `scripts/generate_candidate_index.py <submit-root>`
- Generate draft HTML: `scripts/generate_bug_report_html.py --allow-ungated-draft --language <zh|en> <submit-root>`
- Write a **session end state** to `work/session-end-state.md`:
  ```markdown
  # Session End State
  - Candidates: <total> across <N> repos
  - Candidate priority mix: P1 <count> · P2 <count> · P3 <count> · P4 <count> · unknown <count>
  - Recommended deepening: <top 5-8 repos by risk>
  - Skipped surfaces: <what wasn't covered>
  - Next session: deepen <repos>, then cross-repo lenses, promotion, package
  ```
- **Stop here.** Phases 8-14 below are for session 2+ (deepening + packaging). Do not execute them in session 1.

### Session 2+: Deepening and Final Packaging

8. **Run cross-repo and META lenses ⚠️ REQUIRED**
   - Re-apply every boundary across sibling repos (see cross-repo amplification in `exploration-lenses.md`).
   - Start each lens with a concrete failure hypothesis, then hunt, refute with sibling implementations, and promote or park the result.
   - Write/update `submit/quality/lens-coverage.md` while the lenses run. Zero-candidate lens records are valid when the scan path and exclusion reason are explicit.
   - Update `submit/quality/depth-coverage.md` as candidates move: every repo needs either submitted Bugs, parked candidates, or an explicit zero-finding rationale with scanned surfaces and remaining gaps.
   - Use `references/risk-taxonomy.md` for categories, P1-P4 definitions, and confidence rules.
   - Use `references/domain-profiles.md` to choose the primary repository lens.
   - Use `references/security-static-analysis.md` for security-specific checks and tool ideas.
   - Use `references/architecture-review.md` for architecture risk signals.
   - Use `references/candidate-triage.md` for weak leads that should not enter submitted findings yet.

9. **Promote, dedupe, and verify candidates ⛔ BLOCKING**
   - For each candidate, prove code evidence, trigger path, impact, affected resource, and realistic failure mode.
   - Use `references/deduplication.md` before creating or splitting a Bug.
   - Lower confidence or move to `work/candidates/` if evidence depends on unverified assumptions.
   - Use `systematic-debugging` style reasoning: root cause first, no speculative fixes.
   - Keep the discovery funnel visible: update shard `candidate_count`, `submitted_bug_ids`, and candidate notes as leads are promoted, parked, refuted, or merged.
   - **Priority Promotion Sweep**: review retained candidates across P1-P4 before finalizing. Candidate notes should expose `priority_estimate`, `outcome`, `bug_gate`, and `missing_gate` when known. Submit lower-priority Bugs when code evidence, trigger path, realistic failure mode, affected resource, and impact are all explicit; park only leads that fail a named gate.
   - Revisit parked P1/P2 leads before freezing counts. Each parked high-priority lead must have a `Promotion Review` entry in the shard candidate file; promote it if the only reason for parking is prioritization or time.
   - A P1-only final package is acceptable only when lower-priority retained candidates are parked/refuted/merged with missing gates, or the user explicitly requested a critical-only scope. Do not stop simply because enough P1 Bugs were found.
   - Freeze final Bug count and dominant issue themes only after every in-scope shard has submitted Bugs, parked candidates, or a concrete zero-finding rationale.

10. **Write final Bug records ⚠️ REQUIRED**
   - Use `references/bug-schema.md` for the Markdown metadata and QA-style sections.
   - Use `references/writing-style.md` to keep wording natural and submission-ready.
   - Include priority, confidence, category, issue family, infra domains, fix risk, evidence, static reproduction path, expected behavior, actual behavior, fix boundary, fix suggestion, suggested verification commands, and validation checks.
   - Sort and name files as `P1-BUG-0001-short-description.md`.
   - On continuation runs, keep existing IDs stable and continue from the current maximum `BUG-xxxx`.
   - Write Bug records as direct Markdown artifacts or one file at a time from promoted candidate notes. Do not embed multiple full Bug records in a Python/JS/shell script.
   - **Final-deliverable Bug IDs must be a single contiguous range `BUG-0001..BUG-N`** — no gaps, no segmentation, no per-agent reserved ranges. If multiple agents ran in parallel and produced segmented IDs (e.g. agent A: `0001-0010`, agent B: `0100-0108`), renumber to a single contiguous sequence before submission. See `references/resume-audit.md` → "Parallel Multi-Agent Consolidation".

11. **Consolidate knowledge and architecture risk ⚠️ REQUIRED**
   - Read `references/knowledge-capture.md`. Promote evidence-backed atoms from `work/drafts/knowledge-capture.md` into `submit/knowledge/`; leave speculative atoms in `work/`.
   - Update `submit/knowledge/` after each evidence-backed Bug batch; final repo knowledge should be complete enough for another Agent to continue without rescanning basics.
   - Do this for multi-repo analysis, repeated issue families, cross-system risk paths, or explicit architecture-review requests.
   - For small single-repo scans with few findings, summarize architecture signals in README instead of creating a large review.
   - Use `references/knowledge-base.md` to check final knowledge completeness.
   - Write `knowledge/architecture-design-review.md` from a discovery perspective.
   - Write architecture signals such as use cases, adapters, Saga/Outbox, and state reconciliation as discovered risk signals, not as commands or abstract principles.

12. **Pre-package validation and evaluation ⛔ BLOCKING**
   - Run `scripts/generate_bug_index.py`.
   - Run `scripts/generate_candidate_index.py <submit-root>` for repo-group, deep/full, or high-recall runs. This creates `indexes/candidates.generated.json`, `indexes/candidates.generated.md`, and `quality/candidate-coverage.md`; final validation rejects repo-group packages when this funnel is missing, inconsistent with shard `candidate_count`, or shows `gate-complete` candidates that remain unsubmitted without a recorded critical-only scope.
   - Validate that `quality/issue-family-coverage.md` exists and covers every required family for repo-group/deep/high-recall packages. A low Bug count is credible only when this file and the candidate funnel explain what was promoted, parked, refuted, or found not applicable.
   - Run a pre-package validation pass with `scripts/validate_bug_package.py --repo-root <path>` after findings and knowledge are current. `<path>` may be either a single repo checkout or a parent directory containing multiple repo checkouts; the validator expands repo-group roots and fails if discovered repos are missing profiles, version evidence, shard evidence, or depth coverage. Lens coverage and default lens completeness are required by default; use `--lens-scope custom` only when `submission-scope.md` declares a narrowed strategy. Use `--skip-lens-coverage` only for in-progress / resume runs, never final handoff. Pass `--repo-root <path>` so frontmatter paths can be verified (see `references/authenticity.md`).
   - For repo-group final packages, validation also checks `work/scanner-output/repo-inventory.json`, `work/scanner-output/repo-shards.md`, `work/scanner-output/repo-scan-roots.txt`, every `work/shards/<repo>/shard-summary.json`, every shard candidates file, and the shard gate receipt. A package with generated-looking final Markdown but missing shard evidence must not pass final handoff.
   - Read `references/evaluation.md`.
   - Evaluate all P1/P2 Bugs; for large packages, also sample each issue family and risk domain.
   - **Failure handling** — if a P1/P2 Bug fails the Bug-Level Gate in `evaluation.md`: apply one of the four documented actions (lower confidence / move to candidates / merge / record uncertainty) per the gate, do NOT pause the run, and log every change in `quality/submission-scope.md`. If pre-package validation returns errors, fix them before generating report assets.
   - Record material downgrades, removals, merges, priority changes, or weak areas in `quality/submission-scope.md`.
   - Fix missing metadata, stale counts, oversize images, old terminology, duplicate content, weak evidence, or priority inflation.
   - A successful pre-package validation before HTML/overview generation writes `work/scanner-output/prepackage-validation.passed.json`; report asset generation requires this receipt.
   - When editing this skill itself, validate `evals/core-regressions.json` and grade any fresh-agent trace with `scripts/grade_eval_trace.py`.

13. **Generate report assets and package ⚠️ REQUIRED FOR FINAL HANDOFF**
   - Only start this phase after shard validation and pre-package validation pass. Report assets are a render layer over final evidence, never a substitute for exploration.
   - `scripts/generate_bug_report_html.py` refuses final HTML generation unless `work/scanner-output/prepackage-validation.passed.json` exists. Use its ungated draft flag only for a clearly labeled non-final draft, never for final handoff.
   - For repo-group audits, `scripts/generate_bug_report_html.py` refuses final HTML generation unless `work/scanner-output/shard-gate.passed.json` exists. Use its ungated draft flag only for a clearly labeled non-final draft, never for final handoff.
   - If audit depth intent is deep/full/per-repo-deep but coverage is `first-pass`, `focused`, or `in-progress`, do not generate final HTML or overview assets until exploration continues or the user explicitly accepts a depth downgrade in `submission-scope.md`.
   - Add `README.md`, indexes, knowledge docs, quality scope, standards, optional `audit-overview.png`, and default `bug-audit-report.html` under `submit/` for final handoff/report packages.
   - If `audit-overview.png` was not requested, continue without it and record `deferred-post-handoff` or an explicit omission in `submission-scope.md`. Do not block the final package on this optional image. Ask after the validated handoff summary whether the user wants the overview image added.
   - If creating `audit-overview.png`, use `references/audit-overview-image.md` for content, layout, color, metadata, and wording constraints.
   - Prefer HTML/CSS screenshot for dense text and exact numbers; native image generation is allowed after visual and data consistency review.
   - For HTML/CSS overview images, verify both the exported PNG and a constrained browser preview; avoid long vertical canvases, stale browser tabs, scrolling screenshots, and fixed canvases that crop in common viewports.
   - **Image verification failure**: if the PNG fails the Quality Gate in `audit-overview-image.md` (clipped content, stale layout, anti-pattern present, wrong counts), regenerate. Cap at 3 regeneration attempts in **all modes** (counting `audit-overview.png` overwrites under `submit/`, not draft iterations under `work/`). After the cap: in automatic mode, omit the image and record `omitted-after-failure` plus the last failure cause in `submission-scope.md`; in interactive/checkpointed mode, surface the last failure in the user's language and ask one yes/no: try native image generation once, or omit the image for this package.
   - Apply `references/writing-style.md` to README, knowledge docs, Bug records, and image text.
   - For final handoff/report packages, create `bug-audit-report.html` by default: read `references/interactive-html-report.md`, then run `scripts/generate_bug_report_html.py <submit-root> --language <zh|en>` after indexes and submitted knowledge are current. Validate with `scripts/validate_bug_package.py --require-html-report`. The report is a self-contained browser delivery layer over final package files, not a replacement for Markdown deliverables.
   - Keep zip packages small; compress images and avoid unused large assets.

14. **Final validation and handoff summary ⛔ BLOCKING**
   - Run final validation after README, indexes, knowledge, `bug-audit-report.html`, and optional `audit-overview.png` are current: `scripts/validate_bug_package.py --require-knowledge --require-html-report --repo-root <path>`. Multi-repo packages with `--require-knowledge` require `quality/depth-coverage.md` by default; pass `--require-depth-coverage` explicitly for any single-repo task that the user called "deep". Add `--require-image` only when `audit-overview.png` is included or explicitly expected.
   - For repo-group audits, a validation command without `--require-knowledge --require-html-report --repo-root <path>` is not a final validation, even if it prints zero errors.
   - After final validation exits 0, give the user a concise handoff summary in the user's language.
   - Include: output root, `bug-audit-report.html` link when generated, `audit-overview.png` state (`included`, `omitted-by-user`, `omitted-as-lightweight-scan`, `omitted-after-failure`, or `deferred-post-handoff`), Bug totals by priority, repo/profile/depth coverage status, coverage classification (`first-pass`, `focused`, or `deep-complete`), and validation result.
   - If overview image was not generated and not explicitly declined, finish the handoff summary first, then ask one short yes/no question about adding `audit-overview.png` as a follow-up artifact.

## Delivery Checklists

### Session 1 (first-pass / batch-first-pass)

- `scripts/validate_bug_package.py --validate-shards-only --repo-root <path>` reports zero evidence errors (warnings acceptable).
- `indexes/candidates.generated.json` and `indexes/candidates.generated.md` exist and match shard `candidate_count`.
- Every roster repo has `work/shards/<repo>/shard-summary.json` and `work/shards/<repo>/candidates.md` with code-anchored candidate bullets or a zero-finding rationale naming scanned surfaces.
- `submit/quality/depth-coverage.md` lists every repo with candidate counts and coverage classification.
- `work/session-end-state.md` records candidate totals, P1/P2 hotspots, and recommended repos for session 2 deepening.
- Draft `bug-audit-report.html` generated with `--allow-ungated-draft`.

### Final Session (deep-complete package)

- `scripts/validate_bug_package.py --require-knowledge --require-html-report --repo-root <path>` reports zero errors.
- `submit/quality/submission-scope.md` records depth intent; delivered coverage matches or has user-accepted downgrade.
- Every submitted Bug has: P1-P4 priority, confidence, `status=open`, `source=static-analysis`, code evidence, static reproduction path, fix boundary, and suggested verification commands.
- `quality/candidate-coverage.md` includes the Priority Promotion Sweep, and no `gate-complete` P1-P4 candidate remains unsubmitted unless `submission-scope.md` records a critical-only scope.
- P1/P2 Bugs pass `references/evaluation.md` gates.
- `submit/quality/lens-coverage.md` covers every enabled lens. `submit/quality/issue-family-coverage.md` covers every required family.
- For repo-group: Bug IDs are one contiguous range `BUG-0001..BUG-N`. Global outputs merged serially.
- Every repo has a `submit/knowledge/repo-profiles/<repo>.md` profile.
- `bug-audit-report.html` is current and generated without `--allow-ungated-draft`.
- Optional `audit-overview.png` follows `references/audit-overview-image.md` if included.
- Package text avoids AI-flavored phrasing per `references/writing-style.md`.

## Tooling Guidance

- Use `rg` / `rg --files` for searches when available.
- Read `references/cross-platform.md` before running shell commands on Windows, Linux, macOS, or when a suggested command fails.
- Run bundled scripts through Python explicitly; do not rely on Unix executable bits or shebang behavior.
- Use Semgrep, CodeQL, dependency scanners, secret scanners, or language-native linters when available, but never submit raw tool output without human triage.
- Use multiple passes: broad pattern search, module-level tracing, cross-repo call-chain review, then false-positive pass.
- For large repo groups, analyze by domain and boundary: compute, storage, network, deployment/runtime, identity, billing, monitoring/recovery, UI/API, execution, serialization/contracts, and cross-repo consistency.

## Related Skills and References

- Read `references/related-skills.md` when deciding whether to combine this skill with runtime or public companion skills.
- Read `references/agent-compatibility.md` when packaging, sharing, or adapting this skill for another Agent Skills-compatible client.
- Read only the reference files needed for the current task; keep context small.

## Bundled Resources

- `scripts/init_bug_workspace.py` — create output directories and baseline docs.
- `scripts/discover_repositories.py` — discover and freeze a repo-group roster and source scan roots from a repo checkout or parent directory containing multiple repo checkouts.
- `scripts/run_high_recall_scan.py` — run roster-safe supplemental search seeds from `repo-scan-roots.txt` and an LLM-generated `--patterns-file` without scanning historical audit outputs.
- `scripts/generate_bug_index.py` — build Markdown/JSON indexes from Bug records.
- `scripts/generate_bug_report_html.py` — build a self-contained interactive `bug-audit-report.html` from final package files.
- `scripts/validate_bug_package.py` — verify package structure, evidence paths, candidate count consistency, shard evidence honesty, and cross-repo pattern detection without prescribing Bug discovery routes.
- `scripts/generate_candidate_index.py` — build candidate pool indexes from shard evidence.
- `scripts/generate_session_handoff.py` — generate a session 1→2 deepening plan from candidate index and shard summaries.
- `scripts/grade_eval_trace.py` — replay-grade stored fresh-agent transcripts and output artifacts against portable eval cases.
- `evals/core-regressions.json` — five portable regression cases for multi-repo depth, forbidden package writers, default HTML/optional image, single-repo lightweight scans, and historical-baseline fresh rescans.
- `references/workflow.md` — full multi-pass workflow.
- `references/authenticity.md` — **Authenticity First rule**, anti-fabrication categories, honest-uncertainty markers, per-output rules, and validator/evaluator enforcement levels.
- `references/exploration-lenses.md` — **13 architecture boundaries** that guide exploration without hardcoded patterns. plus cross-repo amplification.
- `references/repo-understanding.md` — per-repo surface map and hypothesis-loop contract used before Bug hunting.
- `references/repo-profile.md` — per-repo profile spec (5 boundary types, Intent Inputs for META-1, Mermaid call graph or small-repo exemption).
- `references/call-graph-conventions.md` — Mermaid call graph guardrails (edge evidence, ≤30 nodes, ≤4 depth, dashed unconfirmed, uncovered area, small-repo exemption).
- `references/deep-discussion.md` — analysis charter and brainstorming prompts.
- `references/resume-audit.md` — continue an existing audit, keep IDs stable, and record downgrade/removal reasons.
- `references/evaluation.md` — Bug-level, package-level, depth, priority, and skill-regression evaluation gates.
- `references/depth-coverage.md` — multi-repo/deep coverage ledger: repo inventory, historical baselines, per-repo coverage, zero-finding rationale, and final depth claim rules.
- `references/issue-family-coverage.md` — fresh-run risk-family coverage matrix for deep/high-recall audits.
- `references/metadata.md` — audit metadata and repository version evidence standard.
- `references/knowledge-base.md` — minimal discovery map and final reusable repo knowledge standard.
- `references/knowledge-capture.md` — capture and promote reusable facts learned during exploration.
- `references/bug-schema.md` — Bug record schema and example.
- `references/risk-taxonomy.md` — priorities, confidence, categories, and sorting.
- `references/domain-profiles.md` — domain-specific audit lenses for infra, backend, frontend, SDK, mobile, and generic repositories.
- `references/language-ecosystems.md` — language/build-system discovery, entry-point hints, verification command evidence, and language-specific false-positive checks.
- `references/candidate-triage.md` — candidate lead format and promotion rules.
- `references/deduplication.md` — merge/split rules for repeated findings.
- `references/architecture-review.md` — architecture-risk analysis vocabulary.
- `references/security-static-analysis.md` — security checks and scanner workflow.
- `references/writing-style.md` — natural developer-facing wording rules and banned AI-flavored phrases.
- `references/package-output.md` — final package structure and README/image conventions.
- `references/audit-overview-image.md` — `audit-overview.png` content, layout, color, and metadata rules.
- `references/interactive-html-report.md` — `bug-audit-report.html` content, interaction, provenance, design, and validation rules.
- `references/cross-platform.md` — Windows/Linux/macOS command, Python, path, and archive guidance.
- `references/related-skills.md` — optional companion skills, public locators, `npx -y skills` commands, and audit lenses.
- `references/exploration-methodology.md` — exploration loop, agent dispatch templates, and methodology for maximizing Bug discovery through deep code reading.
- `references/shard-schema.md` — canonical schema for shard-summary.json and candidates.md.
- `references/multi-repo-strategy.md` — multi-session strategy, Agent output conversion rules, and session split recommendations.
