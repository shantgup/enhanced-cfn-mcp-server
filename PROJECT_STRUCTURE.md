# Enhanced CloudFormation MCP Server - Project Structure

This document provides an overview of the project structure and organization.

## 📁 Root Directory Structure

```
enhanced-cfn-mcp-server/
├── README.md                          # Main project documentation
├── CHANGELOG.md                       # Version history and changes
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                           # Apache 2.0 license
├── NOTICE                           # Copyright notice
├── pyproject.toml                   # Python package configuration
├── .gitignore                       # Git ignore rules
├── PROJECT_STRUCTURE.md             # This file
├── awslabs/                         # Main source code
├── tests/                           # Test suite
├── examples/                        # Usage examples and tutorials
├── docs/                           # Additional documentation
├── scripts/                        # Utility scripts
└── tools/                          # Development and diagnostic tools
```

## 🐍 Source Code (`awslabs/`)

### Core MCP Server
```
awslabs/cfn_mcp_server/
├── __init__.py                      # Package initialization
├── server.py                        # Main MCP server implementation
├── config.py                        # Configuration management
├── context.py                       # Request context handling
└── errors.py                        # Error handling and exceptions
```

### AWS Integration
```
awslabs/cfn_mcp_server/
├── aws_client.py                    # AWS service clients
├── cloud_control_utils.py           # CloudControl API utilities
├── stack_manager.py                 # CloudFormation stack operations
├── schema_manager.py                # Resource schema management
└── resource_mapping.py              # AWS resource type mappings
```

### Template Management
```
awslabs/cfn_mcp_server/
├── template_generator_clean.py      # Template generation engine
├── template_analyzer_clean.py       # Template analysis and validation
├── template_fixer.py                # Automatic template fixing
├── template_validator.py            # Template validation
├── template_capabilities.py         # IAM capability detection
├── intelligent_template_generator.py # AI-powered template generation
└── architecture_templates.py        # Pre-built architecture patterns
```

### Enhanced Features
```
awslabs/cfn_mcp_server/
├── enhanced_troubleshooter.py       # Advanced troubleshooting
├── enhanced_error_handling.py       # Enhanced error analysis
├── autonomous_deployer.py           # Autonomous deployment engine
├── troubleshooter.py                # Core troubleshooting logic
├── troubleshooting_enhancer_clean.py # Troubleshooting enhancements
└── stack_operations_enhancer_clean.py # Stack operation enhancements
```

### Knowledge and Documentation
```
awslabs/cfn_mcp_server/
├── documentation_knowledge_base.py  # Built-in knowledge base
├── knowledge_integration.py         # Knowledge system integration
├── initialize_knowledge.py          # Knowledge base initialization
└── prompt_validator.py              # Prompt validation and enhancement
```

### Utilities
```
awslabs/cfn_mcp_server/
├── cloudformation_yaml.py           # YAML processing utilities
├── yaml_utils.py                    # YAML manipulation helpers
├── iac_generator.py                 # Infrastructure as Code generation
├── resource_generator.py            # Resource generation utilities
├── error_messages.py                # Error message templates
└── clean_prompt_server.py           # Clean prompt generation
```

## 🧪 Tests (`tests/`)

### Test Organization
```
tests/
├── __init__.py                      # Test package initialization
├── test_server.py                   # Main server tests
├── test_aws_client.py               # AWS client tests
├── test_stack_manager.py            # Stack management tests
├── test_template_generation.py      # Template generation tests
├── test_template_generator.py       # Template generator tests
├── test_schema_manager.py           # Schema management tests
├── test_cloud_control_utils.py      # CloudControl utility tests
├── test_cloudformation_yaml.py      # YAML processing tests
├── test_template_capabilities.py    # Template capability tests
├── test_iac_generator.py            # IaC generator tests
├── test_documentation_knowledge.py  # Knowledge base tests
├── test_config.py                   # Configuration tests
├── test_errors.py                   # Error handling tests
├── test_init.py                     # Initialization tests
└── test_main.py                     # Main entry point tests
```

### Test Categories
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Live Tests**: Test with real AWS APIs (marked with `@pytest.mark.live`)

## 📚 Examples (`examples/`)

### Example Categories
```
examples/
├── README.md                        # Examples overview and guide
├── basic-usage/                     # Simple usage examples
│   └── README.md                    # Basic usage guide
├── q-cli-integration/               # Amazon Q CLI integration
│   └── README.md                    # Q CLI setup and usage
├── template-generation/             # Template generation examples
│   ├── README.md                    # Template generation guide
│   └── samples/                     # Sample CloudFormation templates
│       ├── simple-s3-template.yaml
│       ├── cross-account-s3-template.yaml
│       ├── cross-account-s3-template-fixed.yaml
│       └── minimal-s3-demo.yaml
├── advanced-workflows/              # Complex deployment scenarios
└── troubleshooting/                 # Troubleshooting examples
```

### Example Features
- **Progressive Complexity**: From basic to advanced
- **Real-World Scenarios**: Practical use cases
- **Step-by-Step Guides**: Detailed instructions
- **Working Code**: Tested and verified examples

## 📖 Documentation (`docs/`)

### Documentation Structure
```
docs/
├── CHANGELOG.md                     # Version history (duplicate)
├── CONTRIBUTING.md                  # Contribution guide (duplicate)
├── cross-account-s3-deployment-guide.md # Specific deployment guide
├── DOCUMENTATION_INTEGRATION.md     # Documentation integration guide
├── INDEX.md                         # Documentation index
└── archive/                         # Archived documentation
    ├── BRAZIL_SETUP_GUIDE.md
    ├── CLOUDFORMATION_FIRST_PRINCIPLES.md
    ├── COMPLETE_SYSTEM_DOCUMENTATION.md
    ├── ENHANCED_COMPARISON_ANALYSIS.md
    ├── ENHANCED_DEPLOYMENT_CAPABILITIES.md
    ├── ENHANCED_TROUBLESHOOTING_SUMMARY.md
    ├── ENHANCEMENT_SUMMARY.md
    ├── FINAL_SOLUTION_CONFIRMED.md
    ├── INTELLIGENT_TEMPLATE_GENERATOR_SUMMARY.md
    ├── PROJECT_STRUCTURE.md
    └── [other archived docs]
```

## 🛠️ Scripts (`scripts/`)

### Utility Scripts
```
scripts/
├── enhanced_prompt_flow.py          # Enhanced prompt flow utilities
└── intelligent_question_generator.py # Question generation utilities
```

### Script Purposes
- **Development Utilities**: Helper scripts for development
- **Prompt Engineering**: Tools for prompt generation and validation
- **Testing Utilities**: Scripts for testing and validation

## 🔧 Tools (`tools/`)

### Development Tools
```
tools/
├── diagnostics/                     # Diagnostic utilities
│   ├── diagnose_python.py          # Python environment diagnostics
│   ├── test_import.py               # Import testing
│   └── test_python.py               # Python functionality testing
└── validate_dynamic_config.py      # Configuration validation
```

### Tool Categories
- **Diagnostics**: Environment and setup diagnostics
- **Validation**: Configuration and setup validation
- **Development**: Development workflow utilities

## 📦 Package Configuration

### Python Package (`pyproject.toml`)
```toml
[project]
name = "enhanced-cfn-mcp-server"
version = "2.0.0"
description = "Enhanced AWS CloudFormation MCP server with intelligent capabilities"

[project.scripts]
"enhanced-cfn-mcp-server" = "awslabs.cfn_mcp_server.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Key Features
- **Modern Python Packaging**: Uses `pyproject.toml` standard
- **Entry Points**: Command-line script registration
- **Development Dependencies**: Comprehensive dev tooling
- **Code Quality**: Ruff, Pyright, and pre-commit integration

## 🚀 Key Components Overview

### 1. MCP Server Core
- **FastMCP Framework**: Modern MCP server implementation
- **Tool Registration**: 20+ MCP tools for CloudFormation operations
- **Error Handling**: Comprehensive error handling and recovery
- **Configuration**: Flexible configuration management

### 2. AWS Integration
- **Multi-Service Support**: CloudFormation, CloudControl, CloudWatch, CloudTrail
- **Credential Management**: Multiple authentication methods
- **Region Support**: All AWS regions supported
- **Error Recovery**: Smart retry and recovery mechanisms

### 3. Enhanced Features
- **Intelligent Prompting**: AI-guided prompt generation
- **Autonomous Fixing**: Automatic issue detection and resolution
- **Template Analysis**: Deep template analysis and optimization
- **Best Practices**: Built-in AWS best practices integration

### 4. Developer Experience
- **Comprehensive Testing**: Unit, integration, and live tests
- **Rich Documentation**: Examples, guides, and API documentation
- **Code Quality**: Automated formatting, linting, and type checking
- **Easy Installation**: Simple pip installation and setup

## 🔄 Development Workflow

### 1. Setup
```bash
git clone https://github.com/your-username/enhanced-cfn-mcp-server.git
cd enhanced-cfn-mcp-server
pip install -e ".[dev]"
pre-commit install
```

### 2. Development
```bash
# Make changes
# Run tests
pytest
# Check code quality
ruff check .
pyright
# Commit changes
git commit -m "feat: add new feature"
```

### 3. Testing
```bash
# Unit tests
pytest tests/unit/
# Integration tests
pytest tests/integration/
# Live tests (requires AWS credentials)
pytest tests/live/ -m live
```

## 📊 Project Statistics

### Code Organization
- **Total Python Files**: 35+ source files
- **Test Coverage**: Comprehensive test suite
- **Documentation**: 25+ documentation files
- **Examples**: 15+ working examples

### Feature Completeness
- **MCP Tools**: 20+ tools implemented
- **AWS Services**: 10+ AWS services integrated
- **Template Types**: Support for all CloudFormation resource types
- **Use Cases**: 50+ documented use cases

## 🎯 Next Steps

### For Users
1. Start with [Basic Usage](examples/basic-usage/)
2. Try [Q CLI Integration](examples/q-cli-integration/)
3. Explore [Template Generation](examples/template-generation/)
4. Master [Advanced Workflows](examples/advanced-workflows/)

### For Contributors
1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Set up development environment
3. Run tests and ensure they pass
4. Pick an issue or feature to work on

### For Maintainers
1. Review and merge pull requests
2. Update documentation as needed
3. Release new versions following semantic versioning
4. Maintain compatibility with AWS services

---

This project structure is designed for:
- **Scalability**: Easy to add new features and tools
- **Maintainability**: Clear separation of concerns
- **Usability**: Comprehensive examples and documentation
- **Quality**: Robust testing and code quality standards

For more information, see the main [README.md](README.md) or explore the [examples](examples/) directory.
