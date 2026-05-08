# Related Skills

Use this when choosing optional companion skills. Companion skills are accelerators, not dependencies.

## Use Order

1. Use any relevant skill already exposed by the current agent runtime.
2. If a public skill is needed and Node/npm are available, search with `npx -y skills find <query>`.
3. Prefer complete public locators from search results, for example `obra/superpowers@brainstorming`.
4. Preview a repository before installing when the result is unfamiliar.
5. **Interactive mode**: when a high-value recommended skill is missing, pause once and ask the user whether to install it. Do not silently skip — silent skipping defeats the purpose of recommending the skill in the first place. Phrase as a single yes/no with the public locator visible.
6. **Automatic mode**: do not pause; continue without the skill and record the skipped recommendation in `submit/quality/submission-scope.md` under a `跳过的推荐 skill` note so the next reviewer knows what was bypassed.
7. Never re-ask within the same session if the user already declined a skill.
8. If `npx -y skills` is unavailable, use a safe platform-supported install/import path or continue with this skill's built-in workflow.

### When to Ask (Per-Phase Trigger Table)

Use this table to decide WHERE in the workflow to surface each prompt. One ask per skill per session, at the latest sensible phase — never a batch of installs at kickoff.

| Phase | Skill | Trigger condition |
|---|---|---|
| 1 (set scope) | `brainstorming` | User says "先讨论/帮我想想" OR target spans 3+ unfamiliar repos OR scope/audience unclear. |
| 3 (knowledge map) | `acquire-codebase-knowledge` | Multi-repo OR single repo >50k LOC AND unfamiliar to the user. |
| 4 (find Bugs) | `software-architecture`, `code-review-expert` | When the audit explicitly targets architecture risk or security — not for general scans. (Note: `systematic-debugging`'s core mental model is **already internalized** in `references/exploration-lenses.md` — install it only when the audit also includes runtime debugging beyond static scope.) |
| 6 (write Bugs) | `error-debugging-error-analysis` | When ≥3 P1/P2 findings touch incident-response paths (recovery, retry, observability). |
| 7 (knowledge docs) | `codebase-documenter` | Final handoff package only. |
| 9 (package) | `humanizer-zh` | Chinese deliverables AND README/knowledge docs were written by this skill. |
| 9 (package) | `baoyu-infographic` | When `audit-overview.png` is being generated AND user has no rendering preference. |

### Example Ask Scripts

Use these as templates. Always: single yes/no, public locator visible, default behavior named, no enumeration of alternatives. Phrase like a teammate, not a system message — avoid "检测到/系统提示/本次/当前/标志着/凸显" and similar console-log tone.

**At Phase 9 — humanizer-zh missing, Chinese deliverables ready:**

```text
README 和知识文档写完了，想再过一遍去掉一些 AI 腔。
要不要装一下 `op7418/humanizer-zh@humanizer-zh` 让它顺一遍？不装的话就用内置的 writing-style.md 自检走一遍。
```

**At Phase 3 — acquire-codebase-knowledge missing, large multi-repo target:**

```text
这次要扫 4 个仓库，加起来差不多 12 万行，没有现成的仓库地图。
要不要先装 `github/awesome-copilot@acquire-codebase-knowledge` 跑一遍生成关系图？不装就按这个 skill 自带的最小知识图谱推进。
```

**At Phase 1 — brainstorming missing, scope unclear:**

```text
P1/P2 怎么定、最后交什么形式，这两点你还没说死。
要不要先装 `obra/superpowers@brainstorming` 一起把 charter 聊清楚？不装我就按 references/deep-discussion.md 自带的流程走。
```

**Logging the user's choice (always do this, regardless of yes/no):**

In `submit/quality/submission-scope.md`:

```markdown
## 推荐 skill 处理

| 阶段 | Skill | 何时问的 | 用户选择 | 说明 |
|---|---|---|---|---|
| 9 | op7418/humanizer-zh@humanizer-zh | Phase 9 入口 | 跳过 | 用户说不用，沿用内置自检 |
| 3 | github/awesome-copilot@acquire-codebase-knowledge | Phase 3 入口 | 安装 | 多仓关系图 |
```

### Anti-Patterns

- Asking 5 install questions in a row at Phase 1 ("要不要装 A、B、C、D、E？") — split across phases per the table above.
- Silently continuing without recording the skip in `submission-scope.md` — leaves no audit trail.
- Re-asking a previously declined skill on resume — read `submission-scope.md` first.
- Phrasing as multi-choice ("要装 A 还是 B 还是都不装？") — always yes/no.
- Hiding the public locator behind a friendly name only — users need the locator to install it themselves later.

## Companion Skill Hints

Verify public locators with `npx -y skills find <query>` before installation.

| Purpose | Skill | Public locator |
|---|---|---|
| Remove AI-flavored phrasing in Chinese deliverables | `humanizer-zh` | `op7418/humanizer-zh@humanizer-zh` |
| Scope, tradeoffs, output format decisions | `brainstorming` | `obra/superpowers@brainstorming` |
| Repository map and codebase knowledge | `acquire-codebase-knowledge` | `github/awesome-copilot@acquire-codebase-knowledge` |
| Architecture boundary review | `software-architecture` | `sickn33/antigravity-awesome-skills@software-architecture` |
| Review heuristics, SOLID, security checklists | `code-review-expert` | `sanyuan0704/code-review-expert@code-review-expert` |
| Root-cause discipline and false-positive reduction (already internalized — see `exploration-lenses.md`) | `systematic-debugging` | `obra/superpowers@systematic-debugging` |
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
