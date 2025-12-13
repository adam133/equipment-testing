# OpenAg-DB: Open Agricultural Equipment Database

[![CI](https://github.com/adam133/equipment-testing/workflows/CI/badge.svg)](https://github.com/adam133/equipment-testing/actions)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A public, community-driven agricultural equipment database using a Python-centric stack and Lakehouse architecture. OpenAg-DB provides comprehensive specifications for tractors, combines, implements, and other agricultural equipment.

## 🚀 Live Demo

**Frontend**: [https://adam133.github.io/equipment-testing/](https://adam133.github.io/equipment-testing/)

The frontend is currently deployed with mock data for demonstration purposes. It showcases the search, filtering, and browsing capabilities with sample tractors, combines, and implements.

## 🌾 About

OpenAg-DB is designed to be the go-to resource for agricultural equipment specifications, built on modern data infrastructure:

- **Data Model**: Pydantic models with polymorphic support for different equipment types
- **Storage**: Apache Iceberg v2 tables on AWS S3 for versioned, queryable data
- **API**: FastAPI backend with DuckDB for fast serverless analytics
- **Scrapers**: Polite, scheduled Scrapy spiders for data collection
- **Frontend**: React + Vite + Shadcn UI for searchable interface
- **Community**: Open-source contribution model via GitHub

## 🏗️ Architecture

```
OpenAg-DB/
├── src/
│   ├── api/           # FastAPI backend (AWS Lambda compatible)
│   ├── scrapers/      # Scrapy spiders for data collection
│   ├── core/          # Pydantic models & Iceberg utilities
│   └── frontend/      # React/Vite static site
├── .github/workflows/ # CI/CD and scheduled scrapers
└── tests/            # Pytest test suite
```

### Data Flow

1. **Collection**: Scrapy spiders collect equipment data from manufacturer websites
2. **Validation**: All data validated against Pydantic models
3. **Storage**: Data written to Iceberg tables in S3
4. **Query**: FastAPI + DuckDB serve data to frontend
5. **Contribution**: Users suggest corrections via GitHub Issues

## 📊 Equipment Types

OpenAg-DB supports multiple equipment categories with specialized models:

### Tractors
- Horsepower (PTO/Engine)
- Transmission Type
- Hydraulic Flow & Pressure
- Three-Point Hitch Specifications

### Combines
- Grain Tank Capacity
- Separator Type (Conventional/Rotary/Hybrid)
- Unloading Rate
- Engine Specifications

### Implements
- Working Width
- Weight
- Required HP Range
- Row Configuration (for planters/cultivators)

## Quick Start

### Backend (Python)

```bash
# Clone and install
git clone https://github.com/adam133/equipment-testing.git
cd equipment-testing
uv sync

# Run examples
uv run python examples.py

# Start the API server
uv run openagdb-api
# Visit http://localhost:8000/docs for interactive API documentation

# Run tests
uv run pytest
```

### Frontend (React)

```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Visit http://localhost:5173

# Build for production
npm run build
```

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Node.js 18+ (for frontend development)
- AWS credentials (for S3 Tables access in production) - See [AWS_CONFIGURATION.md](AWS_CONFIGURATION.md)

## Installation

### Install uv

If you don't have `uv` installed:

**On macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Project Dependencies

```bash
# Clone the repository
git clone https://github.com/adam133/equipment-testing.git
cd equipment-testing

# Sync Python dependencies
uv sync

# For development with all optional dependencies
uv sync --all-extras
```

## Usage

### Running the API Server

```bash
# Start the FastAPI development server
uv run openagdb-api

# The API will be available at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
```

### Using the Equipment Models

```python
from core.models import Tractor, EquipmentCategory, TransmissionType

# Create a tractor instance
tractor = Tractor(
    make="John Deere",
    model="5075E",
    series="5E Series",
    year_start=2014,
    pto_hp=65,
    engine_hp=75,
    transmission_type=TransmissionType.POWERSHIFT,
)

# Validate and export
print(tractor.model_dump())
```

### Running Scrapers

```bash
# Run a specific spider
uv run scrapy crawl tractordata

# List all available spiders
uv run scrapy list
```

## Development

### Project Structure

```
equipment-testing/
├── .github/workflows/
│   ├── ci.yml           # Testing, linting, building
│   └── scraper.yml      # Scheduled data collection
├── src/
│   ├── api/             # FastAPI REST API
│   │   └── main.py      # API endpoints
│   ├── core/            # Core data models
│   │   ├── models.py    # Pydantic equipment models
│   │   └── iceberg_utils.py  # Iceberg table utilities
│   ├── scrapers/        # Scrapy data collection
│   │   ├── spiders/     # Spider implementations
│   │   ├── pipelines.py # Data processing pipelines
│   │   └── settings.py  # Scrapy configuration
│   ├── frontend/        # React frontend (future)
│   └── equipment_testing/  # Legacy CLI
├── tests/               # Pytest test suite
│   ├── test_models.py   # Model tests
│   └── test_api.py      # API tests
├── pyproject.toml       # Project metadata & dependencies
└── README.md
```

### Adding Dependencies

To add new dependencies to the project:

```bash
# Add a production dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Add to specific optional group
uv add --optional iceberg <package-name>
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=core --cov=api --cov-report=term

# Run specific test file
uv run pytest tests/test_models.py

# Run specific test
uv run pytest tests/test_models.py::test_tractor_creation
```

### Code Quality

#### Pre-commit Hooks

Set up pre-commit hooks to automatically check code quality:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

#### Manual Code Quality Checks

```bash
# Format code with ruff
uv run ruff format src/ tests/

# Check formatting without making changes
uv run ruff format --check src/ tests/

# Lint code with ruff
uv run ruff check src/ tests/

# Fix linting issues automatically
uv run ruff check --fix src/ tests/

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

## API Documentation

Once the API server is running, interactive documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List all equipment
curl http://localhost:8000/equipment?limit=10

# Filter tractors by manufacturer
curl http://localhost:8000/equipment/tractors?make=John%20Deere

# Submit a contribution
curl -X POST http://localhost:8000/contributions \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "engine_hp",
    "proposed_value": "105",
    "notes": "Updated from manufacturer specs"
  }'
```

## Data Model

OpenAg-DB uses Pydantic models for data validation and serialization:

- **CommonEquipment**: Base model with fields shared across all equipment
- **Tractor**: Extends CommonEquipment with tractor-specific fields
- **Combine**: Extends CommonEquipment with combine-specific fields  
- **Implement**: Extends CommonEquipment with implement-specific fields

All models support:
- Automatic validation
- Type safety
- JSON serialization
- Time-travel queries (via Iceberg snapshots)

## Contributing

We welcome contributions! Here's how you can help:

1. **Submit Equipment Data**: Use the web interface to suggest corrections
2. **Improve Scrapers**: Add new spiders for additional data sources
3. **Enhance Models**: Propose new equipment types or fields
4. **Fix Bugs**: Report and fix issues on GitHub

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Roadmap

### Phase 1: Core Setup ✅
- [x] Initialize project structure
- [x] Define Pydantic models
- [x] Create FastAPI application
- [x] Set up Scrapy framework

### Phase 2: Data Collection
- [ ] Implement manufacturer-specific spiders
- [ ] Add Iceberg table integration
- [x] Configure AWS S3 Tables (see [AWS_CONFIGURATION.md](AWS_CONFIGURATION.md))
- [ ] Set up automated scraping workflow

### Phase 3: API & Query Layer
- [ ] Integrate DuckDB for Iceberg queries
- [ ] Add authentication/rate limiting
- [ ] Implement contribution workflow
- [ ] Deploy to AWS Lambda

### Phase 4: Frontend
- [x] Build React search interface
- [x] Add filtering and sorting
- [x] Deploy to GitHub Pages
- [ ] Implement contribution form
- [ ] Connect to real API backend

### Phase 5: Community Features
- [ ] Automated contribution review
- [ ] Data quality metrics
- [ ] Community guidelines
- [ ] Public API keys

## Technology Stack

- **Language**: Python 3.12+
- **Package Manager**: uv
- **Data Models**: Pydantic
- **API Framework**: FastAPI
- **Scraping**: Scrapy
- **Storage**: Apache Iceberg on AWS S3 Tables
- **Query Engine**: DuckDB
- **Frontend**: React + Vite + Shadcn UI
- **CI/CD**: GitHub Actions
- **Hosting**: AWS Lambda (API) + GitHub Pages (Frontend)

## Why uv?

- **Fast**: 10-100x faster than pip
- **Reliable**: Deterministic dependency resolution
- **Compatible**: Drop-in replacement for pip and pip-tools
- **Modern**: Built with Rust for performance
- **All-in-one**: Package management, virtual environments, and more

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [AWS Quick Start Guide](AWS_QUICKSTART.md) - Fast setup for AWS infrastructure
- [AWS Configuration Guide](AWS_CONFIGURATION.md) - Comprehensive AWS setup and security best practices
- [Terraform Examples](terraform/README.md) - Infrastructure-as-code templates
- [uv Documentation](https://docs.astral.sh/uv/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Project Repository](https://github.com/adam133/equipment-testing)
