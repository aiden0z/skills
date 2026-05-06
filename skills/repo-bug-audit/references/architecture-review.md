# Architecture Review Lens

Use this file when writing architecture-risk knowledge or interpreting repeated Bug families.

Architecture principles are not Bugs by themselves. Use them to find concrete failure paths, repeated issue families, and cross-system risk signals.

## Term Choices

Use mature Chinese translations first. Keep English when the term is commonly used as-is.

| English term | Preferred Chinese | Use in audit |
|---|---|---|
| Use Case | 用例 | One complete user/operator/background action. |
| Application Service | 应用服务 | Orchestrates a use case without owning infrastructure details. |
| Domain Model | 领域模型 | Core business/resource rules that should not depend on frameworks or SDKs. |
| Bounded Context | 限界上下文 | Boundary where terms, rules, and ownership stay consistent. |
| Port | 端口 | Abstract boundary required by the application layer. |
| Adapter | 适配器 | Implementation that talks to DB, HTTP, cloud SDK, storage, network, shell, or device. |
| Ports and Adapters | 端口与适配器 | Also called Hexagonal Architecture. |
| Anti-corruption Layer | 防腐层 | Translation layer that protects local models from external model leakage. |
| Saga | Saga | Multi-step distributed transaction or compensation workflow. |
| Transactional Outbox | 事务性发件箱（Outbox） | Persist event/message with local transaction before async delivery. |
| Inbox | 收件箱（Inbox） | Record consumed messages to avoid duplicate processing. |
| Idempotency | 幂等 | Same request/job can be retried without duplicated side effects. |
| Reconciliation | 状态对账 / 状态收敛 | Compare local state with backend truth and repair drift. |
| Operation Log / Record | 操作日志 / 操作记录 | Plain implementation term. Use only when code has a durable record of a task or operation. |

Avoid non-standard coined terms when a mature term exists. For durable workflow records, prefer `操作记录`, `任务执行记录`, `Saga 状态`, or `Outbox 记录` according to the code evidence.

## Discovery Perspective

In submitted materials, prefer “架构风险信号” over “架构落地原则”. The goal is to show what static analysis found, not to command a redesign.

Good wording:

- 用例层与基础设施细节混在同一段代码，失败分支容易遗漏状态回滚。
- 外部系统调用绕过统一适配器，超时、重试、鉴权和错误映射不一致。
- 跨系统写操作没有 Saga 状态或操作记录，部分成功后缺少可恢复入口。
- 本地状态和后端真实状态缺少状态对账，状态漂移依赖人工发现。

Avoid wording:

- 必须引入某某层。
- 开发必须按某原则改。
- 已完成验证。
- 可直接修复。

## Architecture Principles to Risk Signals

Use these principles as search lenses. Submit a Bug only after code evidence, trigger path, failure mode, and impact are explicit.

| Principle | Risk signal | Bug families to inspect |
|---|---|---|
| 单一职责原则（SRP） | Controller/provider/service mixes request parsing, authorization, DB writes, remote calls, task dispatch, and response mapping. | partial success, skipped cleanup, masked failure, duplicate side effect. |
| 开闭原则（OCP） | New resource type, driver, cloud vendor, or workflow requires scattered `if/else` edits. | missing validation, missing rollback, missing policy check, unhandled backend type. |
| 里氏替换原则（LSP） | Providers/drivers share an interface but return different status meanings or side effects. | false success, state drift, resource leak, incompatible behavior by backend. |
| 接口隔离原则（ISP） | Fat interface forces empty implementations, silent no-op, default success, or broad capability assumptions. | operation appears supported but backend skipped work. |
| 依赖倒置原则（DIP） | Business logic directly depends on HTTP clients, SDKs, shell commands, storage drivers, or framework globals. | inconsistent timeout, retry, audit, authz, TLS, error mapping, cleanup. |
| 关注点分离（Separation of Concerns） | UI/API/task/driver persistence concerns are tangled. | hard-to-recover long task, inconsistent API behavior, missing observability. |
| 高内聚低耦合 | One module owns unrelated domains or many modules mutate the same resource state. | conflicting source of truth, duplicated lifecycle code, cross-module race. |
| 最小知识原则（Law of Demeter） | Code walks through deep object graphs or remote model internals. | fragile integration, external schema leakage, missing compatibility handling. |

## Architecture Styles to Risk Signals

| Style or pattern | What to inspect |
|---|---|
| 整洁架构（Clean Architecture） | Whether use cases depend inward on domain rules or outward on framework/SDK details. Outward dependency in use-case code often explains inconsistent failure handling. |
| 领域驱动设计（DDD） | Whether terms and state transitions stay inside one bounded context / 同一限界上下文. Mixed domain vocabulary often predicts duplicated validation and inconsistent state transitions. |
| 端口与适配器（Ports and Adapters） | Whether all external calls pass through consistent adapters. Bypasses often miss timeout, retry, auth, audit, and error translation. |
| 防腐层（Anti-corruption Layer） | Whether external API models leak into internal state. Leakage often causes backend-specific fields, enum drift, and upgrade regressions. |
| Saga | Whether multi-step cross-system work records step state, compensation state, retry count, terminal state, and manual handoff. |
| 事务性发件箱（Outbox） | Whether local DB changes and async messages/events can diverge. Missing Outbox often creates “DB updated but event lost” or “event sent but DB rolled back”. |
| 收件箱（Inbox） | Whether consumers can process duplicate messages safely. Missing Inbox often creates duplicate resource creation or repeated destructive action. |
| CQRS | Whether read model lag is visible and recoverable. Stale read models should not drive destructive decisions without backend confirmation. |
| 状态对账（Reconciliation） | Whether local DB, cache, cloud backend, storage, network, and billing state can converge after partial failure. |

## Review Sections

Use these sections for `knowledge/architecture-design-review.md`:

1. `结论`
2. `评审材料来源`
3. `架构风险口径`
4. `架构体检指标`
5. `架构发现`
6. `重复问题族`
7. `目标风险边界`
8. `与 Bug 修复的关系`

Keep evidence concrete: file sizes, large functions, mixed concerns, repeated issue families, and cross-repo call paths.

## Evidence Standard

- Architecture review can group repeated risks, but it does not replace concrete Bug records.
- A broad architecture signal belongs in `knowledge/architecture-design-review.md`.
- A submitted Bug still needs a specific entry point, code evidence, realistic failure mode, affected resource, and impact.
