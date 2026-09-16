"""
Tool-level callbacks.

These callbacks are configured on the AGENT, not as decorators.
They run before/after EVERY tool call made by the agent.

Configure on agent:
    agent = LlmAgent(
        name="my_agent",
        tools=[tool1, tool2],
        before_tool_callback=log_before_tool,
        after_tool_callback=log_after_tool,
    )

Use cases:
- Validate tool parameters
- Log tool execution
- Monitor performance
- Cache tool results
"""

import logging
from typing import Any, Dict, Optional

from google.adk.tools import BaseTool, ToolContext

from app.utils.error import ToolExecutionError

logger = logging.getLogger(__name__)


def log_before_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Log before tool execution.

    Args:
        callback_context: Agent callback context
        tool: The tool being called
        args: Tool arguments
        tool_context: Tool execution context

    Returns:
        None: Proceed with tool execution
        Dict: Skip execution and return this dict as result
    """
    logger.info("Tool '%s' called", tool.name)
    return None  # Proceed with execution


def log_after_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """
    Log after tool execution.

    Args:
        callback_context: Agent callback context
        tool: The tool that was called
        args: Tool arguments
        tool_context: Tool execution context
        response: Tool response

    Returns:
        None: Use original response
        Dict: Replace the tool response with this dict
    """
    logger.info(f"Tool '{tool.name}' completed")
    return None  # Use original response


def handle_tool_error(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, error: Exception
) -> Optional[Dict]:
    """Return expected tool failures to the model so it can explain or recover."""
    if not isinstance(error, ToolExecutionError):
        return None
    logger.warning("Tool '%s' failed: %s", tool.name, error.error_code.name)
    return {"status": "error", **error.to_dict()}
