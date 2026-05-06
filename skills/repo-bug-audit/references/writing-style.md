# Writing Style

Use this before writing submitted Bug records, README files, knowledge docs, indexes, summaries, emails, or infographic text.

## Goal

Write like a careful QA engineer or senior reviewer handing over concrete findings. The text should read as a project artifact, not as a chat transcript, tool output, or generated explanation.

## Required Style

- Use direct conclusions backed by evidence.
- Prefer concrete nouns: module, entry point, resource, state, failure branch, backend, adapter, task.
- Keep sentences short enough to scan.
- State uncertainty through `confidence` and false-positive review, not through vague filler.
- Describe static-analysis status plainly: `source=static-analysis`, `待开发复核`, `需运行时验证`.
- Use `Bug`, not mixed labels such as “缺陷/问题/风险项” unless the context needs a broader architecture signal.
- Use discovery wording for architecture findings: “发现/集中在/表现为/容易导致”.

## Avoid

- Self-reference: “我/我们/本 AI/模型/智能体/Agent 发现”.
- Process narration: “下面是分析结果/经过分析/我将从几个方面说明”.
- Audience explanation: “面向开发团队/供开发者参考/方便后续使用”.
- Inflated certainty: “已完成验证/确认无误/可直接修复/全部真实”.
- Generic praise or padding: “整体来看非常重要/值得关注/有较大帮助”.
- Tool-flavored wording: “静态扫描显示大量/高置信缺陷/自动生成报告”.
- Commanding architecture language: “必须引入/开发必须/应该立刻重构”.

## Prefer

| Weak wording | Better wording |
|---|---|
| 经过分析发现该接口可能有问题。 | `delete_volume` 在远端删除成功后才更新本地状态，本地更新失败会留下不可恢复的状态漂移。 |
| 这个 Bug 面向开发团队参考。 | 删除。文件结构和 README 已说明阅读顺序。 |
| 这是高置信缺陷。 | `confidence=high` 写入元信息；正文说明证据和误报排查。 |
| 建议开发必须引入 Saga。 | 当前跨系统写操作缺少可恢复的步骤状态，失败后只能依赖人工排查。 |
| AI 静态分析发现很多问题。 | 本次记录 `source=static-analysis` 的 Bug，用代码证据、触发路径和影响范围收录。 |

## Final Pass

Before packaging:

- Search for banned/meta phrases with `validate_bug_package.py`.
- Re-read README and `audit-overview.png` text as if they were pasted into an internal release email.
- Remove lines that explain the report instead of describing findings.
- Keep architecture comments tied to repeated Bug families or concrete risk paths.
