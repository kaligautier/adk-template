"""
After-agent callback examples.

These callbacks are executed after agent execution completes.
Use cases:
- Log agent execution completion
- Process agent outputs
- Update workflow status
"""

import logging

from google.adk.agents.callback_context import CallbackContext

logger = logging.getLogger(__name__)


def log_agent_end(callback_context: CallbackContext) -> None:
    """
    Log when agent execution completes.

    Args:
        callback_context: ADK callback context
    """
    agent_name = callback_context.agent_name
    logger.info(f"Agent '{agent_name}' execution completed")
