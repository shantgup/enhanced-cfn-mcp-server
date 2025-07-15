# CloudFormation MCP Server - Clean Project Structure

## 📁 **Active Files (DO NOT MODIFY)**

### **Core Server Files**
```
awslabs/cfn_mcp_server/
├── server_robust.py              ← **ACTIVE SERVER** (13 tools) - Q CLI uses this
├── server.py                     ← Original server (not used by Q CLI)
├── aws_client.py                 ← AWS client utilities (required)
├── troubleshooter.py             ← Troubleshooting classes (required)
├── template_generator.py         ← Template generation (required)
├── stack_manager.py              ← Stack management (required)
├── schema_manager.py             ← Schema management (required)
├── iac_generator.py              ← Infrastructure as Code generation (required)
├── intelligent_template_generator.py ← Smart template generation (required)
├── resource_generator.py         ← Resource generation (required)
├── cloud_control_utils.py        ← Cloud Control API utilities (required)
├── context.py                    ← Context management (required)
├── errors.py                     ← Error handling (required)
└── __init__.py                   ← Package initialization (required)
```

### **Configuration Files**
```
~/.aws/amazonq/mcp.json           ← **Q CLI GLOBAL CONFIG** (critical)
/Users/shantgup/bin/enhanced-cfn-mcp-server ← **EXECUTABLE SCRIPT** (critical)
pyproject.toml                    ← Package configuration
```

### **Documentation**
```
COMPLETE_SYSTEM_DOCUMENTATION.md  ← **COMPLETE SETUP DOCS** (read this!)
PROJECT_STRUCTURE.md              ← This file
validate_setup.py                 ← Configuration validation script
```

## 📁 **Archived Files (Moved to tmp/)**

### **Unused Server Variants**
```
tmp/unused_servers/
├── server_enhanced.py            ← Enhanced server (not used by Q CLI)
├── server_working.py             ← Working server (not used by Q CLI)
├── server_minimal.py             ← Minimal server (not used by Q CLI)
└── troubleshooter_old.py         ← Old troubleshooter implementation
```

### **Test and Debug Files**
```
tmp/test_files/
├── test_capabilities.py          ← Capability testing
├── test_capabilities_simple.py   ← Simple capability testing
├── test_intelligent_template.py  ← Template testing
├── test_mcp_server.py            ← MCP server testing
├── test_simple_template.py       ← Simple template testing
├── test_structure.py             ← Structure testing
├── test_troubleshooting.py       ← Troubleshooting testing
└── minimal_server.py             ← Minimal server implementation
```

## 🎯 **Key Points**

### **What Q CLI Actually Uses:**
1. `~/.aws/amazonq/mcp.json` → Points to executable script
2. `/Users/shantgup/bin/enhanced-cfn-mcp-server` → Runs Python with server_robust.py
3. `server_robust.py` → Contains all 13 working tools

### **What Q CLI Ignores:**
- `pyproject.toml` entry point (not used for MCP)
- `server.py` (despite being the "official" entry point)
- All other server_*.py files
- Test files and debug scripts

### **Critical Dependencies:**
- Python environment: `/Users/shantgup/Projects/cfn-troubleshooting-mcp/cfn-recovery-mcp/venv_new/bin/python`
- Working directory: `/Users/shantgup/Projects/cfn-mcp-server-2`
- AWS credentials: Inherited from environment

## 🛠 **Maintenance Commands**

### **Validate Setup:**
```bash
cd /Users/shantgup/Projects/cfn-mcp-server-2
python3 validate_setup.py
```

### **Check Tool Count:**
```bash
grep -c "@mcp.tool()" awslabs/cfn_mcp_server/server_robust.py
```

### **Test Server Compilation:**
```bash
python3 -m py_compile awslabs/cfn_mcp_server/server_robust.py
```

### **View Q CLI Configuration:**
```bash
cat ~/.aws/amazonq/mcp.json
```

## 🚨 **Warning**

**NEVER modify these files without understanding the impact:**
- `~/.aws/amazonq/mcp.json`
- `/Users/shantgup/bin/enhanced-cfn-mcp-server`
- `awslabs/cfn_mcp_server/server_robust.py`

**These files control the entire MCP server operation for Q CLI.**

## ✅ **Current Status**

- **13/13 tools loading successfully**
- **All configurations validated**
- **Clean project structure**
- **Unnecessary files archived**
- **Complete documentation available**

**System is fully operational and optimized!** 🎉
