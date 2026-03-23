# VibeDeck

> Vibe-code professional slide presentations — describe what you want, AI builds it.

[中文文档](README_CN.md)

## What It Does

You describe a presentation in natural language, and VibeDeck builds it as a React app with charts, animations, theming, and print support. No design skills needed — the AI handles layout, data visualization, and visual polish.

### Supported AI Tools

| Tool | Project Path | User Path |
|------|-------------|-----------|
| Claude Code | `.claude/skills/vibe-deck/` | `~/.claude/skills/vibe-deck/` |
| GitHub Copilot | `.github/skills/vibe-deck/` | `~/.copilot/skills/vibe-deck/` |
| OpenAI Codex | `.agents/skills/vibe-deck/` | `~/.codex/skills/vibe-deck/` |
| Kimi Code | `.kimi/skills/vibe-deck/` | `~/.kimi/skills/vibe-deck/` |

## Quick Start

1. Install the skill into your AI tool's skills directory
2. Ask naturally:
   ```
   Create a quarterly review deck with revenue charts,
   user growth metrics, and a product roadmap slide.
   ```
3. The AI scaffolds a React project, generates slides, and starts a dev server

## Features

- **3 workflows**: Create new deck, add slides to existing deck, or modify/reorder/delete slides
- **10 layout templates**: FullChart, SplitView, MetricGrid, ComparisonView, DataTable, TimelineFlow, CardGrid, CardRow, ConceptSlide, plus Composite patterns
- **Layout decision engine**: Intent-aware system that automatically matches content to the right layout
- **7 chart components**: BarChart, LineChart, StackedBar, PieChart, FunnelChart, RingGauge, ConversionChart
- **Theme system**: Corporate Blue and Minimal presets, custom colors via config
- **Keyboard navigation**: Arrow keys to navigate, `F` for fullscreen
- **Print mode**: `Ctrl+P` for clean PDF export
- **Single HTML export**: `npm run build:single` produces one portable HTML file for sharing
- **Data extraction**: Extract data from Excel files via built-in script
- **Animations**: Stagger and fade-in transitions via Framer Motion

## Tech Stack

- **React 19** + **Vite** for fast dev and build
- **ECharts 6** for data visualization
- **Tailwind CSS v4** for styling
- **Framer Motion** for animations

## Project Structure

```
vibe-deck/
  SKILL.md              # Skill entry — create + build + modify workflows
  reference/
    layout-engine.md    # Intent-aware layout decision engine (5 steps)
    layout-templates.md # 10 slide layout patterns with code
    chart-components.md # 7 chart APIs with props and examples
    content-rules.md    # Data integrity and narrative rules
    style-guide.md      # Color, typography, spacing conventions
    theme-presets.md    # Theme configuration options
    instruction-template.md  # Template for CLAUDE.md/AGENTS.md
  template/             # Complete React + Vite starter project
    src/
      components/       # Deck, Slide, MetricCard, KeyMessage, etc.
      charts/           # BarChart, PieChart, FunnelChart, etc.
      slides/           # Cover, Divider, Agenda, ThankYou
      theme/            # Theme engine + presets
    package.json
    vite.config.js
    slide-kit.config.js
```

## Requirements

- **Node.js 20+** (for React dev server and build)
- **An AI CLI tool** (Claude Code, Copilot, Codex, Kimi Code)

## License

MIT
