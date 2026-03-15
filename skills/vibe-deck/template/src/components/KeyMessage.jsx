import { colors } from '../theme'

export default function KeyMessage({ children, label = 'Key Message' }) {
  return (
    <div className="flex items-stretch">
      {/* 蓝色标签 + 箭头作为一个整体 SVG，避免拼接缝隙 */}
      <div className="shrink-0 relative" style={{ width: 96 }}>
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 96 100" preserveAspectRatio="none">
          <path d="M6,0 H80 L96,50 L80,100 H6 Q0,100 0,94 V6 Q0,0 6,0 Z" fill={colors.primaryDark} />
        </svg>
        <span className="relative z-10 flex items-center justify-center h-full text-white text-[14px] font-bold leading-tight text-center px-3 pr-6">
          {label}
        </span>
      </div>
      <div className="bg-neutral-100/80 pl-8 pr-4 py-2 space-y-0.5 text-[14px] leading-relaxed rounded-r-lg flex-1 flex flex-col justify-center font-medium text-neutral-700 -ml-[16px]">
        {children}
      </div>
    </div>
  )
}
