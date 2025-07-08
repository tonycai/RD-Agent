#!/bin/bash
set -e

# RD-Agent Docker Entrypoint Script
echo "Starting RD-Agent..."

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "Waiting for $service_name to be available at $host:$port..."
    
    while ! nc -z "$host" "$port"; do
        echo "Waiting for $service_name..."
        sleep 2
    done
    
    echo "$service_name is available!"
}

# Function to setup directories
setup_directories() {
    echo "Setting up directories..."
    
    # Create data directories
    mkdir -p /app/data
    mkdir -p /app/log
    mkdir -p /app/cache
    
    # Set permissions
    chown -R appuser:appuser /app/data /app/log /app/cache || true
    
    echo "Directories setup complete."
}

# Function to validate environment
validate_environment() {
    echo "Validating environment..."
    
    # Check required environment variables based on mode
    if [ "$RD_AGENT_AUTH_ENABLED" = "true" ]; then
        if [ -z "$RD_AGENT_API_KEY" ]; then
            echo "ERROR: RD_AGENT_API_KEY is required when authentication is enabled"
            exit 1
        fi
    fi
    
    # Check LLM configuration
    if [ -z "$OPENAI_API_KEY" ] && [ -z "$DEEPSEEK_API_KEY" ]; then
        echo "WARNING: No LLM API keys configured. Some features may not work."
    fi
    
    echo "Environment validation complete."
}

# Function to perform health check
health_check() {
    echo "Performing health check..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            echo "Health check passed!"
            return 0
        fi
        
        echo "Health check attempt $attempt/$max_attempts failed, retrying..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "Health check failed after $max_attempts attempts"
    return 1
}

# Function to run migrations (if needed)
run_migrations() {
    echo "Running migrations..."
    
    # Add any database migrations here
    # python -m rdagent.db.migrate
    
    echo "Migrations complete."
}

# Main execution
main() {
    echo "RD-Agent Entrypoint - Mode: ${RD_AGENT_MODE:-gateway}"
    
    # Setup
    setup_directories
    validate_environment
    
    # Wait for dependencies if specified
    if [ -n "$WAIT_FOR_REDIS" ]; then
        wait_for_service redis 6379 "Redis"
    fi
    
    if [ -n "$WAIT_FOR_POSTGRES" ]; then
        wait_for_service postgres 5432 "PostgreSQL"
    fi
    
    # Run migrations if in production
    if [ "$NODE_ENV" = "production" ]; then
        run_migrations
    fi
    
    # Determine command based on mode
    case "${RD_AGENT_MODE:-gateway}" in
        "gateway")
            echo "Starting RD-Agent Gateway..."
            exec uvicorn rdagent.app.gateway.main_new:app \
                --host 0.0.0.0 \
                --port "${RD_AGENT_PORT:-8000}" \
                --workers "${WORKERS:-1}" \
                "$@"
            ;;
        "ui")
            echo "Starting RD-Agent UI..."
            exec python -m rdagent.app.cli ui \
                --port "${UI_PORT:-19899}" \
                --host "0.0.0.0" \
                --log_dir "/app/log" \
                "$@"
            ;;
        "worker")
            echo "Starting RD-Agent Worker..."
            exec python -m rdagent.worker \
                "$@"
            ;;
        "cli")
            echo "Running RD-Agent CLI..."
            exec python -m rdagent.app.cli "$@"
            ;;
        *)
            echo "Unknown mode: ${RD_AGENT_MODE}"
            echo "Available modes: gateway, ui, worker, cli"
            exit 1
            ;;
    esac
}

# Signal handlers for graceful shutdown
shutdown() {
    echo "Received shutdown signal, gracefully stopping..."
    
    # Kill child processes
    jobs -p | xargs -r kill
    
    # Wait for processes to stop
    wait
    
    echo "Shutdown complete."
    exit 0
}

# Trap signals
trap shutdown SIGTERM SIGINT

# Execute main function with all arguments
main "$@"