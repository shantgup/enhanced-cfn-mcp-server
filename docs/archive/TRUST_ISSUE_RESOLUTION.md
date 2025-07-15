# MCP Tool Trust Issue Resolution Guide

## 🚨 **Current Issue**

Your MCP tools are showing as "not trusted" which prevents them from being used:

```
enhanced_cfn_mcp_server (MCP):
- enhanced_cfn_mcp_server___deploy_simple_stack                       * not trusted
- enhanced_cfn_mcp_server___generate_cloudformation_template          * not trusted
- enhanced_cfn_mcp_server___get_resource                              * not trusted
- enhanced_cfn_mcp_server___get_resource_schema_information           * not trusted
- enhanced_cfn_mcp_server___get_stack_status                            trusted
- enhanced_cfn_mcp_server___list_resources                            * not trusted
- enhanced_cfn_mcp_server___test_aws_connection                         trusted
```

## 🎯 **Root Cause**

The "not trusted" status occurs when:
1. **Tool signatures changed** - When I modified the tools, their signatures changed
2. **New tools added** - The troubleshooting and safeguard tools are new
3. **MCP cache issues** - Q CLI may have cached the old tool definitions

## ✅ **Resolution Steps**

### **Step 1: Restart Q CLI**
```bash
# Exit Q CLI completely
exit

# Restart Q CLI
q chat
```

### **Step 2: Clear MCP Cache (if restart doesn't work)**
```bash
# Clear Q CLI cache
rm -rf ~/.q/cache/mcp/
# or
rm -rf ~/.cache/q/mcp/

# Restart Q CLI
q chat
```

### **Step 3: Trust the Tools**
When Q CLI shows the tools, you'll need to trust them:

```
Do you want to trust these tools? (y/n): y
```

Or trust them individually when prompted.

### **Step 4: Verify Tool Access**
After trusting, verify the tools work:

```bash
# Test a basic tool
enhanced_cfn_mcp_server___test_aws_connection

# Test troubleshooting (this should now work)
enhanced_cfn_mcp_server___troubleshoot_stack
```

## 🔧 **Alternative: Reset MCP Configuration**

If the above doesn't work, you may need to reset the MCP configuration:

### **Option 1: Remove and Re-add MCP Server**
```bash
# Remove the MCP server from Q CLI configuration
# (This depends on how you added it - check your Q CLI config)

# Re-add the MCP server
# (Use the same method you used initially)
```

### **Option 2: Check Q CLI MCP Configuration**
```bash
# Check your Q CLI configuration file
cat ~/.q/config.json
# or
cat ~/.config/q/config.json

# Look for MCP server configuration and verify paths are correct
```

## 🎯 **Why This Happened**

### **Tool Signature Changes**
When I enhanced the tools, I added new parameters:
- `troubleshoot_stack` got `symptoms_description` parameter
- `deploy_simple_stack` got `capabilities`, `parameters`, `tags` parameters
- New tools were added entirely

### **Security Feature**
Q CLI's "not trusted" status is a security feature that:
- Prevents automatic execution of changed tools
- Requires explicit user approval for new/modified tools
- Protects against potentially malicious tool modifications

## 🚀 **Expected Outcome**

After following the resolution steps, you should see:

```
enhanced_cfn_mcp_server (MCP):
- enhanced_cfn_mcp_server___deploy_simple_stack                         trusted
- enhanced_cfn_mcp_server___generate_cloudformation_template            trusted
- enhanced_cfn_mcp_server___get_resource                                trusted
- enhanced_cfn_mcp_server___get_resource_schema_information             trusted
- enhanced_cfn_mcp_server___get_stack_status                            trusted
- enhanced_cfn_mcp_server___list_resources                              trusted
- enhanced_cfn_mcp_server___test_aws_connection                         trusted
- enhanced_cfn_mcp_server___troubleshoot_stack                          trusted
- enhanced_cfn_mcp_server___recover_stack                               trusted
- enhanced_cfn_mcp_server___detect_template_capabilities                trusted
- enhanced_cfn_mcp_server___detect_stack_drift                          trusted
- enhanced_cfn_mcp_server___cloudformation_best_practices_guide         trusted
- enhanced_cfn_mcp_server___prevent_out_of_band_changes                 trusted
```

## 🎉 **New Enhanced Tools Available**

Once trusted, you'll have access to all the enhanced capabilities:

### **Enhanced Deployment**
- `deploy_simple_stack` - Now with intelligent capability detection, parameters, and tags

### **Comprehensive Troubleshooting**
- `troubleshoot_stack` - Multi-dimensional failure analysis with CloudTrail integration
- `recover_stack` - Template-based recovery recommendations

### **Capability Management**
- `detect_template_capabilities` - Intelligent capability analysis

### **Anti-Pattern Prevention**
- `detect_stack_drift` - Configuration drift detection
- `cloudformation_best_practices_guide` - Workflow guidance
- `prevent_out_of_band_changes` - Anti-pattern prevention

## 🔍 **Troubleshooting**

### **If Tools Still Show as "Not Trusted"**
1. Check Q CLI version - ensure you're using a recent version
2. Verify MCP server path is correct in configuration
3. Check file permissions on the MCP server files
4. Look for error messages in Q CLI logs

### **If Specific Tools Don't Work**
1. Check for import errors in the MCP server
2. Verify all dependencies are installed
3. Test the MCP server independently

### **If You Get Import Errors**
The troubleshooting tools require the `CloudFormationTroubleshooter` class. If you get import errors:

```bash
# Verify the troubleshooter file exists
ls -la awslabs/cfn_mcp_server/troubleshooter.py

# Check for syntax errors
python3 -m py_compile awslabs/cfn_mcp_server/troubleshooter.py
```

## 🎯 **Next Steps**

1. **Restart Q CLI** and trust the tools
2. **Test basic functionality** with `test_aws_connection`
3. **Try troubleshooting** with `troubleshoot_stack`
4. **Explore new capabilities** like drift detection and best practices guidance

The enhanced CloudFormation MCP server is now ready to provide comprehensive infrastructure management with anti-pattern prevention! 🚀
