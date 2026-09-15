"""Pytest configuration and shared fixtures for unit tests."""

from unittest.mock import MagicMock

import pytest
from google.adk.tools import ToolContext


@pytest.fixture
def mock_tool_context():
    """Mock ToolContext for testing ADK tools."""
    context = MagicMock(spec=ToolContext)
    context.state = {}
    return context
