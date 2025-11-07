# Contributing to ResearchPulse

Thank you for your interest in contributing to ResearchPulse! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of research paper aggregation and LLMs

### Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ResearchPulse.git
cd ResearchPulse
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up pre-commit hooks (optional but recommended):
```bash
pip install pre-commit
pre-commit install
```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

2. Make your changes following the code style guidelines below

3. Write or update tests for your changes

4. Run tests locally:
```bash
pytest tests/
```

5. Run linters and formatters:
```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type checking (optional)
mypy src/
```

### Code Style

- **Python**: Follow PEP 8 guidelines
- **Line length**: 100 characters (configured in pyproject.toml)
- **Formatting**: Use `black` for automatic formatting
- **Imports**: Sort with `ruff` (isort rules)
- **Type hints**: Encouraged but not required

### Testing Guidelines

#### Writing Tests

- All new features must include unit tests
- Aim for >80% code coverage
- Use pytest fixtures from `tests/conftest.py`
- Mock external API calls using `pytest-mock` or `responses`
- Use `freezegun` for time-based tests

#### Test Structure

```python
# tests/unit/test_your_module.py

import pytest
from your_module import YourClass


class TestYourClass:
    """Test cases for YourClass."""

    @pytest.fixture
    def instance(self):
        """Create a YourClass instance for testing."""
        return YourClass(config={})

    def test_method_with_valid_input(self, instance):
        """Test method behavior with valid input."""
        result = instance.method("valid input")
        assert result == expected_value

    def test_method_with_invalid_input(self, instance):
        """Test method handles invalid input gracefully."""
        with pytest.raises(ValueError):
            instance.method("invalid")
```

#### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_processor.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run only fast tests (mark with @pytest.mark.unit)
pytest -m unit
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `style`: Code style changes (formatting, etc.)

**Examples:**
```
feat(fetcher): add PubMed paper source integration

Implements PubMed API integration with keyword and author search.
Includes unit tests and documentation.

Closes #42

---

fix(processor): correct deduplication logic for papers without DOI

Papers without DOI were incorrectly considered duplicates.
Now checks DOI only when present.

Fixes #56
```

## Pull Request Process

### Before Submitting

1. Ensure all tests pass locally
2. Update documentation if needed
3. Add or update tests for your changes
4. Run code formatters and linters
5. Rebase your branch on the latest main

### Submitting

1. Push your branch to your fork:
```bash
git push origin feature/your-feature-name
```

2. Open a Pull Request on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Link to related issues (if any)
   - Screenshots (if applicable)

3. Wait for CI checks to pass:
   - Tests run on Python 3.9, 3.10, 3.11, 3.12
   - Linting and formatting checks
   - Coverage report

### Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Once approved, maintainers will merge your PR

## Areas for Contribution

### High Priority

- [ ] Additional paper sources (PubMed, bioRxiv, SSRN)
- [ ] Improved error handling and logging
- [ ] Performance optimizations
- [ ] Additional unit test coverage

### Medium Priority

- [ ] Email/Slack notifications
- [ ] Paper recommendation engine
- [ ] Mobile-responsive UI improvements
- [ ] Multi-language support

### Low Priority

- [ ] GraphQL API
- [ ] Paper similarity clustering
- [ ] Automated paper reading
- [ ] Browser extension

See [Claude.md](../Claude.md) for the full list of future enhancements.

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discrimination of any kind
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

## Questions?

- Check the [documentation](../Claude.md)
- Search [existing issues](https://github.com/dengzeyu/ResearchPulse/issues)
- Open a new issue for bugs or feature requests
- Join discussions in pull requests

## License

By contributing to ResearchPulse, you agree that your contributions will be licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

## Thank You!

Your contributions make ResearchPulse better for everyone. Thank you for taking the time to contribute! 🎉
