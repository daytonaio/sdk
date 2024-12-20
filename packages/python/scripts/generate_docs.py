import os
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.interfaces import Context
import yaml

def generate_docs():
    # Ensure docs directory exists
    docs_dir = "../../docs/python-sdk"
    os.makedirs(docs_dir, exist_ok=True)
    
    # Load main config
    config_file = "config/pydoc/main.yml"
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Generate docs for each module
    modules = [
        "daytona_sdk",
        "daytona_sdk.daytona",
        "daytona_sdk.workspace",
        "daytona_sdk.filesystem",
        "daytona_sdk.git",
        "daytona_sdk.process",
        "daytona_sdk.lsp_server"
    ]
    
    for module in modules:
        # Create module-specific config
        module_config = config.copy()
        module_config['loaders'][0]['modules'] = [module]
        
        # Generate documentation
        session = PydocMarkdown()
        session.load_config(module_config)
        session.init(Context(os.path.abspath("src")))
        content = session.render()
        
        # Write to file
        output_file = os.path.join(docs_dir, f"{module.split('.')[-1]}.md")
        with open(output_file, "w") as f:
            f.write(content)
    
    # Generate index
    generate_index(modules)

def generate_index(modules):
    """Generate the main README.md file."""
    version = "0.1.3"  # Get this from package version
    
    with open("docs/templates/README.md", "r") as f:
        template = f.read()
    
    # Build sections
    classes = []
    modules_list = []
    types = []
    
    for module in modules:
        module_name = module.split(".")[-1]
        if module_name != "daytona_sdk":
            modules_list.append(f"- [{module_name}]({module_name}.md)")
    
    content = template.format(
        version=version,
        classes="\n".join(classes),
        modules="\n".join(modules_list),
        types="\n".join(types)
    )
    
    with open("../../docs/python-sdk/README.md", "w") as f:
        f.write(content)

if __name__ == "__main__":
    generate_docs() 