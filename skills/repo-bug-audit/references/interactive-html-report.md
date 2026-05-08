# Interactive HTML Report

Use this when generating `submit/bug-audit-report.html`.

## Contents

- Purpose
- When To Generate
- Output
- Source Data Contract
- Page Structure
- Interaction Scope
- Visual Design Bar
- Provenance Requirements
- Validation

## Purpose

The HTML report is a rich delivery layer over the final Bug audit package. It helps reviewers understand the audit quickly, then navigate to underlying Markdown files. It is not a replacement for README, Bug records, indexes, knowledge, or quality docs.

First constraint: see `authenticity.md`. Every number, label, repo, module, Bug ID, path, status, and provenance claim in the report must trace to the submitted package.

## When To Generate

Generate the HTML report by default for:

- final handoff packages
- multi-repo audits
- large Bug sets
- packages with architecture review, repo profiles, or promoted knowledge-capture material
- any package likely to be opened in a browser
- any result the user calls a report, dashboard, delivery package, handoff, `报告`, `报告台`, `交付`, or `打包`

Do not ask the user whether to include it in normal interactive mode; it is the default delivery surface for final reports. Skip by default only for quick scans, candidate-only studies, narrow single-Bug reviews, or when the user explicitly asks for a lightweight/no-HTML package. Record the decision in `quality/submission-scope.md`.

## Output

Default file:

```text
submit/bug-audit-report.html
```

Generation command:

```bash
python3 scripts/generate_bug_report_html.py <submit-root> --language zh
```

Use `--language en` for English packages.

## Source Data Contract

The generator reads submitted package files only:

- `indexes/findings.generated.json`
- `README.md`
- `quality/submission-scope.md`
- `quality/repository-versions.md`
- `quality/lens-coverage.md`
- `knowledge/system-overview.md`
- `knowledge/repo-relationship-map.md`
- `knowledge/risk-paths.md`
- `knowledge/architecture-design-review.md`
- `knowledge/repo-profiles/*.md`
- submitted Bug Markdown files under `findings/P*/`

Do not read `work/` for final report content. Promote reusable exploration facts into `submit/knowledge/` first.

## Page Structure

Required sections:

1. **Top Bar and Hero**: use a desktop-first report top bar for orientation only: delivery-report label, short scope label, and section navigation. Do not use logo-like decorative marks in the top bar or hero. Do not duplicate date, Bug counts, priority summary, or status in the top bar; those belong in the hero metadata strip and Metrics console. In the hero, give the title full editorial width, keep audit metadata as a compact inline strip, then place a single unified Metrics console below the title. Do not put `repo-bug-audit` or `github.com/aiden0z/skills` in the top/hero metadata; reserve those for footer provenance. Do not show absolute filesystem paths in the visible scope; prefer repo names or declared audit labels.
2. **Metrics**: total Bugs, P1-P4 counts, P1/P2 focus, repo count, and risk type count. Keep secondary metric cards aligned on an equal-width grid unless the data clearly requires a different hierarchy.
3. **Quality Core**: keep this section MECE. Separate evidence/admission gates, exploration coverage strategy, known exclusions/uncovered areas, and confidence distribution. Do not repeat header metadata or dump raw submission-scope fields.
4. **Architecture Insights**: surface architecture invariants and risk paths before repository distribution. Extract both bullet lists and headed narrative sections from `knowledge/architecture-design-review.md` / `knowledge/risk-paths.md`; do not claim the architecture file is missing just because it uses paragraphs instead of bullets.
5. **Repository Situation**: per-repo Bug counts, dominant risk categories, shared boundaries, uncovered areas.
6. **Findings Preview**: searchable/filterable list with expandable Bug summaries and Markdown file paths.
7. **Reusable Knowledge**: show reusable product/development knowledge such as issue families, impact domains, and fix handoff focus. Do not show exploration-view / lens-tag distribution charts in this section; exploration views are quality-coverage evidence and belong only in **Quality Core** plus `quality/lens-coverage.md`. Preserve technical `lens` metadata for Bug filters and source files when useful.
8. **Delivery Package Guide**: reading order and file guide. File cards must reflect files and directories that actually exist in the submitted package; optional artifacts such as `audit-overview.png` should be omitted when absent.
9. **Footer Provenance**: compact labeled source lines for generated-with skill, skill source, static-analysis status, and package data source.

## Interaction Scope

Allowed interactions:

- sticky section navigation
- local search
- filter chips by priority, repo, category, confidence, lens, and fix risk
- P1/P2 quick toggle
- expandable Bug details
- anchor links

Avoid:

- server dependency
- external JS/CSS/fonts/images
- complex SPA routing
- state persistence
- chart libraries

## Visual Design Bar

The report must feel like a polished modern product analytics page, not a Markdown export.

Reuse the `audit-overview.png` design language:

- modern neutral background
- white raised cards
- graphite top rail, restrained teal quality accent, slate architecture accent, and hue-separated priority colors
- the sticky top rail must keep the approved theme transition: `linear-gradient(90deg,rgba(16,68,59,.96) 0%,rgba(15,118,110,.94) 58%,rgba(18,130,113,.92) 100%)`
- compact provenance; metadata is not a card grid
- strong desktop-first report hierarchy: dark top navigation rail, full-width hero title, and a single grouped Metrics console
- avoid an equal-card Metrics wall; use one primary total block plus a priority lane and grouped secondary metrics for P1/P2 focus, repo count, and risk type count
- keep the `Total Bugs` / `Bug 总数` primary card neutral-light, not green or black; green is an audit-theme accent, while Bug count is problem volume rather than a success state
- keep repeated alignment systems consistent: section headings use one left-aligned eyebrow/title group, metric rows use stable equal columns, finding rows use a left content column plus right metadata column, and footer provenance uses fixed left/center/right alignment on desktop
- keep bottom whitespace tight: the main shell bottom padding should remain modest and the footer should sit close to the final content block
- visible scope labels should use repo names or declared audit labels, not absolute local paths
- hue-separated P1-P4 chips
- mono font for metrics, Bug IDs, and numeric counts
- clear type scale and generous spacing
- subtle elevation; no heavy shadows on every card
- no tiny text used to fit more content

Reject these outputs:

- raw Markdown converted to HTML
- Bootstrap/admin-template look
- huge unstyled table
- overcrowded report with tiny labels
- decorative charts with no source data
- external CDN dependencies

## Provenance Requirements

The report must visibly include:

- `repo-bug-audit`
- `github.com/aiden0z/skills`
- `source=static-analysis`
- generated from final package files
- static-analysis status and final-package data source
- no runtime verification claimed unless explicitly supported

Attribution is methodology traceability, not branding. Keep it factual and unobtrusive, but not hidden.

## Validation

For final handoff packages where the report is expected, run:

```bash
python3 scripts/validate_bug_package.py <submit-root> --require-html-report
```

The validator checks:

- `bug-audit-report.html` exists
- required section anchors exist
- skill provenance exists
- `source=static-analysis` exists
- no placeholder markers remain
- no external asset references exist
- total and P1-P4 counts match `findings.generated.json`
- sticky top navigation keeps the approved theme gradient
- total Bug metric card keeps the approved neutral-light background
- shell bottom padding and footer margin stay within the compact handoff-report spacing budget

When possible, open the report in a browser and check:

- no overlapping text
- sticky navigation does not cover content
- filters and search work
- expanded Bug rows remain readable
- the page still reads well at common desktop widths
