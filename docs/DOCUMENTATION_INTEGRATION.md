# CloudFormation Documentation Integration

This document explains how the CloudFormation MCP Server integrates with the CloudFormation documentation to provide enhanced guidance to Q CLI.

## Overview

The CloudFormation MCP Server now includes a comprehensive knowledge base built from:
- CloudFormation API Reference documentation
- CloudFormation User Guide
- CloudFormation Knowledge Center articles

This knowledge is automatically integrated into all MCP server tools, enhancing responses with relevant documentation, best practices, and troubleshooting guidance.

## How It Works

1. **Documentation Knowledge Base**: The system loads and indexes all HTML documentation from the `mcp_docs` folder at server startup.

2. **Knowledge Integration**: All MCP tools are enhanced with relevant documentation using the `@enhance_with_knowledge` decorator.

3. **Automatic Enhancement**: Responses from MCP tools are automatically enhanced with:
   - Best practices for specific resource types
   - Troubleshooting guidance for errors
   - Documentation references for relevant topics

4. **Dedicated Documentation Tools**: New tools are available for direct access to documentation:
   - `get_cloudformation_documentation`: Search documentation for specific topics
   - `get_cloudformation_best_practices`: Get best practices for resources or templates
   - `get_cloudformation_troubleshooting`: Get troubleshooting guidance for errors

## Documentation Structure

The documentation is organized in the `mcp_docs` folder:
- `mcp_docs/api/`: CloudFormation API Reference
- `mcp_docs/user_guide/`: CloudFormation User Guide
- `mcp_docs/knowledge_center/`: CloudFormation Knowledge Center articles

## Usage Examples

### Getting Documentation

```python
response = await get_cloudformation_documentation(
    topic="S3 bucket encryption",
    doc_type="user_guide",
    max_results=3
)
```

### Getting Best Practices

```python
response = await get_cloudformation_best_practices(
    resource_type="AWS::S3::Bucket",
    topic="security"
)
```

### Getting Troubleshooting Guidance

```python
response = await get_cloudformation_troubleshooting(
    error_message="Stack creation failed: Access Denied"
)
```

## Enhanced Template Generation

When generating CloudFormation templates, the system now automatically includes:
- Best practices for each resource type in the template
- Security recommendations based on documentation
- Links to relevant documentation

## Enhanced Error Handling

When errors occur, the system now automatically provides:
- Troubleshooting steps from the documentation
- Common solutions for the specific error
- Links to relevant documentation

## Implementation Details

The implementation consists of:

1. `documentation_knowledge_base.py`: Loads and indexes documentation
2. `knowledge_integration.py`: Integrates knowledge with MCP tools
3. `initialize_knowledge.py`: Initializes the knowledge base at startup

The knowledge base is loaded in a background thread at server startup to avoid delaying the server initialization.

## Extending the Knowledge Base

To update the documentation:

1. Add new HTML files to the appropriate folder in `mcp_docs/`
2. Restart the server to reindex the documentation

The knowledge base will automatically incorporate the new documentation into all responses.