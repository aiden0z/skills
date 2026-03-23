# Email Designer

> 通过自然对话生成专业邮件模板。**全面兼容所有主流邮件客户端** — Outlook、Gmail、Apple Mail、Yahoo Mail 等。

[English](README.md)

## 为什么需要这个 Skill？

制作一封在所有邮件客户端都能正确显示的精美邮件，远比你想象的要难。**Outlook 2007–2019 使用 Microsoft Word 的渲染引擎**而非浏览器引擎，这意味着现代 CSS（flexbox、grid、border-radius、margin）完全不生效。网上找到的大多数邮件模板在 Outlook 中都会排版错乱。

这个 Skill 解决了这个问题。生成的每一封邮件都**经过最严苛的邮件客户端（Outlook）验证**，同时为现代客户端（Gmail、Apple Mail）做了渐进增强。能在 Outlook 里正常显示，就能在所有地方正常显示。

### 兼容的邮件客户端

| 客户端 | 渲染引擎 | 兼容状态 |
|--------|----------|----------|
| Outlook 2007–2019 (Windows) | Microsoft Word | 完全兼容 |
| Outlook for Mac | WebKit | 完全兼容 |
| Outlook.com (网页版) | 浏览器 | 完全兼容 |
| Gmail (网页版 & 移动端) | 浏览器 | 完全兼容 |
| Apple Mail (macOS & iOS) | WebKit | 完全兼容 |
| Yahoo Mail | 浏览器 | 完全兼容 |
| Thunderbird | Gecko | 完全兼容 |

## 它能做什么

你描述想要的邮件 — 布局、颜色、内容 — Skill 会生成：

- **EML 文件** — 双击用 Outlook 打开，进入草稿编辑模式，填内容直接发送
- **HTML 文件** — 在浏览器中预览，反复调整直到满意

### 核心功能

- **4 种预设布局** — 单栏、双栏、杂志风、公告
- **自定义布局** — 用自然语言描述，AI 自动设计
- **设计系统** — 专业配色方案、字体层级、一致的间距体系
- **品牌色提取** — 提供 Logo 图片，AI 自动提取品牌色
- **19 个邮件组件** — 页头、页脚、表格、卡片、数据面板、进度条、按钮、导航栏、状态标签、分隔线、图片占位、内容区块、提示框、推荐语、功能列表、定价表、团队成员、警告、时间线
- **32 条 HTML 验证规则** — 自动检查兼容性问题，输出前拦截错误
- **内容填充** — 在对话中填入内容，或留空在 Outlook 中编辑
- **模板复用** — 保存满意的设计，下次直接使用
- **多语言支持** — 中文、英文、日文占位符
- **核心零依赖** — HTML/EML 生成仅需 Python 标准库；图表和图片处理的可选依赖（plotly、pillow）按需自动安装

## 安装使用

将 skill 目录复制到你的 AI 工具的 skills 路径：

| 工具 | 项目级 | 用户级（所有项目生效） |
|------|-------|---------------------|
| Claude Code | `.claude/skills/email-designer/` | `~/.claude/skills/email-designer/` |
| GitHub Copilot | `.github/skills/email-designer/` | `~/.copilot/skills/email-designer/` |
| OpenAI Codex | `.agents/skills/email-designer/` | `~/.codex/skills/email-designer/` |
| Kimi Code | `.kimi/skills/email-designer/` | `~/.kimi/skills/email-designer/` |

然后用自然语言或 `/email-designer` 调用：

```
帮我做一个邮件模板，蓝色主题，800px 宽
```

> 需要系统安装 Python 3.8+（仅标准库，无需 pip install）。

## 项目结构

```
skill.md                    # Skill 入口 — 自适应向导流程
rules/
  outlook-compatibility.md  # Outlook 渲染规则（最难的部分）
  design-system.md          # 配色、字体、间距（通用基础）
  design-system-data-report.md  # KPI 卡片、状态标签（数据类邮件扩展）
  email-best-practices.md   # 宽度、无障碍、内容规范
  placeholder-i18n.md       # 多语言占位符
  brand-color-extraction.md # 品牌色识别 + 预设调色板
templates/
  components/*.html         # 19 个经过验证的 HTML 邮件组件
  layouts/*.md              # 7 种预设布局定义
  guides/*.md               # Outlook 使用指引（中/英）
code-blocks/
  html-validator.py         # 32 条规则兼容性检查器
  html-to-eml.py            # HTML → EML 转换（自动 images/ → CID）
  eml-builder.py            # EML 构建器（链式 API）
  html-patcher.py           # 局部修改（无需重新生成）
  content-filler.py         # 批量占位符填充
  template-manager.py       # 模板保存/加载
  output-manager.py         # 按时间戳组织输出目录
  preview-helper.py         # 自动浏览器预览 + ASCII 布局图
  cid-embedder.py           # 图片扫描 + 占位图创建
examples/
  example-single-column.html  # 完整 600px 单栏参考
  example-two-column.html     # 完整 800px 双栏参考
```

## 工作流程

```
你描述想要的邮件
      ↓
AI 读取兼容性规则 + 设计系统
      ↓
生成 Outlook 安全的 HTML（表格布局、VML、MSO 指令）
      ↓
自动验证 32 条规则（捕获溢出、禁用 CSS 等）
      ↓
浏览器打开预览 + 终端显示 ASCII 布局图
      ↓
你反复调整直到满意
      ↓
生成 EML 文件 → 用 Outlook 打开 → 编辑发送
```

### 兼容性挑战

大多数邮件客户端用浏览器引擎渲染 HTML，Outlook 是例外 — 它用 **Microsoft Word**：

| 特性 | 浏览器客户端 | Outlook |
|------|-------------|---------|
| Flexbox / Grid | 正常 | 被忽略 |
| border-radius（圆角） | 正常 | 被忽略 |
| CSS margin | 正常 | 部分失效 |
| CSS border 颜色 | 正常 | 全部变成黑色 |
| background-image | 正常 | 部分支持 |
| `<div>` 布局 | 正常 | 不可靠 |

Skill 自动处理所有这些问题：
- **表格布局**替代 div/flexbox
- **VML（矢量标记语言）** 实现彩色分隔线和边框
- **MSO 条件注释**（`<!--[if mso]>`）处理 Outlook 专属修复
- **双重声明**（HTML 属性 + CSS）确保最大兼容
- **间距行**替代 margin 实现可靠的间距

最终结果：邮件在每个客户端都看起来一致。

## 设计系统

Skill 内置了从真实企业邮件系统中提炼的设计规范：

- **5 级文本色阶** — `#0f172a` → `#94a3b8`（不使用纯黑色）
- **背景色分层** — 用 `#f8fafc` 浅灰背景分组元素，替代边框
- **4px 间距网格** — 从 4px 到 40px 的一致节奏
- **仅 2 种字重** — 400（常规）+ 600（中粗）
- **现代表格设计** — 无竖线、灰色表头行、简洁分隔线
- **语义化颜色** — 绿色/橙色/红色表示状态，不是装饰
- **数据报告扩展** — KPI 卡片、状态标签、趋势指标、进度条

## 环境要求

- **Python 3.8+**（用于 EML 生成 — 仅使用标准库，无需安装额外包）
- **AI CLI 工具**（Claude Code、Kimi CLI 或类似工具）

## 许可证

MIT
