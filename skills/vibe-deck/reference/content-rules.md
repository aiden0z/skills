# Content Rules

## Key Message
- **Optional** — only add when the slide has a data-driven insight worth highlighting. Skip for cover, divider, or self-explanatory content slides
- **Position is automatic** — pass content via `keyMessage` prop on `SlideLayout`; do NOT manually position `<KeyMessage>` in JSX
- Every bullet MUST correspond to a visible chart/metric on the same slide
- MUST include quantified data
- Cross-dimensional insights > single-dimension
- Quantify problem scale

## Data Integrity
- NEVER fabricate data
- Verify source file exists before referencing
- If breakdown doesn't exist in source, inform user
- Verify sub-totals sum to total
- When creating placeholder data files (before real extraction), use obviously fake values like `0` or add `// TODO: replace with real data` comments — never use realistic-looking numbers that could be mistaken for actual data

## Data Extraction Workflow

When the user provides an Excel file for data extraction:
1. Use `scripts/extract-xlsx.js` to inspect the structure first (sheets, columns, row counts)
2. Write a custom extraction script specific to this data (node + xlsx)
3. Run the script and verify totals: sub-dimensions MUST sum to the overall total
4. Only after verification passes, write the result to `src/data/<name>.js`
5. NEVER skip the verification step — past experience shows silent data errors are common

## Multi-Source Data Validation

When working with multiple data sources (e.g., different Excel files for different metrics):
- **Verify subset relationships**: If data A is a subset of data B (e.g., won deals ⊆ all opportunities), write a script to confirm every item in A exists in B
- **Watch for inconsistent definitions**: The same field name (e.g., "won") may mean different things in different files. Always confirm the definition with the user
- **Same file, different sheets may contradict**: Dashboard summaries within an Excel may use different logic than the raw data sheet. Trust raw data over dashboards
- **Cascade changes**: When modifying a shared data file (e.g., `opportunities.js`), first grep ALL files that import it, list the full impact, then update every reference

## Data Display Conventions
- Title subtitle text is for data source disclaimers (e.g., "基于 BTM 商机数据，数据可能存在偏差")
- Footer `footnote` prop is for stage/pipeline definitions and abbreviations

## Text Conventions
- Standard unit: `$K`
- Avoid "管线" — use "商机" or "在跟商机"
- Data disclaimers go in `footnote` prop
