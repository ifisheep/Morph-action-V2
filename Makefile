.PHONY: check test lint

PYTHON ?= python3

test:
	$(PYTHON) -m pytest -m "not gpu"

lint:
	$(PYTHON) -m ruff check morphdream scripts tests

check: lint test
