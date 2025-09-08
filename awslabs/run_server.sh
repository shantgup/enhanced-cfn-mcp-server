#!/bin/bash
set -e
cd "$(dirname "$0")/.."

CACHE_FILE=".python_cache"

# Try cached Python first (fast path)
if [[ -f "$CACHE_FILE" ]]; then
    cached_python=$(cat "$CACHE_FILE")
    if "$cached_python" -c "import fastmcp, boto3, pydantic" 2>/dev/null; then
        exec "$cached_python" -m awslabs.cfn_mcp_server.server "$@"
    fi
    rm -f "$CACHE_FILE"
fi

# Quick function to test Python (no package installation)
quick_test() {
    local python_cmd="$1"
    "$python_cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null && \
    "$python_cmd" -c "import fastmcp, boto3, pydantic" 2>/dev/null
}

# Try default python3 first (fast)
if quick_test python3; then
    echo "python3" > "$CACHE_FILE"
    exec python3 -m awslabs.cfn_mcp_server.server "$@"
fi

# Try common alternatives (fast)
for python_cmd in /opt/homebrew/bin/python3 /usr/local/bin/python3 python3.12 python3.11 python3.10; do
    if command -v "$python_cmd" >/dev/null 2>&1 && quick_test "$python_cmd"; then
        echo "$python_cmd" > "$CACHE_FILE"
        exec "$python_cmd" -m awslabs.cfn_mcp_server.server "$@"
    fi
done

# If we get here, packages are missing - install them (slow path)
install_and_test() {
    local python_cmd="$1"
    if ! "$python_cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
        return 1
    fi
    
    if "$python_cmd" -m pip install --user fastmcp boto3 pydantic >/dev/null 2>&1 || \
       "$python_cmd" -m pip install --user --break-system-packages fastmcp boto3 pydantic >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# Try installing packages (only if needed)
for python_cmd in python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
    if command -v "$python_cmd" >/dev/null 2>&1 && install_and_test "$python_cmd"; then
        echo "$python_cmd" > "$CACHE_FILE"
        exec "$python_cmd" -m awslabs.cfn_mcp_server.server "$@"
    fi
done

echo "Error: No working Python found. Run: ./setup.sh" >&2
exit 1
