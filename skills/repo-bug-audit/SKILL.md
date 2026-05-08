---
name: repo-bug-audit
description: Use when an agent needs repository-level Bug audits, static-analysis Bug discovery, architecture/security/reliability risk review, cross-repo relationship mapping, false-positive triage, deduplication, incremental/resume audits, evidence-backed Bug records, reusable repo knowledge, or fix-ready Bug audit outputs.
---

# Repo Bug Audit

IRON LAW: Do not submit a Bug unless code evidence, trigger path, realistic failure mode, and impact are all explicit.

## Purpose

Find evidence-backed Bugs and architecture risk signals across one or more repositories, then package the results so developers or later Agents can review, reproduce, triage, and fix them safely.

This skill is review-first. Do not patch code unless the user explicitly asks for fixes after the analysis.

## Operating Rules

- **Authenticity First (overrides every other rule)**: never fabricate code references, commands, metrics, status claims, or filler content to satisfy any thickness or completeness requirement. Lower priority, move to candidates, shorten the section, or write an explicit honest-uncertainty marker (`insufficient evidence`, `static analysis cannot confirm`, `unconfirmed`). This rule applies to **every output under `submit/`** — Bug records, README, knowledge docs, repo profiles, architecture review, audit-overview image, submission-scope. Read `references/authenticity.md` before writing anything submittable.
- **Language policy**: skill instructions, reference methodology, and exploration notes are written in English. Final deliverables under `submit/` use the requested language; if the user is Chinese and does not specify otherwise, default final deliverables to Chinese. Preserve code identifiers, file paths, commands, API names, and frontmatter enum values exactly.
- **Lens-based exploration**: a lens is a risk perspective for the audit phase: state a concrete failure hypothesis, collect code evidence, refute with sibling implementations, then promote or park candidates. Phase 2 is not a single grep pass; read `references/exploration-lenses.md` first, then the relevant split lens files (`lenses-tier1.md`, `lenses-tier2.md`, `lenses-tier3.md`, `lenses-meta.md`). Single-repo default = Tier 1 + Tier 2 + META; multi-repo default = Tier 1 + Tier 2 + Tier 3 + META. Every enabled lens needs a 5-section record in `submit/quality/lens-coverage.md`. "Applied and found no Bug" is legitimate — never invent findings to fill coverage.
- **Per-repo profile**: every audited repo must have one `submit/knowledge/repo-profiles/<repo>.md` per `references/repo-profile.md`. Include a Mermaid call graph that follows `references/call-graph-conventions.md`, except ≤10-file utility repos may use the documented call-graph exemption. Profile is the input substrate for Tier 3 lens and META-1.
- **Exploration knowledge capture**: when exploration reveals reusable repo facts, write short atoms to `work/drafts/knowledge-capture.md` per `references/knowledge-capture.md`, then promote evidence-backed atoms into `submit/knowledge/`. Do not dump raw exploration notes into final knowledge.
- **Pluggable strategy**: default lens scope follows `references/exploration-lenses.md` (single-repo vs multi-repo). When the user specifies a different strategy (e.g. OWASP ASVS, internal checklist, lens subset), record the choice as a free-form paragraph in `submit/quality/submission-scope.md` (no structured field needed); execute lens coverage according to the declared subset.
- Treat findings as static-analysis results until runtime validation proves otherwise.
- Prefer fewer real Bugs over hundreds of weak claims; keep weak leads in `work/candidates/`, not submitted findings.
- Prioritize infra-stability risks: data integrity, recovery, availability, resource leakage, storage/network performance, control-plane safety, security boundaries, and cross-system consistency.
- Use Deep Discussion Mode when the user explicitly asks for `$brainstorming`, when scope/output/risk definitions are still unstable, or when evolving this skill itself.
- Skip Deep Discussion Mode when the user asks for full automatic execution; apply the default workflow and keep progress moving.
- Treat related skills as optional accelerators, not hard dependencies; encourage installation only when they materially improve the current task.
- Infer safe defaults first. Ask the user only when a missing answer changes safety, scope, or final package semantics.
- Treat branch selection as audit scope. Branch handling per mode is defined in **Run Modes** and `references/metadata.md`; never switch branches without approval.
- Do not infer analyst or author identity from OS username, Git config, directory owner, or model identity; use a provided value or mark it missing.
- Use the language policy above for deliverables. Keep wording natural and developer-facing; avoid meta, self-referential, inflated, or AI-flavored language.
- Keep the skill itself reusable and neutral; do not hardcode real project names, company names, personal names, or analyst identifiers in instructions or examples.
- Do not include SLA fields in Bug records unless the user asks for process management data.
- Use Markdown files with embedded metadata; do not create separate YAML files for individual Bugs.
- Never delete or modify files outside the requested working/output directory unless explicitly asked.

## Run Modes

Every interaction rule in this skill and its references is anchored to one of these three modes. When you read "interactive mode" / "automatic mode" / "checkpointed mode" anywhere in this skill, use the definitions below.

**Mode detection — automatic mode requires an EXPLICIT, UNAMBIGUOUS signal**, not a casual mention of "auto" or its localized equivalents:

- ✅ Triggers automatic mode: standalone directives such as "don't ask me anything", "run autonomously", "fully automatic", or localized equivalents meaning unattended execution; or the agent runtime explicitly declared a non-interactive run.
- ❌ Does NOT trigger automatic mode: casual usage like "auto-format the output" or "automatically generate a Bug list" — here "auto" describes the action, not the interaction style. Treat as **interactive**.
- ⚠️ When in doubt, treat as **interactive**. A false-positive automatic detection silently destroys user trust; a false-positive interactive detection only costs one extra question.

| Mode | Pause for clarification? | Pause for optional companion skills? | Pause for image / scope / analyst decisions? |
|---|---|---|---|
| **interactive** (default) | Yes — pause when the answer materially changes safety, scope, or final package semantics. | Yes — pause once per high-value skill at the phase named in `references/related-skills.md` → "When to Ask (Per-Phase Trigger Table)". | Yes — pause once at Phase 1 kickoff if the choice changes the final package shape. |
| **automatic** (explicit signal only) | No — never pause. Infer safe defaults and record every assumption in `submit/quality/submission-scope.md`. | No — never prompt for installation. Record skipped recommendations under a `skipped recommended skills` note in `submission-scope.md`. | No — apply the documented automatic-mode default and record it in `submission-scope.md`. |
| **checkpointed** (user requested checkpoints, step-by-step confirmation, or this is a resume) | Yes at declared checkpoints only — phase boundaries by default; otherwise behave like interactive within each chunk. | On resume: do NOT re-prompt for skills already declined in `submission-scope.md`. Otherwise behave like interactive. | Read `submission-scope.md` first; do not re-ask decisions already recorded there. |

A decision is **user-affecting** (and therefore subject to the table above) when it changes any of: audit branch, package shape (image/no-image, knowledge file count), Bug priority on a P1/P2 finding, or analyst identity displayed in deliverables. Pure formatting, file-naming, or workspace-layout choices are NOT user-affecting — apply safe defaults silently.

## Deep Discussion Mode

Use this mode before scanning when analysis intent needs design, not just execution.

Do not enter this mode just because a repository group is large. Enter it only when a decision cannot be safely inferred and materially changes scope, risk classification, package format, or user-facing commitments.

Trigger it for:

- User mentions `$brainstorming` or asks to think, discuss, or design the audit flow before scanning.
- The target includes many repositories, unknown ownership, unclear priorities, or multiple possible output formats.
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

1. **Set scope ⚠️ REQUIRED**
   - Identify target repositories, reference repositories, branch context, output root, provided analyst, analysis date, and package audience.
   - Record audit metadata and repository version evidence when available; use `references/metadata.md`.
   - Identify current branch, default branch, and stable-branch candidate when evidence is available. For interactive runs, confirm the audit branch baseline before scanning if the user did not provide explicit branches.
   - Decide overview image intent using `references/package-output.md`: requested, recommended, omitted, or unknown. In interactive mode, ask once at this phase if the answer changes the final package shape; in automatic mode, apply the default in `package-output.md` and record it in `submission-scope.md`.
   - Treat `bug-audit-report.html` differently from the overview image: it is generated by default for final handoff/report/dashboard packages and does not need a kickoff question. Skip it only for lightweight scans, candidate-only studies, narrow single-Bug reviews, or an explicit no-HTML request.
   - If the user gives no output root, create a descriptive lowercase workspace under the repo group, with `submit/` for final files and `work/` for temporary artifacts.
   - If the output root already exists or the user asks to continue/deepen/review, read `references/resume-audit.md` before changing findings.
   - **End of phase**: report a one-line scope summary to the user (interactive/checkpointed) or write the same summary into `submit/quality/submission-scope.md` (automatic), using the final deliverable language. Format in English: `Scope: <repos> · Branch: <branch> · Output: <path> · Image: <included|omitted|pending>`. This is a report, not a confirmation prompt — do not ask "proceed?".

2. **Initialize workspace ⛔ BLOCKING**
   - Run `scripts/init_bug_workspace.py` through Python explicitly to create the output skeleton.
   - Read `references/package-output.md` for directory and packaging conventions.

3. **Build minimal knowledge map ⚠️ REQUIRED**
   - Inventory languages, frameworks, entry points, largest files/functions, external dependencies, background jobs, data stores, and risky integration points.
   - Use `references/language-ecosystems.md` to identify build metadata, framework entry points, and evidence-backed verification command sources.
   - Read `references/repo-profile.md` and write/update one `submit/knowledge/repo-profiles/<repo>.md` for every audited repo before Phase 2. Use `org__repo.md` for `org/repo` scope names.
   - Include the 5 boundary inventories, Intent Inputs, Verification Sources, Risk Surfaces, and a Mermaid call graph per `references/call-graph-conventions.md`, unless the repo qualifies for the documented ≤10-file small-repo exemption.
   - Build enough repo relationship and risk-path knowledge to choose high-risk paths; do not wait for a complete knowledge base before hunting Bugs.
   - Use `references/knowledge-base.md` to separate minimal discovery knowledge from final submitted knowledge.
   - For detailed mapping, prefer `acquire-codebase-knowledge` if exposed by the runtime. If it is not installed and this is a multi-repo or unfamiliar large codebase, follow `references/related-skills.md` → "Use Order" (interactive: ask once with the locator visible; automatic: continue and record in `submission-scope.md`).

4. **Hunt candidates by risk lens ⚠️ REQUIRED**
   - Read `references/exploration-lenses.md` first. Load `lenses-tier1.md`, `lenses-tier2.md`, `lenses-meta.md`, and, for multi-repo audits, `lenses-tier3.md`.
   - Start each lens with a concrete failure hypothesis, then hunt, refute with sibling implementations, and promote or park the result.
   - Write/update `submit/quality/lens-coverage.md` while the lenses run. Zero-candidate lens records are valid when the scan path and exclusion reason are explicit.
   - Capture reusable exploration facts in `work/drafts/knowledge-capture.md` using `references/knowledge-capture.md`: entry points, boundaries, state owners, invariants, false-positive guards, verification sources, risk paths, and uncovered areas.
   - Use `references/risk-taxonomy.md` for categories, P1-P4 definitions, and confidence rules.
   - Use `references/domain-profiles.md` to choose the primary repository lens.
   - Use `references/security-static-analysis.md` for security-specific checks and tool ideas.
   - Use `references/architecture-review.md` for architecture risk signals.
   - Use `references/candidate-triage.md` for weak leads that should not enter submitted findings yet.

5. **Verify before submitting ⛔ BLOCKING**
   - For each candidate, prove code evidence, trigger path, impact, affected resource, and realistic failure mode.
   - Use `references/deduplication.md` before creating or splitting a Bug.
   - Lower confidence or move to `work/candidates/` if evidence depends on unverified assumptions.
   - Use `systematic-debugging` style reasoning: root cause first, no speculative fixes.

6. **Write Bug records ⚠️ REQUIRED**
   - Use `references/bug-schema.md` for the Markdown metadata and QA-style sections.
   - Use `references/writing-style.md` to keep wording natural and submission-ready.
   - Include priority, confidence, category, issue family, infra domains, fix risk, evidence, static reproduction path, expected behavior, actual behavior, fix boundary, fix suggestion, suggested verification commands, and validation checks.
   - Sort and name files as `P1-BUG-0001-short-description.md`.
   - On continuation runs, keep existing IDs stable and continue from the current maximum `BUG-xxxx`.
   - **Final-deliverable Bug IDs must be a single contiguous range `BUG-0001..BUG-N`** — no gaps, no segmentation, no per-agent reserved ranges. If multiple agents ran in parallel and produced segmented IDs (e.g. agent A: `0001-0010`, agent B: `0100-0108`), renumber to a single contiguous sequence before submission. See `references/resume-audit.md` → "Parallel Multi-Agent Consolidation".

7. **Consolidate knowledge and architecture risk ⚠️ REQUIRED**
   - Read `references/knowledge-capture.md`. Promote evidence-backed atoms from `work/drafts/knowledge-capture.md` into `submit/knowledge/`; leave speculative atoms in `work/`.
   - Update `submit/knowledge/` after each evidence-backed Bug batch; final repo knowledge should be complete enough for another Agent to continue without rescanning basics.
   - Do this for multi-repo analysis, repeated issue families, cross-system risk paths, or explicit architecture-review requests.
   - For small single-repo scans with few findings, summarize architecture signals in README instead of creating a large review.
   - Use `references/knowledge-base.md` to check final knowledge completeness.
   - Write `knowledge/architecture-design-review.md` from a discovery perspective.
   - Write architecture signals such as use cases, adapters, Saga/Outbox, and state reconciliation as discovered risk signals, not as commands or abstract principles.

8. **Generate indexes, validate, and evaluate ⛔ BLOCKING**
   - Run `scripts/generate_bug_index.py`.
   - Run `scripts/validate_bug_package.py`. Lens coverage and default lens completeness are required by default; use `--lens-scope custom` only when `submission-scope.md` declares a narrowed strategy. Use `--skip-lens-coverage` only for in-progress / resume runs, never final handoff. Pass `--repo-root <path>` (repeatable) so the validator can verify every frontmatter `files[].path` exists in the audited repo(s) — this catches fabricated code references (see `references/authenticity.md`).
   - For final handoff/report packages, run `scripts/validate_bug_package.py --require-knowledge --require-html-report --repo-root <path>`. Add `--require-image` only when `audit-overview.png` is included or explicitly expected.
   - Read `references/evaluation.md`.
   - Evaluate all P1/P2 Bugs; for large packages, also sample each issue family and risk domain.
   - **Failure handling** — if a P1/P2 Bug fails the Bug-Level Gate in `evaluation.md`: apply one of the four documented actions (lower confidence / move to candidates / merge / record uncertainty) per the gate, do NOT pause the run, and log every change in `quality/submission-scope.md`. If `validate_bug_package.py` returns errors, fix them before submitting; the script must exit 0 on the final package.
   - Record material downgrades, removals, merges, priority changes, or weak areas in `quality/submission-scope.md`.
   - Fix missing metadata, stale counts, oversize images, old terminology, duplicate content, weak evidence, or priority inflation.

9. **Package (conditional)**
   - Add `README.md`, indexes, knowledge docs, quality scope, standards, optional `audit-overview.png`, and default `bug-audit-report.html` under `submit/` for final handoff/report packages.
   - If creating `audit-overview.png`, use `references/audit-overview-image.md` for content, layout, color, metadata, and wording constraints.
   - Prefer HTML/CSS screenshot for dense text and exact numbers; native image generation is allowed after visual and data consistency review.
   - For HTML/CSS overview images, verify both the exported PNG and a constrained browser preview; avoid long vertical canvases, stale browser tabs, scrolling screenshots, and fixed canvases that crop in common viewports.
   - **Image verification failure**: if the PNG fails the Quality Gate in `audit-overview-image.md` (clipped content, stale layout, anti-pattern present, wrong counts), regenerate. Cap at 3 regeneration attempts in **all modes** (counting `audit-overview.png` overwrites under `submit/`, not draft iterations under `work/`). After the cap: in automatic mode, omit the image and record `omitted-after-failure` plus the last failure cause in `submission-scope.md`; in interactive/checkpointed mode, surface the last failure in the user's language and ask one yes/no: try native image generation once, or omit the image for this package.
   - Apply `references/writing-style.md` to README, knowledge docs, Bug records, and image text.
   - For final handoff/report packages, create `bug-audit-report.html` by default: read `references/interactive-html-report.md`, then run `scripts/generate_bug_report_html.py <submit-root> --language <zh|en>` after indexes and submitted knowledge are current. Validate with `scripts/validate_bug_package.py --require-html-report`. The report is a self-contained browser delivery layer over final package files, not a replacement for Markdown deliverables.
   - Keep zip packages small; compress images and avoid unused large assets.

## Pre-Delivery Checklist

- `scripts/validate_bug_package.py` reports zero errors.
- `indexes/findings.generated.md` and `indexes/findings.generated.json` are current.
- Every submitted Bug has P1-P4 priority, high/medium/low confidence, `status=open`, and `source=static-analysis`.
- Every submitted Bug has code evidence, static reproduction path, false-positive review, fix boundary, fix suggestion, suggested verification commands, and validation standard.
- P1/P2 Bugs pass `references/evaluation.md` priority and evidence gates.
- Large packages have issue-family and risk-domain samples checked through `references/evaluation.md`.
- `work/candidates/` contains weak leads instead of mixing them into submitted findings.
- Exploration knowledge atoms from `work/drafts/knowledge-capture.md` have been promoted, parked, or removed; final `submit/knowledge/` is not just initial inventory.
- Candidate notes follow the lightweight format in `references/candidate-triage.md`.
- Duplicate Bugs have been merged or moved to `work/candidates/`.
- `work/` is excluded from the final zip/package.
- Every audited repo has a `submit/knowledge/repo-profiles/<repo>.md` profile with boundary sections, verification sources, risk surfaces, finding/candidate links, and either a Mermaid call graph or the documented small-repo exemption.
- `submit/quality/lens-coverage.md` records every enabled lens for the declared strategy: default single-repo = L1-L14 + META; default multi-repo = L1-L19 + META.
- Custom or lightweight final packages pass validation with `--lens-scope custom` only when `submit/quality/submission-scope.md` names the narrowed strategy.
- Final `submit/knowledge/` meets `references/knowledge-base.md`; remove empty or repetitive optional files before packaging.
- For large or multi-repo packages, `scripts/validate_bug_package.py --require-knowledge` passes.
- If `audit-overview.png` is part of the package, image content follows `references/audit-overview-image.md`.
- If `audit-overview.html` is used to create the image, a common browser viewport can show the whole artboard without clipping, and the final PNG is visually reviewed for compression, overlap, stale layout, and accidental empty space.
- Final handoff/report packages include `bug-audit-report.html` unless explicitly omitted or recorded as a lightweight scan. The report follows `references/interactive-html-report.md`, is self-contained, exposes `repo-bug-audit`, `github.com/aiden0z/skills`, and `source=static-analysis`, and passes `validate_bug_package.py --require-html-report`.
- README counts match generated indexes.
- `quality/repository-versions.md` records branch, commit hash, and dirty status when available; missing version evidence is marked rather than guessed.
- Package text avoids banned/meta wording and project-specific residue.
- Package text has no process explanation, self-reference, vague summary claims, or AI-flavored phrasing.
- Images are compressed and no unused large assets remain.

## Tooling Guidance

- Use `rg` / `rg --files` for searches when available.
- Read `references/cross-platform.md` before running shell commands on Windows, Linux, macOS, or when a suggested command fails.
- Run bundled scripts through Python explicitly; do not rely on Unix executable bits or shebang behavior.
- Use Semgrep, CodeQL, dependency scanners, secret scanners, or language-native linters when available, but never submit raw tool output without human triage.
- Use multiple passes: broad pattern search, module-level tracing, cross-repo call-chain review, then false-positive pass.
- For large repo groups, analyze by domain: compute, storage, network, deployment, identity, billing, monitoring, UI/API.

## Related Skills and References

- Read `references/related-skills.md` when deciding whether to combine this skill with runtime or public companion skills.
- Read `references/agent-compatibility.md` when packaging, sharing, or adapting this skill for another Agent Skills-compatible client.
- Read only the reference files needed for the current task; keep context small.

## Bundled Resources

- `scripts/init_bug_workspace.py` — create output directories and baseline docs.
- `scripts/generate_bug_index.py` — build Markdown/JSON indexes from Bug records.
- `scripts/generate_bug_report_html.py` — build a self-contained interactive `bug-audit-report.html` from final package files.
- `scripts/validate_bug_package.py` — verify package structure, metadata, terminology, image sizes; with `--repo-root` also enforces frontmatter path existence and cross-Bug literal-duplicate detection (Authenticity First).
- `references/workflow.md` — full multi-pass workflow.
- `references/authenticity.md` — **Authenticity First rule**, anti-fabrication categories, honest-uncertainty markers, per-output rules, and validator/evaluator enforcement levels.
- `references/exploration-lenses.md` — **lens-based exploration entry point**: default scope, hypothesis-first / sibling-diff loop, 5-section application record format, pluggable strategy, and links to split lens files.
- `references/lenses-tier1.md` — L1-L7 single-file / single-function surface lens.
- `references/lenses-tier2.md` — L8-L14 cross-file / cross-module lens.
- `references/lenses-tier3.md` — L15-L19 cross-repo / architecture boundary lens.
- `references/lenses-meta.md` — META-1 / META-2 global contrast scans.
- `references/repo-profile.md` — per-repo profile spec (5 boundary types, Intent Inputs for META-1, Mermaid call graph or small-repo exemption).
- `references/call-graph-conventions.md` — Mermaid call graph guardrails (edge evidence, ≤30 nodes, ≤4 depth, dashed unconfirmed, uncovered area, small-repo exemption).
- `references/deep-discussion.md` — analysis charter and brainstorming prompts.
- `references/resume-audit.md` — continue an existing audit, keep IDs stable, and record downgrade/removal reasons.
- `references/evaluation.md` — Bug-level, package-level, depth, priority, and skill-regression evaluation gates.
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
- `references/agent-compatibility.md` — installation boundary, portability rules, and cross-agent behavior.
