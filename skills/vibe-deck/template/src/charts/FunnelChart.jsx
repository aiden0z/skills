import ReactEChartsCore from 'echarts-for-react'
import { TOOLTIP_STYLE, CHART_COLORS } from '../lib/chart-theme'

export default function FunnelChart({
  tiers,
  height = '100%',
  showBottomLabel,
}) {
  const option = {
    tooltip: {
      ...TOOLTIP_STYLE,
      trigger: 'item',
      formatter: (p) => `${p.name}<br/>数量: <b>${tiers[p.dataIndex].value}</b>`,
    },
    series: [{
      type: 'funnel',
      left: '5%', right: '5%', top: '6%', bottom: showBottomLabel ? '14%' : '6%',
      width: '80%', minSize: '20%', maxSize: '100%',
      sort: 'descending', gap: 4,
      label: {
        show: true, position: 'inside', fontSize: 12, fontWeight: 600, color: '#fff',
        formatter: (p) => `${tiers[p.dataIndex].name}\n${tiers[p.dataIndex].value}`,
      },
      labelLine: { show: false },
      itemStyle: { borderWidth: 0 },
      data: tiers.map((t, i) => ({
        name: t.name,
        value: t.value,
        itemStyle: { color: t.color || CHART_COLORS[i % CHART_COLORS.length] },
      })),
    }],
    ...(showBottomLabel ? {
      graphic: [{
        type: 'text', left: 'center', bottom: 2,
        style: { text: showBottomLabel.text, fontSize: 13, fontWeight: 700, fill: showBottomLabel.color },
      }],
    } : {}),
  }

  return <ReactEChartsCore option={option} style={{ height }} />
}
