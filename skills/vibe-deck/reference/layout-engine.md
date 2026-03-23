# Layout Decision Engine

Before choosing a layout, run through this decision engine. It replaces guesswork with a systematic process: classify intent → analyze content → match layout → check capacity → compose if needed.

## Phase 0: Slide Intent Classification

**Do this FIRST.** Different slide types have fundamentally different rules. Applying data-slide density rules to a showcase slide produces false alarms.

| Intent | Description | Examples | Density Tolerance |
|--------|------------|---------|------------------|
| **data** | Charts, metrics, quantitative analysis | Revenue chart, KPI dashboard, funnel analysis | Strict — every element must serve the takeaway |
| **concept** | Explain what/why/how about a topic | "What is X?", "How does Y work?", comparison of approaches | Moderate — multi-dimensional explanation (definition + components + comparison) is normal for one slide |
| **showcase** | Demonstrate capability, impress | "This PPT was made by AI", product demo results | Relaxed — density itself is the message, don't limit |
| **reference** | Resource list, links, cheat sheet — audience will photograph | Resource links, installation guide, getting started paths | Relaxed — multiple sections OK, people save this slide |
| **tool** | Introduce a specific tool with UI mockup | IDE walkthrough, terminal demo, tool comparison | Moderate — mockup colors are exempt from theme rules |
| **narrative** | Story transition, chapter break, opening/closing | Cover, divider, agenda, thank you | Minimal — these are pacing elements, not content |

**How to classify:** Ask "What will the audience DO with this slide?"
- Analyze a number → **data**
- Understand a concept → **concept**
- Feel impressed → **showcase**
- Photograph for later → **reference**
- Learn a tool → **tool**
- Orient themselves in the talk → **narrative**

## Phase 1: Content Inventory

Count and classify everything the slide needs to show:

```
For each slide, list:
  metrics:     N  (single numbers with labels, e.g., "$2.4M Revenue")
  charts:      N  (bar, line, pie, funnel, ring, stacked bar)
  text_blocks: N  (paragraphs, bullet lists, descriptions)
  table_rows:  N  (comparison or data table rows)
  table_cols:  N  (table columns)
  list_items:  N  (feature items, steps, capabilities)
  images:      N  (screenshots, icons, logos)
  timeline:    N  (phases, milestones, steps in sequence)
```

**Single Takeaway Check — adjusted by intent:**
- **data/concept/tool**: State the slide's ONE takeaway in a single sentence. If you can't → consider splitting.
- **showcase**: The takeaway is "look how much was accomplished" — density serves it.
- **reference**: The takeaway is "here's where to find everything" — completeness serves it.
- For concept slides, "What is X?" naturally combines definition + components + comparison. That's ONE takeaway ("understand X"), not three.

## Phase 2: Semantic Layout Matching

Match content profile to layout. This table encodes "what data pattern → what layout":

| Content Profile | Layout | Why This Works |
|----------------|--------|---------------|
| 1 chart, ≤ 3 bullets | **FullChart** | Chart dominates, text supports |
| 2 charts OR chart + text block | **SplitView** | Side-by-side lets eye compare |
| 2–6 metrics, no chart | **MetricGrid** | Numbers in grid scan fastest |
| 2 things being compared | **ComparisonView** | Symmetry shows differences |
| 5+ rows × 3+ cols of data | **DataTable** | Grid structure = fastest scan for tabular data |
| 3–5 sequential phases | **TimelineFlow** | Horizontal flow = time progression |
| 4–6 feature items with descriptions | **CardGrid** | 2×2 or 2×3 grid with icon + text |
| 2–4 items in a row (no deep description) | **CardRow** | Single row, items stretch to fill |
| Concept explanation, no data | **ConceptSlide** | Larger fonts, breathing room, no KeyMessage |
| Tool intro with UI mockup | **SplitView** or **custom** | Left: features/steps, Right: mockup screenshot |
| Resource/link collection | **multi-section grid** | Multiple labeled grids stacked vertically |
| 1 chart + 2–4 metrics | **Composite: chart + metrics** | See Phase 4 |
| Chart + table | **Composite: chart + table** | See Phase 4 |

**Ambiguous cases:**
- If content matches multiple layouts → pick the one that best serves the takeaway
- If content matches none → check intent first. Reference/showcase slides can break templates; data slides should split.

## Phase 3: Capacity Check

Capacity limits vary by slide intent and audience density level.

### Capacity Limits by Intent

| Layout | data | concept | showcase/reference | Overflow Strategy |
|--------|------|---------|-------------------|-------------------|
| **MetricGrid** | 6 cards | 6 cards | 8 cards | Split or TabSwitcher |
| **CardGrid** | 6 cards | 6 cards | 8 cards | Split or compact list |
| **CardRow** | 4 items | 4 items | 4 items | Switch to CardGrid |
| **DataTable** | 8 rows × 6 cols | 6 rows × 5 cols | 10 rows × 6 cols | Paginate or top-N |
| **TimelineFlow** | 5 phases | 5 phases | 5 phases | Split into 2 slides |
| **Zones per slide** | 2 | 2–3 | 3–4 | Split if exceeding |
| **Visual elements** | 10–18 | 10–25 | no hard limit | Split if unreadable |
| **Text per card** | 2–3 lines | 2–3 lines | 1–4 lines | Trim or split |

### Audience Density Adjustment

Phase 5 density levels further modify these limits:

| | Executive | Team (default) | Technical |
|---|----------|---------------|-----------|
| MetricGrid max | 4 | 6 | 8 |
| CardGrid max | 4 | 6 | 8 |
| Font: Title | 32px | 28px | 24px |
| Font: Body | 14px | 12px | 11px |
| Text per card | 1 line | 2–3 lines | 3–4 lines |

### Adaptive Component Behaviors

When content hits the edge of a capacity limit, components should adapt before triggering overflow:

**MetricCard — auto font sizing:**
- Value ≤ 4 chars (e.g., `85%`): `text-[28px]`
- Value 5–7 chars (e.g., `$1.2M`): `text-[28px]` (default)
- Value 8+ chars (e.g., `$123,456`): `text-[22px]`

**BarChart — auto orientation:**
- Category labels ≤ 4 chars average: vertical bars (default)
- Category labels > 8 chars average: switch to `horizontal={true}`
- Categories > 8: switch to horizontal + consider top-N

**PieChart — auto label strategy:**
- ≤ 4 slices: external labels with value + percent
- 5–6 slices: external labels, smaller font
- > 6 slices: merge small slices into "Other", use Legend component below

**DataTable — auto column compression:**
- ≤ 4 cols: equal `1fr` widths
- 5–6 cols: primary col wider (`1.2fr`), others `0.8fr`
- 7+ cols: consider hiding lowest-priority columns, add "..." indicator

## Phase 4: Composite Layouts

For mixed content that no single template covers, compose from building blocks.

### Composition Grammar

Every slide's content area is a flex column. Divide it into **zones**:

```
┌─────────────────────────────┐
│  Zone A: Primary (60-70%)   │  ← chart, table, or main content
├─────────────────────────────┤
│  Zone B: Secondary (30-40%) │  ← metrics, summary, action items
└─────────────────────────────┘

OR horizontal split:

┌──────────────┬──────────────┐
│  Zone A      │  Zone B      │
│  (50-60%)    │  (40-50%)    │
└──────────────┴──────────────┘
```

### Common Composite Patterns

**Pattern: Chart + Metrics (most common composite)**
```jsx
<SlideLayout title="..." keyMessage={[...]}>
  <div className="flex flex-col h-full gap-3">
    {/* Zone A: Chart — takes 65% */}
    <div className="flex-[2] min-h-0">
      <BarChart data={...} />
    </div>
    {/* Zone B: Metrics row — takes 35% */}
    <div className="grid grid-cols-3 gap-3">
      <MetricCard value="$2.4M" label="Total" ... />
      <MetricCard value="+18%" label="QoQ" ... />
      <MetricCard value="85%" label="Target" ... />
    </div>
  </div>
</SlideLayout>
```

**Pattern: Chart + Text Analysis**
```jsx
<div className="flex gap-4 h-full">
  <div className="w-3/5 min-h-0"><LineChart ... /></div>
  <div className="w-2/5 flex flex-col gap-3 justify-center">
    {/* Analysis bullets or insight cards */}
  </div>
</div>
```

**Pattern: Mini Charts Dashboard (2–3 small charts)**
```jsx
<div className="grid grid-cols-2 gap-3 h-full">
  <div><PieChart ... height="100%" /></div>
  <div><BarChart ... height="100%" /></div>
</div>
```

**Pattern: Table + Recommendation Cards**
```jsx
<div className="flex flex-col h-full gap-3">
  <div className="flex-[3]">{/* DataTable */}</div>
  <div className="grid grid-cols-3 gap-2">{/* 3 recommendation cards */}</div>
</div>
```

### Composition Rules

Zone limits depend on intent (see Phase 3 table):
- **data slides**: Max 2 zones — focus on one story
- **concept/tool slides**: Max 2–3 zones — definition + illustration + comparison is normal
- **showcase/reference slides**: Max 3–4 zones — completeness and density serve the purpose
- **One zone dominates** (60-70% of space) — equal splits feel indecisive
- **Zone A = what proves the takeaway** (chart, data, main explanation)
- **Zone B = what contextualizes it** (metrics, actions, details)
- Never put 2 unrelated charts in the same slide — if they serve different takeaways, they need separate slides

## Phase 5: Content Density Calibration

Calibrate density to audience. This phase connects directly to Phase 3's capacity limits.

| Audience | Density | Font Sizes | Items per Card |
|----------|---------|-----------|----------------|
| **Executive / Board** | Sparse — big numbers, minimal text | Title 32px, Body 14px | 1 metric + 1 line context |
| **Team / Internal** | Standard — balanced data + context | Title 28px, Body 12px | Title + 2–3 lines + example |
| **Technical / Workshop** | Dense — detailed data, code snippets | Title 24px, Body 11px | Title + 3–4 lines + aux data |

When the user hasn't specified audience, default to **Standard**. If they say "board meeting" or "investor", use Sparse. If they say "training" or "workshop", use Dense.

## Phase 6: Auto-Split Decision

When content exceeds a layout's capacity, split rather than cram — but check intent first.

**When NOT to split (even if dense):**
- **showcase** slides where density IS the message ("look how much AI produced")
- **reference** slides where completeness matters more than elegance (people will photograph it)
- The slide renders cleanly at 1440×810 with all text readable

**When to split:**
- Content inventory exceeds capacity limits from Phase 3 (adjusted for intent)
- Slide has 2+ distinct takeaways that serve different purposes (not just multi-dimensional explanation of one concept)
- Text overflows the content area at minimum readable font size
- For **data** slides: total visual elements > 18

**How to split:**
1. Identify the natural break point (different data sources, different topics, overview vs detail)
2. First slide: overview / summary / key numbers
3. Second slide: breakdown / detail / supporting data
4. Insert a SlideDivider between them if they start a new section
5. Notify the user: "This content is too dense for one slide. I've split it into 2 slides: [title 1] and [title 2]."

## Phase 7: Color & Style Validation

### Theme Color Rules

All design colors should use `import { colors } from '../theme'`. But some colors are exempt.

**Must use theme colors** (semantic design choices):
- Primary accents → `colors.primary`
- Success/positive indicators → `colors.success`
- Danger/negative indicators → `colors.danger`
- Warning/attention → `colors.accent`
- Text colors → `colors.text`, `colors.textSecondary`, `colors.muted`
- Card backgrounds → `${colors.primary}08`, `${colors.primary}15`

**Exempt from theme colors** (brand/mockup simulation):
- Terminal window chrome (`#ff5f57` red dot, `#febc2e` yellow dot, `#28c840` green dot)
- IDE/terminal backgrounds (`#1e1e2e`, `#181825`, etc.) — simulating real product UI
- Third-party brand colors when showing their product (e.g., a specific tool's purple)

**The test:** "Is this color OUR design choice, or are we simulating someone else's product?" Our choices → theme. Their product → hardcode is fine.

## Phase 8: Visual Self-Review (Optional)

After building a slide, verify the layout visually. Inspired by the excalidraw-diagram-skill's render → review → fix cycle.

**When the dev server is running**, use browser tools (if available) to screenshot the slide and check:

- [ ] No text truncated or overflowing its container
- [ ] No overlapping elements
- [ ] Clear visual hierarchy (title > keyMessage > content > footer)
- [ ] Content fills ≥ 80% of slide area (no large empty zones)
- [ ] Charts are readable (labels not overlapping, legend visible)
- [ ] Color contrast is sufficient (text on backgrounds)

**When no browser tools available**, use the Layout Verification checklist from SKILL.md Step 7 instead.

If issues are found: fix the layout, then re-verify. Maximum 2 iterations — if it still doesn't work, the content needs splitting.
