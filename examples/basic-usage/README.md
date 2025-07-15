# Basic Usage Examples

This directory contains simple examples to get you started with the Enhanced CloudFormation MCP Server.

## Resource Management

### List Resources

```bash
# In Q CLI chat
q chat

# List all S3 buckets
"List all my S3 buckets"

# List EC2 instances
"Show me all my EC2 instances"

# List RDS databases
"What RDS databases do I have?"
```

### Get Resource Details

```bash
# Get details of a specific S3 bucket
"Show me details of my bucket named 'my-app-bucket'"

# Get EC2 instance information
"Tell me about EC2 instance i-1234567890abcdef0"

# Get RDS database details
"Show me details of my RDS database 'prod-db'"
```

### Create Resources

```bash
# Create a simple S3 bucket
"Create an S3 bucket named 'my-new-bucket'"

# Create S3 bucket with versioning
"Create an S3 bucket named 'versioned-bucket' with versioning enabled"

# Create an EC2 security group
"Create a security group named 'web-sg' that allows HTTP and HTTPS traffic"
```

### Update Resources

```bash
# Enable versioning on an existing bucket
"Enable versioning on my S3 bucket 'existing-bucket'"

# Update security group rules
"Add SSH access to security group 'web-sg' from my IP"
```

### Delete Resources

```bash
# Delete an S3 bucket
"Delete my S3 bucket 'old-bucket'"

# Delete a security group
"Delete security group 'unused-sg'"
```

## Simple CloudFormation Operations

### Deploy a Stack

```bash
# Deploy from a local template
"Deploy a CloudFormation stack named 'my-web-app' using the template in ./template.yaml"

# Deploy with parameters
"Deploy stack 'my-app' with parameter Environment=prod and InstanceType=t3.medium"
```

### Check Stack Status

```bash
# Get stack status
"What's the status of my CloudFormation stack 'my-web-app'?"

# Get detailed stack information
"Show me detailed information about stack 'production-stack'"
```

### Delete a Stack

```bash
# Delete a stack
"Delete my CloudFormation stack 'old-stack'"

# Delete with resource retention
"Delete stack 'app-stack' but retain the RDS database"
```

## Next Steps

- Check out [Advanced Workflows](../advanced-workflows/) for complex scenarios
- See [Template Generation](../template-generation/) for creating templates from natural language
- Explore [Troubleshooting](../troubleshooting/) for debugging failed deployments
