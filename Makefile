# Makefile for SweCli development
.PHONY: help install install-dev test test-cov lint format security clean build docker

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e .

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-integration:  ## Run integration tests
	pytest tests/ -v -m integration

format:  ## Format code
	black src/ tests/
	isort src/ tests/

lint:  ## Run linting
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports
	pylint src/ --disable=C0114,C0115,C0116 --max-line-length=88

security:  ## Run security checks
	bandit -r src/ -f json -o bandit-report.json
	safety check --json --output safety-report.json

check: format lint security test  ## Run all checks

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

docker:  ## Build Docker image
	docker build -t swecli:latest .

docker-run:  ## Run Docker container
	docker run --rm -it swecli:latest

release-test:  ## Upload to test PyPI
	twine upload --repository testpypi dist/*

release:  ## Upload to PyPI
	twine upload dist/*
