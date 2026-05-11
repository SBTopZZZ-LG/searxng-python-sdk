.PHONY: setup test test-unit test-integration example lint format

.venv/.done: pyproject.toml
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	touch .venv/.done

setup: .venv/.done

test:
	.venv/bin/pytest

test-unit:
	.venv/bin/pytest tests/searxng_search/

test-integration:
	.venv/bin/pytest tests/integration/

example:
	.venv/bin/python example/main.py

lint:
	.venv/bin/ruff check .

format:
	.venv/bin/ruff format .
