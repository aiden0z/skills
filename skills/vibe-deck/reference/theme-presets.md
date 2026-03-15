# Available Theme Presets

## corporate-blue (default)
- **Best for:** Business presentations, strategy decks, quarterly reviews
- **Primary:** #3b82f6 (blue-500)
- **Accent:** #f59e0b (amber-500)
- **Background:** white
- **Feel:** Professional, clean, corporate

## minimal
- **Best for:** Design reviews, simple reports, text-heavy decks
- **Primary:** #18181b (zinc-900)
- **Accent:** #3b82f6 (blue-500)
- **Background:** white
- **Feel:** Clean, typography-focused, no visual noise

## Custom Theme

Users can create custom themes by setting `overrides` in `slide-kit.config.js`:

```js
export default {
  theme: 'corporate-blue',
  overrides: {
    colors: {
      primary: '#8b5cf6',
      accent: '#ec4899',
    },
  },
}
```

**Color auto-derivation:** When you override `primary` without specifying `primaryDark`/`primaryLight`/`primaryLighter`, the theme system automatically derives them by blending with black (25%) and white (45%, 65%). You only need to set `primary` — the variants come for free.

Or create a new preset file in `src/theme/presets/` and register it in `src/theme/presets/index.js`.
