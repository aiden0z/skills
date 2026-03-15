# Chart Components API

Import via: `import { StackedBar, BarChart, RingGauge, FunnelChart, PieChart, ConversionChart } from '../charts'`

## StackedBar

HTML-based horizontal stacked bar with hover tooltips.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `segments` | `[{ value, color, label }]` | required | Bar segments |
| `height` | `number` | 24 | Bar height in px |
| `className` | `string` | '' | Additional CSS |

```jsx
<StackedBar segments={[
  { value: 500, color: colors.primary, label: 'Software' },
  { value: 300, color: colors.primaryLight, label: 'Services' },
]} />
```

## BarChart

ECharts vertical/horizontal bar chart for simple category comparisons.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `[{ name, value, color? }]` | required | Bar items |
| `height` | `string` | '100%' | Chart height |
| `horizontal` | `boolean` | false | Flip to horizontal bars |
| `barWidth` | `string` | '50%' | Bar width |
| `showLabel` | `boolean` | true | Show value labels |

```jsx
<BarChart data={[
  { name: 'Region A', value: 300 },
  { name: 'Region B', value: 200 },
  { name: 'Region C', value: 150 },
]} />
```

**When to use BarChart vs StackedBar**: `BarChart` is ECharts-based with axes, tooltips, and labels — use for comparing categories. `StackedBar` is HTML-based, renders a single horizontal bar with colored segments — use for showing composition of a single total.

## RingGauge

ECharts gauge ring for achievement rates.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `number` | required | Percentage (0-100) |
| `label` | `string` | required | Label below |
| `sublabel` | `string` | - | Secondary text |
| `color` | `string` | required | Ring color |
| `size` | `number` | 90 | Width/height px |

```jsx
<RingGauge value={85.2} label="达成率" sublabel="853/1000" color={colors.primary} />
```

## FunnelChart

ECharts funnel for pipeline visualization.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `tiers` | `[{ name, value, color? }]` | required | Funnel tiers |
| `height` | `string` | '100%' | Chart height |
| `showBottomLabel` | `{ text, color }` | - | Bottom summary |

## PieChart

ECharts pie/donut chart.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `[{ name, value, color? }]` | required | Pie slices |
| `height` | `string` | '100%' | Chart height |
| `showLabel` | `boolean` | true | Show labels |
| `radius` | `[string, string]` | ['40%','70%'] | Inner/outer |

## ConversionChart

Dual-axis: bar counts + line conversion rate.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `categories` | `string[]` | required | X-axis labels |
| `countData` | `[{ name, data, color }]` | required | Bar series |
| `rateData` | `number[]` | required | Line % values |
| `rateName` | `string` | '转化率' | Line name |

## ECharts General Rules

### Data Labels
- ALL ECharts charts MUST have `label: { show: true }`
- StackedBar: segment label shows `value · percent%` only when segment width >= 20%
- PieChart: label format `name\nvalue · percent%`, use `overflow: 'break'`
- ECharts label `fontSize` minimum 12px (except segment-internal labels which can be 10px)

### Tooltip
- ALL charts MUST use `TOOLTIP_STYLE` from `src/lib/chart-theme.js`
- `appendToBody: true` is REQUIRED — Slide container `overflow-hidden` clips tooltips without it
- For custom HTML bars (StackedBar), each segment has hover tooltip built in
- Tooltip format convention: `Type: value $K (percent%)`

### Heatmap (if needed)
- MUST configure `visualMap`, otherwise ECharts throws "Heatmap must use with visualMap"
- Use `type: 'piecewise'` + `pieces` for semantic color segments (e.g., conversion rate tiers)
- Use blue color scheme + red for warnings (NOT green — clashes with blue theme)
- Label color must adapt to background: white text on dark cells, dark text on light cells
- Set label color per data item via `data[i].label.color` — more reliable than series-level functions

### Animation
- Keep ECharts built-in animations at defaults (`animationDuration: 800-1200`, `animationEasing: 'cubicOut'`)
- Do NOT disable or override ECharts animation unless specifically requested
