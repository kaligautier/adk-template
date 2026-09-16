# Tool Guidelines

## Decision: MCP vs Custom Tools

### Use MCP Servers When

✅ **External data sources**
- PostgreSQL, MongoDB, Redis
- REST APIs, external services

✅ **Reusable across projects**
- Shared toolsets
- Centrally managed definitions

✅ **Third-party integrations**
- GitLab, GitHub, Confluence, Jira
- Pre-built MCP servers available

✅ **Declarative queries**
- SQL-based operations
- Complex data transformations

### Use Custom Python Tools When

✅ **Custom business logic**
- Domain-specific operations
- Python-specific processing

✅ **Simple operations**
- Quick implementations
- Minimal external dependencies

✅ **Python libraries needed**
- NumPy, Pandas processing
- ML model inference
- File processing

> [!Note]
> Check for existing [ADK's built-in tools](https://google.github.io/adk-docs/tools/built-in-tools/#built-in-tools) before creating custom ones.

## Custom Tools Implementation

### Basic Structure

```python
# tools/custom/my_tool.py
from google.adk.tools import ToolContext
from google.adk.tools.function_tool import FunctionTool

def my_tool(param: str, tool_context: ToolContext) -> dict:
    """Tool description for LLM."""
    # Implementation
    return {"result": "..."}

# Wrap in FunctionTool
my_tool_instance = FunctionTool(func=my_tool)
```

### With Services Layer

```python
# services/my_service.py
def process_data(data: str) -> dict:
    """Pure Python business logic."""
    return {"processed": data.upper()}

# tools/custom/my_tool.py
from app.services.my_service import process_data
from app.utils.error import ToolExecutionError

def my_tool(data: str, tool_context: ToolContext) -> dict:
    """ADK adapter."""
    try:
        return process_data(data)
    except ValueError as e:
        raise ToolExecutionError(
            message=str(e),
            details={"data": data}
        ) from e

my_tool_instance = FunctionTool(func=my_tool)
```

### Register with Agent

```python
# components/agents/root/agent.py
from app.components.callbacks.tool_callbacks import handle_tool_error
from app.components.tools.custom.my_tool import my_tool_instance

assistant_agent = LlmAgent(
    name="template_agent",
    tools=[my_tool_instance, ...],
    on_tool_error_callback=handle_tool_error,
)
```

Keep `root_agent` as the workflow composition point. Its edges reference the
assistant agent. Wrap expected service errors at the tool boundary; avoid
catching every exception, which would hide programming defects from the caller.

## Testing

### Custom Tools

```python
# test/unit/components/tools/test_my_tool.py
def test_my_tool(mock_tool_context):
    result = my_tool("input", mock_tool_context)
    assert result["result"] == "expected"

def test_my_tool_error(mock_tool_context):
    with pytest.raises(ToolExecutionError):
        my_tool("invalid", mock_tool_context)
```

### Test Fixture

```python
# test/unit/conftest.py
@pytest.fixture
def mock_tool_context():
    context = MagicMock(spec=ToolContext)
    context.state = {}
    return context
```
