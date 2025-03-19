#!/usr/bin/env python3
# This file contains the bootstrapper code for matplotlib interceptor
# It will be loaded and base64 encoded in the workspace_python_code_toolbox.py

# Standard library imports
import sys
import types
import base64
import json
import traceback
import linecache
import re
import io
import math
from importlib.abc import MetaPathFinder, Loader
from importlib.util import spec_from_loader, find_spec

# Flag to track if we've already patched matplotlib
plt_patched = False

# Set to track figure numbers that have been processed
processed_figures = set()


def extract_line_plot_data(ax):
    """Extract data from line plots"""
    elements = []

    # Get all lines - improve detection to find more possible line objects
    lines = ax.get_lines()

    # Process each line
    for line in lines:
        label = line.get_label()
        x_data = line.get_xdata()
        y_data = line.get_ydata()
        points = []

        for _, (x, y) in enumerate(zip(x_data, y_data)):
            points.append((x, y))

        element = {
            "label": label if label is not None else f"Line {len(elements) + 1}",
            "points": points
        }
        elements.append(element)

    return elements


def extract_box_plot_data(ax, xticklabels):
    """Extract data from box plots"""
    import matplotlib.pyplot as plt
    import math  # Use math instead of numpy
    import matplotlib.patches

    elements = []
    # Find all box plot elements
    boxes = [child for child in ax.get_children() if isinstance(
        child, matplotlib.patches.PathPatch)]
    whiskers = [child for child in ax.get_children() if isinstance(
        child, plt.Line2D) and child.get_linestyle() == '-']
    caps = [child for child in ax.get_children() if isinstance(
        child, plt.Line2D) and child.get_marker() == '_']
    medians = [child for child in ax.get_children() if isinstance(
        child, plt.Line2D) and child.get_linestyle() == '-' and (child.get_color() == 'orange' or child.get_color() == 'red')]
    fliers = [child for child in ax.get_children() if isinstance(
        child, plt.Line2D) and child.get_marker() == 'o']

    # Process each box plot
    for idx in range(len(boxes)):
        # Get statistical values
        box = boxes[idx]
        path = box.get_path()
        vertices = path.vertices

        # Box coordinates
        y_values = vertices[:, 1]  # Get all y-coordinates
        sorted_y = sorted(set(y_values))  # Remove duplicates and sort

        # Ensure we have enough values (at least 5 for min, q1, median, q3, max)
        if len(sorted_y) < 5:

            # If we can't extract from path vertices, try to find min and max from whiskers
            if idx < len(whiskers) // 2:
                lower_whisker = whiskers[idx*2]
                upper_whisker = whiskers[idx*2 + 1]

                y_min = float(min(lower_whisker.get_ydata()))
                y_max = float(max(upper_whisker.get_ydata()))

                # Get median from median line
                median_value = float(0.0)
                if idx < len(medians):
                    # Use average instead of numpy mean
                    y_data = medians[idx].get_ydata()
                    median_value = float(sum(y_data) / len(y_data))

                # Use approximated values for quartiles
                q1 = float(y_min + (median_value - y_min) / 2)
                q3 = float(median_value + (y_max - median_value) / 2)

                element = {
                    "label": xticklabels[idx] if idx < len(xticklabels) else f"Box {idx + 1}",
                    "min": y_min,
                    "first_quartile": q1,
                    "median": median_value,
                    "third_quartile": q3,
                    "max": y_max,
                    "outliers": []
                }
            else:
                continue
        else:
            # Extract statistical values
            element = {
                "label": xticklabels[idx] if idx < len(xticklabels) else f"Box {idx + 1}",
                "min": float(sorted_y[0]),  # Bottom whisker
                "first_quartile": float(sorted_y[1]),  # Bottom of box
                "median": float(sorted_y[2]),  # Median line
                "third_quartile": float(sorted_y[3]),  # Top of box
                "max": float(sorted_y[4]),  # Top whisker
                "outliers": []  # Will be populated if there are any
            }

        # Get outliers if any exist
        for flier in fliers:
            if flier.get_ydata() is not None:
                outliers = [float(y) for y in flier.get_ydata()]
                if outliers:
                    element["outliers"] = outliers
                    break

        elements.append(element)

    return elements


def extract_scatter_plot_data(ax):
    """Extract data from scatter plots"""
    import matplotlib.collections
    import matplotlib.pyplot as plt
    import matplotlib.cm
    import matplotlib.colors

    elements = []
    # Get all scatter plots
    scatters = [child for child in ax.get_children()
                if isinstance(child, matplotlib.collections.PathCollection)]

    # Process each scatter plot
    for idx, scatter in enumerate(scatters):
        # Get the scatter points
        offsets = scatter.get_offsets()
        if offsets is not None and len(offsets) > 0:
            # Convert to list if needed
            offsets = offsets.tolist() if hasattr(offsets, 'tolist') else list(offsets)

            # Ensure values are float for JSON serialization
            # Filter out any points with None or NaN values
            points = []
            for point in offsets:
                try:
                    x, y = point
                    if (x is not None and y is not None and
                        not (isinstance(x, float) and math.isnan(x)) and
                            not (isinstance(y, float) and math.isnan(y))):
                        points.append([float(x), float(y)])
                except (TypeError, ValueError):
                    # Skip invalid points
                    continue

            # Only proceed if we have valid points
            if points:
                # Try to get colormap information if available
                colors = None
                has_colorbar = False

                # Attempt to get array data for color mapping
                array_data = scatter.get_array()
                if array_data is not None and len(array_data) > 0:
                    has_colorbar = True
                    # Get the colormap if possible
                    cmap_name = "unknown"
                    if hasattr(scatter, "get_cmap") and scatter.get_cmap() is not None:
                        try:
                            cmap_name = scatter.get_cmap().name
                        except:
                            cmap_name = "unknown"

                    # Convert array data for JSON
                    array_data = array_data.tolist() if hasattr(
                        array_data, 'tolist') else list(array_data)
                    # Filter out None or NaN values
                    colors = []
                    for c in array_data:
                        if c is not None and not (isinstance(c, float) and math.isnan(c)):
                            colors.append(float(c))
                        else:
                            colors.append(0.0)  # Default color value

                # Get label, with fallback
                label = scatter.get_label()
                # Matplotlib uses '_' prefix for auto-generated labels
                if label is None or label.startswith('_'):
                    label = f"Scatter {idx + 1}"

                element = {
                    "label": label if label is not None else f"Scatter {idx + 1}",
                    "points": points
                }

                # Add color information if available
                if has_colorbar and colors and len(colors) == len(points):
                    element["colors"] = colors
                elif has_colorbar and colors:
                    # If color lengths don't match, truncate or extend
                    if len(colors) > len(points):
                        element["colors"] = colors[:len(points)]
                    else:
                        # Extend with defaults
                        element["colors"] = colors + [0.0] * \
                            (len(points) - len(colors))

                elements.append(element)

    return elements


def extract_bar_chart_data(ax, xticklabels):
    """Extract data from bar charts"""
    import matplotlib.pyplot as plt
    import matplotlib.patches

    elements = []
    # First look for standard Rectangle objects
    bars = [child for child in ax.get_children()
            if isinstance(child, plt.Rectangle) and hasattr(child, 'get_height') and child.get_height() > 0]

    # If no standard rectangles found, check for patch rectangles
    if len(bars) == 0:
        bars = [child for child in ax.get_children()
                if isinstance(child, matplotlib.patches.Rectangle) and hasattr(child, 'get_height') and child.get_height() > 0]

    # If we still don't have bars, look for patches that might be part of bar charts
    if len(bars) == 0:
        # In newer matplotlib versions, bars might be PathPatches without get_height method
        # In this case, try to get the patch vertices
        patches = [child for child in ax.get_children()
                   if isinstance(child, matplotlib.patches.PathPatch)]
        bar_like_patches = []

        for patch in patches:
            # Try to estimate if this patch is likely a bar
            path = patch.get_path()
            vertices = path.vertices
            if len(vertices) >= 4:  # Bars typically have at least 4 vertices
                # Check if the patch has a rectangular shape (approximate)
                xs = vertices[:, 0]
                ys = vertices[:, 1]
                width = max(xs) - min(xs)
                height = max(ys) - min(ys)

                if width > 0 and height > 0:
                    # Add a get_height method to the patch
                    patch.get_height = lambda: height
                    patch.y_base = min(ys)
                    bar_like_patches.append(patch)

        bars = bar_like_patches

    # Extract bar data
    raw_elements = []
    for idx, bar in enumerate(bars):
        # Try to get a meaningful label
        if idx < len(xticklabels):
            label = xticklabels[idx]
            # Ensure label is a string and not None
            if label is None:
                label = f"Bar {idx + 1}"
        else:
            label = f"Bar {idx + 1}"

        # Try to extract actual text from Text objects if needed
        if isinstance(label, str) and label.startswith("Text("):
            match = re.search(r"'([^']*)'", label)
            if match:
                label = match.group(1)
            else:
                # If no match is found, use a default label
                label = f"Bar {idx + 1}"

        # Get group/category if available
        group = bar.get_label()
        if group is None or not group or group.startswith('_'):
            group = "default"

        value = float(bar.get_height())
        # Ensure value is not None or NaN
        if value is None or (isinstance(value, float) and math.isnan(value)):
            value = 1.0

        element = {
            "label": label if label is not None else f"Bar {idx + 1}",
            "group": group if group is not None else "default",
            "value": value if value is not None else 1.0
        }
        raw_elements.append(element)

    # Filter out likely artifact bars:
    # 1. Bars with very small values (1.0) that are auto-labeled (Bar X)
    # 2. Default group
    elements = []
    for elem in raw_elements:
        # Skip likely artifact bars (those with value 1.0, label starting with "Bar", and default group)
        is_artifact = (
            abs(elem["value"] - 1.0) < 0.0001 and  # Value is 1.0
            isinstance(elem["label"], str) and
            elem["label"].startswith("Bar") and   # Auto-generated label
            elem["group"] == "default"            # Default group
        )

        if not is_artifact:
            elements.append(elem)

    return elements


def extract_pie_chart_data(ax):
    import matplotlib.pyplot as plt
    import matplotlib.patches

    elements = []

    wedges = [child for child in ax.get_children() if isinstance(child, matplotlib.patches.Wedge)]
    if len(wedges) == 0: return elements

    texts = [child.get_text() for child in ax.get_children()if isinstance(child, plt.Text)]
    texts = texts[:-3]

    labels = []
    autopcts = []

    if len(texts) == 2*len(wedges):
        labels = [texts[i] for i in range(0, 2 * len(wedges), 2)]
        autopcts = [texts[i] for i in range(1, 2 * len(wedges), 2)]
    else:
        labels = texts[:len(wedges)]

    for idx, wedge in enumerate(wedges):
        element = {
            "label": labels[idx],
            "angle": float(wedge.theta2 - wedge.theta1),
            "radius": float(wedge.r),
            "autopct": autopcts[idx] if autopcts else None
        }
        elements.append(element)

    return elements


def recreate_and_save_bar_chart(ax, elements, subplot_ax):
    """Recreate a bar chart in a new axis"""
    # Filter out zero values and any elements with default or numeric-only labels
    filtered_elements = []
    for elem in elements:
        # Skip elements with very small values
        if elem["value"] <= 1.0:
            continue

        # Skip elements with default group and numeric labels (likely artifacts)
        if elem["group"] == "default" and elem["label"].isdigit():
            continue

        # Skip elements with labels that start with "Text("
        # but extract the actual label if it's embedded
        if isinstance(elem["label"], str) and elem["label"].startswith("Text("):
            # Try to extract the actual label from the Text object representation
            match = re.search(r"'([^']*)'", elem["label"])
            if match:
                elem["label"] = match.group(1)

        filtered_elements.append(elem)

    if filtered_elements:
        # Use numeric positions for bars
        positions = list(range(len(filtered_elements)))
        labels = [elem["label"] for elem in filtered_elements]
        values = [elem["value"] for elem in filtered_elements]

        # Plot bars at numeric positions
        subplot_ax.bar(positions, values, color='blue')

        # Set the x-ticks and labels only at the bar positions
        subplot_ax.set_xticks(positions)
        subplot_ax.set_xticklabels(labels)

        # Set a slightly wider x limit to give some padding
        subplot_ax.set_xlim(-0.5, len(positions) - 0.5)
    else:
        # No valid elements after filtering
        subplot_ax.text(0.5, 0.5, "No valid data", ha='center', va='center')

    # Add legend if original plot had one
    if ax.get_legend():
        subplot_ax.legend()

    return subplot_ax


def recreate_and_save_scatter_plot(ax, elements, subplot_ax):
    """Recreate a scatter plot in a new axis"""
    for elem in elements:
        points = elem["points"]
        if points:  # Only process if there are actual points
            x_values = [point[0] for point in points]
            y_values = [point[1] for point in points]
            subplot_ax.scatter(x_values, y_values, label=elem["label"])

    if ax.get_legend():
        subplot_ax.legend()

    return subplot_ax


def recreate_and_save_line_plot(ax, elements, subplot_ax):
    """Recreate a line plot in a new axis"""
    for elem in elements:
        points = elem["points"]
        if points:  # Only process if there are actual points
            x_values = [point[0] for point in points]
            y_values = [point[1] for point in points]
            subplot_ax.plot(x_values, y_values, label=elem["label"])

    if ax.get_legend():
        subplot_ax.legend()

    return subplot_ax


def recreate_and_save_pie_chart(ax, elements, subplot_ax):
    """Recreate a pie chart in a new axis"""
    if elements:
        # Filter out very small slices (less than 1 degree)
        filtered_elements = [elem for elem in elements if elem["angle"] > 1.0]

        if filtered_elements:
            labels = [elem["label"] for elem in filtered_elements]
            angles = [elem["angle"] for elem in filtered_elements]
            subplot_ax.pie(angles, labels=labels, autopct='%1.1f%%')
        else:
            # Fallback if all slices were filtered out
            labels = [elem["label"] for elem in elements]
            angles = [elem["angle"] for elem in elements]
            subplot_ax.pie(angles, labels=labels, autopct='%1.1f%%')

    return subplot_ax


def copy_axis_properties(source_ax, target_ax):
    """Copy axis properties from one axis to another"""
    # Copy title and labels
    target_ax.set_title(source_ax.get_title())
    target_ax.set_xlabel(source_ax.get_xlabel())
    target_ax.set_ylabel(source_ax.get_ylabel())

    # Copy scales
    target_ax.set_xscale(source_ax.get_xscale())
    target_ax.set_yscale(source_ax.get_yscale())

    # Copy ticks and tick labels
    target_ax.set_xticks(source_ax.get_xticks())
    target_ax.set_yticks(source_ax.get_yticks())
    target_ax.set_xticklabels(source_ax.get_xticklabels())
    target_ax.set_yticklabels(source_ax.get_yticklabels())

    return target_ax


def save_figure_as_base64(fig, bbox_inches='tight', dpi=100):
    """Save a figure as a base64-encoded PNG string"""
    png_buffer = io.BytesIO()
    fig.savefig(png_buffer, format='png', bbox_inches=bbox_inches, dpi=dpi)
    png_buffer.seek(0)
    return base64.b64encode(png_buffer.getvalue()).decode('utf-8')


def is_grid_line(line: any) -> bool:
    x_data = line.get_xdata()
    if len(x_data) != 2:
        return False

    y_data = line.get_ydata()
    if len(y_data) != 2:
        return False

    if x_data[0] == x_data[1] or y_data[0] == y_data[1]:
        return True

    return False


def get_chart_type(ax):
    from matplotlib.lines import Line2D
    from matplotlib.patches import PathPatch, Rectangle
    from matplotlib.collections import PathCollection
    from matplotlib.text import Text
    from matplotlib.patches import Wedge, Shadow

    objects = list(filter(lambda obj: not isinstance(obj, Text) and not isinstance(obj, Shadow), ax._children))

    # Check for Line plots
    if all(isinstance(line, Line2D) for line in objects):
        return "line"

    if all(isinstance(box_or_path, (PathPatch, Line2D)) for box_or_path in objects):
        return "box_and_whisker"

    filtered = []
    for obj in objects:
        if isinstance(obj, Line2D) and is_grid_line(obj):
            continue
        filtered.append(obj)

    objects = filtered

    # Check for Scatter plots
    if all(isinstance(path, PathCollection) for path in objects):
        return "scatter"

    # Check for Bar plots
    if all(isinstance(rect, Rectangle) for rect in objects):
        return "bar"

    # Check for Pie plots
    if all(isinstance(artist, Wedge) for artist in objects):
        return "pie"

    return "unknown"


def filter_out_colorbar_axes(axes):
    import matplotlib.colorbar
    return [ax for ax in axes if not any(isinstance(child, matplotlib.colorbar._ColorbarSpine) for child in ax.get_children())]


def extract_chart_data(ax):
    subplot_data = {}

    # Title and labels
    if ax.get_title():
        subplot_data["title"] = ax.get_title()
    if ax.get_xlabel():
        subplot_data["x_label"] = ax.get_xlabel()
    if ax.get_ylabel():
        subplot_data["y_label"] = ax.get_ylabel()

    # Add X and Y units - extract from labels if possible
    subplot_data["x_unit"] = "None"  # Default value
    subplot_data["y_unit"] = "None"  # Default value

    # Try to extract units from axis labels if they contain parentheses
    if ax.get_xlabel():
        x_unit_match = re.search(r'\((.*?)\)', ax.get_xlabel())
        if x_unit_match:
            subplot_data["x_unit"] = x_unit_match.group(1)

    if ax.get_ylabel():
        y_unit_match = re.search(r'\((.*?)\)', ax.get_ylabel())
        if y_unit_match:
            subplot_data["y_unit"] = y_unit_match.group(1)

    # Scale types
    subplot_data["x_scale"] = ax.get_xscale()
    subplot_data["y_scale"] = ax.get_yscale()

    # Ticks and tick labels
    xticks = ax.get_xticks()
    yticks = ax.get_yticks()

    # Get tick labels, handling different matplotlib versions
    try:
        xticklabels = [label.get_text() if hasattr(label, 'get_text') else str(label)
                        for label in ax.get_xticklabels()]
        yticklabels = [label.get_text() if hasattr(label, 'get_text') else str(label)
                        for label in ax.get_yticklabels()]
    except:
        # Fallback to simpler method
        xticklabels = [str(label) for label in ax.get_xticklabels()]
        yticklabels = [str(label) for label in ax.get_yticklabels()]

    # Convert to list if needed and ensure all values are JSON serializable
    try:
        subplot_data["x_ticks"] = [float(x) for x in (
            xticks.tolist() if hasattr(xticks, 'tolist') else list(xticks))]
        subplot_data["y_ticks"] = [float(y) for y in (
            yticks.tolist() if hasattr(yticks, 'tolist') else list(yticks))]
    except (ValueError, TypeError) as e:
        subplot_data["x_ticks"] = list(range(len(xticklabels)))
        subplot_data["y_ticks"] = list(range(len(yticklabels)))

    subplot_data["x_tick_labels"] = xticklabels
    subplot_data["y_tick_labels"] = yticklabels

    # Try to determine chart type and extract elements data
    chart_type = get_chart_type(ax)
    elements = []
    
    if chart_type == "line":
        elements = extract_line_plot_data(ax)
    elif chart_type == "scatter":
        elements = extract_scatter_plot_data(ax)
    elif chart_type == "bar":
        elements = extract_bar_chart_data(ax, xticklabels)
    elif chart_type == "box_and_whisker":
        elements = extract_box_plot_data(ax, xticklabels)
    elif chart_type == "pie":
        elements = extract_pie_chart_data(ax)
        
    # Continue with empty elements if extraction fails
    subplot_data["type"] = chart_type
    if elements:  # Only add elements if we have any
        subplot_data["elements"] = elements

    return subplot_data

def extract_and_print_figure_metadata(fig):
    """Extract metadata from a matplotlib figure and print as JSON"""
    import matplotlib.pyplot as plt
    import json

    metadata = {}
    subplots = []

    for ax in filter_out_colorbar_axes(fig.axes):
        subplot_data = extract_chart_data(ax)
        subplots.append(subplot_data)

    metadata_png = save_figure_as_base64(fig)

    # Count actual plot axes (excluding colorbars)
    actual_plot_axes = 0
    for ax in fig.axes:
        # Skip colorbar axes
        is_colorbar_axis = False
        try:
            if hasattr(ax, 'get_aspect') and ax.get_aspect() == 20.0:
                is_colorbar_axis = True
            if hasattr(ax, '_axes') and hasattr(ax._axes, 'colorbar'):
                is_colorbar_axis = True
            for child in ax.get_children():
                if str(type(child).__name__).lower().find('colorbar') >= 0:
                    is_colorbar_axis = True
                    break
        except:
            pass
        
        if is_colorbar_axis:
            print(f"colorbar: {ax}")
            print("children: ", ax.get_children())
        if not is_colorbar_axis:
            actual_plot_axes += 1

    # Create the final metadata structure
    if actual_plot_axes > 1:
        # Multiple actual subplots - create a main chart
        metadata = {
            # Try to get figure suptitle
            "title": fig.texts[0].get_text() if fig.texts else None,
            "type": "composite_chart",  # Reverted to snake_case
            "png": metadata_png,
            "subplots": subplots
        }
    else:
        # Single plot (possibly with colorbars) - use the subplot data directly
        # Find the non-colorbar subplot
        for subplot in subplots:
            if subplot.get("type") != "unknown":
                metadata = subplot
                metadata["png"] = metadata_png
                break
        else:
            # Fallback if no valid subplot found
            metadata = subplots[0] if subplots else {"type": "unknown"}
            metadata["png"] = metadata_png

    # Print metadata in the specified JSON format
    json_output = {
        "type": "chart",
        "value": metadata
    }

    # if metadata.get("type") == "line":
    #     metadata_copy = metadata.copy()  # Create a copy of metadata
    #     metadata_copy.pop("png", None)  # Remove the png property
    #     print(f"line: {metadata_copy}")

    print(f"dtn_artifact:{json.dumps(json_output)}")


class MatplotlibFinder(MetaPathFinder):
    """Custom finder to intercept matplotlib.pyplot imports"""

    def find_spec(self, fullname, path, target=None):
        global plt_patched

        # Only intercept matplotlib.pyplot
        if fullname == 'matplotlib.pyplot' and not plt_patched:
            # Mark as patched to prevent recursion
            plt_patched = True

            # Find the original spec
            original_spec = find_spec(fullname)
            if original_spec is None:
                return None

            # Create a spec with our loader
            return spec_from_loader(
                fullname,
                MatplotlibLoader(original_spec.loader),
                origin=original_spec.origin,
                is_package=original_spec.submodule_search_locations is not None
            )
        return None


class MatplotlibLoader(Loader):
    """Custom loader to patch the matplotlib.pyplot module"""

    def __init__(self, original_loader):
        self.original_loader = original_loader

    def create_module(self, spec):
        # Let the original loader create the module
        return self.original_loader.create_module(spec)

    def exec_module(self, module):
        # First execute the real module
        self.original_loader.exec_module(module)

        # Now patch the show function
        if hasattr(module, 'show'):
            # Store the original show function
            original_show = module.show

            # Define our custom show function
            def custom_show(*args, **kwargs):
                global processed_figures

                # Get all current figure numbers
                fig_nums = module.get_fignums()

                # Check for new figures
                for fig_num in fig_nums:
                    if fig_num not in processed_figures:
                        # This is a new figure, process it
                        fig = module.figure(fig_num)
                        extract_and_print_figure_metadata(fig)

                        # Mark as processed
                        processed_figures.add(fig_num)

                # Call the original show function with all arguments
                return original_show(*args, **kwargs)

            # Replace the show function with our custom version
            module.show = custom_show


def setup_user_code_environment(code):
    """Set up the module to run user code in"""
    module = types.ModuleType('__main__')
    module.__file__ = '<user_code>'
    sys.modules['__main__'] = module

    # Add code to line cache for better tracebacks
    code_lines = code.splitlines()
    linecache.cache['<user_code>'] = (
        len(code),
        None,
        code_lines,
        '<user_code>'
    )

    return module


def run_user_code(code):
    """Run the user code with the matplotlib interceptor installed"""
    # Install matplotlib interceptor
    sys.meta_path.insert(0, MatplotlibFinder())

    # Set up clean environment for user code
    module = setup_user_code_environment(code)

    # Compile and run the code
    compiled = compile(code, '<user_code>', 'exec')

    # Execute in the module's namespace
    exec(compiled, module.__dict__)


if __name__ == '__main__':
    try:
        # Get the encoded user code
        user_code = base64.b64decode("{encoded_code}").decode()

        # Run the code
        run_user_code(user_code)
    except Exception:
        # Print only the relevant parts of the traceback
        exc_type, exc_value, exc_tb = sys.exc_info()

        # Filter traceback to only show user code frames
        filtered_tb = []
        tb = exc_tb
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == '<user_code>':
                filtered_tb.append(tb)
            tb = tb.tb_next

        if filtered_tb:
            # Create a new traceback from the filtered frames
            exc_value.__traceback__ = filtered_tb[-1]
            traceback.print_exception(
                exc_type, exc_value, exc_value.__traceback__)
        else:
            # Fallback if no user code frames found - raise the original exception type
            # with the original message but create a fresh traceback
            raise exc_type(str(exc_value)) from None

        sys.exit(1)
