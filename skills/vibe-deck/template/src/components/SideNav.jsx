import { useRef, useEffect } from 'react'

export default function SideNav({ slides, current, onSelect }) {
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
