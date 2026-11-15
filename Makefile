.PHONY: setup train test lint serve docker-build docker-run compose-up compose-down k8s-apply k8s-status k8s-delete clean

PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest
UVICORN := .venv/bin/uvicorn
FLAKE8 := .venv/bin/flake8

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

train:
	$(PYTHON) -m src.train

test:
	$(PYTEST) -v tests/

lint:
	$(FLAKE8) . --count --select=E9,F63,F7,F82 --show-source --statistics

serve:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t mlops-churn-api:latest .

docker-run:
	docker run --rm -p 8000:8000 --name mlops-churn-app mlops-churn-api:latest

compose-up:
	docker-compose up --build -d

compose-down:
	docker-compose down

k8s-apply:
	kubectl apply -k k8s/

k8s-status:
	kubectl get all,hpa -n mlops-prod

k8s-delete:
	kubectl delete -k k8s/

clean:
	rm -rf .pytest_cache .coverage htmlcov __pycache__ src/__pycache__ app/__pycache__ tests/__pycache__
