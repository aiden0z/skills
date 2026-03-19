---
name: email-designer
description: >
  Generate professional, Outlook-compatible email templates (EML + HTML) through
  natural conversation. Creates pixel-perfect newsletter layouts, announcement emails,
  weekly reports, event invitations, and any formatted email that needs to render
  correctly in Outlook. MUST use this skill when the user wants to: create or design
  an email template, generate an EML file, make a newsletter, format an email for
  Outlook, design a 邮件模板, do 邮件排版 or 邮件设计, create HTML email with
  Outlook compatibility, build a professional-looking email to send via Outlook,
  or produce any kind of formatted/styled email output. Also trigger when the user
  mentions: weekly report email (周报邮件), product update email, event invitation
  email (活动邀请邮件), announcement email (公告邮件), company newsletter, or wants
  to make an email "look professional/beautiful" for sending. This skill handles
  the visual design and EML generation — not email sending, SMTP setup, or email
  parsing. Without this skill, Outlook emails will have broken layouts because
  Outlook uses Word's rendering engine which ignores modern CSS.
---

# Email Designer

Generate Outlook-compatible email templates through conversation. The user describes
what they want, you produce a pixel-perfect EML file that opens as a draft in Outlook.

## How It Works

This skill has three layers:
1. **Rules** — Outlook compatibility constraints you follow when generating HTML
2. **Templates** — Pre-built components and layouts you assemble from
3. **Code blocks** — Python scripts (stdlib only) you execute to produce EML files

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

## Adaptive Flow

Not every request needs the full wizard. Match your approach to the user's input:

**If the user's request already contains enough info** (layout, colors, width, content
type are clear from context), skip ahead. For example, "帮我做一个蓝色的产品更新邮件
模板，600px" already tells you: single-column, blue (#2563eb), 600px. Go straight to
generating.

**If the request is vague** (e.g., "生成一个邮件模板"), use the wizard steps below
to gather what you need — but ask efficiently, combining questions when natural.

### Step 1: Understand the Request

Parse what you already know from the user's message, then fill gaps:

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

### Step 2: Generate HTML

Before generating HTML, read these files for guidance:
- `rules/outlook-compatibility.md` — the Outlook compatibility rules (essential)
- `rules/design-system.md` — universal design foundation (colors, typography, spacing)
  (this is what makes emails look **professional and modern**, not just compatible)
- `rules/design-system-data-report.md` — ONLY for data-heavy emails (KPI dashboards,
  weekly reports, status updates). Skip this for simple newsletters/announcements.
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
   Checks 29 rules including: forbidden CSS, missing VML, column width overflow, text overflow,
   Gmail 102KB size limit, missing alt text, non-HTTPS links, missing preheader,
   elements exceeding container width. Fix any errors before proceeding.
2. **Organize output**: execute `code-blocks/output-manager.py` → `create_project(name)`
   to create a timestamped directory in the **user's working directory**
   (e.g., `./output/2026-03-15_product-report/`). Never write output files
   into the skill's own installation directory.
3. Save HTML to `{project_dir}/newsletter-preview.html`
4. Auto-open in browser: execute `code-blocks/preview-helper.py` → `open_in_browser()`
5. Show ASCII layout summary in conversation: → `ascii_layout_summary(html)`
6. Ask if adjustments needed, iterate until satisfied

### Step 3: Fill Content (Optional)

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

### Step 4: Generate EML

This is where the HTML becomes a real email file. Execute `code-blocks/html-to-eml.py`:

```python
# How to execute: write a modified copy of the script with filled-in CONFIG values,
# then run it with: python3 /path/to/modified_script.py

# The CONFIG section to modify:
HTML_FILE = "output/newsletter-preview.html"   # your generated HTML
OUTPUT_EML = "output/newsletter.eml"           # output path
SUBJECT = "..."                                # ask user
SENDER = ""                                    # optional
TO_ADDRS = []                                  # optional
IMAGE_DIR = "output/images"                    # if images exist
```

The script uses Python's built-in `email` module — no pip install needed. It creates
a proper MIME structure (multipart/alternative → text/plain + multipart/related →
text/html + CID images) with `X-Unsent: 1` so Outlook opens it in draft/compose mode.

### Step 5: Wrap Up

1. Offer to save the template: execute `code-blocks/template-manager.py` → `save_template()`
2. Show the output file locations
3. Display the appropriate usage guide:
   - Chinese user → `templates/guides/outlook-usage-guide-zh.md`
   - English user → `templates/guides/outlook-usage-guide-en.md`

## File Map

```
rules/
  outlook-compatibility.md   ← Read before generating HTML (Outlook rendering rules)
  design-system.md           ← Universal: colors, typography, spacing (ALWAYS read)
  design-system-data-report.md ← Extension: KPI cards, status badges, trends (data emails only)
  email-best-practices.md    ← Design guidance (widths, colors, typography)
  style-presets.md           ← 3 design styles: Corporate, Editorial, Minimal
  placeholder-i18n.md        ← Localized placeholder text (zh/en/ja)
  brand-color-extraction.md  ← Color extraction + preset palettes

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
  html-to-eml.py             ← Complete HTML→EML script (execute this)
  content-filler.py          ← {{placeholder}} replacement + batch filling
  template-manager.py        ← Save/load/list custom templates
  preview-helper.py          ← Browser auto-open + ASCII layout

examples/
  example-single-column.html ← Complete 600px single-column reference
  example-two-column.html    ← Complete 800px two-column reference
```
