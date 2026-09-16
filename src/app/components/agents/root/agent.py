"""
Root ADK 2.0 Workflow with Callbacks Example.

This demonstrates a complete ADK 2.0 workflow setup with:
- Custom tools (calculate, get_current_time)
- Before-agent callback (logs start, initializes state)
- After-agent callback (logs completion, finalizes state)
- A workflow root that can grow with sequential, routed, and parallel nodes

Use this pattern when:
- You need to track agent execution lifecycle
- You want to initialize/finalize workflow state
- You need logging and monitoring

Examples:
- AI personal shopper (product search)
- Customer service chatbot
- Document Q&A assistant
"""

import logging

from google.adk import Workflow
from google.adk.agents import LlmAgent

from app.components.callbacks.after_agent import log_agent_end
from app.components.callbacks.before_agent import log_agent_start
from app.components.callbacks.tool_callbacks import (
    handle_tool_error,
    log_after_tool,
    log_before_tool,
)
from app.components.tools.custom.example_tool import (
    calculate_tool,
    get_current_time_tool,
)
from app.config.constants import SINGLE_AGENT_DESCRIPTION, SINGLE_AGENT_INSTRUCTION
from app.config.settings import settings

logger = logging.getLogger(__name__)

assistant_agent = LlmAgent(
    name=settings.AGENT_NAME,
    model=settings.MODEL,
    mode="chat",
    description=SINGLE_AGENT_DESCRIPTION,
    instruction=SINGLE_AGENT_INSTRUCTION,
    tools=[
        calculate_tool,
        get_current_time_tool,
    ],
    before_agent_callback=log_agent_start,  # Log when agent starts
    after_agent_callback=log_agent_end,  # Log when agent completes
    before_tool_callback=log_before_tool,  # Log before each tool call
    after_tool_callback=log_after_tool,  # Log after each tool call
    on_tool_error_callback=handle_tool_error,
)

# CAUTION: this variable should always be called `root_agent` to be discovered by ADK.
# Keep the ADK 2.0 workflow as the composition root; add nodes and edges here as
# the application grows instead of coupling the API to individual agents.
root_agent = Workflow(
    name=settings.AGENT_NAME,
    edges=[("START", assistant_agent)],
)
