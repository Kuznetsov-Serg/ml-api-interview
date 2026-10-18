# app/main.py
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.config import get_settings
from app.config.logging_config import setup_logging
from app.core.cache import get_cache
from app.core.db import get_db_session
from app.models.model_json import SideModelJSON
from app.models.model_pickle import SideModelPickle
from app.schemas.predictions import ErrorResponse

# 1. Логирование и настройки
setup_logging()
logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при старте, очистка при shutdown."""
    logger.info("app_starting", env=settings.ENV)

    # Загрузка модели
    if settings.MODEL_TYPE == "type_pickle":
        app.state.ml_model_instance = SideModelPickle()
        model_path = settings.MODEL_PATH_PICKLE
    elif settings.MODEL_TYPE == "type_json":
        app.state.ml_model_instance = SideModelJSON()
        model_path = settings.MODEL_PATH_JSON
    else:
        raise ValueError(f"Unknown MODEL_TYPE: {settings.MODEL_TYPE}")

    from pathlib import Path

    abs_path = Path(__file__).resolve().parent.parent / model_path.lstrip("./")
    logger.info(f"Loading model from: {abs_path}")
    app.state.ml_model_instance.load(str(abs_path))

    # Инициализация БД
    app.state.db_engine, app.state.session_factory = await get_db_session()

    # Инициализация кэша
    app.state.cache_client = await get_cache(settings.REDIS_URL, settings.IS_REDIS)

    logger.info("app_started")
    yield

    # Shutdown
    logger.info("app_shutting_down")

    db_engine = getattr(app.state, "db_engine", None)
    if db_engine is not None:
        await db_engine.dispose()

    cache_client = getattr(app.state, "cache_client", None)
    if cache_client is not None:
        await cache_client.close()


# 2. Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 3. Middleware (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        ["*"] if settings.ENV == "development" else ["https://client.example.com"]
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Prometheus Instrumentator (автоматически собирает http_requests_total и duration)
Instrumentator().instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)

# 5. Подключение роутеров
from app.api import monitoring, predictions

app.include_router(monitoring.router)
app.include_router(predictions.router)


# 6. Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_error", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            type="InternalError",
            title="Internal Server Error",
            status=500,
            detail=str(exc) if settings.ENV == "development" else "Internal error",
            instance=str(request.url),
        ).model_dump(),
    )
