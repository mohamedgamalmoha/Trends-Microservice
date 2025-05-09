# Makefile for managing multiple microservices
# Configuration
PACKAGE_MANAGER := pip
DEFAULT_REQUIREMENTS_FILE := requirements-dev.txt
TEST_RUNNER := pytest
TEST_FLAGS := -v -p no:warnings --asyncio-mode=auto --tb=short

# Get all subdirectories that might be services
SERVICES := $(notdir $(wildcard */))

# Help command
.PHONY: help
help:
	@echo "Microservices Management Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make list                        - List all available services"
	@echo "  make install [SERVICE]           - Install dependencies for SERVICE or all services"
	@echo "  make test [SERVICE]              - Run tests for SERVICE or all services"
	@echo "  make pre-run [SERVICE]           - Run pre-test setup for SERVICE or all services"
	@echo "  make run [SERVICE]               - Run tests for SERVICE or all services"
	@echo "  make post-run [SERVICE]          - Run post-test cleanup for SERVICE or all services"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build [SERVICE]      - Build Docker image for SERVICE or all services"
	@echo "  make docker-run [SERVICE]        - Run Docker container for SERVICE or all services"
	@echo "  make docker-clean                - Remove all Docker containers, images, volumes, and networks"
	@echo ""
	@echo "Cleanup commands:"
	@echo "  make clean [SERVICE]             - Clean Python cache files for SERVICE or all services"
	@echo ""
	@echo "Available services:"
	@for service in $(SERVICES); do \
		echo "  $$service"; \
	done

# List available services
.PHONY: list
list:
	@echo "Available services:"
	@for service in $(SERVICES); do \
		echo "  $$service"; \
	done

# Generic rule for installing requirements
.PHONY: install-%
install-%:
	@echo "Installing dependencies for $*..."
	@if [ -d "$*" ]; then \
		cd $* && \
		if [ -f "requirements-dev.txt" ]; then \
			$(PACKAGE_MANAGER) install -r requirements-dev.txt; \
		elif [ -f "requirements.txt" ]; then \
			$(PACKAGE_MANAGER) install -r requirements.txt; \
		elif [ -f "package.json" ]; then \
			npm install; \
		else \
			echo "No recognized dependency file found for $*"; \
		fi \
	else \
		echo "Service $* not found"; \
		exit 1; \
	fi

# Generic rule for running pre-test commands
.PHONY: pre-run-%
pre-run-%: install-%
	@echo "Running pre-test setup for $*..."
	@if [ -d "$*" ] && [ -f "$*/Makefile" ]; then \
		cd $* && $(MAKE) -f Makefile test-pre-run 2>/dev/null || echo "No test-pre-run target in $*/Makefile"; \
	fi

# Generic rule for running tests
.PHONY: run-%
run-%:
	@echo "Running tests for $*..."
	@if [ -d "$*" ]; then \
		cd $* && \
		if [ -f "Makefile" ]; then \
			$(MAKE) -f Makefile test-run 2>/dev/null || \
			echo "No test-run target in $*/Makefile, using default test runner"; \
			$(TEST_RUNNER) $(TEST_FLAGS); \
		else \
			$(TEST_RUNNER) $(TEST_FLAGS); \
		fi \
	else \
		echo "Service $* not found"; \
		exit 1; \
	fi

# Generic rule for running post-test commands
.PHONY: post-run-%
post-run-%:
	@echo "Running post-test cleanup for $*..."
	@if [ -d "$*" ] && [ -f "$*/Makefile" ]; then \
		cd $* && $(MAKE) -f Makefile test-post-run 2>/dev/null || echo "No test-post-run target in $*/Makefile"; \
	fi

# Generic rule for full test process on a service
.PHONY: test-%
test-%: pre-run-% run-% post-run-%
	@echo "Completed testing for $*"

# Default commands when no service is specified
.PHONY: install test pre-run run post-run

# Install all services
install:
	@for service in $(SERVICES); do \
		$(MAKE) install-$$service; \
	done

# Pre-run for all services
pre-run:
	@for service in $(SERVICES); do \
		$(MAKE) pre-run-$$service; \
	done

# Run tests for all services
run:
	@for service in $(SERVICES); do \
		$(MAKE) run-$$service; \
	done

# Post-run for all services
post-run:
	@for service in $(SERVICES); do \
		$(MAKE) post-run-$$service; \
	done

# Test all services
test:
	@for service in $(SERVICES); do \
		$(MAKE) test-$$service; \
	done

# Docker commands
.PHONY: docker-build-% docker-run-% docker-clean

# Build Docker image for specific service
docker-build-%:
	@echo "Building Docker image for $*..."
	@if [ -d "$*" ] && [ -f "$*/docker-compose.yml" ]; then \
		cd $* && docker compose build; \
	elif [ -d "$*" ] && [ -f "$*/Dockerfile" ]; then \
		docker build -t $* $*; \
	else \
		echo "No Dockerfile or docker-compose.yml found for $*"; \
		exit 1; \
	fi

# Run Docker container for specific service
docker-run-%:
	@echo "Running Docker container for $*..."
	@if [ -d "$*" ] && [ -f "$*/docker-compose.yml" ]; then \
		cd $* && docker compose up --build; \
	else \
		echo "No docker-compose.yml found for $*"; \
		exit 1; \
	fi

# Build Docker images for all services or the default service
docker-build:
	@if [ -f "docker-compose.yml" ]; then \
		echo "Building all services defined in root docker-compose.yml..."; \
		docker compose build; \
	else \
		for service in $(SERVICES); do \
			if [ -f "$service/docker-compose.yml" ] || [ -f "$service/Dockerfile" ]; then \
				$(MAKE) docker-build-$service; \
			fi \
		done \
	fi

# Run Docker containers for all services or the default service
docker-run:
	@if [ -f "docker-compose.yml" ]; then \
		echo "Starting all services defined in root docker-compose.yml..."; \
		docker compose up --build; \
	else \
		for service in $(SERVICES); do \
			if [ -f "$service/docker-compose.yml" ]; then \
				$(MAKE) docker-run-$service; \
			fi \
		done \
	fi

# Clean Docker resources (USE WITH CAUTION)
docker-clean:
	@echo "WARNING: This will remove ALL Docker containers, images, volumes, and networks"
	@read -p "Are you sure you want to continue? [y/N] " confirm && \
	if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then \
		echo "Stopping all running containers..."; \
		docker stop $(docker ps -a -q) 2>/dev/null || true; \
		echo "Removing all containers..."; \
		docker rm $(docker ps -a -q) 2>/dev/null || true; \
		echo "Removing all images..."; \
		docker rmi $(docker images -q) -f 2>/dev/null || true; \
		echo "Removing all volumes..."; \
		docker volume rm $(docker volume ls -q) 2>/dev/null || true; \
		echo "Removing all networks..."; \
		docker network rm $(docker network ls -q) 2>/dev/null || true; \
		echo "Performing system prune to clean up any remaining resources..."; \
		docker system prune -a --volumes -f; \
		echo "Docker cleanup complete!"; \
	else \
		echo "Docker cleanup aborted."; \
	fi

# Cleanup commands
.PHONY: clean-% clean

# Clean specific service
clean-%:
	@echo "Cleaning up Python cache files for $*..."
	@if [ -d "$*" ]; then \
		find $* -type d -name "__pycache__" -exec rm -rf {} +; \
		find $* -type d -name ".pytest_cache" -exec rm -rf {} +; \
		find $* -type f -name "*.pyc" -delete; \
		find $* -type f -name "*.pyo" -delete; \
		echo "Python cache cleanup for $* complete!"; \
	else \
		echo "Service $* not found"; \
		exit 1; \
	fi

# Clean all services
clean:
	@echo "Cleaning up Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Python cache cleanup complete!"

# Default target
.DEFAULT_GOAL := help
