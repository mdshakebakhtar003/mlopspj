# 🎯 Simple MLOps Project: End-to-End Pipeline

## 💡 Overview

This project illustrates the complete lifecycle of putting a Machine Learning model into production:

| MLOps Pillar | File | Description |
| :--- | :--- | :--- |
| **1. Model Training** | [`train.py`](train.py) | Trains a classification model on the Iris dataset and exports `model.joblib`. |
| **2. API Serving** | [`app.py`](app.py) | Serves the model via a FastAPI REST API (`/health` and `/predict`). |
| **3. Automated Testing** | [`test_app.py`](test_app.py) | Verifies the model training output and API endpoints using `pytest`. |
| **4. Containerization** | [`Dockerfile`](Dockerfile) | Packages the code, dependencies, and model into a Docker image. |
| **5. Orchestration** | [`k8s/deployment.yaml`](k8s/deployment.yaml) | Deploys 2 replicated pods with a Kubernetes Service for load balancing. |
| **6. CI/CD Automation** | [`.github/workflows/cicd.yaml`](.github/workflows/cicd.yaml) | Automatically runs tests and builds the Docker image on every GitHub push. |

---

## 📂 Project Structure

```text
mlopsnew/
├── .github/workflows/
│   └── cicd.yaml        # GitHub Actions CI/CD workflow
├── k8s/
│   └── deployment.yaml  # Kubernetes Deployment (2 replicas) + Service
├── app.py               # FastAPI application (/health and /predict)
├── train.py             # Trains model & exports model.joblib
├── test_app.py          # Pytest automated test suite
├── Dockerfile           # Minimal Dockerfile
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## 🚀 How to Run the Project (Direct Commands)
## Activate venv first
[.\.venv\Scripts\Activate.ps1]

### 1. Train the Machine Learning Model
```bash
python train.py
```

### 2. Run Automated Tests
```bash
pytest -v test_app.py
```

### 3. Start the REST API
```bash
uvicorn app:app --reload --port 8000
```
* **Interactive UI (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Send a Prediction Request
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -ContentType "application/json" -Body '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

### 5. Build & Run with Docker
```bash
docker build -t mlops-app:latest .
docker run -p 8000:8000 mlops-app:latest
```

### 6. Deploy to Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods,svc
kubectl delete -f k8s/deployment.yaml
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions workflow in `.github/workflows/cicd.yaml` automatically executes on every push:
1. Checks out repository
2. Sets up Python 3.11
3. Installs requirements
4. Runs `python train.py`
5. Executes `pytest -v test_app.py`
6. Builds Docker container `mlops-app:latest`
