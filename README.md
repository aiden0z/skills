# Agent Skills

A collection of production-grade Agent Skills for AI coding assistants.

[中文](README_CN.md)

## Skills

| Skill | What it does | Stack |
|-------|-------------|-------|
| [**Email Designer**](skills/email-designer/) | Generate email templates that render perfectly across Outlook, Gmail, Apple Mail | Python stdlib |
| [**Repo Bug Audit**](skills/repo-bug-audit/) | Audit repositories for evidence-backed Bugs, architecture risks, reusable knowledge, and fix-ready audit outputs | Python stdlib |
| [**VibeDeck**](skills/vibe-deck/) | Vibe-code professional slide presentations from natural language | React + ECharts |

## Install

```bash
# Install via npx (recommended)
npx skills add aiden0z/skills --skill email-designer
npx skills add aiden0z/skills --skill repo-bug-audit
npx skills add aiden0z/skills --skill vibe-deck

# Or specify the agent
npx skills add aiden0z/skills --skill email-designer -a claude-code
npx skills add aiden0z/skills --skill repo-bug-audit -a codex
npx skills add aiden0z/skills --skill vibe-deck -a codex
```

Supports: Claude Code, GitHub Copilot, OpenAI Codex, Kimi Code, Cursor, Windsurf, and [17+ more agents](https://github.com/vercel-labs/skills).

Then ask naturally or invoke with `/<skill-name>`.

## Structure

```
skills/
  email-designer/    →  SKILL.md + rules/ + templates/ + code-blocks/
  repo-bug-audit/    →  SKILL.md + references/ + scripts/
  vibe-deck/          →  SKILL.md + reference/ + template/
```

Each skill is self-contained. See its `SKILL.md` or README where present.

## License

MIT
