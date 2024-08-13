.PHONY : help install update test lint clean build publish all

all: test

# Install project dependencies
install:
	poetry install

# Update project dependencies
update:
	poetry update

# Run project tests
test:
	poetry run pytest --cov-report xml --cov=athena_federation

# Lint code using flake8
lint:
	black .
	flake8

# Clean up generated files
clean:
	poetry run rm -rf dist build

# Build project distribution
build: lint
	poetry build

# Publish project to PyPI
publish: build
	poetry publish