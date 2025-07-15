# Contributing to Enhanced CloudFormation MCP Server

We welcome contributions to the Enhanced CloudFormation MCP Server! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- AWS CLI configured with appropriate credentials
- Git
- Basic understanding of CloudFormation and AWS services

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/enhanced-cfn-mcp-server.git
   cd enhanced-cfn-mcp-server
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Setup Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Verify Setup**
   ```bash
   pytest
   ruff check .
   pyright
   ```

## 🛠️ Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=awslabs

# Run only unit tests (skip live AWS tests)
pytest -m "not live"

# Run specific test file
pytest tests/test_your_feature.py
```

### 4. Code Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
pyright

# Run pre-commit hooks
pre-commit run --all-files
```

### 5. Commit Your Changes

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
git add .
git commit -m "feat: add new template generation feature"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference any related issues
- Include screenshots/examples if applicable

## 📝 Code Style Guidelines

### Python Code Style

We use Ruff for code formatting and linting. The configuration is in `pyproject.toml`.

**Key Guidelines:**
- Line length: 99 characters
- Use single quotes for strings
- Follow PEP 8 naming conventions
- Add type hints for all functions
- Use docstrings for all public functions and classes

**Example:**
```python
async def create_resource(
    resource_type: str,
    properties: Dict[str, Any],
    region: Optional[str] = None
) -> Dict[str, Any]:
    """Create an AWS resource using CloudControl API.
    
    Args:
        resource_type: The AWS resource type (e.g., 'AWS::S3::Bucket')
        properties: Resource properties dictionary
        region: AWS region (optional)
        
    Returns:
        Dictionary containing resource creation status and details
        
    Raises:
        ClientError: If resource creation fails
    """
    # Implementation here
    pass
```

### Documentation Style

- Use Google-style docstrings
- Include type hints in function signatures
- Provide examples in docstrings for complex functions
- Keep README and documentation up to date

### Testing Guidelines

- Write tests for all new functionality
- Use descriptive test names
- Include both positive and negative test cases
- Mock AWS API calls in unit tests
- Use the `live` marker for tests that require AWS credentials

**Example:**
```python
import pytest
from unittest.mock import Mock, patch

class TestResourceManager:
    def test_create_s3_bucket_success(self):
        """Test successful S3 bucket creation."""
        # Test implementation
        pass
    
    def test_create_s3_bucket_invalid_name(self):
        """Test S3 bucket creation with invalid name."""
        # Test implementation
        pass
    
    @pytest.mark.live
    def test_create_s3_bucket_live(self):
        """Test S3 bucket creation with live AWS API."""
        # Live test implementation
        pass
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests (no AWS API calls)
├── integration/          # Integration tests (mock AWS APIs)
├── live/                # Live tests (require AWS credentials)
├── fixtures/            # Test data and fixtures
└── conftest.py          # Pytest configuration
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Live tests (requires AWS credentials)
pytest tests/live/ -m live

# Specific test
pytest tests/unit/test_resource_manager.py::TestResourceManager::test_create_s3_bucket

# With coverage
pytest --cov=awslabs --cov-report=html
```

### Test Markers

- `@pytest.mark.live`: Tests that make real AWS API calls
- `@pytest.mark.asyncio`: Async tests
- `@pytest.mark.slow`: Tests that take a long time to run

## 📚 Documentation

### Code Documentation

- All public functions and classes must have docstrings
- Use Google-style docstrings
- Include examples for complex functionality
- Document all parameters and return values

### README Updates

When adding new features:
- Update the feature list in README.md
- Add usage examples
- Update the tools table if adding new MCP tools

### Examples

Add examples to the `examples/` directory:
- Create a new subdirectory for your feature
- Include a README.md with usage instructions
- Provide working code samples

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Package version
   - Operating system
   - AWS region

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Minimal code example
   - Expected vs actual behavior

3. **Error Messages**
   - Full error traceback
   - Relevant log messages
   - AWS error codes if applicable

4. **Additional Context**
   - Screenshots if applicable
   - Related issues or PRs
   - Workarounds you've tried

## 💡 Feature Requests

When requesting features:

1. **Use Case Description**
   - What problem does this solve?
   - Who would benefit from this feature?
   - How would you use this feature?

2. **Proposed Solution**
   - High-level approach
   - API design (if applicable)
   - Examples of usage

3. **Alternatives Considered**
   - Other approaches you've considered
   - Why this approach is preferred

## 🔒 Security

### Reporting Security Issues

Please do not report security vulnerabilities through public GitHub issues. Instead:

1. Email security concerns to [security@yourproject.com]
2. Include detailed information about the vulnerability
3. Allow time for the issue to be addressed before public disclosure

### Security Guidelines

- Never commit AWS credentials or secrets
- Use IAM roles with least privilege principle
- Validate all user inputs
- Use secure defaults in templates
- Follow AWS security best practices

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages follow conventional commits
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Reviewers may test changes locally
4. **Documentation**: Ensure documentation is complete and accurate

## 🏷️ Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Create release notes
- [ ] Tag release in Git
- [ ] Publish to PyPI
- [ ] Update documentation

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Pull Requests**: Code contributions and reviews

## 📞 Getting Help

If you need help:

1. Check existing documentation and examples
2. Search GitHub issues for similar problems
3. Create a new issue with detailed information
4. Join community discussions

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to the Enhanced CloudFormation MCP Server! 🎉
