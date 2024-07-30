# Define the virtual environment activation command
POETRY_RUN = poetry run

# Define the source directories for formatting
SRC_DIRS = src tests

.PHONY: install format test run

# 1. Activate virtual environment and install required packages
install:
	poetry install

# 2. Format code using black and sort imports using isort
format:
	$(POETRY_RUN) black $(SRC_DIRS)
	$(POETRY_RUN) isort $(SRC_DIRS)
	$(POETRY_RUN) flake8

# 3. Run project tests using pytest
test:
	$(POETRY_RUN) pytest

# 4. Run the project
run:
	$(POETRY_RUN) python src/app.py
