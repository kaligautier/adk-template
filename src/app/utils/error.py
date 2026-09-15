"""Error handling with structured exceptions and HTTP status mapping."""

from enum import Enum


class ErrorCode(Enum):
    """Error codes for application exceptions."""

    GENERIC_ERROR = 1000
    INVALID_INPUT = 1001
    CONFIGURATION_ERROR = 1002
    INSTRUCTION_ERROR = 1003
    TOOL_EXECUTION_ERROR = 3001


HTTP_STATUS_CODES = {
    ErrorCode.GENERIC_ERROR: 500,
    ErrorCode.INVALID_INPUT: 400,
    ErrorCode.CONFIGURATION_ERROR: 500,
    ErrorCode.INSTRUCTION_ERROR: 500,
    ErrorCode.TOOL_EXECUTION_ERROR: 502,
}


ERROR_MESSAGES = {
    ErrorCode.GENERIC_ERROR: "An unexpected error occurred",
    ErrorCode.INVALID_INPUT: "Invalid input provided",
    ErrorCode.CONFIGURATION_ERROR: "Configuration error",
    ErrorCode.INSTRUCTION_ERROR: "Instruction loading or rendering failed",
    ErrorCode.TOOL_EXECUTION_ERROR: "Tool execution failed",
}


class AppError(Exception):
    """
    Base application error with automatic HTTP status mapping.

    Attributes:
        error_code: ErrorCode enum value
        message: Human-readable error message
        details: Optional dictionary with error context
        status_code: HTTP status code (automatically mapped)
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: str = None,
        details: dict = None,
    ):
        self.error_code = error_code
        self.status_code = HTTP_STATUS_CODES.get(error_code, 500)
        self.message = message or ERROR_MESSAGES.get(error_code, "An error occurred")
        self.details = details or {}

        super().__init__(self.message)

    def __str__(self):
        """String representation with error code and details."""
        detail_str = f", details={self.details}" if self.details else ""
        return f"[{self.error_code.name}] {self.message}{detail_str}"

    def to_dict(self):
        """Convert exception to dictionary for API responses."""
        return {
            "error_code": self.error_code.name,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }


class InvalidInputError(AppError):
    """Raised when input validation fails."""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCode.INVALID_INPUT,
            message=message,
            details=details,
        )


class ConfigurationError(AppError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCode.CONFIGURATION_ERROR,
            message=message,
            details=details,
        )


class InstructionError(AppError):
    """Raised when instruction loading or rendering fails."""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCode.INSTRUCTION_ERROR,
            message=message,
            details=details,
        )


class ToolExecutionError(AppError):
    """Raised when tool execution fails."""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            error_code=ErrorCode.TOOL_EXECUTION_ERROR,
            message=message,
            details=details,
        )
