# Dashboard Layout (数据面板布局)

## Applicable Scenarios
KPI dashboards, weekly reports, monthly reviews, data digests, analytics summaries

## Structure
1. **Header** (component: header.html)
   - Compact banner with report title and date range

2. **Stats Grid** (component: stats-grid.html)
   - 3-7 key metrics in a single row
   - Large number + label + optional change indicator

3. **Chart Section** (1-2 charts, component: image-placeholder.html)
   - Full-width or half-width chart placeholders
   - Chart title above each chart

4. **Data Table** (component: table.html)
   - Detailed breakdown data
   - Optional status badges and progress bars

5. **Alert / Callout** (component: alert.html or callout.html)
   - Key insight or action item

6. **Footer** (component: footer.html)

## Visual Layout
┌──────────────────────────┐
│       HEADER/BANNER      │
│    Report Title + Date   │
├──────────────────────────┤
│  [Metric 1] [Metric 2]  │
│  [Metric 3] [Metric 4]  │
├──────────────────────────┤
│     [Chart Placeholder]  │
│     Chart title above    │
├──────────────────────────┤
│  Data Table              │
│  Col A | Col B | Col C   │
│  ------+-------+------   │
│  data  | data  | data    │
├──────────────────────────┤
│  ▎ Key Insight / Action  │
├──────────────────────────┤
│         FOOTER           │
└──────────────────────────┘

## Default Style
- Primary color: #2563eb
- Background: #f5f5f5
- Recommended width: 800px
- Uses design-system-data-report.md extension for data colors
