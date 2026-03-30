# Production Mode (量产模式)

## Overview

Production mode allows users to repeatedly generate emails from a crystallized
template by filling an Excel spreadsheet. The AI agent is the rendering engine —
no Python scripts are needed by the user.

## Project Structure

Crystallized projects live in `email-projects/` under the user's working directory:

```
email-projects/
  {project-name}/
    template.html           # Jinja2 template (structure + styles fixed, content = variables)
    template.xlsx           # Excel data template (instructions + data sheets + validation + examples)
    assets/                 # Static resources (logo, background images, etc.)
    output/                 # Generation output directory
```

## Detection & Entry (Step 0 Addition)

When the user starts email designer:

1. Check if `email-projects/` exists in the current working directory
2. If yes, scan for subdirectories containing `template.html` + `template.xlsx`
3. List discovered projects with their names
4. Prompt the user:
   - Choose a project + provide Excel data file path → enter Production Mode
   - Type `new` → enter Design Mode (existing flow)
5. If no projects found, enter Design Mode directly

## Production Mode Workflow

### Step P1: Load Template & Excel

1. Read `template.html` from the selected project
2. Read the user-provided Excel file using openpyxl (execute `code-blocks/excel-template-generator.py` → `load_excel_data()`)
3. Parse each data sheet into a list of row dicts
4. Process markup syntax in cell values (`<red>`, `<strong>`, `<blue>`, `<green>`, `<orange>`, `<a>`)
   - Use the same color mapping as the reference project's markup_parser:
     - `<black>` → `#374151`, `<red>` → `#b91c1c`, `<green>` → `#059669`
     - `<orange>` → `#d97706`, `<blue>` → `#2563eb`
   - `<strong>` passes through as-is (standard HTML)
   - `<a href="url">text</a>` → add inline style `color:#2563eb; text-decoration:underline;`
5. Process image references: if a column value looks like an image path, resolve it relative to the project's `assets/` directory

### Step P2: Fill Template

1. For each data sheet, match the sheet name to the corresponding Jinja2 block in `template.html`
2. The template uses Jinja2 syntax:
   - `{{ header.title }}` — single value from a sheet with one row
   - `{% for row in articles %}...{{ row.title }}...{% endfor %}` — repeating rows
3. AI reads the template to understand expected variables, then maps Excel data to them
4. Handle edge cases intelligently:
   - Empty cells → omit the corresponding element (don't render empty table cells)
   - More rows than example → generate additional table rows
   - Fewer rows → generate fewer rows
   - Missing optional columns → skip gracefully

### Step P3: Validate & Preview

1. Run `code-blocks/html-validator.py` → `validate(filled_html)` to check Outlook compatibility
2. Fix any validation errors
3. Save HTML to `{project}/output/{date}_{name}.html`
4. Auto-open browser preview via `code-blocks/preview-helper.py`
5. Ask user if adjustments needed

### Step P4: Generate EML

1. On user confirmation, generate EML via `code-blocks/html-to-eml.py`
2. Save to `{project}/output/`
3. Show output file locations

## Crystallization Process (Design Mode → Production Mode)

After the user completes email design in Design Mode and is satisfied:

### Trigger
Agent asks: "邮件设计完成。是否要将此模板沉淀为可复用项目？以后只需填 Excel 即可重复生成。"

### Step C1: Analyze HTML Structure

Examine the completed HTML and classify each content element:

**Fixed (stays in template as-is):**
- All CSS styles, colors, spacing, fonts
- Table structure and layout
- Dividers, spacers, decorative elements
- Static text (copyright, company name, fixed headings)
- MSO conditional blocks, VML elements

**Dynamic (becomes Jinja2 variable):**
- Data values (numbers, percentages, dates)
- Article/section titles and body text
- Image paths (src attributes for content images, not decorative)
- Links (href values)
- CTA button text
- Any content that changes each time

### Step C2: Generate Jinja2 Template

1. Replace each dynamic content element with Jinja2 syntax
2. Group related variables by section (each section = one Excel sheet)
3. Use `{% for row in sheet_name %}` for repeating content blocks
4. Use `{{ sheet_name.field }}` for single-value sections
5. Preserve ALL original HTML structure, styles, and Outlook compatibility patterns
6. The template MUST produce identical output when filled with the original content

### Step C3: Generate Excel Template

Execute `code-blocks/excel-template-generator.py` → `generate_template()` with the analyzed structure.

The Excel template contains:
- **Sheet 1 "填写说明"**: Green theme, field descriptions, examples, markup syntax reference
- **Sheet 2~N (one per content section)**: Column headers matching Jinja2 variables, data validation dropdowns where applicable, cell comments explaining each field, 2-3 example rows pre-filled with original content

### Step C4: Round-Trip Verification

**This is critical for correctness.**

1. Load the generated Excel template (which contains example data from the original email)
2. Run the Production Mode workflow (P1-P2) to generate HTML from the template + example data
3. Compare the generated HTML with the original design HTML
4. Verify: same structure, same content, same rendering
5. If differences found → fix the Jinja2 template or Excel mapping, repeat verification
6. Only save the project after verification passes

### Step C5: Save Project

1. Create `email-projects/{project-name}/` directory
2. Save `template.html` (Jinja2 version)
3. Save `template.xlsx` (generated Excel template)
4. Copy static assets to `assets/` (logo, background images, decorative images)
5. Create `output/` directory
6. Inform user: "项目已沉淀到 email-projects/{name}/，下次使用时我会自动检测到。"
