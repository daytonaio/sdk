import { Chart, ChartType } from '../types/Chart';
import { ExecutionArtifacts } from '../types/ExecuteResponse';

/**
 * Utility class for parsing artifacts from command output
 */
export class ArtifactParser {
  /**
   * Parses artifacts from command output text
   * 
   * @param output - Raw output from command execution
   * @returns Parsed artifacts including stdout and charts
   */
  public static parseArtifacts(output: string): ExecutionArtifacts {
    const charts: Chart[] = [];
    let stdout = output;

    // Split output by lines to find artifact markers
    const lines = output.split('\n');
    const artifactLines: string[] = [];
    
    for (const line of lines) {
      // Look for the artifact marker pattern
      if (line.startsWith('dtn_artifact:')) {
        artifactLines.push(line);
        
        try {
          const artifactJson = line.substring('dtn_artifact:'.length).trim();
          const artifactData = JSON.parse(artifactJson);
          
          if (artifactData.type === 'chart' && artifactData.value) {
            const chartData = artifactData.value;
            
            // Create a Chart object
            const chart: Chart = {
              metadata: chartData,
              type: chartData.type as ChartType || ChartType.UNKNOWN,
              title: chartData.title,
              elements: chartData.elements || 
                       (chartData.type === ChartType.COMPOSITE_CHART
                        ? chartData.subplots?.map((subplot: any) => this.createChartFromData(subplot)) 
                        : undefined),
              x_label: chartData.x_label,
              y_label: chartData.y_label,
              x_ticks: chartData.x_ticks,
              x_tick_labels: chartData.x_tick_labels,
              x_scale: chartData.x_scale,
              y_ticks: chartData.y_ticks,
              y_tick_labels: chartData.y_tick_labels,
              y_scale: chartData.y_scale,
              png: chartData.png
            };
            
            charts.push(chart);
          }
        } catch (error) {
          // Skip invalid artifacts
          console.warn('Failed to parse artifact:', error);
        }
      }
    }
    
    // Remove artifact lines from stdout along with their following newlines
    for (const line of artifactLines) {
      stdout = stdout.replace(line + '\n', '');
      stdout = stdout.replace(line, '');
    }
    
    return {
      stdout,
      charts: charts.length > 0 ? charts : undefined
    };
  }
  
  /**
   * Creates a Chart object from chart data
   * 
   * @param chartData - Raw chart data
   * @returns A Chart object
   */
  private static createChartFromData(chartData: any): Chart {
    return {
      metadata: chartData,
      type: chartData.type as ChartType || ChartType.UNKNOWN,
      title: chartData.title,
      elements: chartData.elements,
      x_label: chartData.x_label,
      y_label: chartData.y_label,
      x_ticks: chartData.x_ticks,
      x_tick_labels: chartData.x_tick_labels,
      x_scale: chartData.x_scale,
      y_ticks: chartData.y_ticks,
      y_tick_labels: chartData.y_tick_labels,
      y_scale: chartData.y_scale,
      png: chartData.png
    };
  }
} 