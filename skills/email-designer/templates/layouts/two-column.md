# Two Column Layout (双栏布局)

## Applicable Scenarios
Feature comparisons, product catalogs, team introductions, side-by-side content presentations, pricing plans

## Structure
1. **Header** (component: header.html)
   - Full-width banner with brand color background
   - Optional logo placeholder (CID image)
   - Title + subtitle

2. **Two-Column Content Area** (nested tables)
   - Outer table with single row, two `<td>` cells (each 50% width)
   - **Left Column** (inner table within left `<td>`)
     - Section title
     - Text paragraph placeholder (component: section.html)
     - Optional: image placeholder (component: image-placeholder.html)
   - **Right Column** (inner table within right `<td>`)
     - Section title
     - Text paragraph placeholder (component: section.html)
     - Optional: image placeholder (component: image-placeholder.html)
   - 20px gap between columns using `<td>` padding or spacer `<td>`

3. **Divider** (component: divider.html)
   - 1px gray line between content rows

4. **Two-Column Content Area** (repeat as needed)
   - Same structure as above for additional rows

5. **Footer** (component: footer.html)
   - Copyright text
   - Unsubscribe link placeholder

## Visual Layout
┌────────────────────────────────────┐
│           HEADER/BANNER            │
│          Title + Subtitle          │
├────────────────────────────────────┤
│                                    │
│  ┌───────────┐  ┌───────────┐     │
│  │  Left Col │  │ Right Col │     │
│  │  [title]  │  │  [title]  │     │
│  │  [text]   │  │  [text]   │     │
│  │  [image]  │  │  [image]  │     │
│  └───────────┘  └───────────┘     │
│                                    │
├─ ─ ─ ─ ─ ─ divider ─ ─ ─ ─ ─ ─ ─┤
│                                    │
│  ┌───────────┐  ┌───────────┐     │
│  │  Left Col │  │ Right Col │     │
│  │  [title]  │  │  [title]  │     │
│  │  [text]   │  │  [text]   │     │
│  └───────────┘  └───────────┘     │
│                                    │
├────────────────────────────────────┤
│             FOOTER                 │
└────────────────────────────────────┘

## Implementation Notes
- Use `<table>` with `border="0" cellpadding="0" cellspacing="0"` for the outer container
- Each column is a `<td>` with `width="50%"` and `valign="top"`
- Place an inner `<table>` inside each `<td>` for column content
- Use a spacer `<td width="20">` between columns for the gap
- All widths use fixed pixel values for Outlook compatibility

## Default Style
- Primary color: #1e40af
- Secondary color: #3b82f6
- Background: #f1f5f9
- Text color: #1e293b
- Column background: #ffffff
- Recommended width: 800px
