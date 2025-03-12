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

    metadata: Dict[str, Any]
    type: Optional[ChartType] = None
    title: Optional[str] = None

    elements: Optional[List[Any]] = None

    x_label: Optional[str] = None
    y_label: Optional[str] = None
    x_unit: Optional[str] = None
    y_unit: Optional[str] = None

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
