#!/bin/bash

# Production server startup script for ADK agent
# Supports both production (Gunicorn) and development (Uvicorn) modes

set -euo pipefail

# Configuration
APP_MODULE="app.main:app"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_CONFIG="logging.conf"

# Change to src directory (where app module is located)
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/src"

# Determine mode: production or development
if [ "${1:-}" = "local" ]; then
    export DEBUG=true
    echo "Starting in DEVELOPMENT mode..."
    echo "Using Uvicorn with auto-reload"

    exec uvicorn "${APP_MODULE}" \
        --host "${HOST}" \
        --port "${PORT}" \
        --log-config "${LOG_CONFIG}" \
        --reload
else
    export DEBUG=false
    echo "Starting in PRODUCTION mode..."
    echo "Using Gunicorn with Uvicorn workers"

    server_command=(
        gunicorn "${APP_MODULE}"
        --bind "${HOST}:${PORT}"
        --worker-class uvicorn.workers.UvicornWorker
        --workers 1
        --timeout 600
        --access-logfile -
        --log-config "${LOG_CONFIG}"
    )
    if [ "${DD_TRACE_ENABLED:-false}" = "true" ]; then
        if ! command -v ddtrace-run &> /dev/null; then
            echo "Datadog requested: install the datadog extra or build with INSTALL_DATADOG=true." >&2
            exit 1
        fi
        server_command=(ddtrace-run "${server_command[@]}")
    fi

    exec "${server_command[@]}"
fi
