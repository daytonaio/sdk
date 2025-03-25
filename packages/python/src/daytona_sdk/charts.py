from enum import Enum
from typing import Any, List, Optional, Tuple, Union


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


class Chart:
    """Represents a chart with metadata from matplotlib."""

    type: ChartType
    title: str
    elements: List[Any]
    png: Optional[str] = None

    def __init__(self, **kwargs):
        """
        Initialize a Chart object.

        Args:
            kwargs: Dictionary containing chart metadata
        """
        super().__init__()
        self._metadata = kwargs
        self.type = kwargs.get("type")
        self.title = kwargs.get("title")
        self.elements = kwargs.get("elements", [])
        self.png = kwargs.get("png")

    def to_dict(self):
        return self._metadata


class Chart2D(Chart):
    x_label: Optional[str]
    y_label: Optional[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x_label = kwargs.get("x_label")
        self.y_label = kwargs.get("y_label")


class PointData:
    label: str
    points: List[Tuple[Union[str, float], Union[str, float]]]

    def __init__(self, **kwargs):
        self.label = kwargs["label"]
        self.points = list(kwargs["points"])


class PointChart(Chart2D):
    x_ticks: List[Union[str, float]]
    x_tick_labels: List[str]
    x_scale: str

    y_ticks: List[Union[str, float]]
    y_tick_labels: List[str]
    y_scale: str

    elements: List[PointData]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x_label = kwargs.get("x_label")
        self.x_scale = kwargs.get("x_scale")
        self.x_ticks = kwargs.get("x_ticks")
        self.x_tick_labels = kwargs.get("x_tick_labels")

        self.y_label = kwargs.get("y_label")
        self.y_scale = kwargs.get("y_scale")
        self.y_ticks = kwargs.get("y_ticks")
        self.y_tick_labels = kwargs.get("y_tick_labels")

        self.elements = [PointData(**d) for d in kwargs.get("elements", [])]


class LineChart(PointChart):
    type: ChartType = ChartType.LINE


class ScatterChart(PointChart):
    type: ChartType = ChartType.SCATTER


class BarData:
    label: str
    group: str
    value: str

    def __init__(self, **kwargs):
        self.label = kwargs.get("label")
        self.value = kwargs.get("value")
        self.group = kwargs.get("group")


class BarChart(Chart2D):
    type: ChartType = ChartType.BAR

    elements: List[BarData]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements = [BarData(**element) for element in kwargs.get("elements", [])]


class PieData:
    label: str
    angle: float
    radius: float
    autopct: float

    def __init__(self, **kwargs):
        self.label = kwargs.get("label")
        self.angle = kwargs.get("angle")
        self.radius = kwargs.get("radius")
        self.autopct = kwargs.get("autopct")


class PieChart(Chart):
    type: ChartType = ChartType.PIE

    elements: List[PieData]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements = [PieData(**element) for element in kwargs.get("elements", [])]


class BoxAndWhiskerData:
    label: str
    min: float
    first_quartile: float
    median: float
    third_quartile: float
    max: float
    outliers: List[float]

    def __init__(self, **kwargs):
        self.label = kwargs.get("label")
        self.min = kwargs.get("min")
        self.first_quartile = kwargs.get("first_quartile")
        self.median = kwargs.get("median")
        self.third_quartile = kwargs.get("third_quartile")
        self.max = kwargs.get("max")
        self.outliers = kwargs.get("outliers", [])


class BoxAndWhiskerChart(Chart2D):
    type: ChartType = ChartType.BOX_AND_WHISKER

    elements: List[BoxAndWhiskerData]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements = [BoxAndWhiskerData(**element) for element in kwargs.get("elements", [])]


class CompositeChart(Chart):
    type: ChartType = ChartType.COMPOSITE_CHART

    elements: List[Chart]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements = [parse_chart(**element) for element in kwargs.get("elements", [])]


def parse_chart(**kwargs) -> Optional[Chart]:
    if not kwargs:
        return None

    chart_type = ChartType(kwargs.get("type", ChartType.UNKNOWN))

    match chart_type:
        case ChartType.LINE:
            return LineChart(**kwargs)
        case ChartType.SCATTER:
            return ScatterChart(**kwargs)
        case ChartType.BAR:
            return BarChart(**kwargs)
        case ChartType.PIE:
            return PieChart(**kwargs)
        case ChartType.BOX_AND_WHISKER:
            return BoxAndWhiskerChart(**kwargs)
        case ChartType.COMPOSITE_CHART:
            return CompositeChart(**kwargs)
        case _:
            return Chart(**kwargs)
