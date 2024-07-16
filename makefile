.PHONY: build run run-prod stop clean logs logs-prod

DOCKER_COMPOSE := docker compose
COMPOSE_FILE := docker-compose.yml
COMPOSE_FILE_PROD := docker-compose.prod.yml

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
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) down -v
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_PROD) down -v

logs:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) logs -f

logs-prod:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_PROD) logs -f