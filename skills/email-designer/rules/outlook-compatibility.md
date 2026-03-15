# Outlook Compatibility Rules for HTML Email

> Agent MUST read this file before generating any HTML email content. ALL HTML output MUST comply with these rules.

---

## 1. Document Structure

Every HTML email MUST begin with this exact document structure. Do not omit any element.

### DOCTYPE

```html
<!DOCTYPE html>
```

### HTML tag with VML namespaces

The `<html>` tag MUST declare VML and Office namespaces for Outlook vector graphics support:

```html
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
```

### Meta tags

All of the following meta tags are required in `<head>`:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="format-detection" content="telephone=no">
    <meta name="color-scheme" content="light">
    <meta name="supported-color-schemes" content="light">
    <title>Email Subject Line</title>
```

### OfficeDocumentSettings XML

Immediately after the `<title>`, include this conditional block. It tells Outlook to allow PNG images and to render at 96 DPI (preventing scaling artifacts):

```html
    <!--[if gte mso 9]>
    <xml>
        <o:OfficeDocumentSettings>
            <o:AllowPNG/>
            <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
    </xml>
    <![endif]-->
```

### Base style blocks

Include these style blocks in the `<head>` after the OfficeDocumentSettings:

```html
    <!--[if mso]>
    <style type="text/css">
        body { margin: 0 !important; padding: 0 !important; }
        table {
            border-collapse: collapse !important;
            mso-table-lspace: 0pt !important;
            mso-table-rspace: 0pt !important;
        }
    </style>
    <![endif]-->

    <style type="text/css">
        body, table, td, p, a, li, blockquote {
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }
        table, td {
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }
    </style>
</head>
```

---

## 2. Layout Rules

Outlook 2007-2019 on Windows uses the Microsoft Word rendering engine, which has no support for modern CSS layout. All layout MUST be built with tables.

### Table-only layout

```html
<!-- CORRECT: table layout -->
<table cellpadding="0" cellspacing="0" border="0" width="600" style="width: 600px;">
    <tr>
        <td>Content here</td>
    </tr>
</table>

<!-- WRONG: div layout -- Outlook will ignore width, display, and positioning -->
<div style="width: 600px;">Content here</div>
```

### Required table attributes

Every `<table>` used for layout MUST include these HTML attributes:

```html
<table cellpadding="0" cellspacing="0" border="0">
```

### table-layout: fixed

Use `table-layout: fixed` to prevent Outlook from auto-sizing columns:

```html
<table cellpadding="0" cellspacing="0" border="0" width="1168"
       style="width: 1168px; border-collapse: collapse; table-layout: fixed;">
```

### Table column width rule (CRITICAL)

The sum of all `<td width>` values MUST exactly equal the `<table width>` value.
Column widths in email HTML include padding — `width="200"` with `padding: 0 12px`
means 176px content + 24px padding = 200px total.

**Wrong** (columns + padding exceed table width):
```html
<table width="600">
  <tr>
    <td width="300" style="padding:0 12px;">...</td>  <!-- 300px -->
    <td width="300" style="padding:0 12px;">...</td>  <!-- 300px -->
  </tr>                                                <!-- = 600px ✓ -->
</table>
<!-- Padding is INCLUDED in the 300px, not added on top -->
```

**If your table overflows the container**, reduce column widths so they sum
to exactly the table width. Or use percentage widths (e.g., `width="33%"`).

### Multi-column layouts with nested tables

For side-by-side columns, use nested tables -- never CSS float or inline-block:

```html
<table cellpadding="0" cellspacing="0" border="0" width="600" style="width: 600px;">
    <tr>
        <td width="300" valign="top" style="width: 300px;">
            <!-- Left column table -->
            <table cellpadding="0" cellspacing="0" border="0" width="300" style="width: 300px;">
                <tr><td>Left content</td></tr>
            </table>
        </td>
        <td width="300" valign="top" style="width: 300px;">
            <!-- Right column table -->
            <table cellpadding="0" cellspacing="0" border="0" width="300" style="width: 300px;">
                <tr><td>Right content</td></tr>
            </table>
        </td>
    </tr>
</table>
```

### Table centering

```html
<table width="100%" border="0" cellspacing="0" cellpadding="0" align="center">
    <tr>
        <td align="center" valign="top">
            <table width="1200" align="center" style="width: 1200px; margin: 0 auto;">
                <!-- Content -->
            </table>
        </td>
    </tr>
</table>
```

---

## 3. Style Rules -- Dual Declaration Principle

Outlook's Word engine reads HTML attributes for some properties and CSS for others, but not consistently. To guarantee correct rendering across ALL clients, you MUST declare styles in BOTH places.

### Inline styles only

All styles MUST be inline. Outlook ignores most `<style>` tag CSS and all external stylesheets. The only exception is MSO-conditional `<style>` blocks inside `<!--[if mso]>`.

```html
<!-- CORRECT: inline style -->
<td style="padding: 10px; color: #333333;">Content</td>

<!-- WRONG: class-based styling -- Outlook will ignore it -->
<td class="content">Content</td>
```

### bgcolor + background-color

Always declare background color as BOTH an HTML attribute and a CSS property. Outlook reads `bgcolor`; modern clients read `background-color`. Missing `bgcolor` causes white gaps between nested tables in Outlook.

```html
<!-- CORRECT: dual declaration -->
<td bgcolor="#2563eb" style="background-color: #2563eb;">Content</td>

<!-- WRONG: CSS only -- Outlook may render white background -->
<td style="background-color: #2563eb;">Content</td>
```

Apply `bgcolor` to every nested `<table>` and `<td>` in colored sections:

```html
<td align="center" valign="top" bgcolor="#2563eb" style="background-color: #2563eb;">
    <table width="600" bgcolor="#2563eb" style="width: 600px; background-color: #2563eb;">
        <tr>
            <td bgcolor="#2563eb" style="background-color: #2563eb;">
                Content
            </td>
        </tr>
    </table>
</td>
```

### width and height

Always declare dimensions as BOTH HTML attributes and CSS:

```html
<table width="600" style="width: 600px;">
<td width="300" style="width: 300px;">
<img width="100" height="50" style="width: 100px; height: 50px;">
```

### align and valign

Always declare alignment as BOTH HTML attributes and CSS:

```html
<td align="left" valign="top" style="text-align: left; vertical-align: top;">
```

### mso-line-height-rule: exactly

This MSO-specific property forces Outlook to honor the specified line-height instead of auto-calculating. Apply it to ANY element where precise vertical sizing matters:

```html
<td style="line-height: 24px; mso-line-height-rule: exactly;">Text content</td>
```

### Font stack with CJK support

Use this comprehensive font stack for cross-platform rendering including CJK characters:

```html
<td style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
           'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC',
           'Hiragino Sans GB', 'WenQuanYi Micro Hei', 'Microsoft JhengHei',
           Roboto, 'Helvetica Neue', Arial, sans-serif;">
```

| Font | Platform |
|------|----------|
| `-apple-system`, `BlinkMacSystemFont` | macOS, iOS |
| `Segoe UI` | Windows |
| `PingFang SC` | macOS/iOS Chinese |
| `Microsoft YaHei` | Windows Chinese |
| `Noto Sans CJK SC` | Android/Linux Chinese |
| `Hiragino Sans GB` | macOS Chinese fallback |
| `WenQuanYi Micro Hei` | Linux Chinese |
| `Microsoft JhengHei` | Windows Traditional Chinese |
| `Roboto` | Android |
| `Helvetica Neue`, `Arial` | Universal fallback |

---

## 4. Conditional Comments

Outlook supports IE-style conditional comments. Use them to serve Outlook-specific code or to hide code from Outlook.

### Target Outlook only: `<!--[if mso]>`

Code inside this block is rendered ONLY by Outlook (Word engine). All other clients ignore it.

```html
<!--[if mso]>
<p>This text only appears in Outlook desktop.</p>
<![endif]-->
```

### Target non-Outlook only: `<!--[if !mso]><!-->`

Code inside this block is rendered by ALL clients EXCEPT Outlook. Note the extra `<!-->` -- this is required syntax.

```html
<!--[if !mso]><!-->
<div style="font-size: 0; line-height: 0; height: 1px;">&#8203;</div>
<!--<![endif]-->
```

### Target Outlook version ranges: `<!--[if gte mso 9]>`

Use version-specific conditionals for features like OfficeDocumentSettings. `gte mso 9` means "Outlook 2000 and above" (covers all modern Outlook versions).

```html
<!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
        <o:AllowPNG/>
        <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]-->
```

### Common pattern: VML for Outlook, CSS fallback for others

This is the standard pattern for elements that need different rendering:

```html
<!--[if mso]>
<v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false"
        style="width:600px;height:1px;">
    <v:fill type="solid" color="#e5e7eb"/>
</v:rect>
<![endif]-->
<!--[if !mso]><!-->
<div style="font-size: 0; line-height: 0; height: 1px;">&#8203;</div>
<!--<![endif]-->
```

### MSO-conditional style blocks

Place Outlook-specific CSS overrides inside conditional comments in `<head>`:

```html
<!--[if mso]>
<style type="text/css">
    table {
        border-collapse: collapse !important;
        mso-table-lspace: 0pt !important;
        mso-table-rspace: 0pt !important;
        table-layout: fixed !important;
    }
    td {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
    }
    body, table, td, p, span {
        mso-line-height-rule: exactly !important;
    }
    p.MsoNormal, li.MsoNormal, div.MsoNormal {
        margin: 0 !important;
        margin-bottom: 0 !important;
        mso-para-margin-bottom: 0pt !important;
        mso-margin-bottom-alt: 0pt !important;
        mso-para-margin-top: 0pt !important;
        mso-margin-top-alt: 0pt !important;
        line-height: normal !important;
    }
    td[height] {
        mso-height-rule: exactly !important;
    }
    /* 1px dividers: lock to 0.75pt in Outlook */
    td[height="1"], td[style*="max-height: 1px"] {
        font-size: 0 !important;
        height: 0.75pt !important;
        line-height: 0.75pt !important;
        mso-line-height-alt: 0.75pt !important;
    }
    th[rowspan], td[rowspan], th[colspan], td[colspan] {
        mso-table-layout: auto !important;
    }
</style>
<![endif]-->
```

---

## 5. Spacing Rules

Outlook's Word engine does NOT reliably support CSS `margin`. Never use `margin` for vertical spacing between elements. Instead, use dedicated spacer rows.

### NEVER use margin for spacing

```html
<!-- WRONG: margin is ignored or inconsistent in Outlook -->
<table style="margin-top: 16px; margin-bottom: 16px;">
    ...
</table>
```

### Spacer row pattern

Use a dedicated `<tr>` with a fixed-height `<td>`. The `line-height` MUST match the `height` value. Use `font-size: 1px` (not 0) and `&nbsp;` as content.

```html
<!-- CORRECT: 16px vertical spacer -->
<tr>
    <td height="16"
        style="height: 16px; font-size: 1px; line-height: 16px; mso-line-height-rule: exactly;">&nbsp;</td>
</tr>
```

### Rules for spacer rows

| Element height | font-size | line-height | Content |
|----------------|-----------|-------------|---------|
| 3px | `1px` | `3px` | `&nbsp;` |
| 8px | `1px` | `8px` | `&nbsp;` |
| 16px | `1px` | `16px` | `&nbsp;` |
| 24px | `1px` | `24px` | `&nbsp;` |

**Key constraints:**
- `line-height` MUST equal `height` -- never use `line-height: 0`
- `font-size` MUST be `1px` -- never use `font-size: 0` (it fails to create a valid line box)
- Content MUST be `&nbsp;` -- with correct `line-height` it renders at the exact height
- Always include `mso-line-height-rule: exactly`

### WRONG spacer patterns

```html
<!-- WRONG: line-height: 0 cannot establish a valid line box height -->
<td height="16" style="height: 16px; font-size: 0; line-height: 0;">&#8203;</td>

<!-- WRONG: using padding-bottom instead of a spacer row -- Outlook may expand it -->
<td style="padding-bottom: 16px;">Section title</td>
```

### Full spacer example: section title + blue bar

Use spacer rows to control the gap between a title and a decorative bar, rather than padding:

```html
<table cellpadding="0" cellspacing="0" border="0" width="736" style="width: 736px;">
    <!-- Title row: no padding-bottom -->
    <tr>
        <td style="padding: 0;">
            <span style="font-size: 18px; font-weight: 600; color: #1a1a1a;">Section Title</span>
        </td>
    </tr>
    <!-- 8px spacer row: line-height matches height -->
    <tr>
        <td height="8"
            style="height: 8px; font-size: 1px; line-height: 8px; mso-line-height-rule: exactly;">&nbsp;</td>
    </tr>
    <!-- Blue bar row (see Section 6 for divider pattern) -->
</table>
```

---

## 6. Divider/Border Rules -- CRITICAL

This is the most error-prone area in Outlook email rendering. CSS `border` colors are NOT supported by Outlook's Word engine. All borders render as black regardless of the color you specify.

### NEVER use CSS border for colored lines

```html
<!-- WRONG: CSS border color is IGNORED by Outlook -- renders as BLACK -->
<td style="border-bottom: 1px solid #e5e7eb;">Content</td>
<td style="border-bottom: 3px solid #2563eb;">Section title</td>
```

### Use VML for all colored dividers/borders

Replace every CSS border with a dedicated table row containing a VML rectangle. This is the ONLY reliable method for colored lines in Outlook.

#### 1px gray divider line

```html
<tr>
    <td width="1168" bgcolor="#e5e7eb" height="1"
        style="width: 1168px; height: 1px; max-height: 1px;
               font-size: 1px; line-height: 1px; mso-line-height-rule: exactly;
               background-color: #e5e7eb; padding: 0; margin: 0; border: 0;">
        <!--[if mso]>
        <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false"
                style="width:1168px;height:0.75pt;">
            <v:fill type="solid" color="#e5e7eb"/>
        </v:rect>
        <![endif]-->
        <!--[if !mso]><!-->
        <div style="font-size: 1px; line-height: 1px; height: 1px;">&nbsp;</div>
        <!--<![endif]-->
    </td>
</tr>
```

#### 3px blue accent bar

```html
<tr>
    <td width="736" bgcolor="#2563eb" height="3"
        style="width: 736px; height: 3px; max-height: 3px;
               font-size: 1px; line-height: 3px; mso-line-height-rule: exactly;
               background-color: #2563eb; padding: 0; margin: 0; border: 0;">
        <!--[if mso]>
        <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false"
                style="width:736px;height:3px;">
            <v:fill type="solid" color="#2563eb"/>
        </v:rect>
        <![endif]-->
        <!--[if !mso]><!-->
        <div style="font-size: 1px; line-height: 3px; height: 3px;">&nbsp;</div>
        <!--<![endif]-->
    </td>
</tr>
```

### 1px = 0.75pt in Outlook

Outlook's Word engine uses points (pt), not pixels. 1px equals 0.75pt. For 1px divider lines, use `height: 0.75pt` in the VML style to prevent Outlook from rounding up to 2px:

```html
<!-- In the MSO conditional style block: -->
td[height="1"], td[style*="max-height: 1px"] {
    font-size: 0 !important;
    height: 0.75pt !important;
    line-height: 0.75pt !important;
    mso-line-height-alt: 0.75pt !important;
}
```

### Use `&#8203;` (zero-width space) for thin divider content

For dividers where you need absolute minimal height (1px), use `&#8203;` instead of `&nbsp;`. The `&nbsp;` character triggers Word's paragraph formatting logic, which can add an 18pt bottom margin.

```html
<!-- For 1px dividers, &#8203; prevents paragraph margin insertion -->
<td height="1" style="height: 1px; font-size: 0; line-height: 0; mso-line-height-rule: exactly;">
    <!--[if mso]>
    <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false"
            style="width:1168px;height:0.75pt;">
        <v:fill type="solid" color="#e5e7eb"/>
    </v:rect>
    <![endif]-->
    <!--[if !mso]><!-->
    <div style="font-size: 0; line-height: 0; height: 1px;">&#8203;</div>
    <!--<![endif]-->
</td>
```

### VML divider rules summary

| Property | Required value | Why |
|----------|---------------|-----|
| `bgcolor` HTML attribute | The divider color | Outlook reads HTML attributes |
| `background-color` CSS | Same color | Modern clients read CSS |
| `height` HTML attribute | Divider thickness | Outlook reads HTML attributes |
| `max-height` CSS | Same as height | Prevents expansion |
| `font-size` | `0` or `1px` | Prevents line box from expanding |
| `line-height` | Must match `height` | Controls actual rendered height |
| `mso-line-height-rule` | `exactly` | Forces Outlook to honor line-height |
| `padding`, `margin`, `border` | `0` | Prevents any extra space |
| VML `v:rect` | Inside `<!--[if mso]>` | Renders the colored line in Outlook |
| `&#8203;` or `&nbsp;` | In non-mso fallback | Ensures the div has content to render |

### Full table divider example with VML

```html
<table cellpadding="0" cellspacing="0" border="0" width="1168"
       style="width: 1168px; border-collapse: collapse; table-layout: fixed;">
    <!-- Header row -->
    <tr>
        <th width="200" align="left" valign="middle" bgcolor="#f8fafc"
            style="width: 200px; padding: 8px 12px; background-color: #f8fafc;">
            Column 1
        </th>
        <th width="968" align="left" valign="middle" bgcolor="#f8fafc"
            style="width: 968px; padding: 8px 12px; background-color: #f8fafc;">
            Column 2
        </th>
    </tr>
    <!-- Header divider (VML) -->
    <tr>
        <td colspan="2" width="1168" bgcolor="#cbd5e1" height="1"
            style="width: 1168px; height: 1px; max-height: 1px; font-size: 0; line-height: 0;
                   mso-line-height-rule: exactly; mso-line-height-alt: 0; mso-height-rule: exactly;
                   background-color: #cbd5e1; padding: 0; margin: 0; border: 0;">
            <!--[if mso]>
            <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false"
                    style="width:1168px;height:0.75pt;">
                <v:fill type="solid" color="#cbd5e1"/>
            </v:rect>
            <![endif]-->
            <!--[if !mso]><!-->&nbsp;<!--<![endif]-->
        </td>
    </tr>
    <!-- Data row -->
    <tr>
        <td width="200" align="left" valign="top"
            style="width: 200px; padding: 10px 12px;">Data 1</td>
        <td width="968" align="left" valign="top"
            style="width: 968px; padding: 10px 12px;">Data 2</td>
    </tr>
    <!-- Row divider (VML) -->
    <tr>
        <td colspan="2" width="1168" bgcolor="#e2e8f0" height="1"
            style="width: 1168px; height: 1px; max-height: 1px; font-size: 0; line-height: 0;
                   mso-line-height-rule: exactly; mso-line-height-alt: 0; mso-height-rule: exactly;
                   background-color: #e2e8f0; padding: 0; margin: 0; border: 0;">
            <!--[if mso]>
            <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false"
                    style="width:1168px;height:0.75pt;">
                <v:fill type="solid" color="#e2e8f0"/>
            </v:rect>
            <![endif]-->
            <!--[if !mso]><!-->&nbsp;<!--<![endif]-->
        </td>
    </tr>
</table>
```

---

## 7. Image Rules

### Required attributes

Every `<img>` tag MUST include `width` and `height` HTML attributes, `display: block`, and `border: 0`:

```html
<img src="cid:logo" alt="Logo"
     width="160" height="17"
     style="width: 160px; height: 17px; display: block; border: 0;">
```

### Why each attribute matters

| Attribute | Purpose |
|-----------|---------|
| `width` / `height` HTML attributes | Outlook uses these, ignores CSS dimensions |
| `width` / `height` CSS | Modern clients use these |
| `display: block` | Removes phantom whitespace below images |
| `border: 0` | Removes blue border on linked images |

### Images with auto height

When you need to maintain aspect ratio, set width only and use `height: auto`. Do NOT set the `height` HTML attribute in this case:

```html
<img src="cid:feature" alt="Feature screenshot"
     width="370"
     style="width: 370px; height: auto; display: block; border: 0;">
```

### CID image format

For embedded images in EML files, use the `cid:` URI scheme. The CID value must match the `Content-ID` header of the MIME image part:

```html
<img src="cid:company_logo" alt="Company Logo"
     width="160" height="17"
     style="width: 160px; height: 17px; display: block; border: 0;">
```

The corresponding MIME part must include `X-Attachment-Id` for Outlook Windows:

```
Content-Type: image/png
Content-Transfer-Encoding: base64
Content-ID: <company_logo>
X-Attachment-Id: company_logo
Content-Disposition: inline; filename="company_logo.png"
```

---

## 8. Forbidden Properties

The following CSS properties and techniques are NOT supported by Outlook's Word rendering engine. Using them will cause broken layouts. NEVER use any of these in email HTML.

| Forbidden | Reason | Use instead |
|-----------|--------|-------------|
| `display: flex` / flexbox | Not supported by Word engine | Nested `<table>` layout |
| `display: grid` / CSS Grid | Not supported by Word engine | Nested `<table>` layout |
| `border-radius` | Not supported by Word engine | Square corners only, or VML rounded rect |
| `background-image` (CSS) | Not supported by Word engine | VML fill or solid `bgcolor` |
| `margin` (for spacing) | Inconsistent support | Spacer `<tr>` rows (see Section 5) |
| `float` | Not supported by Word engine | Table cells with `width` |
| `position: absolute/relative` | Not supported by Word engine | Table-based layout |
| `max-width` (on table) | Ignored by Outlook | Fixed `width` attribute |
| External CSS (`<link>`) | Stripped by all email clients | Inline styles only |
| `<style>` in `<body>` | Stripped by many clients | Inline styles; `<style>` in `<head>` only |
| `@media` queries | Ignored by Outlook | Fixed-width design |
| `box-shadow` | Not supported by Word engine | Omit or use VML shadow |
| `opacity` | Not supported by Word engine | Omit |
| `overflow: hidden` | Not supported by Word engine | Omit |
| `<ul>` / `<ol>` lists | Inconsistent indent/spacing in Outlook | Table rows with `•` or numbered text in `<td>` |
| `@font-face` / web fonts | Completely ignored by Outlook | System font stack with CJK fallbacks |
| `<video>` / `<audio>` | Not supported in Outlook/Gmail | Static image with play button linking to URL |
| Animated GIF | Outlook shows first frame only | Ensure first frame conveys the message |
| Table nesting > 8 levels | Can crash Outlook | Simplify layout, flatten nesting |

---

## 9. MSO-Specific CSS Properties

These are proprietary CSS properties recognized only by Outlook's Word rendering engine. Use them inside `<!--[if mso]>` style blocks or as inline styles.

### mso-table-lspace / mso-table-rspace

Removes the default left/right spacing Outlook adds around tables:

```css
table, td {
    mso-table-lspace: 0pt;
    mso-table-rspace: 0pt;
}
```

### mso-line-height-rule

Forces Outlook to use the exact `line-height` value instead of auto-calculating based on font metrics:

```css
td, p, span {
    mso-line-height-rule: exactly;
}
```

### mso-line-height-alt

An Outlook-specific line-height override. Used for pixel-precise divider lines:

```css
td[height="1"] {
    mso-line-height-alt: 0.75pt;
}
```

### mso-hide

Hides elements in Outlook. Used to prevent auto-linking of email addresses and phone numbers:

```css
a[href^="mailto:"] {
    mso-hide: all;
}
```

### mso-height-rule

Forces Outlook to use the exact height value on `<td>` elements:

```css
td[height] {
    mso-height-rule: exactly !important;
}
```

### mso-para-margin-bottom / mso-margin-bottom-alt

Resets Outlook's default paragraph bottom margin (18pt). Critical for preventing spacing bloat:

```css
p.MsoNormal, li.MsoNormal, div.MsoNormal {
    margin: 0 !important;
    margin-bottom: 0 !important;
    mso-para-margin-bottom: 0pt !important;
    mso-margin-bottom-alt: 0pt !important;
    mso-para-margin-top: 0pt !important;
    mso-margin-top-alt: 0pt !important;
    line-height: normal !important;
}
```

### mso-padding-alt

Outlook sometimes ignores CSS `padding` on `<td>` elements. Use `mso-padding-alt`
as a fallback with identical values:

```html
<td style="padding: 24px 16px 8px 16px; mso-padding-alt: 24px 16px 8px 16px;">
```

Always specify both when padding is critical for layout (e.g., section wrappers,
header/footer). For simple table cells, CSS `padding` alone is usually sufficient.

### mso-table-layout

Override table layout for cells using `rowspan` or `colspan`:

```css
th[rowspan], td[rowspan], th[colspan], td[colspan] {
    mso-table-layout: auto !important;
}
```

### mso-line-break-override

Forces word breaking for long URLs and strings in Outlook:

```css
td[style*="word-wrap"] {
    word-break: break-all !important;
    mso-line-break-override: all !important;
}
```

### Complete MSO style block template

Place this inside `<!--[if mso]>` in the `<head>`:

```html
<!--[if mso]>
<style type="text/css">
    table {
        mso-table-lspace: 0pt !important;
        mso-table-rspace: 0pt !important;
        table-layout: fixed !important;
        border-collapse: collapse !important;
        border-spacing: 0 !important;
    }
    td {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
    }
    body, table, td, p, span {
        mso-line-height-rule: exactly !important;
    }
    p.MsoNormal, li.MsoNormal, div.MsoNormal {
        margin: 0 !important;
        margin-bottom: 0 !important;
        mso-para-margin-bottom: 0pt !important;
        mso-margin-bottom-alt: 0pt !important;
        mso-para-margin-top: 0pt !important;
        mso-margin-top-alt: 0pt !important;
        line-height: normal !important;
    }
    td[height] {
        mso-height-rule: exactly !important;
    }
    td[height="1"], td[style*="max-height: 1px"] {
        font-size: 0 !important;
        height: 0.75pt !important;
        line-height: 0.75pt !important;
        mso-line-height-alt: 0.75pt !important;
    }
    td[height="1"] p, td[style*="max-height: 1px"] p {
        margin: 0 !important;
        font-size: 0 !important;
        line-height: 0.75pt !important;
        mso-line-height-alt: 0.75pt !important;
    }
    td[style*="word-wrap"] {
        word-break: break-all !important;
        mso-line-break-override: all !important;
    }
    th[rowspan], td[rowspan], th[colspan], td[colspan] {
        mso-table-layout: auto !important;
    }
    p {
        mso-line-height-rule: exactly !important;
        mso-para-margin-bottom: 0pt !important;
        mso-margin-bottom-alt: 0pt !important;
        mso-para-margin-top: 0pt !important;
        mso-margin-top-alt: 0pt !important;
    }
    h1, h2, h3, h4, h5, h6 {
        mso-line-height-rule: exactly !important;
    }
</style>
<![endif]-->
```

---

## 10. Dark Mode

Outlook.com, Apple Mail, and some other clients support dark mode, which can invert colors unexpectedly. Force light mode to prevent this.

### Required meta tags

Include both of these in `<head>` (already listed in Section 1, repeated here for emphasis):

```html
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
```

### Effect by client

| Client | Behavior |
|--------|----------|
| Outlook.com | Respects `color-scheme: light`, does not auto-invert |
| Gmail | Respects explicit background color declarations |
| Apple Mail | Respects `supported-color-schemes` |
| Outlook desktop (Word engine) | Does not have dark mode -- not affected |

### Do NOT add dark mode CSS

Do not include `@media (prefers-color-scheme: dark)` rules. The email should always render in light mode to maintain consistent appearance across all clients.

---

## Quick Reference: Complete HTML Email Skeleton

```html
<!DOCTYPE html>
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="format-detection" content="telephone=no">
    <meta name="color-scheme" content="light">
    <meta name="supported-color-schemes" content="light">
    <title>Email Title</title>
    <!--[if gte mso 9]>
    <xml>
        <o:OfficeDocumentSettings>
            <o:AllowPNG/>
            <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
    </xml>
    <![endif]-->
    <!--[if mso]>
    <style type="text/css">
        body { margin: 0 !important; padding: 0 !important; }
        table {
            border-collapse: collapse !important;
            mso-table-lspace: 0pt !important;
            mso-table-rspace: 0pt !important;
            table-layout: fixed !important;
        }
        td {
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }
        body, table, td, p, span {
            mso-line-height-rule: exactly !important;
        }
        p.MsoNormal, li.MsoNormal, div.MsoNormal {
            margin: 0 !important;
            mso-para-margin-bottom: 0pt !important;
            mso-margin-bottom-alt: 0pt !important;
        }
        td[height] {
            mso-height-rule: exactly !important;
        }
        td[height="1"], td[style*="max-height: 1px"] {
            font-size: 0 !important;
            height: 0.75pt !important;
            line-height: 0.75pt !important;
            mso-line-height-alt: 0.75pt !important;
        }
    </style>
    <![endif]-->
    <style type="text/css">
        body, table, td, p, a, li, blockquote {
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }
        table, td {
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #ffffff;
             font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
             'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC',
             Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center">
        <tr>
            <td align="center" valign="top">
                <!-- Content table -->
                <table width="600" align="center" cellpadding="0" cellspacing="0" border="0"
                       style="width: 600px; table-layout: fixed;">
                    <tr>
                        <td>
                            <!-- Email content here -->
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
```
