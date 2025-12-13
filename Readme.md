# Equipment Testing

A Python project for equipment testing, managed with [uv](https://github.com/astral-sh/uv).

## About

This project provides tools and utilities for testing equipment.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer and resolver

## Installation

### Install uv

First, install `uv` if you haven't already:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Using pip
pip install uv
```

### Clone the Repository

```bash
git clone https://github.com/adam133/equipment-testing.git
cd equipment-testing
```

### Install Dependencies

```bash
# Create a virtual environment and install dependencies
uv sync
```

## Usage

### Running the Project

```bash
# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows

# Run your scripts
python your_script.py
```

### Using uv run

You can also run scripts directly without activating the virtual environment:

```bash
uv run python your_script.py
```

## Development

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Removing Dependencies

```bash
uv remove package-name
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update a specific package
uv add package-name --upgrade
```

## Project Structure

```
equipment-testing/
├── Readme.md           # This file
├── pyproject.toml      # Project configuration and dependencies
├── uv.lock            # Lock file for reproducible installs
└── src/               # Source code directory
```

## Testing

```bash
# Run tests (when test framework is set up)
uv run pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Python Documentation](https://docs.python.org/)
