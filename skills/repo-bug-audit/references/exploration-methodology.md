# Exploration Methodology

This is not a bug pattern catalog. LLMs already know what `eval()`, `pickle.loads()`, and `dangerouslySetInnerHTML` do. This document is about **how to explore** — how to read code in a way that maximizes credible Bug discovery.

## Core Principle

Bug discovery is proportional to **code read × call chains traced × sibling comparisons made**. A grep hit is a starting point, not a finding. A Bug is only real when you've read the surrounding 50 lines, traced the input to its source, and checked whether the sibling code does the same thing differently.

## Exploration Loop

For each repo, run this loop on every non-trivial surface (entry points, state owners, execution boundaries, external integrations):

1. **Pick a surface.** Start from an HTTP endpoint, message handler, cron job, or CLI entry point.
2. **Trace input to state.** Follow the request/event data from entry to where it touches a database, cache, queue, or filesystem. Read every function in between.
3. **Trace state to side effect.** From the state mutation, trace to the external effect: what API is called, what file is written, what process is spawned.
4. **Find the sibling.** Look for 1-2 other places in the codebase that do the same thing (same API call pattern, same DB operation, same file I/O). If the sibling has a guard (timeout, validation, error handling) that this path lacks, you've found a Bug.
5. **Hypothesize and refute.** Form a concrete failure hypothesis. Try to kill it: is there a framework middleware that catches this? A try/except higher in the stack? A config gate? If the hypothesis survives refutation, it's a candidate.

## What NOT to Do

- **Don't grep-and-report.** A grep hit for `eval(` is not a Bug. Read the 50 lines around it. What is the input? Where does it come from? Is there a guard?
- **Don't scan one surface and move on.** The first `eval()` in a repo is a signal. Find every other `eval()` in the same repo. Compare them. The Bug is in the difference.
- **Don't trust the first guard you see.** "There's a try/except" — read the except block. Is it `pass`? Does it log and continue with corrupted state? Guards can be the Bug.

## Cross-Repo Amplification

When you find a pattern in one repo (e.g., "all Python services use `multiprocessing.connection` over a world-readable UDS"), check the sibling repos. The same team, the same patterns, the same bugs. A finding in repo A is a hypothesis for repo B.

## Time Allocation

For a typical repo (50-200 source files), spend:
- 30% reading entry points and tracing call chains
- 30% hunting across surfaces from repo understanding; supplemental high-recall seeds are reviewed after the first exploration pass
- 20% sibling comparison and refutation
- 20% writing candidate notes with code evidence

If you're spending more than 10% of time on grep or pattern matching, you're not reading enough code.

## Agent Dispatch Template

When dispatching exploration agents, use this structure. Fill in the bracketed values from the repo brief. Do not give agents pre-generated high-recall seeds; the first pass should reveal repo-specific gaps that later become LLM-generated scan patterns.

```
You are exploring the [repo-name] repository as part of a bug audit.
RESEARCH ONLY — do not write any files. Read code, identify risks, report back.

Repo path: [absolute-path]

Your job: read enough code to understand what this service does, how it's built,
and where it might fail. You already know what dangerous patterns look like —
trust your expertise. Don't checklist your way through. Read code deeply.

For each risk you find:
- Trace the full path from entry point to risky operation
- Find at least one sibling implementation that does it differently (or correctly)
- If the sibling has a guard this path lacks, that's a real finding
- If you can't trace the full chain, mark it as "needs deeper tracing"

Report in this structure:
- **Project Summary**: Purpose, frameworks, data stores, key dependencies (3-5 lines)
- **Surface Map**: Entry points, auth, state, integrations, execution boundaries, config, file I/O — each with file:line references
- **Top Risk Candidates** (as many as you find): For each: hypothesis, code evidence (file:line), trigger path, failure mode, priority (P1-P4). Include medium-confidence leads — don't self-censor.
- **Repo Profile Data**: Languages, build system, Dockerfile review, key config locations
```

### Single-repo vs batch

- **Single repo**: one agent, one repo. The agent reads 50-200 files over 30-60 minutes.
- **Batch (2-4 small repos)**: one agent, multiple repos. Explicitly tell the agent to switch repos after finding the first 3-5 candidates in each. The goal is broad first-pass coverage, not exhaustive depth.
- **Large repos (>500 files)**: one agent, one repo, but tell it to prioritize high-risk surfaces (auth, execution boundaries, config, external integrations) and skip exhaustive coverage of CRUD controllers, DTOs, and generated code.
