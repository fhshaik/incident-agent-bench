.PHONY: install lint typecheck test demo benchmark

install:
	uv sync --extra dev

lint:
	uv run ruff format --check .
	uv run ruff check .

typecheck:
	uv run mypy src

test:
	uv run pytest

demo:
	uv run incident-bench replay scenarios/impossible_travel.json --report artifacts/demo-report.html

benchmark:
	uv run incident-bench benchmark scenarios --output artifacts/benchmark.json --report artifacts/benchmark-report.html

