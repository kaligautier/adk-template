"""
Logging configuration with custom filter for module-qualified function names.

This module provides:
- Custom logging filter for enhanced log formatting
- Module-qualified function names in logs
- Configurable log level from settings
"""

import logging

from app.config.settings import settings


class AppLoggingFilter(logging.Filter):
    """
    Custom logging filter that enhances log records.

    Adds:
    - expandedFuncName: module.function format
    - Formatted levelname with colon suffix
    """

    def filter(self, record):
        """Enhance log record with custom attributes."""
        # Create module-qualified function name
        record.expandedFuncName = f"{record.module}.{record.funcName}"

        # Add colon to level name for visual clarity
        record.levelname = f"{record.levelname}:"

        return True


def config_logger():
    """
    Configure application logging.

    Sets up:
    - StreamHandler for console output
    - AppLoggingFilter for enhanced formatting
    - Custom format with module-qualified function names
    - Log level from settings
    """
    # Create handler
    handler = logging.StreamHandler()

    # Add custom filter
    handler.addFilter(AppLoggingFilter())

    # Set format
    formatter = logging.Formatter("%(levelname)-9s %(expandedFuncName)s: %(message)s")
    handler.setFormatter(formatter)

    # Configure root logger
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        handlers=[handler],
        force=True,  # Override any existing configuration
    )

    # Log configuration complete
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={settings.LOG_LEVEL}, app={settings.APP_NAME}"
    )
