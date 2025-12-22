.PHONY: help build up down logs clean restart ps shell db-shell migrate seed

# Цвета для вывода
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Показать этот файл помощи
	@echo "$(BLUE)=== Logistics Management System - Docker Commands ===$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Построить Docker образы
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build

up: ## Запустить все сервисы
	@echo "$(BLUE)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started!$(NC)"
	@echo "$(BLUE)URLs:$(NC)"
	@echo "  API: http://localhost:8000"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc: http://localhost:8000/redoc"
	@echo "  Web UI: http://localhost:8001"
	@echo "  PostgreSQL: localhost:5432"

down: ## Остановить все сервисы
	@echo "$(BLUE)Stopping all services...$(NC)"
	docker-compose down

logs: ## Просмотреть логи всех контейнеров (Ctrl+C для выхода)
	docker-compose logs -f

logs-api: ## Просмотреть логи API
	docker-compose logs -f api

logs-db: ## Просмотреть логи PostgreSQL
	docker-compose logs -f postgres

logs-web: ## Просмотреть логи Nginx
	docker-compose logs -f web_server

restart: ## Перезагрузить все сервисы
	@echo "$(BLUE)Restarting all services...$(NC)"
	docker-compose restart

ps: ## Показать статус контейнеров
	@docker-compose ps

clean: ## Очистить все контейнеры, образы и данные
	@echo "$(RED)Warning: This will delete all containers, images, and data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		echo "$(GREEN)✓ Cleaned up!$(NC)"; \
	else \
		echo "$(BLUE)Cancelled.$(NC)"; \
	fi

shell: ## Подключиться к контейнеру API (bash)
	docker exec -it logistics_api /bin/bash

db-shell: ## Подключиться к PostgreSQL контейнеру (psql)
	docker exec -it logistics_postgres psql -U logistics -d logistics_db

migrate: ## Запустить миграции БД
	docker exec -it logistics_api python migrate.py

seed: ## Заполнить БД тестовыми данными
	docker exec -it logistics_api python populate_database.py

test: ## Запустить тесты
	docker exec -it logistics_api pytest

# Development targets
dev-build: ## Построить образы для разработки
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

dev-up: ## Запустить с hot-reload для разработки
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Database backup
backup: ## Сделать backup БД
	@echo "$(BLUE)Backing up database...$(NC)"
	docker exec logistics_postgres pg_dump -U logistics -d logistics_db -F c -b -v > backups/logistics_$(shell date +%Y%m%d_%H%M%S).dump
	@echo "$(GREEN)✓ Backup created!$(NC)"

restore: ## Восстановить БД из backup (использование: make restore FILE=backups/logistics_20240101_000000.dump)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Please specify FILE parameter$(NC)"; \
		echo "Usage: make restore FILE=backups/logistics_*.dump"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database from $(FILE)...$(NC)"
	docker exec -i logistics_postgres pg_restore -U logistics -d logistics_db -c $(FILE)
	@echo "$(GREEN)✓ Database restored!$(NC)"

# Status and info
status: ps ## Alias для ps

info: ## Показать информацию о сервисах
	@echo "$(BLUE)=== Docker Services Information ===$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)=== Docker Images ===$(NC)"
	@docker images | grep logistics
	@echo ""
	@echo "$(BLUE)=== Docker Networks ===$(NC)"
	@docker network ls | grep logistics

# Docker system cleanup
prune: ## Очистить неиспользуемые Docker объекты
	@echo "$(BLUE)Pruning Docker system...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✓ Done!$(NC)"

# API health check
health: ## Проверить здоровье API
	@curl -s http://localhost:8000/api/health | python -m json.tool

# Database stats
db-stats: ## Показать статистику БД
	@docker exec logistics_postgres psql -U logistics -d logistics_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

db-count: ## Показать количество записей в таблицах
	@docker exec logistics_postgres psql -U logistics -d logistics_db << EOF
	SELECT tablename, (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name=tablename) FROM pg_tables WHERE schemaname='public';
	EOF

# Version info
version: ## Показать версии используемых инструментов
	@echo "$(BLUE)=== Version Information ===$(NC)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@echo "PostgreSQL image: postgres:15-alpine"
	@echo "Python: 3.11"
	@echo "FastAPI: see requirements.txt"
