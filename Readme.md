# Equipment Testing

A Python application for equipment testing, built with [uv](https://github.com/astral-sh/uv) - a fast Python package installer and resolver.

## About

This application provides tools and utilities for testing equipment. Built using modern Python development practices with `uv` for fast and reliable dependency management.

## Prerequisites

- Python 3.8 or higher
- uv (Python package installer)

## Installation

### Install uv

If you don't have `uv` installed, you can install it using one of the following methods:

**On macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Via pip:**
```bash
pip install uv
```

### Install Project Dependencies

Once you have `uv` installed, you can install the project dependencies:

```bash
# Sync dependencies from pyproject.toml
uv sync
```

## Usage

### Running the Application

```bash
# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Run the main application
python -m equipment_testing
```

### Using uv run (Alternative)

You can also use `uv run` to run commands without manually activating the virtual environment:

```bash
uv run python -m equipment_testing
```

## Development

### Project Structure

```
equipment-testing/
├── src/
│   └── equipment_testing/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
├── .gitignore
└── README.md
```

### Adding Dependencies

To add new dependencies to the project:

```bash
# Add a production dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>
```

### Running Tests

```bash
# Run tests with pytest
uv run pytest

# Run tests with coverage
uv run pytest --cov=equipment_testing
```

### Code Quality

```bash
# Format code with black
uv run black src/ tests/

# Lint code with ruff
uv run ruff check src/ tests/

# Type checking with mypy
uv run mypy src/
```

### Creating a New Virtual Environment

If you need to recreate the virtual environment:

```bash
# Remove existing environment
rm -rf .venv

# Create new environment and sync dependencies
uv sync
```

## Building and Distribution

### Building the Package

```bash
# Build distribution packages
uv build
```

This will create wheel and source distributions in the `dist/` directory.

### Installing the Package Locally

```bash
# Install in development mode
uv pip install -e .
```

## Why uv?

- **Fast**: 10-100x faster than pip
- **Reliable**: Deterministic dependency resolution
- **Compatible**: Drop-in replacement for pip and pip-tools
- **Modern**: Built with Rust for performance
- **All-in-one**: Package management, virtual environments, and more

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Project Repository](https://github.com/adam133/equipment-testing)
