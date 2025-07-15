# Changelog

All notable changes to the Enhanced CloudFormation MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation
- Comprehensive documentation and examples

## [2.0.0] - 2024-07-15

### Added
- **Enhanced CloudFormation MCP Server** - Complete rewrite with intelligent capabilities
- **Intelligent Prompt Generation** - Expert-level prompts for AI assistants
- **Autonomous Template Fixing** - Automatic detection and fixing of CloudFormation issues
- **Multi-Stage Conversation Flow** - Guided template generation through discovery, refinement, validation, and generation phases
- **Enhanced Troubleshooting** - Comprehensive error analysis with CloudWatch and CloudTrail integration
- **Security Analysis** - Built-in security vulnerability detection and compliance checking
- **Best Practices Integration** - Automated application of AWS best practices
- **Template Analysis Engine** - Deep analysis of CloudFormation templates for optimization opportunities

#### New MCP Tools
- `generate_cloudformation_template` - Natural language to CloudFormation with intelligent conversation flow
- `troubleshoot_cloudformation_stack` - Expert troubleshooting with systematic investigation
- `fix_and_retry_cloudformation_stack` - Intelligent fix-and-retry with detailed guidance
- `autonomous_fix_and_deploy_stack` - Fully autonomous deployment with iterative fixing
- `analyze_template_structure` - Comprehensive template analysis with security and compliance checks
- `generate_template_fixes` - Generate and optionally apply template fixes
- `detect_stack_drift` - Enhanced drift detection with remediation guidance
- `cloudformation_best_practices_guide` - Expert best practices guidance
- `prevent_out_of_band_changes` - Prevent manual changes to CloudFormation-managed resources
- `detect_template_capabilities` - Analyze templates for required IAM capabilities

#### Enhanced Existing Tools
- `deploy_cloudformation_stack` - Added comprehensive parameter and tag support
- `get_stack_status` - Enhanced with operational analysis and monitoring guidance
- `delete_cloudformation_stack` - Added resource retention options
- `create_template` - Enhanced IaC Generator integration with better error handling

### Enhanced Features
- **CloudWatch Integration** - Automatic log analysis for troubleshooting
- **CloudTrail Integration** - API call investigation for root cause analysis
- **Security Compliance** - Support for HIPAA, PCI, SOX, GDPR compliance frameworks
- **Cost Optimization** - Built-in cost analysis and optimization recommendations
- **Error Recovery** - Smart error recovery with multiple fix strategies
- **Template Validation** - Enhanced validation with security and best practices checks

### Infrastructure
- **FastMCP Framework** - Built on FastMCP for robust MCP server implementation
- **Comprehensive Testing** - Unit, integration, and live testing suites
- **Code Quality** - Ruff formatting, linting, and type checking with Pyright
- **Documentation** - Comprehensive documentation with examples and tutorials
- **CI/CD Ready** - Pre-commit hooks and automated testing setup

### Developer Experience
- **Rich Examples** - Comprehensive examples for all use cases
- **Q CLI Integration** - Seamless integration with Amazon Q CLI
- **Debug Support** - Enhanced logging and debugging capabilities
- **Configuration Management** - Flexible configuration options

## [1.0.0] - 2024-06-01

### Added
- Initial release of AWS CloudFormation MCP Server
- Basic CloudFormation stack operations
- Resource management via CloudControl API
- Template generation from existing resources

#### Core MCP Tools
- `get_resource_schema_information` - Get schema information for AWS resource types
- `list_resources` - List AWS resources of a specified type
- `get_resource` - Get detailed information about a specific resource
- `create_resource` - Create new AWS resources
- `update_resource` - Update existing AWS resources using JSON Patch
- `delete_resource` - Delete AWS resources
- `get_resource_request_status` - Check status of long-running operations
- `create_template` - Generate templates from existing AWS resources
- `deploy_cloudformation_stack` - Deploy CloudFormation stacks
- `get_stack_status` - Get stack status information
- `delete_cloudformation_stack` - Delete CloudFormation stacks

### Infrastructure
- Python 3.10+ support
- Boto3 integration for AWS API access
- Basic error handling and logging
- MCP protocol implementation

---

## Version Comparison

### v2.0.0 vs v1.0.0 - Major Enhancements

| Feature | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| **Template Generation** | Basic from existing resources | Natural language with intelligent conversation |
| **Troubleshooting** | Basic error reporting | Expert analysis with CloudWatch/CloudTrail |
| **Fixing** | Manual intervention required | Autonomous fixing with iterative deployment |
| **Security** | Basic validation | Comprehensive vulnerability detection |
| **Compliance** | None | HIPAA, PCI, SOX, GDPR support |
| **Best Practices** | None | Built-in AWS best practices |
| **AI Integration** | Basic tool calls | Intelligent prompt generation |
| **Error Recovery** | Manual | Smart recovery with multiple strategies |
| **Documentation** | Basic | Comprehensive with examples |

### Breaking Changes in v2.0.0

- **Package Name**: Changed from `awslabs.cfn-mcp-server` to `enhanced-cfn-mcp-server`
- **Tool Names**: Some tools have been enhanced with additional parameters
- **Configuration**: New configuration options for enhanced features
- **Dependencies**: Updated to newer versions of core dependencies

### Migration Guide from v1.0.0

1. **Update Package Name**
   ```bash
   pip uninstall awslabs.cfn-mcp-server
   pip install enhanced-cfn-mcp-server
   ```

2. **Update Q CLI Configuration**
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

3. **Review New Features**
   - Explore new autonomous fixing capabilities
   - Try intelligent template generation
   - Use enhanced troubleshooting tools

4. **Update Scripts**
   - Tool signatures are backward compatible
   - New optional parameters available
   - Enhanced error handling

---

## Upcoming Features

### v2.1.0 (Planned)
- [ ] Multi-account support
- [ ] Enhanced security analysis with AWS Security Hub integration
- [ ] Real-time cost analysis and recommendations
- [ ] Infrastructure visualization and diagram generation
- [ ] Advanced compliance automation
- [ ] Template optimization suggestions
- [ ] Integration with AWS Well-Architected Framework

### v2.2.0 (Planned)
- [ ] Custom template libraries
- [ ] Advanced drift remediation
- [ ] Cross-region deployment support
- [ ] Enhanced monitoring and alerting
- [ ] Template versioning and rollback
- [ ] Integration with AWS Config
- [ ] Advanced IAM policy generation

### Long-term Roadmap
- [ ] Machine learning-powered optimization
- [ ] Predictive failure analysis
- [ ] Advanced cost modeling
- [ ] Integration with third-party tools
- [ ] Custom compliance frameworks
- [ ] Advanced template testing

---

## Support and Compatibility

### Supported Python Versions
- Python 3.10+
- Python 3.11 (recommended)
- Python 3.12
- Python 3.13

### Supported AWS Regions
- All AWS commercial regions
- AWS GovCloud (US) regions
- China regions (with appropriate credentials)

### Dependencies
- `boto3 >= 1.34.0`
- `botocore >= 1.34.0`
- `mcp[cli] >= 1.6.0`
- `pydantic >= 2.10.6`
- `pyyaml >= 6.0.0`
- `loguru >= 0.7.0`

---

For more information about any release, see the [GitHub Releases](https://github.com/your-username/enhanced-cfn-mcp-server/releases) page.
