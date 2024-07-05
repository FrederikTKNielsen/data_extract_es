.PHONY: build run run-prod stop clean

build:
	docker-compose build

run:
	docker-compose up

run-prod:
	docker-compose -f docker-compose.prod.yml up -d

stop:
	docker-compose down

stop-prod:
	docker-compose -f docker-compose.prod.yml down

clean:
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v

logs:
	docker-compose logs -f

logs-prod:
	docker-compose -f docker-compose.prod.yml logs -f