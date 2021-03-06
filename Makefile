.EXPORT_ALL_VARIABLES:
DOCKER_BUILDKIT=1

.PHONY: up
up: build
	docker-compose -p mrr up -d --build

down:
	docker-compose -p mrr down

.PHONY: build
build: build-app

.PHONY: build-app
build-app:
	docker build -t meeting-room-remover:dev .
