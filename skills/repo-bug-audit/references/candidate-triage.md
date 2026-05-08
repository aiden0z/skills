# Candidate Triage

Use candidates for plausible leads that are not ready for submitted findings. A candidate is useful scratch evidence, not a weaker Bug record.

## Candidate Format

Keep each candidate short. One Markdown file under `work/candidates/` is enough.

English template:

```markdown
# <title>

- Location: `repo/path/file.ext:line`
- Suspicion: <risk visible in code>
- Not Submitted Because: <missing key evidence or likely false-positive guard>
- Evidence Needed To Promote: <entry point, config, call chain, test, log, or runtime condition>
```

Chinese deliverables may use:

```markdown
# <标题>

- 位置：`repo/path/file.ext:line`
- 疑点：<代码呈现出的风险>
- 未提交原因：<缺少的关键证据，或可能误报的地方>
- 升级所需证据：<需要继续确认的入口、配置、调用链、测试、日志或运行条件>
```

Optional after a later pass:

```markdown
- Promotion Result: `BUG-xxxx` / kept / removed / merged into `BUG-xxxx`
- Review Result: <short reason>
```

## Promotion Rules

- Promote only when code evidence, trigger path, failure mode, and impact are all explicit.
- Do not submit raw scanner output as a Bug.
- Do not submit pattern-only claims such as "HTTP call has no timeout" unless the affected call path and production impact are clear.
- If evidence remains weak, keep the lead in `work/candidates/` and improve the "Evidence Needed To Promote" field.
- If the same lead repeats across files without distinct impact, keep one candidate and list representative locations.
- If a candidate becomes a Bug, copy only evidence-backed claims into `submit/`; leave speculation in `work/`.
