from unittest.mock import MagicMock

import pytest_asyncio
from app.model import MLModel
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def mock_model():
    model = MagicMock(spec=MLModel)
    model.predict.return_value = [
        {"prediction": 1, "probability": 0.85, "class": "churn"}
    ]
    model.health_check.return_value = {"model_loaded": True}
    app.state.model = model
    yield model


@pytest_asyncio.fixture
async def client(mock_model):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
