import os
from fastapi.testclient import TestClient
from app import app
from train import train

client = TestClient(app)


def test_train_creates_model():
    train()
    assert os.path.exists("model.joblib")


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_predict_endpoint():
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "species" in data
    assert data["species"] == "setosa"
