# Enhanced CloudFormation MCP Server

An AWS CloudFormation MCP server that **automatically troubleshoots stack failures** using real AWS data and expert guidance. When your CloudFormation stack fails, this server collects AWS logs, analyzes the failure, and provides step-by-step fix instructions.

## What This Actually Does

This MCP server has 22 tools, but the core value is **automated CloudFormation troubleshooting**:

1. **Collects real AWS data** - Stack events, CloudWatch logs, CloudTrail events, resource states
2. **Analyzes failure patterns** - Correlates errors across AWS services to find root causes  
3. **Provides expert guidance** - Gives you specific AWS CLI commands and fix instructions
4. **Fixes issues automatically** - Can apply template fixes and retry deployments

Everything else (basic CRUD operations, template generation) supports this core troubleshooting workflow.

## Quick Start

```bash
git clone https://github.com/shantgup/enhanced-cfn-mcp-server.git
cd enhanced-cfn-mcp-server
./setup.sh
q chat
```

**Requirements:** Python 3.10+ and AWS CLI configured with credentials.

## Core Troubleshooting Workflow

### 1. Enhanced Stack Analysis
The `enhanced_troubleshoot_cloudformation_stack` tool does the heavy lifting:

```
User: "My CloudFormation stack failed, help me troubleshoot it"
↓
Tool collects AWS data:
- Stack events (describe-stack-events)
- Resource states (describe-stack-resources) 
- CloudWatch logs (filter-log-events)
- CloudTrail events (lookup-events)
- Template analysis (get-template)
↓
Tool analyzes failure patterns:
- Correlates errors across resources
- Identifies root causes
- Matches patterns to known scenarios
↓
Tool provides context recommendations:
- "This looks like a custom resource failure"
- "Call get_cloudformation_context('custom_resource_debugging')"
```

### 2. Context-Driven Guidance
The context system provides expert troubleshooting workflows:

**Context Files Available:**
- `custom_resource_debugging.json` - Lambda-backed custom resource failures
- `nested_stack_troubleshooting.json` - Nested CloudFormation stack issues
- `drift_detection_guide.json` - Out-of-band resource modifications
- `permission_issues_guide.json` - IAM and access problems
- `rollback_analysis_guide.json` - Rollback scenarios and recovery

**Each context includes:**
- Step-by-step diagnosis procedures
- Common failure causes with likelihood ratings
- Specific AWS CLI commands to run
- Code examples for fixes
- Prevention strategies

### 3. Autonomous Fixing
The `autonomous_fix_and_deploy_stack` tool can fix and redeploy automatically:

```
Tool analyzes template → Identifies issues → Applies fixes → Redeploys → Monitors → Repeats if needed
```

## Real Example: Custom Resource Failure

Here's how the server handled an actual custom resource failure:

### The Problem
Stack `failing-custom-resource-test` failed with:
```
ResourceStatusReason: "CloudFormation did not receive a response from your Custom Resource. 
Please check your logs for requestId [c718b62b-b361-4a4e-bbb8-6b4cbc41c08b]"
```

### What The Server Did

**Step 1: Data Collection**
```
enhanced_troubleshoot_cloudformation_stack() called
↓ 
Collected stack events, found failed resource: FailingCustomResource
↓
Extracted ServiceToken: arn:aws:lambda:us-east-1:285005585511:function:failing-custom-resource-test-failing-custom-resource
↓
Found RequestId in error message: c718b62b-b361-4a4e-bbb8-6b4cbc41c08b
```

**Step 2: Pattern Matching**
```
Analysis detected: "Custom resource failures" trigger
↓
Recommended context: custom_resource_debugging
↓
get_cloudformation_context('custom_resource_debugging') called
```

**Step 3: Expert Guidance Provided**
```
Context provided:
- Diagnosis steps: "Extract RequestId from CloudFormation error"
- Investigation command: aws logs filter-log-events --log-group-name /aws/lambda/failing-custom-resource-test-failing-custom-resource
- Root cause identified: "Lambda throws exception without sending response to CloudFormation"
- Fix provided: Complete Python code with proper error handling
```

**Step 4: AWS CLI Execution**
```
Server executed: aws logs get-log-events --log-group-name /aws/lambda/failing-custom-resource-test-failing-custom-resource
↓
Found Lambda logs showing: Exception thrown, no response sent to ResponseURL
↓
Confirmed root cause: Lambda needs to call CloudFormation ResponseURL even on failure
```

**Result:** Complete diagnosis with specific fix code in under 2 minutes.

## Tool Categories

### Core Troubleshooting Tools
| Tool | Purpose |
|------|---------|
| `enhanced_troubleshoot_cloudformation_stack` | **Primary troubleshooter** - Collects AWS data, analyzes failures, provides context recommendations |
| `get_cloudformation_context` | **Expert guidance** - Returns step-by-step troubleshooting workflows for specific scenarios |
| `autonomous_fix_and_deploy_stack` | **Autonomous fixing** - Iteratively fixes templates and redeploys until successful |

### Supporting Analysis Tools  
| Tool | Purpose |
|------|---------|
| `analyze_template_structure` | Deep template analysis for security, compliance, best practices |
| `generate_template_fixes` | Automated template issue detection and fixing |
| `detect_template_capabilities` | Determines required IAM capabilities |
| `prevent_out_of_band_changes` | Prevents manual changes to CloudFormation-managed resources |

### Stack Operations
| Tool | Purpose |
|------|---------|
| `deploy_cloudformation_stack` | Deploy stacks with comprehensive monitoring |
| `delete_cloudformation_stack` | Delete stacks with resource retention options |

### Template Generation
| Tool | Purpose |
|------|---------|
| `generate_cloudformation_template` | Multi-stage conversation for template creation |
| `create_template` | Generate templates from existing AWS resources |

### AWS Resource Management
| Tool | Purpose |
|------|---------|
| `get_resource_schema_information` | Get AWS resource type schemas |
| `list_resources` | List AWS resources by type |
| `get_resource` | Get details of specific resources |
| `create_resource` | Create AWS resources |
| `update_resource` | Update resources using JSON Patch |
| `delete_resource` | Delete AWS resources |
| `get_resource_request_status` | Check status of long-running operations |

### Best Practices & Guidance
| Tool | Purpose |
|------|---------|
| `cloudformation_best_practices_guide` | Expert best practices guidance for any infrastructure scenario |

## How Tool Chaining Works

Tools are designed to work together in troubleshooting workflows:

```
1. enhanced_troubleshoot_cloudformation_stack
   ↓ (identifies failure pattern)
2. get_cloudformation_context  
   ↓ (provides specific guidance)
3. AWS CLI commands (via context instructions)
   ↓ (collects additional data)
4. generate_template_fixes (if template issues found)
   ↓ (applies fixes)
5. deploy_cloudformation_stack (redeploy with fixes)
```

## Context System Deep Dive

### Context File Structure
Each context file is a JSON document with this structure:

```json
{
  "scenario": "custom_resource_debugging",
  "when_to_use": ["Custom resource shows CREATE_FAILED", "Error mentions ServiceToken"],
  "diagnosis_steps": [
    {
      "step": 1,
      "action": "Identify the custom resource", 
      "details": "Look for resources with Type: Custom::*",
      "what_to_look_for": "Resource type starting with 'Custom::'"
    }
  ],
  "common_causes": [
    {
      "cause": "No response sent to CloudFormation",
      "likelihood": "VERY_HIGH",
      "indicators": ["CloudFormation did not receive a response"]
    }
  ],
  "investigation_commands": [
    {
      "command": "aws logs filter-log-events --log-group-name /aws/lambda/{function_name}",
      "purpose": "Get Lambda execution logs",
      "parameters_needed": ["function_name"]
    }
  ],
  "resolution_strategies": [
    {
      "scenario": "Invalid response format",
      "steps": ["Ensure Lambda returns Status: SUCCESS or FAILED"],
      "code_example": { "language": "python", "snippet": "..." }
    }
  ]
}
```

### Trigger Matching Algorithm
The enhanced troubleshooter matches failures to contexts using:

1. **Resource Type Patterns** - `Custom::*` → custom_resource_debugging
2. **Error Message Keywords** - "already exists" → drift_detection_guide  
3. **Stack Status Patterns** - `ROLLBACK_COMPLETE` → rollback_analysis_guide
4. **Service Indicators** - IAM errors → permission_issues_guide

### Adding New Contexts
To add a new troubleshooting scenario:

1. Create JSON file in `awslabs/cfn_mcp_server/context_files/`
2. Follow the structure above
3. Add trigger patterns to `enhanced_troubleshooter.py`
4. Context automatically loads via `context_loader.py`

## Installation & Configuration

### 1. Install Package
```bash
git clone https://github.com/shantgup/enhanced-cfn-mcp-server.git
cd enhanced-cfn-mcp-server
pip install -e .
```

### 2. Configure AWS
```bash
aws configure
# Or set environment variables:
# export AWS_ACCESS_KEY_ID=your_key
# export AWS_SECRET_ACCESS_KEY=your_secret  
# export AWS_DEFAULT_REGION=us-east-1
```

### 3. Use with Amazon Q CLI
Auto-loads when you run `q chat` in the project directory (configured in `.amazonq/mcp_servers.json`).

For manual configuration elsewhere:
```json
{
  "mcpServers": {
    "enhanced-cfn": {
      "command": "python",
      "args": ["-m", "awslabs.cfn_mcp_server.server"],
      "env": {}
    }
  }
}
```

## Usage Examples

### Troubleshoot Any Stack Failure
```
"My CloudFormation stack 'production-app' failed during deployment. Help me troubleshoot it."
```

### Autonomous Fix and Deploy
```
"Automatically fix and deploy my CloudFormation stack 'broken-stack' until it succeeds."
```

### Security Analysis
```
"Analyze my CloudFormation template for security vulnerabilities and compliance issues."
```

### Template Generation
```
"Create a CloudFormation template for a web application with ALB, ECS, and RDS."
```

## AWS Permissions Required

Your AWS credentials need:
- **CloudFormation operations**: `cloudformation:*`
- **CloudControl API**: `cloudcontrol:*` 
- **Resource-specific permissions**: `s3:*`, `ec2:*`, etc.
- **CloudWatch Logs**: `logs:*`
- **CloudTrail access**: `cloudtrail:LookupEvents`

## Limitations & Gotchas

### What This Tool Can't Do
- **Fix infrastructure-level issues** - Can't resolve AWS service outages or account limits
- **Handle cross-account dependencies** - Limited to single AWS account context
- **Resolve external dependencies** - Can't fix issues with third-party services
- **Bypass IAM restrictions** - Requires proper AWS permissions to function

### Common Gotchas
- **Large stacks** - Analysis may be slow for stacks with 100+ resources
- **Custom resources** - Limited to Lambda-backed custom resources (no SNS-backed)
- **Nested stacks** - Deep nesting (5+ levels) may cause incomplete analysis
- **Regional resources** - Some analysis requires resources to be in the same region

### When to Use Alternatives
- **Simple syntax errors** - Use `aws cloudformation validate-template` directly
- **Large-scale deployments** - Consider AWS CDK or Terraform for complex infrastructure
- **Production incidents** - Use AWS Support for critical production issues

## FAQ

### Why not just use AWS CLI directly?
**Direct answer:** You could, but you'd need to run 15-20 commands manually, correlate the data yourself, and know which logs to check. This tool does all that automatically and gives you the exact fix.

**Example:** For the custom resource failure above, you'd need to:
1. `aws cloudformation describe-stack-events` 
2. Parse events to find the failed resource
3. Extract the Lambda function name from ServiceToken
4. `aws logs describe-log-streams` to find log streams
5. `aws logs get-log-events` to get actual logs
6. Correlate RequestId between CloudFormation and Lambda
7. Analyze the logs to understand the failure
8. Know that custom resources must send responses even on failure
9. Write the fix code

This tool does steps 1-9 automatically in one command.

### How is this better than existing CloudFormation tools?
**Direct answer:** Existing tools show you what failed. This tool shows you why it failed and how to fix it.

**Comparison:**
- **AWS Console**: Shows stack events, but you have to interpret them
- **AWS CLI**: Gives you raw data, but no analysis or guidance  
- **CloudFormation Linter**: Catches syntax issues, but not runtime failures
- **This tool**: Collects data + analyzes failures + provides specific fixes

### Is this just another ChatGPT wrapper?
**Direct answer:** No. This tool makes real AWS API calls, collects actual data from your account, and provides structured troubleshooting workflows. The "AI" part is just the interface - the core functionality is AWS data collection and analysis.

**What it actually does:**
- Calls `describe-stack-events`, `filter-log-events`, `lookup-events`
- Parses CloudFormation templates and validates syntax
- Correlates errors across AWS services
- Matches failure patterns to known troubleshooting procedures
- Provides specific AWS CLI commands to run

### Will this work with my existing CloudFormation setup?
**Direct answer:** Yes, if you have AWS CLI access. This tool only reads your existing stacks and resources - it doesn't change your setup unless you explicitly ask it to deploy or fix something.

**Requirements:**
- AWS CLI configured with credentials
- CloudFormation read permissions
- CloudWatch Logs read permissions (for troubleshooting)

## Architecture

```
Enhanced CFN MCP Server
├── FastMCP Framework (MCP server foundation)
├── AWS Client Management (Boto3 integration)
├── Enhanced Troubleshooter (Data collection + failure analysis)
│   ├── Stack Event Analysis
│   ├── CloudWatch Log Correlation  
│   ├── CloudTrail Event Analysis
│   └── Template Structure Analysis
├── Context System (Expert guidance workflows)
│   ├── Context Loader (JSON file management)
│   ├── Trigger Matching (Failure pattern recognition)
│   └── Context Files (5 troubleshooting scenarios)
├── Template Operations (Generation & analysis)
├── Autonomous Deployer (Iterative fix-and-deploy)
├── Template Fixer (Automated issue resolution)
└── Resource Operations (CloudControl API)
```

## Key Files

- `server.py` - Main MCP server with 22 tools
- `enhanced_troubleshooter.py` - Core troubleshooting engine with AWS data collection
- `context_loader.py` - Context system management
- `context_files/` - 5 JSON files with expert troubleshooting workflows
- `autonomous_deployer.py` - Iterative deployment with automatic fixing
- `template_fixer.py` - Automated template issue detection and fixing
- `template_analyzer.py` - Template structure analysis and validation
- `stack_manager.py` - CloudFormation stack operations

## Development

```bash
# Install for development
pip install -e ".[dev]"

# Run tests  
pytest

# Format code
ruff format .

# Type checking
pyright
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.

## Support

- **Issues**: [GitHub Issues](https://github.com/shantgup/enhanced-cfn-mcp-server/issues)
- **Documentation**: [Project Wiki](https://github.com/shantgup/enhanced-cfn-mcp-server/wiki)

Built on [AWS Labs MCP](https://github.com/awslabs/mcp) and the [Model Context Protocol](https://modelcontextprotocol.io/).
