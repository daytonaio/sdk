import matplotlib.pyplot as plt
import numpy as np
from matplotalt import infer_chart_type
from daytona_sdk import ChartType
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.collections import PathCollection
from matplotlib.text import Text
from matplotlib.patches import Wedge, Shadow

# Sample data
x = np.linspace(0, 10, 30)
y = np.sin(x)
categories = ['A', 'B', 'C', 'D', 'E']
values = [40, 63, 15, 25, 8]
box_data = [np.random.normal(0, std, 100) for std in range(1, 6)]

# 1. Line Chart
plt.figure(figsize=(8, 5))
plt.plot(x, y, 'b-', linewidth=2)
plt.plot(x, np.cos(x), 'r--', linewidth=2)  # Added line for cosine function
plt.title('Line Chart')
plt.xlabel('X-axis (seconds)')  # Added unit
plt.ylabel('Y-axis (amplitude)')  # Added unit
plt.grid(True)
# plt.show()

# 2. Scatter Plot
plt.figure(figsize=(8, 5))
plt.scatter(x, y, c=y, cmap='viridis', s=100*np.abs(y))
plt.colorbar(label='Value (normalized)')  # Added unit
plt.title('Scatter Plot')
plt.xlabel('X-axis (time in seconds)')  # Added unit
plt.ylabel('Y-axis (signal strength)')  # Added unit
# plt.show()

# 3. Bar Chart
plt.figure(figsize=(10, 6))
plt.bar(categories, values, color='skyblue', edgecolor='navy')
plt.title('Bar Chart')
plt.xlabel('Categories')  # No change (categories don't have units)
plt.ylabel('Values (count)')  # Added unit
# plt.show()

# 4. Pie Chart
plt.figure(figsize=(8, 8))
plt.pie(values, labels=categories,
        autopct='%1.1f%%',
        colors=plt.cm.Set3.colors, shadow=True, startangle=90)
plt.title('Pie Chart (Distribution in %)')  # Modified title
plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
plt.legend()
# plt.show()


# 5. Box and Whisker Plot
plt.figure(figsize=(10, 6))
plt.boxplot(box_data, patch_artist=True, 
            boxprops=dict(facecolor='lightblue'),
            medianprops=dict(color='red', linewidth=2))
plt.title('Box and Whisker Plot')
plt.xlabel('Groups (Experiment IDs)')  # Added unit
plt.ylabel('Values (measurement units)')  # Added unit
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()


def print_object_properties(obj, obj_name="Object"):
    """Prints all attributes of an object with their types."""
    print(f"\n{'='*40}")
    print(f"Properties of {obj_name} ({type(obj).__name__}):")
    
    for attr in dir(obj):
        if not attr.startswith("_"):  # Skip private/internal attributes
            try:
                value = getattr(obj, attr)
                print(f"  - {attr}: {type(value).__name__}")
            except Exception as e:
                print(f"  - {attr}: Could not retrieve ({str(e)})")


def is_grid_line(line: Line2D) -> bool:
    x_data = line.get_xdata()
    if len(x_data) != 2:
        return False

    y_data = line.get_ydata()
    if len(y_data) != 2:
        return False

    if x_data[0] == x_data[1] or y_data[0] == y_data[1]:
        return True

    return False


def get_type_of_chart(ax: Axes) -> ChartType:
    objects = list(filter(lambda obj: not isinstance(obj, Text) and not isinstance(obj, Shadow), ax._children))

    # Check for Line plots
    if all(isinstance(line, Line2D) for line in objects):
        return ChartType.LINE

    if all(isinstance(box_or_path, (PathPatch, Line2D)) for box_or_path in objects):
        return ChartType.BOX_AND_WHISKER

    filtered = []
    for obj in objects:
        if isinstance(obj, Line2D) and is_grid_line(obj):
            continue
        filtered.append(obj)

    objects = filtered

    # Check for Scatter plots
    if all(isinstance(path, PathCollection) for path in objects):
        return ChartType.SCATTER

    # Check for Bar plots
    if all(isinstance(rect, Rectangle) for rect in objects):
        return ChartType.BAR

    # Check for Pie plots
    if all(isinstance(artist, Wedge) for artist in objects):
        return ChartType.PIE

    return ChartType.UNKNOWN


all_figs = [manager.canvas.figure for manager in plt._pylab_helpers.Gcf.get_all_fig_managers()]

i=0
# Iterate over all figures
for fig in all_figs:
  i += 1
  # if i == 4:
  print(get_type_of_chart(fig.get_axes()[0]))
  # print(type(fig.get_axes()[0]))
  # print(isinstance(fig.get_axes()[0], plt.PolarAxes))
  # for child in fig.get_axes()[0]._children:
  #   print(type(child))
  # i = 0
  # print(len(fig.get_axes()))
  # for ax in fig.get_axes():
  #   print(f"Figure {fig.number} - Axis {i}")
  #   print(infer_chart_type(ax))
  #   i += 1
  #   break
  # print()

# print(get_type_of_chart(plt.gcf().get_axes()[0]))