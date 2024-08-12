# Install project dependencies
install:
	poetry install

# Update project dependencies
update:
	poetry update

# Run project tests
test:
	poetry run pytest

# Lint code using flake8
lint:
	black .
	flake8

# Clean up generated files
clean:
	poetry run rm -rf dist build

# Build project distribution
build:
	poetry build

# Publish project to PyPI
publish:
	poetry publish