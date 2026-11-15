import os
import joblib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Simple MLOps Iris Prediction API",
    description="A minimal API to serve a machine learning model",
    version="1.0.0"
)

MODEL_FILE = "model.joblib"
TARGET_NAMES = ["setosa", "versicolor", "virginica"]

model = None
if os.path.exists(MODEL_FILE):
    model = joblib.load(MODEL_FILE)


class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


@app.get("/")
def home():
    return {
        "message": "Welcome to Simple MLOps API",
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


@app.post("/predict")
def predict(data: IrisInput):
    global model
    if model is None:
        model = joblib.load(MODEL_FILE)

    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]]

    prediction = int(model.predict(features)[0])
    species = TARGET_NAMES[prediction]

    return {
        "prediction": prediction,
        "species": species
    }
