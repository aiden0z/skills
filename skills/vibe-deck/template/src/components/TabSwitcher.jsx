export default function TabSwitcher({ tabs, active, onChange }) {
  return (
    <div className="flex bg-neutral-200/60 rounded-md p-0.5 text-[11px]">
      {tabs.map(t => (
        <button
          key={t.key}
          className={`px-2.5 py-0.5 rounded transition-all ${
            active === t.key
              ? 'bg-white text-neutral-700 font-semibold shadow-sm'
              : 'text-neutral-400 hover:text-neutral-500'
          }`}
          onClick={() => onChange(t.key)}
        >
          {t.label}
        </button>
      ))}
    </div>
  )
}
