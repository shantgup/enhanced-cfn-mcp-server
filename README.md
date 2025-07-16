# Enhanced CloudFormation MCP Server

An enhanced AWS CloudFormation Model Context Protocol (MCP) server that provides intelligent prompting, autonomous fixing, and comprehensive AWS resource management capabilities for AI assistants like Amazon Q.

## 🚀 What is this?

This is an enhanced version of the AWS CloudFormation MCP server that extends the original functionality with:

- **Intelligent Prompt Generation**: Creates expert-level prompts that guide AI assistants to provide comprehensive CloudFormation analysis and solutions
- **Autonomous Template Fixing**: Automatically detects and fixes common CloudFormation template issues
- **Enhanced Troubleshooting**: Provides detailed error analysis with step-by-step resolution guidance
- **Best Practices Integration**: Built-in AWS best practices and security recommendations
- **Comprehensive Resource Management**: Full CRUD operations for AWS resources via CloudFormation types

## ✨ Key Features & Differentiators

### 🧠 Intelligent AI Guidance
- **Expert Prompt Engineering**: Transforms simple requests into comprehensive, expert-level prompts
- **Context-Aware Analysis**: Provides detailed investigation workflows with specific CLI commands
- **Multi-Stage Conversations**: Guides through discovery, refinement, validation, and generation phases

### 🔧 Autonomous Problem Solving
- **Auto-Fix Templates**: Automatically identifies and fixes common CloudFormation issues
- **Iterative Deployment**: Continues fixing and redeploying until successful
- **Smart Error Recovery**: Analyzes failures and applies appropriate fixes

### 📊 Enhanced Troubleshooting
- **Root Cause Analysis**: Deep investigation of CloudFormation failures
- **CloudWatch Integration**: Automatic log analysis and error correlation
- **CloudTrail Analysis**: API call investigation for comprehensive debugging

### 🛡️ Security & Best Practices
- **Security Vulnerability Detection**: Identifies potential security issues in templates
- **Compliance Framework Alignment**: Supports HIPAA, PCI, SOX, GDPR compliance checks
- **Cost Optimization**: Provides cost-aware recommendations

## 🛠️ Available Tools

### Core Resource Management
| Tool | Description |
|------|-------------|
| `get_resource_schema_information` | Get schema information for AWS resource types |
| `list_resources` | List AWS resources of a specified type |
| `get_resource` | Get detailed information about a specific resource |
| `create_resource` | Create new AWS resources |
| `update_resource` | Update existing AWS resources using JSON Patch |
| `delete_resource` | Delete AWS resources |
| `get_resource_request_status` | Check status of long-running operations |

### CloudFormation Stack Management
| Tool | Description |
|------|-------------|
| `deploy_cloudformation_stack` | Deploy stacks with comprehensive configuration |
| `get_stack_status` | Get detailed stack status with operational analysis |
| `delete_cloudformation_stack` | Safely delete stacks with resource retention options |
| `detect_stack_drift` | Detect and analyze configuration drift |

### Template Generation & Analysis
| Tool | Description |
|------|-------------|
| `generate_cloudformation_template` | Generate templates from natural language with intelligent conversation flow |
| `create_template` | Generate templates from existing AWS resources |
| `analyze_template_structure` | Comprehensive template analysis with security and compliance checks |
| `detect_template_capabilities` | Analyze templates for required IAM capabilities |

### Enhanced Troubleshooting & Fixing
| Tool | Description |
|------|-------------|
| `troubleshoot_cloudformation_stack` | Expert troubleshooting with systematic investigation |
| `fix_and_retry_cloudformation_stack` | Intelligent fix-and-retry with detailed guidance |
| `autonomous_fix_and_deploy_stack` | Fully autonomous deployment with iterative fixing |
| `generate_template_fixes` | Generate and optionally apply template fixes |

### Best Practices & Guidance
| Tool | Description |
|------|-------------|
| `cloudformation_best_practices_guide` | Expert best practices guidance for infrastructure issues |
| `prevent_out_of_band_changes` | Prevent manual changes to CloudFormation-managed resources |

## 📋 Prerequisites

- **Python 3.10+**
- **AWS CLI configured** with appropriate credentials
- **Amazon Q CLI** (for integration)
- **AWS Account** with necessary permissions

### Required AWS Permissions

Your AWS credentials need permissions for:
- CloudFormation operations (`cloudformation:*`)
- CloudControl API operations (`cloudcontrol:*`)
- Resource-specific permissions (e.g., `s3:*`, `ec2:*`)
- CloudWatch Logs access (`logs:*`)
- CloudTrail access (`cloudtrail:LookupEvents`)

## 🚀 Installation & Setup

### 1. Install the Package

```bash
# Clone the repository
git clone https://github.com/shantgup/enhanced-cfn-mcp-server.git
cd enhanced-cfn-mcp-server

# Install the package
pip install -e .

```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Integration with Amazon Q CLI

If you run q in the root directory of this project, the enhanced_cfn_mcp_server should be loaded automatically, it's configured in the .amazonq directory. 

Optionally, you can add the MCP server to your Q CLI configuration like below:

```json
{
  "mcpServers": {
    "enhanced-cfn": {
      "command": "enhanced-cfn-mcp-server",
      "args": [],
      "env": {}
    }
  }
}
```

### 4. Verify Installation

```bash
# Test through Q CLI
q chat
# Then ask: "Use the enhanced cfn mcp server to create a robust web server architecture cloudformation template. Then deploy it, and if it fails, troubleshoot it, fix the template and redeploy until successful."
```

## 💡 Usage Examples

### One-shot Prompt - Generate template, deploy, troubleshoot, fix and redeploy until successful

```bash
# Generate template, deploy, troubleshoot, fix and redeploy until successful
"Use the enhanced cfn mcp server to create a <INSERT USE CASE HERE>. Then deploy it, and if it fails, troubleshoot it, fix the template and redeploy until successful."

# Use case examples:
- robust web server architecture
- secure VPC with public and private subnets
- serverless API with Lambda and API Gateway
- multi-AZ RDS database setup
- static website hosting with S3 and CloudFront
- auto-scaling application with ALB
- containerized application using ECS
- serverless data processing pipeline
- high-availability WordPress site
- CI/CD pipeline with CodePipeline
- cross-region backup solution
- ElasticSearch cluster
- EKS cluster with worker nodes
- real-time data streaming architecture
- multi-region active-active setup


### Basic Resource Management

```bash
# In Q CLI chat
q chat

# List all S3 buckets
"List all my S3 buckets"

# Get details of a specific bucket
"Show me details of my bucket named 'my-app-bucket'"

# Create a new S3 bucket
"Create an S3 bucket named 'my-new-bucket' with versioning enabled"
```

### CloudFormation Operations

```bash
# Generate a template from description
"Create a CloudFormation template for a web application with ALB, ECS, and RDS"

# Deploy a stack
"Deploy a CloudFormation stack named 'my-web-app' using the template in ./template.yaml"

# Troubleshoot a failed deployment
"My CloudFormation stack 'my-app-stack' failed to deploy. Help me troubleshoot it."

# Autonomous fixing and deployment
"Automatically fix and deploy my CloudFormation stack 'problematic-stack'"
```

### Advanced Analysis

```bash
# Analyze template for issues
"Analyze my CloudFormation template for security vulnerabilities and best practices"

# Detect stack drift
"Check if my production stack has any configuration drift"

# Get best practices guidance
"I need to implement a HIPAA-compliant data processing pipeline. What are the best practices?"
```


## 🏗️ Architecture

```
Enhanced CFN MCP Server
├── Core MCP Server (FastMCP)
├── AWS Client Management
├── CloudFormation Stack Manager
├── Resource Schema Manager
├── Intelligent Prompt Generator
├── Template Analysis Engine
├── Autonomous Fixing Engine
└── Best Practices Database
```

### Key Components

- **FastMCP Framework**: Provides the MCP server foundation
- **AWS Integration**: Boto3-based AWS service clients
- **CloudControl API**: Unified resource management interface
- **Template Generator**: Natural language to CloudFormation conversion
- **Error Analysis**: Comprehensive failure analysis and resolution
- **Prompt Engineering**: Expert-level prompt generation for AI guidance

## 🔧 Configuration

### Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Server Configuration
MCP_SERVER_PORT=3000
LOG_LEVEL=INFO

# Feature Flags
ENABLE_AUTO_FIX=true
ENABLE_SECURITY_ANALYSIS=true
MAX_FIX_ITERATIONS=5
```

### Advanced Configuration

Create a `config.yaml` file:

```yaml
aws:
  region: us-east-1
  profile: default
  
server:
  port: 3000
  log_level: INFO
  
features:
  auto_fix: true
  security_analysis: true
  max_fix_iterations: 5
  
templates:
  default_capabilities:
    - CAPABILITY_IAM
    - CAPABILITY_NAMED_IAM
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/shantgup/enhanced-cfn-mcp-server.git
cd enhanced-cfn-mcp-server

# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=awslabs

# Run only unit tests (skip live AWS tests)
pytest -m "not live"
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
pyright
```

## 📚 Examples

See the [examples/](examples/) directory for comprehensive usage examples:

- [Basic Usage](examples/basic-usage/) - Simple resource management
- [Advanced Workflows](examples/advanced-workflows/) - Complex deployment scenarios
- [Q CLI Integration](examples/q-cli-integration/) - Amazon Q specific examples
- [Template Generation](examples/template-generation/) - Natural language to CloudFormation
- [Troubleshooting](examples/troubleshooting/) - Error resolution workflows

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/shantgup/enhanced-cfn-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shantgup/enhanced-cfn-mcp-server/discussions)
- **Documentation**: [Project Wiki](https://github.com/shantgup/enhanced-cfn-mcp-server/wiki)

## 🙏 Acknowledgments

- Built on the foundation of [AWS Labs MCP](https://github.com/awslabs/mcp)
- Powered by the [Model Context Protocol](https://modelcontextprotocol.io/)
- Enhanced for [Amazon Q Developer](https://aws.amazon.com/q/developer/)

## 🗺️ Roadmap

- [ ] **Enhanced Template Generation**: More sophisticated natural language processing
- [ ] **Multi-Account Support**: Cross-account resource management
- [ ] **Advanced Security Analysis**: Integration with AWS Security Hub
- [ ] **Cost Optimization**: Real-time cost analysis and recommendations
- [ ] **Infrastructure Visualization**: Automatic architecture diagram generation
- [ ] **Compliance Automation**: Automated compliance checking and reporting

---

**Made with ❤️ for the AWS community**
