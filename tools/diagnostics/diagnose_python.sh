#!/bin/bash

# Create a temporary directory
TEMP_DIR="/tmp/python_diagnosis_$(date +%s)"
mkdir -p $TEMP_DIR
echo "Created temporary directory: $TEMP_DIR"

# Function to run a command and save output to a file
run_cmd() {
  local cmd="$1"
  local outfile="$2"
  echo "Running: $cmd"
  $cmd > "$TEMP_DIR/$outfile" 2>&1
  echo "Output saved to: $TEMP_DIR/$outfile"
}

# Basic system information
echo "System information" > "$TEMP_DIR/system_info.txt"
echo "Date: $(date)" >> "$TEMP_DIR/system_info.txt"
echo "Hostname: $(hostname)" >> "$TEMP_DIR/system_info.txt"
echo "User: $(whoami)" >> "$TEMP_DIR/system_info.txt"

# Python paths
run_cmd "which python" "which_python.txt"
run_cmd "which python3" "which_python3.txt"
run_cmd "which python3.11" "which_python311.txt"

# Python versions
run_cmd "python --version" "python_version.txt"
run_cmd "python3 --version" "python3_version.txt"
run_cmd "python3.11 --version" "python311_version.txt"

# Environment
run_cmd "echo PATH=$PATH" "path.txt"
run_cmd "echo PYTHONPATH=$PYTHONPATH" "pythonpath.txt"

# Configuration files
run_cmd "cat ~/.bashrc | grep python" "bashrc_python.txt"
run_cmd "cat ~/.bash_profile | grep python 2>/dev/null || echo 'No .bash_profile'" "bash_profile_python.txt"
run_cmd "ls -la ~/bin/python 2>/dev/null || echo 'No ~/bin/python'" "bin_python.txt"

# Module import test
cat > "$TEMP_DIR/import_test.py" << EOF
try:
    import awslabs.cfn_mcp_server.config
    print("Successfully imported config module")
except ImportError as e:
    print(f"Failed to import config module: {e}")
EOF

run_cmd "python3 $TEMP_DIR/import_test.py" "import_test.txt"

# Create a summary file
echo "Python Diagnosis Summary" > "$TEMP_DIR/summary.txt"
echo "=======================" >> "$TEMP_DIR/summary.txt"
echo "" >> "$TEMP_DIR/summary.txt"

echo "System Information:" >> "$TEMP_DIR/summary.txt"
cat "$TEMP_DIR/system_info.txt" >> "$TEMP_DIR/summary.txt"
echo "" >> "$TEMP_DIR/summary.txt"

echo "Python Paths:" >> "$TEMP_DIR/summary.txt"
echo "which python: $(cat $TEMP_DIR/which_python.txt)" >> "$TEMP_DIR/summary.txt"
echo "which python3: $(cat $TEMP_DIR/which_python3.txt)" >> "$TEMP_DIR/summary.txt"
echo "which python3.11: $(cat $TEMP_DIR/which_python311.txt)" >> "$TEMP_DIR/summary.txt"
echo "" >> "$TEMP_DIR/summary.txt"

echo "Python Versions:" >> "$TEMP_DIR/summary.txt"
echo "python --version: $(cat $TEMP_DIR/python_version.txt)" >> "$TEMP_DIR/summary.txt"
echo "python3 --version: $(cat $TEMP_DIR/python3_version.txt)" >> "$TEMP_DIR/summary.txt"
echo "python3.11 --version: $(cat $TEMP_DIR/python311_version.txt)" >> "$TEMP_DIR/summary.txt"
echo "" >> "$TEMP_DIR/summary.txt"

echo "Environment:" >> "$TEMP_DIR/summary.txt"
echo "PATH: $(cat $TEMP_DIR/path.txt)" >> "$TEMP_DIR/summary.txt"
echo "PYTHONPATH: $(cat $TEMP_DIR/pythonpath.txt)" >> "$TEMP_DIR/summary.txt"
echo "" >> "$TEMP_DIR/summary.txt"

echo "Configuration:" >> "$TEMP_DIR/summary.txt"
echo "~/.bashrc python entries: $(cat $TEMP_DIR/bashrc_python.txt)" >> "$TEMP_DIR/summary.txt"
echo "~/.bash_profile python entries: $(cat $TEMP_DIR/bash_profile_python.txt)" >> "$TEMP_DIR/summary.txt"
echo "~/bin/python: $(cat $TEMP_DIR/bin_python.txt)" >> "$TEMP_DIR/summary.txt"
echo "" >> "$TEMP_DIR/summary.txt"

echo "Module Import Test:" >> "$TEMP_DIR/summary.txt"
cat "$TEMP_DIR/import_test.txt" >> "$TEMP_DIR/summary.txt"

echo "Diagnosis complete. Summary file: $TEMP_DIR/summary.txt"
echo "All output files are in: $TEMP_DIR"

# Print the summary file
echo ""
echo "Summary:"
echo "========"
cat "$TEMP_DIR/summary.txt"