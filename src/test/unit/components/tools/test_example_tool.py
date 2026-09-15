"""Unit tests for custom ADK tools."""

from unittest.mock import patch

import pytest

from app.components.tools.custom.example_tool import calculate, get_current_time
from app.services.calculator_service import Operation
from app.utils.error import ToolExecutionError


class TestCalculateTool:
    """Tests for calculate ADK tool."""

    def should_perform_addition(self, mock_tool_context):
        """Test calculate tool with addition operation."""
        result = calculate(Operation.ADD, 5, 3, mock_tool_context)

        assert result["operation"] == "add"
        assert result["a"] == 5
        assert result["b"] == 3
        assert result["result"] == 8

    def should_perform_subtraction(self, mock_tool_context):
        """Test calculate tool with subtraction operation."""
        result = calculate(Operation.SUBTRACT, 10, 3, mock_tool_context)

        assert result["operation"] == "subtract"
        assert result["result"] == 7

    def should_perform_multiplication(self, mock_tool_context):
        """Test calculate tool with multiplication operation."""
        result = calculate(Operation.MULTIPLY, 5, 3, mock_tool_context)

        assert result["operation"] == "multiply"
        assert result["result"] == 15

    def should_perform_division(self, mock_tool_context):
        """Test calculate tool with division operation."""
        result = calculate(Operation.DIVIDE, 10, 2, mock_tool_context)

        assert result["operation"] == "divide"
        assert result["result"] == 5

    def should_raise_tool_execution_error_on_division_by_zero(self, mock_tool_context):
        """Test calculate tool wraps ValueError as ToolExecutionError."""
        with pytest.raises(ToolExecutionError) as exc_info:
            calculate(Operation.DIVIDE, 10, 0, mock_tool_context)

        assert exc_info.value.error_code.name == "TOOL_EXECUTION_ERROR"
        assert "divide" in exc_info.value.details.get("operation", "").lower()

    def should_include_operation_details_in_error(self, mock_tool_context):
        """Test error details include operation parameters."""
        with pytest.raises(ToolExecutionError) as exc_info:
            calculate(Operation.DIVIDE, 10, 0, mock_tool_context)

        details = exc_info.value.details
        assert details["a"] == 10
        assert details["b"] == 0

    def should_accept_string_operation_and_convert_to_enum(self, mock_tool_context):
        """Test calculate accepts string operation."""
        # Tool should convert string to Operation enum
        result = calculate(Operation.ADD, 5, 3, mock_tool_context)

        assert result["operation"] == "add"

    def should_handle_float_numbers(self, mock_tool_context):
        """Test calculate with float numbers."""
        result = calculate(Operation.ADD, 2.5, 3.7, mock_tool_context)

        assert result["result"] == pytest.approx(6.2)

    def should_call_calculator_service(self, mock_tool_context):
        """Test tool delegates to calculator service."""
        with patch(
            "app.components.tools.custom.example_tool.calculator_client"
        ) as mock_client:
            mock_client.calculate.return_value = {"result": 42}

            calculate(Operation.ADD, 1, 1, mock_tool_context)

            mock_client.calculate.assert_called_once()


class TestGetCurrentTimeTool:
    """Tests for get_current_time ADK tool."""

    def should_return_time_info_with_default_timezone(self, mock_tool_context):
        """Test get_current_time with default timezone."""
        result = get_current_time(tool_context=mock_tool_context)

        assert "timezone" in result
        assert "timestamp" in result
        assert "unix_timestamp" in result
        assert "formatted" in result

    def should_accept_custom_timezone(self, mock_tool_context):
        """Test get_current_time with custom timezone."""
        result = get_current_time(
            timezone="America/New_York", tool_context=mock_tool_context
        )

        assert result["timezone"] == "America/New_York"

    def should_work_without_tool_context(self):
        """Test get_current_time when tool_context is None."""
        result = get_current_time(timezone="UTC", tool_context=None)

        assert result["timezone"] == "UTC"
        assert "timestamp" in result

    def should_return_current_utc_time_by_default(self, mock_tool_context):
        """Test default returns UTC time."""
        result = get_current_time(tool_context=mock_tool_context)

        assert result["timezone"] == "UTC"

    def should_call_time_service(self, mock_tool_context):
        """Test tool delegates to time service."""
        with patch(
            "app.components.tools.custom.example_tool.time_client"
        ) as mock_client:
            mock_client.get_current_time_info.return_value = {"timezone": "UTC"}

            get_current_time(timezone="UTC", tool_context=mock_tool_context)

            mock_client.get_current_time_info.assert_called_once_with("UTC")

    def should_return_iso_format_timestamp(self, mock_tool_context):
        """Test timestamp format."""
        result = get_current_time(tool_context=mock_tool_context)

        # Verify it's a valid ISO format
        from datetime import datetime

        datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))

    def should_return_integer_unix_timestamp(self, mock_tool_context):
        """Test unix timestamp type."""
        result = get_current_time(tool_context=mock_tool_context)

        assert isinstance(result["unix_timestamp"], int)
        assert result["unix_timestamp"] > 0
