# SolarOps AI — developer task runner.
# Usage: make <target>.  All Python targets put the repo root on PYTHONPATH.

export PYTHONPATH := .

.DEFAULT_GOAL := help
.PHONY: help install data train backend frontend test lint clean docker-up docker-down

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

data: ## Seed farm registry and build the RAG index
	bash scripts/load_data.sh

train: ## Train forecasting + anomaly models
	bash scripts/train_models.sh

backend: ## Run the FastAPI backend (port 8000)
	bash scripts/run_backend.sh

frontend: ## Run the Streamlit console (port 8501)
	bash scripts/run_streamlit.sh

test: ## Run the test suite
	python -m pytest backend/tests -q

lint: ## Byte-compile check across the source tree
	python -m compileall -q backend ml agents rag workflows streamlit_app

clean: ## Remove caches and trained artifacts
	rm -rf .pytest_cache **/__pycache__ data/processed/models/* data/processed/rag_index/*

docker-up: ## Build and start the full stack via docker-compose
	docker compose up --build

docker-down: ## Stop the stack
	docker compose down
