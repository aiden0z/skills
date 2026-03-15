# Announcement Layout (公告布局)

## Applicable Scenarios
Product launches, service outages, policy changes, milestone celebrations, important notices, single-message communications

## Structure
1. **Header - Compact** (component: header.html)
   - Minimal height header with brand color background
   - Optional logo placeholder (CID image)
   - Short title only, no subtitle

2. **Centered Announcement Text** (component: section.html)
   - Large centered heading (28-32px font)
   - Supporting body text centered below (16px font)
   - Generous vertical padding (40px top and bottom)
   - All text uses `text-align: center`

3. **CTA Button** (table-based, optional)
   - Centered table with single cell
   - `<td>` styled with background-color, padding, and border-radius via `bgcolor` attribute
   - `<a>` tag inside with inline color and text-decoration styles
   - NOT CSS-only: uses `bgcolor` on `<td>` for Outlook compatibility
   - Button text placeholder (e.g., "Learn More", "Get Started")

4. **Footer** (component: footer.html)
   - Copyright text
   - Unsubscribe link placeholder

## Visual Layout
┌──────────────────────────┐
│   HEADER (compact)       │
├──────────────────────────┤
│                          │
│                          │
│                          │
│     ANNOUNCEMENT         │
│      HEADLINE            │
│    (large, centered)     │
│                          │
│   Supporting text goes   │
│   here, also centered.   │
│                          │
│                          │
│     ┌──────────────┐     │
│     │  CTA BUTTON  │     │
│     └──────────────┘     │
│                          │
│                          │
├──────────────────────────┤
│         FOOTER           │
└──────────────────────────┘

## Implementation Notes
- Header should use reduced padding (15px vs typical 30px) for compact appearance
- Announcement text wrapped in a `<table>` with a single centered `<td>`
- Use `style="font-size:28px; font-weight:bold; text-align:center;"` on heading
- CTA button built as a nested table:
  ```
  <table border="0" cellpadding="0" cellspacing="0" align="center">
    <tr>
      <td bgcolor="#374151" style="padding:14px 30px; border-radius:6px;">
        <a href="{{CTA_URL}}" style="color:#ffffff; text-decoration:none; font-weight:bold; font-size:16px;">
          {{CTA_TEXT}}
        </a>
      </td>
    </tr>
  </table>
  ```
- Keep content minimal; this layout is designed for a single focused message
- Generous whitespace reinforces the importance of the announcement

## Default Style
- Primary color: #374151
- Secondary color: #6b7280
- Background: #f9fafb
- Text color: #111827
- Button background: #374151
- Button text color: #ffffff
- Heading font size: 28px
- Body font size: 16px
- Recommended width: 600px
