.PHONY: build run run-prod stop clean logs logs-prod

DOCKER_COMPOSE := docker compose
COMPOSE_FILE := docker-compose.yml
COMPOSE_FILE_PROD := docker-compose.prod.yml

# Folders to clean
DATA_FOLDER := ./data
OUTPUT_FOLDER := ./output
LOG_FOLDER := ./logs

build:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) build

run:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) up

run-prod:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_PROD) up -d

stop:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) down

stop-prod:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_PROD) down

clean:
	# Stop and remove containers, volumes, and networks
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) down -v
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_PROD) down -v
	# Remove unused Docker images
	docker image prune -f
	# Remove all Docker images associated with this project
	docker rmi $$(docker images -q --filter=reference="*/*:latest" --filter=reference="*/*:<your-tag>") || true
	# Remove all stopped containers
	docker container prune -f
	# Remove all Docker builds
	docker builder prune -f
		# Remove files from data and output folders
	rm -rf $(DATA_FOLDER)/*
	rm -rf $(OUTPUT_FOLDER)/*
	rm -rf $(LOG_FOLDER)/*

logs:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) logs -f

logs-prod:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_PROD) logs -f
