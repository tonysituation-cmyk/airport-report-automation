PYTHON ?= python

.PHONY: install install-dev sample-data run test lint typecheck check clean

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev]

sample-data:
	$(PYTHON) sample_data/generate_sample_data.py

run:
	PYTHONPATH=src $(PYTHON) -m report_automation

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src

check: lint typecheck test

clean:
	rm -rf build dist *.egg-info reports logs .pytest_cache .mypy_cache
