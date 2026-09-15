"""Unit tests for application constants."""


class TestSingleAgentDescription:
    """Tests for SINGLE_AGENT_DESCRIPTION constant."""

    def should_be_defined(self):
        """Test constant is defined and not None."""
        from app.config.constants import SINGLE_AGENT_DESCRIPTION

        assert SINGLE_AGENT_DESCRIPTION is not None

    def should_be_string(self):
        """Test constant is a string."""
        from app.config.constants import SINGLE_AGENT_DESCRIPTION

        assert isinstance(SINGLE_AGENT_DESCRIPTION, str)

    def should_have_content(self):
        """Test constant has non-empty content."""
        from app.config.constants import SINGLE_AGENT_DESCRIPTION

        assert len(SINGLE_AGENT_DESCRIPTION.strip()) > 0

    def should_describe_agent_purpose(self):
        """Test description contains agent-related terms."""
        from app.config.constants import SINGLE_AGENT_DESCRIPTION

        description_lower = SINGLE_AGENT_DESCRIPTION.lower()
        # Should contain at least one agent-related term
        assert any(
            term in description_lower
            for term in ["agent", "adk", "tool", "demonstrate"]
        )


class TestSingleAgentInstruction:
    """Tests for SINGLE_AGENT_INSTRUCTION constant."""

    def should_be_defined(self):
        """Test constant is defined and not None."""
        from app.config.constants import SINGLE_AGENT_INSTRUCTION

        assert SINGLE_AGENT_INSTRUCTION is not None

    def should_be_string(self):
        """Test constant is a string."""
        from app.config.constants import SINGLE_AGENT_INSTRUCTION

        assert isinstance(SINGLE_AGENT_INSTRUCTION, str)

    def should_have_content(self):
        """Test constant has non-empty content."""
        from app.config.constants import SINGLE_AGENT_INSTRUCTION

        assert len(SINGLE_AGENT_INSTRUCTION.strip()) > 0

    def should_be_loaded_from_template(self):
        """Test instruction is loaded from template manager."""
        from app.config.constants import SINGLE_AGENT_INSTRUCTION

        # Should contain content from agent_instruction.j2 template
        instruction_lower = SINGLE_AGENT_INSTRUCTION.lower()
        assert "assistant" in instruction_lower or "ai" in instruction_lower

    def should_contain_guidance_for_agent(self):
        """Test instruction contains behavioral guidance."""
        from app.config.constants import SINGLE_AGENT_INSTRUCTION

        instruction_lower = SINGLE_AGENT_INSTRUCTION.lower()
        # Should contain guidance terms
        guidance_terms = ["role", "answer", "use", "provide", "help", "you are"]
        assert any(term in instruction_lower for term in guidance_terms)


class TestInstructionsManager:
    """Tests for instructions_manager instance."""

    def should_be_defined(self):
        """Test instructions_manager instance is defined."""
        from app.config.constants import instructions_manager

        assert instructions_manager is not None

    def should_be_instructions_manager_instance(self):
        """Test instance is InstructionsManager type."""
        from app.config.constants import instructions_manager
        from app.instructions.instructions_manager import InstructionsManager

        assert isinstance(instructions_manager, InstructionsManager)
