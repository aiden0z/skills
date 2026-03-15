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
