from typing import Dict, Optional, List, Any, Union
from pydantic import BaseModel
from enum import Enum


class ChartType(str, Enum):
    """
    Chart types
    """

    LINE = "line"
    SCATTER = "scatter"
    BAR = "bar"
    PIE = "pie"
    BOX_AND_WHISKER = "box_and_whisker"
    COMPOSITE_CHART = "composite_chart"
    UNKNOWN = "unknown"


class Chart(BaseModel):
    """Represents a chart with metadata from matplotlib."""

    # All charts
    metadata: Dict[str, Any]
    type: Optional[ChartType] = None
    title: Optional[str] = None
    elements: Optional[List[Any]] = None

    # Line, Scatter, Bar, Box and Whisker charts
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    x_unit: Optional[str] = None
    y_unit: Optional[str] = None

    # Line, Scatter charts
    x_ticks: Optional[List[Union[str, float]]] = None
    x_tick_labels: Optional[List[str]] = None
    x_scale: Optional[str] = None
    y_ticks: Optional[List[Union[str, float]]] = None
    y_tick_labels: Optional[List[str]] = None
    y_scale: Optional[str] = None

    png: Optional[str] = None

    def __init__(self, **kwargs):
        """
        Initialize a Chart object.

        Args:
            metadata: Dictionary containing chart metadata
        """
        # Extract chart type
        chart_type = kwargs.get("type", ChartType.UNKNOWN)

        # Handle elements based on chart type
        elements = None
        if chart_type == ChartType.COMPOSITE_CHART:
            # For main charts, convert subplots to Chart objects
            subplots = kwargs.get("subplots", [])
            elements = [Chart(**subplot) for subplot in subplots]
        else:
            # For other charts, keep the elements as is (dicts with various structures)
            elements = kwargs.get("elements", None)

        # Call parent class constructor with all fields
        super().__init__(
            metadata=kwargs,
            type=ChartType(chart_type),
            title=kwargs.get("title"),
            elements=elements,
            x_label=kwargs.get("x_label"),
            y_label=kwargs.get("y_label"),
            x_ticks=kwargs.get("x_ticks"),
            x_tick_labels=kwargs.get("x_tick_labels"),
            x_scale=kwargs.get("x_scale"),
            y_ticks=kwargs.get("y_ticks"),
            y_tick_labels=kwargs.get("y_tick_labels"),
            y_scale=kwargs.get("y_scale"),
            png=kwargs.get("png")
        )

    def __str__(self):
        result = ''
        result += f'type: {self.type}\n'
        result += f'title: {self.title}\n'

        if self.type in [ChartType.LINE, ChartType.SCATTER, ChartType.BAR, ChartType.BOX_AND_WHISKER]:
            result += f'x_label: {self.x_label}\n'
            result += f'y_label: {self.y_label}\n'
            result += f'x_unit: {self.x_unit}\n'
            result += f'y_unit: {self.y_unit}\n'

        if self.type in [ChartType.LINE, ChartType.SCATTER]:
            result += f'x_ticks: {self.x_ticks}\n'
            result += f'x_tick_labels: {self.x_tick_labels}\n'
            result += f'x_scale: {self.x_scale}\n'
            result += f'y_ticks: {self.y_ticks}\n'
            result += f'y_tick_labels: {self.y_tick_labels}\n'
            result += f'y_scale: {self.y_scale}\n'
            result += f'elements:\n'
            for element in self.elements:
                result += '\n'
                result += f'* label: {element.get("label", None)}\n'
                result += f'* points: {element.get("points", None)}\n'
        elif self.type == ChartType.BAR:
            result += f'elements:\n'
            for bar in self.elements:
                result += '\n'
                result += f'* label: {bar.get("label", None)}\n'
                result += f'* group: {bar.get("group", None)}\n'
                result += f'* value: {bar.get("value", None)}\n'
        elif self.type == ChartType.PIE:
            result += f'elements:\n'
            for element in self.elements:
                result += '\n'
                result += f'* label: {element.get("label", None)}\n'
                result += f'* angle: {element.get("angle", None)}\n'
                result += f'* radius: {element.get("radius", None)}\n'
                result += f'* autopct: {element.get("autopct", None)}\n'
        elif self.type == ChartType.BOX_AND_WHISKER:
            result += f'elements:\n'
            for element in self.elements:
                result += '\n'
                result += f'* label: {element.get("label", None)}\n'
                result += f'* min: {element.get("min", None)}\n'
                result += f'* first_quartile: {element.get("first_quartile", None)}\n'
                result += f'* median: {element.get("median", None)}\n'
                result += f'* third_quartile: {element.get("third_quartile", None)}\n'
                result += f'* max: {element.get("max", None)}\n'
                result += f'* outliers: {element.get("outliers", None)}\n'
        elif self.type == ChartType.COMPOSITE_CHART:
            result += f'elements:\n'
            for element in self.elements:
                result += '\n'
                result += f'* {element}\n'
        return result
