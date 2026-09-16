#!/usr/bin/env -S just --justfile
# ADK Agent Template

# Load environment variables from .env file
set dotenv-load

# Internal helper to check UV is available
_check-uv:
    #!/usr/bin/env bash
    if ! command -v uv &> /dev/null; then
        echo "ERROR: UV is required but not installed."
        echo "Please install UV from: https://docs.astral.sh/uv/"
        exit 1
    fi

# Install dependencies using UV
[group('setup')]
install: _check-uv
    echo "Installing dependencies with UV..."
    cd {{ source_directory() }} && uv sync

# Launch agent as API server
[group('run')]
api: _check-uv
    cd {{ source_directory() }}/src && DEBUG=true uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Format code with ruff
[group('quality')]
format: _check-uv
    cd {{ source_directory() }} && uv run ruff format src/

[group('quality')]
sort-imports: _check-uv
    cd {{ source_directory() }} && uv run ruff check --select I --fix src/

# Lint code with ruff
[group('quality')]
lint: _check-uv
    cd {{ source_directory() }} && uv run ruff check src/

# Run full test suite with coverage
[group('quality')]
test: _check-uv
    cd {{ source_directory() }}/src && PYTHONDONTWRITEBYTECODE=1 uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=83

# Run all quality checks (format + lint + test) - required before commit
[group('quality')]
pre-commit: format lint test

# Build Docker image
[group('docker')]
build:
    cd {{ source_directory() }} && docker build --no-cache -t adk-agent-template:latest .

# Run Docker with the environment already resolved by Just's dotenv loader
[group('docker')]
run:
    cd {{ source_directory() }} && docker run --rm -p 127.0.0.1:8000:8000 \
        -e GOOGLE_GENAI_USE_VERTEXAI \
        -e GOOGLE_CLOUD_PROJECT \
        -e GOOGLE_CLOUD_LOCATION \
        -e APP_NAME -e APP_DESCRIPTION -e APP_VERSION -e PROJECT_NAME \
        -e HOST -e PORT -e DEBUG -e LOG_LEVEL \
        -e AGENT_NAME -e MODEL -e USER_ID \
        -e DD_TRACE_ENABLED \
        -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/adc.json \
        --mount "type=bind,source=${CLOUDSDK_CONFIG:-${HOME}/.config/gcloud}/application_default_credentials.json,target=/tmp/adc.json,readonly" \
        adk-agent-template:latest local
