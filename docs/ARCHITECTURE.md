# Architecture

## Overview

This template follows hexagonal architecture with clear layer separation and ADK framework conventions.

## Layer Structure

```
┌─────────────────────────────────────┐
│  Presentation (main.py, routes/)    │  HTTP interface
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Application (services/)             │  Business logic
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Domain (components/agents/)         │  Agent definitions
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Infrastructure (config/, utils/)    │  Configuration, logging
└─────────────────────────────────────┘
```

## Key Decisions

### 1. Component-Based Organization

```
components/
├── agents/      # ADK auto-detects subfolders
├── tools/       # Custom Python + MCP servers
└── callbacks/   # Lifecycle hooks
```

**Why:** Clear separation, ADK conventions, scalability.

### 2. Services Layer Separation

Business logic lives in `services/`, ADK adapters in `tools/`.

**Benefits:**
- Framework-independent business logic
- Testable without ADK overhead
- Reusable across contexts

### 3. Pydantic Settings

Environment-driven configuration with type safety and validation.

**Why:** Type safety, automatic .env loading, clear defaults.

### 4. Jinja2 Instructions

Templates with frontmatter metadata for agent instructions.

**Why:** Separates content from code, supports variables, version control friendly.

### 5. Error Hierarchy

Custom exceptions with automatic HTTP status mapping.

```python
class AppError(Exception):
    error_code: ErrorCode
    status_code: int  # Auto-mapped
    message: str
    details: dict
```

## File Organization

### Root Agent Pattern

```
components/agents/root/
├── __init__.py
└── agent.py  # Must export 'root_agent' variable
```

**Critical:** Variable name must match folder name for ADK auto-detection.

### Tools Structure

```
components/tools/
├── custom/      # Python functions
│   └── example_tool.py
└── mcp/         # MCP server integrations
```

### Services Structure

```
services/
├── calculator_service.py  # Pure Python
└── time_service.py        # No ADK dependencies
```

## Configuration Flow

1. Environment variables (highest priority)
2. `.env` file (auto-loaded if not Docker)
3. Default values in `settings.py`

## Error Handling

```python
# Service raises standard exceptions
raise ValueError("Division by zero")

# Tool wraps as ToolExecutionError
raise ToolExecutionError(
    message=str(e),
    details={"operation": "divide", "a": 10, "b": 0}
)
```

## Testing Strategy

- **Services:** Fast unit tests, no ADK
- **Tools:** Integration tests with mocked ToolContext
- **Agent:** End-to-end tests via API

## Design Principles

1. **Dependency Direction:** Outer → Inner layers only
2. **Framework Independence:** Business logic has no ADK imports
3. **Type Safety:** Enums for operations, Pydantic for config
4. **Clear Boundaries:** Each layer has single responsibility
