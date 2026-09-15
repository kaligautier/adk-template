"""FastAPI application factory."""

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.adk.cli.fast_api import get_fast_api_app

from app.config.settings import settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    # Create FastAPI app with ADK integration
    app: FastAPI = get_fast_api_app(
        agents_dir=settings.AGENT_DIR,
        web=True,  # Enable web UI
    )

    # Set application metadata
    app.title = settings.APP_NAME
    app.description = settings.APP_DESCRIPTION
    app.version = settings.APP_VERSION

    # Add custom health check endpoint
    @app.get("/health", tags=["Health"], summary="Health Check")
    async def health_check():
        """
        Health check endpoint for monitoring systems.

        Returns:
            JSONResponse: A simple JSON response with status "ok"
        """
        return JSONResponse(
            content={
                "status": "ok",
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
            },
            status_code=200,
        )

    logger.info(
        f"FastAPI application created: {settings.APP_NAME} v{settings.APP_VERSION}"
    )
    logger.info(f"Agent directory: {settings.AGENT_DIR}")
    logger.info("Web UI enabled: True")

    return app
