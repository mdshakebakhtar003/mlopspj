# =============================================================
# Stage 1: Build & Dependencies
# =============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# =============================================================
# Stage 2: Final Minimal Runtime Image
# =============================================================
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    MODEL_PATH=/app/artifacts/model.joblib \
    METRICS_PATH=/app/artifacts/metrics.json \
    PORT=8000

# Copy installed venv from builder
COPY --from=builder /opt/venv /opt/venv

# Create a non-privileged user for security compliance
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser && \
    mkdir -p /app/artifacts /app/data && \
    chown -R appuser:appgroup /app

# Copy application source code and scripts
COPY --chown=appuser:appgroup src/ /app/src/
COPY --chown=appuser:appgroup app/ /app/app/
COPY --chown=appuser:appgroup artifacts/ /app/artifacts/

# Switch to non-root user
USER appuser

# Expose HTTP port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')" || exit 1

# Start FastAPI serving using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
