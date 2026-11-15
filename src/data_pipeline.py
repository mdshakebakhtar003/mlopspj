import os
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

NUMERICAL_FEATURES = [
    "credit_score",
    "age",
    "tenure",
    "balance",
    "num_of_products",
    "has_cr_card",
    "is_active_member",
    "estimated_salary",
]

CATEGORICAL_FEATURES = ["country", "gender"]

TARGET_COL = "churn"


def generate_synthetic_data(num_samples: int = 2000, random_seed: int = 42) -> pd.DataFrame:
    """Generates synthetic bank customer data for churn prediction."""
    np.random.seed(random_seed)

    credit_score = np.random.normal(650, 80, num_samples).clip(350, 850).astype(int)
    country = np.random.choice(["France", "Germany", "Spain"], size=num_samples, p=[0.5, 0.25, 0.25])
    gender = np.random.choice(["Female", "Male"], size=num_samples, p=[0.45, 0.55])
    age = np.random.normal(38, 10, num_samples).clip(18, 80).astype(int)
    tenure = np.random.randint(0, 11, num_samples)
    balance = np.where(np.random.rand(num_samples) > 0.3, np.random.uniform(10000, 200000, num_samples), 0.0)
    num_of_products = np.random.choice([1, 2, 3, 4], size=num_samples, p=[0.5, 0.45, 0.04, 0.01])
    has_cr_card = np.random.choice([0, 1], size=num_samples, p=[0.3, 0.7])
    is_active_member = np.random.choice([0, 1], size=num_samples, p=[0.48, 0.52])
    estimated_salary = np.random.uniform(15000, 180000, num_samples).round(2)

    # Churn probability based on realistic risk factors
    logits = (
        (age - 40) * 0.06
        + (country == "Germany") * 0.7
        + (gender == "Female") * 0.4
        - (is_active_member * 0.9)
        + (num_of_products >= 3) * 1.5
        + (balance > 100000) * 0.3
        - 1.8
    )
    prob = 1 / (1 + np.exp(-logits))
    churn = (np.random.rand(num_samples) < prob).astype(int)

    df = pd.DataFrame(
        {
            "credit_score": credit_score,
            "country": country,
            "gender": gender,
            "age": age,
            "tenure": tenure,
            "balance": balance.round(2),
            "num_of_products": num_of_products,
            "has_cr_card": has_cr_card,
            "is_active_member": is_active_member,
            "estimated_salary": estimated_salary,
            "churn": churn,
        }
    )
    return df


def build_preprocessor() -> ColumnTransformer:
    """Builds a scikit-learn ColumnTransformer for numerical and categorical features."""
    numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])

    categorical_transformer = Pipeline(
        steps=[("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )
    return preprocessor


def get_data(data_path: str = "data/customer_churn.csv") -> pd.DataFrame:
    """Loads existing dataset or creates a synthetic one if not found."""
    if os.path.exists(data_path):
        return pd.read_csv(data_path)

    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    df = generate_synthetic_data()
    df.to_csv(data_path, index=False)
    return df
