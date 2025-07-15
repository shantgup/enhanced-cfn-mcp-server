#!/usr/bin/env python3

import sys
import os

# Print Python information
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Check if the awslabs directory exists
awslabs_dir = os.path.join(os.getcwd(), "awslabs")
print(f"Checking if {awslabs_dir} exists: {os.path.exists(awslabs_dir)}")

# Check if the config module exists
config_file = os.path.join(os.getcwd(), "awslabs/cfn_mcp_server/config.py")
print(f"Checking if {config_file} exists: {os.path.exists(config_file)}")

# Try to import the modules
try:
    import awslabs
    print("Successfully imported awslabs package")
except ImportError as e:
    print(f"Failed to import awslabs package: {e}")

try:
    import awslabs.cfn_mcp_server
    print("Successfully imported awslabs.cfn_mcp_server package")
except ImportError as e:
    print(f"Failed to import awslabs.cfn_mcp_server package: {e}")

try:
    import awslabs.cfn_mcp_server.config
    print("Successfully imported awslabs.cfn_mcp_server.config module")
except ImportError as e:
    print(f"Failed to import awslabs.cfn_mcp_server.config module: {e}")

# Print Python path
print("\nPython path:")
for path in sys.path:
    print(f"  {path}")

# Write output to a file so we can check it
with open("import_test_output.txt", "w") as f:
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Current working directory: {os.getcwd()}\n")
    f.write(f"Checking if {awslabs_dir} exists: {os.path.exists(awslabs_dir)}\n")
    f.write(f"Checking if {config_file} exists: {os.path.exists(config_file)}\n")
    
    try:
        import awslabs
        f.write("Successfully imported awslabs package\n")
    except ImportError as e:
        f.write(f"Failed to import awslabs package: {e}\n")
    
    try:
        import awslabs.cfn_mcp_server
        f.write("Successfully imported awslabs.cfn_mcp_server package\n")
    except ImportError as e:
        f.write(f"Failed to import awslabs.cfn_mcp_server package: {e}\n")
    
    try:
        import awslabs.cfn_mcp_server.config
        f.write("Successfully imported awslabs.cfn_mcp_server.config module\n")
    except ImportError as e:
        f.write(f"Failed to import awslabs.cfn_mcp_server.config module: {e}\n")
    
    f.write("\nPython path:\n")
    for path in sys.path:
        f.write(f"  {path}\n")

print("Output written to import_test_output.txt")