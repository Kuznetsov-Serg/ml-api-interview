import pytest


@pytest.mark.asyncio
async def test_predict_success(client):
    response = await client.post(
        "/predict", json={"age": 30, "income": 50000.0, "has_loan": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert 0 <= data["probability"] <= 1


@pytest.mark.asyncio
async def test_predict_validation_error(client):
    response = await client.post(
        "/predict", json={"age": -5, "income": 50000.0}  # невалидно
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_batch(client):
    response = await client.post(
        "/predict/batch",
        json={"items": [{"age": 25, "income": 30000}, {"age": 35, "income": 60000}]},
    )
    assert response.status_code == 200
    assert len(response.json()["predictions"]) == 2


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data
