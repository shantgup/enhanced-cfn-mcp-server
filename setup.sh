#!/bin/bash
set -e

echo "Setting up Enhanced CloudFormation MCP Server..."

# Find Python 3.9+
python_cmd=""
for cmd in python3.11 python3.10 python3.9 python3; do
    if command -v "$cmd" >/dev/null 2>&1; then
        if "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
            python_cmd="$cmd"
            break
        fi
    fi
done

if [ -z "$python_cmd" ]; then
    echo "Error: Python 3.9+ not found. Please install:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi

echo "Using $python_cmd"

# Install required packages
echo "Installing required packages..."
"$python_cmd" -m pip install --user fastmcp boto3 pydantic

# Make run script executable
chmod +x awslabs/run_server.sh

echo "Setup complete! You can now run 'q chat' in this directory."
