"""Unit tests for before_agent callback."""

import logging
from unittest.mock import MagicMock

import pytest
from google.adk.agents.callback_context import CallbackContext

from app.components.callbacks.before_agent import log_agent_start


class TestLogAgentStart:
    """Tests for log_agent_start callback function."""

    def should_be_callable(self):
        """Test function exists and is callable."""
        assert callable(log_agent_start)

    def should_accept_callback_context_parameter(self):
        """Test function accepts CallbackContext parameter."""
        context = MagicMock(spec=CallbackContext)
        context.agent_name = "test_agent"

        # Should not raise
        log_agent_start(context)

    def should_access_agent_name_from_context(self):
        """Test function accesses agent_name from context."""
        context = MagicMock(spec=CallbackContext)
        context.agent_name = "my_agent"

        # Should not raise
        log_agent_start(context)

        # Verify agent_name was accessed
        assert context.agent_name == "my_agent"

    def should_log_info_message(self, caplog):
        """Test function logs info message."""
        context = MagicMock(spec=CallbackContext)
        context.agent_name = "test_agent"

        with caplog.at_level(logging.INFO):
            log_agent_start(context)

        # Verify log message contains expected content
        assert any("test_agent" in record.message for record in caplog.records)
        assert any("starting" in record.message.lower() for record in caplog.records)

    def should_log_at_info_level(self, caplog):
        """Test function logs at INFO level."""
        context = MagicMock(spec=CallbackContext)
        context.agent_name = "test_agent"

        with caplog.at_level(logging.INFO):
            log_agent_start(context)

        # Verify at least one INFO log was created
        assert any(record.levelname == "INFO" for record in caplog.records)

    def should_include_agent_name_in_log(self, caplog):
        """Test log message includes the agent name."""
        context = MagicMock(spec=CallbackContext)
        context.agent_name = "custom_agent_name"

        with caplog.at_level(logging.INFO):
            log_agent_start(context)

        # Verify agent name is in log message
        log_messages = " ".join(record.message for record in caplog.records)
        assert "custom_agent_name" in log_messages

    def should_not_raise_exception(self):
        """Test function completes without exception."""
        context = MagicMock(spec=CallbackContext)
        context.agent_name = "test_agent"

        try:
            log_agent_start(context)
        except Exception as e:
            pytest.fail(f"log_agent_start raised exception: {e}")

    def should_return_none(self):
        """Test function returns None."""
        context = MagicMock(spec=CallbackContext)
        context.agent_name = "test_agent"

        result = log_agent_start(context)

        assert result is None
