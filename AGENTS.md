# AGENTS.md

This file provides guidance to AI coding agents working with this repository.

## Repository Overview

A collection of production-grade Agent Skills. Each skill is a self-contained directory under `skills/` with a `SKILL.md` entry point.

## Available Skills

| Skill | Directory | Description |
|-------|-----------|-------------|
| Email Designer | `skills/email-designer/` | Generate Outlook-compatible email templates (EML + HTML) |
| Repo Bug Audit | `skills/repo-bug-audit/` | Evidence-backed repository Bug audits and audit packages |
| Skill Evaluator | `skills/skill-evaluator/` | Review, harden, and regression-test Agent Skills |
| VibeDeck | `skills/vibe-deck/` | Vibe-code professional slide presentations |

## How to Use a Skill

1. Read the skill's `SKILL.md` for instructions
2. Follow the workflow defined in the skill
3. Reference files in the skill's subdirectories as directed by SKILL.md

## Skill Structure Convention

```
skills/
  {skill-name}/
    SKILL.md              # Required: skill entry point
    reference/            # Optional: supporting documentation
    scripts/              # Optional: executable helpers
    templates/            # Optional: reusable templates
    examples/             # Optional: reference outputs
```

Do not place human-facing README files, design notes, planning drafts, or temporary generated documents inside `skills/{skill-name}/`. A skill package should contain only files needed by agent runtimes and installers.

Use this documentation rule:

- `docs/` is ignored by default and may contain design notes, maintenance docs, specs, rationale, temporary generated docs, brainstorming drafts, and local working material.
- Do not commit `docs/` content by default. Only commit a specific docs file when the user explicitly asks for that document to be versioned, and then add only that file intentionally.

If a document is meant to help future maintainers understand why a skill is designed a certain way, put it under `docs/` and commit it only when explicitly requested. If it is a transient artifact from an agent run, keep it under `docs/` but leave it untracked.

## Privacy and Public-Safe Content

This repository is a reusable skill package. Do not commit internal or user-specific names, concepts, paths, or raw run artifacts into skills, references, examples, evals, scripts, or generated docs.

Forbidden content includes:

- Private project, repository, product, customer, tenant, organization, environment, or codename strings.
- Internal architecture names, incident names, service names, domain names, ticket IDs, meeting names, or roadmap concepts unless they are already intentionally public.
- Local absolute paths, machine-specific home directories, private workspace paths, shell history, API keys, tokens, secrets, certificates, or credentials.
- Raw agent transcripts, real audit packages, eval JSONL traces, screenshots, logs, or command outputs that were produced against private repositories or local workspaces.
- Examples copied from internal projects, even when the code itself is not included.

Use portable placeholders instead: `example-api`, `example-worker`, `example-repo`, `example.com`, `/path/to/repo`, `<skill-root>`, `<audit-workspace>`, `<transcript.jsonl>`. Before finishing a skill change, scan the touched skill package for private-name and local-path leakage, and replace or remove anything that is not public-safe.

## Installation

```bash
npx skills add aiden0z/skills --skill <skill-name>
```
