# Makefile for Talkabout project

.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test clean

help:
	@echo "Talkabout - Makefile Commands"
	@echo ""
	@echo "  make build           - Build Docker images"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - View logs"
	@echo "  make shell           - Open Django shell"
	@echo "  make migrate         - Run migrations"
	@echo "  make makemigrations  - Create migrations"
	@echo "  make createsuperuser - Create superuser"
	@echo "  make test            - Run tests"
	@echo "  make clean           - Clean containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec backend python manage.py shell

migrate:
	docker-compose exec backend python manage.py migrate

makemigrations:
	docker-compose exec backend python manage.py makemigrations

createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v
	docker system prune -f

setup: build up migrate createsuperuser
	@echo "Setup complete! Access the application at http://localhost:8000"
