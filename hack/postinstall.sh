#!/bin/bash
set -e

# Upgrade basic tools
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools wheel "black<24.0.0,>=23.1.0"

# Install dependencies
echo "Installing Python packages..."
python3 -m pip install "aiohttp>=3.8.5" "pydantic>=2.4.2" "python-dateutil>=2.8.2" "typing-extensions>=4.7.1" "urllib3>=1.25.3" "pydoc-markdown>=4.8.0" "isort>=5.10.0,<6.0.0" "nbqa>=1.9.1" "pylint>=3.3.4" "black[jupyter]>=23.1.0,<=23.12.1" "matplotlib>=3.10.0,<3.11.0"
python3 -m pip install environs build

# Install the local package in editable mode
python3 -m pip install -e "packages/python"

echo "Post-install completed successfully"

echo "Building and linking @daytonaio/sdk..."
cd packages/typescript
yarn build
yarn link

cd ../../examples/typescript/exec-command
yarn link @daytonaio/sdk
