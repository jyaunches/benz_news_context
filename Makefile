# Makefile for benz_news_context service using uv

.PHONY: help install dev test test-cov lint format check clean serve

help:
	@echo "Available commands:"
	@echo "  install         Install dependencies"
	@echo "  dev             Start development server with hot reload"
	@echo "  serve           Start production server"
	@echo "  test            Run all tests"
	@echo "  test-cov        Run tests with coverage report"
	@echo "  lint            Run code linting"
	@echo "  format          Format code"
	@echo "  check           Run lint + test"
	@echo "  clean           Clean up build artifacts"

install:
	uv sync --extra dev

dev:
	PYTHONPATH=src uv run python -m benz_news_context

serve:
	PYTHONPATH=src uv run uvicorn benz_news_context.app:app --host 0.0.0.0 --port 8000

test:
	uv sync --extra dev
	PYTHONPATH=src uv run pytest

test-cov:
	uv sync --extra dev
	PYTHONPATH=src uv run pytest --cov=src/benz_news_context --cov-report=html --cov-report=term

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

check: lint test

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
