# Contributing to Text-to-SQL System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/your-username/text-to-sql-system.git
cd text-to-sql-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. **Setup pre-commit hooks**
```bash
pre-commit install
```

5. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. **Run tests**
```bash
pytest
```

## 📋 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow coding standards (see below)
- Add tests for new functionality
- Update documentation if needed

### 3. Run Quality Checks
```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy text_to_sql/

# Run tests
pytest --cov=text_to_sql
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add new SQL generator for complex queries"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

## 📝 Coding Standards

### Code Style
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Maximum line length: **88 characters**

### Type Hints
```python
from typing import Dict, List, Optional, Any

def process_data(
    data: List[Dict[str, Any]], 
    config: Optional[Dict[str, str]] = None
) -> List[str]:
    """Process data with optional configuration."""
    pass
```

### Docstrings
Use Google-style docstrings:
```python
def generate_sql(self, question: str, context: Optional[Dict] = None) -> str:
    """Generate SQL query from natural language question.
    
    Args:
        question: Natural language question
        context: Optional context information
        
    Returns:
        Generated SQL query string
        
    Raises:
        ValueError: If question is empty or invalid
        DatabaseError: If schema information is unavailable
    """
    pass
```

### Error Handling
```python
import logging

logger = logging.getLogger(__name__)

def risky_operation():
    try:
        # Risky code here
        result = perform_operation()
        return result
    except SpecificException as e:
        logger.error(f"Operation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Operation failed: {e}") from e
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data
└── conftest.py     # Pytest configuration
```

### Writing Tests
```python
import pytest
from unittest.mock import Mock, patch

class TestSQLGenerator:
    """Test SQL generator functionality."""
    
    def setup_method(self):
        """Setup before each test."""
        self.generator = SQLGenerator(mock_schema)
    
    def test_basic_query_generation(self):
        """Test basic query generation."""
        question = "Which sector has lowest exposure?"
        sql = self.generator.generate_sql(question)
        
        assert "SELECT" in sql
        assert "counterparty_sector" in sql
        assert "ORDER BY" in sql
    
    @patch('text_to_sql.core.llm_client.OpenAI')
    def test_llm_integration(self, mock_openai):
        """Test LLM integration with mocking."""
        mock_openai.return_value.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="SELECT * FROM table;"))]
        )
        
        result = self.generator.generate_with_llm("test question")
        assert result == "SELECT * FROM table;"
```

### Test Coverage
- Aim for **>90% test coverage**
- Test both success and failure cases
- Include edge cases and error conditions

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Include type hints for all parameters and return values
- Document complex algorithms and business logic

### README Updates
- Update README.md for new features
- Add examples for new functionality
- Update installation instructions if needed

### API Documentation
- Document new API endpoints
- Include request/response examples
- Update OpenAPI schema if applicable

## 🔍 Code Review Process

### Before Submitting PR
- [ ] All tests pass
- [ ] Code coverage maintained
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] No merge conflicts

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

## 🐛 Bug Reports

### Bug Report Template
```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.9.0]
- Package version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of desired solution

**Describe alternatives you've considered**
Alternative solutions considered

**Additional context**
Any other context or screenshots
```

## 🏷️ Commit Message Guidelines

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes
- **refactor**: Code refactoring
- **test**: Adding tests
- **chore**: Maintenance tasks

### Examples
```bash
feat(generators): add support for custom fine-tuned models

- Add CustomOpenAIGenerator class
- Integrate with generator factory
- Add frontend dropdown option
- Include monitoring scripts

Closes #123
```

## 🚀 Release Process

### Version Numbering
Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release in git

## 📞 Getting Help

- **Issues**: Create GitHub issue
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check `/docs` folder
- **Examples**: See `/examples` folder

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing! 🎉