import ReactEChartsCore from 'echarts-for-react'
import { TOOLTIP_STYLE, CHART_COLORS } from '../lib/chart-theme'

export default function PieChart({
  data,
  height = '100%',
  showLabel = true,
  radius = ['40%', '70%'],
}) {
  const option = {
    tooltip: {
      ...TOOLTIP_STYLE,
      trigger: 'item',
      formatter: (p) => `${p.name}<br/>${p.value} (${p.percent}%)`,
    },
    series: [{
      type: 'pie',
      radius,
      label: {
        show: showLabel,
        fontSize: 12,
        overflow: 'break',
        formatter: (p) => `${p.name}\n${p.value} · ${p.percent}%`,
      },
      data: data.map((d, i) => ({
        ...d,
        itemStyle: { color: d.color || CHART_COLORS[i % CHART_COLORS.length] },
      })),
    }],
  }

  return <ReactEChartsCore option={option} style={{ height }} />
}
