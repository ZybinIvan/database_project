## 🚀 Инструкция по быстрому развертыванию

### Вариант 1: Локальное развертывание (без Docker)

#### 1. Установка PostgreSQL

**Windows:**
- Загрузить с https://www.postgresql.org/download/windows/
- Установить с параметрами по умолчанию (порт 5432)
- Запомнить пароль суперпользователя `postgres`

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### 2. Создание БД и пользователя

```bash
# Подключиться к PostgreSQL
psql -U postgres

# В консоли PostgreSQL:
CREATE DATABASE logistics_db;
CREATE USER logistics WITH PASSWORD 'logistics_password';
ALTER ROLE logistics SET client_encoding TO 'utf8';
ALTER ROLE logistics SET default_transaction_isolation TO 'read committed';
ALTER ROLE logistics SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE logistics_db TO logistics;
\q
```

#### 3. Загрузка схемы БД

```bash
psql -U postgres -d logistics_db -f database_schema.sql
```

#### 4. Установка Python и зависимостей

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать (Linux/Mac)
source venv/bin/activate

# Активировать (Windows)
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

#### 5. Заполнить БД данными

```bash
python populate_database.py
```

#### 6. Запустить FastAPI сервер

```bash
python -m uvicorn fastapi_backend:app --reload --host 0.0.0.0 --port 8000
```

#### 7. Открыть веб-интерфейс

Вариант A: Через файловый протокол
```
file:///путь/до/interface_web.html
```

Вариант B: Через локальный HTTP сервер
```bash
# В отдельном терминале
python -m http.server 8001
```
Затем откройте `http://localhost:8001/interface_web.html`

Вариант C: Через Swagger UI
```
http://localhost:8000/docs
```

---

### Вариант 2: Docker развертывание

#### Требования

- Docker Desktop (https://www.docker.com/products/docker-desktop)

#### Шаг 1: Создать Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установить зависимости системы
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Скопировать требования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать приложение
COPY fastapi_backend.py .
COPY database_schema.sql .
COPY populate_database.py .

# Expose порты
EXPOSE 8000

# Run приложение
CMD ["python", "-m", "uvicorn", "fastapi_backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Шаг 2: Создать docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: logistics_postgres
    environment:
      POSTGRES_USER: logistics
      POSTGRES_PASSWORD: logistics_password
      POSTGRES_DB: logistics_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database_schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U logistics" ]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: ../../../../Загрузки
    container_name: logistics_api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://logistics:logistics_password@postgres:5432/logistics_db
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - .:/app
    command: sh -c "python populate_database.py && python -m uvicorn fastapi_backend:app --host 0.0.0.0 --port 8000 --reload"

volumes:
  postgres_data:
```

#### Шаг 3: Запустить через Docker Compose

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить логи
docker-compose logs -f api

# Остановить
docker-compose down

# Очистить данные (включая БД)
docker-compose down -v
```

#### Шаг 4: Доступ к приложению

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- PostgreSQL: localhost:5432 (пользователь: logistics)

---

### Вариант 3: Docker без compose (отдельные контейнеры)

```bash
# 1. Запустить PostgreSQL контейнер
docker run -d \
  --name logistics_postgres \
  -e POSTGRES_USER=logistics \
  -e POSTGRES_PASSWORD=logistics_password \
  -e POSTGRES_DB=logistics_db \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# 2. Подождать инициализации (10-15 сек)
sleep 15

# 3. Загрузить схему
docker exec -i logistics_postgres psql -U logistics -d logistics_db < database_schema.sql

# 4. Построить образ API
docker build -t logistics_api .

# 5. Запустить контейнер API
docker run -d \
  --name logistics_api \
  -p 8000:8000 \
  --link logistics_postgres:postgres \
  -e DATABASE_URL=postgresql://logistics:logistics_password@postgres:5432/logistics_db \
  logistics_api

# 6. Проверить логи
docker logs logistics_api
```

---

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env`:

```env
# PostgreSQL
DATABASE_URL=postgresql://logistics:logistics_password@localhost:5432/logistics_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=logistics_db
DB_USER=logistics
DB_PASSWORD=logistics_password

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# Безопасность (production)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Используйте в Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
```

---

## 📊 Проверка после установки

```bash
# 1. Проверить подключение к БД
psql -U logistics -d logistics_db -c "SELECT COUNT(*) FROM orders;"

# 2. Проверить API
curl http://localhost:8000/api/health

# 3. Получить список заказов
curl http://localhost:8000/api/orders

# 4. Проверить документацию
curl http://localhost:8000/openapi.json
```

---

## 📈 Мониторинг и логирование

### Включить логирование в FastAPI

Обновите `fastapi_backend.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

# Конфигурация логирования
log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler = RotatingFileHandler(
    'logs/logistics.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
```

### Мониторинг БД

```bash
# Размер БД
psql -U logistics -d logistics_db -c "SELECT pg_size_pretty(pg_database_size('logistics_db'));"

# Таблица с наибольшим размером
psql -U logistics -d logistics_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Активные подключения
psql -U postgres -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

---

## 🔄 Бэкап и восстановление

### Создание бэкапа

```bash
# Полный бэкап БД
pg_dump -U logistics -d logistics_db -F c -b -v -f logistics_backup.dump

# Бэкап в текстовом формате
pg_dump -U logistics -d logistics_db -f logistics_backup.sql
```

### Восстановление из бэкапа

```bash
# Из binary dump
pg_restore -U logistics -d logistics_db -v logistics_backup.dump

# Из SQL dump
psql -U logistics -d logistics_db -f logistics_backup.sql
```

### Автоматический бэкап (cron)

```bash
# Отредактировать crontab
crontab -e

# Добавить строку для ежедневного бэкапа в 2:00 AM
0 2 * * * pg_dump -U logistics -d logistics_db -F c -f /backups/logistics_$(date +\%Y\%m\%d_\%H\%M\%S).dump
```

---

## 🐛 Решение проблем при развертывании

### Проблема: "could not connect to server"

```bash
# Проверить, запущена ли PostgreSQL
sudo systemctl status postgresql  # Linux
brew services list               # macOS
sc query postgresql-x64-15       # Windows

# Запустить PostgreSQL
sudo systemctl start postgresql   # Linux
brew services start postgresql@15 # macOS
```

### Проблема: "permission denied"

```bash
# Проверить права доступа
psql -U postgres -d postgres -c "SELECT * FROM pg_user WHERE usename = 'logistics';"

# Сбросить пароль
psql -U postgres -c "ALTER USER logistics WITH PASSWORD 'logistics_password';"
```

### Проблема: PORT 5432 уже занят

```bash
# Linux/Mac - найти процесс
lsof -i :5432

# Убить процесс
kill -9 <PID>

# Или измениить порт PostgreSQL в postgresql.conf
# Найти строку: port = 5432
# Изменить на: port = 5433
```

### Проблема: "ModuleNotFoundError: No module named 'fastapi'"

```bash
# Активировать виртуальное окружение
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Переустановить зависимости
pip install -r requirements.txt
```

### Проблема: CORS ошибки

Убедитесь, что в `fastapi_backend.py` добавлено:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📱 Production развертывание

### Рекомендации для production

1. **Используйте переменные окружения** для всех конфигураций
2. **Отключите debug режим** (`API_DEBUG=False`)
3. **Используйте Gunicorn** вместо Uvicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 fastapi_backend:app
   ```

4. **Настройте reverse proxy** (Nginx/Apache):
   ```nginx
   upstream logistics_api {
       server 127.0.0.1:8000;
   }
   
   server {
       listen 80;
       server_name logistics.example.com;
       
       location / {
           proxy_pass http://logistics_api;
       }
   }
   ```

5. **Включите SSL/TLS** (Let's Encrypt):
   ```bash
   sudo certbot certonly --standalone -d logistics.example.com
   ```

6. **Используйте systemd service** для автозапуска:
   ```ini
   [Unit]
   Description=Logistics API Service
   After=network.target
   
   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/logistics
   ExecStart=/usr/bin/python3 -m gunicorn -w 4 -b 0.0.0.0:8000 fastapi_backend:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

---

## 📚 Полезные команды

```bash
# Очистить Docker образы и контейнеры
docker system prune -a

# Посмотреть размер БД в контейнере
docker exec logistics_postgres du -sh /var/lib/postgresql/data

# Вывести логи в реальном времени
docker-compose logs -f api

# Выполнить SQL команду в контейнере
docker exec logistics_postgres psql -U logistics -d logistics_db -c "SELECT COUNT(*) FROM orders;"

# Загрузить backup в контейнер
docker cp logistics_backup.sql logistics_postgres:/
docker exec logistics_postgres psql -U logistics -d logistics_db -f /logistics_backup.sql
```

---

## ✅ Чек-лист развертывания

- [ ] PostgreSQL установлена и запущена
- [ ] БД `logistics_db` создана
- [ ] Пользователь `logistics` создан
- [ ] Схема БД загружена (`database_schema.sql`)
- [ ] Python виртуальное окружение создано
- [ ] Зависимости установлены (`requirements.txt`)
- [ ] БД заполнена данными (`populate_database.py`)
- [ ] FastAPI сервер запущен
- [ ] Веб-интерфейс доступен
- [ ] API отвечает на запросы (`/api/health`)

**Готово к использованию! 🎉**
