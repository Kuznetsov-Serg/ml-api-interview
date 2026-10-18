# app/api/monitoring.py
from datetime import UTC, datetime

from fastapi import APIRouter, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config.config import get_settings
from app.schemas.predictions import HealthResponse

router = APIRouter(tags=["monitoring"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check для Kubernetes readiness/liveness probes."""
    # Проверяем состояние глобальных переменных из main.py
    app_state = request.app.state

    return HealthResponse(
        status="ok",
        model={
            "type": settings.MODEL_TYPE,
            "loaded": getattr(app_state, "ml_model_instance", None) is not None,
            "db_connected": getattr(app_state, "db_engine", None) is not None,
            "cache_connected": getattr(app_state, "cache_client", None) is not None,
        },
        timestamp=datetime.now(tz=UTC),
        version="1.0.0",
    )


@router.get("/metrics")
async def metrics():
    """Endpoint для сбора метрик Prometheus."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
