# Email Design System — Data Report Extension

> Read this file ONLY when generating data-heavy emails: weekly reports, KPI dashboards,
> status updates, product health reports, analytics digests.
> For general newsletters/announcements, the base `design-system.md` is sufficient.

## When to Use This Extension

Use these patterns when the email contains:
- KPI metrics / key numbers to highlight
- Status tracking (on track / at risk / blocked)
- Trend indicators (up/down changes vs. previous period)
- Priority levels (P1/P2/P3/P4)
- Progress tracking tables

## 1. Semantic Colors for Data

### Trend/Change Colors

| Meaning | Hex | Usage |
|---------|-----|-------|
| Positive / Success | `#059669` | Closed issues, goals met, positive trends |
| Warning / Attention | `#d97706` | Approaching limits, moderate risk, increase |
| Danger / Critical | `#dc2626` | Blocked, overdue, critical issues |
| Neutral / Info | `#3b82f6` | Reference lines, informational |
| No Change | `#94a3b8` | Flat trends, unchanged metrics |

### Priority Colors

| Level | Hex | Background tint |
|-------|-----|-----------------|
| P1 Critical | `#dc2626` | `#fef2f2` |
| P2 High | `#f97316` | `#fff7ed` |
| P3 Medium | `#fbbf24` | `#fffbeb` |
| P4 Low | `#fef08a` | `#fefce8` |

### Highlight Backgrounds

Use tinted backgrounds to draw attention to key areas:

| Hex | Usage |
|-----|-------|
| `#eff6ff` | Blue-tinted: progress highlights, key achievements |
| `#fef2f2` | Red-tinted: risk areas, items needing attention |
| `#f0fdf4` | Green-tinted: success metrics, completed items |
| `#fffbeb` | Yellow-tinted: warnings, items to watch |

## 2. Status Badges

Colored dot (●) + text label. Use inline within table cells or paragraphs.

| Status | Dot | Text | Example |
|--------|-----|------|---------|
| On Track | `#22c55e` | `#166534` | ●&nbsp;On Track |
| At Risk | `#d97706` | `#92400e` | ●&nbsp;At Risk |
| Blocked | `#ef4444` | `#991b1b` | ●&nbsp;Blocked |
| Completed | `#94a3b8` | `#475569` | ●&nbsp;Completed |

```html
<span style="color:#166534;font-size:13px;font-weight:500;white-space:nowrap;">
  <span style="color:#22c55e;font-size:10px;">&#9679;</span>&nbsp;On Track
</span>
```

Use the component at `templates/components/status-badge.html`.

## 3. Change Indicators

Show trends next to metric numbers:

```html
<!-- Increase (concerning — use when "up" is bad, e.g., open bugs) -->
<span style="color:#d97706;font-size:13px;font-weight:600;">↑ 5</span>

<!-- Decrease (positive — use when "down" is good, e.g., bug count) -->
<span style="color:#059669;font-size:13px;font-weight:600;">↓ 3</span>

<!-- No change -->
<span style="color:#94a3b8;font-size:13px;font-weight:400;">— 0</span>
```

Note: The color reflects whether the change is good or bad, not the direction.
A revenue increase would be green (↑), while an open-bug increase would be orange (↑).

## 4. Key Metrics Grid (Stats Cards)

Display 3-7 KPI numbers prominently. Each metric: large number + small label +
optional change indicator. No borders — just `#f8fafc` background.

| Property | Value |
|----------|-------|
| Number | 24px, weight 600, color `#334155` or semantic |
| Label | 12px, weight 400, color `#64748b` |
| Change | 13px, weight 600, semantic color |
| Cell padding | `12px 8px` |
| Background | `#f8fafc` |
| Column width | Percentage-based (e.g., `25%` for 4 metrics) |

Use the component at `templates/components/stats-grid.html`.

## 5. Data Table Enhancements

Beyond the base table types, data reports often need:

### Summary Row
Add a totals/summary row at the bottom with a heavier top border:
- Background: `#f8fafc`
- Text: 12px/600/`#334155`
- Top divider: 1px `#cbd5e1` (heavier than row dividers)

### Conditional Cell Colors
Color individual cells based on value:
- Critical values: text color `#dc2626`
- Warning values: text color `#d97706`
- Good values: text color `#059669`

### Sequence Column
For numbered lists within tables:
- Width: 22-30px
- Text: centered, `#64748b`, 12px
- Padding: `10px 4px` (tighter)

## 6. Progress Bars

Outlook-safe progress bars using two bgcolor table cells. No CSS gradients,
no border-radius — just two colored cells side by side.

```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0"
       width="120" style="width:120px;border-collapse:collapse;">
  <tr>
    <td width="75%" bgcolor="#2563eb" height="6"
        style="width:75%;height:6px;background-color:#2563eb;
               font-size:1px;line-height:6px;mso-line-height-rule:exactly;">&nbsp;</td>
    <td bgcolor="#e2e8f0" height="6"
        style="height:6px;background-color:#e2e8f0;
               font-size:1px;line-height:6px;mso-line-height-rule:exactly;">&nbsp;</td>
  </tr>
</table>
<p style="margin:2px 0 0 0;font-size:11px;color:#64748b;text-align:center;">75%</p>
```

Use the component at `templates/components/progress-bar.html`.

| Property | Value |
|----------|-------|
| Bar width | 100-140px (inside table cells) |
| Bar height | 6px |
| Fill color | Brand accent (e.g., `#2563eb`) |
| Track color | `#e2e8f0` |
| Label | 11px, `#64748b`, centered below |

Color the fill bar semantically when appropriate:
- `#059669` (green) for healthy progress (>75%)
- `#d97706` (orange) for moderate progress (40-75%)
- `#dc2626` (red) for stalled progress (<40%)

## 7. Chart Image Placeholders

Data reports often include charts. Standard dimensions:

| Type | Width | Height |
|------|-------|--------|
| Full-width chart | Container - 32px | ~400px |
| Half-width chart | (Container - 48px) / 2 | ~360px |
| Small chart | ~450px | ~250px |

Always include a chart title above the image:
- Background: `#f1f5f9`
- Text: 14px/600/`#334155`
- Padding: `6px 12px`
