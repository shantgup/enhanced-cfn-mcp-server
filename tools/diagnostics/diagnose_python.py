#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
import time

# Create a temporary directory for our output files
temp_dir = tempfile.mkdtemp(prefix="python_diagnosis_")
print(f"Created temporary directory: {temp_dir}")

def run_command_to_file(cmd, filename):
    """Run a command and write output to a file in the temp directory."""
    full_path = os.path.join(temp_dir, filename)
    
    # Run the command and redirect output to the file
    os.system(f"{cmd} > {full_path} 2>&1")
    
    # Return the path to the output file
    return full_path

def read_file(filepath):
    """Read and return the contents of a file."""
    try:
        with open(filepath, 'r') as f:
            return f.read().strip()
    except Exception as e:
        return f"Error reading file: {e}"

# Write basic Python info to files
with open(os.path.join(temp_dir, "python_info.txt"), 'w') as f:
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"PATH: {os.environ.get('PATH', 'Not set')}\n")

# Run commands and write outputs to files
commands = {
    "which_python": "which python",
    "which_python3": "which python3",
    "which_python311": "which python3.11",
    "python_version": "python --version",
    "python3_version": "python3 --version",
    "python311_version": "python3.11 --version",
    "bashrc_check": "cat ~/.bashrc | grep python",
    "symlink_check": "ls -la ~/bin/python 2>/dev/null || echo 'No symbolic link found'",
    "pythonpath": "echo $PYTHONPATH",
    "module_check": "python3 -c 'import sys; print(sys.path)'"
}

# Execute commands and save outputs
output_files = {}
for name, cmd in commands.items():
    output_files[name] = run_command_to_file(cmd, f"{name}.txt")

# Write a summary file with all the information
with open(os.path.join(temp_dir, "summary.txt"), 'w') as f:
    f.write("Python Diagnosis Summary\n")
    f.write("======================\n\n")
    
    # Basic Python info
    f.write("Python Information:\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"PATH: {os.environ.get('PATH', 'Not set')}\n\n")
    
    # Command outputs
    f.write("Command Outputs:\n")
    for name, filepath in output_files.items():
        f.write(f"\n--- {name} ---\n")
        f.write(f"Command: {commands[name]}\n")
        f.write(f"Output: {read_file(filepath)}\n")

# Write the location of the summary file
print(f"Diagnosis complete. Summary file: {os.path.join(temp_dir, 'summary.txt')}")
print(f"All output files are in: {temp_dir}")

# Try to import our module and write result to a file
with open(os.path.join(temp_dir, "import_test.txt"), 'w') as f:
    try:
        import awslabs.cfn_mcp_server.config
        f.write("Successfully imported config module\n")
    except ImportError as e:
        f.write(f"Failed to import config module: {e}\n")