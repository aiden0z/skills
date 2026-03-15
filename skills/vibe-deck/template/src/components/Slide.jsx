import { motion } from 'framer-motion'
import { useRef, useState, useEffect } from 'react'
import { config } from '../theme'

// Fixed reference resolution (16:9) — all slides designed at this size
// 1440×810 gives more vertical room for content-heavy slides while maintaining 16:9
const REF_W = 1440
const REF_H = 810

export default function Slide({
  children,
  pageNumber,
  totalPages,
  bg = 'white',
  className = '',
  logo = config.logo || '/logo.svg',
  footnote,
  title,      // 可选标题，由 Deck 导航栏读取，不渲染
  bonus,      // 附录标记，由 Deck 过滤使用，不渲染
  printMode,  // 打印模式：跳过动画，使用 flex 布局替代 absolute
}) {
  const containerRef = useRef(null)
  const [scale, setScale] = useState(1)

  useEffect(() => {
    if (printMode) return  // 打印模式不需要 ResizeObserver，CSS 控制尺寸
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect
      if (width > 0 && height > 0) {
        setScale(Math.min(width / REF_W, height / REF_H))
      }
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [printMode])

  // ── 打印模式：纯 flex 列布局，无 absolute，无 transform，无动画 ──
  if (printMode) {
    return (
      <div
        className={`slide-container overflow-hidden ${className}`}
        style={{ width: REF_W, height: REF_H, backgroundColor: bg }}
      >
        {/* 内容区域 — flex-1 撑满剩余空间 */}
        <div
          style={{ height: REF_H - 32, padding: 32, overflow: 'hidden' }}
        >
          {children}
        </div>

        {/* 底部栏 — 固定 32px */}
        <div
          style={{ height: 32, padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
        >
          <div className="flex items-center gap-2 opacity-60">
            <img src={logo} alt="logo" className="h-3.5 w-auto" onError={(e) => e.target.style.display = 'none'} />
            {footnote && <span className="text-[9px] text-neutral-400 ml-2 leading-tight">{footnote}</span>}
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-[1px] bg-gradient-to-r from-transparent to-neutral-200" />
            <span className="text-xs text-neutral-300 font-mono tracking-wider tabular-nums">
              {String(pageNumber).padStart(2, '0')}<span className="text-neutral-200 mx-1">/</span>{String(totalPages).padStart(2, '0')}
            </span>
          </div>
        </div>
      </div>
    )
  }

  // ── 正常模式：absolute 定位 + ResizeObserver scale + Framer Motion 动画 ──
  return (
    <div
      ref={containerRef}
      className={`slide-container w-full h-full flex items-center justify-center overflow-hidden`}
      style={{ backgroundColor: bg }}
    >
      <div
        className={`relative overflow-hidden ${className}`}
        style={{
          width: REF_W,
          height: REF_H,
          transform: `scale(${scale})`,
          transformOrigin: 'center center',
          flexShrink: 0,
          backgroundColor: bg,
        }}
      >
        {/* 内容区域 */}
        <motion.div
          className="absolute inset-0 bottom-8 p-8 overflow-hidden"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
        >
          {children}
        </motion.div>

        {/* 底部栏 */}
        <div className="absolute bottom-0 left-0 right-0 h-8 px-8 flex items-center justify-between">
          <div className="flex items-center gap-2 opacity-60">
            <img src={logo} alt="logo" className="h-3.5 w-auto" onError={(e) => e.target.style.display = 'none'} />
            {footnote && <span className="text-[9px] text-neutral-400 ml-2 leading-tight">{footnote}</span>}
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-[1px] bg-gradient-to-r from-transparent to-neutral-200" />
            <span className="text-xs text-neutral-300 font-mono tracking-wider tabular-nums">
              {String(pageNumber).padStart(2, '0')}<span className="text-neutral-200 mx-1">/</span>{String(totalPages).padStart(2, '0')}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
