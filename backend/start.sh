#!/bin/sh
set -e

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check Neo4j authentication
check_neo4j_auth() {
    log "Testing Neo4j authentication..."
    curl -s -u "$NEO4J_USER:$NEO4J_PASSWORD" http://neo4j:7474/db/data/ > /dev/null 2>&1
    return $?
}

# Wait for Ollama to be ready
log "Waiting for Ollama to be ready..."
while ! curl -s -f http://ollama:11434/ > /dev/null 2>&1; do
    log "Waiting for Ollama server to be ready..."
    sleep 2
done
log "Ollama is ready!"

# Wait for Neo4j to be ready
log "Waiting for Neo4j to be ready..."
while ! curl -s -f http://neo4j:7474/ > /dev/null 2>&1; do
    log "Waiting for Neo4j server to be ready..."
    sleep 2
done

# Additional wait to ensure Neo4j is fully initialized
log "Waiting for Neo4j to be fully initialized..."
sleep 10

# Verify Neo4j authentication
max_retries=5
retry_count=0
while ! check_neo4j_auth; do
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        log "Failed to authenticate with Neo4j after $max_retries attempts"
        exit 1
    fi
    log "Neo4j authentication failed, retrying in 5 seconds... (Attempt $retry_count/$max_retries)"
    sleep 5
done
log "Neo4j authentication successful!"

# Start the FastAPI application without reload for stability
log "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 