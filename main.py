# main.py
# from app.config.logging_config import LOGGING_CONFIG
# import app.config.logging_config.json
from app.main import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # В production заменить на False
        workers=1,  # Для асинхронного кода с uvicorn обычно 1 worker, масштабирование через Docker/K8s
        log_config="app/config/logging_config.json",
    )
