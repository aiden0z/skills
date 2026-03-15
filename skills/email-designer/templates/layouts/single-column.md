# Single Column Layout (单栏布局)

## Applicable Scenarios
Product updates, company announcements, weekly digests, event invitations

## Structure
1. **Header** (component: header.html)
   - Full-width banner with brand color background
   - Optional logo placeholder (CID image)
   - Title + subtitle

2. **Content Blocks** (repeat 1-N times, component: section.html)
   - Section title
   - Text paragraph placeholder
   - Optional: image placeholder (component: image-placeholder.html)
   - Optional: table placeholder (component: table.html)

3. **Divider** (component: divider.html)
   - 1px gray line between content blocks

4. **Footer** (component: footer.html)
   - Copyright text
   - Unsubscribe link placeholder

## Visual Layout
┌──────────────────────────┐
│       HEADER/BANNER      │
│      Title + Subtitle    │
├──────────────────────────┤
│     Content Block 1      │
│   [text placeholder]     │
│   [image placeholder]    │
├─ ─ ─ ─ divider ─ ─ ─ ─ ─┤
│     Content Block 2      │
│   [text placeholder]     │
│   [table placeholder]    │
├──────────────────────────┤
│         FOOTER           │
└──────────────────────────┘

## Default Style
- Primary color: #2563eb
- Background: #f8fafc
- Text color: #1e293b
- Recommended width: 600px
