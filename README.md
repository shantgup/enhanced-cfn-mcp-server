# Enhanced CloudFormation MCP Server

An AWS CloudFormation MCP server that combines real AWS operations with expert guidance prompts. Works with AI assistants like Amazon Q to provide both immediate technical capability and expert-level CloudFormation guidance.

## Quick Start

```bash
git clone https://github.com/shantgup/enhanced-cfn-mcp-server.git
cd enhanced-cfn-mcp-server
./setup.sh
q chat
```

**Requirements:** Python 3.10+ and AWS CLI configured with credentials.

## What This Does

This MCP server has 22 tools that do two main things:

1. **Make real AWS API calls** - Create, read, update, delete AWS resources and CloudFormation stacks
2. **Generate expert prompts** - Create structured guidance that helps AI assistants provide expert-level CloudFormation advice

Instead of just basic CloudFormation operations, you get expert troubleshooting workflows, security analysis, and best practices guidance.

## Available Tools

### AWS Resource Management
| Tool | What It Does |
|------|-------------|
| `get_resource_schema_information` | Get AWS resource type schemas |
| `list_resources` | List AWS resources by type |
| `get_resource` | Get details of specific resources |
| `create_resource` | Create AWS resources |
| `update_resource` | Update resources using JSON Patch |
| `delete_resource` | Delete AWS resources |
| `get_resource_request_status` | Check status of long-running operations |

### CloudFormation Stack Operations
| Tool | What It Does |
|------|-------------|
| `deploy_cloudformation_stack` | Deploy stacks with parameters and tags |
| `get_stack_status` | Get stack status with expert analysis prompts |
| `delete_cloudformation_stack` | Delete stacks with resource retention options |
| `detect_stack_drift` | Check for configuration drift with analysis prompts |

### Template Generation & Analysis
| Tool | What It Does |
|------|-------------|
| `generate_cloudformation_template` | Generate templates from natural language with multi-stage conversation |
| `create_template` | Generate templates from existing AWS resources |
| `analyze_template_structure` | Analyze templates for security, compliance, and best practices |
| `detect_template_capabilities` | Check what IAM capabilities templates need |
| `generate_template_fixes` | Find and fix template issues automatically |

### Enhanced Troubleshooting
| Tool | What It Does |
|------|-------------|
| `troubleshoot_cloudformation_stack` | Basic troubleshooting with expert guidance prompts |
| `enhanced_troubleshoot_cloudformation_stack` | Advanced troubleshooting with AWS data collection and expert analysis |
| `fix_and_retry_cloudformation_stack` | Fix templates and retry deployment with guidance |
| `autonomous_fix_and_deploy_stack` | Fully autonomous deployment with iterative fixing |

### Best Practices & Guidance
| Tool | What It Does |
|------|-------------|
| `cloudformation_best_practices_guide` | Expert best practices guidance for any infrastructure scenario |
| `prevent_out_of_band_changes` | Prevent manual changes to CloudFormation-managed resources |

## Installation

### 1. Install the Package

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

If you run `q chat` in the project directory, the server loads automatically (configured in `.amazonq/mcp_servers.json`).

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

### One-Shot Deployment
```
"Use the enhanced cfn mcp server to create a robust web server architecture cloudformation template. Then deploy it, and if it fails, troubleshoot it, fix the template and redeploy until successful."
```

### Basic Operations
```bash
# List S3 buckets
"List all my S3 buckets"

# Create a bucket
"Create an S3 bucket named 'my-app-bucket' with versioning enabled"

# Deploy a stack
"Deploy a CloudFormation stack named 'web-app' using template.yaml"
```

### Advanced Operations
```bash
# Troubleshoot failures
"My CloudFormation stack 'app-stack' failed. Help me troubleshoot it."

# Autonomous fixing
"Automatically fix and deploy my CloudFormation stack 'broken-stack'"

# Security analysis
"Analyze my template for security vulnerabilities and compliance issues"
```

## How It Works

### Real AWS Operations (60-90% per tool)
- Makes actual AWS API calls (`describe_stacks`, `create_stack`, `get_template`, etc.)
- Collects CloudWatch logs and CloudTrail events
- Parses and validates CloudFormation templates
- Applies automated fixes based on 50+ validation rules
- Manages deployments with waiters and error handling

### Expert Prompt Enhancement (10-40% per tool)
- Generates structured troubleshooting workflows
- Creates expert-level guidance prompts
- Provides step-by-step investigation procedures
- Offers multiple solution approaches with trade-offs
- Includes AWS CLI commands for verification

### Example: Enhanced vs Basic Troubleshooting

**Basic request:**
```
"Help me troubleshoot my CloudFormation stack"
```

**Enhanced prompt generated:**
```
You are a CloudFormation expert with 10+ years of AWS experience. 

INVESTIGATION WORKFLOW:
1. Check stack events for failure patterns
2. Analyze resource dependencies and circular references
3. Review CloudWatch logs for error messages
4. Examine CloudTrail for API call failures
5. Validate template syntax and resource properties

COMMON FAILURE PATTERNS:
- Resource limit exceeded: Check service quotas
- Permission denied: Verify IAM roles and policies
- Resource conflicts: Check for naming collisions
- Timeout issues: Review resource creation times

DIAGNOSTIC COMMANDS:
aws cloudformation describe-stack-events --stack-name {stack_name}
aws logs filter-log-events --log-group-name /aws/lambda/{function_name}

REMEDIATION STRATEGIES:
[Specific fixes based on actual failure analysis]
```

## AWS Permissions Required

Your AWS credentials need:
- CloudFormation operations (`cloudformation:*`)
- CloudControl API operations (`cloudcontrol:*`)
- Resource-specific permissions (`s3:*`, `ec2:*`, etc.)
- CloudWatch Logs access (`logs:*`)
- CloudTrail access (`cloudtrail:LookupEvents`)

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

## Architecture

```
Enhanced CFN MCP Server
├── FastMCP Framework (MCP server foundation)
├── AWS Client Management (Boto3 integration)
├── Resource Operations (CloudControl API)
├── Stack Operations (CloudFormation API)
├── Template Operations (Generation & analysis)
├── Enhanced Troubleshooter (Data collection + analysis)
├── Autonomous Deployer (Iterative fix-and-deploy)
├── Template Fixer (Automated issue resolution)
└── Prompt Generator (Expert guidance creation)
```

## Key Files

- `server.py` - Main MCP server with 22 tools
- `enhanced_troubleshooter.py` - Advanced stack analysis with AWS data collection
- `autonomous_deployer.py` - Iterative deployment with automatic fixing
- `template_fixer.py` - Automated template issue detection and fixing
- `template_analyzer.py` - Template structure analysis and validation
- `stack_manager.py` - CloudFormation stack operations

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.

## Support

- **Issues**: [GitHub Issues](https://github.com/shantgup/enhanced-cfn-mcp-server/issues)
- **Documentation**: [Project Wiki](https://github.com/shantgup/enhanced-cfn-mcp-server/wiki)

Built on [AWS Labs MCP](https://github.com/awslabs/mcp) and the [Model Context Protocol](https://modelcontextprotocol.io/).
