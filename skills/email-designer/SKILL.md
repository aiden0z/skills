---
name: email-designer
description: >
  Generate professional, Outlook-compatible email templates (EML + HTML) through
  natural conversation. Creates pixel-perfect newsletter layouts, announcement emails,
  weekly reports, event invitations, and any formatted email that needs to render
  correctly in Outlook. Supports three modes: Design Mode (create from scratch),
  Import Mode (import and replicate an existing .eml file), and Production Mode
  (fill Excel data to repeatedly generate emails from a crystallized template).
  MUST use this skill when the user wants to: create or design an email template,
  generate an EML file, make a newsletter, format an email for Outlook, import or
  replicate an existing email (导入/复刻邮件), design a 邮件模板, do 邮件排版 or
  邮件设计, create HTML email with Outlook compatibility, build a professional-looking
  email to send via Outlook, or produce any kind of formatted/styled email output.
  Also trigger when the user mentions: weekly report email (周报邮件), product update
  email, event invitation email (活动邀请邮件), announcement email (公告邮件),
  company newsletter, importing an .eml file, replicating an email template, or
  wants to make an email "look professional/beautiful" for sending. This skill
  handles the visual design, EML generation, and EML import — not email sending,
  SMTP setup, or email account management. Without this skill, Outlook emails will
  have broken layouts because Outlook uses Word's rendering engine which ignores
  modern CSS.
---

# Email Designer

Generate Outlook-compatible email templates through conversation. The user describes
what they want, you produce a pixel-perfect EML file that opens as a draft in Outlook.

## How It Works

This skill has three layers:
1. **Rules** — Outlook compatibility constraints you follow when generating HTML
2. **Templates** — Pre-built components and layouts you assemble from
3. **Code blocks** — Python scripts you execute to produce EML files

The core (HTML + EML) uses Python stdlib only. Optional features (charts, header
banners, image optimization) require additional packages that are auto-installed
when needed — see Step 0.

## Step 0: Environment Check

Before starting, verify that Python 3 is available. Try these commands (use whichever works on the current platform):

```sh
python3 --version    # macOS / Linux
python --version     # Windows (check that output shows 3.x, not 2.x)
```

- **Exists and Python ≥ 3.8** → continue silently (do not mention the check to the user).
- **Missing or version too low** → do NOT proceed. Instead:
  1. Run `uname -s` and `uname -m` (or `systeminfo` on Windows) to detect the user's OS and architecture.
  2. If you have web search capability, search for the latest recommended way to install Python 3 on the user's platform, and provide the specific commands.
  3. If you cannot search, show this message in the user's language:
     > **中文**: Email Designer 需要 Python 3.8 或更高版本。请访问 https://www.python.org/downloads/ 下载并安装适合你操作系统的版本，安装完成后重新运行。
     >
     > **English**: Email Designer requires Python 3.8 or later. Please visit https://www.python.org/downloads/ to download and install the version for your OS, then try again.
  4. Stop here and wait for the user to install before continuing.

### Optional Dependencies (auto-installed when needed)

If Step 1 determines the email needs charts or image processing:

1. Execute `code-blocks/deps-checker.py` → `check_and_install(features)`
   - `features` is `['charts']`, `['images']`, or `['charts', 'images']`
2. **All available** → continue silently
3. **Just installed** → continue silently (installation is quiet)
4. **Install failed** → inform user and offer alternatives:
   - Charts unavailable → "I'll use HTML tables and stats-grid components instead"
   - Images unavailable → "I'll use the HTML header component and skip compression"

| Feature | Packages | What It Enables |
|---------|----------|-----------------|
| `charts` | plotly, kaleido | Bar, line, heatmap, pie chart generation |
| `images` | pillow | Header banner compositing, image compression |
| `excel` | openpyxl | Excel template generation and data loading (Production Mode) |

### Mode Detection

After environment checks pass, determine the appropriate mode based on user input
and existing projects. The three modes are:

**1. Import Mode** — if the user provides a `.eml` file (or mentions importing/复刻 an
existing email):
1. Execute `code-blocks/eml-to-html.py` → `extract_from_eml(eml_path)` to extract
   HTML and embedded images
2. Execute `save_extracted(result, output_dir)` to save HTML + images with CID
   references converted to relative paths
3. Auto-open the extracted HTML in browser for preview
4. Ask the user: "已提取邮件内容并预览。接下来您想：
   A) 在此基础上调整设计（进入设计模式 Step 3）
   B) 直接沉淀为可复用量产项目（进入沉淀流程）"
5. If A → validate the extracted HTML (`code-blocks/html-validator.py` → `validate(html)`),
   organize output via `code-blocks/output-manager.py` → `create_project(name)`,
   then skip to Step 3 (Preview & Adjust) with the extracted HTML as starting point
6. If B → read `rules/production-mode.md` § "Crystallization Process" and follow steps C0-C5

**2. Production Mode** — if `email-projects/` directory exists with crystallized projects:
1. Scan for subdirectories containing both `template.html` and `template.xlsx`
2. If projects exist, present them:
   > "检测到以下邮件模板项目：
   > 1. {project-name-1}
   > 2. {project-name-2}
   > ...
   > 请选择项目编号并提供 Excel 数据文件路径（如：1 /path/to/data.xlsx），
   > 或输入 'new' 创建新邮件。"
3. If user selects a project → first run `code-blocks/deps-checker.py` →
   `check_and_install(features=['excel'])` to ensure openpyxl is available,
   then read `rules/production-mode.md` and follow steps P0-P4
4. If user types `new` → continue with Design Mode

**3. Design Mode** — default when no EML file provided and no existing projects (or user
chose `new`). Continue with Step 1 below.

## Adaptive Flow

Not every request needs the full wizard. Match your approach to the user's input:

**If the user's request already contains enough info** (layout, colors, width, content
type are clear from context), skip ahead. For example, "帮我做一个蓝色的产品更新邮件
模板，600px" already tells you: single-column, blue (#2563eb), 600px. Go straight to
generating.

**If the request needs clarification**, use the guided interaction pattern below.
The goal is to make decisions easy for the user — especially non-technical users
who may not know email design terminology.

### Guided Interaction Pattern

When gathering requirements, follow these principles:

**1. Infer first, confirm second.** Extract everything you can from the user's
request before asking. For "商机季度报告邮件", you already know: Dashboard layout,
data-heavy, likely needs charts and KPI cards. State your inference and ask for
confirmation, not for a choice from scratch.

**2. Present options as structured choices.** Use tables or labeled options (A/B/C)
rather than open-ended questions. Users find it easier to pick from options than
to describe what they want:

```
🎨 风格选择
A) 深蓝商务风 — 企业级、专业稳重
B) 深绿增长风 — 业绩导向、正向增长
C) 自定义颜色 — 提供你的品牌色

推荐：基于季度报告场景，建议选 A（深蓝商务风）
```

**3. Group related questions into one message.** Aim to gather all remaining info
in a single well-structured message. Separate sections with clear headings. At the
end, offer a shortcut: "或者直接描述你想要的样式，比如：'深蓝色，4个KPI卡片+漏斗图+Top列表'"

**4. Always give a recommendation.** For each choice, state which option you recommend
and why. Users who don't have a preference can just accept the default.

**5. Offer content module selection.** For complex emails (dashboards, reports),
list available modules as a checklist and let the user select which ones to include:

```
📊 内容模块（可多选）
• KPI 指标卡 — 展示核心数字
• 趋势图表 — 季度趋势折线图
• 漏斗图 — 商机各阶段转化
• Top 列表 — 重点商机排名
• 总结文字 — 季度总结与展望
```

### Step 1: Understand the Request

Parse what you already know from the user's message, then fill gaps using the
guided interaction pattern above:

- **Layout**: Which layout fits? Check `templates/layouts/` for options:
  - Single Column (单栏) — product updates, announcements, weekly digests
  - Two Column (双栏) — reports with sidebar data
  - Magazine (杂志) — editorial with hero image and articles
  - Announcement (公告) — minimal, centered, call-to-action
  - Dashboard (数据面板) — KPI reports, analytics digests, weekly reviews
  - Transactional (事务通知) — order confirmations, password resets, system alerts
  - Onboarding (引导流程) — welcome emails, getting-started guides
  - Custom — user describes, you design from components

- **Width**: 600px (mobile-first) / 800px (balanced) / 1200px (desktop) / custom

- **Colors**: Brand image provided? Analyze it for colors (read the image with vision).
  Otherwise, offer presets: Blue #2563eb, Green #059669, Orange #ea580c, Purple #7c3aed, Gray #374151.
  (Full palettes in `rules/brand-color-extraction.md`)

- **Saved templates**: Run `code-blocks/template-manager.py` → `list_templates()` to
  check for reusable templates. If any exist, offer them first.

### Material Assessment

After understanding layout/width/colors, assess what visual materials are needed:

- **User provided data** (Excel, CSV, table, numbers in conversation) → plan chart generation (Step 1.5a)
- **User provided background image** → plan header banner compositing (Step 1.5b)
- **User provided local images** → plan image optimization (Step 1.5c)
- **Email type is Dashboard/Weekly Report/Data Report but no data provided** → ask: "Do you have data you'd like visualized as charts?"

If any material preparation is needed:
1. Run dependency check (Step 0 optional deps)
2. Proceed to Step 1.5

If no materials needed → skip directly to Step 2.

### Step 1.5: Material Preparation (when materials identified)

Prepare visual assets before generating HTML. All outputs go to the project's `images/` directory.

#### 1.5a: Chart Generation (if data provided)

1. Read `rules/chart-design-system.md` for visual constraints
2. Analyze data structure → recommend chart type:
   - Categories × single value → horizontal bar
   - Categories × multiple series → stacked bar
   - Time × values → line chart
   - 2D matrix → heatmap
   - Parts of whole → pie/donut
   - ≤ 5 data points → suggest HTML table or stats-grid instead
3. Confirm with user: "Based on your data, I recommend a [type] chart. OK?"
4. Execute `code-blocks/chart-generator.py`:
   ```python
   gen = EmailChartGenerator(container_width=WIDTH, output_dir='OUTPUT/images')
   path = gen.bar_chart(categories=[...], series={...}, title='...', filename='chart_name.png')
   ```
5. Preview chart image with user, iterate if needed
6. Final PNG ready at `images/{chart_name}.png`

#### 1.5b: Header Banner (if background image provided)

1. Execute `code-blocks/header-generator.py`:
   ```python
   gen = HeaderGenerator()
   path = gen.generate(title='...', subtitle='...', output_path='OUTPUT/images/header_banner.jpg',
                       bg_image='path/to/bg.png')  # or bg_color='#2563eb' for solid
   ```
2. If no background image but user wants a visual banner → offer solid-color option
3. If user doesn't want a banner image → use the HTML header component instead (no Pillow needed)
4. Output: `images/header_banner.jpg`

#### 1.5c: Image Optimization (if local images provided)

1. Ensure images are in the project's `images/` directory
2. Check filenames — non-ASCII names must be renamed to ASCII (see `rules/design-system.md` § Image filename rules)
3. Execute `code-blocks/image-optimizer.py`:
   ```python
   results = optimize_directory('OUTPUT/images/', threshold_kb=200)
   # results = [(filename, original_kb, compressed_kb), ...]
   ```
4. Report savings to user if any files were optimized

### Step 2: Generate HTML

Before generating HTML, read these files for guidance:
- `rules/outlook-compatibility.md` — the Outlook compatibility rules (essential)
- `rules/design-system.md` — universal design foundation (colors, typography, spacing)
  (this is what makes emails look **professional and modern**, not just compatible)
- `rules/design-system-data-report.md` — ONLY for data-heavy emails (KPI dashboards,
  weekly reports, status updates). Skip this for simple newsletters/announcements.
- `rules/chart-design-system.md` — ONLY when generating charts. Color system,
  typography, sizing, and data label conventions for email-embedded charts.
- `rules/email-best-practices.md` — design guidelines
- `rules/style-presets.md` — design style presets (Corporate, Editorial, Minimal).
  Choose a style matching the email's purpose to guide spacing, font sizes, and color usage.
- `rules/placeholder-i18n.md` — use placeholders matching the user's language
- `templates/components/*.html` — proven Outlook-safe component patterns
  (includes stats-grid, nav-bar, status-badge for advanced layouts)
- `examples/example-*.html` — complete working examples for reference

**Design tip — keep headers compact**: The header should feel like a navigation bar,
not a hero banner. Logo + title on one line, total height around 60-70px. Avoid tall
spacer rows and oversized logos in the header — save vertical space for content.

**Why Outlook compatibility matters**: Outlook 2007-2019 on Windows uses Microsoft
Word's rendering engine instead of a browser engine. This means most modern CSS
(flexbox, grid, border-radius, margin) is ignored or broken. The rules file contains
battle-tested patterns from a production email system that handles this correctly.
Every HTML pattern in `templates/components/` has been verified to render correctly
across Outlook, Gmail, Apple Mail, and web clients.

Key principles when generating:
- **NEVER insert content the user did not request** — no "generated by AI" watermarks,
  no tool credits, no disclaimers. The footer should only include what the user's design
  calls for (copyright, unsubscribe link, etc.).
- **Follow `rules/outlook-compatibility.md` strictly** — it covers table layout, inline
  styles, VML dividers, spacer rows, MSO conditionals, and all other Outlook quirks.
  Read that file before generating any HTML.
- **Gmail size limit** — keep HTML under 102KB or Gmail clips the email.
- **Preheader text** — add a hidden `<div style="display:none;">Preview text</div>`
  right after `<body>`.

After generating:
1. **Validate first**: execute `code-blocks/html-validator.py` → `validate(html)`.
   Checks 32 rules including: forbidden CSS, missing VML, column width overflow, text overflow,
   Gmail 102KB size limit, missing alt text, non-HTTPS links, missing preheader,
   elements exceeding container width. Fix any errors before proceeding.
2. **Organize output**: execute `code-blocks/output-manager.py` → `create_project(name)`
   to create a timestamped directory in the **user's working directory**
   (e.g., `./output/2026-03-15_product-report/`). Never write output files
   into the skill's own installation directory.
3. Save HTML to `{project_dir}/newsletter-preview.html`

### Step 3: Preview & Adjust

1. Auto-open in browser: execute `code-blocks/preview-helper.py` → `open_in_browser()`
   - All images render directly (charts, header banner, content images)
   - No need to generate EML for preview
2. Show ASCII layout summary in conversation: → `ascii_layout_summary(html)`
3. Ask if adjustments needed, iterate until satisfied

### Step 4: Fill Content (Optional)

Ask: "Want to fill in content now, or leave placeholders for editing in Outlook?"

If filling now:
1. Execute `code-blocks/content-filler.py` → `generate_fill_template(html)` to show
   all placeholders as a YAML-like template the user can fill at once
2. Collect content — either one at a time OR as a batch dict from the user
3. Execute `fill_batch(html, content_dict, image_dir)` for efficient batch filling
   (auto-maps images from a directory to CID placeholders)
4. Re-preview and check `unfilled_placeholders(html)` for any remaining

### Quick Edits (anytime after Step 2)

If the user asks for a targeted change (e.g., "change the header color to red",
"make the title bigger"), use `code-blocks/html-patcher.py` instead of regenerating:
- `replace_color(html, old, new)` — swap a color everywhere
- `change_width(html, old_w, new_w)` — resize the container
- `replace_text(html, old, new)` — change visible text
- `add_section(html, section_html)` — insert before footer
- `patch_file(path, colors={...}, texts={...})` — apply multiple patches at once

Re-validate after patching: `html-validator.py` → `validate(patched_html)`.

### Step 5: Generate EML

This is where the HTML becomes a real email file. Two options:

**Option A (recommended): Use `eml-builder.py` fluent API**

Write a short Python script that uses the EMLBuilder class:

```python
from pathlib import Path
# Read the eml-builder.py source, then use:
eml = (
    EMLBuilder(sender="", subject="Newsletter Title")
    .set_html(Path("output/newsletter-preview.html").read_text())
    .add_image("logo", "output/images/logo.png")   # for each CID image
    .build("output/newsletter.eml")
)
```

**Option B: Use `html-to-eml.py` script template**

Copy the script, edit the CONFIG section at the top, then run it:

```python
HTML_FILE = "output/newsletter-preview.html"   # your generated HTML
OUTPUT_EML = "output/newsletter.eml"           # output path
SUBJECT = "..."                                # ask user
SENDER = ""                                    # optional
TO_ADDRS = []                                  # optional
IMAGE_DIR = "output/images"                    # if images exist
```

Both approaches use Python's built-in `email` module — no pip install needed. They create
a proper MIME structure (multipart/alternative → text/plain + multipart/related →
text/html + CID images) with `X-Unsent: 1` so Outlook opens it in draft/compose mode.

**After EML is generated, you MUST proceed to Step 6** — do not end the conversation here.

### Step 6: Wrap Up

**Always perform all of the following**, in order:

#### 6a. Offer to Crystallize for Repeated Use

This is important — many users will want to reuse this template with different data
in the future (e.g., weekly reports, periodic newsletters). Always ask:

> "邮件设计完成。是否要将此模板沉淀为可复用项目？以后只需填 Excel 即可重复生成。"

If the user agrees, read `rules/production-mode.md` § "Crystallization Process" and follow steps C0-C5.
After crystallization completes, continue with 6b and 6c below.
If the user declines, continue with 6b and 6c below.

#### 6b. Save Template and Show Output

1. Offer to save the template: execute `code-blocks/template-manager.py` → `save_template()`
2. Show the output file locations (HTML, EML, images)

#### 6c. Show Usage Guide

Display the appropriate Outlook usage guide:
- Chinese user → `templates/guides/outlook-usage-guide-zh.md`
- English user → `templates/guides/outlook-usage-guide-en.md`

## Placeholder Systems

This skill uses two different placeholder mechanisms for different purposes:

- **`{{placeholder}}`** (Design Mode) — used by `code-blocks/content-filler.py` for
  one-time placeholder filling during interactive design. Simple string replacement.
  Use this when building emails from scratch in Design Mode.

- **`<!-- SECTION/FIELD -->` comments** (Production Mode) — used in crystallized
  `template.html` files as structural markers that the AI agent reads to understand
  where to insert Excel data. These are NOT processed by content-filler.py.
  See `rules/production-mode.md` for details.

The two systems serve different workflows and do not interact. content-filler.py
is a Design Mode tool; Production Mode uses the AI agent as the rendering engine.

## File Map

```
rules/
  outlook-compatibility.md   ← Read before generating HTML (Outlook rendering rules)
  design-system.md           ← Universal: colors, typography, spacing (ALWAYS read)
  design-system-data-report.md ← Extension: KPI cards, status badges, trends (data emails only)
  email-best-practices.md    ← Design guidance (widths, colors, typography)
  style-presets.md           ← 3 design styles: Corporate, Editorial, Minimal
  placeholder-i18n.md        ← Localized placeholder text (zh/en/ja)
  chart-design-system.md     ← Chart colors, typography, sizing (read before chart generation)
  brand-color-extraction.md  ← Color extraction + preset palettes
  production-mode.md         ← Production mode: detection, workflow, crystallization, Excel integration

templates/
  components/*.html          ← 19 Outlook-safe HTML building blocks
                                (header, section, card, table, image-placeholder,
                                 divider, footer, stats-grid, nav-bar, status-badge,
                                 progress-bar, button, callout, testimonial,
                                 feature-list, pricing-table, team-member,
                                 alert, timeline)
  layouts/*.md               ← 7 preset layout descriptions
                                (single-column, two-column, magazine, announcement,
                                 dashboard, transactional, onboarding)
  guides/*.md                ← End-user Outlook usage guides (zh/en)

code-blocks/
  html-validator.py          ← Run AFTER generating, BEFORE EML (auto-check 32 rules)
  html-patcher.py            ← Targeted edits (color, width, text) without regenerating
  output-manager.py          ← Timestamped project directories for organized output
  eml-builder.py             ← EML builder class (fluent API)
  cid-embedder.py            ← Image scanning + placeholder PNG creation
  html-to-eml.py             ← HTML→EML conversion (edit CONFIG section, then execute)
  eml-to-html.py             ← Extract HTML + images from .eml files (Import Mode)
  content-filler.py          ← {{placeholder}} replacement + batch filling
  template-manager.py        ← Save/load/list custom templates
  preview-helper.py          ← Browser auto-open + ASCII layout
  deps-checker.py            ← Auto-install optional dependencies (charts, images)
  chart-generator.py         ← Plotly chart generation (bar, line, heatmap, pie)
  header-generator.py        ← Header banner image compositing (text on background)
  image-optimizer.py         ← Image compression (PNG→JPEG, resize, optimize)
  excel-template-generator.py ← Generate & load Excel data templates (openpyxl)

examples/
  example-single-column.html ← Complete 600px single-column reference
  example-two-column.html    ← Complete 800px two-column reference
```
