"""Application constants."""

from app.instructions.instructions_manager import InstructionsManager

instructions_manager = InstructionsManager()

SINGLE_AGENT_DESCRIPTION = """
Simple single-purpose agent that demonstrates basic ADK patterns.
"""

SINGLE_AGENT_INSTRUCTION = instructions_manager.get_instructions("agent_instruction")
