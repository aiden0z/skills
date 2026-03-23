# Slide Layout Templates

**IMPORTANT: Always use `SlideLayout` for content slides.** It enforces the correct Title → KeyMessage → Content order. Do NOT manually arrange title and KeyMessage — the component handles positioning automatically.

**Layout order (enforced by SlideLayout):** Title → KeyMessage (optional) → Content. When `keyMessage` prop is provided, it renders right after the title, before the main content area. Omit `keyMessage` for slides where the data speaks for itself.

## SlideLayout API

```jsx
import SlideLayout from '../components/SlideLayout'

<SlideLayout
  title="Required Title"         // slide heading (required)
  subtitle="Optional subtitle"   // lighter text next to title
  keyMessage={<>...</>}          // content inside KeyMessage box; omit to skip
  keyLabel="Key Message"         // override KeyMessage label (default "Key Message")
>
  {/* Main content — fills remaining space */}
</SlideLayout>
```

**Rules:**
- `title` is required on every content slide
- `keyMessage` is optional — only use when the slide has a data-driven insight to highlight
- Do NOT render `<h2>` or `<KeyMessage>` manually — SlideLayout handles both
- Do NOT wrap SlideLayout in another `motion.div` with stagger — it has its own

## FullChart

One large chart with title and KeyMessage. Best for data-heavy single-metric slides.

```jsx
import SlideLayout from '../components/SlideLayout'

export default function SlideExample() {
  return (
    <SlideLayout
      title="Title Here"
      subtitle="Subtitle"
      keyMessage={<p>• Insight with quantified data</p>}
    >
      {/* Chart component here — fills remaining space */}
    </SlideLayout>
  )
}
```

## FullChart (no KeyMessage)

When the chart is self-explanatory, omit `keyMessage`:

```jsx
<SlideLayout title="Revenue Overview" subtitle="FY2024">
  {/* Chart fills full content area */}
</SlideLayout>
```

## SplitView

Left/right panels. Best for comparison or chart + explanation.

```jsx
<SlideLayout
  title="Title"
  keyMessage={<p>• Key insight</p>}
>
  <div className="flex gap-4 h-full">
    <div className="w-1/2">{/* Left */}</div>
    <div className="w-1/2">{/* Right */}</div>
  </div>
</SlideLayout>
```

## MetricGrid

Multiple metric cards. Best for dashboards and scorecards.

```jsx
import SlideLayout from '../components/SlideLayout'
import MetricCard from '../components/MetricCard'

<SlideLayout
  title="Key Metrics"
  keyMessage={<p>• All metrics trending up QoQ</p>}
>
  <div className="grid grid-cols-4 gap-3">
    <MetricCard value="85" unit="%" label="Metric 1" color="text-blue-600" />
    <MetricCard value="1,200" unit="$K" label="Metric 2" color="text-emerald-600" />
  </div>
</SlideLayout>
```

## ComparisonView

Side-by-side comparison with card styling. Feature lists inside each panel MUST use `justify-center gap-4` or `justify-between` to fill vertical space — NEVER `justify-start` which bunches content at the top.

```jsx
<SlideLayout title="Comparison" keyMessage={<p>• Option A outperforms by 20%</p>}>
  <div className="flex gap-3 h-full">
    <div className="flex-1 bg-neutral-50/80 border border-neutral-100 rounded-xl px-4 py-3 flex flex-col">
      <h3 className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 mb-2">Option A</h3>
      <div className="flex flex-col gap-4 flex-1 justify-center">
        {/* Feature items here — centered with consistent gap */}
      </div>
      <div className="text-[10px] text-neutral-400 mt-2">Footer info</div>
    </div>
    <div className="flex-1 rounded-xl px-4 py-3 flex flex-col"
      style={{ backgroundColor: `${colors.primary}08`, border: `1.5px solid ${colors.primary}25` }}>
      <h3 className="text-[10px] font-bold uppercase tracking-wider" style={{ color: colors.primary }}>Option B</h3>
      <div className="flex flex-col gap-4 flex-1 justify-center">
        {/* Feature items here */}
      </div>
    </div>
  </div>
</SlideLayout>
```

## CardRow

N items in a single row (2–4 items). Cards stretch to fill available width — **NEVER use fixed pixel widths**.

```jsx
<SlideLayout title="Feature Highlights">
  <motion.div
    className="grid grid-cols-3 gap-5 h-full content-center"
    variants={stagger} initial="hidden" animate="show"
  >
    {items.map((item, i) => (
      <motion.div
        key={i}
        className="flex flex-col items-center p-6 rounded-xl text-center"
        style={{ backgroundColor: `${colors.primary}06` }}
        variants={fadeIn}
      >
        <span className="text-3xl mb-3">{item.icon}</span>
        <h3 className="text-[16px] font-semibold mb-2" style={{ color: colors.text }}>
          {item.title}
        </h3>
        <p className="text-[13px] leading-relaxed" style={{ color: colors.textSecondary }}>
          {item.desc}
        </p>
      </motion.div>
    ))}
  </motion.div>
</SlideLayout>
```

**Rules:**
- Use `grid-cols-N` where N = number of items (2–4)
- `h-full content-center` to vertically center cards in the content area
- `gap-5` (20px) between cards
- Card padding: `p-5` or `p-6`

## DataTable

Comparison table using CSS grid. Best for tool comparisons, feature matrices, pricing tables.

```jsx
<SlideLayout title="Tool Comparison" subtitle="Key features at a glance">
  <div className="flex flex-col h-full gap-2">
    {/* Table */}
    <motion.div className="flex flex-col gap-0 flex-1" variants={stagger} initial="hidden" animate="show">
      {/* Header */}
      <motion.div
        className="grid grid-cols-[1.2fr_0.8fr_0.8fr_1fr_0.6fr_1.5fr] gap-2 px-4 py-2.5 rounded-t-xl"
        style={{ backgroundColor: `${colors.primary}10` }}
        variants={fadeIn}
      >
        {columns.map(col => (
          <div key={col} className="text-[10px] font-bold uppercase tracking-wider text-neutral-600">{col}</div>
        ))}
      </motion.div>

      {/* Rows */}
      {rows.map((row, i) => (
        <motion.div
          key={i}
          className="grid grid-cols-[1.2fr_0.8fr_0.8fr_1fr_0.6fr_1.5fr] gap-2 px-4 py-2.5 items-center flex-1"
          style={{
            backgroundColor: row.highlight ? `${colors.primary}06` : i % 2 === 0 ? '#fafafa' : '#fff',
            borderLeft: row.highlight ? `3px solid ${colors.primary}` : '3px solid transparent',
          }}
          variants={fadeIn}
        >
          <div className="text-[13px] font-bold text-neutral-800">{row.name}</div>
          <div className="text-[12px] text-neutral-500">{row.company}</div>
          {/* ... more cells */}
        </motion.div>
      ))}

      <div className="h-px rounded-b-xl" style={{ backgroundColor: `${colors.primary}15` }} />
    </motion.div>

    {/* Optional: recommendation cards below the table */}
  </div>
</SlideLayout>
```

**Rules:**
- Column widths use `fr` units — NEVER fixed pixel widths
- Header: `${colors.primary}10` background, `rounded-t-xl`
- Rows: alternating `#fafafa` / `#ffffff`, highlighted rows get primary tint + left border
- See `style-guide.md > Tables` for full styling reference

## CardGrid

4+ items in a 2×2 or 2×3 grid with icon + text. Best for capability lists and feature overviews.

**IMPORTANT:** Add `h-full` to each card so it stretches to fill its grid cell. Without `h-full`, cards have natural height and leave empty space in the grid cell.

```jsx
<SlideLayout title="Core Capabilities">
  <motion.div
    className="grid grid-cols-2 gap-2 flex-1"
    variants={stagger} initial="hidden" animate="show"
  >
    {items.map((item, i) => (
      <motion.div
        key={i}
        className="flex items-start gap-3 p-4 rounded-xl h-full"
        style={{ backgroundColor: `${colors.primary}06` }}
        variants={fadeIn}
      >
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-xl"
          style={{ backgroundColor: `${colors.primary}12` }}
        >
          {item.icon}
        </div>
        <div>
          <h3 className="text-[14px] font-bold mb-1" style={{ color: colors.text }}>
            {item.title}
          </h3>
          <p className="text-[12px] leading-relaxed" style={{ color: colors.textSecondary }}>
            {item.desc}
          </p>
          <p className="text-[10px] leading-snug mt-1" style={{ color: colors.muted }}>
            {item.example}
          </p>
        </div>
      </motion.div>
    ))}
  </motion.div>
</SlideLayout>
```

## ConceptSlide

For explanation / text-heavy slides WITHOUT data. **Do NOT add KeyMessage** — these slides have no quantitative data to highlight.

Best for: "What is X?", "Why choose Y?", concept introductions, process overviews.

```jsx
{/* Concept with left/right comparison */}
<SlideLayout title="What is X?" subtitle="From A to B">
  <div className="grid grid-cols-2 gap-8 h-full content-center">
    <div className="p-6 rounded-xl" style={{ backgroundColor: `${colors.muted}08` }}>
      <h3 className="text-[18px] font-semibold mb-4" style={{ color: colors.text }}>Before</h3>
      <ul className="text-[14px] space-y-3" style={{ color: colors.textSecondary }}>
        <li>• Point one</li>
        <li>• Point two</li>
      </ul>
    </div>
    <div className="p-6 rounded-xl border-2" style={{
      backgroundColor: `${colors.primary}08`,
      borderColor: `${colors.primary}25`,
    }}>
      <h3 className="text-[18px] font-semibold mb-4" style={{ color: colors.text }}>After</h3>
      <ul className="text-[14px] space-y-3" style={{ color: colors.textSecondary }}>
        <li>• Point one</li>
        <li>• Point two</li>
      </ul>
    </div>
  </div>
</SlideLayout>
```

**Rules:**
- NO `keyMessage` prop — concept slides are not data-driven
- Use larger font sizes (`text-[14px]`+ for body, `text-[18px]` for card titles) since there's more vertical space without KeyMessage
- Use `grid grid-cols-2` for side-by-side concepts, or single-column with generous spacing for linear flow
- Highlight the "after" / "featured" side with `border-2` and primary color tint

## Built-in Slide Templates

These are ready-to-use slide components included in `src/slides/`. Import and use directly — no custom layout needed. These do NOT use SlideLayout (they have their own specialized layouts).

### Divider (`SlideDivider`)

Chapter divider/transition page. Use between major sections.

**Usage:**
```jsx
import SlideDivider from '../slides/SlideDivider'

<Slide>
  <SlideDivider number="01" title="Market Analysis" subtitle="Understanding the landscape" />
</Slide>
```

Props: `number` (chapter number, e.g. "01"), `title` (required), `subtitle` (optional).

**Full source — `src/slides/SlideDivider.jsx`:**
```jsx
import { motion } from 'framer-motion'
import { colors } from '../theme'
import { stagger, fadeIn } from '../lib/animations'

export default function SlideDivider({ number, title, subtitle }) {
  return (
    <motion.div
      className="flex items-center h-full px-24"
      variants={stagger}
      initial="hidden"
      animate="show"
    >
      {/* 左侧编号 */}
      {number && (
        <motion.div className="shrink-0 mr-12" variants={fadeIn}>
          <span
            className="text-[96px] font-extrabold leading-none"
            style={{ color: colors.primary }}
          >
            {number}
          </span>
        </motion.div>
      )}

      {/* 右侧内容 */}
      <motion.div variants={fadeIn}>
        <div className="w-12 h-[3px] rounded-full mb-5" style={{ background: `linear-gradient(to right, ${colors.primary}, ${colors.primaryLight})` }} />
        <h2 className="text-[40px] font-bold tracking-tight leading-tight" style={{ color: colors.text }}>
          {title}
        </h2>
        {subtitle && (
          <p className="text-[17px] mt-3 leading-relaxed" style={{ color: colors.textSecondary }}>
            {subtitle}
          </p>
        )}
      </motion.div>
    </motion.div>
  )
}
```

### Agenda (`SlideAgenda`)

Table of contents with numbered items. Highlight the current section with `active`.

**Usage:**
```jsx
import SlideAgenda from '../slides/SlideAgenda'

<Slide title="Agenda">
  <SlideAgenda items={[
    { number: '01', title: 'Market Overview', active: true },
    { number: '02', title: 'Product Strategy' },
    { number: '03', title: 'Go-to-Market Plan' },
    { number: '04', title: 'Financials' },
  ]} />
</Slide>
```

Props: `title` (default "Agenda"), `items` (array of `{ number?, title, active? }`).

**Full source — `src/slides/SlideAgenda.jsx`:**
```jsx
import { motion } from 'framer-motion'
import { colors } from '../theme'
import { stagger, fadeIn } from '../lib/animations'

export default function SlideAgenda({ title = 'Agenda', items = [] }) {
  return (
    <motion.div
      className="flex flex-col h-full"
      variants={stagger}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={fadeIn} className="mb-8">
        <h2 className="text-[28px] font-bold tracking-tight" style={{ color: colors.text }}>
          {title}
        </h2>
      </motion.div>

      <motion.div className="flex flex-col gap-2 flex-1 justify-center pl-16" variants={stagger}>
        {items.map((item, i) => {
          const num = item.number || String(i + 1).padStart(2, '0')
          const isActive = !!item.active
          return (
            <motion.div
              key={i}
              className="flex items-center gap-6 py-4"
              variants={fadeIn}
            >
              <span
                className="text-[24px] font-bold font-mono w-10 shrink-0"
                style={{ color: isActive ? colors.primary : `${colors.muted}40` }}
              >
                {num}
              </span>
              <span
                className="text-[20px] tracking-tight"
                style={{
                  color: isActive ? colors.text : colors.muted,
                  fontWeight: isActive ? 600 : 400,
                }}
              >
                {item.title}
              </span>
            </motion.div>
          )
        })}
      </motion.div>
    </motion.div>
  )
}
```

### ThankYou (`SlideThankYou`)

Closing/Q&A page. Reads presenter info from config automatically, or accepts explicit contact.

**Usage:**
```jsx
import SlideThankYou from '../slides/SlideThankYou'

<Slide>
  <SlideThankYou />
</Slide>

{/* Or with explicit contact info */}
<Slide>
  <SlideThankYou
    title="Thank You"
    subtitle="Questions & Discussion"
    contact={{ email: 'team@example.com', phone: '+1 234 567' }}
  />
</Slide>
```

Props: `title` (default "Thank You"), `subtitle` (default "Questions & Discussion"), `contact` (optional `{ email?, phone?, wechat? }`).

**Full source — `src/slides/SlideThankYou.jsx`:**
```jsx
import { motion } from 'framer-motion'
import { config, colors } from '../theme'
import { stagger, fadeIn } from '../lib/animations'

export default function SlideThankYou({
  title = 'Thank You',
  subtitle = 'Questions & Discussion',
  contact,
}) {
  const p = config.presenter || {}
  const c = contact || {}
  const hasContact = c.email || c.phone || c.wechat || p.name

  return (
    <motion.div
      className="flex flex-col items-center justify-center h-full"
      variants={stagger}
      initial="hidden"
      animate="show"
    >
      <motion.div className="flex flex-col items-center text-center" variants={fadeIn}>
        <h1 className="text-[52px] font-extrabold tracking-tight" style={{ color: colors.text }}>
          {title}
        </h1>
        {subtitle && (
          <p className="text-[20px] font-light mt-3" style={{ color: colors.textSecondary }}>
            {subtitle}
          </p>
        )}
      </motion.div>

      {hasContact && (
        <motion.div className="mt-12 flex items-center gap-6 text-[13px]" style={{ color: colors.muted }} variants={fadeIn}>
          {(c.email || c.phone || c.wechat) ? (
            <>
              {c.email && <span>{c.email}</span>}
              {c.phone && <span>{c.phone}</span>}
              {c.wechat && <span>WeChat: {c.wechat}</span>}
            </>
          ) : (
            <>
              {p.name && <span className="font-semibold" style={{ color: colors.textSecondary }}>{p.name}</span>}
              {p.role && (
                <>
                  <div className="h-3 w-[1px]" style={{ backgroundColor: `${colors.muted}40` }} />
                  <span>{p.role}</span>
                </>
              )}
            </>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}
```
