# Agent Compatibility

Use this when sharing, installing, or adapting this skill across Agent Skills-compatible hosts.

## Compatibility Shape

- Keep the skill directory lowercase and hyphenated: `repo-bug-audit`.
- Keep the root file named `SKILL.md`.
- Keep `name` and `description` in YAML frontmatter.
- Keep reusable procedures in `references/`.
- Keep repeatable helpers in `scripts/`.
- Treat `agents/openai.yaml` as optional UI metadata; other agents can ignore it.
- Avoid required workflow steps that depend on Codex-only syntax.

## Installation Boundary

- Do not prescribe installation directories.
- Use the current runtime's already exposed skills first.
- Prefer the target platform's discovery or installation mechanism when available.
- For public skills, prefer `npx -y skills` when Node/npm are available.
- Ask before installing anything unless the user already requested installation.
- Do not interrupt automatic audit runs for optional companion-skill installation.
- If `npx -y skills` is unavailable, use a safe platform-supported install/import flow or continue with the built-in workflow.

Useful public-skill commands:

```bash
npx -y skills find <query>
npx -y skills add <owner/repo> --list
npx -y skills add <owner/repo@skill> --global --yes
```

## Portability Rules

- Reference bundled files from `SKILL.md`; do not assume the agent scans all files deeply.
- Run helper scripts with an explicit Python command instead of relying on Unix shebang execution.
- Keep terminal examples shell-specific when needed: Bash/Zsh for Unix, PowerShell for Windows.
- Treat companion skills as optional. Never require another skill to load before this one can run.
- Verify host-specific commands before using them.
- Do not include secrets, private URLs, or project-specific findings in the skill itself.

## Cross-Agent Overview Images

The `audit-overview.png` quality rules are host-neutral. Any Agent Skills-compatible host that creates the overview image should follow `references/audit-overview-image.md`, even if its screenshot tool, browser shell, or image renderer differs.

Required portable behavior:

- Use a fixed landscape or near-landscape artboard for the final PNG.
- If an HTML preview is provided, make it viewport-fit so common review windows show the whole artboard without scrolling or top-left cropping.
- Screenshot the final artboard/canvas, not a scrolling page.
- Verify the exported PNG and at least one constrained preview size, such as `1600x1000` or `1440x900`.
- Treat DOM overflow checks as a helper only; visual review for clipping, stale previews, compression damage, and accidental empty space is still required.
- Keep preview screenshots and renderer-specific artifacts under `work/tmp/` or `work/drafts/`, not `submit/`.
