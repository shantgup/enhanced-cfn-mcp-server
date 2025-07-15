# Complete CloudFormation MCP Server System Documentation

## 🎯 **System Overview**

This document provides complete documentation of the working CloudFormation MCP Server setup, including all configurations, file locations, and the exact chain of execution.

## 📁 **Directory Structure**

```
/Users/shantgup/Projects/cfn-mcp-server-2/
├── awslabs/
│   └── cfn_mcp_server/
│       ├── server_robust.py          ← **ACTIVE SERVER** (13 tools)
│       ├── server.py                 ← Original server (18 tools, not used)
│       ├── server_enhanced.py        ← Enhanced server (13 tools, not used)
│       ├── server_working.py         ← Working server (5 tools, not used)
│       ├── server_minimal.py         ← Minimal server (3 tools, not used)
│       ├── aws_client.py             ← AWS client utilities
│       ├── troubleshooter.py         ← Troubleshooting classes
│       └── [other support files]
├── pyproject.toml                    ← Package configuration
└── [other files]

/Users/shantgup/bin/
└── enhanced-cfn-mcp-server          ← **EXECUTABLE SCRIPT** (Q CLI entry point)

~/.aws/amazonq/
└── mcp.json                         ← **Q CLI GLOBAL CONFIG**

/Users/shantgup/Projects/cfn-mcp-server-2/.amazonq/
└── mcp.json                         ← **Q CLI WORKSPACE CONFIG** (symlink)
```

## 🔗 **Execution Chain**

### **How Q CLI Loads the MCP Server:**

1. **Q CLI starts** → Reads configuration files
2. **Global config** (`~/.aws/amazonq/mcp.json`) → Specifies `enhanced-cfn-mcp-server`
3. **Executable script** (`/Users/shantgup/bin/enhanced-cfn-mcp-server`) → Runs Python command
4. **Python execution** → Loads `server_robust.py`
5. **MCP server starts** → Registers 13 tools
6. **Q CLI connects** → Shows all 13 tools

### **Detailed Execution Flow:**

```bash
Q CLI → ~/.aws/amazonq/mcp.json 
     → /Users/shantgup/bin/enhanced-cfn-mcp-server
     → /Users/shantgup/Projects/cfn-troubleshooting-mcp/cfn-recovery-mcp/venv_new/bin/python
     → -m awslabs.cfn_mcp_server.server_robust
     → 13 tools loaded and available
```

## 📋 **Configuration Files**

### **1. Q CLI Global Configuration**
**File:** `~/.aws/amazonq/mcp.json`
```json
{
  "mcpServers": {
    "amazon-internal-mcp-server": {
      "command": "amzn-mcp",
      "args": [],
      "env": {}
    },
    "enhanced-cfn-mcp-server": {
      "command": "/Users/shantgup/bin/enhanced-cfn-mcp-server",
      "args": [],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### **2. Q CLI Workspace Configuration**
**File:** `/Users/shantgup/Projects/cfn-mcp-server-2/.amazonq/mcp.json` (symlink)
**Target:** `/Users/shantgup/Projects/cfn-troubleshooting-mcp/cfn-recovery-mcp/mcp-client-config.json`
```json
{
  "mcpServers": {
    "cfn-recovery": {
      "url": "http://localhost:8082",
      "disabled": false,
      "autoApprove": [
        "create_template",
        "troubleshoot_stack",
        "recover_stack",
        "deploy_stack",
        "get_deployment_status"
      ]
    }
  }
}
```

### **3. Executable Script**
**File:** `/Users/shantgup/bin/enhanced-cfn-mcp-server`
```bash
#!/bin/bash
# Enhanced CloudFormation MCP Server Wrapper - Robust Version
# This script ensures AWS credentials are properly inherited

# Export current AWS environment variables if they exist
[ -n "$AWS_ACCESS_KEY_ID" ] && export AWS_ACCESS_KEY_ID
[ -n "$AWS_SECRET_ACCESS_KEY" ] && export AWS_SECRET_ACCESS_KEY
[ -n "$AWS_SESSION_TOKEN" ] && export AWS_SESSION_TOKEN
[ -n "$AWS_DEFAULT_REGION" ] && export AWS_DEFAULT_REGION
[ -n "$AWS_PROFILE" ] && export AWS_PROFILE

# Change to the project directory
cd /Users/shantgup/Projects/cfn-mcp-server-2

# Run the robust MCP server
exec /Users/shantgup/Projects/cfn-troubleshooting-mcp/cfn-recovery-mcp/venv_new/bin/python -m awslabs.cfn_mcp_server.server_robust "$@"
```

### **4. Package Configuration**
**File:** `pyproject.toml`
```toml
[project.scripts]
"awslabs.cfn-mcp-server" = "awslabs.cfn_mcp_server.server:main"
```
**Note:** This entry point is NOT used by Q CLI. Q CLI uses the executable script instead.

## 🛠 **Active Server File**

### **File:** `awslabs/cfn_mcp_server/server_robust.py`

**Total Tools:** 13

**Tool List:**
1. ✅ `get_resource_schema_information` - Get CloudFormation resource schema
2. ✅ `list_resources` - List AWS resources using Cloud Control API
3. ✅ `get_resource` - Get specific AWS resource details
4. ✅ `test_aws_connection` - Test AWS credentials and connection
5. ✅ `generate_cloudformation_template` - Generate CFN templates from descriptions
6. ✅ `deploy_simple_stack` - Deploy CloudFormation stacks with capabilities
7. ✅ `get_stack_status` - Get CloudFormation stack status and information
8. ✅ `troubleshoot_cloudformation_stack` - **NEW** - Comprehensive stack troubleshooting
9. ✅ `fix_and_retry_cloudformation_stack` - **NEW** - Stack recovery recommendations
10. ✅ `detect_template_capabilities` - **NEW** - Analyze template capability requirements
11. ✅ `detect_stack_drift` - **NEW** - Detect configuration drift
12. ✅ `cloudformation_best_practices_guide` - **NEW** - Best practices guidance
13. ✅ `prevent_out_of_band_changes` - **NEW** - Anti-pattern prevention

## 🔧 **Key Technical Details**

### **Python Environment:**
- **Python Path:** `/Users/shantgup/Projects/cfn-troubleshooting-mcp/cfn-recovery-mcp/venv_new/bin/python`
- **Working Directory:** `/Users/shantgup/Projects/cfn-mcp-server-2`
- **Module Path:** `awslabs.cfn_mcp_server.server_robust`

### **AWS Integration:**
- **Client Function:** `get_aws_client()` from `aws_client.py`
- **Credentials:** Inherited from environment variables
- **Regions:** Configurable per tool call

### **MCP Framework:**
- **Framework:** FastMCP
- **Tool Registration:** `@mcp.tool()` decorators
- **Tool Count:** 13 tools successfully registered

## 🎯 **Why This Setup Works**

### **1. Correct File Chain:**
- Q CLI → Executable script → server_robust.py ✅
- NOT: Q CLI → pyproject.toml → server.py ❌

### **2. Proper Tool Positioning:**
- All 13 tools positioned before `main()` function ✅
- No tools after main() that would be ignored ✅

### **3. No Dependency Issues:**
- Uses existing `get_aws_client()` function ✅
- No problematic imports that fail during registration ✅

### **4. Configuration Hierarchy:**
- Global config defines the server ✅
- Workspace config adds additional servers ✅
- No conflicts between configurations ✅

## 🚨 **Critical Files - DO NOT MODIFY**

### **Essential Files:**
1. `~/.aws/amazonq/mcp.json` - Q CLI global configuration
2. `/Users/shantgup/bin/enhanced-cfn-mcp-server` - Executable script
3. `awslabs/cfn_mcp_server/server_robust.py` - Active server with 13 tools
4. `awslabs/cfn_mcp_server/aws_client.py` - AWS client utilities

### **Files Safe to Modify/Remove:**
- `server_enhanced.py` - Not used by Q CLI
- `server_working.py` - Not used by Q CLI
- `server_minimal.py` - Not used by Q CLI
- `server.py` - Not used by Q CLI (despite pyproject.toml entry)

## 📊 **Tool Status Summary**

```
enhanced_cfn_mcp_server (MCP): 13 tools total
- enhanced_cfn_mcp_server___deploy_simple_stack                       ✅ trusted
- enhanced_cfn_mcp_server___generate_cloudformation_template          ✅ trusted
- enhanced_cfn_mcp_server___get_resource                              ✅ trusted
- enhanced_cfn_mcp_server___get_resource_schema_information           ✅ trusted
- enhanced_cfn_mcp_server___get_stack_status                          ✅ trusted
- enhanced_cfn_mcp_server___list_resources                            ✅ trusted
- enhanced_cfn_mcp_server___test_aws_connection                       ✅ trusted
- enhanced_cfn_mcp_server___troubleshoot_cloudformation_stack         ✅ trusted
- enhanced_cfn_mcp_server___fix_and_retry_cloudformation_stack        ✅ trusted
- enhanced_cfn_mcp_server___detect_template_capabilities              ✅ trusted
- enhanced_cfn_mcp_server___detect_stack_drift                        ✅ trusted
- enhanced_cfn_mcp_server___cloudformation_best_practices_guide       ✅ trusted
- enhanced_cfn_mcp_server___prevent_out_of_band_changes               ✅ trusted
```

## 🎉 **Success Metrics**

- ✅ **13/13 tools loading** (was 7/13)
- ✅ **All tools trusted** and functional
- ✅ **AWS connection working** (Account: 285005585511)
- ✅ **Troubleshooting capabilities** added
- ✅ **Anti-pattern prevention** implemented
- ✅ **Configuration drift detection** available

## 📝 **Maintenance Notes**

### **To Add New Tools:**
1. Add to `server_robust.py` before `main()` function
2. Use `@mcp.tool()` decorator
3. Use existing `get_aws_client()` for AWS operations
4. Restart Q CLI to load new tools

### **To Modify Existing Tools:**
1. Edit `server_robust.py`
2. Restart Q CLI to reload changes
3. Re-trust tools if signatures change

### **To Debug Issues:**
1. Check Q CLI configuration: `~/.aws/amazonq/mcp.json`
2. Verify executable script: `/Users/shantgup/bin/enhanced-cfn-mcp-server`
3. Test server file: `python3 -m py_compile awslabs/cfn_mcp_server/server_robust.py`
4. Check tool count: `grep -c "@mcp.tool()" awslabs/cfn_mcp_server/server_robust.py`

---

**Last Updated:** June 18, 2025
**Status:** ✅ FULLY OPERATIONAL - All 13 tools loading successfully
**Next Review:** When adding new tools or modifying configurations
