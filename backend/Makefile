# ============================================
# HECTIC SWARM - Backend Makefile
# ============================================

.PHONY: help install test lint format clean run dev db-migrate orchestrate

help:  ## Show this help message
	@echo "🔥 HECTIC SWARM Backend Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

install-dev:  ## Install dev dependencies (pre-commit, etc.)
	@echo "📦 Installing dev dependencies..."
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install
	@echo "✅ Dev environment ready"

test:  ## Run pytest tests
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=agents --cov=utils --cov-report=term-missing

test-fast:  ## Run tests without coverage
	@echo "🧪 Running fast tests..."
	pytest tests/ -v -x

test-watch:  ## Watch mode for tests
	@echo "👀 Running tests in watch mode..."
	pytest-watch tests/

lint:  ## Run linters (ruff + mypy)
	@echo "🔍 Running linters..."
	ruff check agents/ utils/ --fix
	mypy agents/ utils/

format:  ## Format code with black
	@echo "✨ Formatting code..."
	black agents/ utils/ tests/

format-check:  ## Check formatting without changes
	@echo "🔍 Checking code formatting..."
	black --check agents/ utils/ tests/

clean:  ## Clean cache and build files
	@echo "🧹 Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/
	@echo "✅ Cleaned"

run:  ## Run FastAPI server
	@echo "🚀 Starting FastAPI server..."
	python main.py

dev:  ## Run with auto-reload (development mode)
	@echo "🔥 Starting dev server..."
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

db-migrate:  ## Run database migrations
	@echo "🗄️  Running database migrations..."
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "❌ DATABASE_URL not set"; \
		exit 1; \
	fi
	psql $$DATABASE_URL -f ../database/schema.sql
	psql $$DATABASE_URL -f ../database/migrations/001_optimize_indexes.sql
	@echo "✅ Migrations complete"

db-reset:  ## Reset database (WARNING: destroys all data)
	@echo "⚠️  WARNING: This will destroy all data!"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ]
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "❌ DATABASE_URL not set"; \
		exit 1; \
	fi
	psql $$DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	psql $$DATABASE_URL -f ../database/schema.sql
	@echo "✅ Database reset"

orchestrate:  ## Run hypervisor port orchestrator (usage: make orchestrate TASK="Port VMCS")
	@echo "🚀 Running orchestrator..."
	@if [ -z "$(TASK)" ]; then \
		echo "Usage: make orchestrate TASK=\"Port VMCS to x86\""; \
		exit 1; \
	fi
	python hypervisor_port_orchestrator.py "$(TASK)" $(ARGS)

orchestrate-build:  ## Run orchestrator with cargo build
	@echo "🚀 Running orchestrator with build..."
	python hypervisor_port_orchestrator.py "$(TASK)" --build

# Quick shortcuts
port:  ## Quick port task (alias for orchestrate)
	@$(MAKE) orchestrate

qemu:  ## Test hypervisor in QEMU after building
	@echo "🖥️  Running in QEMU..."
	cd ../../hyper/CHAIN-ARM-HYPERVISOR-ETERNA-main/x86_port && make qemu

# Docker support (optional)
docker-build:  ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t hectic-swarm:latest .

docker-run:  ## Run in Docker
	@echo "🐳 Running in Docker..."
	docker run -p 8000:8000 --env-file .env hectic-swarm:latest

# CI/CD
ci:  ## Run CI checks (lint + test)
	@echo "🔄 Running CI pipeline..."
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) test
	@echo "✅ CI checks passed"

# Stats
stats:  ## Show code statistics
	@echo "📊 Code Statistics:"
	@echo ""
	@echo "Lines of code:"
	@find agents utils -name "*.py" | xargs wc -l | tail -1
	@echo ""
	@echo "Test coverage:"
	@pytest tests/ --cov=agents --cov=utils --cov-report=term | tail -5

# Health check
health:  ## Check system health
	@echo "🏥 System Health Check"
	@echo ""
	@echo "Python version:"
	@python --version
	@echo ""
	@echo "Environment variables:"
	@echo "  OPENROUTER_API_KEY1: $$([ -n "$$OPENROUTER_API_KEY1" ] && echo '✅ Set' || echo '❌ Not set')"
	@echo "  DATABASE_URL: $$([ -n "$$DATABASE_URL" ] && echo '✅ Set' || echo '❌ Not set')"
	@echo "  OPENAI_API_KEY: $$([ -n "$$OPENAI_API_KEY" ] && echo '✅ Set' || echo '❌ Not set')"
	@echo ""
	@echo "Database connection:"
	@if [ -n "$$DATABASE_URL" ]; then \
		psql $$DATABASE_URL -c "SELECT 1" > /dev/null 2>&1 && echo "  ✅ Connected" || echo "  ❌ Failed"; \
	else \
		echo "  ⚠️  DATABASE_URL not set"; \
	fi
