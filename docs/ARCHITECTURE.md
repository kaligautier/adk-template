# Architecture

## Dependency flow

```text
main.py -> create_app() -> ADK HTTP server
                              |
                              v
                         root Workflow
                              |
                              v
                         assistant_agent
                              |
                              v
                         FunctionTool
                              |
                              v
                         Python service
```

`services/` contains framework-independent business logic. ADK agents, tools,
and callbacks live in `components/`. Configuration and prompt loading support
orchestration. This separation allows services to run in another API, CLI, or
job without importing ADK; it does not require additional domain abstractions.

## Composition and discovery

`components/agents/root/agent.py` exports a `root_agent` workflow. Its first edge
is `START -> assistant_agent`. The `LlmAgent` uses `mode="chat"` to include
previous session turns in each model request, alongside the current turn's
tool calls. ADK requires chat agents to be wired directly after `START`.
Extend workflow edges for orchestration while preserving that constraint.

ADK discovers agent directories containing `agent.py`. The exported variable is
always named `root_agent`, including in an agent directory with another name.

## Tools and errors

Services raise Python exceptions. Tool adapters validate and convert input,
call a service, and wrap expected service failures in `ToolExecutionError`.
The agent registers `handle_tool_error` as its `on_tool_error_callback`, which
returns the exception fields plus `status: "error"` as a tool response. The
model can explain the failure or correct its arguments. Unexpected exceptions
abort execution.

FastAPI separately maps an `AppError` escaping an HTTP route to its
`status_code` and `to_dict()` body. An SSE response has already sent its HTTP
headers when execution starts, so failures appear in stream events; HTTP 200
does not prove that a run completed.

## Configuration and prompts

On importing the settings module, `.env` is loaded unless `DOCKER_ENV` is set.
Existing environment variables have priority. `Settings` then validates the
process environment. Google ADK reads provider settings from that same process.

Jinja2 instructions are loaded from `instructions/templates/`, with frontmatter
metadata and strict handling of undefined variables. The root agent's prompt
is loaded at import time; changing the file requires reloading the agent.

## Local and production execution

`DEBUG=false` selects ADK's API server. `DEBUG=true` selects its development
server, including the UI. `just api` and the container's `local` argument enable
that mode explicitly; the production launcher forces `DEBUG=false`.

Authentication is supplied by platform IAM or an authenticating proxy, with
no route around that boundary. End-user identity and session ownership must be
enforced by the adopting application. Disabling the UI alone does not add
authentication or authorization.

ADK selects default session and artifact storage. Local development uses files
under `.adk/`; cloud detection can select in-memory storage. Configure durable
services in `create_app()` for shared storage and persistence across restarts.

The application uses ADK's single `/health` route. This checks server
availability, not provider authentication or successful tool execution.

## Observability and packaging

Lifecycle callbacks log agent and tool names without dumping tool arguments.
Datadog is an optional Python extra and Docker build option, enabled by the
production launcher only when `DD_TRACE_ENABLED=true`.

The Docker image uses locked dependencies and runs as a non-root user. The
`tzdata` dependency supplies timezone data when the host does not provide it.
See [Python's timezone documentation](https://docs.python.org/3/library/zoneinfo.html#data-sources).

## Verification

- Unit tests cover services, tool adapters, callbacks, settings, and prompts.
- HTTP integration tests exercise discovery, sessions, conversation history,
  the real ADK runner, tools, error recovery, and SSE with a deterministic model.
- Launcher tests verify mode selection, configurable ports, and tracing opt-in.
- `just test` collects both naming conventions and enforces 83% coverage.
- Live Gemini behavior and deployment authentication require separate checks.
