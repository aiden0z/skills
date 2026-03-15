# Email Newsletter Best Practices

## 1. Recommended Widths

### 600px — Mobile-First

The most widely compatible width across email clients and devices.

- **Pros:** Renders well on virtually all devices and email clients; no horizontal scrolling on mobile; simplest responsive behavior
- **Cons:** Limited horizontal space for multi-column layouts; can feel narrow on desktop screens; less room for side-by-side content
- **Best for:** Transactional emails, simple announcements, mobile-heavy audiences

### 800px — Balanced

A middle-ground width that provides more layout flexibility while remaining readable.

- **Pros:** Comfortable reading width on both desktop and tablet; supports 2-column layouts without cramping; good balance between information density and readability
- **Cons:** May require media queries for smaller mobile screens; slightly less universal than 600px
- **Best for:** Marketing newsletters, product updates, content digests

### 1200px — Desktop / Info-Dense

A wide layout for data-rich or visually complex newsletters.

- **Pros:** Ample space for multi-column layouts, tables, and dashboards; ideal for information-dense content; maximizes desktop screen real estate
- **Cons:** Requires robust responsive breakpoints; poor experience on mobile without careful adaptation; some email clients may clip or truncate wide content
- **Best for:** Internal reports, data dashboards, desktop-primary audiences

---

## 2. Color Scheme Guidelines

Each palette defines four roles: **Primary**, **Background**, **Text**, and **Accent**.

### Professional Blue

| Role       | Hex       | Usage                        |
|------------|-----------|------------------------------|
| Primary    | `#1A73E8` | Headers, buttons, links      |
| Background | `#F8FAFE` | Email body background        |
| Text       | `#202124` | Body copy                    |
| Accent     | `#FBBC04` | Highlights, badges, CTAs     |

### Emerald Green

| Role       | Hex       | Usage                        |
|------------|-----------|------------------------------|
| Primary    | `#0D9E6E` | Headers, buttons, links      |
| Background | `#F0FDF7` | Email body background        |
| Text       | `#1B1B1B` | Body copy                    |
| Accent     | `#F59E0B` | Highlights, badges, CTAs     |

### Warm Orange

| Role       | Hex       | Usage                        |
|------------|-----------|------------------------------|
| Primary    | `#E8590C` | Headers, buttons, links      |
| Background | `#FFFBF5` | Email body background        |
| Text       | `#1C1917` | Body copy                    |
| Accent     | `#0EA5E9` | Highlights, badges, CTAs     |

### Elegant Purple

| Role       | Hex       | Usage                        |
|------------|-----------|------------------------------|
| Primary    | `#7C3AED` | Headers, buttons, links      |
| Background | `#FAF5FF` | Email body background        |
| Text       | `#1E1B2E` | Body copy                    |
| Accent     | `#EC4899` | Highlights, badges, CTAs     |

### Minimal Gray

| Role       | Hex       | Usage                        |
|------------|-----------|------------------------------|
| Primary    | `#374151` | Headers, buttons, links      |
| Background | `#F9FAFB` | Email body background        |
| Text       | `#111827` | Body copy                    |
| Accent     | `#2563EB` | Highlights, badges, CTAs     |

---

## 3. Typography

### Font Stack (with CJK Support)

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', sans-serif;
```

This stack provides native system fonts on Apple and Windows platforms, with explicit CJK (Chinese, Japanese, Korean) fallbacks for multilingual audiences.

### Heading Sizes

| Element | Size   | Weight  | Line-Height |
|---------|--------|---------|-------------|
| H1      | 28px   | 700     | 1.3         |
| H2      | 22px   | 700     | 1.3         |
| H3      | 18px   | 600     | 1.4         |
| H4      | 16px   | 600     | 1.4         |

### Body Text

| Element        | Size   | Weight  | Line-Height |
|----------------|--------|---------|-------------|
| Body (default) | 16px   | 400     | 1.6         |
| Body (small)   | 14px   | 400     | 1.5         |
| Caption/Footer | 12px   | 400     | 1.5         |

### Recommendations

- Use **16px minimum** for body text to ensure readability on mobile devices.
- Maintain a **line-height of 1.5 to 1.6** for body copy; tighter line-height (1.3) is acceptable for headings.
- Limit heading levels to **H1 through H3** in most newsletters to keep hierarchy clear.
- Avoid custom web fonts in email; system font stacks render faster and are universally supported.

---

## 4. Content Structure

### Visual Hierarchy Principles

- **Single primary CTA per section.** Each content block should drive toward one clear action.
- **Use heading levels consistently.** H1 for the newsletter title, H2 for section titles, H3 for sub-sections.
- **Front-load key information.** Place the most important content and CTA above the fold (roughly the first 300-500px).
- **Limit width of text blocks.** Keep text lines between 50 and 75 characters for comfortable reading.

### Section Breaks

- Use horizontal rules (`<hr>`) or spacer rows (20-30px) to visually separate sections.
- Alternate background colors subtly between sections to create visual rhythm without clutter.
- Add consistent vertical padding (20-40px) above and below each content block.

### Avoiding Excessive Scrolling

- **Aim for 3-5 content sections** in a single newsletter. Beyond that, readers tend to disengage.
- **Summarize and link out.** Provide a brief summary (2-3 sentences) with a "Read more" link rather than embedding full articles.
- **Use a table of contents** at the top for longer newsletters, linking to anchored sections.
- **Target a total email length of 1000-1500px** in rendered height for optimal engagement.

---

## 5. Accessibility

### Alt Text for Images

- Every `<img>` tag must include a descriptive `alt` attribute.
- For decorative images, use `alt=""` (empty alt) so screen readers skip them.
- Keep alt text concise but meaningful: describe what the image conveys, not just what it shows.

### Color Contrast (WCAG AA)

- **Normal text:** Minimum contrast ratio of **4.5:1** against its background.
- **Large text (18px+ or 14px+ bold):** Minimum contrast ratio of **3:1**.
- **UI components and graphical objects:** Minimum contrast ratio of **3:1**.
- Never rely on color alone to convey meaning; pair color cues with text labels or icons.
- All preset color palettes in this guide meet WCAG AA requirements for their text/background combinations.

### Semantic Table Headers

- Use `<th>` elements with `scope="col"` or `scope="row"` for data tables.
- Include a `<caption>` or `aria-label` to describe the table's purpose.
- Avoid using tables purely for layout; when layout tables are necessary, use `role="presentation"` to signal non-semantic use.

### Plain Text Fallback

- Always provide a `text/plain` MIME part alongside the HTML version.
- Structure the plain text version with clear headings (using ALL CAPS or `===` underlines), bullet points (`- `), and explicit URLs.
- Ensure all links from the HTML version are present as full URLs in the plain text fallback.
- Test the plain text version independently to confirm it is coherent and complete.
