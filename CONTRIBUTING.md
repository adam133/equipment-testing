# Contributing to Equipment Testing

Thank you for your interest in contributing to Equipment Testing! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- uv package installer

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/adam133/equipment-testing.git
   cd equipment-testing
   ```

2. Install dependencies:
   ```bash
   uv sync --dev
   ```

3. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines

3. Run tests:
   ```bash
   uv run pytest
   ```

4. Run linters and formatters:
   ```bash
   # Format code
   uv run ruff format src/ tests/
   
   # Lint code
   uv run ruff check src/ tests/
   
   # Type check
   uv run mypy src/
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Maximum line length: 88 characters (Ruff default)
- Write docstrings for public functions and classes

### Testing

- Write tests for new features
- Maintain or improve code coverage
- Tests should be in the `tests/` directory
- Use descriptive test names

### Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in the present tense (e.g., "Add", "Fix", "Update")
- Keep the first line under 72 characters
- Add detailed description if needed

Example:
```
Add user authentication feature

- Implement login/logout functionality
- Add password hashing
- Create user session management
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md with your changes
3. Ensure all tests pass and code quality checks succeed
4. Submit a pull request with a clear title and description
5. Wait for review and address any feedback

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

## Reporting Bugs

When reporting bugs, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Python version and OS
- Any relevant logs or error messages

## Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- A clear and descriptive title
- Detailed description of the proposed feature
- Explanation of why this enhancement would be useful
- Possible implementation approach (optional)

## Questions?

Feel free to open an issue with the question label if you have any questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
