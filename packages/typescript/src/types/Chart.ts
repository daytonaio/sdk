/**
 * Types for chart data extracted from matplotlib visualizations
 */

/**
 * Chart type enumeration matching the Python implementation
 */
export enum ChartType {
  LINE = "line",
  SCATTER = "scatter",
  BAR = "bar",
  PIE = "pie",
  BOX_AND_WHISKER = "box_and_whisker",
  COMPOSITE_CHART = "composite_chart",
  UNKNOWN = "unknown"
}

/**
 * Unified Chart interface that matches the Python Chart class.
 * This is a generic representation of any chart type.
 */
export interface Chart {
  /**
   * The original metadata from the chart
   */
  metadata: Record<string, any>;
  
  /**
   * The type of chart
   */
  type?: ChartType;
  
  /**
   * The title of the chart
   */
  title?: string;
  
  /**
   * Elements/components in the chart (varies by chart type)
   * For composite charts, this contains sub-charts
   * For other charts, this contains data elements like bars, points, etc.
   */
  elements?: any[];
  
  /**
   * X-axis label
   */
  x_label?: string;
  
  /**
   * Y-axis label
   */
  y_label?: string;
  
  /**
   * X-axis unit
   */
  x_unit?: string;
  
  /**
   * Y-axis unit
   */
  y_unit?: string;
  
  /**
   * X-axis tick values
   */
  x_ticks?: Array<string | number>;
  
  /**
   * X-axis tick labels
   */
  x_tick_labels?: string[];
  
  /**
   * X-axis scale type (e.g., "linear", "log")
   */
  x_scale?: string;
  
  /**
   * Y-axis tick values
   */
  y_ticks?: Array<string | number>;
  
  /**
   * Y-axis tick labels
   */
  y_tick_labels?: string[];
  
  /**
   * Y-axis scale type (e.g., "linear", "log")
   */
  y_scale?: string;
  
  /**
   * Base64-encoded PNG image of the chart
   */
  png?: string;
}