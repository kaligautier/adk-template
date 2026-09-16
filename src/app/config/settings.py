"""Application configuration using Pydantic BaseSettings."""

import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.error import ConfigurationError

# ADK also reads Google configuration directly from the process environment.
if not os.getenv("DOCKER_ENV"):
    load_dotenv(find_dotenv(".env"))


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Configuration is loaded from:
    1. Environment variables
    2. .env file (in non-Docker environments)
    3. Default values defined below

    All settings are type-safe and validated by Pydantic.
    """

    model_config = SettingsConfigDict(case_sensitive=True)

    # Application metadata
    APP_NAME: str = Field(
        default="ADK Agent Template",
        description="Application name displayed in API documentation",
    )
    APP_DESCRIPTION: str = Field(
        default="ADK agent template with independent services and HTTP integration",
        description="Application description for API documentation",
    )
    APP_VERSION: str = Field(
        default="0.1.0",
        description="Application version",
    )
    PROJECT_NAME: str = Field(
        default="adk-agent-template",
        description="Project identifier used in paths and naming",
    )

    # Server configuration
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host address (0.0.0.0 for all interfaces)",
    )
    PORT: int = Field(
        default=8000,
        description="Server port",
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable the ADK development UI and development endpoints",
    )

    # Logging configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Agent configuration
    AGENT_NAME: str = Field(
        default="template_agent",
        description="Primary agent name",
    )
    MODEL: str = Field(
        default="gemini-2.5-flash",
        description="AI model to use for the agent",
    )

    # Agent directory (computed from project structure)
    @property
    def AGENT_DIR(self) -> str:  # noqa: N802
        """Get the absolute path to the agents directory."""
        return str(Path(__file__).parent.parent / "components" / "agents")

    # Instructions directory (computed from project structure)
    @property
    def INSTRUCTIONS_DIR(self) -> str:  # noqa: N802
        """Get the absolute path to the instructions templates directory."""
        return str(Path(__file__).parent.parent / "instructions" / "templates")

    # Google Cloud Platform configuration (required for Vertex AI)
    GOOGLE_GENAI_USE_VERTEXAI: bool = Field(
        description="Enable Vertex AI for Google Generative AI (required)",
    )
    GOOGLE_CLOUD_PROJECT: str = Field(
        description="GCP project ID (required)",
    )
    GOOGLE_CLOUD_LOCATION: str = Field(
        description="GCP region (e.g., us-central1, europe-west1)",
    )

    # Session management
    USER_ID: str = Field(
        default="api_user",
        description="Default user ID for session management",
    )


# Singleton settings instance with error handling
try:
    settings = Settings()
except ValidationError as e:
    raise ConfigurationError(
        message="Configuration validation failed",
        details={"pydantic_errors": e.errors()},
    ) from e
