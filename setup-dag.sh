#!/bin/bash

# Check if the system is Unix-based
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    echo "Unix-based system detected."
    echo "Installing graph-tool using conda..."

    # Check if conda is installed
    if command -v conda &> /dev/null; then
        conda install -c conda-forge graph-tool
    else
        echo "Conda is not installed. Please install Conda first."
        exit 1
    fi

else
    echo "It appears you are using Windows."
    echo "Please install graph-tool manually using conda."
    echo "You can do this with: conda install -c conda-forge graph-tool"
    exit 1
fi

# Now proceed with Poetry installation
echo "Installing Python dependencies with Poetry..."
poetry install --extras "dag"

echo "Installation complete."
