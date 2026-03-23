import ReactECharts from 'echarts-for-react'
import { TOOLTIP_STYLE } from '../lib/chart-theme'

export default function RingGauge({
  value,
  label,
  sublabel,
  color,
  size = 90,
  tooltipFormatter,
}) {
  const option = {
    tooltip: {
      ...TOOLTIP_STYLE,
      show: true,
      formatter: tooltipFormatter || (() => `${label}: ${value}%`),
    },
    series: [{
      type: 'gauge',
      startAngle: 90, endAngle: -270,
      radius: '98%', center: ['50%', '50%'],
      pointer: { show: false },
      progress: { show: true, overlap: false, roundCap: true, clip: false, itemStyle: { color } },
      axisLine: { lineStyle: { width: 6, color: [[1, '#f1f5f9']] } },
      splitLine: { show: false }, axisTick: { show: false }, axisLabel: { show: false },
      data: [{ value: Math.min(parseFloat(value), 100) }],
      title: { show: false },
      detail: { fontSize: 13, fontWeight: 700, color, offsetCenter: [0, 0], formatter: `${value}%` },
    }],
  }

  return (
    <div className="flex flex-col items-center gap-1">
      <ReactECharts option={option} style={{ width: size, height: size }} opts={{ renderer: 'svg' }} />
      <div className="text-center">
        <div className="text-[13px] font-medium text-neutral-700 leading-tight">{label}</div>
        {sublabel && <div className="text-xs text-neutral-400 tabular-nums">{sublabel}</div>}
      </div>
    </div>
  )
}
