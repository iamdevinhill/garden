#!/bin/sh
set -e

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting frontend container..."

# Wait for backend with timeout
max_retries=30
retry_count=0
while ! curl -s -f "$API_URL/plants/" > /dev/null; do
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        log "Backend not available after $max_retries attempts, starting anyway..."
        break
    fi
    log "Waiting for backend to be ready... (Attempt $retry_count/$max_retries)"
    sleep 2
done

log "Starting Streamlit application..."
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0 