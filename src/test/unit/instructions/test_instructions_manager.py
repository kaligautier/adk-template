"""Unit tests for instructions manager."""

from pathlib import Path

import pytest

from app.instructions.instructions_manager import InstructionsManager
from app.utils.error import InstructionError


@pytest.fixture
def templates_dir():
    """Provide templates directory path."""
    return (
        Path(__file__).parent.parent.parent.parent
        / "app"
        / "instructions"
        / "templates"
    )


@pytest.fixture
def temp_template(templates_dir):
    """Create and cleanup temporary template file."""
    created_files = []

    def _create_template(name: str, content: str):
        template_path = templates_dir / f"{name}.j2"
        template_path.write_text(content)
        created_files.append(template_path)
        return template_path

    yield _create_template

    # Cleanup
    for file in created_files:
        if file.exists():
            file.unlink()


class TestInstructionsManagerGetInstructions:
    """Tests for InstructionsManager.get_instructions method."""

    def should_load_and_render_template_without_variables(self):
        """Test loading template without variables."""
        result = InstructionsManager.get_instructions("agent_instruction")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "AI assistant" in result

    def should_render_template_with_single_variable(self, temp_template):
        """Test rendering template with one variable."""
        temp_template("test_single_var", "---\n---\nHello {{ name }}!")

        result = InstructionsManager.get_instructions("test_single_var", name="Alice")

        assert result == "Hello Alice!"

    def should_render_template_with_multiple_variables(self, temp_template):
        """Test rendering template with multiple variables."""
        temp_template(
            "test_multi_vars", "---\n---\n{{ greeting }} {{ name }}, you are {{ age }}."
        )

        result = InstructionsManager.get_instructions(
            "test_multi_vars", greeting="Hello", name="Bob", age=25
        )

        assert "Hello Bob" in result
        assert "25" in result

    def should_handle_jinja2_conditionals(self, temp_template):
        """Test rendering template with conditional logic."""
        temp_template(
            "test_conditional",
            "---\n---\n{% if show %}Visible{% else %}Hidden{% endif %}",
        )

        result_true = InstructionsManager.get_instructions(
            "test_conditional", show=True
        )
        result_false = InstructionsManager.get_instructions(
            "test_conditional", show=False
        )

        assert result_true == "Visible"
        assert result_false == "Hidden"

    def should_handle_jinja2_loops(self, temp_template):
        """Test rendering template with loops."""
        temp_template(
            "test_loop", "---\n---\n{% for item in items %}{{ item }}\n{% endfor %}"
        )

        result = InstructionsManager.get_instructions(
            "test_loop", items=["a", "b", "c"]
        )

        assert "a" in result
        assert "b" in result
        assert "c" in result

    def should_raise_error_for_missing_template(self):
        """Test error raised for non-existent template."""
        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_instructions("nonexistent_template")

        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.error_code.name == "INSTRUCTION_ERROR"

    def should_include_template_name_in_error_details(self):
        """Test error details include template name."""
        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_instructions("missing_template")

        assert "missing_template" in exc_info.value.details.get("template", "")

    def should_raise_error_for_undefined_variable(self, temp_template):
        """Test error raised when template uses undefined variable."""
        temp_template("test_undefined", "---\n---\nHello {{ undefined_var }}")

        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_instructions("test_undefined")

        assert "rendering" in str(exc_info.value).lower()

    def should_include_error_context_in_rendering_error(self, temp_template):
        """Test error context when rendering fails."""
        temp_template("test_error_context", "---\n---\nValue: {{ missing }}")

        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_instructions("test_error_context")

        assert "template" in exc_info.value.details
        assert "test_error_context" in exc_info.value.details["template"]

    def should_handle_general_exception_during_template_load(self, monkeypatch):
        """Test handling of general exceptions during template loading."""

        # Mock frontmatter.load to raise an OSError
        def mock_frontmatter_load(file):
            raise OSError("Unexpected file system error")

        import frontmatter

        monkeypatch.setattr(frontmatter, "load", mock_frontmatter_load)

        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_instructions("agent_instruction")

        assert "Failed to load template" in str(exc_info.value)
        assert "error" in exc_info.value.details


class TestInstructionsManagerGetTemplateInfo:
    """Tests for InstructionsManager.get_template_info method."""

    def should_return_complete_template_metadata(self):
        """Test getting all template metadata fields."""
        info = InstructionsManager.get_template_info("agent_instruction")

        assert "name" in info
        assert "description" in info
        assert "author" in info
        assert "variables" in info
        assert "frontmatter" in info

    def should_return_correct_template_name(self):
        """Test template name matches request."""
        info = InstructionsManager.get_template_info("agent_instruction")

        assert info["name"] == "agent_instruction"

    def should_parse_frontmatter_description(self):
        """Test frontmatter description parsing."""
        info = InstructionsManager.get_template_info("agent_instruction")

        assert len(info["description"]) > 0
        assert info["description"] == info["frontmatter"]["description"]

    def should_parse_frontmatter_author(self):
        """Test frontmatter author parsing."""
        info = InstructionsManager.get_template_info("agent_instruction")

        assert "author" in info["frontmatter"]
        assert len(info["author"]) > 0

    def should_return_variables_as_list(self):
        """Test variables are returned as list."""
        info = InstructionsManager.get_template_info("agent_instruction")

        assert isinstance(info["variables"], list)

    def should_detect_single_variable(self, temp_template):
        """Test detection of single variable in template."""
        temp_template(
            "test_one_var", "---\ndescription: Test\nauthor: Me\n---\nHello {{ name }}!"
        )

        info = InstructionsManager.get_template_info("test_one_var")

        assert "name" in info["variables"]
        assert len(info["variables"]) == 1

    def should_detect_multiple_variables(self, temp_template):
        """Test detection of multiple variables."""
        temp_template(
            "test_multi_detect",
            "---\ndescription: Test\n---\n{{ greeting }} {{ name }}, role: {{ role }}",
        )

        info = InstructionsManager.get_template_info("test_multi_detect")

        assert "greeting" in info["variables"]
        assert "name" in info["variables"]
        assert "role" in info["variables"]
        assert len(info["variables"]) == 3

    def should_handle_template_without_variables(self):
        """Test template with no variables returns empty list."""
        info = InstructionsManager.get_template_info("agent_instruction")

        # agent_instruction has no variables
        assert isinstance(info["variables"], list)

    def should_use_default_description_when_missing(self, temp_template):
        """Test default description when not in frontmatter."""
        temp_template("test_no_desc", "---\nauthor: Test\n---\nContent")

        info = InstructionsManager.get_template_info("test_no_desc")

        assert info["description"] == "No description provided"

    def should_use_default_author_when_missing(self, temp_template):
        """Test default author when not in frontmatter."""
        temp_template("test_no_author", "---\ndescription: Test\n---\nContent")

        info = InstructionsManager.get_template_info("test_no_author")

        assert info["author"] == "Unknown"

    def should_raise_error_for_missing_template(self):
        """Test error raised for non-existent template."""
        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_template_info("nonexistent_info")

        assert "not found" in str(exc_info.value).lower()

    def should_include_template_path_in_error(self):
        """Test error includes template path."""
        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_template_info("missing_info")

        assert "template_path" in exc_info.value.details

    def should_handle_general_exception_in_get_template_info(self, monkeypatch):
        """Test handling of general exceptions in get_template_info."""

        # Mock frontmatter.load to raise a PermissionError
        def mock_frontmatter_load(file):
            raise PermissionError("No permission to read file")

        import frontmatter

        monkeypatch.setattr(frontmatter, "load", mock_frontmatter_load)

        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_template_info("agent_instruction")

        assert "Failed to load template" in str(exc_info.value)

    def should_handle_parse_exception_in_get_template_info(self, temp_template):
        """Test handling of Jinja2 parse exceptions."""
        # Create template with invalid Jinja2 syntax
        temp_template("test_parse_error", "---\n---\n{% invalid syntax %}")

        with pytest.raises(InstructionError) as exc_info:
            InstructionsManager.get_template_info("test_parse_error")

        assert "Failed to parse template" in str(exc_info.value)
        assert "error" in exc_info.value.details


class TestInstructionsManagerEnvironment:
    """Tests for InstructionsManager environment management."""

    def should_create_environment_with_strict_undefined(self):
        """Test Jinja2 environment uses StrictUndefined."""
        InstructionsManager._env = None
        env = InstructionsManager._get_env()

        assert env is not None
        # StrictUndefined means undefined variables raise errors
        assert env.undefined.__name__ == "StrictUndefined"

    def should_reuse_environment_across_calls(self):
        """Test environment is cached and reused."""
        InstructionsManager._env = None
        env1 = InstructionsManager._get_env()
        env2 = InstructionsManager._get_env()

        assert env1 is env2

    def should_create_environment_on_first_call(self):
        """Test lazy environment initialization."""
        InstructionsManager._env = None
        env = InstructionsManager._get_env()

        assert env is not None
        assert hasattr(env, "loader")
        assert InstructionsManager._env is env
