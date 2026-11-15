FROM python:3.11-slim

WORKDIR /app

# 1. Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy code and model
COPY . .

# 3. Expose port
EXPOSE 8000

# 4. Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
