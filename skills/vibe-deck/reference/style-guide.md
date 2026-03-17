# Style Guide

## Typography

| Element | Class | Min Size |
|---------|-------|----------|
| Slide title | `text-[28px] font-bold` | 28px |
| Title subtitle | `text-sm font-normal text-neutral-400 ml-3` | 14px |
| Key Message | `text-[14px]` | 14px |
| Body / card title | `text-[13px]` | 13px |
| Chart label | `text-[10px]` | 10px |
| Footer | `text-xs` | 12px |

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

## Tab/Toggle Patterns

- Use `TabSwitcher` component + `useState` for multi-view switching within a slide
- Order tabs by insight value — default to the most insightful view
- Suitable when a single slide needs to show multiple dimensions of the same data
