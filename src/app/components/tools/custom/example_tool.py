"""ADK tool wrappers for custom Python functions."""

import logging
from typing import Optional

from google.adk.tools import ToolContext
from google.adk.tools.function_tool import FunctionTool

from app.services.calculator_service import Operation, calculator_client
from app.services.time_service import time_client
from app.utils.error import ToolExecutionError

logger = logging.getLogger(__name__)


def calculate(
    operation: Operation,
    a: float,
    b: float,
    tool_context: ToolContext,
) -> dict:
    """
    ADK tool wrapper for calculator service.

    This is a thin adapter that:
    - Exposes a synchronous function through ADK's FunctionTool
    - Handles ADK-specific context
    - Wraps service exceptions as ToolExecutionError
    - Uses Operation enum for type safety

    Args:
        operation: Mathematical operation (Operation.ADD, .SUBTRACT, .MULTIPLY, .DIVIDE)
        a: First number
        b: Second number
        tool_context: ADK tool context (automatically provided)

    Returns:
        dict: Calculation result from service

    Raises:
        ToolExecutionError: If calculation fails
    """
    logger.info(f"Calculate tool called: {operation}({a}, {b})")

    try:
        # Convert string to Operation enum
        operation_enum = Operation(operation)

        # Call business logic client
        result = calculator_client.calculate(operation_enum, a, b)
        return result

    except ValueError as e:
        # Wrap service errors as ToolExecutionError
        raise ToolExecutionError(
            message=str(e),
            details={"operation": operation, "a": a, "b": b},
        ) from e


def get_current_time(
    timezone: Optional[str] = None,
    tool_context: ToolContext = None,
) -> dict:
    """
    ADK tool wrapper for time service.

    Args:
        timezone: Optional timezone name
        tool_context: ADK tool context (optional)

    Returns:
        dict: Current time information from service
    """
    logger.info(f"Get current time tool called: {timezone or 'UTC'}")

    try:
        return time_client.get_current_time_info(timezone)
    except ValueError as exc:
        raise ToolExecutionError(
            message=str(exc), details={"timezone": timezone}
        ) from exc


# ADK Tool definitions
calculate_tool = FunctionTool(
    func=calculate,
)

get_current_time_tool = FunctionTool(
    func=get_current_time,
)
