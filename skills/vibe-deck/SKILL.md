---
name: vibe-deck
description: >
  Vibe Deck — vibe-code professional slide presentations — describe what you
  want, AI builds it. Handles project scaffolding, slide creation, chart
  integration, and data extraction. Use when the user mentions slides, deck,
  presentation, PPT, PPTX, slideshow, keynote, pitch deck, quarterly review,
  add a slide, build a deck, create slides. Chinese triggers: 做PPT, 做个deck,
  写pptx, 创建演示, 制作幻灯片, 做幻灯片, 加一页, 新增slide, 做演示文稿,
  工作汇报, 述职报告, 季度回顾, 方案展示, 写个汇报.
---

# VibeDeck

## Step 0: Environment Check

Before anything else, verify that Node.js and npm are available. Try these commands (use whichever works on the current platform):

```sh
node --version    # or: where.exe node (Windows)
npm --version     # or: where.exe npm (Windows)
```

- **Both exist and Node.js ≥ 20** → continue silently (do not mention the check to the user).
- **Missing or version too low** → do NOT proceed. Instead:
  1. Run `uname -s` and `uname -m` (or `systeminfo` on Windows) to detect the user's OS and architecture.
  2. If you have web search capability, search for the latest recommended way to install Node.js on the user's platform, and provide the specific commands.
  3. If you cannot search, show this message in the user's language:
     > **中文**: VibeDeck 需要 Node.js 20 或更高版本。请访问 https://nodejs.org 下载并安装适合你操作系统的版本，安装完成后重新运行。
     >
     > **English**: VibeDeck requires Node.js 20 or later. Please visit https://nodejs.org to download and install the version for your OS, then try again.
  4. Stop here and wait for the user to install before continuing.

## Step 1: Check Project

Check if `slide-kit.config.js` exists in the current directory.

- **Exists** → this is an existing slide-kit project. Go to [Building Slides](#building-slides).
- **Does not exist** → no project yet. Go to [Creating a New Deck](#creating-a-new-deck), then continue to Building Slides if the user also described content.

---

## Creating a New Deck

### 1. Ask for title

Only ask for the **project title** (required). Show defaults for everything else:

> I'll set up the project with these defaults unless you want changes:
> - **Directory**: `./<title-slug>/`
> - **Theme**: `corporate-blue` (also available: `minimal`)
> - **Logo**: built-in SlideKit logo
> - **Presenter**: none (can set later in config)
> - **Password**: none
>
> Let me know if you want to change any of these, or I'll proceed.

See [theme-presets.md](reference/theme-presets.md) for theme details.

### 2. Scaffold the project

```bash
cp -r <this-skill-dir>/template/ <target-dir>
cd <target-dir>
git init
```

No network required — the template is bundled in this skill.

### 3. Configure

- **`slide-kit.config.js`**: set `title`, `theme`, `logo`, `presenter` as needed
  - Custom primary color: use `overrides.colors.primary` — variants auto-derived
  - Custom logo: copy to `public/`, reference as `/filename.svg`
- **`index.html`**: set `<title>`
- **`src/App.jsx`**: remove PasswordGate if no password

### 4. Generate agent instructions

Read [instruction-template.md](reference/instruction-template.md), replace placeholders, write to both `CLAUDE.md` and `AGENTS.md`.

### 5. Install and start

```bash
npm install
npm run dev
```

Report: project location, theme, dev server URL.

---

## Building Slides

### 1. Read context (do this BEFORE planning)

Read these three files first — skipping this step leads to duplicated content, wrong theme colors, or missed conventions:

- `CLAUDE.md` (or `AGENTS.md`) — theme, conventions, data sources
- `src/App.jsx` — current slide list and ordering (what already exists)
- `slide-kit.config.js` — active theme and presenter info

### 2. Understand the request

- What content should this slide show?
- Is there data involved? Where does it come from?
- **Narrative continuity**: new slide should follow logically from the previous one
- **No duplication**: if a data point is already shown elsewhere, present from a different angle
- **Unit consistency**: confirm the same units as existing slides ($K vs $M, etc.)
- **Content density**: Check [content-rules.md](reference/content-rules.md) for minimum content density standards — slides with sparse content (< 10 visual elements, single-line card descriptions) are not acceptable.

### 3. Choose layout

See [layout-templates.md](reference/layout-templates.md) for code templates:

| Layout | Best for |
|--------|----------|
| **FullChart** | Single large chart + KeyMessage |
| **SplitView** | Side-by-side comparison |
| **MetricGrid** | Dashboard with N metric cards |
| **ComparisonView** | Before/after |
| **DataTable** | Tool comparison, feature matrix, pricing |

Built-in slide templates (import from `src/slides/`):

| Template | Use case |
|----------|----------|
| `SlideCover` | Cover page (reads config.title automatically) |
| `SlideDivider` | Chapter divider/transition |
| `SlideAgenda` | Table of contents |
| `SlideThankYou` | Closing/Q&A page |

### 4. Build the slide

- **Layout: MUST use `SlideLayout`** for all content slides — it enforces Title → KeyMessage → Content order. See [layout-templates.md](reference/layout-templates.md)
- Charts: [chart-components.md](reference/chart-components.md)
- Style: [style-guide.md](reference/style-guide.md)
- Content: [content-rules.md](reference/content-rules.md)
- Colors: `import { colors } from '../theme'`

### 5. Register (checklist)

```jsx
import SlideXxx from './slides/SlideXxx'

// In <Deck>:
<Slide title="Page Title"><SlideXxx /></Slide>
```

Before moving on, verify:
- [ ] `import` added at top of App.jsx
- [ ] `<Slide title="...">` — `title` is set (powers navigator, do NOT omit)
- [ ] Placed in correct position within `<Deck>` (narrative order)
- [ ] `footnote` prop set if slide uses external data

### 6. Data extraction (if needed)

- Use `scripts/extract-xlsx.js` to inspect Excel structure
- Write a custom extraction script, verify totals match
- Save to `src/data/<name>.js`
- NEVER fabricate data

---

## Important Rules

- **NEVER fabricate data** — all numbers must come from source files
- When creating a project, generate BOTH `CLAUDE.md` and `AGENTS.md`
- `slide-kit.config.js` is the single source of truth for runtime config
- Slide components: `src/slides/Slide<PascalCaseName>.jsx`
- Data files: `src/data/<kebab-case-name>.js`
