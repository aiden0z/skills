import { useState, useEffect, useCallback, useRef, Children, cloneElement } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { config, colors } from '../theme'

const MODES = { SLIDE: 'slide', LIST: 'list', PRINT: 'print' }

// Hex to rgba helper for CSS custom properties
const hexToRgba = (hex, alpha) => {
  const r = parseInt(hex.slice(1,3), 16)
  const g = parseInt(hex.slice(3,5), 16)
  const b = parseInt(hex.slice(5,7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}
const themeCssVars = {
  '--theme-primary-08': hexToRgba(colors.primary, 0.08),
  '--theme-primary-15': hexToRgba(colors.primary, 0.15),
  '--theme-primary-20': hexToRgba(colors.primary, 0.20),
}

// SVG icon paths
const ICONS = {
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

function SvgIcon({ d, size = 3.5 }) {
  return (
    <svg className={`w-${size} h-${size}`} style={{ width: size * 4, height: size * 4 }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  )
}

function ToolbarButton({ onClick, icon, label, className = '', active = false }) {
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

// 列表模式左侧导航栏 — 纯 slide 列表，职责单一
function SideNav({ slides, current, onSelect }) {
  const activeRef = useRef(null)

  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [current])

  return (
    <div className="hidden lg:flex flex-col w-48 shrink-0 h-screen sticky top-0 bg-white border-r border-neutral-200/80">
      <div className="px-3 py-3 border-b border-neutral-100">
        <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider">Slides</span>
      </div>
      <div className="flex-1 overflow-y-auto py-1.5 px-1.5">
        {slides.map((slide, i) => {
          const title = slide.props.title
          const isActive = i === current
          return (
            <button
              key={i}
              ref={isActive ? activeRef : undefined}
              onClick={() => onSelect(i)}
              className={`w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-left transition-all text-[12px] leading-tight mb-0.5 ${
                isActive
                  ? 'bg-neutral-100 text-neutral-900 font-medium'
                  : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-50'
              }`}
            >
              <span className={`font-mono tabular-nums shrink-0 w-5 text-center text-[11px] ${isActive ? 'text-neutral-900 font-semibold' : 'text-neutral-300'}`}>
                {String(i + 1).padStart(2, '0')}
              </span>
              <span className="truncate">{title || `Slide ${i + 1}`}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

// 演示模式浮层导航 — G 键或底部按钮触发，点击跳转后自动关闭
function PresentationNav({ slides, current, goTo, open, onClose }) {
  const panelRef = useRef(null)
  const activeRef = useRef(null)

  // 点击面板外关闭
  useEffect(() => {
    if (!open) return
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) onClose()
    }
    const id = setTimeout(() => document.addEventListener('pointerdown', handler), 50)
    return () => { clearTimeout(id); document.removeEventListener('pointerdown', handler) }
  }, [open, onClose])

  // 当前项滚动到可视区
  useEffect(() => {
    if (open && activeRef.current) activeRef.current.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }, [open, current])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/40" style={{ backdropFilter: 'blur(2px)' }}>
      <div
        ref={panelRef}
        className="absolute left-4 top-4 bottom-4 w-60 bg-neutral-900/90 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden flex flex-col shadow-2xl"
      >
        <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
          <span className="text-[11px] font-semibold text-white/50 uppercase tracking-wider">Go to Slide</span>
          <button onClick={onClose} className="text-white/30 hover:text-white/70 transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d={ICONS.close} />
            </svg>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto py-2 px-2">
          {slides.map((slide, i) => {
            const title = slide.props.title
            const isActive = i === current
            return (
              <button
                key={i}
                ref={isActive ? activeRef : undefined}
                onClick={() => { goTo(i); onClose() }}
                className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left transition-all text-[12px] leading-tight mb-0.5 ${
                  isActive
                    ? 'bg-white/15 text-white font-medium'
                    : 'text-white/45 hover:text-white/80 hover:bg-white/8'
                }`}
              >
                <span className={`font-mono tabular-nums shrink-0 w-5 text-center text-[11px] ${isActive ? 'text-white font-semibold' : 'text-white/25'}`}>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="truncate">{title || `Slide ${i + 1}`}</span>
              </button>
            )
          })}
        </div>
        <div className="px-4 py-2 border-t border-white/10 text-[10px] text-white/25 text-center">
          Press <kbd className="px-1 py-0.5 bg-white/10 rounded text-white/40">G</kbd> to toggle
        </div>
      </div>
    </div>
  )
}

// 右侧浮动工具栏（收起/展开）
function Toolbar({ mode, setMode, showBonus, setShowBonus, hasBonus, onPrint }) {
  const [open, setOpen] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const menuRef = useRef(null)
  const canFullscreen = typeof document.documentElement.requestFullscreen === 'function'

  useEffect(() => {
    const onFsChange = () => setIsFullscreen(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', onFsChange)
    return () => document.removeEventListener('fullscreenchange', onFsChange)
  }, [])

  // clickOutside / touchOutside 关闭菜单
  useEffect(() => {
    if (!open) return
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    document.addEventListener('touchstart', handler)
    return () => {
      document.removeEventListener('mousedown', handler)
      document.removeEventListener('touchstart', handler)
    }
  }, [open])

  const toggleFullscreen = () => {
    if (document.fullscreenElement) document.exitFullscreen()
    else document.documentElement.requestFullscreen()
    setOpen(false)
  }

  const isSlideMode = mode === MODES.SLIDE

  return (
    <div ref={menuRef} className="toolbar-fab fixed right-4 top-4 z-50 flex flex-col items-end gap-2">
      <button
        onClick={() => setOpen(!open)}
        className="w-9 h-9 rounded-xl bg-neutral-900/70 backdrop-blur-md text-white/80 flex items-center justify-center hover:bg-neutral-800 transition-all shadow-lg border border-white/10"
      >
        <SvgIcon d={open ? ICONS.close : ICONS.dots} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="bg-neutral-900/80 backdrop-blur-md rounded-xl p-1.5 flex flex-col gap-1 shadow-xl border border-white/10"
          >
            {/* 演示模式：显示"退回列表"；非演示模式：显示模式切换 */}
            {isSlideMode ? (
              <ToolbarButton
                onClick={() => {
                  if (document.fullscreenElement) document.exitFullscreen()
                  setMode(MODES.LIST)
                  setOpen(false)
                }}
                icon={ICONS.back}
                label="Back to list"
              />
            ) : (
              <>
                <ToolbarButton
                  onClick={() => { setMode(MODES.SLIDE); setOpen(false) }}
                  icon={ICONS.play}
                  label="Present"
                  active={mode === MODES.SLIDE}
                />
                <ToolbarButton
                  onClick={() => { setMode(MODES.LIST); setOpen(false) }}
                  icon={ICONS.list}
                  label="List"
                  active={mode === MODES.LIST}
                />
              </>
            )}

            <div className="h-px bg-white/10 my-0.5" />

            {canFullscreen && (
              <ToolbarButton
                onClick={toggleFullscreen}
                icon={isFullscreen ? ICONS.exitFs : ICONS.enterFs}
                label={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
              />
            )}

            {hasBonus && (
              <ToolbarButton
                onClick={() => { setShowBonus(!showBonus); setOpen(false) }}
                icon={ICONS.folder}
                label={`Appendix${showBonus ? ' ✓' : ''}`}
                className={showBonus ? 'bg-amber-500/20 text-amber-300' : undefined}
              />
            )}

            <ToolbarButton
              onClick={() => {
                setOpen(false)
                onPrint()
              }}
              icon={ICONS.download}
              label="Export PDF"
              className="text-white/70 hover:text-white/90"
              style={{ backgroundColor: hexToRgba(colors.primary, 0.2) }}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function Deck({ children }) {
  const [current, setCurrent] = useState(0)
  const [mode, setMode] = useState(MODES.LIST)
  const [showBonus, setShowBonus] = useState(false)
  const [navOpen, setNavOpen] = useState(false)
  const slideRefs = useRef([])
  const prevModeBeforePrint = useRef(null)

  const allSlides = Children.toArray(children)
  const hasBonus = allSlides.some(s => s.props.bonus)
  const slides = showBonus ? allSlides : allSlides.filter(s => !s.props.bonus)
  const total = slides.length

  // 点击"导出 PDF"：切到 PRINT 模式渲染全部 slide → 等 ECharts 渲染 → window.print()
  // afterprint 事件自动恢复到之前的模式
  const handlePrint = useCallback(() => {
    prevModeBeforePrint.current = mode
    setMode(MODES.PRINT)

    const restoreMode = () => {
      setMode(prevModeBeforePrint.current || MODES.LIST)
      window.removeEventListener('afterprint', restoreMode)
    }
    window.addEventListener('afterprint', restoreMode)

    // 等 React 渲染 + ECharts 绘制完成后再触发打印（ECharts animationDuration 最长 1200ms）
    setTimeout(() => window.print(), 1500)
  }, [mode])

  // 收起附录时，如果当前页超出范围，回退到最后一页
  useEffect(() => {
    if (current >= total) setCurrent(Math.max(0, total - 1))
  }, [total, current])

  // 全屏状态跟踪（演示模式底部控制条使用）
  const [isFullscreen, setIsFullscreen] = useState(false)
  useEffect(() => {
    const onFs = () => setIsFullscreen(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', onFs)
    return () => document.removeEventListener('fullscreenchange', onFs)
  }, [])


  const goTo = useCallback((index) => {
    const clamped = Math.max(0, Math.min(index, total - 1))
    setCurrent(clamped)
    return clamped
  }, [total])

  const next = useCallback(() => goTo(current + 1), [current, goTo])
  const prev = useCallback(() => goTo(current - 1), [current, goTo])

  const scrollToSlide = useCallback((index) => {
    const el = slideRefs.current[index]
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, [])

  // 演示模式 — 鼠标/触摸静止 2.5s 后自动隐藏 UI（工具栏 + 导航点 + 翻页区）
  const [uiVisible, setUiVisible] = useState(true)
  const hideTimerRef = useRef(null)

  useEffect(() => {
    if (mode !== MODES.SLIDE) { setUiVisible(true); return }

    const resetTimer = () => {
      setUiVisible(true)
      clearTimeout(hideTimerRef.current)
      hideTimerRef.current = setTimeout(() => setUiVisible(false), 2500)
    }
    resetTimer()

    window.addEventListener('mousemove', resetTimer)
    window.addEventListener('mousedown', resetTimer)
    window.addEventListener('touchstart', resetTimer)
    window.addEventListener('touchmove', resetTimer)
    return () => {
      clearTimeout(hideTimerRef.current)
      window.removeEventListener('mousemove', resetTimer)
      window.removeEventListener('mousedown', resetTimer)
      window.removeEventListener('touchstart', resetTimer)
      window.removeEventListener('touchmove', resetTimer)
    }
  }, [mode])

  // 检测是否支持 Fullscreen API（iOS Safari 不支持）
  const canFullscreen = typeof document.documentElement.requestFullscreen === 'function'

  // 进入演示模式时自动全屏（仅在支持的设备上）
  const prevModeRef = useRef(mode)
  useEffect(() => {
    if (prevModeRef.current !== MODES.SLIDE && mode === MODES.SLIDE) {
      if (canFullscreen && !document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {})
      }
    }
    prevModeRef.current = mode
  }, [mode, canFullscreen])

  // 区分 F 键切换全屏 vs ESC 退出全屏：F 键设标记，fullscreenchange 时跳过退出演示
  const fKeyToggleRef = useRef(false)

  // 演示模式下，ESC 退出全屏时同时退回列表（F 键退出全屏则不退演示）
  // 不支持 Fullscreen API 的设备（如 iOS）跳过此监听，避免误触发退出
  useEffect(() => {
    if (mode !== MODES.SLIDE || !canFullscreen) return
    const onFsChange = () => {
      if (!document.fullscreenElement) {
        if (fKeyToggleRef.current) {
          // F 键触发的退出全屏，不退演示
          fKeyToggleRef.current = false
        } else {
          // ESC 或其他方式退出全屏，同时退回列表
          setMode(MODES.LIST)
          setTimeout(() => scrollToSlide(current), 100)
        }
      }
    }
    document.addEventListener('fullscreenchange', onFsChange)
    return () => document.removeEventListener('fullscreenchange', onFsChange)
  }, [mode, current, scrollToSlide, canFullscreen])

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (mode === MODES.PRINT) return

      switch (e.key) {
        case 'Escape':
          if (mode === MODES.SLIDE) {
            e.preventDefault()
            if (navOpen) {
              setNavOpen(false)
            } else if (document.fullscreenElement) {
              document.exitFullscreen()
            } else {
              setMode(MODES.LIST)
              setTimeout(() => scrollToSlide(current), 100)
            }
          }
          break
        case 'ArrowRight': case 'ArrowDown': case ' ':
          e.preventDefault()
          const ni = goTo(current + 1)
          if (mode === MODES.LIST) scrollToSlide(ni)
          break
        case 'ArrowLeft': case 'ArrowUp':
          e.preventDefault()
          const pi = goTo(current - 1)
          if (mode === MODES.LIST) scrollToSlide(pi)
          break
        case 'Home': e.preventDefault(); goTo(0); if (mode === MODES.LIST) scrollToSlide(0); break
        case 'End': e.preventDefault(); goTo(total - 1); if (mode === MODES.LIST) scrollToSlide(total - 1); break
        case 'f': case 'F':
          if (document.fullscreenElement) {
            fKeyToggleRef.current = true
            document.exitFullscreen()
          } else {
            document.documentElement.requestFullscreen()
          }
          break
        case 'g': case 'G':
          if (mode === MODES.SLIDE) {
            e.preventDefault()
            setNavOpen(prev => !prev)
          }
          break
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [current, mode, goTo, scrollToSlide, total])

  // 演示模式 — 触摸滑动翻页
  const touchStartRef = useRef(null)
  useEffect(() => {
    if (mode !== MODES.SLIDE) return
    const onTouchStart = (e) => {
      touchStartRef.current = { x: e.touches[0].clientX, y: e.touches[0].clientY }
    }
    const onTouchEnd = (e) => {
      if (!touchStartRef.current) return
      const dx = e.changedTouches[0].clientX - touchStartRef.current.x
      const dy = e.changedTouches[0].clientY - touchStartRef.current.y
      touchStartRef.current = null
      // 只在水平滑动距离 > 50px 且大于垂直距离时翻页
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) {
        if (dx < 0) next()
        else prev()
      }
    }
    window.addEventListener('touchstart', onTouchStart, { passive: true })
    window.addEventListener('touchend', onTouchEnd, { passive: true })
    return () => {
      window.removeEventListener('touchstart', onTouchStart)
      window.removeEventListener('touchend', onTouchEnd)
    }
  }, [mode, next, prev])

  // 列表模式 — 滚动时跟踪可视 slide 更新页码
  useEffect(() => {
    if (mode !== MODES.LIST) return
    const observers = []
    slideRefs.current.forEach((el, i) => {
      if (!el) return
      const io = new IntersectionObserver(
        ([entry]) => { if (entry.isIntersecting) setCurrent(i) },
        { threshold: 0.5 }
      )
      io.observe(el)
      observers.push(io)
    })
    return () => observers.forEach(io => io.disconnect())
  }, [mode, total])

  // 打印模式 — 只渲染 Slide，不渲染 Toolbar（避免多余元素干扰分页）
  if (mode === MODES.PRINT) {
    return (
      <div className="print-deck">
        {slides.map((slide, i) => cloneElement(slide, { key: i, pageNumber: i + 1, totalPages: total, printMode: true }))}
      </div>
    )
  }

  // 列表模式
  if (mode === MODES.LIST) {
    const HeaderBtn = ({ icon, label, onClick, primary, active }) => (
      <button
        onClick={onClick}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-all ${
          primary ? 'text-white shadow-sm' : active ? 'bg-amber-50 text-amber-600' : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100'
        }`}
        style={primary ? { backgroundColor: colors.primary } : undefined}
      >
        <SvgIcon d={icon} size={3} />
        <span className="hidden sm:inline">{label}</span>
      </button>
    )

    return (
      <div className="flex h-screen" style={themeCssVars}>
        {/* 左侧导航 — lg 屏幕以上 */}
        <SideNav slides={slides} current={current} onSelect={(i) => { setCurrent(i); scrollToSlide(i) }} />

        {/* 主内容区 */}
        <div className="list-deck flex-1 overflow-y-auto">
          {/* Header bar — logo + 标题（左）+ 操作按钮（右） */}
          <div className="sticky top-0 z-40 backdrop-blur-md bg-white/80 border-b border-neutral-200/60">
            <div className="max-w-[90vw] xl:max-w-5xl mx-auto lg:max-w-none lg:mx-0 px-4 lg:px-6 h-12 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <img src={config.logo || '/logo.svg'} alt="logo" className="h-4 opacity-50" onError={(e) => e.target.style.display = 'none'} />
                <div className="h-3 w-[1px] bg-neutral-200" />
                <span className="text-[11px] text-neutral-400 font-mono tracking-wide">{config.title?.toUpperCase() || 'SLIDES'}</span>
                <span className="text-[11px] text-neutral-300 font-mono tabular-nums ml-2">
                  {String(current + 1).padStart(2, '0')}/{String(total).padStart(2, '0')}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <HeaderBtn icon={ICONS.play} label="Present" onClick={() => setMode(MODES.SLIDE)} primary />
                <HeaderBtn icon={ICONS.download} label="Export PDF" onClick={handlePrint} />
                {hasBonus && <HeaderBtn icon={ICONS.folder} label={`Appendix${showBonus ? ' ✓' : ''}`} onClick={() => setShowBonus(!showBonus)} active={showBonus} />}
              </div>
            </div>
          </div>

          {/* Slide 卡片 */}
          <div className="max-w-[90vw] xl:max-w-5xl mx-auto lg:max-w-none lg:px-6 py-6 px-4 flex flex-col gap-6">
            {slides.map((slide, i) => (
              <div
                key={i}
                ref={(el) => (slideRefs.current[i] = el)}
                className={`slide-card aspect-video rounded-2xl overflow-hidden cursor-pointer ${
                  i === current ? 'shadow-2xl scale-[1.005] ring-2' : 'shadow-lg'
                }`}
                style={i === current ? { '--tw-ring-color': hexToRgba(colors.primary, 0.2) } : undefined}
                onClick={(e) => {
                  if (e.target.closest('button, a, input, select, [role="tab"], [role="button"]')) return
                  setCurrent(i); setMode(MODES.SLIDE)
                }}
              >
                {cloneElement(slide, { pageNumber: i + 1, totalPages: total })}
              </div>
            ))}
            <div className="h-4" />
          </div>
        </div>
      </div>
    )
  }

  // 演示模式
  const uiClass = `transition-opacity duration-500 ${uiVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`
  const toggleFullscreen = () => {
    if (document.fullscreenElement) document.exitFullscreen()
    else document.documentElement.requestFullscreen()
  }

  // 小图标按钮 — 用于底部控制条右侧
  const CtrlBtn = ({ icon, label, onClick, active }) => (
    <button
      onClick={onClick}
      className={`w-7 h-7 rounded-lg flex items-center justify-center transition-all ${
        active ? 'bg-white/20 text-white' : 'text-white/40 hover:text-white/70 active:text-white'
      }`}
      title={label}
    >
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
      </svg>
    </button>
  )

  return (
    <div className={`relative w-screen h-screen overflow-hidden bg-black flex items-center justify-center ${uiVisible ? '' : 'cursor-none'}`}>
      {/* Slide 内容 */}
      <div className="slide-stage">
        <AnimatePresence mode="wait">
          {cloneElement(slides[current], { key: current, pageNumber: current + 1, totalPages: total })}
        </AnimatePresence>
      </div>

      {/* 统一底部控制条 */}
      <div className={`nav-controls fixed bottom-3 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 bg-black/40 backdrop-blur-md rounded-full px-3 py-1.5 border border-white/10 ${uiClass}`}>
        {/* 左区：导航按钮 + 页码圆点 */}
        <CtrlBtn icon={ICONS.list} label="Slide 导航 (G)" onClick={() => setNavOpen(!navOpen)} active={navOpen} />
        <div className="w-[1px] h-3.5 bg-white/10" />
        <div className="flex gap-1.5 items-center">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => goTo(i)}
              className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
                i === current ? 'bg-white scale-150' : 'bg-white/25 hover:bg-white/50'
              }`}
            />
          ))}
        </div>

        {/* 分隔 */}
        <div className="w-[1px] h-3.5 bg-white/10" />

        {/* 右区：操作按钮 */}
        {hasBonus && <CtrlBtn icon={ICONS.folder} label={`Appendix${showBonus ? ' ✓' : ''}`} onClick={() => setShowBonus(!showBonus)} active={showBonus} />}
        <CtrlBtn icon={ICONS.close} label="Exit (ESC)" onClick={() => {
          if (document.fullscreenElement) document.exitFullscreen()
          setMode(MODES.LIST)
          setTimeout(() => scrollToSlide(current), 100)
        }} />
      </div>

      {/* Slide 导航浮层 */}
      <PresentationNav slides={slides} current={current} goTo={goTo} open={navOpen} onClose={() => setNavOpen(false)} />

      {/* 左侧翻页 */}
      <div className={`fixed top-0 left-0 w-12 h-full cursor-pointer z-30 group ${uiClass}`} onClick={prev}>
        <div className="w-full h-full flex items-center justify-center opacity-20 md:opacity-0 md:group-hover:opacity-100 active:opacity-100 transition-opacity">
          <div className="w-8 h-8 rounded-full bg-black/20 backdrop-blur-sm flex items-center justify-center">
            <svg className="w-4 h-4 text-white/60" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          </div>
        </div>
      </div>

      {/* 右侧翻页 */}
      <div className={`fixed top-0 right-0 w-12 h-full cursor-pointer z-30 group ${uiClass}`} onClick={next}>
        <div className="w-full h-full flex items-center justify-center opacity-20 md:opacity-0 md:group-hover:opacity-100 active:opacity-100 transition-opacity">
          <div className="w-8 h-8 rounded-full bg-black/20 backdrop-blur-sm flex items-center justify-center">
            <svg className="w-4 h-4 text-white/60" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
          </div>
        </div>
      </div>
    </div>
  )
}
