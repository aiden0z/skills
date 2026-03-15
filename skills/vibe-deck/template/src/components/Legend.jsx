export default function Legend({ items, className = '' }) {
  return (
    <div className={`flex flex-wrap gap-x-3 gap-y-1 text-[11px] ${className}`}>
      {items.map(([color, label]) => (
        <div key={label} className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: color }} />
          <span className="text-neutral-500">{label}</span>
        </div>
      ))}
    </div>
  )
}
