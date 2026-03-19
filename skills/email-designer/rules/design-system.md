# Email Design System — Universal Foundation

> Read this file to produce modern, professional-looking emails.
> These patterns work for ANY email type: newsletters, announcements,
> invitations, reports, digests, notifications.

## 1. Color System

### Text Colors (5-Level Slate Grayscale)

Never use pure black (#000). Use this slate grayscale to create visual depth:

| Level | Hex | When to use |
|-------|-----|-------------|
| **Primary** | `#0f172a` | Main titles (H1/H2), table headers |
| **Secondary** | `#334155` | Subtitles (H3/H4), emphasized text |
| **Body** | `#475569` | Body text, table data, paragraphs |
| **Caption** | `#64748b` | Captions, notes, dates, metadata |
| **Muted** | `#94a3b8` | Labels, secondary info, disabled text |

### Background Colors

Layer backgrounds from light to white to create visual grouping without borders:

| Hex | When to use |
|-----|-------------|
| `#f5f5f5` | Page outer background (email client body) |
| `#f8fafc` | Card backgrounds, grouped sections, table headers |
| `#ffffff` | Main content area, active/primary content |
| `#f1f5f9` | Subtle emphasis areas, secondary sections |

### Border/Divider Colors

| Hex | When to use |
|-----|-------------|
| `#e2e8f0` | Row dividers, section separators (standard) |
| `#cbd5e1` | Heavier separators (e.g., table header bottom) |

### Link Colors

| Hex | State |
|-----|-------|
| `#1d4ed8` | Default link |
| `#1e40af` | Outlook fallback |
| `#1e3a8a` | Hover state |

## 2. Typography

### Font Stack

```
-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei',
'Noto Sans CJK SC', 'Hiragino Sans GB', Roboto, 'Helvetica Neue', Arial, sans-serif
```

### Type Scale

| Element | Size | Weight | Line Height | Color |
|---------|------|--------|-------------|-------|
| H1 Main Title | 28px | 600 | 36px | `#0f172a` |
| H2 Section Title | 20px | 600 | 28px | Brand accent |
| H3 Subsection | 16px | 600 | 24px | `#334155` |
| H4 Small Title | 14px | 600 | 20px | `#334155` |
| Body Text | 14-16px | 400 | 24px | `#475569` |
| Table Header | 13px | 600 | 18px | `#334155` |
| Table Data | 12-13px | 400 | 18px | `#475569` |
| Caption | 11-12px | 400 | 16px | `#64748b` |

### Weight Rules

Only use **400** (regular) and **600** (semi-bold). Avoid 300, 500, 700 —
they render inconsistently across email clients, especially Outlook.

## 3. Spacing System

**Base unit: 4px.** All spacing values should be multiples of 4.

| Token | Value | When to use |
|-------|-------|-------------|
| `xs` | 4px | Tight gaps between related elements |
| `sm` | 8px | Internal spacing, small gaps |
| `md` | 12px | Table cell padding, subsection spacing |
| `lg` | 16px | Standard padding, content margins |
| `xl` | 20px | Larger gaps inside sections |
| `2xl` | 24px | Between sections, after dividers |
| `3xl` | 32px | Major section top padding |
| `4xl` | 40px | Large visual breaks |

### Standard Paddings

| Element | Padding |
|---------|---------|
| Content area sides | `16px` left/right |
| Table header cell | `8px 12px` |
| Table data cell | `10px 12px` |
| Section title area | `24px 16px 8px 16px` |
| Card / highlight block | `12px 16px` |
| Header / Footer | `16px 24px` |

## 4. Universal Component Patterns

### Section Title

Brand-colored title with a subtle underline to separate sections:

```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
  <tr>
    <td style="padding:24px 16px 8px 16px;">
      <h2 style="margin:0;padding:0;font-size:20px;font-weight:600;
                 color:{{accent_color}};line-height:28px;mso-line-height-rule:exactly;
                 font-family:[FONT_STACK];">Section Title</h2>
    </td>
  </tr>
  <tr>
    <td style="padding:0 16px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          <td height="2" bgcolor="#e2e8f0"
              style="background-color:#e2e8f0;height:2px;font-size:0;line-height:0;
                     mso-line-height-rule:exactly;">&#8203;</td>
        </tr>
      </table>
    </td>
  </tr>
</table>
```

### Gradient Header/Footer

A gradient creates a polished bookend effect. Outlook ignores `linear-gradient`
but renders the solid `bgcolor` fallback cleanly.

```html
<!-- Header -->
<td bgcolor="{{accent_color}}" style="background-color:{{accent_color}};
    background:linear-gradient(to right, {{accent_color}}, {{accent_dark}});
    padding:16px 24px;">

<!-- Footer (reverse direction for visual symmetry) -->
<td bgcolor="{{accent_dark}}" style="background-color:{{accent_dark}};
    background:linear-gradient(to right, {{accent_dark}}, {{accent_color}});
    padding:16px 24px;">
```

### Navigation Bar

For multi-section emails, add anchor links below the header:

```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
       bgcolor="#f8fafc" style="background-color:#f8fafc;">
  <tr>
    <td align="center" style="padding:12px 20px;">
      <a href="#section1" style="color:#1d4ed8;font-size:14px;font-weight:600;
         text-decoration:none;padding:0 16px;">Section 1</a>
      <span style="color:#e2e8f0;">|</span>
      <a href="#section2" style="color:#1d4ed8;font-size:14px;font-weight:600;
         text-decoration:none;padding:0 16px;">Section 2</a>
    </td>
  </tr>
</table>
```

## 5. Table Design

### Type 1: Standard Table (Gray Header) — most common

- Header: bgcolor `#f8fafc`, 13px/600/`#334155`, padding `8px 12px`
- Data rows: bgcolor `#ffffff`, 12-13px/400/`#475569`, padding `10px 12px`
- Row dividers: 1px `#e2e8f0` (VML, not CSS border)
- **No vertical borders** — modern, clean look
- Summary row: bgcolor `#f8fafc`, 12px/600/`#334155`

### Type 2: Minimal Table (Header border only)

- Header: bgcolor `#ffffff`, 13px/600, bottom border 1px `#cbd5e1`
- Data: same as above but lighter feel
- Good for inline/secondary data

### Column Width Calculation (CRITICAL)

Table column widths MUST include padding. In email HTML, `<td width="X">` defines
the **total** cell width including padding. If you set `width="200"` and
`padding: 0 12px`, the content area is only 176px.

**Formula:** Sum of all `<td width>` values MUST equal the `<table width>` value.
Padding is already included in the `width` attribute.

**Example** for an 800px container with 16px side padding (768px content):

```
Table width: 768px
Columns:  #(40) + Name(260) + Owner(120) + Status(160) + Progress(188) = 768px
                                                                          ✓ exact match
```

Each `<td>` uses `width="N"` where N already accounts for padding.
The `padding` CSS controls where text sits within that fixed width.

**Common mistake:** Setting column widths that sum to the table width, then
ALSO adding padding — this causes the table to exceed the container width.
The fix is either: (a) reduce column widths to account for padding, or
(b) use percentage widths that always stay within bounds.

### Column Alignment

- Text → `text-align: left`
- Numbers → `text-align: center` or `right`
- Sequence (#) → `center`, narrow (30-40px)

## 6. Image Integration

| Type | Width formula |
|------|---------------|
| Full-width banner | `= container width` |
| Content image | `= container - 32px` (padding) |
| Multi-card images | `= (container - gaps) / N` |

Always set: `display:block; border:0; width:Npx; height:auto;`

## 7. Mobile Responsiveness

Outlook ignores `@media` queries, but Gmail, Apple Mail, and web clients support them.
Use progressive enhancement: build for Outlook (fixed width), then add mobile fallbacks
inside `<!--[if !mso]><!-->` blocks.

```html
<!--[if !mso]><!-->
<style type="text/css">
    @media only screen and (max-width: 620px) {
        .email-container { width: 100% !important; max-width: 100% !important; }
        .mobile-full { width: 100% !important; display: block !important; }
        .mobile-hide { display: none !important; }
        .mobile-padding { padding: 12px !important; }
    }
</style>
<!--<![endif]-->
```

Add `class="email-container"` to the main table and `class="mobile-full"` to
columns that should stack on mobile. Outlook ignores these classes entirely
(they're inside `[if !mso]`), so the fixed-width layout is preserved.

## 8. Additional Patterns

### Callout / Accent Bar

A highlighted block with a colored left border and tinted background. Use for
summaries, key notes, important remarks. See `templates/components/callout.html`.

The Outlook-safe version uses a narrow colored `<td>` instead of `border-left`
(CSS border colors render as black in Outlook).

```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
  <tr>
    <td width="4" bgcolor="#2563eb" style="width:4px;background-color:#2563eb;">&nbsp;</td>
    <td bgcolor="#eff6ff" style="background-color:#eff6ff;padding:12px 16px;">
      <p style="...">Callout text here</p>
    </td>
  </tr>
</table>
```

### Monospace for IDs and Code

When displaying IDs, codes, or technical values in tables, use monospace font:

```html
<td style="font-family:monospace;font-size:12px;color:#475569;">BUG-20261234</td>
```

### Summary / Total Row in Tables

The last row of a data table (summary or total) should be visually distinct:
- Background: `#f8fafc` (same as header)
- Font weight: 600 (bold)
- Top divider: 1px `#cbd5e1` (heavier than row dividers)

### Image Container Reset

When placing images directly in `<td>`, reset the container to prevent extra
spacing around the image:

```html
<td style="padding:0;line-height:0;font-size:0;">
    <img src="cid:image" width="600" style="display:block;width:600px;height:auto;border:0;" />
</td>
```

The `line-height:0;font-size:0;` on the parent prevents Outlook from adding
invisible spacing below the image.

## 9. Design Principles

1. **Slate over black** — never `#000`. The 5-level grayscale creates depth
   without harshness.

2. **Backgrounds over borders** — group elements with `#f8fafc` background
   instead of drawing boxes around them. Cleaner, more modern.

3. **One accent color** — pick one brand color for titles, links, header/footer.
   Multiple accents create visual noise.

4. **Breathing room** — 24-32px between sections. Dense emails get skimmed,
   spaced emails get read.

5. **Two weights only** — 400 and 600. Size and color create hierarchy,
   not a zoo of font weights.

6. **Borderless tables** — no vertical lines, subtle horizontal `#e2e8f0`
   dividers, gray header row. Clean and modern.

### Accessibility
- All layout tables: `role="presentation"` (screen readers skip layout structure)
- Data tables: `<th scope="col">` / `<th scope="row">` (screen readers announce headers)
- `<html lang="xx">` — always set, matching email language
- Touch targets: buttons ≥ 44×44px
- Color: never rely on color alone; always pair with text labels
- Alt text: required on all `<img>` (use `alt=""` only for decorative images)
