param(
    [Parameter(Position=0)]
    [string]$Action = "help"
)

$VENV_PY = ".\.venv\Scripts\python.exe"
$VENV_PIP = ".\.venv\Scripts\pip.exe"
$VENV_UVICORN = ".\.venv\Scripts\uvicorn.exe"
$VENV_PYTEST = ".\.venv\Scripts\pytest.exe"

function Show-Help {
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  MLOps Customer Churn Project CLI (PowerShell)" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "Usage: .\run.ps1 <command>`n"
    Write-Host "Commands:"
    Write-Host "  setup             Create .venv and install all dependencies"
    Write-Host "  train             Train model and export artifacts"
    Write-Host "  test              Run full test suite (pytest)"
    Write-Host "  serve             Start FastAPI development server (port 8000)"
    Write-Host "  predict-sample    Send a test prediction request via curl/Invoke-RestMethod"
    Write-Host "  docker-build      Build the Docker image (mlops-churn-api:latest)"
    Write-Host "  docker-run        Run the Docker container locally on port 8000"
    Write-Host "  compose-up        Launch API + Prometheus via Docker Compose"
    Write-Host "  compose-down      Stop and clean up Docker Compose services"
    Write-Host "  k8s-apply         Apply all Kubernetes manifests (mlops-prod namespace)"
    Write-Host "  k8s-status        Check status of pods, services, and HPA in k8s"
    Write-Host "  k8s-delete        Delete Kubernetes resources"
    Write-Host "==========================================================" -ForegroundColor Cyan
}

switch ($Action.ToLower()) {
    "setup" {
        Write-Host "📦 Setting up virtual environment..." -ForegroundColor Green
        if (-not (Test-Path ".venv")) {
            python -m venv .venv
        }
        & $VENV_PIP install --upgrade pip
        & $VENV_PIP install -r requirements.txt
        Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
    }
    "train" {
        Write-Host "🏋️ Running Model Training Pipeline..." -ForegroundColor Green
        & $VENV_PY -m src.train
    }
    "test" {
        Write-Host "🧪 Running Automated Tests..." -ForegroundColor Green
        & $VENV_PYTEST -v tests/
    }
    "serve" {
        Write-Host "🚀 Starting FastAPI server on http://localhost:8000 ..." -ForegroundColor Green
        & $VENV_UVICORN app.main:app --host 0.0.0.0 --port 8000 --reload
    }
    "predict-sample" {
        Write-Host "🔮 Sending sample prediction request..." -ForegroundColor Green
        $body = @{
            credit_score = 650
            country = "Germany"
            gender = "Female"
            age = 42
            tenure = 5
            balance = 85000.50
            num_of_products = 2
            has_cr_card = 1
            is_active_member = 1
            estimated_salary = 65000.0
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"
        $response | Format-List
    }
    "docker-build" {
        Write-Host "🐳 Building Docker image: mlops-churn-api:latest ..." -ForegroundColor Green
        docker build -t mlops-churn-api:latest .
    }
    "docker-run" {
        Write-Host "🐳 Running Docker container on http://localhost:8000 ..." -ForegroundColor Green
        docker run --rm -p 8000:8000 --name mlops-churn-app mlops-churn-api:latest
    }
    "compose-up" {
        Write-Host "🚀 Launching stack with Docker Compose..." -ForegroundColor Green
        docker-compose up --build -d
        Write-Host "Services started:"
        Write-Host "  - API:        http://localhost:8000 (Swagger: http://localhost:8000/docs)"
        Write-Host "  - Prometheus: http://localhost:9090"
    }
    "compose-down" {
        Write-Host "🛑 Stopping Docker Compose stack..." -ForegroundColor Green
        docker-compose down
    }
    "k8s-apply" {
        Write-Host "☸️ Applying Kubernetes manifests..." -ForegroundColor Green
        kubectl apply -k k8s/
    }
    "k8s-status" {
        Write-Host "☸️ Checking Kubernetes cluster resources..." -ForegroundColor Green
        kubectl get all,hpa -n mlops-prod
    }
    "k8s-delete" {
        Write-Host "🗑️ Deleting Kubernetes resources..." -ForegroundColor Yellow
        kubectl delete -k k8s/
    }
    default {
        Show-Help
    }
}
