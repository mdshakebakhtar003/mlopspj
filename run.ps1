param(
    [Parameter(Position=0)]
    [string]$Action = "help"
)

$VENV_PY = ".\.venv\Scripts\python.exe"
$VENV_PYTEST = ".\.venv\Scripts\pytest.exe"
$VENV_UVICORN = ".\.venv\Scripts\uvicorn.exe"

function Show-Help {
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  Simple MLOps Project Helper Commands" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "Usage: .\run.ps1 <command>`n"
    Write-Host "Available Commands:"
    Write-Host "  train         Train ML model and save 'model.joblib'"
    Write-Host "  test          Run pytest unit tests"
    Write-Host "  serve         Start FastAPI local server (http://localhost:8000)"
    Write-Host "  predict       Send a sample prediction request to the local API"
    Write-Host "  docker-build  Build Docker image: mlops-app:latest"
    Write-Host "  docker-run    Run Docker container on http://localhost:8000"
    Write-Host "  k8s-deploy    Deploy to Kubernetes (2 replicas + service)"
    Write-Host "  k8s-status    Check Kubernetes pods and services"
    Write-Host "  k8s-delete    Remove Kubernetes deployment"
    Write-Host "==========================================================" -ForegroundColor Cyan
}

switch ($Action.ToLower()) {
    "train" {
        Write-Host "🏋️ Training Machine Learning Model..." -ForegroundColor Green
        & $VENV_PY train.py
    }
    "test" {
        Write-Host "🧪 Running Automated Tests..." -ForegroundColor Green
        & $VENV_PYTEST -v test_app.py
    }
    "serve" {
        Write-Host "🚀 Starting FastAPI server on http://localhost:8000 ..." -ForegroundColor Green
        & $VENV_UVICORN app:app --host 0.0.0.0 --port 8000 --reload
    }
    "predict" {
        Write-Host "🔮 Sending sample prediction request..." -ForegroundColor Green
        $body = @{
            sepal_length = 5.1
            sepal_width  = 3.5
            petal_length = 1.4
            petal_width  = 0.2
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"
        Write-Host "`nResponse from Model:" -ForegroundColor Yellow
        $response | Format-List
    }
    "docker-build" {
        Write-Host "🐳 Building Docker image..." -ForegroundColor Green
        docker build -t mlops-app:latest .
    }
    "docker-run" {
        Write-Host "🐳 Running Docker container on port 8000..." -ForegroundColor Green
        docker run --rm -p 8000:8000 --name mlops-container mlops-app:latest
    }
    "k8s-deploy" {
        Write-Host "☸️ Deploying to Kubernetes..." -ForegroundColor Green
        kubectl apply -f k8s/deployment.yaml
    }
    "k8s-status" {
        Write-Host "☸️ Checking Kubernetes status..." -ForegroundColor Green
        kubectl get pods,services
    }
    "k8s-delete" {
        Write-Host "🗑️ Deleting Kubernetes resources..." -ForegroundColor Yellow
        kubectl delete -f k8s/deployment.yaml
    }
    default {
        Show-Help
    }
}
