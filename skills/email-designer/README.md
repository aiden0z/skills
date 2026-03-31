# Email Designer

> Generate professional email templates through natural conversation. Designed for compatibility with **all major email clients** — Outlook, Gmail, Apple Mail, Yahoo Mail, and more.

[中文文档](README_CN.md)

## Why This Skill?

Creating beautiful emails that render correctly everywhere is surprisingly hard. **Outlook 2007–2019 uses Microsoft Word's rendering engine** instead of a browser engine, which means modern CSS (flexbox, grid, border-radius, margin) simply doesn't work. Most email templates you find online break in Outlook.

This skill solves that. Every template it generates is **validated against Outlook-safe rules and designed for the toughest email client** (Outlook) and gracefully enhanced for modern clients (Gmail, Apple Mail, web). If it works in Outlook, it works everywhere.

### Supported Email Clients

| Client | Engine | Status |
|--------|--------|--------|
| Outlook 2007–2019 (Windows) | Microsoft Word | Fully compatible |
| Outlook for Mac | WebKit | Fully compatible |
| Outlook.com (Web) | Browser | Fully compatible |
| Gmail (Web & Mobile) | Browser | Fully compatible |
| Apple Mail (macOS & iOS) | WebKit | Fully compatible |
| Yahoo Mail | Browser | Fully compatible |
| Thunderbird | Gecko | Fully compatible |

## What It Does

You describe the email you want — layout, colors, content — and the skill generates:

- **EML file** — double-click to open in Outlook as a draft, ready to edit and send
- **HTML file** — preview in any browser, iterate until perfect

### Features

- **4 preset layouts** — single-column, two-column, magazine, announcement
- **Custom layouts** — describe in natural language, the AI designs it
- **Design system** — professional color palette, typography scale, consistent spacing
- **Brand color extraction** — provide your logo, AI extracts your brand colors
- **19 Outlook-safe components** — header, footer, table, card, stats grid, progress bar, CTA button, nav bar, status badge, divider, image placeholder, section, callout, testimonial, feature list, pricing table, team member, alert, timeline
- **32-rule HTML validator** — auto-checks for compatibility issues before output
- **Content filling** — fill placeholders in conversation or leave for Outlook editing
- **Template save/reuse** — save confirmed designs for future use
- **Multilingual** — Chinese, English, Japanese placeholder support
- **Minimal dependencies** — Python stdlib for core HTML/EML; openpyxl auto-installed for Production Mode; optional plotly and pillow for charts and image processing

## Production Mode (量产模式)

Once you've designed an email template you're happy with, crystallize it for repeated use:

1. **Crystallize**: After design, the agent converts your email into a reusable project (reference template + Excel data template)
2. **Fill Excel**: Open the generated `template.xlsx`, fill in your data following the instructions sheet
3. **Generate**: Next time you start the email designer, it auto-detects your project and asks for the Excel file
4. **Repeat**: Same template, different data — consistent professional emails every time

No coding required. The AI agent handles everything.

## Import Mode

Have an existing email you want to replicate? Provide the `.eml` file:

1. **Import**: The agent extracts HTML and images from the EML file
2. **Preview**: Review the extracted email in your browser
3. **Adjust or Crystallize**: Modify the design, or directly crystallize it for production use

## Installation

Copy this skill directory into your AI tool's skills path:

| Tool | Project-level | User-level (all projects) |
|------|--------------|--------------------------|
| Claude Code | `.claude/skills/email-designer/` | `~/.claude/skills/email-designer/` |
| GitHub Copilot | `.github/skills/email-designer/` | `~/.copilot/skills/email-designer/` |
| OpenAI Codex | `.agents/skills/email-designer/` | `~/.codex/skills/email-designer/` |
| Kimi Code | `.kimi/skills/email-designer/` | `~/.kimi/skills/email-designer/` |

Then ask naturally or invoke with `/email-designer`:

```
帮我做一个邮件模板，蓝色主题，800px 宽
```

> Requires Python 3.8+. Core features use stdlib only; Production Mode auto-installs openpyxl when needed.

## Project Structure

```
skill.md                    # Skill entry — adaptive wizard flow
rules/
  outlook-compatibility.md  # Outlook rendering rules (the hard part)
  design-system.md          # Colors, typography, spacing (universal)
  design-system-data-report.md  # KPI cards, status badges (data emails)
  email-best-practices.md   # Width, accessibility, content guidelines
  placeholder-i18n.md       # Multilingual placeholder text
  brand-color-extraction.md # Brand color detection + preset palettes
templates/
  components/*.html         # 19 battle-tested HTML email components
  layouts/*.md              # 7 preset layout definitions
  guides/*.md               # End-user Outlook guides (zh/en)
code-blocks/
  html-validator.py         # 32-rule compatibility checker
  html-to-eml.py            # HTML → EML conversion (auto images/ → CID)
  eml-to-html.py            # Extract HTML + images from .eml files (Import Mode)
  eml-builder.py            # EML builder class (fluent API)
  html-patcher.py           # Targeted edits without regeneration
  content-filler.py         # Batch placeholder filling
  template-manager.py       # Save/load custom templates
  output-manager.py         # Timestamped output directories
  preview-helper.py         # Auto browser preview + ASCII layout
  cid-embedder.py           # Image scanning + placeholder creation
  excel-template-generator.py  # Generate & load Excel data templates (openpyxl)
examples/
  example-single-column.html  # Complete 600px reference
  example-two-column.html     # Complete 800px reference
```

## How It Works

```
You describe what you want
        ↓
AI reads compatibility rules + design system
        ↓
Generates Outlook-safe HTML (table layout, VML, MSO directives)
        ↓
Validates against 32 rules (catches overflow, forbidden CSS, etc.)
        ↓
Opens preview in browser + shows ASCII layout in terminal
        ↓
You iterate until satisfied
        ↓
Generates EML file → open in Outlook → edit & send
```

### The Compatibility Challenge

Most email clients use browser engines to render HTML. Outlook is the exception — it uses **Microsoft Word**, which means:

| Feature | Browser Clients | Outlook |
|---------|----------------|---------|
| Flexbox / Grid | Works | Ignored |
| border-radius | Works | Ignored |
| CSS margin | Works | Partially ignored |
| CSS border colors | Works | All render as black |
| background-image | Works | Partial support |
| `<div>` layout | Works | Unreliable |

This skill handles all of this automatically using:
- **Table-based layouts** instead of div/flexbox
- **VML (Vector Markup Language)** for colored dividers and borders
- **MSO conditional comments** (`<!--[if mso]>`) for Outlook-specific fixes
- **Dual declarations** (HTML attributes + CSS) for maximum compatibility
- **Spacer rows** instead of margin for reliable spacing

The result: emails designed to render consistently across clients.

## Design System

The skill includes a production-tested design system extracted from a real enterprise email platform:

- **5-level text color scale** — `#0f172a` → `#94a3b8` (no pure black)
- **Background layering** — group elements with subtle `#f8fafc` backgrounds instead of borders
- **4px spacing grid** — consistent rhythm from 4px to 40px
- **2 font weights only** — 400 (regular) + 600 (semi-bold)
- **Modern table design** — no vertical borders, gray header rows, clean dividers
- **Semantic colors** — green/orange/red for status, not decoration
- **Data report extension** — KPI cards, status badges, trend indicators, progress bars

## Requirements

- **Python 3.8+** (core features use stdlib only; Production Mode requires openpyxl, auto-installed on first use)
- **An AI CLI tool** (Claude Code, Kimi CLI, or similar)

## License

MIT
