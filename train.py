import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


def train():
    print("=" * 50)
    print("Step 1: Loading Dataset...")
    iris = load_iris()
    X, y = iris.data, iris.target
    print(f"Dataset loaded: {len(X)} samples, 4 features.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Step 2: Training RandomForest Model...")
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"Step 3: Evaluating Model - Test Accuracy: {accuracy * 100:.2f}%")

    joblib.dump(model, "model.joblib")
    print("Step 4: Model successfully saved to 'model.joblib'")
    print("=" * 50)


if __name__ == "__main__":
    train()
