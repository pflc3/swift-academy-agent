# Makefile
.PHONY: reset install test lint run runmod clean

# Remove the virtual environment
reset:
	poetry env remove python3

# Remove build artifacts and caches
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache *.pyc *.pyo *.egg-info dist build

# Install dependencies from pyproject.toml
install:
	poetry install

# Check code style and auto-fix with Ruff (don't fail on warnings)
lint:
	poetry run ruff check src/ --fix || true

# Run the FastAPI server directly
run:
	poetry run uvicorn api.main:app --reload --app-dir src

# Run the API as a module (alternative style)
runmod:
	poetry run python -m api.main

# Run all tests using pytest
test:
	poetry run pytest
