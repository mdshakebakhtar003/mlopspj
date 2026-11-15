import json
import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib  # noqa: E402
from src.train import train_model  # noqa: E402

MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/model.joblib")
METRICS_PATH = os.getenv("METRICS_PATH", "artifacts/metrics.json")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")

_model = None
_metrics = None


def get_model(force_reload: bool = False):
    """Loads and caches the trained ML pipeline singleton."""
    global _model

    if _model is not None and not force_reload:
        return _model

    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ Model not found at {MODEL_PATH}. Initiating automatic training...")
        train_model(model_output_path=MODEL_PATH, metrics_output_path=METRICS_PATH)

    _model = joblib.load(MODEL_PATH)
    print(f"✅ Successfully loaded model from {MODEL_PATH}")
    return _model


def get_metrics() -> dict:
    """Loads metrics associated with current model."""
    global _metrics
    if _metrics is not None:
        return _metrics

    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r") as f:
                _metrics = json.load(f)
                return _metrics
        except Exception:
            return {"status": "error loading metrics"}
    return {"status": "no metrics file found"}
