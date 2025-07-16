# Contributing to Enhanced CloudFormation MCP Server

We welcome contributions to the Enhanced CloudFormation MCP Server! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- AWS CLI configured with appropriate credentials
- Git for version control
- Basic understanding of AWS CloudFormation and MCP (Model Context Protocol)

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/enhanced-cfn-mcp-server.git
   cd enhanced-cfn-mcp-server
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=awslabs

# Run only unit tests (skip live AWS tests)
pytest -m "not live"

# Run specific test file
pytest tests/test_server.py
```

### Test Categories

- **Unit Tests**: Fast tests that don't require AWS credentials
- **Integration Tests**: Tests that interact with AWS services (marked with `@pytest.mark.live`)
- **End-to-End Tests**: Full workflow tests

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names that explain what is being tested
- Mock AWS services for unit tests when possible
- Use the `@pytest.mark.live` decorator for tests that require AWS credentials

## 🎨 Code Style

We use several tools to maintain code quality:

### Formatting and Linting

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
pyright
```

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable and function names

## 📝 Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples

```bash
feat(server): add autonomous template fixing capability
fix(stack): resolve drift detection for nested stacks
docs(readme): update installation instructions
test(template): add tests for template generation
```

## 🔧 Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run tests
   pytest
   
   # Check code quality
   ruff check .
   ruff format .
   pyright
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📋 Pull Request Process

1. **Before Submitting**
   - Ensure all tests pass
   - Update documentation if needed
   - Add changelog entry for significant changes
   - Rebase your branch on the latest main branch

2. **Pull Request Description**
   - Clearly describe what your PR does
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

3. **Review Process**
   - All PRs require at least one review
   - Address reviewer feedback promptly
   - Keep PRs focused and reasonably sized

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Clear description of the issue
- Steps to reproduce the problem
- Expected vs actual behavior
- Environment details (Python version, OS, AWS region)
- Relevant error messages or logs

### Feature Requests

For feature requests, please provide:

- Clear description of the desired functionality
- Use case and motivation
- Proposed implementation approach (if any)
- Examples of how it would be used

## 🏗️ Architecture Guidelines

### Adding New Tools

When adding new MCP tools:

1. Define the tool in the appropriate module
2. Add comprehensive error handling
3. Include detailed docstrings
4. Add unit and integration tests
5. Update documentation

### Code Organization

- Keep related functionality together in modules
- Use clear separation between AWS service interactions and MCP logic
- Follow the existing patterns for error handling and logging
- Maintain backward compatibility when possible

## 📚 Documentation

### Types of Documentation

- **Code Documentation**: Docstrings and inline comments
- **User Documentation**: README, examples, and guides
- **API Documentation**: Tool descriptions and parameters
- **Architecture Documentation**: Design decisions and patterns

### Documentation Standards

- Use clear, concise language
- Include practical examples
- Keep documentation up-to-date with code changes
- Use proper markdown formatting

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional tone

### Getting Help

- Check existing issues and discussions
- Ask questions in GitHub Discussions
- Provide context when asking for help
- Be patient and respectful

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

- **New AWS Resource Types**: Adding support for additional CloudFormation resource types
- **Enhanced Error Handling**: Improving error messages and recovery mechanisms
- **Performance Optimization**: Making operations faster and more efficient
- **Documentation**: Improving examples, guides, and API documentation
- **Testing**: Adding more comprehensive test coverage
- **Security**: Enhancing security analysis and best practices

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0.

## 🙏 Recognition

Contributors will be recognized in:

- The project's README
- Release notes for significant contributions
- GitHub's contributor statistics

Thank you for contributing to the Enhanced CloudFormation MCP Server! 🚀
