# Multi-stage Docker build for ADK agent
# =============================================================================
# Stage 1: Base
# =============================================================================
FROM python:3.12-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2 AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKER_ENV=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:0.12.2@sha256:069a51314a7bb6031777a9273205fe1b0b19e914ef418207d1338b268df641dd /uv /usr/local/bin/uv

# =============================================================================
# Stage 2: Builder
# =============================================================================
FROM base AS builder

ARG INSTALL_DATADOG=false

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$INSTALL_DATADOG" = "true" ]; then \
        uv sync --frozen --no-dev --no-install-project --extra datadog; \
    else \
        uv sync --frozen --no-dev --no-install-project; \
    fi

# =============================================================================
# Stage 3: Runtime
# =============================================================================
FROM base

WORKDIR /app

# Install runtime utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    procps \
    htop \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user first (before copying files)
RUN useradd -m -u 1000 app

# Copy dependencies from builder with correct ownership
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy application code with correct ownership
COPY --chown=app:app src/ /app/src/
COPY --chown=app:app pyproject.toml uv.lock start_server.sh ./

# Make start script executable
RUN chmod +x start_server.sh

USER app

# Add virtualenv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start server
ENTRYPOINT ["/app/start_server.sh"]
