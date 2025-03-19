from e2b_code_interpreter import Sandbox

code = """
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Sample data
categories = ['A', 'B', 'C', 'D', 'E']
values = [22, 30, 15, 25, 8]

# Convert to DataFrame
df = pd.DataFrame({'Category': categories, 'Value': values})

# Create a bar plot as a pie chart alternative
plt.figure(figsize=(8, 6))
sns.barplot(x="Category", y="Value", data=df, palette="Set3")

plt.title("Bar Chart Alternative to Pie Chart")
plt.show()


"""

sandbox = Sandbox(api_key='e2b_1395305c0b213d62178ac8de1ba936188ae50c9f')
execution = sandbox.run_code(code)
chart = execution.results[0].chart

print('Type:', chart.type)
print('Title:', chart.title)
print('Elements:', chart.elements)
for element in chart.elements:
  print(element)
  print('\n  Label:', element.label)
  print('  angle:', element.angle)
  print('  radius:', element.radius)
