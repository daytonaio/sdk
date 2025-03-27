/**
 * Types for chart data extracted from matplotlib visualizations
 */

/**
 * Chart type enumeration matching the Python implementation
 */
export enum ChartType {
  LINE = 'line',
  SCATTER = 'scatter',
  BAR = 'bar',
  PIE = 'pie',
  BOX_AND_WHISKER = 'box_and_whisker',
  COMPOSITE_CHART = 'composite_chart',
  UNKNOWN = 'unknown',
}

/**
 * Base chart type
 */
export type Chart = {
  type: ChartType
  title: string
  elements: any[]
  png?: string
}

type Chart2D = Chart & {
  x_label?: string
  y_label?: string
}

export type PointData = {
  label: string
  points: [number | string, number | string][]
}

type PointChart = Chart2D & {
  x_ticks: (number | string)[]
  x_scale: string
  x_tick_labels: string[]
  y_ticks: (number | string)[]
  y_scale: string
  y_tick_labels: string[]
  elements: PointData[]
}

export type LineChart = PointChart & {
  type: ChartType.LINE
}

export type ScatterChart = PointChart & {
  type: ChartType.SCATTER
}

export type BarData = {
  label: string
  value: string
  group: string
}

export type BarChart = Chart2D & {
  type: ChartType.BAR
  elements: BarData[]
}

export type PieData = {
  label: string
  angle: number
  radius: number
}

export type PieChart = Chart & {
  type: ChartType.PIE
  elements: PieData[]
}

export type BoxAndWhiskerData = {
  label: string
  min: number
  first_quartile: number
  median: number
  third_quartile: number
  max: number
  outliers: number[]
}

export type BoxAndWhiskerChart = Chart2D & {
  type: ChartType.BOX_AND_WHISKER
  elements: BoxAndWhiskerData[]
}

export type CompositeChart = Chart & {
  type: ChartType.COMPOSITE_CHART
  elements: Chart[]
}

export function parseChart(data: any): Chart {
  switch (data.type) {
    case ChartType.LINE:
      return { ...data } as LineChart
    case ChartType.SCATTER:
      return { ...data } as ScatterChart
    case ChartType.BAR:
      return { ...data } as BarChart
    case ChartType.PIE:
      return { ...data } as PieChart
    case ChartType.BOX_AND_WHISKER:
      return { ...data } as BoxAndWhiskerChart
    case ChartType.COMPOSITE_CHART:
      const charts = data.elements.map((g: any) => parseChart(g))
      delete data.data
      return {
        ...data,
        data: charts,
      } as CompositeChart
    default:
      return { ...data, type: ChartType.UNKNOWN } as Chart
  }
}
