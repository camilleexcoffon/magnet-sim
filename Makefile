# Makefile for magnet-sim development

.PHONY: help install install-dev test test-cov lint format type-check clean build upload docs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev,docs]"

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage report
	pytest tests/ --cov=magnet_sim --cov-report=html --cov-report=term-missing

lint:  ## Run linting
	flake8 magnet_sim/ tests/ examples/

format:  ## Format code with black
	black magnet_sim/ tests/ examples/

type-check:  ## Run type checking
	mypy magnet_sim/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

upload-test:  ## Upload to test PyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*

docs:  ## Build documentation
	@echo "Documentation files are in docs/ directory"
	@echo "For Sphinx docs, run: sphinx-build -b html docs/ docs/_build/"

example:  ## Run basic example
	cd examples && python basic_simulation.py

check:  ## Run all quality checks
	$(MAKE) format
	$(MAKE) lint  
	$(MAKE) type-check
	$(MAKE) test-cov

release:  ## Prepare release (run checks, build, upload)
	$(MAKE) check
	$(MAKE) clean
	$(MAKE) build
	@echo "Ready for release. Run 'make upload' to publish."