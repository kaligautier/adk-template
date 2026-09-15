"""Unit tests for error handling module."""

from app.utils.error import (
    ERROR_MESSAGES,
    HTTP_STATUS_CODES,
    AppError,
    ConfigurationError,
    ErrorCode,
    InstructionError,
    InvalidInputError,
    ToolExecutionError,
)


class TestErrorCode:
    """Tests for ErrorCode enum."""

    def should_have_generic_error_code(self):
        """Test GENERIC_ERROR code exists."""
        assert ErrorCode.GENERIC_ERROR.value == 1000

    def should_have_invalid_input_code(self):
        """Test INVALID_INPUT code exists."""
        assert ErrorCode.INVALID_INPUT.value == 1001

    def should_have_configuration_error_code(self):
        """Test CONFIGURATION_ERROR code exists."""
        assert ErrorCode.CONFIGURATION_ERROR.value == 1002

    def should_have_instruction_error_code(self):
        """Test INSTRUCTION_ERROR code exists."""
        assert ErrorCode.INSTRUCTION_ERROR.value == 1003

    def should_have_tool_execution_error_code(self):
        """Test TOOL_EXECUTION_ERROR code exists."""
        assert ErrorCode.TOOL_EXECUTION_ERROR.value == 3001


class TestHttpStatusCodes:
    """Tests for HTTP status code mapping."""

    def should_map_generic_error_to_500(self):
        """Test generic error maps to 500."""
        assert HTTP_STATUS_CODES[ErrorCode.GENERIC_ERROR] == 500

    def should_map_invalid_input_to_400(self):
        """Test invalid input maps to 400."""
        assert HTTP_STATUS_CODES[ErrorCode.INVALID_INPUT] == 400

    def should_map_configuration_error_to_500(self):
        """Test configuration error maps to 500."""
        assert HTTP_STATUS_CODES[ErrorCode.CONFIGURATION_ERROR] == 500

    def should_map_tool_execution_error_to_502(self):
        """Test tool execution error maps to 502."""
        assert HTTP_STATUS_CODES[ErrorCode.TOOL_EXECUTION_ERROR] == 502


class TestErrorMessages:
    """Tests for error message mapping."""

    def should_have_message_for_all_error_codes(self):
        """Test all error codes have messages."""
        for error_code in ErrorCode:
            assert error_code in ERROR_MESSAGES
            assert len(ERROR_MESSAGES[error_code]) > 0


class TestAppError:
    """Tests for AppError base exception."""

    def should_create_error_with_code_and_message(self):
        """Test creating error with code and message."""
        error = AppError(ErrorCode.GENERIC_ERROR, "Test error")

        assert error.error_code == ErrorCode.GENERIC_ERROR
        assert error.message == "Test error"
        assert error.details == {}

    def should_use_default_message_when_not_provided(self):
        """Test default message from ERROR_MESSAGES."""
        error = AppError(ErrorCode.INVALID_INPUT)

        assert error.message == ERROR_MESSAGES[ErrorCode.INVALID_INPUT]

    def should_map_error_code_to_http_status(self):
        """Test automatic HTTP status code mapping."""
        error = AppError(ErrorCode.INVALID_INPUT)

        assert error.status_code == 400

    def should_default_to_500_for_unmapped_codes(self):
        """Test unmapped error codes default to 500."""
        # Create error with code not in HTTP_STATUS_CODES
        error = AppError(ErrorCode.GENERIC_ERROR)
        error.error_code = type("obj", (object,), {"name": "UNKNOWN"})()

        # Should fall back to 500
        new_error = AppError(ErrorCode.GENERIC_ERROR)
        assert new_error.status_code == 500

    def should_store_optional_details_dict(self):
        """Test details dictionary storage."""
        details = {"field": "username", "value": "invalid"}
        error = AppError(ErrorCode.INVALID_INPUT, details=details)

        assert error.details == details

    def should_include_error_code_in_string_representation(self):
        """Test string representation includes error code."""
        error = AppError(ErrorCode.INVALID_INPUT, "Test error")
        error_str = str(error)

        assert "INVALID_INPUT" in error_str
        assert "Test error" in error_str

    def should_include_details_in_string_when_present(self):
        """Test string representation includes details."""
        error = AppError(ErrorCode.INVALID_INPUT, "Test error", {"key": "value"})
        error_str = str(error)

        assert "details=" in error_str

    def should_convert_to_dict_with_all_fields(self):
        """Test to_dict includes all error fields."""
        error = AppError(ErrorCode.INVALID_INPUT, "Test error", {"field": "email"})
        error_dict = error.to_dict()

        assert error_dict["error_code"] == "INVALID_INPUT"
        assert error_dict["message"] == "Test error"
        assert error_dict["status_code"] == 400
        assert error_dict["details"] == {"field": "email"}


class TestInvalidInputError:
    """Tests for InvalidInputError exception."""

    def should_set_correct_error_code(self):
        """Test InvalidInputError uses INVALID_INPUT code."""
        error = InvalidInputError("Bad input")

        assert error.error_code == ErrorCode.INVALID_INPUT

    def should_map_to_400_status_code(self):
        """Test InvalidInputError maps to 400."""
        error = InvalidInputError("Bad input")

        assert error.status_code == 400

    def should_accept_custom_message(self):
        """Test custom message."""
        error = InvalidInputError("Custom message")

        assert error.message == "Custom message"

    def should_accept_details_dict(self):
        """Test details dictionary."""
        error = InvalidInputError("Bad input", {"field": "age"})

        assert error.details == {"field": "age"}


class TestConfigurationError:
    """Tests for ConfigurationError exception."""

    def should_set_correct_error_code(self):
        """Test ConfigurationError uses CONFIGURATION_ERROR code."""
        error = ConfigurationError("Config missing")

        assert error.error_code == ErrorCode.CONFIGURATION_ERROR

    def should_map_to_500_status_code(self):
        """Test ConfigurationError maps to 500."""
        error = ConfigurationError("Config missing")

        assert error.status_code == 500


class TestInstructionError:
    """Tests for InstructionError exception."""

    def should_set_correct_error_code(self):
        """Test InstructionError uses INSTRUCTION_ERROR code."""
        error = InstructionError("Template not found")

        assert error.error_code == ErrorCode.INSTRUCTION_ERROR

    def should_map_to_500_status_code(self):
        """Test InstructionError maps to 500."""
        error = InstructionError("Template not found")

        assert error.status_code == 500


class TestToolExecutionError:
    """Tests for ToolExecutionError exception."""

    def should_set_correct_error_code(self):
        """Test ToolExecutionError uses TOOL_EXECUTION_ERROR code."""
        error = ToolExecutionError("Tool failed")

        assert error.error_code == ErrorCode.TOOL_EXECUTION_ERROR

    def should_map_to_502_status_code(self):
        """Test ToolExecutionError maps to 502."""
        error = ToolExecutionError("Tool failed")

        assert error.status_code == 502

    def should_accept_tool_details(self):
        """Test tool execution details."""
        error = ToolExecutionError(
            "Division by zero", {"tool": "calculate", "operation": "divide"}
        )

        assert error.details["tool"] == "calculate"
        assert error.details["operation"] == "divide"
