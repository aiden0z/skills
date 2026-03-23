import { useState, useEffect, useRef } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { colors } from '../theme'
import { MODES, ICONS, SvgIcon, ToolbarButton, hexToRgba } from './deck-utils'

export default function Toolbar({ mode, setMode, showBonus, setShowBonus, hasBonus, onPrint }) {
  const [open, setOpen] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const menuRef = useRef(null)
  const canFullscreen = typeof document.documentElement.requestFullscreen === 'function'

  useEffect(() => {
    const onFsChange = () => setIsFullscreen(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', onFsChange)
    return () => document.removeEventListener('fullscreenchange', onFsChange)
  }, [])

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
