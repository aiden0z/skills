# Cross-Platform Execution

Use this reference whenever commands may run on Windows, Linux, or macOS.

## Core Rules

- Treat the Python scripts as portable helpers. They use standard library modules, `pathlib`, and UTF-8 file IO.
- Use Python 3.9 or newer for bundled helper scripts.
- Run scripts through Python explicitly. Do not rely on shebangs, executable bits, `chmod`, or Unix shell behavior.
- Prefer commands that match the current shell. Do not force Bash-only pipelines in PowerShell.
- Use platform-neutral paths in Markdown when possible, but use host-native paths in terminal commands.
- Quote paths that contain spaces.
- Keep `work/` scratch output out of `submit/` on every platform.

## Python Commands

Unix, Linux, and macOS:

```bash
python3 scripts/init_bug_workspace.py <output-root> --project "<Project>" --scope "<scope>"
python3 scripts/generate_bug_index.py <output-root>/submit --language zh
python3 scripts/validate_bug_package.py <output-root>/submit --language zh
```

Windows PowerShell:

```powershell
py -3 scripts\init_bug_workspace.py <output-root> --project "<Project>" --scope "<scope>"
py -3 scripts\generate_bug_index.py <output-root>\submit --language zh
py -3 scripts\validate_bug_package.py <output-root>\submit --language zh
```

If `py -3` is unavailable on Windows, try `python` instead.

## Inventory Commands

Preferred when `rg` is installed:

```bash
rg --files
rg -n "requests\.|subprocess|os\.system|pickle|eval\(|transaction\.atomic|while True|sleep\(" .
```

Unix, Linux, and macOS fallback:

```bash
find . -type f
find . -name '*.py' -print0 | xargs -0 wc -l | sort -n | tail
```

Windows PowerShell fallback:

```powershell
Get-ChildItem -Recurse -File
Get-ChildItem -Recurse -File | Select-String -Pattern 'requests\.|subprocess|os\.system|pickle|eval\(|transaction\.atomic|while True|sleep\('
Get-ChildItem -Recurse -Filter *.py | Sort-Object Length -Descending | Select-Object -First 20 FullName,Length
```

If the repository is very large, prefer `git ls-files` inside Git worktrees to avoid scanning generated or vendored files.

## Archive Commands

Zip only the `submit/` directory contents. Never include `work/`.

Unix, Linux, and macOS:

```bash
cd <output-root>/submit && zip -r ../repo-bug-audit.zip .
```

Windows PowerShell:

```powershell
Compress-Archive -Path <output-root>\submit\* -DestinationPath <output-root>\repo-bug-audit.zip -Force
```

## Tool Fallbacks

- If `rg` is missing, use `git ls-files`, `find`, or `Get-ChildItem`.
- If Semgrep, CodeQL, dependency scanners, or secret scanners are missing, continue with manual static-analysis passes.
- If image compression tools are missing, either omit the image or regenerate a smaller PNG.
- If a companion skill is unavailable, continue with this skill's built-in workflow and record the assumption in `quality/submission-scope.md`.
- On continuation runs, use `resume-audit.md` before modifying existing findings, regardless of platform.
