# Skill Evaluator 设计说明

`skill-evaluator` 是一个用于审查和加固 Agent Skills 的 Skill。它帮助维护者判断一个 Skill 是否容易触发、能否执行、是否可验证，以及在真实 agent 行为下是否足够稳健。

本文档面向人类维护者。Agent 运行时仍应以 `skills/skill-evaluator/SKILL.md` 作为入口。

[English](design.md)

## 用途

当你需要做以下事情时，可以使用这个 Skill：

- 审查一个 Skill 是否已经适合发布或安装。
- 调查一个 Skill 为什么触发不稳定。
- 把一次真实 agent 失败转成回归 eval case。
- 检查一个 fresh agent 是否能按 Skill 的 workflow 正确执行。
- 为 Skill 输出增加确定性校验。
- 为复杂或高风险 Skill 设计轻量 eval harness。
- 比较不同版本、不同 agent、不同模型下的 Skill 行为。
- 发现某个 agent runtime 如何暴露 trace、transcript、diff 或验证证据。
- 在选择捕获策略前，检查本地 Codex、Claude Code、GitHub Copilot、Kimi 或自定义 agent CLI。

它特别适合那些会生成结构化交付物、协调多步骤流程、依赖 references/scripts，或者曾经在真实运行中失败过的 Skill。

## 解决的问题

很多 Skill 读起来像是好说明，但实际使用时会失败。常见问题包括：

- `description` 太模糊，agent 不知道什么时候该触发。
- workflow 写了，但没有 gate 或 validator 强约束。
- agent 生成了漂亮的最终产物，却跳过了必要探索。
- references 存在，但没有从 `SKILL.md` 直接暴露出来。
- validation 只检查最终文件，不检查生成过程。
- 历史失败只被讨论过一次，没有变成可重复 eval。
- Skill 通过了机械结构检查，但语义上仍然薄弱。

`skill-evaluator` 通过静态审查、rubric 评估、eval case 设计、失败回归、可选 harness plan，以及真实 agent 运行的证据捕获发现，来解决这些问题。

## 设计理念

1. **评估行为，而不是评估说明写得好不好**

   一个 Skill 应该由 fresh agent 的真实行为来证明。文字清楚很重要，但不够。

2. **优先看证据，而不是看信心**

   好的评估会使用 transcript、tool calls、diff、生成物、validator 输出和 trace logs。只看最终回答很容易误判。

3. **默认路径保持轻量**

   不是每个 Skill 都需要完整 harness。基础审查应保持快速：读 Skill、跑机械检查、按 rubric 评分、提出具体修改。

4. **复杂评估按需启用**

   Harness engineering 适合高影响或易失败的 Skill，但不应强加给每个小 Skill。

5. **把失败变成资产**

   一次真实失败应该变成 regression case、validator check、reference 改进或 workflow gate。

6. **先做确定性检查**

   先用脚本和断言捕获客观失败，再使用 model-assisted grading。

7. **发现证据通道，而不是硬编码某个 agent**

   Codex JSONL 是很好的参考实现，但不是唯一协议。其他 runtime 可能暴露 transcript、IDE log、PR comment、CI log、trace span、diff 或生成物。Evaluator 应先发现当前 runtime 能捕获什么，再说明这些证据能支持什么结论。

## 工作机制

主 workflow 在 `SKILL.md` 中：

1. **确定评估范围**
   - 识别目标 Skill、runtime、用户类型和真实 prompt。
   - 收集先前 transcript、生成物、validation logs 等证据。

2. **运行机械检查**
   - 使用 `scripts/check_skill_quality.py` 检查包装和卫生问题。
   - 如果被评估 Skill 有自己的 validator，也要运行。

3. **评估设计适配度**
   - 使用 `references/evaluation-rubric.md` 对触发质量、workflow 控制、渐进披露、确定性资源、验证完整性和输出证据进行评分。

4. **设计或审查 eval cases**
   - 使用 `references/eval-case-design.md`。
   - 使用 `references/failure-regression.md` 把已知失败转成无泄漏 regression case。
   - 使用 `scripts/check_eval_cases.py` 校验 eval case 文件。

5. **必要时做 forward-test**
   - 使用 `references/forward-testing.md` 运行 fresh-agent 检查，不泄漏预期诊断。
   - 使用 `references/harness-engineering.md` 发现 runtime 的 evidence capture channel，再评估 workflow adherence。
   - 可选运行 `scripts/discover_agent_runtime.py`，先检查本地 agent CLI，再决定捕获策略。

6. **建议或应用修改**
   - 把每个弱点转成具体改动：metadata、workflow gate、script、reference 拆分、validator、eval case 或 output schema。

## 轻量 Harness 模型

对于复杂 Skill，`references/harness-engineering.md` 定义了最小可重复 harness 模型：

- **Dataset**：真实 prompt、trigger case、negative control、regression。
- **Runner**：执行每个 case 的 runtime 命令或环境。
- **Evidence capture discovery**：运行或评分前先发现最佳证据通道。
- **Trace and artifact capture**：结构化 trace、transcript、commands、diff、生成文件、CI logs、validation logs。
- **Scorers**：先确定性检查，再 model-assisted 或 human review。
- **Aggregation**：按 case、tag、failure category、model、runtime、skill version 聚合结果。
- **Gate**：定义什么会阻塞发布。

这只是设计模式，不是强制框架。目标是让评估可重复，但不把每个 Skill 都变成大型测试平台。

## 证据捕获发现

真实运行评估需要过程证据。不同 agent 工具暴露证据的方式不同，所以 evaluator 应先发现可用证据通道，而不是假设固定格式。

本地 CLI 发现可以运行：

```bash
python3 scripts/discover_agent_runtime.py --json
```

这个脚本是只读的。它检查本地 `PATH`、安全的 help/version 命令，以及与捕获相关的 help 文本。它不会启动 agent run。

证据等级：

| Level | Evidence | Claims Allowed |
|---|---|---|
| 3 | Structured trace + artifacts + validator output | 可以声明 workflow adherence 和 artifact validation |
| 2 | Transcript 或 command/tool log + artifacts | 可以声明部分 workflow adherence 和 artifact validation |
| 1 | Artifacts + validator output only | 只能声明 artifact validation |
| 0 | Final answer only | 不足以做 real-run eval |

示例：

- Codex CLI：`codex exec --json` 可以产生 JSONL structured events。
- Claude Code 或 IDE agents：捕获 transcript/session export、terminal logs、diff、artifacts、validator output。
- GitHub Copilot coding agent：捕获 PR/commit diff、issue 或 PR comments、workflow logs、generated artifacts、CI validation。
- LangSmith、Phoenix、Braintrust、OpenTelemetry 系统：捕获 trace spans、tool calls、evaluator scores、artifacts。
- 自定义或未知 CLI agent：检查 help 输出里是否有 `json`、`trace`、`log`、`session`、`export`、`output`、non-interactive/headless 模式。

如果只有最终产物，evaluator 应该说 `artifact validation passed`，而不是说 `workflow adhered`。这对那些“最终报告看起来完整，但探索过程可能被跳过”的 Skill 很关键。

## 文件结构

```text
docs/
  skill-evaluator/
    design.md
    design_CN.md

skills/
  skill-evaluator/
    SKILL.md
    agents/
      openai.yaml
    evals/
      core-regressions.json
    references/
      agent-runtime-discovery.md
      best-practices.md
      eval-case-design.md
      evaluation-rubric.md
      failure-regression.md
      forward-testing.md
      harness-engineering.md
      skill-prompt-quality.md
    scripts/
      check_eval_cases.py
      check_skill_quality.py
      discover_agent_runtime.py
    templates/
      eval-case.json
      harness-plan.md
```

## 关键 References

- `references/best-practices.md`
  - Skill 创建和 eval 最佳实践的提炼。

- `references/agent-runtime-discovery.md`
  - 本地 agent CLI 和 runtime 捕获通道的安全发现流程。

- `references/evaluation-rubric.md`
  - Skill readiness 评分框架。

- `references/eval-case-design.md`
  - 可移植 eval case schema 和模式。

- `references/failure-regression.md`
  - 如何把观察到的失败转成无泄漏 regression case。

- `references/forward-testing.md`
  - fresh-agent 测试协议。

- `references/harness-engineering.md`
  - 可重复 Skill evaluation 的轻量 harness 设计，包括 evidence capture discovery。

- `references/skill-prompt-quality.md`
  - 检查 `SKILL.md` 是否能可靠引导 agent 行为的静态质量门。

## 脚本

### `check_skill_quality.py`

对 Skill 目录运行确定性结构检查：

```bash
python3 scripts/check_skill_quality.py /path/to/skill
```

它会检查 frontmatter、行数、references、scripts 和常见反模式。

### `check_eval_cases.py`

校验可移植 Skill eval case JSON：

```bash
python3 scripts/check_eval_cases.py /path/to/evals.json
```

当 eval suite 准备强制执行 portable schema 时，使用 strict 模式：

```bash
python3 scripts/check_eval_cases.py --strict-portable /path/to/evals.json
```

Strict 模式会要求 `scope`、`trigger_expectation`、`tags`、`grader`、`failure_categories` 等字段。

### `discover_agent_runtime.py`

只读发现常见 agent runtime：

```bash
python3 scripts/discover_agent_runtime.py --json
```

它会检查 Codex、Claude Code、GitHub Copilot、Kimi 和类似本地 wrapper 的 CLI 线索。输出是 harness plan 的起点，不保证真实运行一定能暴露每个事件。

## Eval Case 形状

Starter template 位于 `templates/eval-case.json`。

重要字段：

- `id`：稳定 case id。
- `type`：happy path、edge case、negative、regression、trigger 或 ambiguous scope。
- `scope`：agent-level、component-level、reference-retrieval 或 artifact-review。
- `trigger_expectation`：explicit、implicit、contextual、negative 或 not-applicable。
- `prompt`：真实用户请求，不泄漏隐藏 rubric。
- `must_do`：必须执行的动作。
- `must_not_do`：禁止的捷径。
- `required_artifacts`：运行后应出现的文件或输出。
- `success_evidence`：证明成功的 transcript、trace、artifact 或 validator evidence。
- `trace_assertions`：针对捕获事件或 transcript 的确定性检查。
- `artifact_assertions`：针对生成文件的确定性检查。
- `grader`：deterministic、model-assisted、human 或 hybrid。
- `failure_categories`：用于聚合的失败标签。

## 什么时候不该使用

不要把这个 Skill 当成每次小修改都必须套用的重流程。一个很小、触发清楚、只有一个简单脚本的 Skill，可能只需要：

```bash
python3 scripts/check_skill_quality.py /path/to/skill
python3 /path/to/skill-creator/scripts/quick_validate.py /path/to/skill
```

当 Skill 复杂、面向用户、容易失败，或准备广泛发布时，再使用完整 rubric、eval cases 或 harness planning。

## 和其他 Skill 工具的关系

`skill-evaluator` 补充 Skill 创建工具：

- 使用 `skill-creator` 创建或重塑 Skill。
- 使用 `skill-evaluator` 测试 Skill 在真实条件下是否能工作。
- 使用目标 Skill 自己的 validator 检查领域交付物。

Evaluator 不替代领域校验。它关注的是 Skill 本身设计是否合理，以及 agent 是否能可靠遵循它。

## 维护建议

- 保持 `SKILL.md` 简洁，低于 500 行。
- 把详细方法放在 `references/`。
- 脚本保持依赖轻、输出确定。
- 把真实失败加入 eval case，而不是只写在说明文里。
- 普通模式优先 warning，strict 模式使用硬阻塞。
- 修改后重新运行：

```bash
python3 scripts/check_skill_quality.py .
python3 scripts/check_eval_cases.py --strict-portable templates/eval-case.json
python3 -m py_compile scripts/check_eval_cases.py scripts/check_skill_quality.py scripts/discover_agent_runtime.py
```
