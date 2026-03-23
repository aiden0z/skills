import { colors } from '../theme'

export const MODES = { SLIDE: 'slide', LIST: 'list', PRINT: 'print' }

export const hexToRgba = (hex, alpha) => {
  const r = parseInt(hex.slice(1,3), 16)
  const g = parseInt(hex.slice(3,5), 16)
  const b = parseInt(hex.slice(5,7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

export const themeCssVars = {
  '--theme-primary-08': hexToRgba(colors.primary, 0.08),
  '--theme-primary-15': hexToRgba(colors.primary, 0.15),
  '--theme-primary-20': hexToRgba(colors.primary, 0.20),
}

export const ICONS = {
  dots: 'M12 6.75a.75.75 0 110-1.5.75.75 0 010 1.5zM12 12.75a.75.75 0 110-1.5.75.75 0 010 1.5zM12 18.75a.75.75 0 110-1.5.75.75 0 010 1.5z',
  close: 'M6 18L18 6M6 6l12 12',
  list: 'M4 6h16M4 10h16M4 14h16M4 18h16',
  play: 'M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 010 1.972l-11.54 6.347a1.125 1.125 0 01-1.667-.986V5.653z',
  exitFs: 'M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25',
  enterFs: 'M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15',
  folder: 'M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 00-1.883 2.542l.857 6a2.25 2.25 0 002.227 1.932H19.05a2.25 2.25 0 002.227-1.932l.857-6a2.25 2.25 0 00-1.883-2.542m-16.5 0V6A2.25 2.25 0 016 3.75h3.879a1.5 1.5 0 011.06.44l2.122 2.12a1.5 1.5 0 001.06.44H18A2.25 2.25 0 0120.25 9v.776',
  download: 'M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3',
  back: 'M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3',
}

export function SvgIcon({ d, size = 3.5 }) {
  return (
    <svg className={`w-${size} h-${size}`} style={{ width: size * 4, height: size * 4 }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  )
}

export function ToolbarButton({ onClick, icon, label, className = '', active = false }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs transition-all whitespace-nowrap ${
        active
          ? 'bg-white/15 text-white'
          : className || 'text-white/50 hover:text-white/80 hover:bg-white/5'
      }`}
    >
      <SvgIcon d={icon} />
      {label}
    </button>
  )
}
