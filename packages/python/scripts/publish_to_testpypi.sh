#!/bin/bash

set -e # Exit on error

# Ensure required tools are installed
if ! command -v python3 &>/dev/null || ! command -v twine &>/dev/null; then
  echo "Error: Python3 and twine must be installed!"
  exit 1
fi

# Extract the main version from pyproject.toml
MAIN_VERSION=$(python3 -c "import tomli; from pathlib import Path; \
  content = Path('pyproject.toml').read_text(); \
  print(tomli.loads(content)['project']['version'])")

# Set a fake GitHub run number (use argument if provided, else default to 100)
RUN_NUMBER=${1:-100}

# Generate the new pre-release version
NEW_VERSION="${MAIN_VERSION}rc${RUN_NUMBER}"

echo "Extracted main version: $MAIN_VERSION"
echo "Bumping version to: $NEW_VERSION"

# Install dependencies if missing
pip install --upgrade setuptools wheel twine tomli tomli-w build

# Update the version in pyproject.toml using python
python3 -c "
import tomli, tomli_w
from pathlib import Path

toml_path = Path('pyproject.toml')
data = tomli.loads(toml_path.read_text())
data['project']['version'] = '$NEW_VERSION'
toml_path.write_text(tomli_w.dumps(data))
"

# Clean previous builds
rm -rf dist/*

# Build the package
python3 -m build

# tmp
TEST_PYPI_API_TOKEN="pypi-AgENdGVzdC5weXBpLm9yZwIkNGNjMWM3ZjUtMTMyNi00NzNmLTllNGYtYjEwODBiYjZlM2I3AAIQWzEsWyJzZGstdGVzdCJdXQACLFsyLFsiM2ZmNDVhNDktNjI4ZS00M2M5LTk3NDgtY2Q5ODg2OTU1ZjIyIl1dAAAGIPEKMk3Cv60g1uSMkAYLPOQZiGnMkkOMyR__gP4QM3vb"

# Upload to TestPyPI
if [ -z "$TEST_PYPI_API_TOKEN" ]; then
  echo "Error: TEST_PYPI_API_TOKEN environment variable is not set!"
  exit 1
fi

twine upload --repository testpypi dist/* --verbose -u __token__ -p "$TEST_PYPI_API_TOKEN"

echo "✅ Successfully published $NEW_VERSION to TestPyPI!"


echo "dummy"