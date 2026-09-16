# Services vs Tools

## Architecture

Separate business logic (services) from ADK adapters (tools).

```
┌─────────────────────────────────────┐
│ tools/                               │  ADK Tool Adapters
│ - Handle ToolContext                 │
│ - Wrap exceptions                    │
└──────────────┬──────────────────────┘
               │ calls
               ▼
┌─────────────────────────────────────┐
│ services/                            │  Business Logic
│ - Pure Python                        │
│ - No ADK dependencies                │
└─────────────────────────────────────┘
```

## Why Separate?

**Benefits:**
1. **Testable** - Services test without ADK
2. **Reusable** - Use in routes, CLI, other contexts
3. **Framework Independent** - Survives framework changes
4. **Clear Boundaries** - Tools = thin adapters, Services = business logic

## Implementation

### Service Layer (Pure Python)

```python
# services/calculator_service.py
class Operation(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"

class CalculatorClient:
    def calculate(self, operation: Operation, a: float, b: float) -> dict:
        operations = {
            Operation.ADD: lambda x, y: x + y,
            Operation.SUBTRACT: lambda x, y: x - y,
        }
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")
        return {
            "operation": operation.value,
            "a": a,
            "b": b,
            "result": operations[operation](a, b)
        }

calculator_client = CalculatorClient()
```

### Tool Layer (ADK Adapter)

```python
# tools/custom/example_tool.py
from google.adk.tools import ToolContext
from google.adk.tools.function_tool import FunctionTool
from app.services.calculator_service import calculator_client, Operation
from app.utils.error import ToolExecutionError

def calculate(
    operation: Operation,
    a: float,
    b: float,
    tool_context: ToolContext,
) -> dict:
    """ADK tool wrapper - delegates to service."""
    try:
        return calculator_client.calculate(Operation(operation), a, b)
    except ValueError as e:
        raise ToolExecutionError(
            message=str(e),
            details={"operation": operation, "a": a, "b": b}
        ) from e

# Wrap in FunctionTool
calculate_tool = FunctionTool(func=calculate)
```

## Type Safety with Enums

**Why Enums:**
- Type safety in services
- Automatic validation
- Better IDE support
- Clear documentation

```python
# Agent sends string
{"operation": "add", "a": 5, "b": 3}

# Tool converts to enum
operation_enum = Operation(operation)  # Validates

# Service uses type-safe enum
result = calculator_client.calculate(operation_enum, a, b)
```

## Testing Strategy

### Service Tests (Fast)

```python
# test/unit/services/test_calculator_service.py
def test_add():
    result = calculator_client.calculate(Operation.ADD, 5, 3)
    assert result["result"] == 8

def test_invalid_operation():
    with pytest.raises(ValueError):
        calculator_client.calculate(Operation("invalid"), 5, 3)
```

### Tool Adapter Tests (Unit)

```python
# test/unit/components/tools/test_example_tool.py
def test_calculate_tool(mock_tool_context):
    result = calculate(Operation.ADD, 5, 3, mock_tool_context)
    assert result["result"] == 8

def test_tool_error_handling(mock_tool_context):
    with pytest.raises(ToolExecutionError):
        calculate(Operation.DIVIDE, 10, 0, mock_tool_context)
```

### ADK and HTTP Integration

`src/test/integration/test_application.py` calls the real HTTP server and ADK
runner with a deterministic model. It verifies successful calculations and
recovery from expected tool errors through both `/run` and `/run_sse`.

The agent must register `handle_tool_error` as `on_tool_error_callback` to
deliver `ToolExecutionError` to the model as a structured response. Direct
Python callers of the adapter still receive the exception.

## When to Use This Pattern

**Use when:**
- Business logic can be reused
- Testing without ADK is important
- Logic may live outside ADK agents

**Skip when:**
- Tool is pure ADK integration (e.g., calling another agent)
- Logic is trivial (1-2 lines)
- Tool is prototype/temporary
