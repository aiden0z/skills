# Eval Artifacts

Do not commit raw agent transcripts or real audit workspaces here. They often
contain local filesystem paths, private repository names, code snippets, and
user-specific command history.

For portable regression coverage, keep scenario definitions in
`../core-regressions.json` and run local traces through
`scripts/grade_eval_trace.py` from an untracked location.
