.PHONY: help setup install-hooks sync test lint format type-check clean dev

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

setup: ## Install dependencies and pre-commit hooks
	@echo "Installing dependencies..."
	uv sync --all-extras --dev
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install
	@echo "✓ Setup complete! Pre-commit hooks are installed."

install-hooks: ## Install pre-commit hooks only
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install
	@echo "✓ Pre-commit hooks installed."

sync: ## Sync dependencies only
	uv sync --all-extras --dev

test: ## Run tests with coverage
	uv run pytest --cov=equipment_testing --cov-report=term --cov-report=xml

lint: ## Run linter
	uv run ruff check src/ tests/

format: ## Format code with ruff
	uv run ruff format src/ tests/

format-check: ## Check code formatting without changes
	uv run ruff format --check src/ tests/

type-check: ## Run type checker
	uv run mypy src/

pre-commit: ## Run pre-commit on all files
	uv run pre-commit run --all-files

clean: ## Clean build artifacts and cache
	rm -rf .venv
	rm -rf dist
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -f coverage.xml
	rm -f .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

dev: setup ## Alias for setup - install everything needed for development
	@echo "✓ Development environment ready!"
