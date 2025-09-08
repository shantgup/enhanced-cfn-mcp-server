#!/bin/bash
set -e
cd "$(dirname "$0")/.."

# Function to check if Python is user-installable (not system Python)
is_user_python() {
    local python_cmd="$1"
    local python_path=$("$python_cmd" -c "import sys; print(sys.executable)")
    
    # Skip system Python paths
    case "$python_path" in
        /usr/bin/python*) return 1 ;;  # System Python
        /System/*) return 1 ;;         # System Python
    esac
    
    # Test if we can install packages
    if "$python_cmd" -m pip --version >/dev/null 2>&1; then
        return 0
    fi
    
    return 1
}

# Function to check if required packages are installed
check_packages() {
    local python_cmd="$1"
    echo "Checking packages for $python_cmd..." >&2
    
    # Check for required packages
    if ! "$python_cmd" -c "import fastmcp, boto3, pydantic" 2>/dev/null; then
        echo "Installing required packages for $python_cmd..." >&2
        "$python_cmd" -m pip install --user fastmcp boto3 pydantic || {
            echo "Failed to install packages for $python_cmd" >&2
            return 1
        }
    fi
    return 0
}

# Try different Python sources in order of preference
python_candidates=(
    # Homebrew Python (best choice)
    /opt/homebrew/bin/python3
    /usr/local/bin/python3
    # Pyenv Python
    ~/.pyenv/shims/python3
    # Generic commands (may include system Python)
    python3.12 python3.11 python3.10 python3.9 python3
)

for python_cmd in "${python_candidates[@]}"; do
    if command -v "$python_cmd" >/dev/null 2>&1; then
        echo "Testing $python_cmd..." >&2
        
        # Check Python version is 3.9+
        if "$python_cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
            version=$("$python_cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
            python_path=$("$python_cmd" -c "import sys; print(sys.executable)")
            echo "Found Python $version at $python_path" >&2
            
            # Check if it's user-installable
            if is_user_python "$python_cmd"; then
                echo "Python is user-installable" >&2
                
                # Check and install packages if needed
                if check_packages "$python_cmd"; then
                    echo "Starting server with $python_cmd..." >&2
                    exec "$python_cmd" -m awslabs.cfn_mcp_server.server "$@"
                fi
            else
                echo "Skipping system Python (can't install packages)" >&2
            fi
        fi
    fi
done

echo "Error: No suitable user-installable Python version found."
echo "Please install Python 3.9+ using one of these methods:"
echo "  macOS: brew install python3"
echo "  pyenv: pyenv install 3.11.0 && pyenv global 3.11.0"
echo "  python.org: Download from https://www.python.org/downloads/"
exit 1
