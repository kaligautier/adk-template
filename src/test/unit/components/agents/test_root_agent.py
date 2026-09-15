"""Unit tests for root agent configuration."""


class TestRootAgent:
    """Tests for root agent instance."""

    def should_exist_and_be_importable(self):
        """Test that root_agent can be imported."""
        from app.components.agents.root.agent import root_agent

        assert root_agent is not None

    def should_have_correct_type(self):
        """Test that root_agent is an ADK 2.0 Workflow."""
        from google.adk import Workflow

        from app.components.agents.root.agent import root_agent

        assert isinstance(root_agent, Workflow)

    def should_have_configured_name(self):
        """Test agent has name from settings."""
        from app.components.agents.root.agent import root_agent
        from app.config.settings import settings

        assert root_agent.name == settings.AGENT_NAME

    def should_have_configured_model(self):
        """Test agent has model from settings."""
        from app.components.agents.root.agent import assistant_agent
        from app.config.settings import settings

        assert assistant_agent.model == settings.MODEL

    def should_use_single_turn_mode(self):
        """Test workflow leaves use deterministic single-turn execution."""
        from app.components.agents.root.agent import assistant_agent

        assert assistant_agent.mode == "single_turn"

    def should_have_description(self):
        """Test agent has description."""
        from app.components.agents.root.agent import assistant_agent

        assert assistant_agent.description is not None
        assert len(assistant_agent.description) > 0

    def should_have_instruction(self):
        """Test agent has instruction."""
        from app.components.agents.root.agent import assistant_agent

        assert assistant_agent.instruction is not None
        assert len(assistant_agent.instruction) > 0

    def should_have_calculate_tool(self):
        """Test agent has calculate tool."""
        from app.components.agents.root.agent import assistant_agent
        from app.components.tools.custom.example_tool import calculate_tool

        assert calculate_tool in assistant_agent.tools

    def should_have_get_current_time_tool(self):
        """Test agent has get_current_time tool."""
        from app.components.agents.root.agent import assistant_agent
        from app.components.tools.custom.example_tool import get_current_time_tool

        assert get_current_time_tool in assistant_agent.tools

    def should_have_two_tools(self):
        """Test agent has exactly two tools."""
        from app.components.agents.root.agent import assistant_agent

        assert len(assistant_agent.tools) == 2

    def should_have_before_agent_callback(self):
        """Test agent has before_agent_callback configured."""
        from app.components.agents.root.agent import assistant_agent
        from app.components.callbacks.before_agent import log_agent_start

        assert assistant_agent.before_agent_callback == log_agent_start

    def should_have_after_agent_callback(self):
        """Test agent has after_agent_callback configured."""
        from app.components.agents.root.agent import assistant_agent
        from app.components.callbacks.after_agent import log_agent_end

        assert assistant_agent.after_agent_callback == log_agent_end

    def should_have_before_tool_callback(self):
        """Test agent has before_tool_callback configured."""
        from app.components.agents.root.agent import assistant_agent
        from app.components.callbacks.tool_callbacks import log_before_tool

        assert assistant_agent.before_tool_callback == log_before_tool

    def should_have_after_tool_callback(self):
        """Test agent has after_tool_callback configured."""
        from app.components.agents.root.agent import assistant_agent
        from app.components.callbacks.tool_callbacks import log_after_tool

        assert assistant_agent.after_tool_callback == log_after_tool


class TestRootAgentDescription:
    """Tests for root agent description."""

    def should_be_from_constants(self):
        """Test description matches SINGLE_AGENT_DESCRIPTION."""
        from app.components.agents.root.agent import assistant_agent
        from app.config.constants import SINGLE_AGENT_DESCRIPTION

        assert assistant_agent.description == SINGLE_AGENT_DESCRIPTION

    def should_contain_key_terms(self):
        """Test description contains expected terms."""
        from app.components.agents.root.agent import assistant_agent

        description = assistant_agent.description.lower()
        assert "agent" in description or "adk" in description


class TestRootAgentInstruction:
    """Tests for root agent instruction."""

    def should_be_from_constants(self):
        """Test instruction matches SINGLE_AGENT_INSTRUCTION."""
        from app.components.agents.root.agent import assistant_agent
        from app.config.constants import SINGLE_AGENT_INSTRUCTION

        assert assistant_agent.instruction == SINGLE_AGENT_INSTRUCTION

    def should_be_loaded_from_template(self):
        """Test instruction is loaded from template."""
        from app.components.agents.root.agent import assistant_agent

        # Instruction should contain content from agent_instruction.j2
        instruction = assistant_agent.instruction.lower()
        assert "assistant" in instruction or "ai" in instruction
