# Production Mode (量产模式)

## Overview

Production mode allows users to repeatedly generate emails from a crystallized
template by filling an Excel spreadsheet. The AI agent is the rendering engine —
it reads the template as a structural reference, reads the Excel data, and
directly generates the filled HTML. No Jinja2 library or Python rendering scripts
are needed.

## Project Structure

Crystallized projects live in `email-projects/` under the user's working directory:

```
email-projects/
  {project-name}/
    template.html           # Reference template (structure + styles fixed, dynamic content marked with comments)
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

### Step P0: Install Dependencies

Before loading Excel data, ensure openpyxl is available:

Execute `code-blocks/deps-checker.py` → `check_and_install(features=['excel'])`

### Step P1: Load Template & Excel

1. Read `template.html` from the selected project — this is the **structural reference**
   that shows the email's layout, styles, and where dynamic content goes
2. Read the user-provided Excel file using openpyxl:
   execute `code-blocks/excel-template-generator.py` → `load_excel_data(excel_path)`
3. The returned data is a dict mapping sheet names to lists of row dicts:
   `{"Header": [{"title": "周报", "date": "2026-03-30"}], "Articles": [...]}`
4. Markup syntax in cell values is automatically processed by `load_excel_data()`:
   - `<black>` → `#374151`, `<red>` → `#b91c1c`, `<green>` → `#059669`
   - `<orange>` → `#d97706`, `<blue>` → `#2563eb`
   - `<strong>` passes through as-is (standard HTML)
   - `<a href="url">text</a>` → adds inline style `color:#2563eb; text-decoration:underline;`
   - Newlines in cells → `<br>` tags
5. Process image references: if a column value looks like an image path,
   resolve it relative to the project's `assets/` directory

### Step P2: Generate Filled HTML

**The AI agent is the rendering engine.** There is no mechanical template rendering
step. Instead:

1. Read `template.html` to understand the email's structure:
   - Which sections exist and their HTML table structure
   - Where dynamic content is marked (with `<!-- SECTION: sheet_name -->` comments
     and `<!-- FIELD: field_name -->` comments)
   - Which parts are fixed (styles, layout, decorative elements)
2. Read the Excel data (from P1) to get the content for each section
3. **Generate the filled HTML directly** by reproducing the template's structure
   and inserting the Excel data in the appropriate places:
   - For single-row sections (e.g., Header): insert values directly
   - For multi-row sections (e.g., Articles): replicate the row HTML pattern
     for each data row in the Excel sheet
   - For empty cells: omit the corresponding element (don't render empty table cells)
   - For missing optional columns: skip gracefully
4. The column names in Excel (English) directly correspond to the content positions
   in the template — this mapping is established during crystallization

### Step P3: Validate & Preview

1. Run `code-blocks/html-validator.py` → `validate(filled_html)` to check Outlook compatibility
2. Fix any validation errors — use `code-blocks/html-patcher.py` for targeted fixes
   (same as Design Mode Quick Edits)
3. Ensure the project's `output/` directory exists (create if missing)
4. Save HTML to `{project}/output/{date}_{name}.html`
5. Auto-open browser preview via `code-blocks/preview-helper.py`
6. Ask user if adjustments needed

### Step P4: Generate EML

1. On user confirmation, generate EML via `code-blocks/html-to-eml.py`
2. Save to `{project}/output/`
3. Show output file locations
4. Ask if the user wants to generate another email from the same template

## Crystallization Process (Design Mode → Production Mode)

After the user completes email design in Design Mode and is satisfied:

### Trigger
Agent asks: "邮件设计完成。是否要将此模板沉淀为可复用项目？以后只需填 Excel 即可重复生成。"

### Step C0: Install Dependencies

Execute `code-blocks/deps-checker.py` → `check_and_install(features=['excel'])`

### Step C1: Analyze HTML Structure

Examine the completed HTML and classify each content element:

**Fixed (stays in template as-is):**
- All CSS styles, colors, spacing, fonts
- Table structure and layout
- Dividers, spacers, decorative elements
- Static text that never changes (copyright notice, company name)
- MSO conditional blocks, VML elements
- Section headings that are structural (e.g., "本周亮点" as a fixed category label)

**Dynamic (marked in template, becomes Excel column):**
- Data values (numbers, percentages, dates)
- Article/section titles and body text
- Image paths (src attributes for content images, not decorative)
- Links (href values)
- CTA button text
- Any content that changes each time the email is sent

**When in doubt**: If a piece of content _could_ change between sends, mark it as
dynamic. It's better to have an extra Excel column the user fills with the same
value each time than to hard-code something that later needs changing.

### Step C2: Generate Reference Template

Create `template.html` — a copy of the original HTML with dynamic content replaced
by descriptive comments that the AI agent can read:

1. For each dynamic section, add an HTML comment: `<!-- SECTION: section_name -->`
2. For each dynamic field within a section, add: `<!-- FIELD: field_name -->`
3. Keep ONE example row for repeating sections (to show the HTML pattern)
4. Preserve ALL original HTML structure, styles, and Outlook compatibility patterns
5. **Use English names** for section and field names — these become Excel column headers

Example:
```html
<!-- SECTION: Header (single row) -->
<td><!-- FIELD: title -->第12期产品周报<!-- /FIELD --></td>
<td><!-- FIELD: date -->2026-03-30<!-- /FIELD --></td>
<!-- /SECTION -->

<!-- SECTION: Articles (repeating rows) -->
<tr>
  <td><!-- FIELD: title -->新功能发布<!-- /FIELD --></td>
  <td><!-- FIELD: summary -->本周发布了...<!-- /FIELD --></td>
</tr>
<!-- /SECTION -->
```

### Step C3: Generate Excel Template

Execute `code-blocks/excel-template-generator.py` → `generate_template(sections, output_path)`

The `sections` argument is a list of dicts with this structure:

```python
sections = [
    {
        "name": "Header",              # Sheet name (English, matches SECTION comment)
        "description": "邮件标题区",    # Chinese description for instructions sheet
        "columns": [
            {
                "name": "title",       # Column header (English, matches FIELD comment)
                "description": "邮件标题",  # Chinese description (shown as cell comment)
                "example": "第12期产品周报",  # Example value from original email
                "required": True,      # Whether field is required
            },
            {
                "name": "date",
                "description": "日期",
                "example": "2026-03-30",
                "required": True,
            },
        ],
        "single_row": True,            # True = one row only (e.g., Header)
                                       # False = multiple rows (e.g., Articles)
    },
    {
        "name": "Articles",
        "description": "文章列表区",
        "columns": [
            {
                "name": "title",
                "description": "文章标题",
                "example": "新功能发布",
                "required": True,
            },
            {
                "name": "summary",
                "description": "摘要",
                "example": "本周发布了...",
                "required": True,
            },
            {
                "name": "image_path",
                "description": "配图路径",
                "example": "banner.png",
                "required": False,
            },
        ],
        "single_row": False,
    },
]

# Optional: add dropdown validation to a column
{
    "name": "trend",
    "description": "趋势方向",
    "example": "↑",
    "required": False,
    "validation": ["↑", "↓", "—"],   # Creates Excel dropdown
}
```

The `output_path` should be `email-projects/{project-name}/template.xlsx`.

### Step C4: Round-Trip Verification

**This is critical for correctness.**

1. Load the generated Excel template (which contains example data from the original email):
   `data = load_excel_data("email-projects/{name}/template.xlsx")`
2. Follow the Production Mode workflow (P1-P2) to generate filled HTML from
   `template.html` + the example data
3. **Compare with the original design HTML** using these criteria:
   - All text content matches (compare visible text, ignoring whitespace differences)
   - All images reference the same paths
   - Table structure has the same number of rows and columns
   - No sections are missing or duplicated
4. If differences found → identify root cause (wrong field mapping, missing section,
   incorrect example data), fix the template or Excel, and re-verify
5. **After 3 failed attempts**: save the project anyway, warn the user, and suggest
   they review the template manually
6. Only save the project after verification passes (or after the 3-attempt warning)

### Step C5: Save Project

1. Create `email-projects/{project-name}/` directory
2. Save `template.html` (reference template with section/field comments)
3. Save `template.xlsx` (generated Excel template with example data)
4. Copy static assets to `assets/` (logo, background images, decorative images)
5. Create `output/` directory
6. Inform user: "项目已沉淀到 email-projects/{name}/，下次使用时我会自动检测到。"

After C5 completes, return to SKILL.md Step 6 and continue with the remaining
wrap-up items (save template, show file locations, show usage guide).
