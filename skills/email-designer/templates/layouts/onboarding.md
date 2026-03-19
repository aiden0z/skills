# Onboarding Layout (引导流程布局)

## Applicable Scenarios
Welcome emails, getting-started guides, feature introductions, setup instructions

## Structure
1. **Header** (component: header.html)
   - Welcoming banner with brand color

2. **Welcome Message**
   - Warm greeting, 1-2 sentences

3. **Numbered Steps** (3-5 steps, using feature-list.html with number icons)
   - Each step: number icon + title + short description
   - Icons: ①②③④⑤ or 1️⃣2️⃣3️⃣

4. **CTA Button** (component: button.html)
   - "Get Started" / "开始使用"

5. **Help Section** (component: callout.html)
   - Support contact info or FAQ link

6. **Footer** (component: footer.html)

## Visual Layout
┌──────────────────────────┐
│       WELCOME BANNER     │
│      Welcome, {{name}}!  │
├──────────────────────────┤
│                          │
│  Here's how to get       │
│  started in 3 steps:     │
│                          │
│  ① Set up your profile   │
│     Description text...  │
│                          │
│  ② Connect your data     │
│     Description text...  │
│                          │
│  ③ Invite your team      │
│     Description text...  │
│                          │
│     [ Get Started ]      │
│                          │
├──────────────────────────┤
│  ▎ Need help? Contact us │
├──────────────────────────┤
│         FOOTER           │
└──────────────────────────┘

## Default Style
- Primary color: #2563eb
- Background: #f8fafc
- Recommended width: 600px
- Friendly tone, generous spacing between steps
