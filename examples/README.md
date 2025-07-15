# Enhanced CloudFormation MCP Server Examples

This directory contains comprehensive examples demonstrating the capabilities of the Enhanced CloudFormation MCP Server.

## 📁 Directory Structure

### [Basic Usage](basic-usage/)
Simple examples to get you started with resource management and basic CloudFormation operations.

**What you'll learn:**
- List and manage AWS resources
- Create, update, and delete resources
- Basic CloudFormation stack operations
- Simple troubleshooting

**Best for:** Beginners, quick reference

### [Q CLI Integration](q-cli-integration/)
Comprehensive guide for integrating with Amazon Q CLI and using natural language interactions.

**What you'll learn:**
- Q CLI setup and configuration
- Natural language conversations
- Context-aware assistance
- Advanced Q CLI features

**Best for:** Amazon Q users, conversational AI workflows

### [Template Generation](template-generation/)
Advanced template generation from natural language descriptions with intelligent conversation flows.

**What you'll learn:**
- Multi-stage conversation flows
- Natural language to CloudFormation
- Architecture pattern recognition
- Compliance and security integration

**Best for:** Infrastructure architects, complex deployments

### [Advanced Workflows](advanced-workflows/)
Complex deployment scenarios, multi-stack architectures, and enterprise patterns.

**What you'll learn:**
- Multi-stack deployments
- Cross-account architectures
- Enterprise patterns
- Advanced automation

**Best for:** Enterprise users, complex architectures

### [Troubleshooting](troubleshooting/)
Comprehensive troubleshooting techniques, error analysis, and autonomous fixing capabilities.

**What you'll learn:**
- Error analysis techniques
- Autonomous fixing workflows
- CloudWatch and CloudTrail integration
- Recovery strategies

**Best for:** DevOps engineers, production support

## 🚀 Quick Start

### 1. Choose Your Path

**New to CloudFormation?** → Start with [Basic Usage](basic-usage/)

**Using Amazon Q CLI?** → Go to [Q CLI Integration](q-cli-integration/)

**Need complex infrastructure?** → Check [Template Generation](template-generation/)

**Troubleshooting issues?** → See [Troubleshooting](troubleshooting/)

### 2. Prerequisites

Before running examples, ensure you have:

```bash
# Install the enhanced CFN MCP server
pip install enhanced-cfn-mcp-server

# Configure AWS credentials
aws configure

# Verify Q CLI integration (if using Q CLI)
q chat
"List my S3 buckets"
```

### 3. Example Categories

| Category | Complexity | Time to Complete | Prerequisites |
|----------|------------|------------------|---------------|
| Basic Usage | Beginner | 15-30 minutes | AWS credentials |
| Q CLI Integration | Intermediate | 30-60 minutes | Q CLI installed |
| Template Generation | Intermediate | 45-90 minutes | CloudFormation knowledge |
| Advanced Workflows | Advanced | 1-3 hours | Enterprise AWS experience |
| Troubleshooting | Advanced | 30-120 minutes | Debugging experience |

## 🎯 Learning Paths

### Path 1: CloudFormation Beginner
1. [Basic Usage - Resource Management](basic-usage/#resource-management)
2. [Basic Usage - Simple CloudFormation](basic-usage/#simple-cloudformation-operations)
3. [Template Generation - Simple Web App](template-generation/#simple-web-application)
4. [Troubleshooting - Basic Debugging](troubleshooting/#basic-debugging)

### Path 2: Amazon Q User
1. [Q CLI Integration - Setup](q-cli-integration/#setup-and-configuration)
2. [Q CLI Integration - Conversations](q-cli-integration/#q-cli-conversation-examples)
3. [Template Generation - Natural Language](template-generation/#natural-language-to-cloudformation)
4. [Advanced Workflows - Q CLI Automation](advanced-workflows/#q-cli-automation)

### Path 3: Enterprise Architect
1. [Template Generation - Microservices](template-generation/#microservices-architecture)
2. [Advanced Workflows - Multi-Account](advanced-workflows/#multi-account-deployments)
3. [Advanced Workflows - Compliance](advanced-workflows/#compliance-frameworks)
4. [Troubleshooting - Production Support](troubleshooting/#production-support)

### Path 4: DevOps Engineer
1. [Basic Usage - All Operations](basic-usage/)
2. [Troubleshooting - All Techniques](troubleshooting/)
3. [Advanced Workflows - CI/CD Integration](advanced-workflows/#cicd-integration)
4. [Advanced Workflows - Monitoring](advanced-workflows/#monitoring-and-alerting)

## 🛠️ Common Use Cases

### Infrastructure as Code
- **Template Generation**: Create templates from natural language
- **Template Analysis**: Analyze existing templates for improvements
- **Best Practices**: Apply AWS best practices automatically

### Troubleshooting and Support
- **Error Analysis**: Deep dive into CloudFormation failures
- **Autonomous Fixing**: Automatically fix and redeploy stacks
- **Root Cause Analysis**: Investigate issues with CloudWatch/CloudTrail

### Compliance and Security
- **Security Analysis**: Detect vulnerabilities in templates
- **Compliance Checking**: Ensure HIPAA, PCI, SOX compliance
- **Best Practices**: Apply security best practices

### Operational Excellence
- **Drift Detection**: Identify configuration drift
- **Cost Optimization**: Optimize infrastructure costs
- **Monitoring**: Set up comprehensive monitoring

## 📋 Example Templates

### Sample CloudFormation Templates

The [template-generation/samples/](template-generation/samples/) directory contains:

- **Simple S3 Template**: Basic S3 bucket with versioning
- **Cross-Account S3 Template**: S3 bucket with cross-account access
- **Web Application Template**: Three-tier web application
- **Microservices Template**: Container-based microservices
- **Data Pipeline Template**: Serverless data processing pipeline

### Usage Patterns

Each example includes:
- **README.md**: Detailed explanation and usage instructions
- **Template Files**: CloudFormation templates (YAML/JSON)
- **Parameter Files**: Example parameter configurations
- **Scripts**: Automation scripts and helpers
- **Documentation**: Architecture diagrams and explanations

## 🔧 Testing Examples

### Unit Testing
```bash
# Test individual components
pytest examples/tests/unit/

# Test specific example
pytest examples/tests/unit/test_basic_usage.py
```

### Integration Testing
```bash
# Test with mock AWS APIs
pytest examples/tests/integration/

# Test Q CLI integration
pytest examples/tests/integration/test_q_cli.py
```

### Live Testing
```bash
# Test with real AWS resources (requires credentials)
pytest examples/tests/live/ -m live

# Test specific workflow
pytest examples/tests/live/test_template_generation.py -m live
```

## 🆘 Getting Help

### Common Issues

1. **AWS Credentials Not Configured**
   ```bash
   aws configure
   # or
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   ```

2. **Q CLI Integration Issues**
   ```bash
   q configure
   # Check MCP server configuration
   ```

3. **Permission Errors**
   ```bash
   # Verify IAM permissions
   aws iam get-user
   aws sts get-caller-identity
   ```

### Support Channels

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions and share experiences
- **Documentation**: Check the main README and docs
- **Examples**: Look for similar use cases in other examples

## 🤝 Contributing Examples

We welcome contributions of new examples! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Example Contribution Checklist

- [ ] Clear README with usage instructions
- [ ] Working code with proper error handling
- [ ] Test cases for the example
- [ ] Documentation with architecture diagrams
- [ ] Integration with existing example structure

### Suggested Example Topics

- **Industry-Specific Templates**: Healthcare, finance, retail
- **Advanced Patterns**: Event-driven architectures, serverless
- **Integration Examples**: Third-party tools, hybrid cloud
- **Compliance Examples**: Industry-specific compliance
- **Cost Optimization**: Advanced cost optimization techniques

---

**Happy Learning!** 🎉

Start with the examples that match your experience level and use case. Each example builds on previous concepts, so feel free to progress through them in order or jump to specific topics that interest you.
