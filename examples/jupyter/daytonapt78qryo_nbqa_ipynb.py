# %%NBQA-CELL-SEP84ee27
import base64
import io
import os
from pprint import pp

import matplotlib.pyplot as plt
from daytona_sdk import BarChart, CompositeChart, Daytona, LineChart, SessionExecuteRequest

daytona = Daytona()


# %%NBQA-CELL-SEP84ee27
sandbox = daytona.create()

print(sandbox.id)


# %%NBQA-CELL-SEP84ee27
response = sandbox.process.code_run('print("Hello World!")')
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)


# %%NBQA-CELL-SEP84ee27
response = sandbox.process.exec('echo "Hello World from exec!"', cwd="/home/daytona", timeout=10)
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)


# %%NBQA-CELL-SEP84ee27
exec_session_id = "exec-session-1"
sandbox.process.create_session(exec_session_id)
session = sandbox.process.get_session(exec_session_id)
pp(session)
print()

# Execute the first command in the session
execCommand1 = sandbox.process.execute_session_command(exec_session_id, SessionExecuteRequest(command="export FOO=BAR"))
if execCommand1.exit_code != 0:
    print(f"Error: {execCommand1.exit_code} {execCommand1.output}")

# Get the command details
session_command = sandbox.process.get_session_command(exec_session_id, execCommand1.cmd_id)
pp(session_command)
print()

# Execute a second command in the session and see that the environment variable is set
execCommand2 = sandbox.process.execute_session_command(exec_session_id, SessionExecuteRequest(command="echo $FOO"))
if execCommand2.exit_code != 0:
    print(f"Error: {execCommand2.exit_code} {execCommand2.output}")
else:
    print(f"Output: {execCommand2.output}\n")

logs = sandbox.process.get_session_command_logs(exec_session_id, execCommand2.cmd_id)
print(f"Logs: {logs}")


# %%NBQA-CELL-SEP84ee27
code = """
import matplotlib.pyplot as plt

# Data
categories = ['A', 'B', 'C', 'D']
values = [20, 35, 30, 10]

# Plot
plt.figure(figsize=(8, 5))
plt.bar(categories, values, color='skyblue', edgecolor='black')

# Labels and title
plt.xlabel('Category')
plt.ylabel('Value')
plt.title('Bar Chart Example')

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
"""

response = sandbox.process.code_run(code)
chart = response.artifacts.charts[0]

img_data = base64.b64decode(chart.png)
img = plt.imread(io.BytesIO(img_data))
plt.imshow(img)
plt.axis("off")
plt.show()

print(f"type: {chart.type}")
print(f"title: {chart.title}")
if isinstance(chart, BarChart):
    print(f"x_label: {chart.x_label}")
    print(f"y_label: {chart.y_label}")
    print("elements:")
    for element in chart.elements:
        print(f"\n\tlabel: {element.label}")
        print(f"\tgroup: {element.group}")
        print(f"\tvalue: {element.value}")


# %%NBQA-CELL-SEP84ee27
code = """
import matplotlib.pyplot as plt
import numpy as np

# Data for bar chart
categories = ['A', 'B', 'C', 'D']
bar_values = [20, 35, 30, 10]

# Data for line chart
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x) * 0.1  # scaled to fit nicely

# Create a figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# --- Bar Chart (subplot 1) ---
ax1.bar(categories, bar_values, color='skyblue', edgecolor='black')
ax1.set_title('Bar Chart')
ax1.set_xlabel('Category')
ax1.set_ylabel('Value')
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# --- Line Chart with 3 lines (subplot 2) ---
ax2.plot(x, y1, label='sin(x)', linewidth=2)
ax2.plot(x, y2, label='cos(x)', linewidth=2)
ax2.plot(x, y3, label='0.1 * tan(x)', linewidth=2)
ax2.set_title('Line Chart with 3 Lines')
ax2.set_xlabel('X-axis')
ax2.set_ylabel('Y-axis')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend()

# Add main title
fig.suptitle('Composite Chart Example', fontsize=16)

# Adjust layout and show
plt.tight_layout()
plt.show()
"""

response = sandbox.process.code_run(code)
chart = response.artifacts.charts[0]

img_data = base64.b64decode(chart.png)
img = plt.imread(io.BytesIO(img_data))
plt.imshow(img)
plt.axis("off")
plt.show()

print(f"type: {chart.type}")
print(f"title: {chart.title}")
if isinstance(chart, CompositeChart):
    for subplot in chart.elements:
        print(f"\n\ttype: {subplot.type}")
        print(f"\ttitle: {subplot.title}")
        if isinstance(subplot, BarChart):
            print(f"\tx_label: {subplot.x_label}")
            print(f"\ty_label: {subplot.y_label}")
            print("\telements:")
            for element in subplot.elements:
                print(f"\n\t\tlabel: {element.label}")
                print(f"\t\tgroup: {element.group}")
                print(f"\t\tvalue: {element.value}")
        elif isinstance(subplot, LineChart):
            print(f"\tx_label: {subplot.x_label}")
            print(f"\ty_label: {subplot.y_label}")
            print(f"\tx_ticks: {subplot.x_ticks}")
            print(f"\tx_tick_labels: {subplot.x_tick_labels}")
            print(f"\tx_scale: {subplot.x_scale}")
            print(f"\ty_ticks: {subplot.y_ticks}")
            print(f"\ty_tick_labels: {subplot.y_tick_labels}")
            print(f"\ty_scale: {subplot.y_scale}")
            print("\telements:")
            for element in subplot.elements:
                print(f"\n\t\tlabel: {element.label}")
                print(f"\t\tpoints: {element.points}")


# %%NBQA-CELL-SEP84ee27
# List files in the sandbox
files = sandbox.fs.list_files("~")
pp(files)

# Create a new directory in the sandbox
new_dir = "new-dir"
sandbox.fs.create_folder(new_dir, "755")

file_path = os.path.join(new_dir, "data.txt")

# Add a new file to the sandbox
file_content = b"Hello, World!"
sandbox.fs.upload_file(file_path, file_content)

# Search for the file we just added
matches = sandbox.fs.find_files("~", "World!")
pp(matches)

# Replace the contents of the file
sandbox.fs.replace_in_files([file_path], "Hello, World!", "Goodbye, World!")

# Read the file
downloaded_file = sandbox.fs.download_file(file_path)
print("File content:", downloaded_file.decode("utf-8"))

# Change the file permissions
sandbox.fs.set_file_permissions(file_path, mode="777")

# Get file info
file_info = sandbox.fs.get_file_info(file_path)
pp(file_info)  # Should show the new permissions

# Move the file to the new location
new_file_path = "moved-data.txt"
sandbox.fs.move_files(file_path, new_file_path)

# Find the file in the new location
search_results = sandbox.fs.search_files("~", "moved-data.txt")
pp(search_results)

# Delete the file
sandbox.fs.delete_file(new_file_path)


# %%NBQA-CELL-SEP84ee27
project_dir = "learn-typescript"

# Clone the repository
sandbox.git.clone("https://github.com/panaverse/learn-typescript", project_dir, "master")

sandbox.git.pull(project_dir)

branches = sandbox.git.branches(project_dir)
pp(branches)


# %%NBQA-CELL-SEP84ee27
project_dir = "learn-typescript"

# Search for the file we want to work on
matches = sandbox.fs.find_files(project_dir, "var obj1 = new Base();")
print("Matches:", matches)

# Start the language server
lsp = sandbox.create_lsp_server("typescript", project_dir)
lsp.start()

# Notify the language server of the document we want to work on
lsp.did_open(matches[0].file)

# Get symbols in the document
symbols = lsp.document_symbols(matches[0].file)
print("Symbols:", symbols)

# Fix the error in the document
sandbox.fs.replace_in_files([matches[0].file], "var obj1 = new Base();", "var obj1 = new E();")

# Notify the language server of the document change
lsp.did_close(matches[0].file)
lsp.did_open(matches[0].file)

# Get completions at a specific position
completions = lsp.completions(matches[0].file, {"line": 12, "character": 18})
print("Completions:", completions)


# %%NBQA-CELL-SEP84ee27
sandboxes = daytona.list()
print(f"Total sandboxes count: {len(sandboxes)}")

for s in sandboxes:
    print(s.id)
    pp(s.info())
    print()


# %%NBQA-CELL-SEP84ee27
daytona.stop(sandbox)


# %%NBQA-CELL-SEP84ee27
daytona.start(sandbox)


# %%NBQA-CELL-SEP84ee27
daytona.delete(sandbox)
