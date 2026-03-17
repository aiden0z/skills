# Instruction Template

Generate CLAUDE.md and AGENTS.md with this content, replacing {{placeholders}}:

---

# {{title}}

## Project Info
- Framework: Slide Kit (Vite + React + Tailwind v4 + ECharts + Framer Motion)
- Theme: {{theme}}
- Logo: {{logo}}
- Presenter: {{presenter.name}} — {{presenter.role}} (set in `slide-kit.config.js`, auto-displayed on cover)
- Config: `slide-kit.config.js`

## Theme Colors
- Primary: {{colors.primary}}
- Accent: {{colors.accent}}
- Success: {{colors.success}}
- Use `import { colors } from '../theme'` — NEVER hardcode hex values

## Typography
- Slide title: `text-[28px] font-bold`
- Key Message / subtitle: minimum `text-sm` (14px)
- Body text / card titles: minimum `text-[13px]`
- Chart internal labels: `text-[10px]` allowed
- Footer page number: `text-xs`

## Charts
- Use chart components from `src/charts/` — do NOT write inline ECharts options
- Available: StackedBar, BarChart, RingGauge, FunnelChart, PieChart, ConversionChart
- All tooltips MUST use `TOOLTIP_STYLE` from `src/lib/chart-theme.js` (has `appendToBody: true`)
- All charts MUST have `label: { show: true }`

## Animations
- Use presets from `src/lib/animations.js` — do NOT define stagger/fadeIn locally
- Available: `stagger`, `staggerSlow`, `fadeIn`, `slideUp`, `fadeOnly`

## Slide Layout (IMPORTANT)
- **All content slides MUST use `SlideLayout`** — it enforces Title → KeyMessage → Content order
- Pass title via `title` prop, key insights via `keyMessage` prop (optional)
- Do NOT manually render `<h2>` title or `<KeyMessage>` — SlideLayout handles both
- Cover, Divider, Agenda, ThankYou slides use their own dedicated components, not SlideLayout

## Components
- `SlideLayout` — **required wrapper for content slides** (title + optional KeyMessage + content)
- `KeyMessage` — blue label + arrow, for key insights (used internally by SlideLayout; do NOT use directly)
- `TabSwitcher` — multi-view toggle within a slide
- `MetricCard` — big number + label + sublabel
- `Legend` — color dot + label list for charts

## Content Rules
- Key Message: every claim MUST be supported by a visible chart on the page
- Quantify all insights (e.g., "8% conversion" not just "low conversion")
- NEVER fabricate data — all numbers must come from data files in `src/data/`

## Key Message Usage
- **Data slides ONLY** — only add `keyMessage` on slides with charts, metrics, or numbers
- Do NOT use KeyMessage on concept/explanation slides (e.g., "什么是 X？", "为什么选择 Y？")
- Format: pass as a string array `keyMessage={['bullet 1', 'bullet 2']}` — auto-formatted with bullets
- Maximum 3 bullets, each ≤ 25 Chinese characters / 60 English characters

## Space Utilization
- NEVER use fixed pixel width (`w-[Npx]`) for card containers — use `grid grid-cols-N` or `flex-1`
- Cards in a row: `grid grid-cols-N gap-5 h-full content-center` (N = number of cards)
- Cards in a 2×2 grid: `grid grid-cols-2 gap-5 h-full content-center`
- Content should utilize ≥ 70% of available width
- NEVER fix both width and height on the same element

## Semi-transparent Colors
- Pattern: `${colors.primary}XX` where XX is hex alpha (e.g., `08` = subtle, `15` = card bg, `40` = border)
- NEVER hardcode `rgba()` — always use hex alpha on theme colors

## Concept / Text Slides
- For non-data slides (explanations, comparisons, overviews): use ConceptSlide layout pattern
- NO `keyMessage` — use the extra vertical space for larger fonts and more breathing room
- Use `grid grid-cols-2` for side-by-side concepts, single-column for linear flow

## Data Sources
{{dataSources — user fills in}}

## Project-Specific Rules
{{projectRules — user fills in}}
