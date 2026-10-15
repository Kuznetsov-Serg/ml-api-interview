# app/main.py
import time
import uuid
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pathlib import Path

from app.config import get_settings
from app.schemas.schemas import PredictionRequest, PredictionResponse, HealthResponse, ErrorResponse
from app.models.model_type_a import SideModelA
from app.models.model_type_b import SideModelB

logger = logging.getLogger("uvicorn.error")
settings = get_settings()

# Глобальная переменная для хранения экземпляра модели
ml_model_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ml_model_instance
    logger.info("Starting up application...")

    # Factory pattern: выбираем реализацию в зависимости от конфига
    if settings.MODEL_TYPE == "type_a":
        ml_model_instance = SideModelA()
        model_path = settings.MODEL_PATH_A
    elif settings.MODEL_TYPE == "type_b":
        ml_model_instance = SideModelB()
        model_path = settings.MODEL_PATH_B
    else:
        raise ValueError(f"Unknown MODEL_TYPE: {settings.MODEL_TYPE}")

    # Преобразуем относительный путь в абсолютный для надежности
    abs_path = Path(__file__).resolve().parent.parent / model_path.lstrip("./")
    logger.info(f"Loading model from: {abs_path}")

    ml_model_instance.load(str(abs_path))
    logger.info("Model loaded successfully!")

    yield

    logger.info("Shutting down application...")
    ml_model_instance = None

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
async def health_check():
    return HealthResponse(
        status="ok",
        model={"type": settings.MODEL_TYPE, "loaded": ml_model_instance is not None},
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["predictions"]
)
async def predict(request: PredictionRequest):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    try:
        # 1. Предсказание
        result = ml_model_instance.predict(request.model_dump())

        # 2. Расчет latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        # 3. Формирование ответа
        return PredictionResponse(
            prediction=result["prediction"],
            probability=result.get("probability", 0.95),
            class_name=result.get("class_name", "Unknown"),
            request_id=request_id,
            model_version=result.get("model_version", "1.0"),
            latency_ms=round(latency_ms, 2)
        )
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")