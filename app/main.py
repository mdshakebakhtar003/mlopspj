import os
import time
from contextlib import asynccontextmanager
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.model_loader import MODEL_VERSION, get_metrics, get_model
from app.schemas import (
    BatchCustomerFeatures,
    BatchPredictionResponse,
    CustomerFeatures,
    HealthResponse,
    PredictionResponse,
)

# -------------------------------------------------------------
# Prometheus Metrics Definition
# -------------------------------------------------------------
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total count of requests to endpoints",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "Request latency in seconds",
    ["endpoint"],
)

PREDICTION_COUNT = Counter(
    "model_churn_predictions_total",
    "Churn prediction distribution",
    ["prediction_label"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: preload the model
    print("⏳ Initializing model during application startup...")
    get_model()
    print("🚀 Model successfully loaded and ready for predictions.")
    yield
    print("🛑 Application shutdown.")


app = FastAPI(
    title="Customer Churn Prediction MLOps API",
    description="Production-grade MLOps Serving API with Docker, Kubernetes probes, and Prometheus Metrics",
    version=MODEL_VERSION,
    lifespan=lifespan,
)


@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path
    status_code = str(response.status_code)

    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

    return response


# -------------------------------------------------------------
# Core & Health Endpoints (Kubernetes Probes)
# -------------------------------------------------------------
@app.get("/", tags=["General"])
def root():
    return {
        "service": "MLOps Customer Churn Predictor",
        "version": MODEL_VERSION,
        "docs_url": "/docs",
        "metrics_url": "/metrics",
        "health_check": "/health/ready",
    }


@app.get("/health/live", response_model=HealthResponse, tags=["Health"])
def liveness_probe():
    """Kubernetes liveness probe: checks if process is alive."""
    return HealthResponse(
        status="healthy",
        model_loaded=True,
        version=MODEL_VERSION,
        environment=os.getenv("ENVIRONMENT", "production"),
    )


@app.get("/health/ready", response_model=HealthResponse, tags=["Health"])
def readiness_probe():
    """Kubernetes readiness probe: verifies model is loaded in memory."""
    try:
        model = get_model()
        if model is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not loaded")
        return HealthResponse(
            status="ready",
            model_loaded=True,
            version=MODEL_VERSION,
            environment=os.getenv("ENVIRONMENT", "production"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Readiness check failed: {str(exc)}",
        )


@app.get("/metrics", tags=["Monitoring"])
def metrics_endpoint():
    """Prometheus metrics endpoint for cluster scraping."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/model/info", tags=["Model"])
def model_info():
    """Retrieves metadata and evaluation metrics of the active model."""
    metrics = get_metrics()
    return {
        "model_version": MODEL_VERSION,
        "model_algorithm": "RandomForestClassifier",
        "metrics": metrics,
    }


# -------------------------------------------------------------
# Prediction Endpoints
# -------------------------------------------------------------
def _classify_risk(prob: float) -> str:
    if prob >= 0.7:
        return "High"
    elif prob >= 0.35:
        return "Medium"
    return "Low"


@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
def predict(features: CustomerFeatures):
    """Predict churn for a single customer."""
    model = get_model()
    input_df = pd.DataFrame([features.model_dump()])

    try:
        proba = float(model.predict_proba(input_df)[0][1])
        prediction = int(proba >= 0.5)
        risk = _classify_risk(proba)

        PREDICTION_COUNT.labels(prediction_label="Churn" if prediction == 1 else "Retain").inc()

        return PredictionResponse(
            churn_prediction=prediction,
            churn_probability=round(proba, 4),
            risk_level=risk,
            model_version=MODEL_VERSION,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(exc)}",
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Inference"])
def predict_batch(batch: BatchCustomerFeatures):
    """Batch prediction endpoint for high-throughput scoring."""
    if not batch.customers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No customer records provided")

    model = get_model()
    records = [c.model_dump() for c in batch.customers]
    input_df = pd.DataFrame(records)

    try:
        probabilities = model.predict_proba(input_df)[:, 1]
        results = []

        for p in probabilities:
            prob = float(p)
            pred = int(prob >= 0.5)
            PREDICTION_COUNT.labels(prediction_label="Churn" if pred == 1 else "Retain").inc()
            results.append(
                PredictionResponse(
                    churn_prediction=pred,
                    churn_probability=round(prob, 4),
                    risk_level=_classify_risk(prob),
                    model_version=MODEL_VERSION,
                )
            )

        return BatchPredictionResponse(
            predictions=results,
            total_processed=len(results),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch inference error: {str(exc)}",
        )
