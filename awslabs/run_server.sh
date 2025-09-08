#!/bin/bash
set -e
cd "$(dirname "$0")/.."

CACHE_FILE=".python_cache"

# Try cached Python first
if [[ -f "$CACHE_FILE" ]]; then
    cached_python=$(cat "$CACHE_FILE")
    if "$cached_python" -c "import sys, fastmcp, boto3, pydantic; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
        exec "$cached_python" -m awslabs.cfn_mcp_server.server "$@"
    fi
    rm -f "$CACHE_FILE"
fi

# Function to install packages
install_packages() {
    local python_cmd="$1"
    
    # Try standard user install
    if "$python_cmd" -m pip install --user fastmcp boto3 pydantic >/dev/null 2>&1; then
        return 0
    fi
    
    # Try with --break-system-packages for PEP 668
    if "$python_cmd" -m pip install --user --break-system-packages fastmcp boto3 pydantic >/dev/null 2>&1; then
        return 0
    fi
    
    return 1
}

# Function to test Python
test_python() {
    local python_cmd="$1"
    
    # Must be Python 3.9+
    if ! "$python_cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
        return 1
    fi
    
    # Check/install packages
    if ! "$python_cmd" -c "import fastmcp, boto3, pydantic" 2>/dev/null; then
        install_packages "$python_cmd" || return 1
    fi
    
    return 0
}

# Start with the user's default Python3 (what they're already using)
if command -v python3 >/dev/null 2>&1; then
    if test_python python3; then
        echo "python3" > "$CACHE_FILE"
        exec python3 -m awslabs.cfn_mcp_server.server "$@"
    fi
fi

# Fallback to common alternatives only if default doesn't work
for python_cmd in /opt/homebrew/bin/python3 /usr/local/bin/python3 python3.12 python3.11 python3.10 python3.9; do
    if command -v "$python_cmd" >/dev/null 2>&1; then
        if test_python "$python_cmd"; then
            echo "$python_cmd" > "$CACHE_FILE"
            exec "$python_cmd" -m awslabs.cfn_mcp_server.server "$@"
        fi
    fi
done

echo "Error: No working Python 3.9+ found. Please install: brew install python3" >&2
exit 1
