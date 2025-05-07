FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Create startup script with better error handling and logging
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
log() {\n\
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1"\n\
}\n\
\n\
log "Starting frontend container..."\n\
\n\
# Wait for backend with timeout\n\
MAX_RETRIES=30\n\
RETRY_COUNT=0\n\
\n\
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do\n\
    if curl -s "${API_URL:-http://backend:8000}" > /dev/null; then\n\
        log "Backend is ready!"\n\
        break\n\
    fi\n\
    RETRY_COUNT=$((RETRY_COUNT + 1))\n\
    log "Waiting for backend... (Attempt $RETRY_COUNT/$MAX_RETRIES)"\n\
    sleep 2\n\
done\n\
\n\
if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then\n\
    log "Warning: Backend not available after $MAX_RETRIES attempts. Starting frontend anyway..."\n\
fi\n\
\n\
log "Starting Streamlit application..."\n\
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Add healthcheck with more lenient settings
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["/app/start.sh"] 