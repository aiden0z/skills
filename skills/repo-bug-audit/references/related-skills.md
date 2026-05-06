# Related Skills

Use this when choosing optional companion skills. Companion skills are accelerators, not dependencies.

## Use Order

1. Use any relevant skill already exposed by the current agent runtime.
2. If a public skill is needed and Node/npm are available, search with `npx -y skills find <query>`.
3. Prefer complete public locators from search results, for example `obra/superpowers@brainstorming`.
4. Preview a repository before installing when the result is unfamiliar.
5. Ask before installing anything unless the user already requested installation.
6. Do not pause automatic audit runs for optional companion-skill installation.
7. If `npx -y skills` is unavailable, use a safe platform-supported install/import path or continue with this skill's built-in workflow.

## Companion Skill Hints

Verify public locators with `npx -y skills find <query>` before installation.

| Purpose | Skill | Public locator |
|---|---|---|
| Scope, tradeoffs, output format decisions | `brainstorming` | `obra/superpowers@brainstorming` |
| Repository map and codebase knowledge | `acquire-codebase-knowledge` | `github/awesome-copilot@acquire-codebase-knowledge` |
| Architecture boundary review | `software-architecture` | `sickn33/antigravity-awesome-skills@software-architecture` |
| Review heuristics, SOLID, security checklists | `code-review-expert` | `sanyuan0704/code-review-expert@code-review-expert` |
| Root-cause discipline and false-positive reduction | `systematic-debugging` | `obra/superpowers@systematic-debugging` |
| Incident, observability, and recovery thinking | `error-debugging-error-analysis` | `sickn33/antigravity-awesome-skills@error-debugging-error-analysis` |
| README and reusable knowledge clarity | `codebase-documenter` | `ailabs-393/ai-labs-claude-skills@codebase-documenter` |
| Audit overview image planning | `baoyu-infographic` | `jimliu/baoyu-skills@baoyu-infographic` |
| Native image generation | `imagegen` | Runtime-provided image capability if available; do not install as a public skill. |

## Commands

Search:

```bash
npx -y skills find <query>
```

Preview repository contents:

```bash
npx -y skills add <owner/repo> --list
```

Install a specific public locator:

```bash
npx -y skills add <owner/repo@skill> --global --yes
```

Install one skill from a previewed repository when the CLI supports `--skill`:

```bash
npx -y skills add <owner/repo> --skill <skill-name> --global --yes
```

## Rules

- Do not hard-code local filesystem paths for companion skills.
- Do not install every recommended skill; install only the one that materially improves the current task.
- Check source reputation before installing unfamiliar public skills.
- Verify host-specific commands before using them; do not assume a command exists just because another agent supports it.
- Mention external tools or companion skills in deliverables only if they were actually used.

## External Lenses

Use these as audit lenses, not as dependencies:

- Security: OWASP ASVS, OWASP Top 10, CWE.
- Static scanning: Semgrep, CodeQL, dependency scanners, secret scanners.
- Reliability: SRE incident review, blast radius, recovery path, observable symptoms.
- Architecture: Clean Architecture, DDD, explicit boundaries, source-of-truth ownership.
