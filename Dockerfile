FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install uv
RUN uv pip install --system -r pyproject.toml

COPY fastapi_backend.py .
COPY database_schema.sql .
COPY populate_database.py .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "fastapi_backend:app", "--host", "0.0.0.0", "--port", "8000"]
