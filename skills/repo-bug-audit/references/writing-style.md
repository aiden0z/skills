# Writing Style

Use this before writing submitted Bug records, README files, knowledge docs, indexes, summaries, emails, or infographic text.

Language boundary: methodology and skill instructions are English. Submitted deliverables use the requested language; default to Chinese when the user is Chinese and does not specify otherwise. The banned phrases and examples below are Chinese-focused because most default deliverables are Chinese; for English packages, apply the same principles instead of translating the banned list mechanically.

## Goal

Write like a careful QA engineer or senior reviewer handing over concrete findings. The text should read as a project artifact, not as a chat transcript, tool output, or generated explanation.

> **Authenticity First** (`authenticity.md`): natural wording is required, but **only on top of real evidence**. Smooth-sounding fabricated content is the worst possible failure of this skill — worse than awkward AI-flavored honest content.

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
- Hollow fix-suggestion clichés (the most common AI padding): "建议添加 try/catch", "建议加强校验", "建议增加日志", "考虑使用 X", "可能需要重构", "建议关注", "建议进行压测", "应该优化".
- Pseudo-precise speculation: "推测此处会…", "理论上可能…", "代码中应有 X 校验" (without proof of absence — use "已搜索 [grep pattern] 未发现 X 校验" instead), "该函数可能被多处调用" (without enumeration — write "未做调用方枚举" if you have not).

## AI-Flavored Patterns to Strip

These patterns survive the basic banned-word list because the individual words look harmless. Catch them in the final pass.

- **Inflated significance / "标志着" framing**: “标志着……重要时刻/关键节点”、“反映了更广泛的趋势”、“代表着一次重要转变”、“凸显了……的重要性”、“为……奠定了基础”、“在……中扮演关键角色”。
  - 处理方式：删掉评价语，只留事实。`X 模块负责发布快照` 而不是 `X 模块在系统中扮演关键角色，标志着发布流程的重要节点`。
- **"-ing" 浅层补尾**：句尾接 `, 体现/反映/确保/促进/展示了……`，给一个本来已经说完的句子再贴一个空泛动词短语。
  - 处理方式：删掉补尾从句。
- **三段并列 / 二元对比的公式结构**：`既……又……更……`、`一方面……另一方面……`、`不仅是……更是……`。
  - 处理方式：拆成短句直陈。
- **宣传式形容词**：`充满活力的`、`丰富的`、`深刻的`、`显著的`、`重大的`、`深远的`、`核心的`（用作泛义而非限定）、`系统性的`、`全方位的`。
  - 处理方式：用具体名词或数字替换。
- **模糊归因**：`业内普遍认为`、`相关研究表明`、`观察者指出`、`多个来源`（实际无引用）。
  - 处理方式：要么补具体出处，要么改成 `当前实现` / `从 src/x.py:42 可以看到`。
- **"挑战与展望" 公式段**：`尽管面临……挑战，但……仍将继续……`、`展望未来……`。
  - 处理方式：审计报告不需要展望。删除整段。
- **空心收尾句**：`总体而言/综上所述/总的来说/在某种意义上`。
  - 处理方式：删除，让最后一条事实自然收尾。
- **节奏单一**：所有段落都是 2-3 句、句式相同长度相近。
  - 处理方式：刻意混合长短句、允许单句段落。

## Companion Skill: humanizer-zh

When the deliverable is in Chinese (README、knowledge docs、image text、submission-scope), recommend the user install `op7418/humanizer-zh@humanizer-zh` and run it on text that fails the patterns above.

Trigger an install prompt (interactive mode) when:

- The README or any knowledge doc exceeds ~500 字 of generated narrative.
- The audit-overview image text is being authored.
- The final pass surfaces three or more AI-flavored patterns that the built-in banned list did not catch.

Skip the prompt if the user has already declined humanizer-zh in this session, or if the deliverable is short structured Bug records (which are already constrained by `bug-schema.md`).

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
