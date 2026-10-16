# Dockerfile
# ============================================================
# Stage 1: Builder — установка зависимостей
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Устанавливаем системные зависимости для компиляции (если нужны C-extensions)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Копируем только requirements для кэширования слоя зависимостей
COPY requirements.txt .

# Устанавливаем зависимости в отдельный префикс (чтобы потом скопировать только их)
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Stage 2: Production — финальный образ
# ============================================================
FROM python:3.11-slim AS production

WORKDIR /app

# Переменные окружения
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/install/bin:$PATH

# Создаём непривилегированного пользователя
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Копируем установленные зависимости из builder
COPY --from=builder /install /usr/local

# Копируем код приложения
COPY app/ ./app/
COPY data/ ./data/

# Копируем конфигурацию логирования (если используется JSON-конфиг)
# COPY logging_config.json ./

# Генерация dummy-моделей при сборке (если нужно)
RUN python -m app.utils.create_dummy_models

# Права на файлы
RUN chown -R appuser:appuser /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Expose порт
EXPOSE 8000

# Запуск приложения
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Запуск с JSON конфигом логирования
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "./app/config/logging_config.json"]
