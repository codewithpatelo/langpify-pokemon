.PHONY: setup setup-uv install install-uv run run-prod test lint format \
        build-docker run-docker stop-docker clean help

# Load .env file
ifneq (,$(wildcard .env))
	include .env
	export $(shell sed 's/=.*//' .env)
endif

# Default environment (development)
ENVIRONMENT ?= DEVELOPMENT
PORT ?= 8080
WORKERS ?= $(shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)

# Help message
help:
	@echo "Available targets:"
	@echo "  setup         - Install all dependencies (using pip)"
	@echo "  setup-uv      - Install all dependencies (using uv)"
	@echo "  install       - Install production dependencies (pip)"
	@echo "  install-uv    - Install production dependencies (uv)"
	@echo "  run           - Run development server (Uvicorn)"
	@echo "  run-prod      - Run production server (Gunicorn)"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code with Black"
	@echo "  build-docker  - Build Docker image"
	@echo "  run-docker    - Start Docker containers"
	@echo "  stop-docker   - Stop Docker containers"
	@echo "  clean         - Clean project artifacts"


install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

install-uv:
	uv pip install --upgrade pip
	uv pip install -r requirements.txt

# Run development server
run:
	uvicorn app.main:app --reload --port $(PORT)

# Run production server
run-prod:
	gunicorn -w $(WORKERS) -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$(PORT) app.main:app

# Run tests
test:
	pytest -v --cov=app --cov-report=html

# Run linting and formatting checks
lint:
	flake8 app tests
	black --check app tests
	isort --check-only app tests

# Format code with Black
format:
	black app tests

# Build Docker image
build-docker:
	docker build -t pokemon-multi-agent .

# Run Docker containers
run-docker:
	docker compose up -d

# Stop Docker containers
stop-docker:
	docker compose down

# Clean project artifacts
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.py[cod]' -delete
	find . -type f -name '*$py.class' -delete
	find . -type f -name '.coverage' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	find . -type d -name '.hypothesis' -exec rm -rf {} +
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type d -name 'dist' -exec rm -rf {} +
	find . -type d -name 'build' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +