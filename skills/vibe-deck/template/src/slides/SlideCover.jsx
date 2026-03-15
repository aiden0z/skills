import { config, colors } from '../theme'

export default function SlideCover({ title, subtitle }) {
  const displayTitle = title || config.title || 'Slide Kit'
  const p = config.presenter || {}

  return (
    <div className="relative flex items-center h-full px-24 overflow-hidden">
      {/* 右侧装饰 — 垂直渐变线 + 圆弧 */}
      <div className="absolute right-[160px] top-[15%] bottom-[15%] w-[2px] rounded-full" style={{ background: `linear-gradient(to bottom, transparent, ${colors.primary}30, transparent)` }} />
      <div
        className="absolute -right-48 top-1/2 -translate-y-1/2 w-[420px] h-[420px] rounded-full"
        style={{ border: `1.5px solid ${colors.primary}12` }}
      />
      <div
        className="absolute -right-20 top-1/2 -translate-y-1/2 w-[280px] h-[280px] rounded-full"
        style={{ border: `1.5px solid ${colors.primary}08` }}
      />

      {/* 内容 */}
      <div className="relative z-10 max-w-[680px]">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-8 h-[2px] rounded-full" style={{ backgroundColor: colors.primary }} />
          <span className="text-[11px] font-semibold tracking-[0.2em] uppercase" style={{ color: `${colors.primary}aa` }}>
            Presentation
          </span>
        </div>

        <h1 className="text-[46px] font-extrabold tracking-tight leading-[1.1]" style={{ color: colors.text }}>
          {displayTitle}
        </h1>
        {subtitle && (
          <h2 className="text-[22px] font-light tracking-tight mt-3" style={{ color: colors.textSecondary }}>
            {subtitle}
          </h2>
        )}

        {(p.name || p.date) && (
          <div className="flex items-center gap-4 mt-8">
            {p.name && (
              <div className="flex flex-col">
                <span className="text-[14px] font-semibold" style={{ color: colors.text }}>{p.name}</span>
                {p.role && <span className="text-[12px] mt-0.5" style={{ color: colors.muted }}>{p.role}</span>}
              </div>
            )}
            {p.name && p.date && <div className="h-6 w-[1px]" style={{ backgroundColor: `${colors.muted}30` }} />}
            {p.date && (
              <span className="text-[13px] font-mono tracking-wide" style={{ color: colors.muted }}>{p.date}</span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
