import os
import tempfile
import joblib
import pandas as pd

from src.data_pipeline import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET_COL,
    build_preprocessor,
    generate_synthetic_data,
)
from src.train import train_model


def test_synthetic_data_generation():
    df = generate_synthetic_data(num_samples=100)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    expected_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + [TARGET_COL]
    for col in expected_cols:
        assert col in df.columns
    assert set(df[TARGET_COL].unique()).issubset({0, 1})


def test_preprocessor_pipeline():
    df = generate_synthetic_data(num_samples=50)
    features = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = df[features]
    preprocessor = build_preprocessor()
    transformed = preprocessor.fit_transform(X)
    assert transformed.shape[0] == 50
    # Numerical features (8) + OneHot (country 3 + gender 2 = 5) = 13 features
    assert transformed.shape[1] == len(NUMERICAL_FEATURES) + 5


def test_train_pipeline_execution():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_data = os.path.join(tmp_dir, "data.csv")
        tmp_model = os.path.join(tmp_dir, "model.joblib")
        tmp_metrics = os.path.join(tmp_dir, "metrics.json")

        df = generate_synthetic_data(num_samples=200)
        df.to_csv(tmp_data, index=False)

        metrics = train_model(
            data_path=tmp_data,
            model_output_path=tmp_model,
            metrics_output_path=tmp_metrics,
        )

        assert os.path.exists(tmp_model)
        assert os.path.exists(tmp_metrics)
        assert "accuracy" in metrics
        assert "roc_auc" in metrics
        assert metrics["accuracy"] > 0.60
        assert metrics["roc_auc"] > 0.60

        loaded_model = joblib.load(tmp_model)
        test_sample = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].iloc[:2]
        predictions = loaded_model.predict(test_sample)
        assert len(predictions) == 2
