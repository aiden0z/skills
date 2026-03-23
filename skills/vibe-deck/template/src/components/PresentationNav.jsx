import { useRef, useEffect } from 'react'
import { ICONS } from './deck-utils'

export default function PresentationNav({ slides, current, goTo, open, onClose }) {
  const panelRef = useRef(null)
  const activeRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) onClose()
    }
    const id = setTimeout(() => document.addEventListener('pointerdown', handler), 50)
    return () => { clearTimeout(id); document.removeEventListener('pointerdown', handler) }
  }, [open, onClose])

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
