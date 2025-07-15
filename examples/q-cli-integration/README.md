# Amazon Q CLI Integration Examples

This directory shows how to integrate and use the Enhanced CloudFormation MCP Server with Amazon Q CLI.

## Setup and Configuration

### 1. Install the MCP Server

```bash
# Install the enhanced CFN MCP server
pip install enhanced-cfn-mcp-server

# Verify installation
enhanced-cfn-mcp-server --help
```

### 2. Configure Q CLI

Add the MCP server to your Q CLI configuration:

```bash
# Edit Q CLI configuration
q configure
```

Or manually edit `~/.config/q/config.json`:

```json
{
  "mcpServers": {
    "enhanced-cfn": {
      "command": "enhanced-cfn-mcp-server",
      "args": [],
      "env": {
        "AWS_REGION": "us-east-1",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Verify Integration

```bash
# Start Q CLI chat
q chat

# Test the integration
"List my S3 buckets using the enhanced CloudFormation MCP server"
```

## Q CLI Conversation Examples

### Infrastructure Discovery

```
You: "I need to understand my current AWS infrastructure. Can you help me get an overview?"

Q: I'll help you discover your AWS infrastructure using the enhanced CloudFormation MCP server. Let me start by listing your key resources.

[Q uses list_resources tool for various resource types]

You: "Show me details about my production S3 bucket"

Q: I'll get the detailed information about your production S3 bucket.

[Q uses get_resource tool with specific bucket name]
```

### Template Generation Workflow

```
You: "I need to create a web application with a load balancer, auto scaling group, and RDS database"

Q: I'll help you create a comprehensive CloudFormation template for your web application. Let me guide you through the requirements gathering process.

[Q uses generate_cloudformation_template tool with conversation flow]

You: "The application needs to be HIPAA compliant"

Q: I'll incorporate HIPAA compliance requirements into the template design.

[Q continues the conversation flow with compliance considerations]
```

### Troubleshooting Workflow

```
You: "My CloudFormation stack 'web-app-prod' failed to deploy. Can you help me troubleshoot?"

Q: I'll help you troubleshoot the failed deployment. Let me analyze the stack events and provide detailed guidance.

[Q uses troubleshoot_cloudformation_stack tool]

You: "Can you automatically fix the issues and redeploy?"

Q: I'll use the autonomous fixing capability to identify and resolve the issues, then redeploy the stack.

[Q uses autonomous_fix_and_deploy_stack tool]
```

### Best Practices Consultation

```
You: "I'm designing a microservices architecture on AWS. What are the best practices I should follow?"

Q: I'll provide comprehensive best practices guidance for your microservices architecture.

[Q uses cloudformation_best_practices_guide tool]

You: "How do I ensure my infrastructure is secure and compliant?"

Q: Let me analyze your requirements and provide security and compliance recommendations.

[Q provides detailed security guidance with specific recommendations]
```

## Advanced Q CLI Features

### Multi-Step Workflows

```
You: "I want to migrate my application from EC2 to containers. Walk me through the process."

Q: I'll guide you through a comprehensive migration process:

1. First, let me analyze your current EC2-based infrastructure
2. Then I'll help design the containerized architecture
3. We'll create the CloudFormation templates
4. Finally, we'll plan the migration strategy

[Q uses multiple tools in sequence to provide comprehensive guidance]
```

### Context-Aware Assistance

```
You: "I'm getting permission errors when deploying my stack"

Q: I'll help you diagnose and resolve the permission issues. Let me check your stack status and analyze the specific errors.

[Q uses get_stack_status and troubleshoot_cloudformation_stack tools]

Based on the analysis, here are the specific IAM permissions you need...
```

## Tips for Effective Q CLI Usage

### 1. Be Specific with Context

```
# Good
"Analyze my CloudFormation template in ./templates/web-app.yaml for security vulnerabilities"

# Better
"Analyze my CloudFormation template in ./templates/web-app.yaml for security vulnerabilities, focusing on HIPAA compliance requirements"
```

### 2. Use Natural Language

```
# You can ask naturally
"My stack deployment is taking forever. What's happening?"

# Q will translate this to appropriate tool calls
[Q uses get_stack_status and analyzes deployment progress]
```

### 3. Leverage Autonomous Features

```
# Instead of manual troubleshooting
"My stack failed. Can you automatically fix it and redeploy?"

# Q will use autonomous fixing capabilities
[Q uses autonomous_fix_and_deploy_stack for hands-off resolution]
```

### 4. Ask for Explanations

```
"Explain what this CloudFormation template does and suggest improvements"

[Q uses analyze_template_structure and provides comprehensive analysis]
```

## Configuration Options

### Environment Variables

```bash
# Set in your shell or Q CLI config
export AWS_REGION=us-west-2
export LOG_LEVEL=DEBUG
export ENABLE_AUTO_FIX=true
export MAX_FIX_ITERATIONS=3
```

### Advanced Configuration

Create `~/.config/enhanced-cfn-mcp/config.yaml`:

```yaml
aws:
  region: us-west-2
  profile: production
  
features:
  auto_fix: true
  security_analysis: true
  compliance_checks: ["HIPAA", "PCI", "SOX"]
  
templates:
  default_capabilities:
    - CAPABILITY_IAM
    - CAPABILITY_NAMED_IAM
  
logging:
  level: INFO
  format: structured
```

## Troubleshooting Q CLI Integration

### Common Issues

1. **MCP Server Not Found**
   ```bash
   # Verify installation
   which enhanced-cfn-mcp-server
   
   # Check Q CLI config
   q configure --list
   ```

2. **AWS Credentials Issues**
   ```bash
   # Verify AWS credentials
   aws sts get-caller-identity
   
   # Check Q CLI environment
   q chat
   "What AWS account am I using?"
   ```

3. **Permission Errors**
   ```bash
   # Check required permissions
   aws iam get-user
   aws iam list-attached-user-policies --user-name YOUR_USERNAME
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start Q CLI with verbose output
q chat --verbose
```

## Next Steps

- Explore [Template Generation](../template-generation/) examples
- Check out [Advanced Workflows](../advanced-workflows/) for complex scenarios
- See [Troubleshooting](../troubleshooting/) for debugging techniques
