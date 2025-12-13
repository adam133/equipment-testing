# Copilot Instructions for Equipment Testing

## Project Overview

Equipment Testing is a Python application for equipment testing, built with modern Python development practices. The project uses:

- **Python 3.12+** as the minimum version
- **uv** - A fast Python package installer and resolver (10-100x faster than pip)
- **pytest** for testing with coverage reporting
- **Ruff** for linting and code formatting
- **mypy** for static type checking
- **pre-commit** hooks for automated code quality checks

## Development Setup

### Installing Dependencies

This project uses `uv` for dependency management. To set up the development environment:

```bash
# Install dependencies (creates .venv automatically)
uv sync --all-extras --dev

# Or sync only development dependencies
uv sync --dev
```

### Running the Application

```bash
# Using uv run (recommended - no activation needed)
uv run python -m equipment_testing
uv run equipment-testing

# Or activate virtual environment first
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows
python -m equipment_testing
```

## Code Style and Quality

### Formatting with Ruff

- **Line length**: 88 characters (Black-compatible)
- **Quote style**: Double quotes
- **Target Python version**: 3.12

```bash
# Format code
uv run ruff format src/ tests/

# Check formatting without changes
uv run ruff format --check src/ tests/
```

### Linting with Ruff

The project uses these Ruff rule sets:
- `E` - pycodestyle errors
- `W` - pycodestyle warnings
- `F` - pyflakes
- `I` - isort (import sorting)
- `C` - flake8-comprehensions
- `B` - flake8-bugbear
- `UP` - pyupgrade

```bash
# Lint code
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/
```

### Type Checking with mypy

- All code in `src/` must have type hints
- Function signatures require type annotations
- Tests (`tests/`) are exempt from `disallow_untyped_defs`

```bash
# Type check source code
uv run mypy src/
```

### Pre-commit Hooks

```bash
# Install hooks (one-time setup)
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=equipment_testing --cov-report=term

# Run with coverage and XML report (for CI)
uv run pytest --cov=equipment_testing --cov-report=xml --cov-report=term
```

### Test Configuration

- Test files: `test_*.py` in the `tests/` directory
- Test classes: `Test*`
- Test functions: `test_*`
- Coverage target: Source code in `src/equipment_testing/`

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names that explain what is being tested
- Follow existing test patterns in `test_basic.py`
- Type hints are optional in test files

## Adding Dependencies

```bash
# Add production dependency
uv add <package-name>

# Add development dependency
uv add --dev <package-name>

# Example: Add a new testing tool
uv add --dev pytest-mock
```

Dependencies are automatically added to `pyproject.toml`.

## Building and Distribution

```bash
# Build wheel and source distributions
uv build

# Output: dist/ directory with .whl and .tar.gz files
```

## CI/CD Pipeline

The project uses GitHub Actions with three jobs:

1. **Test**: Runs pytest with coverage on Python 3.12
2. **Lint**: Checks formatting (ruff format), linting (ruff check), and types (mypy)
3. **Build**: Builds distribution packages

All jobs use `uv` for fast dependency installation.

### CI Requirements

Before pushing changes, ensure:
- [ ] Tests pass: `uv run pytest`
- [ ] Formatting is correct: `uv run ruff format --check src/ tests/`
- [ ] No linting errors: `uv run ruff check src/ tests/`
- [ ] Type checking passes: `uv run mypy src/`

## Project Structure

```
equipment-testing/
├── .github/
│   ├── workflows/
│   │   └── ci.yml           # CI/CD pipeline
│   └── copilot-instructions.md
├── src/
│   └── equipment_testing/   # Main package
│       ├── __init__.py
│       ├── __main__.py      # Entry point
│       └── py.typed         # PEP 561 marker for type hints
├── tests/
│   ├── __init__.py
│   └── test_basic.py        # Test files
├── pyproject.toml           # Project configuration and dependencies
├── .pre-commit-config.yaml  # Pre-commit hooks
├── .gitignore
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

## Common Tasks

### Creating a New Module

1. Create a new Python file in `src/equipment_testing/`
2. Add type hints to all functions
3. Create corresponding test file in `tests/test_<module>.py`
4. Run tests and type checking to verify

### Fixing Import Order

Ruff automatically sorts imports using isort rules:

```bash
uv run ruff check --fix src/ tests/
```

### Updating Dependencies

```bash
# Sync to latest compatible versions
uv sync --upgrade

# Update specific package
uv add <package-name>@latest
```

## Best Practices

1. **Always use type hints** in source code (`src/`)
2. **Run pre-commit hooks** before committing
3. **Write tests** for new functionality
4. **Use `uv run`** instead of activating the virtual environment
5. **Follow PEP 8** conventions (enforced by Ruff)
6. **Keep imports organized** (automated by Ruff's isort integration)
7. **Document public APIs** with docstrings
8. **Update CHANGELOG.md** for notable changes

## Key Files

- **pyproject.toml**: All project configuration (dependencies, tools, metadata)
- **.pre-commit-config.yaml**: Pre-commit hook configuration
- **src/equipment_testing/__main__.py**: CLI entry point
- **tests/test_basic.py**: Example test file
- **.github/workflows/ci.yml**: CI/CD pipeline

## Troubleshooting

### Virtual Environment Issues

```bash
# Remove and recreate virtual environment
rm -rf .venv
uv sync --all-extras --dev
```

### Dependency Conflicts

```bash
# Show dependency tree
uv tree

# Force reinstall
uv sync --reinstall
```

### Pre-commit Hook Failures

```bash
# Run hooks individually for debugging
uv run pre-commit run ruff --all-files
uv run pre-commit run mypy --all-files
```

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Project Repository](https://github.com/adam133/equipment-testing)
