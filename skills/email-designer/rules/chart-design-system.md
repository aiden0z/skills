# Chart Design System (Email-Embedded Charts)

Agent MUST read this file before generating any chart with `code-blocks/chart-generator.py`.
These rules ensure charts look professional and render correctly when embedded in emails.

## 1. Size Specifications

| Size | Dimensions | Use Case |
|------|-----------|----------|
| Full-width | `container_width` × 432px | Single chart per section |
| Half-width | `(container_width - 24px) / 2` × 360px | Side-by-side charts (24px gap) |
| Small | 450px × 252px | Inline thumbnail |

### Export settings

- **Export scale**: 2.0× (Retina clarity — a 1168px chart renders as 2336px PNG)
- **Margins**: tight for email (left:5, right:5, top:60, bottom:0)
- **Background**: white `#ffffff` (no transparency — PNG on white)

### Size calculation examples

```
600px email  → full-width chart = 568px  (600 - 32px padding)
800px email  → full-width chart = 768px  (800 - 32px padding)
1200px email → full-width chart = 1168px (1200 - 32px padding)
```

## 2. Color System

### 2.1 Status colors (semantic)

Use these for data that has inherent meaning (good/bad/warning/info):

| Semantic | Color | Hex | When to use |
|----------|-------|-----|-------------|
| Danger / Critical | Red | `#dc2626` | Errors, critical items, negative deltas |
| Warning / Attention | Amber | `#f59e0b` | Warnings, new items, approaching limits |
| Success / Positive | Green | `#059669` | Completed, resolved, positive trends |
| Info / Neutral | Blue | `#3b82f6` | Ratios, percentages, informational |

### 2.2 Gradient palettes (ordered data)

For data with natural ordering (priority levels, time periods, severity):

**Warm gradient** (critical → low):
```
#dc2626 → #f97316 → #fbbf24 → #fef08a
(red)     (orange)   (amber)    (light yellow)
```

**Cool gradient** (primary → tertiary):
```
#2563eb → #60a5fa → #93c5fd → #bfdbfe
(blue)    (light blue) (lighter) (lightest)
```

**Single-hue gradient** (for heatmaps):
```
#ffffff → #fed7aa → #fdba74 → #fb923c → #f97316 → #ea580c
(white)   (very light orange → → → deep orange)
```

### 2.3 Categorical palette (no inherent meaning)

When data categories have no semantic meaning, use this sequence:

```
#3b82f6, #059669, #f59e0b, #8b5cf6, #ec4899, #94a3b8
(blue)    (green)   (amber)   (purple)  (pink)    (slate)
```

**Rule**: Never use more than 6 distinct colors in one chart. If data has more than 6 categories, group smaller ones into "Other" using `#94a3b8`.

### 2.4 Chart infrastructure colors

| Element | Hex | Usage |
|---------|-----|-------|
| Axis tick labels | `#9ca3af` | Numbers and category labels on axes |
| Legend text | `#6b7280` | Legend item labels |
| Grid lines | `#e5e7eb` | Background grid (when shown) |
| Text on dark backgrounds | `#ffffff` | Data labels inside dark bars |
| Text on light backgrounds | `#1a1a1a` | Data labels inside light bars, annotations |
| Fallback / unknown | `#94a3b8` | "Other" category, missing data |

### 2.5 Color consistency rules

- Status colors MUST be consistent across all charts in one email
- Same data series MUST use the same color in different charts
- Dark backgrounds → white text; light backgrounds → dark text
- Text color threshold: use white text when background lightness < 40%

## 3. Typography

### Font family

Chinese-friendly fallback chain (matches email design system):

```
PingFang SC, Heiti SC, STHeiti, Songti SC, Arial Unicode MS, Microsoft YaHei, sans-serif
```

### Font size scale

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Chart title | 14px | normal | `#1a1a1a` |
| Axis title | 14px | normal | `#6b7280` |
| Base text | 14px | normal | `#6b7280` |
| Tick labels | 11px | normal | `#6b7280` |
| Legend | 11px | normal | `#6b7280` |
| Data labels | 10px | **bold** | varies (see §4) |
| Annotations | 10px | normal | varies |

## 4. Data Label Strategy

| Chart Type | textposition | Color Logic | Zero Handling |
|------------|-------------|-------------|---------------|
| Stacked bar | `auto` | White inside dark bars, `#1a1a1a` outside/inside light bars | Hide (empty string) |
| Grouped bar | `inside` | White | Hide (empty string) |
| Line chart | `bottom center` | Match line color | Show |
| Percentage labels | `bottom center` | `#3b82f6` (blue) | Show as "0%" |
| Heatmap cells | centered in cell | White when value > 40% of max, `#1a1a1a` otherwise | Show "0" |
| Pie chart | `inside` | White | Hide (empty string) |

### Stacked bar auto-positioning

Use Plotly's `textposition='auto'` with separate inside/outside font configs:

```python
# Inside text: white, bold
insidetextfont={'size': 10, 'color': 'white', 'weight': 'bold'}
# Outside text: dark, bold (for bars too small to fit text)
outsidetextfont={'size': 10, 'color': '#1a1a1a', 'weight': 'bold'}
constraintext='none'  # Don't constrain text to bar size
```

## 5. Layout Conventions

### Legend

- Position: horizontal, centered above chart
- Plotly config: `orientation='h'`, `y=1.02`, `x=0.5`, `xanchor='center'`, `yanchor='bottom'`

### Axes

- X-axis: `type='category'` (prevents date auto-formatting), `showgrid=False`, `zeroline=False`
- Y-axis: `showgrid=False`, `zeroline=False`
- Tick labels: angled at -30° when > 6 categories (readability)

### Background

- Plot background: `#ffffff` (white)
- Paper background: `#ffffff` (white)

### Bar charts

- `bargap=0.3` (30% gap between bars)
- Y-axis range: `[0, max_value * 1.15]` (15% headroom for labels above bars)
- Hide Y-axis tick labels for stacked bars (totals shown as annotations)

### Heatmap

- Show colorbar: right side, thickness=15, length=0.7
- Left margin: 80px (space for Y-axis labels)
- Bottom margin: 100px (space for angled X-axis labels)
- Cell annotations: show exact values centered in each cell

## 6. Chart Type Recommendations

| Data Pattern | Recommended Chart | When to Use |
|-------------|-------------------|-------------|
| Categories × single value | Horizontal bar | Comparing quantities across categories |
| Categories × multiple series | Stacked bar (vertical) | Composition breakdown per category |
| Time × values | Line chart | Trends over periods |
| 2D matrix (rows × cols) | Heatmap | Cross-tabulation, correlation |
| Parts of whole (≤ 6 slices) | Pie / Donut | Percentage distribution |
| Single KPI value | **Use HTML stats-grid** | Don't generate a chart — use the stats-grid component |

**Rule**: If data has ≤ 5 values total, prefer an HTML table or stats-grid component over a chart. Charts add visual weight — only generate one when the pattern is hard to see in a table.

## 7. Output Format

- **Format**: PNG (white background, no transparency)
- **Filename**: ASCII only, snake_case (e.g., `sales_by_region.png`, `monthly_trend.png`)
- **Directory**: `images/` subdirectory of the output project
- **File size target**: < 200KB per chart (2x export at tight margins typically achieves this)
- **CID handling**: Automatic — `html-to-eml.py` converts `src="images/..."` to `src="cid:..."` during EML generation

## 8. Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using > 6 colors | Group small categories into "Other" (`#94a3b8`) |
| Inconsistent colors across charts | Define color mapping once, reuse for all charts |
| Chart for ≤ 5 data points | Use HTML table or stats-grid component instead |
| Missing data labels | Always show values (except zeros, which are hidden) |
| Transparent background | Set both plot and paper bgcolor to `#ffffff` |
| Non-ASCII filename | Use snake_case ASCII: `revenue_chart.png` not `收入图表.png` |
| Too-wide chart for email | Match chart width to `container_width - 32px` (side padding) |
