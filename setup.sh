#!/bin/bash
set -e

echo "Setting up Enhanced CloudFormation MCP Server..."

# Get absolute path to this project
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
SCRIPT_PATH="$PROJECT_DIR/awslabs/run_server.sh"

# Find Python 3.9+
python_cmd=""
for cmd in python3.12 python3.11 python3.10 python3.9 python3; do
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
if ! "$python_cmd" -m pip install --user fastmcp boto3 pydantic >/dev/null 2>&1; then
    # Try with --break-system-packages for PEP 668
    "$python_cmd" -m pip install --user --break-system-packages fastmcp boto3 pydantic
fi

# Make run script executable
chmod +x "$SCRIPT_PATH"

# Create ~/.aws/amazonq directory if it doesn't exist
AMAZONQ_DIR="$HOME/.aws/amazonq"
mkdir -p "$AMAZONQ_DIR"

# Path to mcp.json
MCP_CONFIG="$AMAZONQ_DIR/mcp.json"

# Create the MCP server configuration
MCP_SERVER_CONFIG='{
  "mcpServers": {
    "enhanced-cfn-mcp-server": {
      "command": "'"$SCRIPT_PATH"'",
      "args": [],
      "env": {},
      "timeout": 120000,
      "disabled": false
    }
  }
}'

# Handle existing config
if [ -f "$MCP_CONFIG" ]; then
    echo "Updating existing MCP configuration..."
    # Create backup
    cp "$MCP_CONFIG" "$MCP_CONFIG.backup"
    
    # Check if jq is available for proper JSON merging
    if command -v jq >/dev/null 2>&1; then
        # Use jq for proper JSON merging
        echo "$MCP_SERVER_CONFIG" | jq -s '.[0] * .[1]' "$MCP_CONFIG" - > "$MCP_CONFIG.tmp"
        mv "$MCP_CONFIG.tmp" "$MCP_CONFIG"
    else
        # Simple replacement without jq
        if grep -q "enhanced-cfn-mcp-server" "$MCP_CONFIG"; then
            echo "Enhanced CFN MCP server already configured, updating path..."
            # Replace the command path
            sed -i.bak "s|\"command\": \".*run_server.sh\"|\"command\": \"$SCRIPT_PATH\"|" "$MCP_CONFIG"
        else
            echo "Adding enhanced CFN MCP server to existing config..."
            # Add to existing config (simple approach)
            python3 -c "
import json
import sys

# Read existing config
with open('$MCP_CONFIG', 'r') as f:
    existing = json.load(f)

# Add our server
if 'mcpServers' not in existing:
    existing['mcpServers'] = {}

existing['mcpServers']['enhanced-cfn-mcp-server'] = {
    'command': '$SCRIPT_PATH',
    'args': [],
    'env': {},
    'timeout': 120000,
    'disabled': False
}

# Write back
with open('$MCP_CONFIG', 'w') as f:
    json.dump(existing, f, indent=2)
"
        fi
    fi
else
    echo "Creating new MCP configuration..."
    echo "$MCP_SERVER_CONFIG" | python3 -c "
import json
import sys
config = json.load(sys.stdin)
with open('$MCP_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "The Enhanced CloudFormation MCP Server is now configured globally."
echo "You can run 'q chat' from any directory and the server will be available."
echo ""
echo "Try it:"
echo "  q chat"
echo "  Then ask: 'Create a simple S3 bucket CloudFormation template'"
