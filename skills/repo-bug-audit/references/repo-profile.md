# Per-Repo Profile

每个被审计的 repo 在 `submit/knowledge/repo-profiles/<repo-name>.md` 输出一份 profile。这是 D2 跨 repo lens（L15-L19）和 META-1（意图与实现漂移）的输入支点：没有 profile 就跑不动 Tier 3。

> 第一约束：见 `authenticity.md`。本文 profile 中每一项 path:line / 端点 / 函数名 / commit hash 必须真实存在，**优先空集 + 诚实标记，不要伪造完整性**。

## 何时写

Phase 1 知识收集结束时，**为每个 repo 写一份**。即使是单 repo 审计也要写——它是后续所有 lens 应用记录的引用基底。

如果某 repo 完全无跨 repo 通信（纯内部库、纯 CLI 工具），仍要写 profile，但 5 类边界段中 4 类可能是空集，明确标 "本 repo 未发现该类边界"。

## 必含段（顺序固定）

```markdown
# <repo-name> Profile

## Tech Stack
## Entry Points
## Outbound Calls
## Inbound Endpoints
## Shared Events
## Shared Storage
## Shared Config
## Intent Inputs
## 调用图
## 已知未覆盖
```

下面逐段说明。

### 1. Tech Stack

简明列表。语言、框架、构建工具、关键中间件。每项一行。证据来自 `package.json` / `pom.xml` / `go.mod` / `requirements.txt` / `Dockerfile` 等可定位文件——不要凭文件名猜测。

```markdown
- 语言：Python 3.11（pyproject.toml）
- Web 框架：FastAPI 0.104（requirements.txt:15）
- ORM：SQLAlchemy 2.x（requirements.txt:22）
- 队列：Celery + Redis（requirements.txt:30, docker-compose.yml:42）
- 测试：pytest（pytest.ini）
```

### 2. Entry Points

所有可触发本 repo 代码执行的外部入口。分类：

- HTTP/gRPC 路由（path → handler 函数 + path:line）
- 消息消费者（topic/queue → handler）
- 定时任务（cron 表达式 → handler）
- CLI 命令（命令名 → entry function）
- WebSocket / 长连接

```markdown
### HTTP
- POST /api/v1/snapshots → src/api/snapshots.py:42 create_snapshot
- DELETE /api/v1/snapshots/{id} → src/api/snapshots.py:101 delete_snapshot

### Worker
- queue=cleanup → src/workers/cleanup.py:18 process_cleanup
```

### 3. Outbound Calls (跨 repo / 跨服务出站)

本 repo 主动调用其他服务/repo 的位置。这是 L15 (契约漂移) 的探测面。

```markdown
| 目标服务 | 调用方式 | 调用位置 | Schema 来源 |
|---|---|---|---|
| user-service | HTTP GET /users/{id} | src/clients/user.py:23 | 无 schema 定义；字段从 src/clients/user.py:30 反推 |
| billing-service | gRPC ChargeOrder | src/clients/billing.py:55 | proto 在 ../shared-protos/billing.proto:12（外部 repo） |
```

字段 `Schema 来源` 直接喂 L15。如果是 "无 schema 定义；字段从代码反推"，就是 L15 高风险信号。

### 4. Inbound Endpoints

被外部 repo 调用的本 repo 端点。即第 2 段 Entry Points 中的子集——**那些被其他 repo 已知会调用的**。如果不能确认是否被外部调用，标 `调用方未确认`。

```markdown
| 端点 | 已知调用方 (repo) | 契约定义位置 |
|---|---|---|
| POST /api/v1/snapshots | release-cli, web-frontend | OpenAPI 在 docs/openapi.yaml |
| internal: validate_token | auth-gateway（调用方未确认） | 无契约文档 |
```

### 5. Shared Events

本 repo 生产或消费的跨服务事件/消息。

```markdown
### 生产
- snapshot.created → Kafka topic `release.snapshot` (src/events/publisher.py:40)
  - schema: src/events/schemas/snapshot_created.py:5
  - 字段：id, version, files[], created_at

### 消费
- billing.charged ← Kafka topic `billing.events` (src/workers/billing_listener.py:12)
  - schema 来源：未确认（消费方按字段名解析）
```

`schema 来源：未确认` 是 L15 必查信号。

### 6. Shared Storage

被本 repo 直接读/写的、且**至少一个其他 repo 也访问的**存储位置。喂 L17（共享状态所有权）。

```markdown
| 存储 | 表/Key | 本 repo 访问方式 | 已知共享方 |
|---|---|---|---|
| MySQL | release.snapshots | 读+写 | release-worker (写)、analytics (只读) |
| Redis | snapshot:lock:* | 读+写+TTL | release-worker (写) |
| S3 | s3://release-bucket/snapshots/ | 写 | analytics (读)、release-cli (读) |
```

如果不能确认共享方，标 `已知共享方：未确认`——这是 L17 候选。

### 7. Shared Config

跨 repo 含义相同（或应该相同）的配置/feature flag/secret 名。喂 L17 + L12 (config 漂移)。

```markdown
- `RELEASE_LOCK_TIMEOUT` env：本 repo 默认 30s（config/settings.py:18）；release-worker 默认 60s（未确认是否预期不一致）
- feature flag `enable_dual_write`：本 repo 在 src/release/snapshot.py:200 检查；release-worker 是否检查未确认
```

### 8. Intent Inputs

META-1（意图与实现漂移）的运作底料。列出本 repo 中**值得核对意图的文档来源**：

```markdown
- README.md（描述本 repo 用途、关键设计决策）
- docs/architecture/snapshot-design.md（快照模块设计文档，2024 年初）
- docs/adrs/0003-use-redis-for-locking.md（ADR）
- 重要 commit message：
  - abc1234 "fix: prevent snapshot drift" (2024-03)
  - def5678 "refactor: extract release service" (2024-06)
- 关键 PR：#445 (snapshot lock redesign)
```

**仅列实际找到的**。没有 ADR 就写 "未发现 ADR 目录"。**禁止**为了"完整性"虚构文档名。

META-1 跑的时候会拿这一段去对照代码，看注释/spec 与实现是否漂移。没有这一段就跑不了 META-1。

### 9. 调用图

按 `call-graph-conventions.md` 的 5 条护栏画 Mermaid 调用图。**每个 profile 至少 1 张图、最多视复杂度拆 N 张图**。

每张图独立的 H3 段：

```markdown
### 调用图：HTTP 写入路径

> 入口：POST /api/v1/snapshots；目的：展示快照创建从入口到落库的链路

```mermaid
flowchart LR
    A[POST /snapshots] -->|api/snapshots.py:42| B[create_snapshot]
    B -->|services/release.py:12| C[reserve_files]
    C -.->|未直接确认: 通过 celery delay| D[CleanupTask]
```

**未覆盖区域**
- auth 中间件（chains in src/middleware/auth.py）
- 错误响应路径
- 第三方 SDK 内部
```

### 10. 已知未覆盖

profile 整体的诚实空集汇总。列出 agent 知道存在但**没有时间/能力深入**的区域：

```markdown
- src/legacy/ 模块（500+ 行遗留代码，已知有自己的入口但未画入调用图）
- 单元测试 fixtures 中的隐藏调用（tests/conftest.py 内 monkeypatch 较多）
- C 扩展模块 src/native/_fast.so（无源码，仅 .so 文件）
```

这一段不是"我没干完活"，而是"我诚实告诉你哪里没看"。这是 META-1 / META-2 后续可以接力的地方。

## 写作规范

- **所有 path:line 必须真实**：写之前 grep 确认；validator 的 `--repo-root` 检查会扫到错误
- **禁止 "应该" / "可能" / "推测"**：详见 `authenticity.md` 与 `writing-style.md` 的禁用词
- **未确认就用未确认**：`schema 来源：未确认`、`调用方：未确认`、`是否预期不一致：未确认` 都是合法且鼓励的表达
- **简洁优先**：每段如果只有 1-2 项，不要硬凑。Tech Stack 的 5 行胜过 30 行装饰
- **每个 profile 文件 < 800 行**：超过就该拆。多入口大型 repo 可以按子系统拆（profile + N 张图 vs 多个 profile 文件，二选一）

## 与 lens 的衔接

| Profile 段 | 直接喂的 lens |
|---|---|
| Outbound Calls | L15 契约漂移 |
| Shared Events | L15、L18（重试幂等）|
| Shared Storage | L17 共享状态所有权 |
| Shared Config | L12 配置环境漂移、L17 |
| Inbound + Outbound 组合 | L16 saga 完整性、L19 迁移发布安全 |
| Intent Inputs | META-1 意图漂移 |
| 调用图 | 几乎所有 Tier 2 lens 的 entry-point 来源 |
| 已知未覆盖 | META-2 测试覆盖盲区 + 后续 audit 接力 |

## 与 validator 的衔接

- `submit/knowledge/repo-profiles/<repo>.md` 至少存在一个文件 → ERROR if 缺失
- 每个 profile 必须包含 10 个标题段（# 一级标题 + 9 个二级标题）→ WARN if 缺段
- profile 中所有出现的 `path:line` 引用，受 `--repo-root` 路径存在性检查（与 frontmatter `files[]` 同规则）
