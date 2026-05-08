# Exploration Lenses

本文是本 skill 的 Bug 探寻方法论。**它是 `workflow.md` Phase 2 的真正实质**——Phase 2 不是 grep 一次了事，是按 lens 体系系统地、深度分层地、可追溯地扫描代码。

> 第一约束：见 `authenticity.md`。**lens 覆盖永远不能成为伪造的借口**。"已应用 lens 但未发现"是合法且鼓励的输出，伪造发现来凑覆盖是最严重的违规。

## 借鉴痕迹（heavy borrow，不是原创）

本 lens 体系的心智模型借鉴自：

- **systematic-debugging skill**（动态调试 4 段式：Root Cause → Pattern → Hypothesis → Implementation）— 反向移植到静态审计。借鉴日期 2026-05-07。
- **error-debugging-error-analysis skill**（多组件边界证据采集思路）— 静态化为"Outbound/Inbound/Shared 五类边界枚举"。借鉴日期 2026-05-07。

未来上游 skill 演进时，应回访本文，必要时同步更新。

## 心智模型（Hypothesis-First Static Audit）

systematic-debugging 的核心是 "NO FIXES WITHOUT ROOT CAUSE"。本文的对应铁律是：

```
NO CANDIDATE WITHOUT HYPOTHESIS FIRST
```

在 grep / 阅读代码之前，agent 必须先写下 **"我在找什么具体的失败模式"**。否则就是模式匹配 + 概率开火，必然浅、必然多假阳。

四步循环（每个 lens 都按这个跑）：

1. **Hypothesize** — 写下"我在找 X 失败模式，因为 Y 会导致 Z 影响"
2. **Hunt** — grep / LSP / 调用图，按 lens 的 "Where to look" 收集候选
3. **Refute (sibling diff)** — 对每个候选，找 1-2 个**做对了的相邻代码**做对照；差异即 bug 或反证候选不成立
4. **Promote or Park** — 通过反证仍成立的写为 Bug；可疑但证据弱的进 `work/candidates/`；明确反证的进 lens 应用记录的"排除原因"

## 深度分层 (3 Tier)

| Tier | 范围 | 代表 lens | 特征 |
|---|---|---|---|
| Tier 1 surface | 单文件/单函数 | L1-L7 | grep + 阅读单文件可发现；技术债 / 防御性编码缺失 |
| Tier 2 cross-cut | 跨文件/跨模块（单 repo） | L8-L14 | 需要追踪多文件状态/时序/配置；架构原因导致 |
| Tier 3 cross-repo | 跨仓库/跨服务 | L15-L19 | 需要 `repo-profile.md` 提供边界清单 + 调用图；分布式/契约/迁移问题 |

**Meta lens** 不是平行第 20、21 个，而是**套在每个 lens 之上的对照动作**：META-1 意图漂移、META-2 失败路径测试覆盖。在 Phase 5 集中跑一次。

## 五元组模板（每个 lens 都按这个写）

每个 lens 文档约 150 字，结构：

```markdown
### L? <名称>

- **Hypothesis** — 我在找什么失败模式
- **Where to look** — grep / LSP / 调用图节点
- **Evidence pattern** — 什么证据算成立（用于写 Bug 的"代码证据"段）
- **False-positive guard** — 什么模式看起来像但其实不是
- **Stop / Tiebreak** — 什么时候停看；与其他 lens 冲突时归属规则
- **正例**：1 行匿名描述（"X 系统中 publish 后未持锁导致快照漂移"）
- **反例**：1 行（"看似缺锁，实为 with_resource_lock 装饰器包装"）
```

---

# Tier 1 Surface Lenses (单文件/单函数)

### L1 资源生命周期

- **Hypothesis**：成对操作（open/close、acquire/release、allocate/free、attach/detach）在所有控制流分支上都配对
- **Where to look**：`open(`、`acquire(`、连接池获取、协程/线程 spawn、文件描述符、`finally:` 缺失
- **Evidence pattern**：发现某 `open` 在某条 except/return 路径无对应 close；或 `try` 内 acquire 但 `finally` 内未 release
- **False-positive guard**：上下文管理器 `with`/RAII / Python `contextmanager` / Go `defer` / Java try-with-resources / Rust drop 已自动处理
- **Stop**：覆盖该函数所有控制流分支即可。**Tiebreak**：与 L9（并发）冲突时，"未释放" 归 L1，"释放但顺序错"归 L9
- 正例：HTTP 长连接客户端在某 retry 分支未关闭，FD 泄露
- 反例：看似无 close，实为 `async with httpx.AsyncClient() as c:` 已包

### L2 边界输入校验

- **Hypothesis**：所有外部输入（请求体、URL 参数、文件、环境变量、上游 SDK 返回）在使用前已经过类型/范围/格式/权限校验
- **Where to look**：HTTP handler 函数签名、`request.json`、`os.environ`、文件读取后的 parse、外部 API 响应字段直接传入下游
- **Evidence pattern**：某外部值未经校验直接进 SQL/shell/eval/file path/redirect
- **False-positive guard**：框架层校验（FastAPI Pydantic / Spring `@Valid` / Rails strong params）；上游 gateway 已做
- **Stop**：覆盖入口函数体一层即可。**Tiebreak**：注入类（SQLi/XSS/path traversal）归 L2；逻辑越权归 Tier 3 L17
- 正例：API 把 `request.headers["X-Tenant"]` 直接拼 SQL `WHERE tenant=`
- 反例：看似拼接，实为 SQLAlchemy ORM 自动参数化

### L3 错误吞没 / silent failure

- **Hypothesis**：捕获的异常都被适当处理（重试、降级、记录、向上抛），而非静默吞掉
- **Where to look**：`except:` / `except Exception:` / `catch (Throwable)` / `recover()` / `_, _ = func()` (Go)；空 catch 块；`pass` / `// ignore` 注释
- **Evidence pattern**：捕获后既无日志、无 metric、无重新抛出，也无降级路径
- **False-positive guard**：捕获后调用了日志/监控函数；或上下文确实可以忽略（如缓存失败 fallback 到原始查询）
- **Stop**：覆盖该函数所有 catch 块。**Tiebreak**：吞没本身归 L3；吞没导致状态机无法回滚归 L8
- 正例：`except: pass` 在数据写入路径，写失败用户无感
- 反例：catch 后确实写了 `logger.warning()` 且业务上允许失败

### L4 数值精度与溢出

- **Hypothesis**：金额/计量/时间戳/计数器的算术不会因类型选择导致精度丢失或溢出
- **Where to look**：`float` 算金额、`int` 计数器无上限检查、除法（除零、整除截断）、累加循环、bit shift、unsigned/signed 转换
- **Evidence pattern**：`amount * rate` 用 float；累加使用 32-bit int；除前未检查分母；NaN 传播未处理
- **False-positive guard**：使用 `Decimal` / `BigDecimal` / `int64` 显式高精度；分母在更早层校验过
- **Stop**：覆盖单函数所有算术。**Tiebreak**：纯数值 → L4；数值正确但跨服务传输丢精度 → L15
- 正例：账单计算 `total += price * qty`，price 是 float，月底累加误差 0.03 元
- 反例：看似 float，实为框架层自动转 Decimal（如 Django `DecimalField`）

### L5 时间与时钟

- **Hypothesis**：所有时间相关代码处理了时区、DST、闰年、wall-vs-monotonic、未来日期、历史日期
- **Where to look**：`datetime.now()` / `time.time()` / `Date()` / 时间相加减、`timedelta`、cron 表达式、超时判断、过期检查、时区转换 `astimezone` / `pytz`
- **Evidence pattern**：用 wall clock 做超时（NTP 跳变破坏）、naive datetime 做跨时区比较、无 DST 处理的"昨天/明天"算法、月底算"下月同日"
- **False-positive guard**：使用 `time.monotonic()` 做时间间隔；统一使用 UTC 存储+展示层转时区；用专门时间库（`pendulum` / `Joda-Time` / `java.time`）
- **Stop**：覆盖时间相关函数。**Tiebreak**：单点时间 bug → L5；多服务时间不一致 → L15 或 L17
- 正例：清理任务用 `datetime.now()` 比较 `created_at`，跨夏令时清理掉刚创建的资源
- 反例：看似 naive，实为框架统一注入 timezone-aware datetime

### L6 数据表示 / 序列化语义

- **Hypothesis**：跨进程/跨语言/跨版本的数据表示在序列化反序列化时语义保持一致
- **Where to look**：JSON `null` 与字段缺失、protobuf optional vs default、字符串编码（UTF-8/UTF-16/BOM）、enum 未知值、base64 padding、数字精度（JS Number vs int64）、日期格式（ISO8601 / 时间戳秒/毫秒）
- **Evidence pattern**：发送方用 `null` 表示"删除字段"，接收方按缺失处理；enum 增加新值，老消费者无 default case；int64 ID 序列化为 JS Number 失精度
- **False-positive guard**：使用强类型 schema（protobuf / avro）+ 兼容性测试；reviewer 已写迁移脚本
- **Stop**：覆盖跨边界序列化点。**Tiebreak**：表示层 → L6；语义/字段含义跨服务漂移 → L15
- 正例：用户 ID 在后端是 int64=18 位，前端 JSON 后变 17 位
- 反例：看似精度丢，实为后端已序列化为字符串

### L7 资源放大入口

- **Hypothesis**：单次请求/事件不会放大成 N 次（或不可控数量）下游调用、查询、内存分配
- **Where to look**：`for item in items: db.query(...)` (N+1)、递归无终止深度限制、`re.compile(user_input)` (ReDoS)、反序列化用户输入（zip/yaml/pickle bomb）、不分页的 list API、fan-out 调用
- **Evidence pattern**：循环内有 IO 调用且循环上界由用户输入控制；正则模式由请求参数构造；反序列化无 size 限制
- **False-positive guard**：批量 API 替代循环（`SELECT WHERE id IN (...)`）；上界已硬编码或经鉴权裁剪；反序列化前已 size limit
- **Stop**：覆盖入口函数 + 一层调用。**Tiebreak**：单 repo 内放大 → L7；跨 repo 重试导致放大 → L18
- 正例：`/api/users` 返回所有用户，无分页；DB 几万行直接 dump
- 反例：看似 N+1，实为 SQLAlchemy `joinedload` 已聚合

---

# Tier 2 Cross-Cut Lenses (跨文件/跨模块，单 repo)

### L8 状态机一致性

- **Hypothesis**：被多处写入的状态字段，所有 transition 都合法、无漏跳、无回退
- **Where to look**：枚举字段（`status`、`state`、`phase`）的所有写入点；grep `set_status` / `update(status=)` / `state =`；状态机定义文档（如有）
- **Evidence pattern**：发现 `pending → done` 直跳（漏 `processing`）；或 `done → pending` 回退；或并发写入相同 transition
- **False-positive guard**：transition 由统一 state machine 库管理（如 `transitions` / Spring State Machine）；DB 约束已禁止非法 transition
- **Stop**：覆盖该状态字段所有写入点。**Tiebreak**：状态合法性 → L8；状态写入并发竞争 → L9
- 正例：订单 `paid → refunded → paid` 出现在某退款回滚路径
- 反例：看似漏跳，实为该 transition 被 admin-only 路径合法触发

### L9 并发与时序

- **Hypothesis**：共享资源的并发访问有正确的锁/原子操作；check-then-act 操作是原子的
- **Where to look**：全局变量、单例、缓存、DB 行（`SELECT FOR UPDATE` 缺失）、Redis 操作（`GET` 后 `SET` 非原子）、定时器/cron 重入、async 任务取消
- **Evidence pattern**：`if not exists: create` 不在事务/锁内；多 worker 同时消费同一 message（无 distributed lock）；定时任务无防重入
- **False-positive guard**：DB 唯一约束兜底；Redis SETNX；分布式锁包装；queue 的 visibility timeout
- **Stop**：覆盖该共享资源所有读写点。**Tiebreak**：单进程并发 → L9；跨进程跨 repo → Tier 3 L17
- 正例：积分扣减 `if balance >= cost: balance -= cost`，并发请求超扣
- 反例：看似 race，实为 SQL `UPDATE balance = balance - X WHERE balance >= X` 已原子

### L10 失败恢复与补偿

- **Hypothesis**：每个多步操作都有补偿/回滚/手动接管路径；partial success 不会留下不一致
- **Where to look**：`step1(); step2(); step3()` 序列；外部 API 调用后的本地状态写入；事务边界外的副作用；retry 上限耗尽后的处理
- **Evidence pattern**：step2 失败后无回滚 step1；retry 上限到达后状态停留在 `processing`；无 `dead letter queue` / 人工介入入口
- **False-positive guard**：使用 saga / outbox / TCC 模式；上层有 idempotent 补偿任务；事务包裹整体
- **Stop**：覆盖多步操作整链。**Tiebreak**：单 repo 内补偿 → L10；跨 repo saga → L16
- 正例：扣款成功但发货 API 失败，订单永久卡在 `paid` 状态无补偿任务
- 反例：看似无补偿，实为 outbox 表 + 后台 reconciler 兜底

### L11 数据生命周期

- **Hypothesis**：数据从创建→活跃→归档→删除的完整生命周期被显式定义；历史数据/软删除/迁移期数据可被正确读取
- **Where to look**：DELETE / soft delete (`deleted_at`)、TTL 配置、归档任务、迁移脚本、读取代码是否过滤已删除/已归档
- **Evidence pattern**：list API 返回包含 soft-deleted 行；GC 任务删除了仍被引用的记录；migration 期间双写但只单读
- **False-positive guard**：QuerySet 基类已默认过滤 `deleted_at IS NULL`；migration 配套 dual-read 已部署
- **Stop**：覆盖该数据类的 CRUD 全路径。**Tiebreak**：单 repo 数据 → L11；跨 repo 数据共享 → L17
- 正例：用户注销后软删，但 `/api/users` 列表仍返回已注销用户
- 反例：看似返回，实为该端点是 admin 审计专用，预期返回所有

### L12 配置与环境漂移

- **Hypothesis**：dev/staging/prod 配置语义一致；feature flag 默认值安全；secret 缺失时 fail-closed
- **Where to look**：`os.environ.get(KEY, default)` 的 default 是否安全；`if env == 'dev'` 分支；feature flag 检查；`config[KEY]` 缺失时行为
- **Evidence pattern**：默认值 fail-open（如 `AUTH_ENABLED=False` 默认）；prod-only 校验在 dev 关闭导致 dev 测不出；secret 未设置时 silently 跳过加密
- **False-positive guard**：配置加载层有 schema 校验（如 pydantic Settings）+ 启动时 fail-fast；feature flag 默认值经过 review
- **Stop**：覆盖所有 config 读取点。**Tiebreak**：单 repo config → L12；跨 repo 同名 config 含义不一致 → L17
- 正例：`MAX_UPLOAD_MB` 默认 1000，prod 设为 10，dev 测试用例从未触发限制
- 反例：看似默认 1000 危险，实为启动校验强制要求 prod 必须显式设置

### L13 缓存一致性

- **Hypothesis**：写入数据后所有缓存层（应用 LRU、Redis、CDN、数据库 query cache）能正确失效或更新；读不到旧值
- **Where to look**：`cache.set` / `@cached` / Redis GET-SET、CDN 缓存策略、ORM 一级二级缓存、`SELECT` 后立即 `INSERT`
- **Evidence pattern**：写入后未失效相关 cache key；缓存 key 不包含 tenant/user 维度（跨租户串）；多层缓存只更新一层
- **False-positive guard**：write-through cache；统一 invalidator（cache 装饰器自带）；TTL 短到可接受漂移
- **Stop**：覆盖该数据类的写入点 + 读取点。**Tiebreak**：单 repo 缓存 → L13；跨 repo 共享缓存 key → L17
- 正例：用户改名后 5 分钟内 `GET /users/me` 仍返回旧名（CDN 缓存）
- 反例：看似旧值，实为业务允许 30s 漂移且文档已声明

### L14 关键路径可观测性

- **Hypothesis**：销毁/扣款/越权敏感操作有审计日志；metric 不会把失败计为成功；告警条件能被实际触发
- **Where to look**：`DELETE` / refund / privilege change 的代码路径；`metrics.inc('success')` 与 try/except 关系；告警 SQL/PromQL 表达式
- **Evidence pattern**：销毁操作无 audit log；metric 在 `try:` 头部就记 success（应在成功后）；告警条件 `where status='error'` 但实际错误存为 `'fail'`（永不触发）
- **False-positive guard**：上层 middleware 统一记录审计；metric 在 try 末尾；告警有 unit test
- **Stop**：覆盖关键路径 + 监控配置。**Tiebreak**：可观测性是元 lens 性质——其他 lens 发现 bug 时常顺手发现 L14 问题，归档到 L14
- 正例：admin 删除用户无 audit log，无法溯源
- 反例：看似无 log，实为框架 middleware 已统一记录

---

# Tier 3 Cross-Repo / Architecture Lenses

> Tier 3 全部依赖 `repo-profile.md` 的 5 类边界段（Outbound / Inbound / Shared Events / Shared Storage / Shared Config）。无 profile 不能跑 Tier 3。

### L15 契约漂移 (API / 事件 / 序列化)

- **Hypothesis**：A 调用 B（HTTP/gRPC/event）的双方对字段名、类型、可选性、enum 值、语义、版本兼容性有一致理解
- **Where to look**：profile 的 Outbound Calls 表 + 对端 repo 的 Inbound Endpoints；Shared Events 的 producer schema vs consumer schema；OpenAPI/proto 与代码反推字段对照
- **Evidence pattern**：producer 字段名与 consumer 不一致；producer 加新字段且非 optional，consumer 旧版部署中；enum 新值在 consumer 无 default
- **False-positive guard**：使用 protobuf + 兼容性 lint；契约测试（pact）覆盖；版本字段 + dual-version 兼容期
- **Stop**：覆盖 profile 列出的所有跨 repo 边界。**Tiebreak**：表示层 → L6；契约语义 → L15
- 正例：order-service 字段 `paid_at` 改名为 `paid_time`，billing-service 仍读旧名 → 报表为空
- 反例：看似漂移，实为 gateway 层有字段重写适配

### L16 分布式事务 / Saga 完整性

- **Hypothesis**：跨 repo 多步操作每步都有可恢复路径；任一步失败，剩余步骤要么继续要么补偿；最终一致性可达
- **Where to look**：profile 的 Outbound Calls 中调用了多个外部服务的入口；event-driven 的事件链；saga orchestrator 代码
- **Evidence pattern**：A 调 B 成功、调 C 失败时 B 的副作用未补偿；中间步骤无 idempotency key；orchestrator crash 后无 resume 机制
- **False-positive guard**：使用 Temporal / Cadence / Camunda 等 workflow 引擎；outbox 模式 + 后台对账任务
- **Stop**：覆盖每条跨服务多步链路。**Tiebreak**：单 repo 内多步 → L10；跨 repo 多步 → L16
- 正例：下单成功调扣库存 OK，调支付失败，库存未回滚
- 反例：看似无补偿，实为有定时对账任务每 5 分钟扫描

### L17 共享状态所有权

- **Hypothesis**：被多 repo 访问的存储（DB 表、Redis key、S3 prefix、feature flag、shared config）有唯一定义不变量的 owner repo；其他 repo 不绕过 owner 直接破坏不变量
- **Where to look**：profile 的 Shared Storage / Shared Config 段；grep 跨 repo 同表名/同 key 前缀的写入点
- **Evidence pattern**：表 X 有"金额必须正"的不变量，repo A 写入时校验，repo B 直接 update 跳过；feature flag `enable_x` 在 repo A 表示开关、repo B 表示百分比；同一 Redis key 在 repo A 是 hash、repo B 当 string 用
- **False-positive guard**：DB 约束/触发器兜底；shared lib 封装访问；明确的 owner-doc + ADR
- **Stop**：覆盖所有共享存储的访问点跨 repo。**Tiebreak**：单 repo 内并发 → L9；跨 repo 不变量违反 → L17
- 正例：account 表 balance 字段，billing-service 校验 ≥0，admin-tool 直接 SET 可负值
- 反例：看似多写，实为 admin-tool 走 billing-service API 而非直连 DB

### L18 跨 Repo 重试与幂等

- **Hypothesis**：A 重试 N 次时 B 是真幂等的；幂等键在跨边界传输时不丢失；重试不放大成 retry storm
- **Where to look**：profile 的 Outbound Calls 中带 retry 配置的；B 的 Inbound Endpoint 是否检查 idempotency key；retry 策略是否有指数退避 + 上限
- **Evidence pattern**：A 重试无 idempotency key；B 的 endpoint 用 random UUID 作主键（每次新建）；retry 无上限或上限过高
- **False-positive guard**：framework 自动注入 idempotency key（如 Stripe SDK）；B 用业务唯一键（order_id）做幂等；circuit breaker 限流
- **Stop**：覆盖所有跨 repo retry 调用对。**Tiebreak**：单 repo retry → L10；跨 repo retry → L18
- 正例：支付回调 A 重试 3 次，每次创建一笔新支付记录（无幂等键）
- 反例：看似无幂等，实为 B 端按 (caller_id, request_id) 做去重

### L19 迁移与发布安全

- **Hypothesis**：DB schema 迁移、API 版本升级、配置变更在 N/N-1 版本同时在线时双向兼容；canary 失败可快速回滚
- **Where to look**：migration 脚本目录；版本字段；feature flag 的灰度发布配置；profile 的 Shared Storage 的最近变更
- **Evidence pattern**：DROP COLUMN 在 N+1 删，但 N 版本仍读该列；NOT NULL 约束加在数据未填齐前；新版本部署后旧版本无法 rollback（unidirectional migration）
- **False-positive guard**：expand-and-contract 模式（先加列、双写、回填、再切读、最后删旧）；migration 配套 rollback 脚本；blue-green 部署
- **Stop**：覆盖近 6 个月的 migration + 当前 in-flight migration。**Tiebreak**：单 repo schema → L11；跨 repo / N-N+1 兼容 → L19
- 正例：v2 删除字段 `legacy_id`，回滚到 v1 时 v1 代码读该字段崩溃
- 反例：看似破坏兼容，实为该字段已 deprecation 6 个月并经下线流程

---

# Meta Lenses (套在每个 lens 之上的对照动作)

Meta lens 不是平行第 20、21 个；它们是**已经跑过其他 lens 后的全局对照扫描**，在 Phase 5 集中跑一次。

### META-1 意图与实现漂移

- **Hypothesis**：注释/README/ADR/spec 描述的行为与代码实际行为一致；不一致处往往是历史 bug 或潜在 bug
- **Where to look**：`repo-profile.md` 的 Intent Inputs 段列出的所有文档；代码中的 docstring / TODO / FIXME / "deprecated" 注释；commit message 中的"修复"声称
- **Evidence pattern**：README 说"X 在失败时重试 3 次"，代码无 retry；ADR 说"使用 outbox 模式"，代码无 outbox；commit "fix: prevent X" 但代码仍存在 X
- **False-positive guard**：注释/文档已明确标 outdated；spec 在更新中（PR open）；改名后未更新文档但行为仍正确
- **Stop**：Intent Inputs 段所列文档 + 关键 commit。**Tiebreak**：META-1 不替代其他 lens，发现的 bug 按其本质归档到 L1-L19；META-1 仅作为发现路径的元数据
- 正例：ADR 说"全部 API 必须 auth"，发现某 internal endpoint 无 auth（实归 L2/L17）
- 反例：注释说"TODO: handle this"，但代码已用 default value 兜底

### META-2 失败路径测试覆盖

- **Hypothesis**：happy path 都有测试覆盖；error / edge / 异常路径**也**有测试覆盖
- **Where to look**：`tests/` 目录、coverage 报告（如有）；grep `test_` 函数名 vs 业务函数名；search `pytest.raises` / `assertThrows` 数量
- **Evidence pattern**：业务函数 `process_payment` 有 5 个 happy test，0 个 failure test；`except` 分支无任何测试；retry 逻辑只测了第 1 次成功，未测重试场景
- **False-positive guard**：集成测试/E2E 覆盖了失败路径但未在 unit test；故意不测因为路径已 deprecated
- **Stop**：覆盖该 audit 涉及的核心模块 + Tier 2/3 已 promote 的 Bug 涉及的模块
- **Tiebreak**：META-2 输出"未测试覆盖"清单，agent 不直接写为 Bug，而是在 lens-coverage.md 的相关 lens 段标记为"风险增强：缺测试"
- 正例：发现 retry 逻辑（L10）未测试，将 BUG-0023 的优先级从 P3 升 P2
- 反例：看似无测试，实为有 contract test 覆盖

---

# Lens 应用记录格式（强制）

每次 audit 在 `submit/quality/lens-coverage.md` 输出 lens 应用记录。**Tier 2/Tier 3 每个 lens 必须有一段；Tier 1 可选**。

每段五段式硬格式：

```markdown
### Lens L? <名称> — 应用记录

- 已扫描入口：<具体路径列表，如 src/api/snapshot.py, src/worker/cleanup.py>
- 关注模式：<grep 模式 / LSP 查询 / 调用图节点描述>
- 候选数：N
- 排除原因：<被哪个 wrapper/guard 排除 → path:line>；升级为 BUG-xxxx
- 未覆盖：<诚实空集 + 原因>
```

### 五段式说明

| 段 | 含义 | 必填？ | 伪造警戒 |
|---|---|---|---|
| 已扫描入口 | 真实文件路径列表 | 是 | 不存在的路径会被 validator `--repo-root` 拒收 |
| 关注模式 | 实际用过的 grep / 调用图节点 | 是 | 模糊措辞（"扫描了相关代码"）= WARN |
| 候选数 | 整数 | 是 | 不允许"若干"/"多个"——必须数字 |
| 排除原因 | 每个非升级候选的反证 + 升级 Bug ID | 是 | 必须 path:line 锚点；纯文字解释 = WARN |
| 未覆盖 | agent 知道存在但没看的部分 | 是 | 写"无未覆盖" = WARN（几乎不可能完整覆盖） |

### "已应用 lens 但未发现" 的合法表达

```markdown
### Lens L13 缓存一致性 — 应用记录

- 已扫描入口：src/cache/, src/api/users.py, src/api/orders.py
- 关注模式：rg "cache\.(set|get|delete|invalidate)|@cached|redis\." src/
- 候选数：4
- 排除原因：
  - src/cache/user_cache.py:23 写入后调用 invalidate_user(user_id)
  - src/api/orders.py:45 缓存 TTL 30s，业务允许漂移（README 已声明）
  - src/cache/lru.py:12 仅 in-process，无跨进程一致性问题
  - src/cache/session.py:8 只读 cache，写在 auth-service（已记入跨 repo profile）
- 未覆盖：CDN 层缓存配置（infra 仓库未在审计范围内）
```

这是合法且鼓励的输出。"未发现 Bug"不是失败，是 agent 诚实工作的证据。

---

# 与其他 skill 文档的衔接

| 文档 | 关系 |
|---|---|
| `authenticity.md` | 第一约束。lens 覆盖永远不能成为伪造借口 |
| `repo-profile.md` | Tier 3 必需输入 |
| `call-graph-conventions.md` | profile 调用图护栏 |
| `bug-schema.md` | Bug frontmatter `lens` 字段 enum 来自本文 |
| `risk-taxonomy.md` | category 与 lens 多对多关系；每个 category 有 primary lens 指向 |
| `domain-profiles.md` | 每个 profile 有 lens 优先级排序（不是排除）|
| `language-ecosystems.md` | L4/L5/L6 evidence pattern 链回各语言高危函数清单 |
| `evaluation.md` | Q6 检查 lens 覆盖完整性 |
| `architecture-review.md` | Tier 3 lens 升级规则路由到此 |

---

# 可插拔策略

**默认**：所有 Tier 1（建议） + Tier 2（强制） + Tier 3（涉及多 repo 时强制） + Meta（Phase 5 强制）。

**用户指定其他策略**（如 OWASP ASVS、内部 checklist、特定 lens 子集）：
- 在 `submit/quality/submission-scope.md` 自由文字一段说明（无结构化字段）
- 例：`本次审计采用 OWASP ASVS 4.0 Level 2 + 内置 Tier 3，跳过 Tier 1。理由：XXX`
- agent 按用户策略跑；内置 lens 覆盖要求按用户声明的子集执行
