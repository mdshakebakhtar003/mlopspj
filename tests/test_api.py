from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data


def test_health_live():
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_health_ready():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["model_loaded"] is True


def test_single_prediction_valid():
    payload = {
        "credit_score": 650,
        "country": "Germany",
        "gender": "Female",
        "age": 42,
        "tenure": 5,
        "balance": 85000.5,
        "num_of_products": 2,
        "has_cr_card": 1,
        "is_active_member": 1,
        "estimated_salary": 65000.0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "churn_prediction" in data
    assert data["churn_prediction"] in [0, 1]
    assert 0.0 <= data["churn_probability"] <= 1.0
    assert data["risk_level"] in ["Low", "Medium", "High"]


def test_single_prediction_invalid():
    # Invalid credit score out of range
    invalid_payload = {
        "credit_score": 100,  # Below minimum 300
        "country": "Mars",   # Invalid country
        "gender": "Female",
        "age": 10,           # Under minimum 18
        "tenure": 5,
        "balance": 85000.5,
        "num_of_products": 2,
        "has_cr_card": 1,
        "is_active_member": 1,
        "estimated_salary": 65000.0,
    }
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422


def test_batch_prediction():
    payload = {
        "customers": [
            {
                "credit_score": 700,
                "country": "France",
                "gender": "Male",
                "age": 30,
                "tenure": 3,
                "balance": 50000.0,
                "num_of_products": 1,
                "has_cr_card": 1,
                "is_active_member": 1,
                "estimated_salary": 45000.0,
            },
            {
                "credit_score": 580,
                "country": "Spain",
                "gender": "Female",
                "age": 55,
                "tenure": 8,
                "balance": 120000.0,
                "num_of_products": 3,
                "has_cr_card": 0,
                "is_active_member": 0,
                "estimated_salary": 90000.0,
            },
        ]
    }
    response = client.post("/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] == 2
    assert len(data["predictions"]) == 2


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "api_requests_total" in response.text or "process_cpu_seconds_total" in response.text


def test_model_info_endpoint():
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert "metrics" in data
