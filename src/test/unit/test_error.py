"""
Tests for error handling module.

Tests:
- Error code mapping
- HTTP status codes
- Error messages
- Custom exceptions
"""

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


def test_error_codes_defined():
    """Test that all error codes are defined."""
    assert ErrorCode.GENERIC_ERROR is not None
    assert ErrorCode.INVALID_INPUT is not None
    assert ErrorCode.CONFIGURATION_ERROR is not None
    assert ErrorCode.INSTRUCTION_ERROR is not None
    assert ErrorCode.TOOL_EXECUTION_ERROR is not None


def test_http_status_mapping():
    """Test that error codes map to appropriate HTTP status codes."""
    assert HTTP_STATUS_CODES[ErrorCode.GENERIC_ERROR] == 500
    assert HTTP_STATUS_CODES[ErrorCode.INVALID_INPUT] == 400
    assert HTTP_STATUS_CODES[ErrorCode.CONFIGURATION_ERROR] == 500
    assert HTTP_STATUS_CODES[ErrorCode.INSTRUCTION_ERROR] == 500
    assert HTTP_STATUS_CODES[ErrorCode.TOOL_EXECUTION_ERROR] == 502


def test_error_messages_defined():
    """Test that error messages are defined for all codes."""
    for error_code in ErrorCode:
        assert error_code in ERROR_MESSAGES
        assert isinstance(ERROR_MESSAGES[error_code], str)
        assert len(ERROR_MESSAGES[error_code]) > 0


def test_app_error_creation():
    """Test AppError creation with all parameters."""
    error = AppError(
        error_code=ErrorCode.GENERIC_ERROR,
        message="Test error message",
        details={"key": "value"},
    )

    assert error.error_code == ErrorCode.GENERIC_ERROR
    assert error.message == "Test error message"
    assert error.details == {"key": "value"}
    assert error.status_code == 500


def test_app_error_default_message():
    """Test that AppError uses default message when none provided."""
    error = AppError(error_code=ErrorCode.INVALID_INPUT)

    assert error.message == ERROR_MESSAGES[ErrorCode.INVALID_INPUT]


def test_app_error_to_dict():
    """Test AppError to_dict method."""
    error = AppError(
        error_code=ErrorCode.CONFIGURATION_ERROR,
        message="Config failed",
        details={"config": "test_config"},
    )

    error_dict = error.to_dict()

    assert error_dict["error_code"] == "CONFIGURATION_ERROR"
    assert error_dict["message"] == "Config failed"
    assert error_dict["status_code"] == 500
    assert error_dict["details"] == {"config": "test_config"}


def test_invalid_input_error():
    """Test InvalidInputError specialized exception."""
    error = InvalidInputError(message="Invalid parameter", details={"param": "value"})

    assert error.error_code == ErrorCode.INVALID_INPUT
    assert error.status_code == 400
    assert error.message == "Invalid parameter"


def test_configuration_error():
    """Test ConfigurationError specialized exception."""
    error = ConfigurationError(message="Config missing")

    assert error.error_code == ErrorCode.CONFIGURATION_ERROR
    assert error.status_code == 500


def test_instruction_error():
    """Test InstructionError specialized exception."""
    error = InstructionError(message="Template not found")

    assert error.error_code == ErrorCode.INSTRUCTION_ERROR
    assert error.status_code == 500


def test_tool_execution_error():
    """Test ToolExecutionError specialized exception."""
    error = ToolExecutionError(message="Tool failed", details={"tool": "calculate"})

    assert error.error_code == ErrorCode.TOOL_EXECUTION_ERROR
    assert error.status_code == 502
    assert error.details["tool"] == "calculate"


def test_app_error_string_representation():
    """Test AppError __str__ method."""
    error = AppError(
        error_code=ErrorCode.GENERIC_ERROR,
        message="Test message",
        details={"key": "value"},
    )

    error_str = str(error)

    assert "GENERIC_ERROR" in error_str
    assert "Test message" in error_str
    assert "key" in error_str
