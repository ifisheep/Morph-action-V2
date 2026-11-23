.PHONY: check test lint import-lint

PYTHON ?= python3

test:
	$(PYTHON) -m pytest -m "not gpu"

lint:
	$(PYTHON) -m ruff check morphdream scripts tests

import-lint:
	lint-imports

check: lint import-lint test
