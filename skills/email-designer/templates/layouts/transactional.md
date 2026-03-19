# Transactional Layout (事务通知布局)

## Applicable Scenarios
Order confirmations, password resets, shipping notifications, account alerts, receipts

## Structure
1. **Compact Header** (component: header.html)
   - Logo only, minimal height, no subtitle

2. **Main Content** (single block, no section borders)
   - Greeting line
   - Core message (1-3 short paragraphs)
   - Optional: order/transaction detail table

3. **CTA Button** (component: button.html)
   - Single prominent action button
   - Centered, generous vertical padding

4. **Minimal Footer** (component: footer.html)
   - Company name + support link only

## Visual Layout
┌──────────────────────────┐
│  [Logo]                  │
├──────────────────────────┤
│                          │
│  Hi {{name}},            │
│                          │
│  Your order #{{id}}      │
│  has been confirmed.     │
│                          │
│     [ View Order ]       │
│                          │
├──────────────────────────┤
│  Company · Support       │
└──────────────────────────┘

## Default Style
- Primary color: #2563eb
- Background: #ffffff (clean, no outer gray)
- Recommended width: 600px
- Minimal decoration, maximum clarity
