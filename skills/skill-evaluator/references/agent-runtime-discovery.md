# Agent Runtime Discovery

## Contents

- Purpose
- Safety Rules
- Discovery Flow
- Runtime Hints
- Capture Decision
- Output Contract

## Purpose

Use this before real-agent evals. The goal is to discover what evidence the current agent runtime can emit without assuming one fixed tool or trace format.

Do not run the target eval during discovery. Discovery is read-only: inspect available CLIs, help text, version output, local docs, and safe configuration hints.

## Safety Rules

- Do not start a real agent run without user approval.
- Do not pass task prompts, secrets, repo paths, or destructive flags during discovery.
- Prefer `--help`, `help`, `--version`, and local documentation commands.
- If a command might authenticate, mutate state, send a prompt, create a PR, or run an agent, skip it.
- Record unknowns honestly. Unknown capture support is better than guessed support.

## Discovery Flow

1. Identify candidate runtimes:
   - Check explicit user context first.
   - Look for common CLI names on `PATH`.
   - Inspect project-local scripts only if they are clearly eval or agent wrappers.

2. Collect safe facts:
   - CLI path.
   - Version when available.
   - Help text snippets that mention JSON, logs, sessions, transcripts, traces, export, non-interactive runs, or PR/CI integration.

3. Assign likely evidence channels:
   - Structured trace.
   - Transcript/session log.
   - Command/tool log.
   - Artifact root.
   - Diff/commit/PR evidence.
   - Validator/CI output.

4. Choose the best capture method:
   - Prefer structured trace when available.
   - Otherwise use transcript or command/tool logs plus artifacts.
   - Otherwise use artifacts, diffs, and validator output only.

5. Record blind spots:
   - Tool calls not observable.
   - Commands hidden inside the agent.
   - No transcript export.
   - Only final answer available.

## Runtime Hints

These are discovery hints, not guaranteed commands.

### Codex

Look for:

- `codex exec --json`
- non-interactive execution mode
- JSONL or structured event output

Typical capture shape:

```bash
codex exec --json "<prompt>" > evals/artifacts/<case>.jsonl
```

Evidence level is usually 3 when JSONL plus artifacts and validators are captured.

### Claude Code

Look for:

- `claude --help`
- non-interactive or print mode
- transcript/session export
- tool-use or terminal log options

If structured output is unavailable, capture:

- terminal transcript
- file diff before/after
- generated artifacts
- validator output

Evidence level is often 2 if transcript or command logs are preserved, 1 if only artifacts are available.

### GitHub Copilot / GitHub Coding Agent

Look for:

- `gh copilot --help`
- `copilot --help`
- GitHub issue/PR comments from the coding agent
- commit or PR diffs
- GitHub Actions logs
- workflow artifacts

For PR-based agents, the useful trace may be outside the local CLI:

- PR conversation.
- Commit history.
- CI logs.
- Generated artifacts.
- Review comments.

Evidence level depends on whether the action timeline or agent comments expose process. PR diff plus CI usually supports artifact validation; workflow logs or action traces may support partial workflow adherence.

### Kimi / Other Agent CLIs

Look for:

- `<cli> --help`
- `<cli> help`
- `<cli> --version`
- flags such as `--json`, `--log`, `--trace`, `--session`, `--export`, `--output`, `--non-interactive`, or `--headless`

If documentation is local and safe to read, inspect it. If capture support remains unknown, fall back to transcript, diff, artifacts, and validator logs.

### Hosted Trace Platforms

For LangSmith, Phoenix, Braintrust, OpenTelemetry, or similar systems, look for:

- trace export
- span export
- tool-call timeline
- evaluator scores
- dataset or experiment run IDs
- artifact links

Treat these as structured trace if they expose step/tool spans and artifacts.

## Capture Decision

After discovery, record:

```markdown
## Agent Runtime Discovery

- Detected runtimes:
- Chosen runtime:
- Capture method:
- Evidence level:
- Structured trace:
- Transcript/session log:
- Command/tool log:
- Artifact root:
- Diff capture:
- Validator/CI logs:
- Known blind spots:
```

If evidence level is 0, do not run a real-agent eval. Ask for a better capture method or limit the review to static/artifact checks.

## Output Contract

When using `scripts/discover_agent_runtime.py`, treat its output as a starting point. It can discover local CLI hints, but it cannot know hosted PR logs, IDE transcripts, or user-specific export features unless they are visible locally.

Expected JSON fields:

- `detected`: list of candidate runtimes.
- `path`: CLI path when found.
- `version`: safe version output when available.
- `structured_trace`: `likely`, `possible`, `unknown`, or `unavailable`.
- `recommended_capture`: suggested capture approach.
- `evidence_level_estimate`: 0, 1, 2, or 3.
- `notes`: caveats and follow-up checks.
