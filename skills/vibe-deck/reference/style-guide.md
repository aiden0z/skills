# Style Guide

## Typography

| Element | Class | Min Size |
|---------|-------|----------|
| Slide title | `text-[28px] font-black tracking-tight` | 28px |
| Title subtitle | `text-[13px] font-normal ml-3` + primary color | 13px |
| Key Message | `text-[14px]` | 14px |
| Section label | `text-[10px] font-bold uppercase tracking-wider text-neutral-400` | 10px |
| Card / feature title | `text-[14px] font-bold text-neutral-800` | 14px |
| Body text | `text-[12px] text-neutral-600` | 12px |
| Auxiliary / example | `text-[10px] text-neutral-400` | 10px |
| Stat numbers | `font-black` + accent color | varies |
| Chart label | `text-[10px]` | 10px |
| Footer | `text-xs` | 12px |

### Typography Hierarchy Rules
- **Minimum 4px jump between levels**: title (28px) → card title (14px) → body (12px) → aux (10px). Avoid adjacent sizes like 11px/12px/13px that blur the hierarchy.
- **font-black for emphasis**: Use `font-black` (900 weight) on page titles and key stat numbers. Use `font-bold` (700) for card titles and section labels. Never use `font-semibold` (600) for headings — it's too similar to body text.
- **Color contrast**: Primary text `text-neutral-800`, body `text-neutral-600`, auxiliary `text-neutral-400`. Avoid intermediate grays like neutral-500 for body text — it's too close to neutral-400.

## Colors

ALWAYS import from theme:
```js
import { colors } from '../theme'
```

## Cards

```
bg-neutral-50/80 border border-neutral-100 rounded-xl p-4
```

## Animations

```js
import { stagger, fadeIn } from '../lib/animations'
```

## Slide Structure

**MANDATORY: Use `SlideLayout` for all content slides.** It enforces the correct layout order automatically:

```jsx
import SlideLayout from '../components/SlideLayout'

<SlideLayout
  title="Title"                    // required
  subtitle="Optional"              // optional
  keyMessage={<p>• Insight</p>}    // optional — omit prop entirely to skip
>
  {/* Content fills remaining space */}
</SlideLayout>
```

Layout order (enforced by component): Title → KeyMessage (when present) → Content (`flex-1 min-h-0`)

**Do NOT:**
- Manually render `<h2>` title + `<KeyMessage>` — use SlideLayout props instead
- Wrap SlideLayout in another `motion.div` with stagger — it has its own animations
- Use SlideLayout for Cover, Divider, Agenda, or ThankYou slides — those have dedicated components

## Layout Details

- Content MUST fill available space — use flex layout to stretch, avoid large whitespace
- Presentation mode: fills entire viewport (no 16:9 letterbox)
- Left sidebar: hover-triggered slide navigator (w-[200px] z-40) — shows slide titles for quick jumping
- Right navigation area: `w-12 z-30` — must not overlap chart interactive areas
- List mode: cards use `aspect-video`, container `max-w-[90vw] xl:max-w-6xl`

## Space Utilization (IMPORTANT)

Card and content containers MUST fill the available space. Small fixed-size elements centered in a 1440px canvas look unbalanced.

**Rules:**
- **NEVER use fixed pixel width** (`w-[200px]`, `w-[220px]`, etc.) for card containers — use `grid grid-cols-N` or `flex-1` so cards stretch to fill the row
- **Only use fixed width** for small decorative elements (icon circles, badges, divider lines)
- **Cards in a row**: use `grid grid-cols-N gap-5 h-full content-center` where N = number of cards
- **Cards in a 2×2 grid**: use `grid grid-cols-2 gap-5 h-full content-center`
- Content area should utilize **≥ 70%** of available width — if cards look like small islands floating in whitespace, the layout is wrong
- Prefer **one dimension flexible**: if width is fixed, height should be auto (or vice versa) — NEVER fix both `w-[Npx]` and `h-[Npx]` on the same element

## Vertical Space Distribution (CRITICAL)

Content must fill the full slide height without large empty gaps. These are the most common layout bugs:

### Problem: Content bunched at top, empty bottom
**Cause**: Using `justify-start` on a `flex-1` container — items cluster at the top while the container stretches.
**Fix**: Use `justify-between` (items spread edge-to-edge) or `justify-center` with fixed `gap-4` (items centered with consistent spacing).

### Problem: Sections pushed apart with large gaps
**Cause**: Using `justify-evenly` — distributes equal space around every item, creating huge gaps when there are only 2-3 items in a tall container.
**Fix**: NEVER use `justify-evenly` on feature lists. Use `justify-between` or `justify-center gap-4`.

### Problem: "Specific actions" section pushed to bottom
**Cause**: Using `mt-auto` to pin a section to the bottom of a flex container. This creates a visual gap between the content above and the pinned section.
**Fix**: Remove `mt-auto`. Use consistent `gap` values between sections instead. If separation is needed, add `mt-2` or `mt-3` — not `mt-auto`.

### Problem: Grid cards have internal empty space
**Cause**: Grid with `flex-1` makes cells stretch, but card content doesn't fill the cell height.
**Fix**: Add `h-full` to each card so it stretches to fill its grid cell. Use `flex-1` on the grid container if it should fill parent space.

### Recommended patterns by content type

| Scenario | Pattern |
|----------|---------|
| 3 feature items in a tall card | `flex flex-col gap-4 justify-center` |
| N items that should fill a column | `flex flex-col gap-3 justify-between` |
| Sections with sub-items below | Use consistent `gap-2` between sections, add `mt-2` before sub-section |
| 2x3 or 3x2 grid of feature cards | `grid grid-cols-N gap-2` + `h-full` on each card |
| Left/right comparison panels | `flex gap-2 flex-1` — each panel uses internal `justify-between` |

### Line height for readability
- Body text: `leading-relaxed` (1.625) — NOT `leading-snug` (1.375) which is too tight
- Auxiliary text: `leading-snug` is fine for footnotes and labels
- Feature descriptions: `leading-relaxed` for paragraphs, `leading-snug` for single-line items

## Semi-transparent Colors

To create semi-transparent variants of theme colors, append a 2-digit hex alpha to the color value:

```jsx
// Pattern: ${colors.primary}XX where XX is hex opacity (00-FF)
style={{ backgroundColor: `${colors.primary}08` }}  // ~3% opacity — subtle tint
style={{ backgroundColor: `${colors.primary}10` }}  // ~6% opacity — light background
style={{ backgroundColor: `${colors.primary}15` }}  // ~8% opacity — card background
style={{ backgroundColor: `${colors.primary}20` }}  // ~12% opacity — hover / border
style={{ backgroundColor: `${colors.primary}40` }}  // ~25% opacity — active border
```

This works because theme colors are hex strings (e.g., `#2563eb`), and appending `08` creates `#2563eb08` (CSS 8-digit hex with alpha). ALWAYS use this pattern instead of hardcoding `rgba()` values.

## Slide Registration Props

- `title` — **Always set** on every `<Slide>`. Powers the navigator sidebar in list mode and the jump-to panel in presentation mode
- `footnote` — Data source disclaimers (color: `text-neutral-400`, NOT 300)
- `bonus` — Marks appendix/backup slides, hidden by default. The "附录" toggle button only appears when at least one slide has `bonus` prop. Use for detailed data tables, supplementary analysis, or Q&A backup slides

## Footer Details

- Logo: `h-3 opacity-60`
- Page number: `text-xs text-neutral-300 font-mono`, format `01 / 04`
- Footnote: `text-[9px] text-neutral-400` (NOT neutral-300, too light to read)

## Tables

Slides use CSS grid to build tables — NOT `<table>` HTML elements. This gives full control over spacing, alignment, and responsive behavior.

### Structure

```jsx
{/* Table container */}
<div className="flex flex-col gap-0">
  {/* Header row */}
  <div
    className="grid grid-cols-[1.2fr_0.8fr_0.8fr_1fr_0.6fr_1.5fr] gap-2 px-4 py-2.5 rounded-t-xl"
    style={{ backgroundColor: `${colors.primary}10` }}
  >
    {columns.map(col => (
      <div className="text-[10px] font-bold uppercase tracking-wider text-neutral-600">{col}</div>
    ))}
  </div>

  {/* Data rows */}
  {rows.map((row, i) => (
    <div
      className="grid grid-cols-[1.2fr_0.8fr_0.8fr_1fr_0.6fr_1.5fr] gap-2 px-4 py-2.5 items-center"
      style={{
        backgroundColor: row.highlight ? `${colors.primary}06` : i % 2 === 0 ? '#fafafa' : '#ffffff',
        borderLeft: row.highlight ? `3px solid ${colors.primary}` : '3px solid transparent',
      }}
    >
      {/* Cell content */}
    </div>
  ))}

  {/* Bottom border */}
  <div className="h-px rounded-b-xl" style={{ backgroundColor: `${colors.primary}15` }} />
</div>
```

### Typography

| Element | Style |
|---------|-------|
| Header text | `text-[10px] font-bold uppercase tracking-wider text-neutral-600` |
| Cell text (primary) | `text-[12px] text-neutral-800` or `font-bold` for name column |
| Cell text (secondary) | `text-[12px] text-neutral-500` |
| Badge in cell | `text-[9px] font-bold px-1.5 py-0.5 rounded-full text-white` + primary bg |

### Row Separation

Use **alternating background colors** for row separation — NOT horizontal border lines.

| Pattern | Style |
|---------|-------|
| Even rows | `#fafafa` (very subtle gray) |
| Odd rows | `#ffffff` (white) |
| Highlighted row | `${colors.primary}06` (primary tint) + `borderLeft: 3px solid ${colors.primary}` |
| Header | `${colors.primary}10` (stronger primary tint) + `rounded-t-xl` |
| Bottom border | Single `h-px` div with `${colors.primary}15` |

### Row Separation — When to use divider lines

For **simple comparison tables** (2-3 columns, fewer rows), use thin horizontal dividers instead of zebra striping:

```jsx
<div className="grid grid-cols-[80px_1fr_1fr] gap-x-3 gap-y-0">
  {/* Header */}
  <div className="text-[10px] font-bold text-neutral-400">维度</div>
  <div className="text-[10px] font-bold text-neutral-400">选项 A</div>
  <div className="text-[10px] font-bold" style={{ color: colors.primary }}>选项 B</div>

  {/* Divider line spanning all columns */}
  <div className="col-span-3 h-px bg-neutral-100 my-1" />

  {/* Row content */}
  <div className="text-[12px] font-medium text-neutral-600">维度名</div>
  <div className="text-[12px] text-neutral-400">选项 A 内容</div>
  <div className="text-[12px] font-medium text-neutral-700">选项 B 内容</div>
</div>
```

### Rules

- **NEVER use `<table>`, `<tr>`, `<td>`** — use CSS grid
- **Column widths**: use `fr` units (`1fr`, `0.8fr`, `1.5fr`) — NEVER fixed pixel widths
- **Row height**: `py-2.5` (10px vertical padding) — consistent across all rows
- **Cell gap**: `gap-2` (8px) horizontal gap between cells
- **Highlight row**: left border accent (`3px solid ${colors.primary}`) + light primary bg
- **Zebra vs dividers**: Use zebra striping for data tables (≥5 rows). Use divider lines for comparison tables (2-4 rows)
- **Responsive**: grid-cols template adapts to content — wider columns for text-heavy fields, narrower for badges/status

## Tab/Toggle Patterns

- Use `TabSwitcher` component + `useState` for multi-view switching within a slide
- Order tabs by insight value — default to the most insightful view
- Suitable when a single slide needs to show multiple dimensions of the same data
