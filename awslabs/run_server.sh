#!/bin/bash
cd "$(dirname "$0")/.."

# Try different Python versions in order of preference
for python_cmd in python3.11 python3.10 python3.9 python3; do
    if command -v "$python_cmd" >/dev/null 2>&1; then
        exec "$python_cmd" -m awslabs.cfn_mcp_server.server "$@"
    fi
done

echo "Error: No suitable Python version found. Please install Python 3.9+ and ensure it's in your PATH."
exit 1
