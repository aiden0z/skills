# Brand Color Extraction

## When User Provides a Logo/Brand Image

If the user provides a logo image or screenshot for color reference,
the Agent should:

1. Use its multimodal vision capability to analyze the image
2. Identify the dominant colors (primary, secondary, accent)
3. Propose a color scheme based on the extracted colors:
   - **Primary**: The most prominent brand color
   - **Secondary**: A complementary or supporting color
   - **Background**: A light tint of the primary (5-10% opacity equivalent)
   - **Text**: Dark neutral that pairs well with the primary
   - **Accent**: For CTAs, links, highlights

## Color Scheme Output Format

Present to user as:
```
Primary:    #XXXXXX  (品牌主色 / Brand primary)
Secondary:  #XXXXXX  (辅助色 / Supporting color)
Background: #XXXXXX  (背景色 / Background)
Text:       #XXXXXX  (正文色 / Body text)
Accent:     #XXXXXX  (强调色 / Accent/CTA)
```

## Preset Palettes (when no image provided)

| Name | Primary | Background | Text | Accent |
|------|---------|------------|------|--------|
| Professional Blue | #2563eb | #f8fafc | #1e293b | #1d4ed8 |
| Emerald Green | #059669 | #f0fdf4 | #1e293b | #047857 |
| Warm Orange | #ea580c | #fff7ed | #1c1917 | #c2410c |
| Elegant Purple | #7c3aed | #faf5ff | #1e1b4b | #6d28d9 |
| Minimal Gray | #374151 | #f9fafb | #111827 | #1f2937 |

## Agent Note

Color extraction relies on the Agent's vision capability (reading image files via the Read tool).
No Python dependency needed — the Agent analyzes the image directly and identifies colors.
If the Agent cannot read the image, ask the user to describe their brand colors or pick a preset palette.
