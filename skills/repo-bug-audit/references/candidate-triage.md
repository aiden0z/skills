# Candidate Triage

Use candidates for plausible leads that are not ready for submitted findings.

## Candidate Format

Keep each candidate short. One Markdown file under `work/candidates/` is enough.

```markdown
# <标题>

- 位置：`repo/path/file.ext:line`
- 疑点：<代码呈现出的风险>
- 未提交原因：<缺少的关键证据，或可能误报的地方>
- 升级所需证据：<需要继续确认的入口、配置、调用链、测试、日志或运行条件>
```

Optional after a later pass:

```markdown
- 升级结果：`BUG-xxxx`
- 复核结果：保留候选 / 移除 / 合并到 `BUG-xxxx`
```

## Promotion Rules

- Promote only when code evidence, trigger path, failure mode, and impact are all explicit.
- Do not submit raw scanner output as a Bug.
- Do not submit pattern-only claims such as “HTTP 无 timeout” unless the affected call path and production impact are clear.
- If evidence remains weak, keep the lead in `work/candidates/` and improve `升级所需证据`.
- If the same lead repeats across files without distinct impact, keep one candidate and list representative locations.
