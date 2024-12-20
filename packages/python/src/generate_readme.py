import json
import os
import re

def create_readme():
    # Read the sidebar.json
    with open('./../../docs/python-sdk/sidebar.json', 'r') as f:
        sidebar = json.load(f)
    
    # Create README content
    readme_content = ["# Daytona Python SDK Documentation\n\n## Table of Contents\n"]
    
    def process_items(items, indent=0):
        for item in items:
            if isinstance(item, dict):
                # Handle categories
                label = item.get('label', '')
                readme_content.append(f"{'  ' * indent}- **{label}**")
                if 'items' in item:
                    process_items(item['items'], indent + 1)
            elif isinstance(item, str):
                # Handle direct links
                # Convert path to markdown link
                path = f"{item}.md"
                name = item.split('/')[-1]  # Get the last part of the path
                readme_content.append(f"{'  ' * indent}- [{name}]({path})")
    
    # Process the main items
    if 'items' in sidebar:
        process_items(sidebar['items'])
    
    # Write the README
    with open('./../../docs/python-sdk/README.md', 'w') as f:
        f.write('\n'.join(readme_content))

create_readme()