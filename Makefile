.PHONY: run install test format docker-build docker-run help
PYTHON_CMD ?= uv run python


help:
	@echo "Available commands:"
	@echo "  make push         - Smart push with auto-generated commit message"
	@echo "  make app          - Start the Streamlit app in Docker"
	@echo "  make logs         - View Docker logs"
	@echo "  make stop         - Stop Docker containers"
	@echo "  make install      - Install dependencies locally (uv)"
	@echo "  make test         - Run tests locally"
	@echo "  make format       - Format code locally"
	@echo "  make docker-build - Rebuild Docker image"

push:
	@echo "✅ Board verified. Running smart push..."
	@$(PYTHON_CMD) scripts/autocommit.py

# Docker Commands
app:
	docker-compose up -d
	@echo "------------------------------------------------"
	@echo "App is running at: http://localhost:8502"
	@echo "------------------------------------------------"

reload:
	docker-compose down
	docker-compose up -d --build
	@echo "------------------------------------------------"
	@echo "App is reloading..."
	@echo "Check logs with 'make logs'"
	@echo "------------------------------------------------"

logs:
	docker-compose logs -f

stop:
	docker-compose down

# Local Commands
run:
	uv run rendercv --help

install:
	uv sync --frozen --all-extras --all-groups

test:
	uv run pytest

format:
	uv run ruff format src tests

docs:
	uv run mkdocs serve

docker-build:
	docker-compose build
