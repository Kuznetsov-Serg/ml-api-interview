# app/schemas/predictions.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    age: int = Field(ge=0, le=150, description="Возраст клиента")
    income: float = Field(ge=0, description="Годовой доход")
    has_loan: bool = Field(default=False, description="Есть ли кредит")
    transaction_count: Optional[int] = Field(ge=0, default=0)

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 18:
            raise ValueError('Возраст должен быть >= 18')
        return v

class PredictionResponse(BaseModel):
    prediction: int
    probability: float = Field(ge=0, le=1)
    class_name: str
    request_id: str
    model_version: str
    latency_ms: float

class BatchPredictionRequest(BaseModel):
    items: list[PredictionRequest] = Field(max_length=100)

class HealthResponse(BaseModel):
    status: str
    model: dict
    timestamp: datetime
    version: str

class ErrorResponse(BaseModel):
    type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None