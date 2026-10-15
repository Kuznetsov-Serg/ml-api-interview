# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Критично: добавляем /app в PYTHONPATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY app/ ./app/
COPY data/ ./data/

# Генерация dummy-моделей при сборке
RUN python -m app.utils.create_dummy_models

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Запуск с JSON конфигом логирования
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "./app/config/logging_config.json"]