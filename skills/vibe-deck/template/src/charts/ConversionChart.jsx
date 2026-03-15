import ReactEChartsCore from 'echarts-for-react'
import { TOOLTIP_STYLE } from '../lib/chart-theme'
import { colors } from '../theme'

export default function ConversionChart({
  categories,
  countData,
  rateData,
  rateName = '转化率',
  height = '100%',
}) {
  const option = {
    tooltip: { ...TOOLTIP_STYLE, trigger: 'axis' },
    grid: { left: 50, right: 50, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } },
    yAxis: [
      { type: 'value', name: '数量', axisLabel: { fontSize: 11 } },
      { type: 'value', name: rateName, axisLabel: { fontSize: 11, formatter: '{value}%' }, max: 100 },
    ],
    series: [
      ...countData.map(s => ({
        type: 'bar',
        name: s.name,
        data: s.data,
        itemStyle: { color: s.color },
        label: { show: true, position: 'top', fontSize: 11 },
      })),
      {
        type: 'line',
        name: rateName,
        data: rateData,
        yAxisIndex: 1,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: colors.accent, width: 2 },
        itemStyle: { color: colors.accent },
        label: { show: true, formatter: '{c}%', fontSize: 11 },
      },
    ],
  }

  return <ReactEChartsCore option={option} style={{ height }} />
}
