# Audit Overview Image

Use this when creating `submit/audit-overview.png`.

## Contents

- Purpose
- Canvas
- Visual Style
- Typography
- Color System
- Spacing & Elevation
- Iconography
- Editorial Mode (optional)
- Generation Mechanism
- Source Data Contract
- Content Structure
- Wording
- Charts
- Metadata
- Quality Gate
- Visual Anti-Patterns

## Purpose

The image is a compact entry point for the audit package. It should help readers understand scope, Bug distribution, core risk families, architecture signals, file structure, and version evidence before opening the Markdown files.

If your output looks materially less designed than a polished editorial dashboard, re-read this document — you are likely missing one of: hero card differentiation, mono numerics, hue-separated P1-P4 chips, or the ≥12px type scale.

## Canvas

- Light neutral background only: pure white `#FFFFFF` or warm/cool neutral such as `#FAFAFA`, `#F8F9FB`, `#F7F8FA`. No dot grids, line grids, gradients, or decorative backgrounds.
- Default to a single fixed `16:10` artboard, preferably `1600x1000`, for repository audit packages.
- Use `16:9` (`1600x900` or `1920x1080`) when the image is primarily for PPTX, slide decks, or widescreen presentation export.
- Use `1920x1200` only as a high-resolution `16:10` source or when the target review surface needs it; keep larger source artboards under `work/tmp/` unless the user explicitly wants the high-resolution PNG as the submitted image.
- The final submitted PNG should use the same ratio and practical size as the target review surface. If `1600x1000` is the preview that reads best, export `submit/audit-overview.png` at `1600x1000`; keep larger source artboards only in `work/tmp/`.
- Avoid long vertical posters for audit overviews. They shrink in chat, browser previews, slides, and review tools, making dense text appear compressed even when the DOM does not overflow.
- If content does not fit the chosen ratio, reduce or summarize content rather than changing the overview into a long poster.
- Keep safe margins at least `64px`.
- Use a clear grid. Avoid overlapping cards, clipped labels, dense legends, and decorative backgrounds.
- Avoid dark theme and neon gradients. Subtle shadows for elevation are encouraged; heavy/glowy shadows are not.
- If the HTML page is also opened in a browser, wrap the artboard in a viewport-fit stage and scale the stage to the current viewport. A valid browser preview must show the whole artboard, not only the top-left part of a fixed canvas.

## Visual Style

The target aesthetic is **modern product dashboard**, in the family of Linear, Vercel, Stripe, shadcn/ui, Geist, Notion. The result must read as a 2024+ deliverable, not a 2014 Bootstrap admin panel.

Reference anchors when in doubt:

- ✅ Linear issue boards, Vercel project dashboards, Stripe overview pages, shadcn/ui card layouts, Notion data views.
- ❌ Bootstrap 3/4 admin templates, AntD Pro default cards, Material Design v1 raised cards, dot-grid "engineering blueprint" backgrounds.

Use elevation, type weight contrast, restrained color, and icons to create hierarchy — not bigger fonts, brighter colors, or more borders.

## Typography

- Font family: `Inter`, `Geist`, `IBM Plex Sans` for Latin; pair with `PingFang SC`, `Noto Sans CJK SC`, `Source Han Sans` for Chinese. Always include CJK fallbacks.
- **Numeric font (mandatory)**: pair the UI font with a monospace for every metric — `JetBrains Mono`, `IBM Plex Mono`, or `Geist Mono`. KPI numbers (hero count, P1-P4 split, bar values, impact counts), version numbers, IDs, and code snippets must render in the mono family. Body and labels stay in the UI font. This separation is the single most important typographic move for an "editorial / data" feel — it stops numbers from looking like body copy.
- Type scale (px, choose from this set, do not invent intermediate sizes): `12, 13, 14, 16, 20, 24, 32, 40, 48, 64, 88`.
- Weight scale (use only these): `400` body, `500` label/metadata, `600` card title, `700` section title, `800` hero number.
- Title-to-body weight contrast must be at least one full step (e.g. `600` vs `400`). Do not render an entire card in a single weight.
- Use `tabular-nums` (`font-variant-numeric: tabular-nums;`) on every count and metric so numbers align vertically. Mono fonts give this for free; if you must use a proportional font for a number, set `tabular-nums` explicitly.
- Audit your own demo before shipping: every text rule must land on the documented type scale. Check for `11px`, `12.5px`, `15px`, etc. — they are the most common "I just needed a bit more space" violations and immediately downgrade the result.
- Line-height: `1.1`-`1.2` for hero numbers and titles, `1.4`-`1.5` for body and labels.
- Letter-spacing: `-0.01em` to `-0.02em` on display sizes (≥32px); `0` on body; `0.04em` uppercase only on small `12px` eyebrows/labels.
- Do not shrink fonts below `12px` to fit content. Remove content instead.

## Color System

Restrained, low-saturation, semantic. No raw high-saturation primaries.

- **Neutrals (text & surface)** — choose one neutral ramp and use it consistently. Two equally valid options:
  - **Cool ramp (default product dashboard)**: text `#0F172A` / `#475569` / `#64748B`, border `#E2E8F0`, raised `#FFFFFF`, base `#FAFAFA` / `#F8F9FB`.
  - **Warm editorial ramp (recommended for handoff/hero overview)**: text `#0A0A0A` / `#525252` / `#A3A3A3`, hairline border `#EAE8E1`, raised `#FFFFFF`, base `#FAFAF7` / `#F5F3EC`. Reads like premium newsprint instead of generic SaaS card.
  - Pick one per image. Do not mix warm and cool neutrals in the same artboard.
- **Brand accent** — exactly one. Use sparingly for the hero number, primary CTA, and one chart fill.
  - Recommended: `#4F46E5` → `#6366F1` (indigo-violet, gradient OK for hero number/title only). Also valid: `#2563EB` (blue-600), `#0EA5E9` (sky-600). Avoid plain corporate blue if you want the result to read as "designed".
- **Semantic priority chips (P1-P4)** — must be **hue-separated**, not just value-separated. Two dark warm colors (e.g. red-800 vs orange-900) look identical in a small chip. Use this set:
  - P1 / critical: bg `#FEE2E2`, text `#DC2626`, border `#FCA5A5` — **pure red**
  - P2 / high: bg `#FEF3C7`, text `#D97706`, border `#FCD34D` — **amber/yellow-orange**
  - P3 / medium: bg `#DBEAFE`, text `#2563EB`, border `#93C5FD` — **blue**
  - P4 / low / info: bg `#F1F5F9`, text `#64748B`, border `#E2E8F0` — **neutral gray**
  - Success / resolved: bg `#F0FDF4`, text `#15803D`, border `#BBF7D0`
  - Rationale: red→amber→blue→gray is a "hot to cool" severity gradient, and red-vs-blue is the strongest accessible contrast pair. The same `--p{n}-fg` color must drive the chip text, the matching split-KPI number, and any small color dot before the label — so a reader's eye links them across cards.
- Use **at most 4 hues** in one image: 1 neutral ramp + 1 brand accent + up to 2 semantic chip colors visible at once.
- Bar/chart fills use the brand accent at full strength for the focal series and a `#E2E8F0` neutral track behind. Secondary series may use a desaturated accent (`#93C5FD`) — never a different hue.

## Spacing & Elevation

- Spacing scale (px, do not invent intermediate values): `4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80`.
- Card padding: `20px` to `24px` for normal cards, `28px` to `32px` for hero/metric cards. Inner gap between elements inside a card: `12px` or `16px`.
- Card radius: `12px` for cards, `8px` for chips and small inputs, `6px` for tags. Use `rounded-2xl` aesthetic, not `rounded-sm` admin boxes.
- Borders: prefer `1px solid` neutral border (`#E5E7EB`) **or** elevation, not both at once. Hero/important cards use elevation; supporting cards use border.
- Elevation tokens (use these, do not invent custom shadows):
  - `shadow-xs`: `0 1px 2px rgba(15, 23, 42, 0.04)`
  - `shadow-sm`: `0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)`
  - `shadow-md`: `0 4px 12px rgba(15, 23, 42, 0.06), 0 2px 4px rgba(15, 23, 42, 0.04)` (reserved for hero KPI card only)
- Never stack heavy `0 10px 30px` drop shadows or apply shadows to every card uniformly — that flattens hierarchy.

### Hero Card Differentiation (mandatory)

The hero/total-Bug card must be visibly distinct — not just larger. If you cannot tell which card is "the one to look at first" from a 200px thumbnail, the hierarchy has failed.

Apply all three to the hero card, none to supporting cards:

1. **Top accent strip**: `3px` linear-gradient bar across the top edge using the brand accent (e.g. `linear-gradient(90deg, #4F46E5 0%, #6366F1 100%)`), implemented via `::before`.
2. **Layered shadow** (not a single soft drop shadow): combine an accent-tinted glow + neutral lift + inset highlight. Example for indigo-violet brand:
   ```
   0 18px 48px -16px rgba(79, 70, 229, 0.15),
   0 8px 24px -8px rgba(10, 10, 10, 0.08),
   inset 0 1px 0 rgba(255, 255, 255, 0.6)
   ```
3. **Accent-tinted hairline border**: `1px solid rgba(<accent>, 0.18)` instead of the standard neutral border.

Supporting cards stay flat: `1px solid <hairline>` only, no shadow, no top strip. The contrast is what makes the hero feel like a hero.

The hero number itself uses the mono font at `64-88px` with a **vertical** ink gradient (`linear-gradient(180deg, #0A0A0A 0%, #404040 100%)` clipped to text). Do not use a colored gradient on the number — keep the brand accent for the title/strip only, otherwise everything competes.

## Iconography

- Every card title and every category/risk row should carry a `16-20px` icon next to it. Icons are mandatory for scannability — they are the fastest way readers locate data-integrity vs security vs recovery.
- Use one icon set throughout the image. Recommended: Lucide, Phosphor (regular weight), Heroicons (outline). Never mix sets.
- Icon stroke weight: `1.5px` to `2px`. Icon color: same as the section's accent color, or text-secondary for neutral labels.
- For priority chips (P1/P2/...), pair the chip with an icon: `AlertOctagon` for P1, `AlertTriangle` for P2, `Info` for P3, `Circle` for P4.
- Do not substitute emoji for icons in the submitted image.

## Editorial Mode (optional, recommended for hero/handoff overviews)

Apply these on top of the base style when the audience is leadership / external review and the image will be embedded in slides, emails, or reports:

- **Warm paper background**: switch to the warm editorial neutral ramp (see Color System). Add a soft dual radial gradient at very low opacity to break the flat fill:
  ```
  radial-gradient(circle at 88% 6%, rgba(79, 70, 229, 0.04), transparent 50%),
  radial-gradient(circle at 4% 96%, rgba(10, 10, 10, 0.03), transparent 50%)
  ```
- **Paper noise texture** (optional, very subtle): an inline SVG `feTurbulence` filter at `opacity: 0.5` with `mix-blend-mode: multiply`. Stops the canvas from looking digital-perfect. Keep noise under 5% effective alpha — anything stronger reads as JPEG artifact.
- **Live anchor pulse**: a single `6px` round dot in the eyebrow strip, animated with `@keyframes pulse` (scale `1→2.6`, opacity `0.5→0`, 2.4s ease-out infinite). Conveys "this is a live snapshot". Use the brand accent color. Exactly **one** pulse per image — multiple pulses look like a broken status page.
- **Dotted reading guide**: when the footer shows numbered steps (01 → 02 → 03), draw a dotted connector behind the step row using `repeating-linear-gradient(90deg, var(--ink-5) 0 4px, transparent 4px 9px)` on a `::before` at 50% height. Each step gets `position: relative; z-index: 1; background: <raised>` so the connector visually breaks at each step. The connector turns three loose chips into a clear path.
- **Anchor badge**: a solid black `border-radius: 999px` pill with white text in the eyebrow (e.g. "OPEN AUDIT · LIVE"). One per image, in the top-left, anchors the eye before it scans down. Do not use this style anywhere else in the image.

These are stylistic upgrades, not requirements. A clean base-style image is preferable to a botched editorial one. Do not enable editorial mode if you cannot also satisfy the base requirements (correct counts, no overflow, hierarchy).

## Generation Mechanism

Recommended order:

1. HTML/CSS layout rendered to PNG through a browser screenshot.
2. Infographic or visual-design skills to plan content hierarchy, grid, and style, then render with HTML/CSS or another deterministic layout.
3. Native image generation when it can produce a cleaner visual result for the current package.

HTML/CSS is preferred for dense text, exact numbers, tables, and file structure because it is easier to verify and align with indexes. Native image generation is allowed; apply the same quality gate and regenerate if text, numbers, spacing, or metadata are wrong.

If native image generation is used:

- Keep source data in the prompt explicit: counts, labels, metadata, and file guide.
- Re-read the final image for Chinese text, numbers, overlap, clipping, and footer metadata.
- Do not rely on the image as the source of truth; README and generated indexes remain authoritative.
- Use another pass or switch to HTML/CSS if the image cannot keep text and numbers accurate.

If HTML/CSS is used:

- Store `audit-overview.html`, CSS, screenshots, and drafts under `work/tmp/` or `work/drafts/`.
- Use `indexes/findings.generated.json`, `quality/repository-versions.md`, README, and knowledge summaries as data sources.
- Screenshot only the final artboard/canvas into `submit/audit-overview.png`; do not screenshot the full scrolling page or the browser viewport unless it is only for preview QA.
- Use the same ratio for final artboard, screenshot viewport, and submitted PNG. Do not export a larger source canvas and assume downstream previews will scale it correctly.
- For browser preview, add a viewport-fit wrapper rather than relying on scroll. Example pattern: `.stage { width: calc(ARTBOARD_W * var(--scale)); height: calc(ARTBOARD_H * var(--scale)); }`, `.artboard { transform: scale(var(--scale)); transform-origin: top left; }`, and set `--scale` to `min(1, innerWidth / ARTBOARD_W, innerHeight / ARTBOARD_H)`.
- Keep a preview screenshot from a constrained viewport such as `1600x1000` or `1440x900` under `work/tmp/` when practical. The preview must show the entire artboard without clipped bottom content.

## Source Data Contract

The image must be generated from a small source snapshot, not from memory.

- For a final submitted image, create `work/tmp/audit-overview-data.md` or `work/tmp/audit-overview-data.json` before rendering.
- Non-final draft images may skip the source snapshot only if no generated PNG enters `submit/`.
- Include only facts that can be traced to `indexes/findings.generated.json`, README, `quality/repository-versions.md`, and submitted knowledge docs.
- Every number in the image must have a source: total Bugs, P1/P2/P3/P4 counts, confidence counts, category counts, top repos/modules, and version-evidence coverage.
- Risk labels and architecture signals must use the same names as README or `knowledge/architecture-design-review.md`.
- Do not invent percentages, trends, "top" rankings, or package status text. If the source does not contain a value, omit it or mark it incomplete.
- The image must not be the only place where a key conclusion appears. Important findings also belong in README, indexes, or knowledge docs.
- Keep source snapshots and prompts under `work/tmp/` or `work/drafts/`; do not place them in `submit/`.

## Content Structure

Recommended layout:

1. Header: project name and title, e.g. `<Project> 仓库 Bug 审计与架构风险总览`.
2. Metadata strip: analysis date, analyst when provided, scope, method, version-evidence summary.
3. Count cards: total Bugs, P1/P2/P3/P4, confidence distribution.
4. Risk composition: categories, infra domains, or top issue families.
5. P1/P2 focus: top affected repos/modules and dominant risk families.
6. Architecture signals: 3-5 concise repeated risk signals.
7. File guide: README, findings, indexes, knowledge, quality, standards.
8. Footer: source status, package status, version-evidence note.

Do not try to include every package detail. The overview image is a cover and navigation aid, not a replacement for README or indexes. If the image starts to need scrolling, tiny labels, or nested cards, remove content before reducing font size.

If space is limited, prioritize:

- Scope.
- Total/P1/P2 counts.
- Stability/security/data-integrity distribution.
- Top repos/modules.
- Architecture signals.
- File guide or three-step reading order, not both.
- Metadata footer.

Recommended density limits:

- 5-7 visible modules total.
- 3-5 P1/P2 focus rows.
- 3-4 architecture signals.
- 3-4 risk bars per group.
- One short file guide or reading-order strip.
- No card inside a card unless the inner card is a repeated data item with enough breathing room.
- Keep body text short enough to read at common review size. Prefer 8-14 Chinese characters per label and one-line rows where possible.
- Do not shrink font sizes to rescue overcrowding. Remove low-value content first.

## Wording

- Follow `writing-style.md`.
- Use `Bug`, not mixed labels.
- Use `source=static-analysis` or `静态分析` plainly.
- Do not write process narration or audience explanation.
- Do not use “高置信缺陷”, “已完成验证”, “面向开发团队”, “AI 分析”, or similar phrasing.
- Architecture text should be discovery wording: `集中在`, `表现为`, `缺少`, `容易导致`.

## Charts

- Prefer simple bar cards, stacked bars, or small tables.
- Do not use tiny pie labels.
- Always show exact counts when possible.
- If counts come from `indexes/findings.generated.json`, keep image numbers aligned with README and index.
- If version evidence is incomplete, show it as incomplete rather than hiding it.

## Metadata

The image should include:

- `时间`
- `分析人` when provided; if missing, show `待补充` or omit it when space is tight
- `范围`
- `方法`
- `版本凭证`
- `工具 aiden0z/skills/repo-bug-audit` — **mandatory**, appended as the final segment of the metadata footer line. Same `12-13px` size as other metadata, `ink-tertiary` color (e.g. `#A3A3A3` warm ramp / `#64748B` cool ramp). No icon, no badge, no link decoration. One single segment, separated from the previous segment by ` · ` like the rest. If the metadata line wraps, keep this segment on the last line so it visually closes the image.

Example footer line:

```
时间 2026-05-07 · 范围 3 仓库 · 方法 静态分析 · 版本凭证 完整 · 工具 aiden0z/skills/repo-bug-audit
```

Rules for the attribution segment:
- Exactly this string `工具 aiden0z/skills/repo-bug-audit`. Do not localize, abbreviate, prepend `Generated by`, or append a version.
- Do not also place it on a separate line, in a hero card, in a corner watermark, or repeated elsewhere in the image.
- Skip it only if the user explicitly asked to remove attribution; in that case the README attribution must also be skipped and the choice recorded in `quality/submission-scope.md`.

Version evidence is summarized in the image and detailed in `quality/repository-versions.md`.

Do not infer analyst or author identity from OS username, Git config, directory owner, hostname, model name, or tool account. The image must use the same analyst value as README.

## Quality Gate

Before packaging:

- Open or inspect the image itself and a constrained browser preview for overlap, clipped text, cropped bottom content, stale old layout, and accidental scroll-page screenshots.
- DOM checks are necessary but not sufficient. Passing `scrollWidth <= clientWidth` and `scrollHeight <= clientHeight` does not prove the image is visually balanced or readable after preview scaling.
- Check the rendered image at original size and at a common review size such as `1600x1000`; reject it if text looks compressed, rows collide, modules are cut off, or large empty holes make the layout feel accidental.
- Confirm the submitted PNG dimensions are the intended review dimensions, not only the source-design dimensions.
- Confirm the preview tab or file viewer is refreshed after rewriting `audit-overview.html`; stale `file://` previews can keep showing old DOM in many agent hosts and browser shells.
- Confirm all counts match generated indexes.
- Confirm each numeric value and "top" ranking can be traced to the source snapshot or package files.
- Confirm image text follows `writing-style.md`.
- Confirm the metadata footer ends with `工具 aiden0z/skills/repo-bug-audit` (unless the user explicitly opted out and the choice is recorded in `quality/submission-scope.md`).
- Reject the image if it contains unsupported claims, invented percentages, old terminology, unresolved placeholder text, personal identifiers not supplied by the user, or process/audience explanation.
- The only allowed missing-value placeholders are `待补充` or `not specified` for the analyst field; omit the analyst field if that reads cleaner.
- Compress the PNG without damaging small text; avoid aggressive color quantization if it makes Chinese text edges muddy. Target `<500KB` by default and `<200KB` only when it remains readable.
- Keep source prompts, drafts, and generation notes under `work/tmp/` or `work/drafts/`, not `submit/`.

## Visual Anti-Patterns

Reject the image and regenerate if any of these are present:

- ❌ Dot-grid or line-grid background, "blueprint" texture, paper texture, gradient mesh.
- ❌ All cards drawn with the same `1px solid` border and identical background — no elevation hierarchy.
- ❌ Single font weight throughout the card (e.g. everything `600`, or everything `400`).
- ❌ Raw high-saturation solid color blocks for priority chips (e.g. solid `#DC2626` red rectangle with white text).
- ❌ Zero icons — every label is plain text.
- ❌ Mixed icon sets (Lucide + Material + emoji in the same image).
- ❌ Random border-radius values (`4px` here, `5px` there, `7px` elsewhere). Stick to the scale: `6 / 8 / 12`.
- ❌ Heavy uniform drop shadows on every card (looks like 2014 Material elevation).
- ❌ Bar charts without a track background — bare colored stripes on white.
- ❌ More than 4 hues visible at once, or two competing brand accents.
- ❌ Tiny `<12px` text used to "fit more content" instead of cutting content. Off-scale sizes like `11px`, `12.5px`, `15px` are equally rejected — they signal "I just needed a bit more room" instead of cutting content.
- ❌ Decorative emoji in headings (🚀 ✅ ⚡) inside the submitted image.
- ❌ **Decorative chart elements with no real data backing** — fake sparklines, randomized bar heights, decorative trend curves, random heatmap cells, "design filler" mini-charts. Every glyph that looks like a chart must read off the source snapshot. If you cannot point to the number it represents, delete it. This is the single most common AI-bloat failure in audit overviews.
- ❌ **Priority chips that don't visually separate by hue** — e.g. P1 dark-red `#991B1B` and P2 dark-orange `#9A3412` look identical in a 60px chip. Use the hue-separated P1-P4 palette in the Color System section (red / amber / blue / gray) and verify by squinting at a thumbnail.
- ❌ Hero card visually identical to supporting cards — same border, same shadow, same background. If readers can't tell which card matters most from a thumbnail, the hierarchy has collapsed.
- ❌ Numbers rendered in the same proportional UI font as body copy. Use the mandated mono font for every metric so numbers feel like data, not text.
- ❌ Skill attribution rendered as a watermark, corner stamp, large badge, hero strip, or anything other than a single `12-13px` ink-tertiary segment at the end of the metadata footer line. Attribution is a methodology trace, not branding.
