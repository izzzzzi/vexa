FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy shared models
COPY ../libs/shared-models /app/shared-models
RUN pip install -e /app/shared-models

# Set environment variables
ENV PYTHONPATH=/app

# Run the bot
CMD ["python", "main.py"] 