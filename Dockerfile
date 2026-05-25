FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for browser-based fetcher
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: start the API server
CMD ["python3", "src/api.py"]