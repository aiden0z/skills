import { colors } from '../theme'

export const TOOLTIP_STYLE = {
  appendToBody: true,
  backgroundColor: 'rgba(23, 23, 23, 0.95)',
  borderColor: 'transparent',
  textStyle: { color: '#fff', fontSize: 12 },
  padding: [6, 10],
  extraCssText: 'border-radius: 8px; box-shadow: 0 4px 24px rgba(0,0,0,0.25);',
}

export const CHART_COLORS = [
  colors.primary,
  colors.accent,
  colors.success,
  colors.primaryLight,
  colors.danger,
  colors.primaryLighter,
]
