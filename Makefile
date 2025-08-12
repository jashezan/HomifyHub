# ====================================================================================
#  Makefile for Django Projects
#
#  Usage:
#    make <target>
#
#  To see a list of all available commands:
#    make help
# ====================================================================================

# --- Configuration ---
# Use this to change the python interpreter
PYTHON := python3
# Path to your manage.py file. Adjust if your project structure is different.
MANAGEPY := homifyhub/manage.py

# --- Default Command ---
# The command that runs if you just type `make`
.DEFAULT_GOAL := help

# --- Phony Targets ---
# Declares targets that are not actual files. This prevents conflicts.
.PHONY: help run main shell test makemigrations migrate superuser collectstatic \
        app setup install freeze check-outdated clean lint format

# ====================================================================================
#  MAIN COMMANDS
# ====================================================================================

help: ## ✨ Show this help message
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

run: ## 🚀 Run the Django development server
	$(PYTHON) $(MANAGEPY) runserver

main: run ## Alias for 'run'

shell: ## 🐚 Open the Django shell (or shell_plus if available)
	$(PYTHON) $(MANAGEPY) shell

test: ## 🧪 Run all tests
	$(PYTHON) $(MANAGEPY) test

# ====================================================================================
#  DATABASE & MIGRATIONS
# ====================================================================================

makemigrations: ## 📝 Create new database migrations
	$(PYTHON) $(MANAGEPY) makemigrations $(app)

migrate: ## 🏗️ Apply database migrations
	$(PYTHON) $(MANAGEPY) migrate

superuser: ## 👑 Create a new superuser
	$(PYTHON) $(MANAGEPY) createsuperuser

# ====================================================================================
#  PROJECT MANAGEMENT
# ====================================================================================

app: ## 📦 Create a new Django app (e.g., make app name=products)
ifeq ($(name),)
	$(error "Please provide an app name. Usage: make app name=<app_name>")
endif
	$(PYTHON) $(MANAGEPY) startapp $(name)

collectstatic: ## 🚚 Collect all static files into STATIC_ROOT
	$(PYTHON) $(MANAGEPY) collectstatic --noinput

setup: ## 🛠️  Run initial project setup (install dependencies, migrate, create superuser)
	@make install
	@make migrate
	@make superuser

# ====================================================================================
#  DEPENDENCY MANAGEMENT
# ====================================================================================

install: ## 📥 Install Python dependencies from requirements.txt
	pip install -r requirements.txt

freeze: ## 🧊 Save current Python dependencies to requirements.txt
	pip freeze > requirements.txt

check-outdated: ## 🔎 Check for outdated Python packages
	pip list --outdated

# ====================================================================================
#  CODE QUALITY & CLEANUP
# ====================================================================================

lint: ## 🧹 Lint the code using flake8
	flake8 .

format: ## 🎨 Format the code using black
	black .

clean: ## 🗑️ Remove temporary Python files
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete