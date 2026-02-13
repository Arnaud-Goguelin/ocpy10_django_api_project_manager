
# Cross-platform shell configuration
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# SoftDesk API - Project automation with Just
# Run 'just --list' to see all available commands

# Default recipe to display help
default:
    @just --list

# === Docker Commands ===

# Build and start the application with Docker Compose
docker-up:
    docker compose -f docker/compose.yml up --build

# Stop the Docker containers
docker-down:
    docker compose -f docker/compose.yml down

# Stop and remove containers, volumes, and images
docker-clean:
    docker compose -f docker/compose.yml down -v --rmi all

# Build Docker image from Dockerfile
docker-build:
    docker build -f docker/Dockerfile -t softdesk-api .

# Run Docker container (without compose)
docker-run:
    docker run -p 8000:8000 softdesk-api

# === Local Development Commands ===

# Install project dependencies with uv
install:
    uv sync

# Apply database migrations
migrate:
    python manage.py migrate

# Create database migrations
makemigrations:
    python manage.py makemigrations

# Collect static files
collectstatic:
    python manage.py collectstatic --noinput

# Run the development server
run:
    python manage.py runserver

# Run the development server with local settings
run-local:
    python manage.py runserver --settings=config.settings.local

# Setup the project for local development (install + migrate + collectstatic)
setup: install migrate collectstatic
    @echo "✅ Local development setup complete!"
    @echo "Run 'just run-local' to start the development server"

# === Test Commands ===

# Run all tests
test:
    pytest

# Run tests with coverage report
test-coverage:
    coverage run -m pytest
    coverage report

# Run tests in verbose mode
test-verbose:
    pytest -v

# Run specific test file
test-file FILE:
    pytest {{ FILE }}

# Run tests matching a pattern
test-pattern PATTERN:
    pytest -k {{ PATTERN }}

# Run tests with markers (e.g., just test-marker django_db)
test-marker MARKER:
    pytest -m {{ MARKER }}

# === Combined Commands ===

# Full setup with Docker
docker-setup: docker-clean docker-up

# Quick start for local development
quick-start: setup run-local

# === Database Commands ===

# Reset the database (delete and recreate)
reset-db:
    rm -f db.sqlite3
    python manage.py migrate
    @echo "✅ Database reset complete!"

# Create a Django superuser
createsuperuser:
    python manage.py createsuperuser

# Open Django shell
shell:
    python manage.py shell

# Open IPython shell (if installed)
shell-plus:
    python manage.py shell

# === Code Quality Commands ===

# Lint code with Ruff (check only)
lint:
    ruff check .

# Lint code with Ruff and fix issues
lint-ruff:
    ruff check --fix .

# Format code with Ruff
format:
    ruff format .

# Check formatting with Ruff (without modifying files)
format-check:
    ruff format --check .

# Run all quality checks (lint + format check)
qa: lint format-check
    @echo "✅ All quality checks passed!"

# Fix all code quality issues (format + lint with fixes)
fix: format lint-ruff
    @echo "✅ Code formatted and linted!"

# === Utility Commands ===

# Check for Django issues
check:
    python manage.py check

# Show Django migrations status
showmigrations:
    python manage.py showmigrations

# Open Swagger/OpenAPI documentation (requires local server running)
docs:
    @echo "📚 Opening API documentation..."
    @echo "Make sure the server is running with 'just run-local'"
    @echo "Documentation available at: http://127.0.0.1:8000/api/docs/swagger/"

# Clean Python cache files
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name ".ruff_cache" -exec rm -rf {} +
    find . -type d -name "htmlcov" -exec rm -rf {} +
    find . -type f -name ".coverage" -delete
    @echo "✅ Cleaned Python cache files!"

# Full clean (cache + database)
clean-all: clean reset-db
    @echo "✅ Full cleanup complete!"
