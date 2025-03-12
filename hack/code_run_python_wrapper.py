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
from importlib.abc import MetaPathFinder, Loader
from importlib.util import spec_from_loader, find_spec

# Flag to track if we've already patched matplotlib
plt_patched = False

# Set to track figure numbers that have been processed
processed_figures = set()


def extract_box_plot_data(ax, xticklabels):
    """Extract data from box plots"""
    import matplotlib.pyplot as plt

    elements = []
    # Find all box plot elements
    boxes = [child for child in ax.get_children() if isinstance(
        child, plt.matplotlib.patches.PathPatch)]
    whiskers = [child for child in ax.get_children() if isinstance(
        child, plt.Line2D) and child.get_linestyle() == '-']
    medians = [child for child in ax.get_children() if isinstance(
        child, plt.Line2D) and child.get_linestyle() == '-' and child.get_color() == 'orange']
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

        # Extract statistical values
        element = {
            "label": xticklabels[idx] if idx < len(xticklabels) else f"Box {idx + 1}",
            "min": sorted_y[0],  # Bottom whisker
            "first_quartile": sorted_y[1],  # Bottom of box
            "median": sorted_y[2],  # Median line
            "third_quartile": sorted_y[3],  # Top of box
            "max": sorted_y[4],  # Top whisker
            "outliers": []  # Will be populated if there are any
        }

        # Get outliers if any exist
        if idx < len(fliers):
            flier = fliers[idx]
            if flier.get_ydata() is not None:
                element["outliers"] = list(flier.get_ydata())

        elements.append(element)

    return elements


def extract_line_plot_data(ax):
    """Extract data from line plots"""
    import matplotlib.pyplot as plt

    elements = []
    # Get all lines
    lines = [child for child in ax.get_children(
    ) if isinstance(child, plt.Line2D)]

    # Process each line
    for line in lines:
        # Skip lines that are part of other plot types (like box plot whiskers)
        if line.get_linestyle() == '-' and not any(isinstance(child, plt.matplotlib.patches.PathPatch) for child in ax.get_children()):
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            # Convert to list if needed
            x_data = x_data.tolist() if hasattr(x_data, 'tolist') else list(x_data)
            y_data = y_data.tolist() if hasattr(y_data, 'tolist') else list(y_data)
            points = [[float(x), float(y)] for x, y in zip(x_data, y_data)]
            element = {
                "label": line.get_label() or f"Line {len(elements) + 1}",
                "points": points
            }
            elements.append(element)

    return elements


def extract_scatter_plot_data(ax):
    """Extract data from scatter plots"""
    import matplotlib.collections

    elements = []
    # Get all scatter plots
    scatters = [child for child in ax.get_children()
                if isinstance(child, matplotlib.collections.PathCollection)]

    # Process each scatter plot
    for scatter in scatters:
        offsets = scatter.get_offsets()
        # Convert to list if needed
        offsets = offsets.tolist() if hasattr(offsets, 'tolist') else list(offsets)
        points = [[float(x), float(y)] for x, y in offsets]
        element = {
            "label": scatter.get_label() or f"Scatter {len(elements) + 1}",
            "points": points
        }
        elements.append(element)

    return elements


def extract_bar_chart_data(ax, xticklabels):
    """Extract data from bar charts"""
    import matplotlib.pyplot as plt

    elements = []
    # Get all bars from the axis
    bars = [child for child in ax.get_children()
            if isinstance(child, plt.Rectangle) and child.get_height() > 0]

    # Extract bar data
    for idx, bar in enumerate(bars):
        # Only add elements if there's a corresponding label
        if idx < len(xticklabels):
            element = {
                "label": xticklabels[idx],
                "group": bar.get_label() or "default",
                "value": float(bar.get_height())
            }
            elements.append(element)

    return elements


def extract_pie_chart_data(ax):
    """Extract data from pie charts"""
    import matplotlib.pyplot as plt

    elements = []
    # Get all wedges from the axis
    wedges = [child for child in ax.get_children(
    ) if isinstance(child, plt.Wedge)]
    texts = [child for child in ax.get_children() if isinstance(
        child, plt.Text) and child.get_text()]

    # Extract pie data
    for idx, wedge in enumerate(wedges):
        # Get the label from the text objects if available
        label = texts[idx].get_text() if idx < len(
            texts) else f"Slice {idx + 1}"

        element = {
            "label": label,
            "angle": float(wedge.theta2 - wedge.theta1),  # Convert to float
            "radius": float(wedge.r)  # Convert to float
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


def extract_and_print_figure_metadata(fig):
    """Extract metadata from a matplotlib figure and print as JSON"""
    import matplotlib.pyplot as plt
    import matplotlib.collections
    import matplotlib.figure

    metadata = {}
    subplots = []

    # Process each axis in the figure
    for i, ax in enumerate(fig.axes):
        subplot_data = {}

        # Title and labels
        if ax.get_title():
            subplot_data["title"] = ax.get_title()
        if ax.get_xlabel():
            subplot_data["x_label"] = ax.get_xlabel()
        if ax.get_ylabel():
            subplot_data["y_label"] = ax.get_ylabel()

        # Scale types
        subplot_data["x_scale"] = ax.get_xscale()
        subplot_data["y_scale"] = ax.get_yscale()

        # Ticks and tick labels
        xticks = ax.get_xticks()
        yticks = ax.get_yticks()
        xticklabels = [str(label) for label in ax.get_xticklabels()]
        yticklabels = [str(label) for label in ax.get_yticklabels()]

        # Convert to list if needed
        subplot_data["x_ticks"] = xticks.tolist() if hasattr(
            xticks, 'tolist') else list(xticks)
        subplot_data["y_ticks"] = yticks.tolist() if hasattr(
            yticks, 'tolist') else list(yticks)
        subplot_data["x_tick_labels"] = xticklabels
        subplot_data["y_tick_labels"] = yticklabels

        # Try to determine chart type and extract elements data
        chart_type = "unknown"
        elements = []

        try:
            # First check for box plots as they can contain rectangles that might be mistaken for bar charts
            box_plots = [child for child in ax.get_children() if isinstance(
                child, plt.matplotlib.patches.PathPatch)]

            if box_plots:
                chart_type = "box_and_whisker"
                elements = extract_box_plot_data(ax, xticklabels)
            else:
                # Get all lines and scatter plots first
                lines = [child for child in ax.get_children(
                ) if isinstance(child, plt.Line2D)]
                scatters = [child for child in ax.get_children() if isinstance(
                    child, matplotlib.collections.PathCollection)]

                if lines:
                    chart_type = "line"
                    elements = extract_line_plot_data(ax)
                elif scatters:
                    chart_type = "scatter"
                    elements = extract_scatter_plot_data(ax)
                else:
                    for artist in ax.get_children():
                        if isinstance(artist, plt.Rectangle):  # bar charts
                            chart_type = "bar"
                            elements = extract_bar_chart_data(ax, xticklabels)
                            break
                        elif isinstance(artist, plt.Wedge):  # pie charts
                            chart_type = "pie"
                            elements = extract_pie_chart_data(ax)
                            break
        except Exception as e:
            print(
                f"Warning: Failed to extract chart data: {e}", file=sys.stderr)
            # Continue with empty elements if extraction fails

        subplot_data["type"] = chart_type
        if elements:  # Only add elements if we have any
            subplot_data["elements"] = elements

        # Save subplot PNG if this is a multi-subplot figure
        if len(fig.axes) > 1:
            try:
                # Create a new figure with just this subplot
                subplot_fig = plt.figure(figsize=(8, 6))
                subplot_ax = subplot_fig.add_subplot(111)

                # Recreate the plot based on the chart type and elements
                if chart_type == "bar":
                    subplot_ax = recreate_and_save_bar_chart(
                        ax, elements, subplot_ax)
                elif chart_type == "scatter":
                    subplot_ax = recreate_and_save_scatter_plot(
                        ax, elements, subplot_ax)
                elif chart_type == "line":
                    subplot_ax = recreate_and_save_line_plot(
                        ax, elements, subplot_ax)
                elif chart_type == "box_and_whisker":
                    # For box plots, use a direct copy approach
                    plt.close(subplot_fig)
                    try:
                        # Use a direct copy instead (capture the entire axis)
                        extent = ax.get_tightbbox(fig.canvas.get_renderer()).transformed(
                            fig.dpi_scale_trans.inverted())
                        subplot_fig = plt.figure(figsize=extent.size)

                        # Save the figure portion that contains just this axis
                        png_buffer = io.BytesIO()
                        fig.savefig(png_buffer, format='png',
                                    bbox_inches=extent, dpi=100)
                        png_buffer.seek(0)
                        subplot_data["png"] = base64.b64encode(
                            png_buffer.getvalue()).decode('utf-8')
                        plt.close(subplot_fig)
                        subplots.append(subplot_data)
                        continue
                    except Exception as e:
                        print(
                            f"Warning: Failed to save box plot: {e}", file=sys.stderr)
                        # Continue to the next subplot if this fails
                        plt.close(subplot_fig)
                        continue
                elif chart_type == "pie":
                    subplot_ax = recreate_and_save_pie_chart(
                        ax, elements, subplot_ax)

                # Set the subplot properties (title, labels, etc.)
                subplot_ax = copy_axis_properties(ax, subplot_ax)

                # Save the new figure
                subplot_fig.tight_layout()
                subplot_data["png"] = save_figure_as_base64(subplot_fig)

                # Close the figure to free memory
                plt.close(subplot_fig)
            except Exception as e:
                print(
                    f"Warning: Failed to recreate subplot: {e}", file=sys.stderr)
                # Continue without the PNG if there's an error

        subplots.append(subplot_data)

    # Save main figure PNG
    metadata_png = save_figure_as_base64(fig)

    # Create the final metadata structure
    if len(fig.axes) > 1:
        # Multiple subplots - create a main chart
        metadata = {
            # Try to get figure suptitle
            "title": fig.texts[0].get_text() if fig.texts else None,
            "type": "composite_chart",
            "png": metadata_png,
            "subplots": subplots
        }
    else:
        # Single plot - use the subplot data directly
        metadata = subplots[0]
        metadata["png"] = metadata_png

    # Print metadata in the specified JSON format
    json_output = {
        "type": "chart",
        "value": metadata
    }
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

        try:
            # Now patch the show function
            if hasattr(module, 'show'):
                # Store the original show function
                original_show = module.show

                # Define our custom show function
                def custom_show(*args, **kwargs):
                    global processed_figures

                    try:
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
                    except Exception as e:
                        print(
                            f"Warning: Error in custom_show: {e}", file=sys.stderr)

                    # Call the original show function with all arguments
                    return original_show(*args, **kwargs)

                # Replace the show function with our custom version
                module.show = custom_show
        except Exception as e:
            print(
                f"Warning: Failed to patch matplotlib.pyplot.show(): {e}", file=sys.stderr)


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
