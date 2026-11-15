import json
import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402

from src.data_pipeline import (  # noqa: E402
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET_COL,
    build_preprocessor,
    get_data,
)


def train_model(
    data_path: str = "data/customer_churn.csv",
    model_output_path: str = "artifacts/model.joblib",
    metrics_output_path: str = "artifacts/metrics.json",
    test_size: float = 0.2,
    random_state: int = 42,
):
    print("=" * 60)
    print("🚀 Starting MLOps Training Pipeline")
    print("=" * 60)

    # 1. Load Data
    df = get_data(data_path)
    print(f"📊 Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = df[feature_cols]
    y = df[TARGET_COL]

    # 2. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"✂️  Train set: {X_train.shape[0]} samples | Test set: {X_test.shape[0]} samples")

    # 3. Create End-to-End Pipeline
    preprocessor = build_preprocessor()
    classifier = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=random_state, class_weight="balanced"
    )

    full_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    # 4. Train
    print("🏋️  Training Random Forest model...")
    full_pipeline.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = full_pipeline.predict(X_test)
    y_proba = full_pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "train_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
    }

    print("\n📈 Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"   - {k}: {v}")

    # 6. Save Artifacts
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(full_pipeline, model_output_path)
    print(f"💾 Model saved to: {model_output_path}")

    with open(metrics_output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"💾 Metrics saved to: {metrics_output_path}")

    # Save a sample input dictionary for testing
    sample_input = X_test.iloc[0].to_dict()
    clean_sample = {}
    for k, v in sample_input.items():
        if isinstance(v, (int, pd.Int64Dtype)):
            clean_sample[k] = int(v)
        elif isinstance(v, (float, pd.Float64Dtype)):
            clean_sample[k] = float(v)
        else:
            clean_sample[k] = str(v)

    sample_path = os.path.join(os.path.dirname(model_output_path), "sample_input.json")
    with open(sample_path, "w") as f:
        json.dump(clean_sample, f, indent=2)
    print(f"💾 Sample input saved to: {sample_path}")

    print("=" * 60)
    print("✅ Training Pipeline completed successfully!")
    print("=" * 60)
    return metrics


if __name__ == "__main__":
    train_model()
