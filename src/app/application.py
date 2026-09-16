"""FastAPI application factory."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.adk.cli.fast_api import get_fast_api_app

from app.config.settings import settings
from app.utils.error import AppError

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    # Create FastAPI app with ADK integration
    app: FastAPI = get_fast_api_app(
        agents_dir=settings.AGENT_DIR,
        web=settings.DEBUG,
    )

    # Set application metadata
    app.title = settings.APP_NAME
    app.description = settings.APP_DESCRIPTION
    app.version = settings.APP_VERSION

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, error: AppError):
        logger.warning("Application error: %s", error.error_code.name)
        return JSONResponse(
            content=error.to_dict(),
            status_code=error.status_code,
        )

    logger.info(
        f"FastAPI application created: {settings.APP_NAME} v{settings.APP_VERSION}"
    )
    logger.info(f"Agent directory: {settings.AGENT_DIR}")
    logger.info("Development UI enabled: %s", settings.DEBUG)

    return app
