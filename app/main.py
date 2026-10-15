# app/main.py
import time
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 1. Сначала настраиваем логирование!
from app.config.logging_config import setup_logging
setup_logging()

logger = structlog.get_logger()

from app.config.config import get_settings
from app.core.db import get_db_session, save_prediction
from app.core.cache import get_cache, check_cache, save_to_cache
from app.models.model_pickle import SideModelPickle
from app.models.model_json import SideModelJSON
from app.schemas.predictions import (
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, HealthResponse, ErrorResponse
)


settings = get_settings()

# Глобальные переменные
ml_model_instance = None
db_engine = None
session_factory = None
cache_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при старте, очистка при shutdown."""
    global ml_model_instance, db_engine, session_factory, cache_client

    logger.info("app_starting", env=settings.ENV)

    # Загрузка модели
    if settings.MODEL_TYPE == "type_pickle":
        ml_model_instance = SideModelPickle()
        model_path = settings.MODEL_PATH_PICKLE
    elif settings.MODEL_TYPE == "type_json":
        ml_model_instance = SideModelJSON()
        model_path = settings.MODEL_PATH_JSON
    else:
        raise ValueError(f"Unknown MODEL_TYPE: {settings.MODEL_TYPE}")

    from pathlib import Path
    abs_path = Path(__file__).resolve().parent.parent / model_path.lstrip("./")
    logger.info(f"Loading model from: {abs_path}")
    ml_model_instance.load(str(abs_path))

    # Инициализация БД
    db_engine, session_factory = await get_db_session()

    # Инициализация кэша
    cache_client = await get_cache(settings.REDIS_URL)

    logger.info("app_started")

    yield

    # Shutdown
    logger.info("app_shutting_down")
    if db_engine:
        await db_engine.dispose()
    if cache_client:
        await cache_client.close()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV == "development" else ["https://client.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
async def health_check():
    """Health check для Kubernetes readiness/liveness probes."""
    return HealthResponse(
        status="ok",
        model={
            "type": settings.MODEL_TYPE,
            "loaded": ml_model_instance is not None,
            "db_connected": db_engine is not None,
            "cache_connected": cache_client is not None
        },
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["predictions"]
)
async def predict(request: PredictionRequest, req: Request):
    """Основной endpoint предсказания."""
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    try:
        # 1. Проверка кэша
        cache_key = f"pred:{request.age}:{request.income}:{request.has_loan}"
        cached = await check_cache(cache_client, cache_key)
        if cached:
            logger.info("cache_hit", request_id=request_id)
            return cached

        # 2. Предсказание
        results = ml_model_instance.predict(request.model_dump())
        result = results[0] if isinstance(results, list) else results

        # 3. Сохранение в БД (асинхронно, не блокируем ответ)
        try:
            await save_prediction(
                db_engine,
                session_factory,
                request_id=request_id,
                input_data=request.model_dump(),
                prediction=result
            )
        except Exception as e:
            logger.error("db_save_failed", error=str(e), request_id=request_id)

        # 4. Кэширование результата
        latency_ms = (time.perf_counter() - start_time) * 1000
        response = PredictionResponse(
            prediction=result["prediction"],
            probability=result.get("probability", 0.95),
            class_name=result.get("class_name", "Unknown"),
            request_id=request_id,
            model_version=result.get("model_version", "1.0"),
            latency_ms=round(latency_ms, 2)
        )

        await save_to_cache(cache_client, cache_key, response, ttl=settings.CACHE_TTL)

        logger.info(
            "prediction_completed",
            request_id=request_id,
            latency_ms=latency_ms,
            prediction=result["prediction"]
        )

        return response

    except Exception as e:
        logger.exception("prediction_failed", request_id=request_id)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )

@app.post("/predict/batch", tags=["predictions"])
async def batch_predict(request: BatchPredictionRequest):
    """Batch предсказание для высокой пропускной способности."""
    items = [item.model_dump() for item in request.items]
    results = ml_model_instance.predict(items)
    return {"predictions": results, "count": len(results)}

# Global error handler
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
            instance=str(request.url)
        ).model_dump()
    )