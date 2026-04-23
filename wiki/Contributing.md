# 🤝 Contributing to Duck Framework

Thank you for your interest in contributing to Duck! We welcome contributions from everyone.

---

## 🌟 Ways to Contribute

You don't need to be a coding expert to contribute! Here are many ways to help:

### 💻 Code Contributions
- Fix bugs
- Add new features
- Improve performance
- Write tests
- Refactor code

### 📝 Documentation
- Fix typos
- Improve clarity
- Add examples
- Translate docs
- Write tutorials

### 🐛 Bug Reports
- Report issues
- Provide reproduction steps
- Test bug fixes
- Verify issues

### 💡 Feature Requests
- Suggest improvements
- Discuss new ideas
- Provide use cases
- Design APIs

### 🎨 Design
- Improve UI/UX
- Create icons
- Design components
- Enhance accessibility

### 🌍 Community
- Answer questions
- Help other users
- Share your projects
- Write blog posts

---

## 🚀 Getting Started

### 1. Fork the Repository

Visit [github.com/duckframework/duck](https://github.com/duckframework/duck) and click "Fork" in the top right.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/duck.git
cd duck
```

### 3. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 4. Create a Branch

```bash
# Create a branch for your changes
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

---

## 💻 Development Workflow

### 1. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Keep changes focused and minimal

### 2. Write Tests

```python
# tests/test_feature.py
import unittest
from duck import YourFeature

class TestYourFeature(unittest.TestCase):
    def test_basic_functionality(self):
        feature = YourFeature()
        result = feature.do_something()
        self.assertEqual(result, expected_value)
```

### 3. Run Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_feature.py

# Run with coverage
python -m pytest --cov=duck
```

### 4. Check Code Style

```bash
# Format code
black duck/

# Check linting
flake8 duck/

# Check imports
isort duck/

# Type checking
mypy duck/
```

### 5. Update Documentation

If your changes affect user-facing features:
- Update relevant documentation files
- Add docstrings to new functions/classes
- Update the README if needed
- Add examples

---

## 📋 Coding Standards

### Python Style

We follow PEP 8 with some modifications:

```python
# Good: Clear, descriptive names
def calculate_user_score(user_id, metrics):
    """Calculate the score for a given user.
    
    Args:
        user_id: The unique identifier for the user
        metrics: Dictionary of metric values
        
    Returns:
        float: The calculated score
    """
    # Implementation
    pass

# Bad: Unclear names
def calc(u, m):
    pass
```

### Code Organization

```python
# Imports
import os
import sys
from typing import Optional, Dict

# Third-party imports
import requests
from django.http import HttpResponse

# Local imports
from duck.http import Request
from duck.shortcuts import render

# Constants
DEFAULT_TIMEOUT = 30

# Classes
class MyClass:
    pass

# Functions
def my_function():
    pass
```

### Documentation

Use Google-style docstrings:

```python
def process_data(data: dict, options: Optional[dict] = None) -> dict:
    """Process the input data according to specified options.
    
    This function takes raw data and transforms it based on the
    provided options. If no options are provided, default settings
    are used.
    
    Args:
        data: The input data to process as a dictionary
        options: Optional processing parameters. Defaults to None.
        
    Returns:
        A dictionary containing the processed results with keys:
        - 'success': Boolean indicating if processing succeeded
        - 'result': The processed data
        - 'errors': List of any errors encountered
        
    Raises:
        ValueError: If data is empty or invalid
        TypeError: If data is not a dictionary
        
    Example:
        >>> data = {'name': 'Duck', 'version': '1.0'}
        >>> result = process_data(data)
        >>> print(result['success'])
        True
    """
    # Implementation
    pass
```

---

## 🧪 Testing Guidelines

### Test Structure

```python
import unittest
from duck.feature import Feature

class TestFeature(unittest.TestCase):
    """Tests for the Feature class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.feature = Feature()
    
    def tearDown(self):
        """Clean up after tests."""
        self.feature.cleanup()
    
    def test_basic_operation(self):
        """Test basic feature operation."""
        result = self.feature.operate()
        self.assertTrue(result)
    
    def test_edge_case(self):
        """Test edge case handling."""
        result = self.feature.operate(edge_case=True)
        self.assertIsNotNone(result)
```

### What to Test

- ✅ Normal operation
- ✅ Edge cases
- ✅ Error handling
- ✅ Boundary conditions
- ✅ Integration with other components

### Test Coverage

Aim for high test coverage:
- New features: 100% coverage
- Bug fixes: Test that verifies the fix
- Existing code: Improve coverage when modifying

---

## 📝 Commit Messages

Write clear, descriptive commit messages:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Good commit messages
git commit -m "feat(components): add virtual DOM diffing algorithm"
git commit -m "fix(ssl): correct certificate renewal timing"
git commit -m "docs(wiki): improve getting started guide"

# Bad commit messages
git commit -m "updated stuff"
git commit -m "fix"
git commit -m "changes"
```

### Detailed Example

```
feat(websocket): add per-message compression support

Implement RFC 7692 permessage-deflate extension for WebSocket
connections. This reduces bandwidth usage for text messages.

- Add compression negotiation during handshake
- Implement compression/decompression for messages
- Add configuration options for compression level
- Include tests for compressed message handling

Closes #123
```

---

## 🔄 Pull Request Process

### 1. Push Your Changes

```bash
git push origin feature/your-feature-name
```

### 2. Create Pull Request

- Go to your fork on GitHub
- Click "New Pull Request"
- Select your branch
- Fill in the PR template

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages are clear
```

### 3. Code Review

- Respond to feedback promptly
- Make requested changes
- Push updates to the same branch
- Be open to suggestions

### 4. Merge

Once approved:
- PR will be merged by maintainers
- Your contribution will be in the next release
- You'll be added to contributors list

---

## 🐛 Reporting Bugs

### Before Reporting

1. Search existing issues
2. Update to latest version
3. Verify it's reproducible

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what went wrong

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Actual behavior**
What actually happened

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Duck version: [e.g., 1.0.0]

**Additional context**
- Error messages
- Stack traces
- Screenshots
```

---

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Problem**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
What other approaches did you consider?

**Use Case**
How would you use this feature?

**Additional Context**
- Examples from other frameworks
- Mockups or diagrams
- Code snippets
```

---

## 📚 Documentation Guidelines

### Writing Style

- Use clear, simple language
- Write in present tense
- Use active voice
- Include examples
- Keep it concise

### Documentation Structure

```markdown
# Feature Name

Brief one-sentence description.

## Overview
Detailed explanation of what it does

## Usage
How to use it with examples

## Parameters
Description of all parameters

## Examples
Multiple usage examples

## Notes
Important information and gotchas

## See Also
Related documentation
```

---

## 🌍 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Focus on what's best for the community
- Show empathy

### Communication

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - Questions, ideas, general discussion
- **Pull Requests** - Code contributions
- **Email** - Private matters, security issues

---

## 🎁 Recognition

### Contributors

All contributors are recognized in:
- [AUTHORS.md](../AUTHORS.md)
- Release notes
- Project README
- GitHub contributors page

### Significant Contributions

Significant contributions may result in:
- Maintainer status
- Repository access
- Decision-making input

---

## 📖 Resources

- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Coding Practices](../CODING-PRACTICES.md)
- [Security Policy](../SECURITY.md)
- [Development Documentation](https://docs.duckframework.xyz/dev/)

---

## 🆘 Getting Help

Stuck? Need help?

- 💬 Ask in [GitHub Discussions](https://github.com/duckframework/duck/discussions)
- 📖 Read the [Documentation](https://docs.duckframework.xyz)
- 📧 Email maintainers (for private matters)

---

## 🙏 Thank You!

Every contribution, no matter how small, makes Duck better. We appreciate your time and effort!

**Happy coding! 🦆**
