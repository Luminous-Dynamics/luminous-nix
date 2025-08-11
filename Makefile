# 🕉️ Sacred Trinity Makefile for Nix for Humanity
# Uses Poetry for all Python operations

.PHONY: help install dev test format lint type security clean build docs serve

# Default target
help: ## Show this help message
	@echo "🕉️ Nix for Humanity Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install production dependencies
	poetry install

dev: ## Install all dependencies including dev and extras
	poetry install --all-extras
	poetry run pre-commit install

# Code quality targets
format: ## Format code with Black (88 chars)
	poetry run black .

format-check: ## Check formatting without changing files
	poetry run black --check .

lint: ## Run Ruff linter
	poetry run ruff check .

lint-fix: ## Fix linting issues automatically
	poetry run ruff check --fix .

type: ## Run type checking with mypy
	poetry run mypy .

security: ## Run security checks with Bandit
	poetry run bandit -r src/ -ll

# Combined quality checks
qa: format lint type ## Run all quality checks (format, lint, type)

qa-fix: ## Fix all auto-fixable issues
	poetry run black .
	poetry run ruff check --fix .
	poetry run isort .

pre-commit: ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

# Testing targets
test: ## Run tests with pytest
	poetry run pytest

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=nix_for_humanity --cov-report=term --cov-report=html

test-verbose: ## Run tests with verbose output
	poetry run pytest -vvs

test-watch: ## Run tests in watch mode (requires pytest-watch)
	poetry run ptw

test-integration: ## Run integration tests only
	poetry run pytest tests/integration/ -v

test-unit: ## Run unit tests only
	poetry run pytest tests/unit/ -v

# Build targets
build: ## Build distribution packages
	poetry build

build-check: ## Check if package builds correctly
	poetry check
	poetry build --dry-run

# Documentation targets
docs: ## Build documentation
	poetry run mkdocs build

docs-serve: ## Serve documentation locally
	poetry run mkdocs serve

# Application targets
run: ## Run ask-nix CLI
	poetry run ask-nix

tui: ## Run TUI interface
	poetry run nix-tui

server: ## Run web server
	poetry run nix-humanity-server

# Development helpers
shell: ## Enter Poetry shell
	poetry shell

update: ## Update dependencies
	poetry update

show: ## Show installed packages
	poetry show

show-tree: ## Show dependency tree
	poetry show --tree

outdated: ## Show outdated packages
	poetry show --latest

# Cleaning targets
clean: ## Clean build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .coverage
	rm -rf coverage_html_report
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .tox

clean-all: clean ## Clean everything including virtual environment
	rm -rf .venv

# Sacred Trinity workflows
trinity-check: ## Run Sacred Trinity quality check
	@echo "🕉️ Sacred Trinity Quality Check"
	@echo "=============================="
	@poetry run black --check . && echo "✅ Formatting OK" || echo "❌ Needs formatting"
	@poetry run ruff check . && echo "✅ Linting OK" || echo "❌ Has linting issues"
	@poetry run mypy . && echo "✅ Types OK" || echo "❌ Has type issues"
	@poetry run pytest -q && echo "✅ Tests passing" || echo "❌ Test failures"

trinity-fix: ## Auto-fix all issues
	@echo "🕉️ Sacred Trinity Auto-Fix"
	@echo "========================"
	poetry run black .
	poetry run ruff check --fix .
	@echo "✅ Fixes applied!"

# Git helpers
commit-ready: pre-commit ## Check if ready to commit
	@echo "✅ Ready to commit!"

# Installation helpers
setup: ## Complete development setup
	./scripts/dev-setup.sh

# Docker targets (if needed)
docker-build: ## Build Docker image
	docker build -t nix-for-humanity .

docker-run: ## Run Docker container
	docker run -it --rm nix-for-humanity

# Release targets
version-patch: ## Bump patch version (0.0.x)
	poetry version patch

version-minor: ## Bump minor version (0.x.0)
	poetry version minor

version-major: ## Bump major version (x.0.0)
	poetry version major

release: build ## Create a release
	@echo "Ready to release version $$(poetry version -s)"
	@echo "Don't forget to:"
	@echo "  1. Commit changes"
	@echo "  2. Tag release: git tag v$$(poetry version -s)"
	@echo "  3. Push tags: git push --tags"

# Default target when just running 'make'
.DEFAULT_GOAL := help
