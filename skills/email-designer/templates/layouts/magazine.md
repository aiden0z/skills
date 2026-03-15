# Magazine Layout (杂志布局)

## Applicable Scenarios
Editorial newsletters, content digests, blog roundups, marketing campaigns, storytelling emails, monthly highlights

## Structure
1. **Header** (component: header.html)
   - Full-width banner with brand color background
   - Optional logo placeholder (CID image)
   - Title + subtitle

2. **Hero Image** (component: image-placeholder.html)
   - Full-width featured image spanning the entire content area
   - Optional overlay text or caption below

3. **Lead Paragraph** (component: section.html)
   - Opening paragraph in slightly larger font (18px)
   - Sets the tone for the newsletter content

4. **Divider** (component: divider.html)
   - 1px styled line separating lead from articles

5. **Article Section - Image Left** (nested tables)
   - Outer table with single row, two `<td>` cells
   - Left `<td>` (40% width): image placeholder (component: image-placeholder.html)
   - Right `<td>` (60% width): inner table with article title, excerpt text, and "Read more" link
   - 15px gap between columns using spacer `<td>`

6. **Divider** (component: divider.html)

7. **Article Section - Image Right** (nested tables)
   - Outer table with single row, two `<td>` cells
   - Left `<td>` (60% width): inner table with article title, excerpt text, and "Read more" link
   - Right `<td>` (40% width): image placeholder (component: image-placeholder.html)
   - 15px gap between columns using spacer `<td>`

8. **Divider** (component: divider.html)

9. **Article Section - Image Left** (nested tables)
   - Same structure as step 5, alternating back to image-left

10. **Footer** (component: footer.html)
    - Copyright text
    - Unsubscribe link placeholder

## Visual Layout
┌────────────────────────────────────┐
│           HEADER/BANNER            │
│          Title + Subtitle          │
├────────────────────────────────────┤
│                                    │
│    ┌──────────────────────────┐    │
│    │                          │    │
│    │       HERO IMAGE         │    │
│    │      (full-width)        │    │
│    │                          │    │
│    └──────────────────────────┘    │
│                                    │
│    Lead paragraph text here...     │
│    Slightly larger font size.      │
│                                    │
├─ ─ ─ ─ ─ ─ divider ─ ─ ─ ─ ─ ─ ─┤
│                                    │
│  ┌─────────┐  ┌──────────────┐    │
│  │  IMAGE  │  │ Article #1   │    │
│  │         │  │ [title]      │    │
│  │         │  │ [excerpt]    │    │
│  │         │  │ Read more >  │    │
│  └─────────┘  └──────────────┘    │
│                                    │
├─ ─ ─ ─ ─ ─ divider ─ ─ ─ ─ ─ ─ ─┤
│                                    │
│  ┌──────────────┐  ┌─────────┐    │
│  │ Article #2   │  │  IMAGE  │    │
│  │ [title]      │  │         │    │
│  │ [excerpt]    │  │         │    │
│  │ Read more >  │  │         │    │
│  └──────────────┘  └─────────┘    │
│                                    │
├─ ─ ─ ─ ─ ─ divider ─ ─ ─ ─ ─ ─ ─┤
│                                    │
│  ┌─────────┐  ┌──────────────┐    │
│  │  IMAGE  │  │ Article #3   │    │
│  │         │  │ [title]      │    │
│  │         │  │ [excerpt]    │    │
│  │         │  │ Read more >  │    │
│  └─────────┘  └──────────────┘    │
│                                    │
├────────────────────────────────────┤
│             FOOTER                 │
└────────────────────────────────────┘

## Implementation Notes
- Hero image uses a single-cell table with `width="100%"`
- Article sections use `<table>` with `border="0" cellpadding="0" cellspacing="0"`
- Image column uses fixed width (e.g., `width="300"` for 40%) and text column fills remaining space
- Use `valign="top"` on all `<td>` elements for proper alignment
- "Read more" links styled inline, not as CSS-dependent buttons
- Alternate image left/right by swapping `<td>` order in each article row

## Default Style
- Primary color: #7c3aed
- Secondary color: #a78bfa
- Background: #faf5ff
- Text color: #1e1b4b
- Accent color: #c084fc
- Lead paragraph font size: 18px
- Article title font size: 16px
- Recommended width: 800px
