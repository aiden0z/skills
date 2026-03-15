import ReactEChartsCore from 'echarts-for-react'
import { TOOLTIP_STYLE, CHART_COLORS } from '../lib/chart-theme'

export default function BarChart({
  data,
  height = '100%',
  horizontal = false,
  barWidth = '50%',
  showLabel = true,
}) {
  const categories = data.map(d => d.name)
  const values = data.map((d, i) => ({
    value: d.value,
    itemStyle: { color: d.color || CHART_COLORS[i % CHART_COLORS.length] },
  }))

  const categoryAxis = {
    type: 'category',
    data: categories,
    axisLabel: { fontSize: 12 },
    axisTick: { show: false },
  }
  const valueAxis = {
    type: 'value',
    axisLabel: { fontSize: 11 },
    splitLine: { lineStyle: { color: '#f3f4f6' } },
  }

  const option = {
    tooltip: {
      ...TOOLTIP_STYLE,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    grid: { left: 16, right: 16, top: 20, bottom: 8, containLabel: true },
    xAxis: horizontal ? valueAxis : categoryAxis,
    yAxis: horizontal ? categoryAxis : valueAxis,
    series: [{
      type: 'bar',
      data: values,
      barWidth,
      label: {
        show: showLabel,
        position: horizontal ? 'right' : 'top',
        fontSize: 12,
        fontWeight: 600,
      },
    }],
  }

  return <ReactEChartsCore option={option} style={{ height }} />
}
