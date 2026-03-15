# AGENTS.md

This file provides guidance to AI coding agents working with this repository.

## Repository Overview

A collection of production-grade Agent Skills. Each skill is a self-contained directory under `skills/` with a `SKILL.md` entry point.

## Available Skills

| Skill | Directory | Description |
|-------|-----------|-------------|
| Email Designer | `skills/email-designer/` | Generate Outlook-compatible email templates (EML + HTML) |
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

## Installation

```bash
npx skills add aiden0z/skills --skill <skill-name>
```
