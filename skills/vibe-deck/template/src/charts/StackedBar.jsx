import { useState } from 'react'

function Tooltip({ tip }) {
  if (!tip) return null
  return (
    <div
      className="fixed z-[9999] pointer-events-none px-2.5 py-1.5 rounded-lg bg-neutral-800/95 text-white text-xs leading-relaxed shadow-xl whitespace-nowrap"
      style={{ left: tip.x, top: tip.y, transform: 'translate(-50%, -110%)' }}
    >
      {tip.text}
    </div>
  )
}

function Segment({ seg, total, onEnter, onLeave }) {
  const pct = (seg.value / total) * 100
  return (
    <div
      className="h-full flex items-center justify-center overflow-hidden cursor-default"
      style={{ width: `${pct}%`, backgroundColor: seg.color }}
      onMouseEnter={(e) => {
        const rect = e.currentTarget.getBoundingClientRect()
        onEnter({ text: `${seg.label}: ${seg.value.toFixed(1)} (${pct.toFixed(1)}%)`, x: rect.left + rect.width / 2, y: rect.top })
      }}
      onMouseLeave={onLeave}
    >
      {pct >= 20 && (
        <span className="text-[10px] text-white font-medium truncate px-0.5 drop-shadow-sm leading-none">
          {seg.value.toFixed(0)} · {pct.toFixed(0)}%
        </span>
      )}
    </div>
  )
}

export default function StackedBar({ segments, height = 24, className = '' }) {
  const [tip, setTip] = useState(null)
  const total = segments.reduce((s, seg) => s + seg.value, 0)

  return (
    <>
      <Tooltip tip={tip} />
      <div className={`flex rounded overflow-hidden ${className}`} style={{ height }}>
        {segments.map((seg, i) => (
          <Segment key={i} seg={seg} total={total} onEnter={setTip} onLeave={() => setTip(null)} />
        ))}
      </div>
    </>
  )
}
