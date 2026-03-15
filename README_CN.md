# Agent Skills

一组生产级 Agent Skills，适用于各类 AI 编程助手。

[English](README.md)

## Skills

| Skill | 功能 | 技术栈 |
|-------|------|--------|
| [**Email Designer**](skills/email-designer/) | 生成完美兼容 Outlook、Gmail、Apple Mail 的邮件模板 | Python 标准库 |
| [**VibeDeck**](skills/vibe-deck/) | 用自然语言生成专业演示文稿 | React + ECharts |

## 安装

```bash
# 通过 npx 安装（推荐）
npx skills add aiden0z/skills --skill email-designer
npx skills add aiden0z/skills --skill vibe-deck

# 指定 AI 工具
npx skills add aiden0z/skills --skill email-designer -a claude-code
npx skills add aiden0z/skills --skill vibe-deck -a codex
```

支持：Claude Code、GitHub Copilot、OpenAI Codex、Kimi Code、Cursor、Windsurf 等 [17+ 种 agent](https://github.com/vercel-labs/skills)。

然后用自然语言或 `/<skill-name>` 调用。

## 结构

```
skills/
  email-designer/    →  SKILL.md + rules/ + templates/ + code-blocks/
  vibe-deck/          →  SKILL.md + reference/ + template/
```

每个 skill 自包含。详情见各 skill 自己的 README。

## 许可证

MIT
