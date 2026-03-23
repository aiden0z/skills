import { useState, useEffect, useCallback, useRef, Children, cloneElement } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { config, colors } from '../theme'
import { MODES, ICONS, hexToRgba, themeCssVars, SvgIcon } from './deck-utils'
import SideNav from './SideNav'
import PresentationNav from './PresentationNav'
import Toolbar from './Toolbar'

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

  // Export PDF: switch to PRINT mode → wait for ECharts render → window.print()
  // afterprint event restores previous mode
  const handlePrint = useCallback(() => {
    prevModeBeforePrint.current = mode
    setMode(MODES.PRINT)

    const restoreMode = () => {
      setMode(prevModeBeforePrint.current || MODES.LIST)
      window.removeEventListener('afterprint', restoreMode)
    }
    window.addEventListener('afterprint', restoreMode)

    // Wait for React render + ECharts draw (max animationDuration ~1200ms)
    setTimeout(() => window.print(), 1500)
  }, [mode])

  // When hiding appendix, clamp current index if it exceeds new total
  useEffect(() => {
    if (current >= total) setCurrent(Math.max(0, total - 1))
  }, [total, current])

  // Fullscreen state tracking
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

  // Presentation mode — auto-hide UI after 2.5s of inactivity
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

  // Detect Fullscreen API support (iOS Safari doesn't support it)
  const canFullscreen = typeof document.documentElement.requestFullscreen === 'function'

  // Auto-fullscreen when entering presentation mode
  const prevModeRef = useRef(mode)
  useEffect(() => {
    if (prevModeRef.current !== MODES.SLIDE && mode === MODES.SLIDE) {
      if (canFullscreen && !document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {})
      }
    }
    prevModeRef.current = mode
  }, [mode, canFullscreen])

  // Distinguish F-key fullscreen toggle vs ESC exit
  const fKeyToggleRef = useRef(false)

  // ESC exits fullscreen AND returns to list (F-key exit stays in presentation)
  useEffect(() => {
    if (mode !== MODES.SLIDE || !canFullscreen) return
    const onFsChange = () => {
      if (!document.fullscreenElement) {
        if (fKeyToggleRef.current) {
          fKeyToggleRef.current = false
        } else {
          setMode(MODES.LIST)
          setTimeout(() => scrollToSlide(current), 100)
        }
      }
    }
    document.addEventListener('fullscreenchange', onFsChange)
    return () => document.removeEventListener('fullscreenchange', onFsChange)
  }, [mode, current, scrollToSlide, canFullscreen])

  // Keyboard navigation
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

  // Touch swipe navigation in presentation mode
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

  // List mode — track visible slide on scroll
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

  // ── Print mode ──
  if (mode === MODES.PRINT) {
    return (
      <div className="print-deck">
        {slides.map((slide, i) => cloneElement(slide, { key: i, pageNumber: i + 1, totalPages: total, printMode: true }))}
      </div>
    )
  }

  // ── List mode ──
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
        <SideNav slides={slides} current={current} onSelect={(i) => { setCurrent(i); scrollToSlide(i) }} />

        <div className="list-deck flex-1 overflow-y-auto">
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

  // ── Presentation mode ──
  const uiClass = `transition-opacity duration-500 ${uiVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`

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
      <div className="slide-stage">
        <AnimatePresence mode="wait">
          {cloneElement(slides[current], { key: current, pageNumber: current + 1, totalPages: total })}
        </AnimatePresence>
      </div>

      <div className={`nav-controls fixed bottom-3 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 bg-black/40 backdrop-blur-md rounded-full px-3 py-1.5 border border-white/10 ${uiClass}`}>
        <CtrlBtn icon={ICONS.list} label="Slide nav (G)" onClick={() => setNavOpen(!navOpen)} active={navOpen} />
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

        <div className="w-[1px] h-3.5 bg-white/10" />

        {hasBonus && <CtrlBtn icon={ICONS.folder} label={`Appendix${showBonus ? ' ✓' : ''}`} onClick={() => setShowBonus(!showBonus)} active={showBonus} />}
        <CtrlBtn icon={ICONS.close} label="Exit (ESC)" onClick={() => {
          if (document.fullscreenElement) document.exitFullscreen()
          setMode(MODES.LIST)
          setTimeout(() => scrollToSlide(current), 100)
        }} />
      </div>

      <PresentationNav slides={slides} current={current} goTo={goTo} open={navOpen} onClose={() => setNavOpen(false)} />

      <div className={`fixed top-0 left-0 w-12 h-full cursor-pointer z-30 group ${uiClass}`} onClick={prev}>
        <div className="w-full h-full flex items-center justify-center opacity-20 md:opacity-0 md:group-hover:opacity-100 active:opacity-100 transition-opacity">
          <div className="w-8 h-8 rounded-full bg-black/20 backdrop-blur-sm flex items-center justify-center">
            <svg className="w-4 h-4 text-white/60" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          </div>
        </div>
      </div>

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
