export default function MetricCard({ value, unit, label, sublabel, color = 'text-red-600' }) {
  return (
    <div className="flex flex-col items-center justify-center py-2 px-1">
      <div className={`text-[28px] font-black tracking-tight leading-none ${color}`}>
        {value}<span className="text-[14px] font-bold ml-0.5">{unit}</span>
      </div>
      <div className="text-[12px] font-semibold text-neutral-600 mt-1.5 text-center leading-tight">{label}</div>
      {sublabel && <div className="text-[12px] text-neutral-400 text-center leading-tight mt-0.5">{sublabel}</div>}
    </div>
  )
}
