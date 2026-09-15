"""
Before-agent callback examples.

These callbacks are executed before agent execution begins.
Use cases:
- Log agent execution start
- Initialize state
- Validate prerequisites
"""

import logging

from google.adk.agents.callback_context import CallbackContext

logger = logging.getLogger(__name__)


def log_agent_start(callback_context: CallbackContext) -> None:
    """
    Log when agent execution starts.

    Args:
        callback_context: ADK callback context
    """
    agent_name = callback_context.agent_name
    logger.info(f"Agent '{agent_name}' execution starting")
