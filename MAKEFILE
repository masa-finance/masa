.PHONY: install dev-install test lint format clean docs build release test-release setup-hooks update-deps run sync-readme

# Define repository names
PYPI_REPOSITORY = pypi
TEST_PYPI_REPOSITORY = testpypi

# Install from TestPyPI
install-testpypi:
	poetry install --source $(TEST_PYPI_REPOSITORY)

# Install from PyPI
install-pypi:
	poetry install

# Run tests
test:
	poetry run pytest tests/

# Run linter
lint:
	poetry run flake8 src/masa_ai tests

# Format code
format:
	poetry run black src/masa_ai tests

# Clean up build artifacts
clean:
	rm -rf build dist .egg *.egg-info
	find . -type d -name '__pycache__' -exec rm -rf {} +

# Generate documentation
docs:
	cd docs && make html

# Build the package
build:
	poetry build

# Synchronize README files
sync-readme:
	poetry run python sync_readme.py
	@echo "README files synchronized."

# Run the CLI tool
run:
	poetry run masa-ai-cli $(ARGS)

# Create a new test release
test-release: clean build sync-readme
	PYPI_TOKEN=$(TEST_PYPI_TOKEN) poetry run semantic-release publish --repository-url https://test.pypi.org/legacy/

# Test validation
test-validation:
	pytest tests/test_validation.py -s --disable-warnings

# Create a new full release
release: clean build sync-readme
	PYPI_TOKEN=$(PYPI_TOKEN) poetry run semantic-release publish

# Set up pre-commit hooks
setup-hooks:
	poetry run pre-commit install

# Update dependencies
update-deps:
	poetry update

# Generate changelog (if using semantic-release)
changelog:
	poetry run semantic-release changelog
