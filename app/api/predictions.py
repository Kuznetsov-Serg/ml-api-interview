# app/api/predictions.py
import time
import uuid

import structlog
from fastapi import APIRouter, HTTPException, Request

from app.config.config import get_settings
from app.core.cache import check_cache, save_to_cache
from app.core.db import save_prediction
from app.core.metrics import (
    cache_hits_total,
    cache_misses_total,
    model_prediction_latency,
)
from app.schemas.predictions import (
    BatchPredictionRequest,
    ErrorResponse,
    PredictionRequest,
    PredictionResponse,
)

# Инициализируем логгер
logger = structlog.get_logger(__name__)

router = APIRouter(tags=["predictions"])
settings = get_settings()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def predict(request: PredictionRequest, req: Request):
    """Основной endpoint предсказания."""
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    app_state = req.app.state

    try:
        # 1. Проверка кэша
        cache_key = f"pred:{request.age}:{request.income}:{request.has_loan}"
        cached = None
        if getattr(app_state, "cache_client", None):
            cached = await check_cache(app_state.cache_client, cache_key)

        if cached:
            cache_hits_total.labels(endpoint="/predict").inc()
            return cached

        cache_misses_total.labels(endpoint="/predict").inc()

        # 2. Предсказание с замером времени
        pred_start = time.perf_counter()
        results = app_state.ml_model_instance.predict(request.model_dump())
        result = results[0] if isinstance(results, list) else results
        pred_latency = time.perf_counter() - pred_start

        model_prediction_latency.labels(
            endpoint="/predict", model_type=settings.MODEL_TYPE
        ).observe(pred_latency)

        # 3. Сохранение в БД (асинхронно, не блокируем ответ)
        try:
            await save_prediction(
                app_state.db_engine,
                app_state.session_factory,
                request_id=request_id,
                input_data=request.model_dump(),
                prediction=result,
            )
        except Exception as e:  # noqa: BLE001
            # Теперь logger здесь работает корректно!
            logger.error("db_save_failed", error=str(e), request_id=request_id)

        # 4. Кэширование результата
        total_latency_ms = (time.perf_counter() - start_time) * 1000
        response = PredictionResponse(
            prediction=result["prediction"],
            probability=result.get("probability", 0.95),
            class_name=result.get("class_name", "Unknown"),
            request_id=request_id,
            model_version=result.get("model_version", "1.0"),
            latency_ms=round(total_latency_ms, 2),
        )

        if getattr(app_state, "cache_client", None):
            await save_to_cache(
                app_state.cache_client, cache_key, response, ttl=settings.CACHE_TTL
            )

        return response

    except Exception as e:
        logger.exception("prediction_failed", request_id=request_id)
        raise HTTPException(status_code=500, detail=f"Internal error: {e!s}")


@router.post("/predict/batch")
async def batch_predict(request: BatchPredictionRequest, req: Request):
    """Batch предсказание для высокой пропускной способности."""
    app_state = req.app.state
    items = [item.model_dump() for item in request.items]

    pred_start = time.perf_counter()
    results = app_state.ml_model_instance.predict(items)
    pred_latency = time.perf_counter() - pred_start

    model_prediction_latency.labels(
        endpoint="/predict/batch", model_type=settings.MODEL_TYPE
    ).observe(pred_latency)

    return {"predictions": results, "count": len(results)}
