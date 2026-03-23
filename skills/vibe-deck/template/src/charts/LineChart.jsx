import ReactECharts from 'echarts-for-react'
import { TOOLTIP_STYLE, CHART_COLORS } from '../lib/chart-theme'

export default function LineChart({
  categories,
  series,
  height = '100%',
  smooth = false,
  showArea = false,
  showLabel = true,
  yAxisFormatter,
}) {
  const option = {
    tooltip: {
      ...TOOLTIP_STYLE,
      trigger: 'axis',
    },
    grid: { left: 16, right: 16, top: 24, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { fontSize: 12 },
      axisTick: { show: false },
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 11,
        ...(yAxisFormatter ? { formatter: yAxisFormatter } : {}),
      },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
    },
    series: series.map((s, i) => ({
      type: 'line',
      name: s.name,
      data: s.data,
      smooth,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: s.color || CHART_COLORS[i % CHART_COLORS.length], width: 2 },
      itemStyle: { color: s.color || CHART_COLORS[i % CHART_COLORS.length] },
      label: {
        show: showLabel,
        fontSize: 11,
        fontWeight: 600,
      },
      ...(showArea ? {
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: (s.color || CHART_COLORS[i % CHART_COLORS.length]) + '30' },
              { offset: 1, color: (s.color || CHART_COLORS[i % CHART_COLORS.length]) + '05' },
            ],
          },
        },
      } : {}),
    })),
    ...(series.length > 1 ? {
      legend: {
        top: 0,
        textStyle: { fontSize: 11 },
      },
    } : {}),
  }

  return <ReactECharts option={option} style={{ height }} />
}
