# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-06-16

### Added
- **Enhanced CloudFormation Capabilities**: Major expansion of CloudFormation functionality
- **Template Generation**: Generate CloudFormation templates from natural language descriptions
  - Intelligent resource identification from natural language
  - Support for both YAML and JSON output formats
  - Interactive clarification and meaningful options
  - Best practices integration and security recommendations
- **Stack Deployment**: Comprehensive CloudFormation stack deployment
  - Support for stack parameters, tags, and IAM capabilities
  - Handle both new deployments and stack updates
  - Real-time deployment monitoring and status tracking
- **Troubleshooting**: Advanced CloudFormation troubleshooting capabilities
  - Stack event analysis and error pattern recognition
  - CloudWatch logs integration for Lambda and custom resources
  - Resource status checking and dependency analysis
  - Actionable recommendations based on identified issues
- **Auto-Fix & Retry**: Intelligent automatic fixing and retry mechanism
  - Built-in knowledge base of common CloudFormation issues
  - Automatic issue detection and fix application
  - Template backup and restore functionality
  - Progressive retry with improvements
- **Stack Management**: Complete stack lifecycle management
  - Comprehensive stack status monitoring
  - Safe stack deletion with resource retention options
  - Stack event tracking and failure analysis

### Enhanced
- **Natural Language Interface**: Improved natural language processing for infrastructure requirements
- **Error Handling**: Enhanced error handling and user feedback
- **Documentation**: Comprehensive documentation with examples and best practices

### Dependencies
- Added `pyyaml>=6.0.0` for YAML template support

### Testing
- Added comprehensive test coverage for all new features
- Test suites for TemplateGenerator, StackManager, and CloudFormationTroubleshooter
- Example usage scripts demonstrating new capabilities

## [1.0.0] - 2025-05-26

### Removed

- **BREAKING CHANGE:** Server Sent Events (SSE) support has been removed in accordance with the Model Context Protocol specification's [backwards compatibility guidelines](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#backwards-compatibility)
- This change prepares for future support of [Streamable HTTP](https://modelcontextprotocol.io/specification/draft/basic/transports#streamable-http) transport

## Unreleased

### Added

- Support for CloudFormation Template generation via IaC Generator APIs

## [0.0.1] 2025-05-14

### Added

- Initial release of CloudFormation MCP Server
- Support for resource CRUDL via CloudControl APIs
