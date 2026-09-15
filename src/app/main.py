"""
Application entry point.

This module creates the FastAPI application instance and configures logging.
"""

from app.application import create_app
from app.utils.logger import config_logger

# Configure logging
config_logger()

# Create FastAPI application
app = create_app()
