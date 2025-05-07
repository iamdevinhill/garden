FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure the start script is executable
RUN chmod +x /app/start.sh

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=5 \
    CMD curl --fail http://localhost:8000/ || exit 1

ENTRYPOINT ["/app/start.sh"] 