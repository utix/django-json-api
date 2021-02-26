# Usage:
# make clean     # Clear virtualenv and pyc files
# make lint      # Run isort, black and flake8
# make .venv     # Create virtualenv
# make test      # Run all tests
# make test-cov  # Run all tests and print coverage in the end
# make build     # Build the package

SHELL := /bin/bash
.PHONY: clean lint test test-cov build

.venv: .venv/touchfile

.venv/touchfile: requirements.txt requirements_dev.txt
	python3 -m virtualenv .venv
	source .venv/bin/activate; \
	pip install -r requirements.txt; \
	pip install -r requirements_dev.txt; \
	touch .venv/touchfile

clean:
	rm -rf .venv
	find . -name "*.pyc" -delete

lint: .venv
	source .venv/bin/activate; \
	python -m isort django_json_api/ tests/; \
	python -m black . ; \
	flake8 ./;

test: .venv
	source .venv/bin/activate; \
	python -m pytest;

test-cov: .venv
	source .venv/bin/activate; \
	python -m pytest --cov-config=.coveragerc --cov=django_json_api/ --cov-report=term;

build: .venv
	source .venv/bin/activate; \
	pip install --upgrade build; \
	python -m build;
