import config from '../../slide-kit.config.js'
import { presetMap } from './presets/index.js'

const base = presetMap[config.theme] || presetMap['corporate-blue']

function deepMerge(target, source) {
  const result = { ...target }
  for (const key of Object.keys(source)) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      result[key] = deepMerge(target[key] || {}, source[key])
    } else {
      result[key] = source[key]
    }
  }
  return result
}

const merged = deepMerge(base, config.overrides || {})

// Auto-derive color variants if user overrides primary but not its variants
if (config.overrides?.colors?.primary && !config.overrides?.colors?.primaryDark) {
  const p = merged.colors.primary
  // Simple hex darken/lighten by blending with black/white
  const hex = (c) => Math.max(0, Math.min(255, Math.round(c))).toString(16).padStart(2, '0')
  const parse = (h) => [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)]
  const blend = (rgb, t, target) => rgb.map((c, i) => c + (target[i] - c) * t)
  const toHex = (rgb) => '#' + rgb.map(hex).join('')
  const rgb = parse(p)
  merged.colors.primaryDark = toHex(blend(rgb, 0.25, [0,0,0]))
  merged.colors.primaryLight = toHex(blend(rgb, 0.45, [255,255,255]))
  merged.colors.primaryLighter = toHex(blend(rgb, 0.65, [255,255,255]))
}

export const theme = merged
export const { colors, fonts, spacing } = theme
export { config }
