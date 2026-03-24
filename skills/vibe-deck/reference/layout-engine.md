# Layout Decision Engine

A 5-step process for choosing the right slide layout. The key insight: different slides have different purposes, and layout rules should flex accordingly. A showcase slide's density is a feature; a data slide's density is a bug.

## Step 1: Understand the Slide

Before touching layout, answer three questions about this slide.

### 1a. What's the intent?

The audience will interact with different slides in fundamentally different ways. A "What is X?" slide needs room to explain; a "Resources" slide will be photographed. Applying the same density rules to both produces bad advice.

| Intent | Audience will... | Examples | Density |
|--------|-----------------|---------|---------|
| **data** | Analyze a number or trend | Revenue chart, KPI dashboard, funnel | Strict — every element serves the takeaway |
| **concept** | Understand an idea | "What is X?", "How does Y work?" | Moderate — definition + components + comparison is one concept, not three |
| **showcase** | Feel impressed | "This was made by AI", demo results | Relaxed — density IS the message |
| **reference** | Photograph for later | Resource links, install guide, cheat sheet | Relaxed — completeness > elegance |
| **tool** | Learn a specific product | IDE walkthrough, terminal demo | Moderate — mockup brand colors are exempt from theme |
| **narrative** | Orient themselves | Cover, divider, agenda, thank you | Minimal — pacing, not content |

### 1b. Who's the audience?

Audience determines how much text each element can carry. Determine this once per deck, not per slide.

| Audience | Density Level | Font Sizes | Text per Card |
|----------|--------------|-----------|---------------|
| **Executive / Board** | Sparse — big numbers, minimal text | Title 32px, Body 14px | 1 line + value |
| **Team / Internal** (default) | Standard — balanced | Title 28px, Body 12px | 2–3 lines |
| **Technical / Workshop** | Dense — detailed, code OK | Title 24px, Body 11px | 3–4 lines |

Trigger words: "board meeting" / "investor" → Sparse. "training" / "workshop" / "internal share" → Dense.

### 1c. What's the single takeaway?

State what the audience should remember from this slide in one sentence.

- **data/concept/tool**: If you can't state it in one sentence, the content probably belongs on 2 slides. But for concept slides, "understand X" can naturally span definition + structure + comparison — that's still one takeaway.
- **showcase**: "Look how much was accomplished" — density serves this.
- **reference**: "Here's where to find everything" — completeness serves this.

## Step 2: Choose Layout

Match the slide's content to a layout pattern. Two paths: use a single layout, or compose from zones.

### Single Layout Matching

| Content Profile | Layout | Why |
|----------------|--------|-----|
| 1 chart, ≤ 3 bullets | **FullChart** | Chart dominates, text supports |
| 2 charts OR chart + text | **SplitView** | Side-by-side comparison |
| 2–6 metrics, no chart | **MetricGrid** | Numbers in grid scan fastest |
| 2 things compared, similar depth | **ComparisonView** | Symmetry highlights differences |
| 2 things compared, very unequal depth | **ComparisonView** with centered short column, or **DataTable** | See content-rules.md > Unequal columns |
| 5+ rows × 3+ cols | **DataTable** | Grid = fastest tabular scan |
| 3–5 sequential phases | **TimelineFlow** | Horizontal flow = time |
| 4–6 items with description | **CardGrid** | 2×2 or 2×3 with icon + text |
| 2–4 items, brief | **CardRow** | Single row, stretch to fill |
| Explanation, no data | **ConceptSlide** | Larger fonts, no KeyMessage |
| Tool + UI mockup | **SplitView** or custom | Left: features, Right: mockup |
| Resource collection | **multi-section grid** | Labeled grids stacked |

For code templates of each layout, see [layout-templates.md](layout-templates.md).

### Composite Layouts (mixed content)

When a slide combines content types (e.g., chart + metrics, table + recommendation cards), divide the content area into **zones**:

```
Vertical:                          Horizontal:
┌─────────────────────────┐       ┌────────────┬────────────┐
│  Zone A: Primary 60-70% │       │ Zone A     │ Zone B     │
├─────────────────────────┤       │ 50-60%     │ 40-50%     │
│  Zone B: Secondary 30%  │       └────────────┴────────────┘
└─────────────────────────┘
```

**Common composites** (see [layout-templates.md](layout-templates.md) for code):

| Pattern | Zone A | Zone B | Code Skeleton |
|---------|--------|--------|--------------|
| Chart + Metrics | Chart (`flex-[2]`) | MetricCard row (`grid-cols-3`) | `flex flex-col gap-3` |
| Chart + Text | Chart (`w-3/5`) | Analysis bullets (`w-2/5`) | `flex gap-4 h-full` |
| Mini Dashboard | Chart 1 | Chart 2 | `grid grid-cols-2 gap-3` |
| Table + Cards | DataTable (`flex-[3]`) | Rec cards (`grid-cols-3`) | `flex flex-col gap-3` |

**Zone rules:**
- One zone should dominate (60-70%). Equal splits feel indecisive.
- Zone A = proves the takeaway. Zone B = contextualizes it.
- Two unrelated charts = two different takeaways = two slides.

**Zone count by intent:**

| Intent | Max Zones | Why |
|--------|----------|-----|
| data | 2 | Focus on one story |
| concept / tool | 2–3 | Definition + illustration + comparison is natural |
| showcase / reference | 3–4 | Completeness and density serve the purpose |

## Step 3: Check Capacity

Every layout has limits. When content exceeds them, adapt before it breaks. The limits below are for **Team/Standard** density — scale down for Executive, up for Technical (see Step 1b).

### Layout Capacity Limits

| Layout | Capacity | Overflow Strategy |
|--------|----------|-------------------|
| **MetricGrid** | 6 cards (3×2) | > 6 → split into 2 slides, or TabSwitcher |
| **CardGrid** | 6 cards (2×3) | > 6 → split, or compact list |
| **CardRow** | 4 items | > 4 → switch to CardGrid |
| **DataTable** | 8 rows × 6 cols | Rows > 8 → top-N + footnote; Cols > 6 → hide low-priority |
| **TimelineFlow** | 5 phases | > 5 → split into 2 timeline slides |
| **BarChart** | 8 categories | > 8 → horizontal; > 15 → group or top-N |
| **PieChart** | 6 slices | > 6 → merge small into "Other" |
| **KeyMessage** | 3 bullets, 25 CJK / 60 EN | Excess → trim or footnote |

**Intent adjustments** — showcase and reference slides get more room because their purpose demands it:

| | data | concept | showcase / reference |
|---|------|---------|---------------------|
| MetricGrid | 6 | 6 | 8 |
| CardGrid | 6 | 6 | 8 |
| DataTable rows | 8 | 6 | 10 |
| Zones | 2 | 2–3 | 3–4 |
| Visual elements | 10–18 | 10–25 | no hard limit |

### When to Split

Split when content can't fit at readable sizes — but check intent first.

**Don't split** (even if dense):
- **showcase** slides — density IS the message
- **reference** slides — completeness matters more than elegance
- The slide renders at 1440×810 with all text readable

**Do split** when:
- Content exceeds limits above (adjusted for intent)
- Two genuinely different takeaways (not multi-dimensional explanation of one)
- Text overflows at minimum readable font size

**How to split:**
1. Find the natural break (different data sources, overview vs detail)
2. Slide 1: overview / summary / key numbers
3. Slide 2: breakdown / detail / supporting data
4. Add SlideDivider if starting a new section
5. Tell the user: "Split into 2 slides: [title 1] and [title 2]"

## Step 4: Adapt Components

When content is near the capacity edge, components should self-adjust before triggering a split. These are guidelines for the agent building the slide — the components themselves don't auto-adapt (yet).

**MetricCard — font sizing by value length:**
- ≤ 7 chars (`$1.2M`, `85%`): `text-[28px]` (default)
- 8+ chars (`$123,456`): `text-[22px]`

**BarChart — orientation by label length:**
- Labels ≤ 4 chars average: vertical (default)
- Labels > 8 chars average: `horizontal={true}`
- Categories > 8: horizontal + consider top-N

**PieChart — label strategy by slice count:**
- ≤ 4 slices: external labels with value + percent
- 5–6 slices: external labels, smaller font
- > 6 slices: merge small into "Other", use Legend below

**DataTable — column sizing by count:**
- ≤ 4 cols: equal `1fr`
- 5–6 cols: primary wider (`1.2fr`), others `0.8fr`
- 7+ cols: hide lowest-priority, add "..." indicator

## Step 5: Validate

After building the slide, run through these checks. This is the same checklist as SKILL.md Step 7 (Layout Verification) — reference it there rather than duplicating here.

**Quick sanity checks specific to the layout engine:**
- [ ] Intent classification still holds? (did the content shift during building?)
- [ ] Zone proportions match the 60/40 or 70/30 plan?
- [ ] No layout was forced — if you struggled to fit content, reconsider splitting
- [ ] Composite layouts have at most the zone count allowed for this intent type

For the full visual checklist (text truncation, overlap, hierarchy, whitespace, chart readability), see **SKILL.md Step 7: Layout Verification**.

---

## Quick Reference Card

For fast decisions, this is the engine in 4 questions:

1. **What will the audience DO?** → intent type → density tolerance
2. **What content is there?** → match to layout or compose zones
3. **Does it fit?** → check capacity limits (adjusted for intent + audience)
4. **Does it look right?** → validate or split
