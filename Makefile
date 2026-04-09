.PHONY: test lint build

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest -q

lint:
	uv run ruff check src tests

build:
	uv run python -m build
