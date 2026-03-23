# VibeDeck

> 用自然语言生成专业演示文稿 — 描述你想要的，AI 帮你构建。

[English](README.md)

## 它能做什么

你用自然语言描述一个演示文稿，VibeDeck 将它构建为一个 React 应用，包含图表、动画、主题和打印支持。不需要设计技能 — AI 处理布局、数据可视化和视觉美化。

### 支持的 AI 工具

| 工具 | 项目级路径 | 用户级路径 |
|------|-----------|-----------|
| Claude Code | `.claude/skills/vibe-deck/` | `~/.claude/skills/vibe-deck/` |
| GitHub Copilot | `.github/skills/vibe-deck/` | `~/.copilot/skills/vibe-deck/` |
| OpenAI Codex | `.agents/skills/vibe-deck/` | `~/.codex/skills/vibe-deck/` |
| Kimi Code | `.kimi/skills/vibe-deck/` | `~/.kimi/skills/vibe-deck/` |

## 快速开始

1. 将 skill 安装到你的 AI 工具的 skills 目录
2. 用自然语言描述需求：
   ```
   做一个季度回顾的 deck，包含营收图表、用户增长指标、
   和产品路线图页面
   ```
3. AI 自动搭建 React 项目、生成幻灯片、启动开发服务器

## 核心功能

- **2 种工作流**: 从零创建新 deck，或向现有 deck 添加幻灯片
- **7 种布局模板**: FullChart、SplitView、MetricGrid、ComparisonView、Divider、Agenda、Cover
- **7 个图表组件**: BarChart、LineChart、StackedBar、PieChart、FunnelChart、RingGauge、ConversionChart
- **主题系统**: Corporate Blue 和 Minimal 两个预设，支持自定义配色
- **键盘导航**: 方向键翻页，`F` 全屏
- **打印模式**: `Ctrl+P` 导出干净的 PDF
- **单文件导出**: `npm run build:single` 生成一个独立 HTML 文件，方便邮件/IM 分享
- **数据提取**: 内置脚本从 Excel 文件提取数据
- **动画效果**: 基于 Framer Motion 的渐入和交错动画

## 技术栈

- **React 19** + **Vite** — 极速开发和构建
- **ECharts 6** — 数据可视化
- **Tailwind CSS v4** — 样式
- **Framer Motion** — 动画

## 项目结构

```
vibe-deck/
  SKILL.md              # Skill 入口 — 创建 + 构建工作流
  reference/
    layout-templates.md # 7 种幻灯片布局模式（含代码）
    chart-components.md # 7 个图表组件 API（含属性和示例）
    content-rules.md    # 数据完整性和叙事规则
    style-guide.md      # 颜色、字体、间距规范
    theme-presets.md    # 主题配置选项
    instruction-template.md  # CLAUDE.md/AGENTS.md 模板
  template/             # 完整的 React + Vite 起始项目
    src/
      components/       # Deck, Slide, MetricCard, KeyMessage 等
      charts/           # BarChart, PieChart, FunnelChart 等
      slides/           # Cover, Divider, Agenda, ThankYou
      theme/            # 主题引擎 + 预设
    package.json
    vite.config.js
    slide-kit.config.js
```

## 环境要求

- **Node.js 20+**（运行 React 开发服务器和构建）
- **AI CLI 工具**（Claude Code、Copilot、Codex、Kimi Code）

## 许可证

MIT
