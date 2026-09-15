# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **enterprise architecture reference template** for Google ADK (Agent Development Kit) agents. The template demonstrates production-ready patterns using intentionally simple examples (calculator, time service) to focus on architectural structure rather than business logic complexity.

**Key Philosophy**: Simple domain examples + sophisticated architecture = clear pattern demonstration.

## Claude Code Execution Policy

### Commands Claude Can Execute Autonomously

**Just commands** (development workflow):
```bash
just install      # Install dependencies
just api          # Run API server
just format       # Format code
just lint         # Lint code
just test         # Run tests
just pre-commit   # All quality checks
just build        # Build Docker image
```

**Git commands** (ONLY when user explicitly requests git operations):
```bash
git status
git add <files>
git commit -m "message"
git push
git checkout -b <branch>
git branch
git log
```

**File operations** (code editing):
- ✅ Create/edit files using artifact system
- ✅ Read files with `cat` or file reading tools
- ❌ Delete files (requires approval)

### Commands Requiring User Approval

All other commands require explicit user approval, including:
- Direct `uv` commands
- Direct `pytest` commands
- Direct `docker` commands
- System modifications
- File deletions

**Rationale**: Use `just` commands as the standard interface for consistency and safety. Direct tool invocation should be user-initiated.

## Development Commands Reference

### Setup
```bash
just install     # Install dependencies with uv
cp .env.example .env
# Edit .env with your GCP project details
```

### Running the Agent
```bash
just api    # API server (development mode with hot reload)

### Testing
```bash
just test   # Run all tests with coverage

### Code Quality
```bash
just format      # Format code with ruff
just lint        # Lint code with ruff
just pre-commit  # All quality checks (format + lint + test)

### Docker
```bash
just build   # Build Docker image
just run     # Run Docker container

## Architecture Overview

### Hexagonal Architecture (4 Layers)

**Layer Flow**: Presentation → Application → Domain → Infrastructure

```
┌─────────────────────────────────────┐
│  Presentation Layer                 │  main.py, application.py, routes/
│  (HTTP interface, request handling) │  Depends on: Application layer
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Application Layer                  │  services/
│  (Business logic, workflow)         │  Depends on: Domain layer
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Domain Layer                       │  components/agents/, config/constants.py
│  (Agent definitions, business rules)│  Depends on: Nothing (pure domain)
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Infrastructure Layer               │  config/settings.py, utils/
│  (Logging, error handling, config)  │  Depends on: Nothing (supports all)
└─────────────────────────────────────┘
```

### Critical Directory Structure

```
src/app/
├── components/                    # ADK-specific components
│   ├── agents/                    # Agent definitions (ADK auto-detects)
│   │   └── root/                  # Root agent (must have agent.py)
│   │       ├── __init__.py
│   │       └── agent.py           # Must export 'root_agent' variable
│   ├── tools/                     # Tool implementations
│   │   ├── custom/                # Custom Python tools
│   │   └── mcp/                   # MCP toolset loaders
│   └── callbacks/                 # Lifecycle hooks
│       ├── before_agent.py        # Agent-level before callback
│       ├── after_agent.py         # Agent-level after callback
│       └── tool_callbacks.py      # Tool-level callbacks
├── services/                      # Business logic layer (framework-independent)
│   ├── calculator_service.py     # Pure Python logic, no ADK dependencies
│   └── time_service.py
├── instructions/                  # Jinja2 instruction templates
│   ├── templates/                 # .j2 template files with frontmatter
│   └── instructions_manager.py   # Template loader with variable substitution
├── config/                        # Configuration layer
│   ├── settings.py                # Pydantic BaseSettings (env-driven)
│   └── constants.py               # Domain constants, loaded instructions
├── utils/                         # Cross-cutting utilities
│   ├── error.py                   # Error codes + HTTP mapping
│   └── logger.py                  # Module-qualified logging filter
├── main.py                        # FastAPI entry point
└── application.py                 # FastAPI app factory
```

## Services vs Tools Pattern

**Critical Concept**: This template separates business logic from ADK framework code.

### Services Layer (Pure Python)
- **Location**: `services/`
- **Purpose**: Framework-independent business logic
- **Dependencies**: None (pure Python)
- **Testing**: Fast unit tests without ADK overhead

```python
# services/calculator_service.py
from enum import Enum

class Operation(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"

def calculate(operation: Operation, a: float, b: float) -> dict:
    """Pure Python logic - no ADK dependencies."""
    operations = {Operation.ADD: lambda x, y: x + y}
    return {"result": operations[operation](a, b)}
```

### Tools Layer (ADK Adapters)
- **Location**: `components/tools/custom/`
- **Purpose**: Thin async wrappers that call services
- **Dependencies**: ADK framework, services
- **Testing**: Integration tests with mocked ToolContext

```python
# components/tools/custom/example_tool.py
from app.services.calculator_service import calculate as calc_service, Operation

async def calculate(operation: str, a: float, b: float, tool_context: ToolContext):
    """Thin ADK wrapper - delegates to service."""
    op_enum = Operation(operation)  # Convert string to enum
    return calc_service(op_enum, a, b)
```

**Why This Pattern**:
- Services testable without ADK
- Business logic reusable outside agents (CLI, routes, background jobs)
- Clear separation of concerns
- Type safety with enums at service layer

## Configuration System

### Environment-Driven with Pydantic

**Required Environment Variables**:
```bash
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_CLOUD_LOCATION=us-central1
```

**Optional (with defaults)**:
```bash
APP_NAME="ADK Agent Template"
AGENT_NAME=template_agent
MODEL=gemini-2.5-flash
LOG_LEVEL=INFO
DEBUG=false
```

### Configuration Loading Order
1. Environment variables (highest priority)
2. `.env` file (auto-loaded in non-Docker environments)
3. Default values in `settings.py`

### Settings Usage
```python
from app.config.settings import settings

# Access settings anywhere
agent = LlmAgent(
    name=settings.AGENT_NAME,
    model=settings.MODEL,
)
```

**Key Feature**: Settings auto-detects Docker environment and only loads `.env` file when not in Docker (prevents conflicts with container orchestration).

## Agent Auto-Detection by ADK

**Critical**: ADK automatically discovers agents using filesystem conventions.

### Agent Discovery Rules
1. Agent folders must be in `components/agents/`
2. Each agent folder must contain `agent.py`
3. `agent.py` must export a variable named like the parent folder: `{folder_name}_agent`

**Example**:
```python
# components/agents/root/agent.py
root_agent = LlmAgent(...)  # Variable name MUST be 'root_agent'

# components/agents/analytics/agent.py
analytics_agent = LlmAgent(...)  # Variable name MUST be 'analytics_agent'
```

### Current Agent
- **Path**: `src/app/components/agents/root/agent.py`
- **Variable**: `root_agent`
- **Type**: `LlmAgent` (single agent with tools and callbacks)

## Error Handling System

### Error Code Categories
```python
# 1xxx: Input validation errors
GENERIC_ERROR = 1000
INVALID_INPUT = 1001
CONFIGURATION_ERROR = 1002
INSTRUCTION_ERROR = 1003

# 3xxx: External dependency errors
TOOL_EXECUTION_ERROR = 3001
```

### Error Usage
```python
from app.utils.error import ToolExecutionError

# Raise with structured error
raise ToolExecutionError(
    message="Division by zero",
    details={"operation": "divide", "a": 10, "b": 0}
)
```

**Automatic HTTP Mapping**: Error codes automatically map to HTTP status codes (defined in `HTTP_STATUS_CODES` dict).

## Logging System

### Module-Qualified Logging

**Output Format**:
```
INFO:      app.agent_service.execute: Starting agent execution
WARNING:   app.tools.calculate.invoke: Division by zero attempt
ERROR:     app.utils.error.handle: Tool execution failed
```

### Logging Usage
```python
import logging

logger = logging.getLogger(__name__)  # Module-level logger

def my_function():
    logger.info("Starting operation")
    logger.debug(f"Processing {count} items")
    logger.error("Operation failed", exc_info=True)
```

**Custom Filter**: `AppLoggingFilter` automatically adds module + function name to all log records.

## Instruction Templates

### Jinja2 with Frontmatter

**Template Structure**:
```jinja2
---
description: "Agent instruction template"
author: "Your Team"
---
You are a helpful assistant that can {{ capability }}.

{% if company %}
You work for {{ company }}.
{% endif %}
```

### Loading Instructions
```python
from app.instructions.instructions_manager import InstructionsManager

manager = InstructionsManager()
instruction = manager.get_instructions(
    "agent_instruction",
    company="TechCorp",
    capability="perform calculations"
)
```

**Error Handling**: Raises `InstructionError` for missing templates or invalid Jinja2 syntax.

## Callbacks System

### Agent-Level Callbacks
- **before_agent_callback**: Initialize workflow, validate prerequisites, set up state
- **after_agent_callback**: Finalize results, cleanup resources, aggregate outputs

### Tool-Level Callbacks
- **before_tool_callback**: Validate tool parameters, log tool invocation, start metrics
- **after_tool_callback**: Log tool results, handle errors, cache results, stop metrics

### Callback Context State Management
```python
def my_callback(callback_context: CallbackContext):
    # Access state
    project_id = callback_context.state.get("project_id")

    # Update state
    callback_context.state.update({
        "branch_name": "feature/new",
        "files_modified": []
    })
```

## Adding New Components

### Add a New Tool
1. **Service (optional)**: Create in `services/` if logic is reusable
   ```python
   # services/my_service.py
   def process_data(data: dict) -> dict:
       return {"processed": data}
   ```

2. **Tool**: Create in `components/tools/custom/`
   ```python
   # components/tools/custom/my_tool.py
   from google.adk.tools import ToolContext
   from app.services.my_service import process_data

   async def my_tool(data: dict, tool_context: ToolContext) -> dict:
       return process_data(data)
   ```

3. **Add to Agent**: Import and add to tools list
   ```python
   # components/agents/root/agent.py
   from app.components.tools.custom.my_tool import my_tool

   root_agent = LlmAgent(
       tools=[calculate, get_current_time, my_tool]
   )
   ```

### Add a New Agent
1. Create folder: `components/agents/my_agent/`
2. Create agent file: `components/agents/my_agent/agent.py`
3. Export variable matching folder name:
   ```python
   # components/agents/my_agent/agent.py
   my_agent = LlmAgent(name="my_agent", tools=[...])
   ```
4. ADK will auto-detect the new agent

### Add MCP Toolset
1. Configure MCP server URL in settings
2. Create toolset loader in `components/tools/mcp/`:
   ```python
   from google.adk.tools.mcp import ToolboxSyncClient
   from app.config.settings import settings

   client = ToolboxSyncClient(url=settings.MCP_URL)
   my_toolset = client.load_toolset("my_toolset")
   ```
3. Add to agent tools: `tools=[*my_toolset]`

## Testing Strategy

### Service Layer Tests (Fast Unit Tests)
```python
# test/unit/services/test_calculator_service.py
from app.services.calculator_service import calculate, Operation

def test_calculate_add():
    result = calculate(Operation.ADD, 5, 3)
    assert result["result"] == 8
```

### Tool Layer Tests (Integration Tests)
```python
# test/unit/components/test_tools.py
import pytest
from app.components.tools.custom.example_tool import calculate

@pytest.mark.asyncio
async def test_calculate_tool(mock_tool_context):
    result = await calculate("add", 5, 3, mock_tool_context)
    assert result["result"] == 8
```

### Test Fixtures
```python
# test/unit/conftest.py
@pytest.fixture
def mock_tool_context():
    """Mock ToolContext for testing tools."""
    return MagicMock(spec=ToolContext)
```

## API Endpoints

### Auto-Generated by ADK
- `POST /api/sessions` - Create conversation session
- `POST /api/sessions/{id}/messages` - Send message to agent
- `GET /api/sessions/{id}/messages` - Get conversation history
- `GET /docs` - Swagger UI (interactive API docs)
- `GET /redoc` - ReDoc (alternative API docs)

### Custom Endpoint Example
```python
# routes/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Specialized Agents for Complex Tasks

Claude Code has access to specialized agents for handling complex, multi-step tasks. Use these agents to delegate work when appropriate.

### Architecture & Design Agents

#### system-architect
**Use when**: Designing system architecture, making long-term technical decisions
**Example**: "Design a multi-agent system architecture for this template"
```python
# Usage in conversation
"I need to design the architecture for adding database support to this template"
# Claude will invoke: Task(subagent_type="system-architect", ...)
```

#### refactoring-expert
**Use when**: Improving code quality, reducing technical debt, challenging design decisions
**Example**: "Review the services layer separation and suggest improvements"

#### backend-architect
**Use when**: Designing backend systems with focus on data integrity, security, fault tolerance
**Example**: "Design error handling strategy for production deployment"

### Development Agents

#### python-expert
**Use when**: Python-specific best practices, SOLID principles, type safety
**Example**: "Review the calculator service for Python best practices"

#### quality-engineer
**Use when**: Testing strategies, edge case detection, quality assurance
**Example**: "Design comprehensive test strategy for the callback system"

#### performance-engineer
**Use when**: Performance optimization, bottleneck elimination
**Example**: "Analyze and optimize agent initialization time"

#### security-engineer
**Use when**: Security vulnerabilities, compliance, best practices
**Example**: "Security review of the authentication middleware placeholder"

### Analysis Agents

#### root-cause-analyst
**Use when**: Investigating complex problems, systematic debugging
**Example**: "Agent fails to start - investigate root cause"

#### requirements-analyst
**Use when**: Transforming ambiguous ideas into concrete specifications
**Example**: "Help me specify requirements for adding email campaign agent"

### Documentation & Learning

#### technical-writer
**Use when**: Creating clear documentation, API documentation
**Example**: "Document the services vs tools pattern for new developers"

#### learning-guide
**Use when**: Teaching concepts, explaining code with progressive learning
**Example**: "Explain the hexagonal architecture to a junior developer"

#### socratic-mentor
**Use when**: Educational guidance through strategic questioning
**Example**: "Help me understand when to use callbacks through Socratic dialogue"

### Business Analysis

#### business-panel-experts
**Use when**: Business strategy, market analysis, strategic decisions
**Example**: "Analyze the market positioning of this ADK template"

### Agent Usage Pattern

```python
# Claude will automatically use Task tool when complexity warrants it
# Example internal decision process:
# - Simple question about code → Direct answer
# - Complex architectural decision → Invoke system-architect agent
# - Multi-file refactoring → Invoke refactoring-expert agent
# - Security concerns → Invoke security-engineer agent
```

## MCP Servers Integration

Claude Code has access to Model Context Protocol (MCP) servers for enhanced capabilities.

### Context7 - Official Documentation Lookup

**Purpose**: Retrieve up-to-date official documentation for libraries and frameworks

**ADK Documentation ID**: `google.github.io/adk-docs`

**When to use**:
- Looking up ADK API reference
- Checking ADK best practices
- Verifying agent patterns
- Understanding tool implementation details

**Example usage**:
```python
# When you need ADK documentation
# 1. Resolve library ID
mcp__context7__resolve-library-id(libraryName="google agent development kit")
# Returns: /google/adk-docs

# 2. Get specific documentation
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/google/adk-docs",
    topic="callbacks",
    mode="code"  # or "info" for conceptual docs
)
```

**Available modes**:
- `mode="code"`: API references, code examples, implementation details
- `mode="info"`: Conceptual guides, architecture, narrative information

### Sequential Thinking - Multi-Step Analysis

**Purpose**: Complex problem-solving through structured reasoning with hypothesis generation and verification

**When to use**:
- Breaking down complex architectural problems
- Multi-step debugging with uncertain root cause
- Design decisions requiring exploration of alternatives
- Analysis requiring revision of earlier thoughts

**Example usage**:
```python
# For complex analysis requiring multiple reasoning steps
mcp__sequential-thinking__sequentialthinking(
    thought="Analyzing why agent initialization is slow...",
    thoughtNumber=1,
    totalThoughts=5,  # Can be adjusted as analysis progresses
    nextThoughtNeeded=True,
    isRevision=False
)
```

**Key features**:
- Dynamic thought adjustment (can increase/decrease total thoughts)
- Revision capability (can revise previous conclusions)
- Branching support (explore alternative approaches)
- Hypothesis generation and verification
- Iterative until satisfactory solution found

### Playwright - Browser Testing

**Purpose**: Automated browser testing and interaction with web UI

**When to use**:
- Testing the ADK web interface (`just api`)
- Verifying agent responses in UI
- E2E testing of agent interactions
- Accessibility testing
- Visual validation

**Testing the ADK Web Interface**:
```python
# 1. Start the ADK web server
just api  # Runs at http://localhost:8000/dev-ui

# 2. Use Playwright to test
# Claude can invoke Playwright MCP to:
# - Navigate to http://localhost:8000/dev-ui
# - Test agent conversation flow
# - Verify tool execution in UI
# - Screenshot results
# - Test accessibility

# Example test flow:
# 1. Open web UI
# 2. Create new session
# 3. Send message: "Calculate 5 + 3"
# 4. Verify agent uses calculate tool
# 5. Verify response shows result: 8
```

**Common test scenarios**:
- Agent loads correctly in web UI
- Tools are available and functional
- Callbacks execute and log properly
- Error handling displays correctly
- Session state persists across messages

### MCP Integration Best Practices

1. **Context7 for Documentation**:
   - Always verify ADK patterns against official docs
   - Use when implementing new ADK features
   - Check for version-specific behavior

2. **Sequential Thinking for Architecture**:
   - Use for complex architectural decisions
   - Good for analyzing trade-offs
   - Helpful when multiple valid approaches exist

3. **Playwright for Validation**:
   - Test after significant agent changes
   - Verify tool integrations work end-to-end
   - Validate error handling in UI
   - Can be used to demonstrate functionality to user

## Documentation Resources

- **ARCHITECTURE.md**: 15 architectural decisions with rationale
- **SERVICES_VS_TOOLS.md**: Hexagonal architecture pattern details
- **TOOL_GUIDELINES.md**: MCP vs custom tools decision guide
- **AGENT_PATTERNS.md**: Single vs hierarchical vs parallel agent patterns

## Important Notes

### Template Purpose
This is an **enterprise reference template** demonstrating production patterns, NOT a minimal quickstart. The calculator example is intentionally simple to keep focus on architectural patterns rather than business logic.

### ADK Framework Behavior
- ADK auto-generates FastAPI endpoints
- Agent discovery happens at startup via filesystem scan
- Tool parameters automatically extracted from function signatures
- ToolContext automatically injected into tool functions

### Common Pitfalls
1. **Agent variable naming**: Must match folder name (`root_agent` for `agents/root/`)
2. **Async tool functions**: All custom tools must be `async def`
3. **ToolContext parameter**: Must be last parameter in tool signature
4. **Settings validation**: Missing required env vars cause startup failure
5. **Import paths**: Use `from app.` prefix (not relative imports)

### Type Safety with Enums
The template uses `str` enums for type-safe operations:
- Agent sends strings (`"add"`)
- Tool converts to enum (`Operation.ADD`)
- Service uses type-safe enum
- Automatic validation via enum construction
