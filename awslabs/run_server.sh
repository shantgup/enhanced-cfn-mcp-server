#!/bin/bash
set -e
cd "$(dirname "$0")/.."

CACHE_FILE=".python_cache"

# Try cached Python first
if [[ -f "$CACHE_FILE" ]]; then
    cached_python=$(cat "$CACHE_FILE")
    if command -v "$cached_python" >/dev/null 2>&1; then
        if "$cached_python" -c "import sys, fastmcp, boto3, pydantic; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
            echo "Using cached Python: $cached_python" >&2
            exec "$cached_python" -m awslabs.cfn_mcp_server.server "$@"
        fi
    fi
    echo "Cached Python no longer valid, rediscovering..." >&2
fi

# Function to check if Python is user-installable (not system Python)
is_user_python() {
    local python_cmd="$1"
    local python_path=$("$python_cmd" -c "import sys; print(sys.executable)" 2>/dev/null) || return 1
    
    # Skip system Python paths
    case "$python_path" in
        /usr/bin/python*) return 1 ;;  # System Python
        /System/*) return 1 ;;         # System Python
    esac
    
    # Test if we can install packages
    "$python_cmd" -m pip --version >/dev/null 2>&1
}

# Function to check if required packages are installed
check_packages() {
    local python_cmd="$1"
    echo "Checking packages for $python_cmd..." >&2
    
    if ! "$python_cmd" -c "import fastmcp, boto3, pydantic" 2>/dev/null; then
        echo "Installing required packages for $python_cmd..." >&2
        "$python_cmd" -m pip install --user fastmcp boto3 pydantic || return 1
    fi
    return 0
}

# Discover all available Python versions dynamically
discover_python_versions() {
    local versions=()
    
    # Check specific paths first (highest priority)
    for path in /opt/homebrew/bin/python3 /usr/local/bin/python3 ~/.pyenv/shims/python3; do
        if [[ -x "$path" ]]; then
            versions+=("$path")
        fi
    done
    
    # Discover all python3.X versions in PATH (sorted newest first)
    while IFS= read -r -d '' python_cmd; do
        if [[ "$python_cmd" =~ python3\.([0-9]+)$ ]]; then
            versions+=("$(basename "$python_cmd")")
        fi
    done < <(find $(echo "$PATH" | tr ':' ' ') -name "python3.*" -type f -executable 2>/dev/null | sort -V -r | tr '\n' '\0')
    
    # Add generic python3 as fallback
    versions+=("python3")
    
    # Remove duplicates while preserving order
    printf '%s\n' "${versions[@]}" | awk '!seen[$0]++'
}

echo "Discovering Python versions..." >&2
while IFS= read -r python_cmd; do
    if command -v "$python_cmd" >/dev/null 2>&1; then
        echo "Testing $python_cmd..." >&2
        
        # Check Python version is 3.9+
        if "$python_cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
            version=$("$python_cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
            python_path=$("$python_cmd" -c "import sys; print(sys.executable)" 2>/dev/null)
            echo "Found Python $version at $python_path" >&2
            
            # Check if it's user-installable
            if is_user_python "$python_cmd"; then
                echo "Python is user-installable" >&2
                
                # Check and install packages if needed
                if check_packages "$python_cmd"; then
                    echo "Caching Python choice: $python_cmd" >&2
                    echo "$python_cmd" > "$CACHE_FILE"
                    echo "Starting server with $python_cmd..." >&2
                    exec "$python_cmd" -m awslabs.cfn_mcp_server.server "$@"
                fi
            else
                echo "Skipping system Python (can't install packages)" >&2
            fi
        else
            echo "Python version too old (need 3.9+)" >&2
        fi
    fi
done < <(discover_python_versions)

echo "Error: No suitable user-installable Python version found."
echo "Please install Python 3.9+ using:"
echo "  macOS: brew install python3"
echo "  pyenv: pyenv install 3.12.0 && pyenv global 3.12.0"
exit 1
